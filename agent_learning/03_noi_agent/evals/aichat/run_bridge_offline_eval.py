import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from noi_agent import bridge_judge_v1, chat as noi_agent_chat, leakage_judge_v1, repair_response_v1


DEFAULT_SEED_PATH = Path("docs/research/bridgebench_cp_seed_v1.jsonl")
DEFAULT_OUTPUT_PATH = Path("evals/aichat/bridge_offline_eval_results.jsonl")

BridgeJudgeFn = Callable[..., dict]
TutorFn = Callable[[dict, list[dict], dict], dict]
LeakageJudgeFn = Callable[..., dict]
RepairFn = Callable[..., dict]


def load_seed_rows(path: Path = DEFAULT_SEED_PATH) -> list[dict]:
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


def _compact_context_line(label: str, value: str, max_chars: int = 1800) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "..."
    return f"{label}: {text}"


def build_messages_from_seed_row(row: dict) -> list[dict]:
    messages = [dict(message) for message in row.get("prior_messages", [])]
    context_lines = [
        _compact_context_line("题目编号/链接", row.get("problem_ref", ""), 300),
        _compact_context_line("题面/题意/约束", row.get("problem_context", ""), 1800),
    ]
    context_lines = [line for line in context_lines if line]
    student_message = row.get("student_message", "")
    if context_lines:
        content = "\n".join(
            [
                "[学生原始问题]",
                student_message,
                "",
                "[当前题目上下文：只用于离线研究诊断，不要直接照抄题解]",
                *context_lines,
                "",
                "请围绕学生当前卡点生成或评估渐进脚手架。",
            ]
        )
    else:
        content = student_message
    messages.append({"role": "user", "content": content})
    return messages


def _default_tutor_fn(row: dict, messages: list[dict], bridge_result: dict) -> dict:
    problem_ref = (row.get("problem_ref") or row.get("id") or "unknown_problem").strip()
    case_id = row.get("id") or problem_ref
    response_text, history_text, level = noi_agent_chat(
        messages,
        "bridge_offline_eval_student",
        f"{problem_ref}::{case_id}",
    )
    return {
        "baseline_group": "current_system",
        "response_text": response_text,
        "history_text": history_text,
        "level": level,
    }


def _bridge_help_forms(bridge_result: dict) -> list[str]:
    help_forms = bridge_result.get("help_forms")
    if isinstance(help_forms, list):
        return [item for item in help_forms if isinstance(item, str) and item.strip()]
    help_form = bridge_result.get("help_form")
    return [help_form] if isinstance(help_form, str) and help_form.strip() else []


def _case_gold(row: dict) -> dict:
    return {
        "student_state": row.get("gold_student_state", ""),
        "bridge_family": row.get("gold_bridge_family", ""),
        "known_focus": row.get("gold_known_focus", ""),
        "help_seeking_type": row.get("gold_help_seeking_type", ""),
        "missing_link": row.get("gold_missing_link", ""),
        "allowed_help_level": row.get("gold_allowed_help_level", ""),
        "forbidden_completion": row.get("gold_forbidden_completion", ""),
        "needs_new_focus": bool(row.get("needs_new_focus", False)),
    }


def _write_progress(progress_stream, event: str, **fields) -> None:
    if progress_stream is None:
        return
    line = " ".join([event] + [f"{key}={value}" for key, value in fields.items()])
    progress_stream.write(line + "\n")
    flush = getattr(progress_stream, "flush", None)
    if callable(flush):
        flush()


