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

CONTEXT_FIELDS = [
    "problem_statement",
    "problem_context",
    "student_message",
    "recent_dialogue",
    "context_ai_reply",
    "problem_ref",
    "problem_source_id",
    "problem_source_platform",
    "problem_source_url",
    *CASE_SPECIFIC_FIELDS,
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


def _has_value(value: object) -> bool:
    return bool(str(value or "").strip())


def _context_score(row: dict) -> int:
    return sum(1 for field in CONTEXT_FIELDS if _has_value(row.get(field)))


def _context_keys(row: dict) -> list[tuple[str, ...]]:
    case_id = str(row.get("case_id") or "").strip()
    response_id = str(row.get("anonymized_response_id") or "").strip()
    condition = str(row.get("condition_id") or row.get("system") or "").strip()
    keys: list[tuple[str, ...]] = []
    if response_id and condition:
        keys.append(("response_condition", response_id, condition))
    if case_id and condition:
        keys.append(("case_condition", case_id, condition))
    if case_id:
        keys.append(("case", case_id))
    return keys


def _build_context_index(context_rows: list[dict]) -> dict[tuple[str, ...], dict]:
    index: dict[tuple[str, ...], dict] = {}
    for row in context_rows:
        for key in _context_keys(row):
            current = index.get(key)
            if current is None or _context_score(row) > _context_score(current):
                index[key] = row
    return index


def enrich_rows_with_context(rows: list[dict], context_rows: list[dict]) -> list[dict]:
    """Copy missing case context/rubric fields without changing labels."""

    if not context_rows:
        return [dict(row) for row in rows]
    context_index = _build_context_index(context_rows)
    enriched = []
    for row in rows:
        out = dict(row)
        source = None
        for key in _context_keys(row):
            source = context_index.get(key)
            if source is not None:
                break
        if source is not None:
            copied = []
            for field in CONTEXT_FIELDS:
                if not _has_value(out.get(field)) and _has_value(source.get(field)):
                    out[field] = source.get(field)
                    copied.append(field)
            if copied:
                out["context_enrichment"] = {
                    "copied_fields": copied,
                    "source_case_id": source.get("case_id") or "",
                    "source_condition_id": source.get("condition_id") or source.get("system") or "",
                }
        enriched.append(out)
    return enriched


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
Use the 1-5 scale exactly. Do not use a 0-10 scale or any score outside 1-5.

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
Use the exact value ranges below:
- overall_quality: integer 1-5 only, never 0-10.
- scaffold_sufficiency: integer 0-2 only, where 0 means insufficient, 1 means partial, 2 means sufficient.
- categorical fields must use one of the listed enum values exactly.

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
Use the exact value ranges below:
- overall_quality: integer 1-5 only, never 0-10.
- scaffold_sufficiency: integer 0-2 only, where 0 means insufficient, 1 means partial, 2 means sufficient.
- categorical fields must use one of the listed enum values exactly.

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
    parser.add_argument(
        "--context-jsonl",
        action="append",
        type=Path,
        default=[],
        help="Optional JSONL with case context/rubric fields used to fill missing prompt context.",
    )
    parser.add_argument(
        "--output-enriched-labels-jsonl",
        type=Path,
        help="Optional path to write context-enriched labels/reference rows.",
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)

    rows = _read_jsonl(args.labels_jsonl)
    context_rows = []
    for path in args.context_jsonl:
        context_rows.extend(_read_jsonl(path))
    rows = enrich_rows_with_context(rows, context_rows)
    if args.output_enriched_labels_jsonl:
        write_jsonl(rows, args.output_enriched_labels_jsonl)
    tasks = build_calibration_tasks(rows, limit=args.limit)
    write_jsonl(tasks, args.output_jsonl)
    print(f"Wrote {len(tasks)} grader calibration tasks: {args.output_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
