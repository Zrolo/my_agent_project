"""Prepare LLM-grader calibration prompts from reviewed response labels.

This script does not call any model. It converts merged human-review rows into
prompt packs for three grader variants:

- likert_only_judge
- generic_rubric_judge
- case_specific_bridge_rubric_judge

The output is for dev calibration only. Coach labels remain expert references;
LLM graders are never treated as gold truth.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


GRADER_TYPES = [
    "likert_only_judge",
    "generic_rubric_judge",
    "case_specific_bridge_rubric_judge",
]

CASE_SPECIFIC_FIELDS = [
    "success_criteria",
    "forbidden_content",
    "critical_bridge_boundary",
    "acceptable_reveal",
    "expected_student_next_action",
]


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


def _shorten(value: object, limit: int = 5000) -> str:
    text = str(value or "").strip()
    return text if len(text) <= limit else text[: limit - 20] + "\n...[truncated]"


def build_grader_prompt(row: dict, grader_type: str) -> str:
    if grader_type not in GRADER_TYPES:
        raise ValueError(f"unsupported grader_type: {grader_type}")

    shared_context = f"""You are calibrating an AI tutor-response grader.

Return JSON only. If the context is insufficient, use UNKNOWN / INSUFFICIENT_CONTEXT instead of guessing.

Problem:
{_shorten(row.get("problem_statement") or row.get("problem_context"))}

Current student message:
{_shorten(row.get("student_message"))}

Recent dialogue:
{_shorten(row.get("recent_dialogue"))}

Context AI reply:
{_shorten(row.get("context_ai_reply"))}

Target AI response to grade:
{_shorten(row.get("response_text"))}
"""

    if grader_type == "likert_only_judge":
        return (
            shared_context
            + """
Task:
Give a holistic tutoring quality score from 1 to 5 and a brief rationale.

Output schema:
{"overall_quality": 1, "rationale": "..."}
"""
        )

    if grader_type == "generic_rubric_judge":
        return (
            shared_context
            + """
Task:
Grade the response using a generic AI-tutor rubric:
- overall quality
- whether it is ready to show to a student
- whether it leaks the answer or over-completes the student's reasoning
- whether the scaffold is sufficient
- expected student response burden

Use UNKNOWN / INSUFFICIENT_CONTEXT when needed.

Output schema:
{
  "overall_quality": 1,
  "student_ready": "yes|borderline|no|UNKNOWN",
  "leakage_label": "no_leakage|minor_bridge_leakage|major_bridge_leakage|answer_leakage|UNKNOWN",
  "bridge_reveal_justification": "no_reveal|pedagogically_justified|borderline|unjustified|UNKNOWN",
  "scaffold_sufficiency": 0,
  "student_response_burden": "low|medium|high|UNKNOWN",
  "rationale": "..."
}
"""
        )

    case_specific = f"""Case-specific rubric:
Success criteria:
{_shorten(row.get("success_criteria"))}

Forbidden content:
{_shorten(row.get("forbidden_content"))}

Critical bridge boundary:
{_shorten(row.get("critical_bridge_boundary"))}

Acceptable reveal:
{_shorten(row.get("acceptable_reveal"))}

Expected student next action:
{_shorten(row.get("expected_student_next_action"))}
"""
    return (
        shared_context
        + "\n"
        + case_specific
        + """
Task:
Grade the response using the case-specific bridge rubric. Focus on whether the response helps the student advance without prematurely completing the current missing bridge.

Use UNKNOWN / INSUFFICIENT_CONTEXT when the case rubric or context is not enough to judge.

Output schema:
{
  "overall_quality": 1,
  "student_ready": "yes|borderline|no|UNKNOWN",
  "leakage_label": "no_leakage|minor_bridge_leakage|major_bridge_leakage|answer_leakage|UNKNOWN",
  "bridge_reveal_justification": "no_reveal|pedagogically_justified|borderline|unjustified|UNKNOWN",
  "scaffold_sufficiency": 0,
  "student_response_burden": "low|medium|high|UNKNOWN",
  "rationale": "..."
}
"""
    )


def build_calibration_tasks(rows: list[dict], *, limit: int | None = None) -> list[dict]:
    selected = rows[:limit] if limit is not None else rows
    tasks = []
    for row in selected:
        case_specific_present = any(str(row.get(field) or "").strip() for field in CASE_SPECIFIC_FIELDS)
        for grader_type in GRADER_TYPES:
            tasks.append(
                {
                    "grader_type": grader_type,
                    "case_id": row.get("case_id") or "",
                    "anonymized_response_id": row.get("anonymized_response_id") or "",
                    "condition_id": row.get("condition_id") or row.get("system") or "",
                    "case_specific_rubric_present": case_specific_present,
                    "prompt": build_grader_prompt(row, grader_type),
                    "coach_reference": {
                        "overall_quality": row.get("overall_quality_score"),
                        "student_ready_pass": row.get("would_show_to_student"),
                        "leakage_label": row.get("leakage_label"),
                        "bridge_reveal_justification": row.get(
                            "bridge_reveal_justification"
                        ),
                        "scaffold_sufficiency": (row.get("scores") or {}).get(
                            "scaffold_sufficiency"
                        ),
                        "student_response_burden": row.get("student_response_burden"),
                    },
                }
            )
    return tasks


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels-jsonl", required=True, type=Path)
    parser.add_argument("--output-jsonl", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)

    rows = _read_jsonl(args.labels_jsonl)
    tasks = build_calibration_tasks(rows, limit=args.limit)
    write_jsonl(tasks, args.output_jsonl)
    print(f"Wrote {len(tasks)} grader calibration tasks: {args.output_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
