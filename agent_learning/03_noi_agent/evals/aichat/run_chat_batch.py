import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from noi_agent import chat as noi_agent_chat


DEFAULT_CASES_PATH = Path("docs/common/aichat_socratic_eval_cases_2026_04.json")
DEFAULT_OUTPUT_PATH = Path("evals/aichat/aichat_socratic_responses.jsonl")
ChatFn = Callable[[list[dict], str, str], tuple[str, str, str]]


def load_cases(cases_path: Path = DEFAULT_CASES_PATH) -> dict:
    return json.loads(cases_path.read_text(encoding="utf-8"))


def _compact_context_line(label: str, value: str, max_chars: int = 1800) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "..."
    return f"{label}: {text}"


def build_messages_from_case(case: dict) -> list[dict]:
    messages = [dict(message) for message in case.get("prior_messages", [])]
    context_lines = [
        _compact_context_line("题目编号/链接", case.get("problem_ref", ""), 300),
        _compact_context_line("题面/题意/约束", case.get("problem_context", ""), 1800),
    ]
    context_lines = [line for line in context_lines if line]
    student_message = case.get("student_message", "")
    if context_lines:
        content = "\n".join(
            [
                "[学生原始问题]",
                student_message,
                "",
                "[当前题目上下文：只用于理解学生卡点，不要直接照抄题解]",
                *context_lines,
                "",
                "请优先围绕学生当前问题给渐进提示；不要直接给完整题解或最终代码。",
            ]
        )
    else:
        content = student_message
    messages.append({"role": "user", "content": content})
    return messages


def generate_response_rows(
    cases_data: dict,
    chat_fn: ChatFn = noi_agent_chat,
    student_id: str = "aichat_eval_student",
    limit: int | None = None,
    progress_stream=None,
) -> list[dict]:
    rows = []
    cases = cases_data.get("cases", [])
    if limit is not None:
        cases = cases[:limit]

    def write_progress(event: str, **fields) -> None:
        if progress_stream is None:
            return
        line = " ".join([event] + [f"{key}={value}" for key, value in fields.items()])
        progress_stream.write(line + "\n")
        flush = getattr(progress_stream, "flush", None)
        if callable(flush):
            flush()

    total = len(cases)
    for index, case in enumerate(cases, 1):
        case_id = case["id"]
        problem_ref = (case.get("problem_ref") or case_id).strip() or case_id
        eval_problem_id = f"{problem_ref}::{case_id}"
        messages = build_messages_from_case(case)
        write_progress("CASE_START", index=index, total=total, case_id=case_id)
        row = {
            "case_id": case_id,
            "problem_ref": problem_ref,
            "eval_problem_id": eval_problem_id,
            "student_message": case.get("student_message", ""),
        }
        try:
            response_text, history_text, level = chat_fn(messages, student_id, eval_problem_id)
            row.update(
                {
                    "response_text": response_text,
                    "history_text": history_text,
                    "level": level,
                }
            )
            write_progress("CASE_DONE", index=index, total=total, case_id=case_id, level=level)
        except Exception as exc:
            row.update(
                {
                    "response_text": "",
                    "history_text": "",
                    "level": "",
                    "error": str(exc),
                }
            )
            write_progress("CASE_ERROR", index=index, total=total, case_id=case_id, error=str(exc)[:120])
        rows.append(row)
    return rows


def write_response_rows(output_path: Path, rows: list[dict]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AIChat responses for Socratic eval cases.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH, help="AIChat Socratic case JSON file.")
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_PATH, help="Where to write generated responses.")
    parser.add_argument("--student-id", default="aichat_eval_student", help="Student id used for quota isolation.")
    parser.add_argument("--limit", type=int, help="Optional case limit for smoke tests.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    rows = generate_response_rows(
        load_cases(args.cases),
        student_id=args.student_id,
        limit=args.limit,
        progress_stream=sys.stderr,
    )
    write_response_rows(args.output_jsonl, rows)
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
