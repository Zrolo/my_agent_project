"""Run LLM-grader calibration prompt packs and write parsed predictions.

This runner consumes JSONL prompt packs produced by
``prepare_llm_grader_calibration_pack.py``. It calls a fixed judge backend,
parses JSON-only grader outputs, and writes rows with a ``grader_prediction``
field for ``summarize_llm_grader_calibration.py``.

The script is calibration infrastructure only. It does not create human labels,
does not modify main experiment data, and does not treat LLM outputs as gold.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

from evals.review.run_review_case_kimi_cli import _run_kimi_cli, _strip_json_fence
from noi_agent import (
    _choice_message_text,
    _offline_judge_completion_create,
    _offline_judge_profile,
    _offline_json_judge_request_kwargs,
)


TaskKey = tuple[str, str, str, str]

READY_LABELS = {"yes", "borderline", "no", "UNKNOWN"}
LEAKAGE_LABELS = {
    "no_leakage",
    "minor_bridge_leakage",
    "major_bridge_leakage",
    "answer_leakage",
    "UNKNOWN",
}
REVEAL_LABELS = {
    "no_reveal",
    "pedagogically_justified",
    "borderline",
    "unjustified",
    "UNKNOWN",
}
BURDEN_LABELS = {"low", "medium", "high", "UNKNOWN"}


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def _task_key(row: dict) -> TaskKey:
    return (
        str(row.get("grader_type") or ""),
        str(row.get("case_id") or ""),
        str(row.get("anonymized_response_id") or ""),
        str(row.get("condition_id") or ""),
    )


def _load_existing_keys(path: Path) -> set[TaskKey]:
    if not path.exists():
        return set()
    return {_task_key(row) for row in _read_jsonl(path)}


def _extract_json_object(raw_output: str) -> tuple[dict, str | None]:
    cleaned = _strip_json_fence(raw_output or "")
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            return {}, "invalid_json"
        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return {}, "invalid_json"
    if not isinstance(parsed, dict):
        return {}, "invalid_schema"
    return parsed, None


def _normalize_prediction(prediction: dict) -> dict:
    normalized = dict(prediction)
    if "overall_quality_score" in normalized and "overall_quality" not in normalized:
        normalized["overall_quality"] = normalized["overall_quality_score"]
    return normalized


def _as_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _label(value: object) -> str:
    raw = str(value or "").strip()
    if "｜" in raw:
        raw = raw.split("｜", 1)[0].strip()
    if "|" in raw:
        raw = raw.split("|", 1)[0].strip()
    return raw


def _validate_prediction(prediction: dict, grader_type: str) -> list[str]:
    errors: list[str] = []
    overall = _as_float(prediction.get("overall_quality"))
    if overall is None or overall < 1 or overall > 5:
        errors.append("overall_quality must be a 1-5 number")

    if grader_type == "likert_only_judge":
        return errors

    ready = _label(prediction.get("student_ready"))
    if ready not in READY_LABELS:
        errors.append("student_ready must be yes|borderline|no|UNKNOWN")

    leakage = _label(prediction.get("leakage_label"))
    if leakage not in LEAKAGE_LABELS:
        errors.append(
            "leakage_label must be no_leakage|minor_bridge_leakage|major_bridge_leakage|answer_leakage|UNKNOWN"
        )

    reveal = _label(prediction.get("bridge_reveal_justification"))
    if reveal not in REVEAL_LABELS:
        errors.append(
            "bridge_reveal_justification must be no_reveal|pedagogically_justified|borderline|unjustified|UNKNOWN"
        )

    sufficiency = _as_float(prediction.get("scaffold_sufficiency"))
    if sufficiency is None or sufficiency < 0 or sufficiency > 2:
        errors.append("scaffold_sufficiency must be a 0-2 number")

    burden = _label(prediction.get("student_response_burden"))
    if burden not in BURDEN_LABELS:
        errors.append("student_response_burden must be low|medium|high|UNKNOWN")
    return errors


def _run_deepseek_offline_judge(prompt: str) -> str:
    profile = _offline_judge_profile("deepseek")
    kwargs = _offline_json_judge_request_kwargs(
        profile=profile,
        messages=[{"role": "user", "content": prompt}],
        max_tokens_env="NOI_LLM_GRADER_MAX_TOKENS",
        default_max_tokens="2048",
        timeout_env="NOI_LLM_GRADER_TIMEOUT_SECONDS",
        default_timeout="60.0",
    )
    response = _offline_judge_completion_create(profile, kwargs)
    return _choice_message_text(response, allow_reasoning_fallback=False)


def _call_backend(prompt: str, backend: str) -> str:
    if backend == "deepseek":
        return _run_deepseek_offline_judge(prompt)
    if backend == "kimi_cli":
        return _run_kimi_cli(prompt)
    raise ValueError(f"Unsupported backend: {backend}")


def run_pack(
    rows: list[dict],
    *,
    backend: str,
    output_jsonl: Path,
    limit: int | None = None,
    force: bool = False,
    retry_non_ok: bool = False,
    sleep_seconds: float = 0.0,
    progress_stream=None,
    backend_fn: Callable[[str, str], str] = _call_backend,
) -> dict:
    selected = rows[:limit] if limit is not None else rows
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    preserved_rows: list[dict] = []
    if force:
        existing = set()
    elif retry_non_ok and output_jsonl.exists():
        preserved_rows = [
            row
            for row in _read_jsonl(output_jsonl)
            if str(row.get("grader_status") or "ok") == "ok"
        ]
        existing = {_task_key(row) for row in preserved_rows}
    else:
        existing = _load_existing_keys(output_jsonl)
    mode = "w" if force or retry_non_ok else "a"

    attempted = written = skipped = errors = invalid = 0
    with output_jsonl.open(mode, encoding="utf-8") as handle:
        for row in preserved_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        for index, row in enumerate(selected, 1):
            key = _task_key(row)
            if key in existing:
                skipped += 1
                continue

            attempted += 1
            status = "ok"
            error = None
            raw_output = ""
            prediction: dict = {}
            started = time.perf_counter()
            try:
                raw_output = backend_fn(str(row.get("prompt") or ""), backend)
                prediction, error = _extract_json_object(raw_output)
                if error:
                    status = error
                    invalid += 1
                else:
                    prediction = _normalize_prediction(prediction)
                    schema_errors = _validate_prediction(prediction, str(row.get("grader_type") or ""))
                    if schema_errors:
                        status = "invalid_schema"
                        error = "; ".join(schema_errors)
                        invalid += 1
            except Exception as exc:  # pragma: no cover - exercised by live backends.
                status = "error"
                error = f"{type(exc).__name__}: {exc}"
                errors += 1

            elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
            out = dict(row)
            out.update(
                {
                    "grader_backend": backend,
                    "grader_status": status,
                    "grader_error": error,
                    "grader_prediction": prediction,
                    "grader_raw_output": raw_output[:4000],
                    "grader_latency_ms": elapsed_ms,
                }
            )
            handle.write(json.dumps(out, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            written += 1

            if progress_stream is not None:
                progress_stream.write(
                    "CALIBRATION_TASK_DONE "
                    f"index={index} total={len(selected)} grader={key[0]} case_id={key[1]} "
                    f"status={status} latency_ms={elapsed_ms}\n"
                )
                progress_stream.flush()
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

    return {
        "input_rows": len(rows),
        "selected_rows": len(selected),
        "attempted": attempted,
        "written": written,
        "skipped_existing": skipped,
        "errors": errors,
        "invalid_json_or_schema": invalid,
        "preserved_existing_ok": len(preserved_rows),
        "output_jsonl": str(output_jsonl),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-jsonl", required=True, type=Path)
    parser.add_argument("--output-jsonl", required=True, type=Path)
    parser.add_argument("--backend", default="deepseek", choices=["deepseek", "kimi_cli"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Overwrite output instead of resuming.")
    parser.add_argument(
        "--retry-non-ok",
        action="store_true",
        help="Preserve existing ok rows and retry rows with error/invalid status.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print planned work only.")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument(
        "--judge-timeout-seconds",
        type=int,
        help=(
            "Override REVIEW_EVAL_KIMI_TIMEOUT_SECONDS for kimi_cli backend and "
            "NOI_LLM_GRADER_TIMEOUT_SECONDS for deepseek backend."
        ),
    )
    args = parser.parse_args(argv)

    if args.judge_timeout_seconds is not None:
        os.environ["REVIEW_EVAL_KIMI_TIMEOUT_SECONDS"] = str(args.judge_timeout_seconds)
        os.environ["NOI_LLM_GRADER_TIMEOUT_SECONDS"] = str(args.judge_timeout_seconds)

    rows = _read_jsonl(args.pack_jsonl)
    selected = rows[: args.limit] if args.limit is not None else rows
    if args.dry_run:
        if args.retry_non_ok and args.output_jsonl.exists() and not args.force:
            existing_rows = [
                row
                for row in _read_jsonl(args.output_jsonl)
                if str(row.get("grader_status") or "ok") == "ok"
            ]
            existing = {_task_key(row) for row in existing_rows}
        else:
            existing = _load_existing_keys(args.output_jsonl)
        planned = [row for row in selected if args.force or _task_key(row) not in existing]
        print(
            json.dumps(
                {
                    "pack_jsonl": str(args.pack_jsonl),
                    "output_jsonl": str(args.output_jsonl),
                    "backend": args.backend,
                    "input_rows": len(rows),
                    "selected_rows": len(selected),
                    "existing_rows": len(existing),
                    "planned_calls": len(planned),
                    "first_task": {
                        "grader_type": selected[0].get("grader_type") if selected else None,
                        "case_id": selected[0].get("case_id") if selected else None,
                        "condition_id": selected[0].get("condition_id") if selected else None,
                        "prompt_chars": len(str(selected[0].get("prompt") or "")) if selected else 0,
                    },
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    summary = run_pack(
        rows,
        backend=args.backend,
        output_jsonl=args.output_jsonl,
        limit=args.limit,
        force=args.force,
        retry_non_ok=args.retry_non_ok,
        sleep_seconds=args.sleep_seconds,
        progress_stream=sys.stderr,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