def _run_one_bridge_offline_case(
    row: dict,
    *,
    bridge_judge_fn: BridgeJudgeFn,
    tutor_fn: TutorFn,
    leakage_judge_fn: LeakageJudgeFn,
    repair_fn: RepairFn,
) -> dict:
    messages = build_messages_from_seed_row(row)
    student_message = row.get("student_message", "")
    problem_context = {
        "problem_ref": row.get("problem_ref", ""),
        "summary": row.get("problem_context", ""),
    }
    case_id = row.get("id") or row.get("case_id") or ""
    result = {
        "case_id": case_id,
        "problem_ref": row.get("problem_ref", ""),
        "topic": row.get("topic", ""),
        "student_message": student_message,
        "gold": _case_gold(row),
    }

    bridge_result = bridge_judge_fn(
        student_message=student_message,
        messages=messages,
        problem_context=problem_context,
        student_code=row.get("student_code"),
        available_known_focus=row.get("available_known_focus", []),
    )
    result["bridge_judge_result"] = bridge_result
    if bridge_result.get("_failed"):
        result["error"] = "bridge_judge_failed"
        return result

    tutor_result = tutor_fn(row, messages, bridge_result)
    result["tutor_response"] = tutor_result
    candidate_response = tutor_result.get("response_text", "")

    forbidden_content = bridge_result.get("forbidden_content") or []
    if row.get("gold_forbidden_completion") and row["gold_forbidden_completion"] not in forbidden_content:
        forbidden_content = [*forbidden_content, row["gold_forbidden_completion"]]

    leakage_result = leakage_judge_fn(
        student_message=student_message,
        messages=messages,
        problem_context=problem_context,
        current_missing_bridge=bridge_result.get("missing_bridge", {}),
        allowed_help_level=bridge_result.get("allowed_help_level", ""),
        help_forms=_bridge_help_forms(bridge_result),
        forbidden_content=forbidden_content,
        candidate_response=candidate_response,
        student_already_stated_bridge=bool(row.get("student_already_stated_bridge", False)),
    )
    result["leakage_judge_result"] = leakage_result

    if leakage_result.get("safe_action") in {"rewrite", "block"} and not leakage_result.get("_failed"):
        result["repair_result"] = repair_fn(
            original_candidate_response=candidate_response,
            leakage_judge_result=leakage_result,
            bridge_judge_result=bridge_result,
            student_message=student_message,
            messages=messages,
        )

    return result


def run_bridge_offline_eval_rows(
    rows: list[dict],
    *,
    bridge_judge_fn: BridgeJudgeFn = bridge_judge_v1,
    tutor_fn: TutorFn = _default_tutor_fn,
    leakage_judge_fn: LeakageJudgeFn = leakage_judge_v1,
    repair_fn: RepairFn = repair_response_v1,
    limit: int | None = None,
    progress_stream=None,
) -> list[dict]:
    selected = rows[:limit] if limit is not None else rows
    result_rows = []
    total = len(selected)
    for index, row in enumerate(selected, 1):
        case_id = row.get("id") or row.get("case_id") or f"case_{index}"
        _write_progress(progress_stream, "CASE_START", index=index, total=total, case_id=case_id)
        try:
            result = _run_one_bridge_offline_case(
                row,
                bridge_judge_fn=bridge_judge_fn,
                tutor_fn=tutor_fn,
                leakage_judge_fn=leakage_judge_fn,
                repair_fn=repair_fn,
            )
            _write_progress(progress_stream, "CASE_DONE", index=index, total=total, case_id=case_id)
        except Exception as exc:
            result = {
                "case_id": case_id,
                "problem_ref": row.get("problem_ref", ""),
                "student_message": row.get("student_message", ""),
                "gold": _case_gold(row),
                "error": f"{type(exc).__name__}: {exc}",
            }
            _write_progress(
                progress_stream,
                "CASE_ERROR",
                index=index,
                total=total,
                case_id=case_id,
                error=str(exc)[:120],
            )
        result_rows.append(result)
    return result_rows


def write_result_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run offline Bridge Judge + Leakage Judge evaluation rows.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_SEED_PATH, help="Seed turn JSONL file.")
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_PATH, help="Where to write result JSONL.")
    parser.add_argument("--limit", type=int, help="Optional case limit for smoke tests.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    rows = run_bridge_offline_eval_rows(
        load_seed_rows(args.input_jsonl),
        limit=args.limit,
        progress_stream=sys.stderr,
    )
    write_result_rows(args.output_jsonl, rows)
    error_count = sum(1 for row in rows if row.get("error"))
    print(
        json.dumps(
            {
                "output_jsonl": str(args.output_jsonl),
                "case_count": len(rows),
                "error_count": error_count,
            },
            ensure_ascii=False,
        )
    )
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
