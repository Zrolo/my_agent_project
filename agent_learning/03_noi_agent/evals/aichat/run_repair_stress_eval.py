"""Run offline repair stress cases through Leakage Judge and Repair.

This runner is intentionally offline-only. It does not change online AIChat
behavior; it evaluates whether an over-strong candidate response can be
detected and rewritten into a safer scaffold.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Callable

from noi_agent import leakage_judge_v1, repair_response_v1

from evals.aichat.run_bridge_offline_eval import (
    _bridge_help_forms,
    _bridge_result_from_runtime_contract,
    _call_stage_with_retries,
)


DEFAULT_INPUT_PATH = Path("docs/research/repair_stress_cases_v1.jsonl")
DEFAULT_OUTPUT_PATH = Path("evals/aichat/ad_hoc_runs/repair_stress_v1_results.jsonl")


def load_repair_stress_cases(path: Path | str) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL row: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: row must be an object")
            rows.append(row)
    return rows


def write_repair_stress_results(path: Path | str, rows: list[dict]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _safe_fallback(row: dict) -> str:
    return (
        "这一步我先不直接补完整关键桥。你把自己当前判断写成一句话，"
        "我只帮你检查这句话哪里还缺证据。"
    )


def _messages_from_recent_dialogue(row: dict) -> list[dict]:
    recent = row.get("recent_dialogue")
    if isinstance(recent, list):
        return [item for item in recent if isinstance(item, dict)]
    if isinstance(recent, str) and recent.strip() and recent.strip().upper() != "N/A":
        return [{"role": "assistant", "content": recent.strip()}]
    return []


def _problem_context(row: dict) -> dict:
    return {
        "problem_ref": row.get("problem_ref", ""),
        "summary": row.get("problem_context", ""),
    }


def _candidate_response(row: dict) -> str:
    return row.get("candidate_response_text") or row.get("candidate_response") or ""


def _stage_error(result: dict) -> str:
    return str(result.get("_error") or result.get("_reason") or "_failed")


def _record_latency(latency_ms: dict, key: str, start: float) -> None:
    latency_ms[key] = round((time.perf_counter() - start) * 1000, 2)


def run_one_repair_stress_case(
    row: dict,
    *,
    leakage_judge_fn: Callable = leakage_judge_v1,
    repair_fn: Callable = repair_response_v1,
    judge_provider: str = "deepseek",
    max_retries: int = 0,
    second_pass_leakage: bool = True,
) -> dict:
    total_start = time.perf_counter()
    stage_latency_ms: dict[str, float] = {}
    stage_errors: dict[str, str] = {}
    retry_count = 0
    llm_call_count = 0

    contract = dict(row.get("runtime_bridge_contract") or {})
    bridge_result = _bridge_result_from_runtime_contract(contract)
    messages = _messages_from_recent_dialogue(row)
    problem_context = _problem_context(row)
    candidate_response = _candidate_response(row)

    result = {
        "id": row.get("id", ""),
        "source_case_id": row.get("source_case_id", ""),
        "stress_type": row.get("stress_type", ""),
        "student_message": row.get("student_message", ""),
        "problem_context": row.get("problem_context", ""),
        "recent_dialogue": row.get("recent_dialogue", ""),
        "candidate_response_text": candidate_response,
        "runtime_bridge_contract": contract,
        "expected_leakage_label": row.get("expected_leakage_label", ""),
        "expected_safe_action": row.get("expected_safe_action", ""),
        "repair_success_criteria": row.get("repair_success_criteria", []),
        "final_response_text": candidate_response,
        "final_response_source": "candidate",
        "repair_applied": False,
        "blocked": False,
    }

    stage_start = time.perf_counter()
    try:
        leakage_result, leakage_retries = _call_stage_with_retries(
            leakage_judge_fn,
            {
                "student_message": row.get("student_message", ""),
                "messages": messages,
                "problem_context": problem_context,
                "current_missing_bridge": bridge_result.get("missing_bridge", {}),
                "allowed_help_level": bridge_result.get("allowed_help_level", ""),
                "help_forms": _bridge_help_forms(bridge_result),
                "forbidden_content": bridge_result.get("forbidden_content", []),
                "candidate_response": candidate_response,
                "student_already_stated_bridge": bool(row.get("student_already_stated_bridge", False)),
            },
            judge_provider=judge_provider,
            max_retries=max_retries,
        )
        llm_call_count += 1 + leakage_retries
        retry_count += leakage_retries
    except Exception as exc:
        leakage_result = {"_failed": True, "_reason": f"{type(exc).__name__}: {exc}"}
        llm_call_count += 1
        stage_errors["leakage_judge"] = leakage_result["_reason"]
    _record_latency(stage_latency_ms, "leakage_judge_latency_ms", stage_start)
    result["leakage_judge_result"] = leakage_result
    if leakage_result.get("_failed"):
        stage_errors["leakage_judge"] = _stage_error(leakage_result)

    safe_action = leakage_result.get("safe_action")
    if safe_action == "block":
        result["final_response_text"] = _safe_fallback(row)
        result["final_response_source"] = "safe_fallback"
        result["blocked"] = True

    if safe_action in {"rewrite", "block"} and not leakage_result.get("_failed"):
        stage_start = time.perf_counter()
        try:
            repair_result, repair_retries = _call_stage_with_retries(
                repair_fn,
                {
                    "original_candidate_response": candidate_response,
                    "leakage_judge_result": leakage_result,
                    "bridge_judge_result": bridge_result,
                    "student_message": row.get("student_message", ""),
                    "messages": messages,
                },
                judge_provider=judge_provider,
                max_retries=max_retries,
            )
            llm_call_count += 1 + repair_retries
            retry_count += repair_retries
        except Exception as exc:
            repair_result = {"_failed": True, "_reason": f"{type(exc).__name__}: {exc}"}
            llm_call_count += 1
            stage_errors["repair"] = repair_result["_reason"]
        _record_latency(stage_latency_ms, "repair_latency_ms", stage_start)
        result["repair_result"] = repair_result
        if repair_result.get("_failed"):
            stage_errors["repair"] = _stage_error(repair_result)

        repaired_response = repair_result.get("repaired_response") if isinstance(repair_result, dict) else ""
        if repaired_response:
            result["final_response_text"] = repaired_response
            result["final_response_source"] = "repair"
            result["repair_applied"] = True
            result["blocked"] = False

            if second_pass_leakage:
                stage_start = time.perf_counter()
                try:
                    post_repair_result, post_repair_retries = _call_stage_with_retries(
                        leakage_judge_fn,
                        {
                            "student_message": row.get("student_message", ""),
                            "messages": messages,
                            "problem_context": problem_context,
                            "current_missing_bridge": bridge_result.get("missing_bridge", {}),
                            "allowed_help_level": bridge_result.get("allowed_help_level", ""),
                            "help_forms": _bridge_help_forms(bridge_result),
                            "forbidden_content": bridge_result.get("forbidden_content", []),
                            "candidate_response": repaired_response,
                            "student_already_stated_bridge": bool(
                                row.get("student_already_stated_bridge", False)
                            ),
                        },
                        judge_provider=judge_provider,
                        max_retries=max_retries,
                    )
                    llm_call_count += 1 + post_repair_retries
                    retry_count += post_repair_retries
                except Exception as exc:
                    post_repair_result = {"_failed": True, "_reason": f"{type(exc).__name__}: {exc}"}
                    llm_call_count += 1
                    stage_errors["post_repair_leakage_judge"] = post_repair_result["_reason"]
                _record_latency(stage_latency_ms, "post_repair_leakage_judge_latency_ms", stage_start)
                result["post_repair_leakage_judge_result"] = post_repair_result
                if post_repair_result.get("_failed"):
                    stage_errors["post_repair_leakage_judge"] = _stage_error(post_repair_result)

    stage_latency_ms["total_latency_ms"] = round((time.perf_counter() - total_start) * 1000, 2)
    result["stage_latency_ms"] = stage_latency_ms
    result["stage_errors"] = stage_errors
    result["retry_count"] = retry_count
    result["llm_call_count"] = llm_call_count
    result["judge_provider"] = judge_provider
    result["second_pass_leakage"] = second_pass_leakage
    return result


def run_repair_stress_eval(
    rows: list[dict],
    *,
    leakage_judge_fn: Callable = leakage_judge_v1,
    repair_fn: Callable = repair_response_v1,
    judge_provider: str = "deepseek",
    max_retries: int = 0,
    second_pass_leakage: bool = True,
    progress_stream=None,
) -> list[dict]:
    results = []
    for index, row in enumerate(rows, start=1):
        result = run_one_repair_stress_case(
            row,
            leakage_judge_fn=leakage_judge_fn,
            repair_fn=repair_fn,
            judge_provider=judge_provider,
            max_retries=max_retries,
            second_pass_leakage=second_pass_leakage,
        )
        results.append(result)
        if progress_stream is not None:
            progress_stream.write(
                "repair_stress_case_done "
                f"index={index} id={result.get('id')} "
                f"source={result.get('source_case_id')} "
                f"action={result.get('leakage_judge_result', {}).get('safe_action')} "
                f"final={result.get('final_response_source')}\n"
            )
            progress_stream.flush()
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--judge-provider", default="deepseek")
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--no-second-pass-leakage", action="store_true")
    args = parser.parse_args(argv)

    rows = load_repair_stress_cases(args.input_jsonl)
    if args.limit > 0:
        rows = rows[: args.limit]
    results = run_repair_stress_eval(
        rows,
        judge_provider=args.judge_provider,
        max_retries=max(0, args.max_retries),
        second_pass_leakage=not args.no_second_pass_leakage,
        progress_stream=sys.stderr,
    )
    write_repair_stress_results(args.output_jsonl, results)
    print(f"Wrote {len(results)} repair stress results to {args.output_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
