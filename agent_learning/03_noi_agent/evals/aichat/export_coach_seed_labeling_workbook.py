import argparse
import csv
import json
import sys
from pathlib import Path
from typing import TextIO


DEFAULT_INPUT_PATH = Path("docs/research/bridgebench_cp_seed_v1.jsonl")
DEFAULT_OUTPUT_PATH = Path("docs/research/coach_seed_labeling_workbook_v1.csv")

BLIND_CONTEXT_COLUMNS = [
    "case_id",
    "problem_ref",
    "student_message",
    "problem_context",
    "recent_dialogue",
    "student_code_excerpt",
]

REVIEW_CONTEXT_COLUMNS = [
    "case_id",
    "problem_ref",
    "topic",
    "student_message",
    "problem_context",
    "recent_dialogue",
    "student_code_excerpt",
]

SEED_GOLD_COLUMNS = [
    "seed_gold_student_state",
    "seed_gold_bridge_family",
    "seed_gold_bridge_subtype",
    "seed_gold_known_focus",
    "seed_gold_help_seeking_type",
    "seed_gold_missing_link",
    "seed_gold_allowed_help_level",
    "seed_gold_forbidden_completion",
    "seed_needs_new_focus",
]

COACH_COLUMNS = [
    "coach_problem_solving_state",
    "coach_bridge_family",
    "coach_secondary_bridge_family",
    "coach_bridge_subtype",
    "coach_known_focus",
    "coach_bridge_evidence",
    "coach_missing_bridge_description",
    "coach_help_seeking_type",
    "coach_allowed_help_level",
    "coach_help_forms",
    "coach_forbidden_content",
    "coach_needs_new_focus",
    "coach_confidence",
    "coach_notes",
    "review_status",
]

BLIND_WORKBOOK_COLUMNS = [*BLIND_CONTEXT_COLUMNS, *COACH_COLUMNS]
REVIEW_WORKBOOK_COLUMNS = [*REVIEW_CONTEXT_COLUMNS, *SEED_GOLD_COLUMNS, *COACH_COLUMNS]
WORKBOOK_COLUMNS = BLIND_WORKBOOK_COLUMNS


def load_seed_rows(path: Path) -> list[dict]:
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


def _dialogue_to_text(messages: list | None) -> str:
    parts = []
    for item in messages or []:
        if not isinstance(item, dict):
            continue
        role = item.get("role") or "unknown"
        content = (item.get("content") or "").strip()
        if content:
            parts.append(f"{role}: {content}")
    return "\n".join(parts)


def _blank_coach_fields() -> dict:
    return {
        "coach_problem_solving_state": "",
        "coach_bridge_family": "",
        "coach_secondary_bridge_family": "",
        "coach_bridge_subtype": "",
        "coach_known_focus": "",
        "coach_bridge_evidence": "",
        "coach_missing_bridge_description": "",
        "coach_help_seeking_type": "",
        "coach_allowed_help_level": "",
        "coach_help_forms": "",
        "coach_forbidden_content": "",
        "coach_needs_new_focus": "",
        "coach_confidence": "",
        "coach_notes": "",
        "review_status": "unlabeled",
    }


def _prefilled_coach_fields(row: dict) -> dict:
    return {
        "coach_problem_solving_state": row.get("gold_student_state", ""),
        "coach_bridge_family": row.get("gold_bridge_family", ""),
        "coach_secondary_bridge_family": row.get("gold_secondary_bridge_family", ""),
        "coach_bridge_subtype": row.get("gold_bridge_subtype", ""),
        "coach_known_focus": row.get("gold_known_focus", ""),
        "coach_bridge_evidence": _list_to_cell(row.get("gold_bridge_evidence", "")),
        "coach_missing_bridge_description": row.get("gold_missing_link", ""),
        "coach_help_seeking_type": row.get("gold_help_seeking_type", ""),
        "coach_allowed_help_level": row.get("gold_allowed_help_level", ""),
        "coach_help_forms": _list_to_cell(row.get("gold_help_forms") or row.get("gold_help_form", "")),
        "coach_forbidden_content": row.get("gold_forbidden_completion", ""),
        "coach_needs_new_focus": str(bool(row.get("needs_new_focus", False))).lower(),
        "coach_confidence": "",
        "coach_notes": "",
        "review_status": "review_seed_gold",
    }


def _list_to_cell(value) -> str:
    if isinstance(value, list):
        return ";".join(str(item) for item in value if str(item).strip())
    return str(value or "")


def build_workbook_rows(
    seed_rows: list[dict],
    *,
    prefill_coach: bool = False,
    include_seed_gold: bool = False,
) -> list[dict]:
    include_seed_gold = include_seed_gold or prefill_coach
    columns = REVIEW_WORKBOOK_COLUMNS if include_seed_gold else BLIND_WORKBOOK_COLUMNS
    workbook_rows = []
    for row in seed_rows:
        workbook_row = {
            "case_id": row.get("id") or row.get("case_id") or "",
            "problem_ref": row.get("problem_ref", ""),
            "topic": row.get("topic", ""),
            "student_message": row.get("student_message", ""),
            "problem_context": row.get("problem_context", ""),
            "recent_dialogue": _dialogue_to_text(row.get("prior_messages") or row.get("recent_dialogue")),
            "student_code_excerpt": row.get("student_code") or row.get("student_code_excerpt") or "",
        }
        if include_seed_gold:
            workbook_row.update(
                {
                    "seed_gold_student_state": row.get("gold_student_state", ""),
                    "seed_gold_bridge_family": row.get("gold_bridge_family", ""),
                    "seed_gold_bridge_subtype": row.get("gold_bridge_subtype", ""),
                    "seed_gold_known_focus": row.get("gold_known_focus", ""),
                    "seed_gold_help_seeking_type": row.get("gold_help_seeking_type", ""),
                    "seed_gold_missing_link": row.get("gold_missing_link", ""),
                    "seed_gold_allowed_help_level": row.get("gold_allowed_help_level", ""),
                    "seed_gold_forbidden_completion": row.get("gold_forbidden_completion", ""),
                    "seed_needs_new_focus": str(bool(row.get("needs_new_focus", False))).lower(),
                }
            )
        workbook_row.update(_prefilled_coach_fields(row) if prefill_coach else _blank_coach_fields())
        workbook_rows.append({column: workbook_row.get(column, "") for column in columns})
    return workbook_rows


def write_workbook_csv(output: TextIO, rows: list[dict], *, include_seed_gold: bool = False) -> None:
    columns = REVIEW_WORKBOOK_COLUMNS if include_seed_gold else BLIND_WORKBOOK_COLUMNS
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def export_workbook(
    *,
    input_jsonl: Path = DEFAULT_INPUT_PATH,
    output_csv: Path = DEFAULT_OUTPUT_PATH,
    prefill_coach: bool = False,
    include_seed_gold: bool = False,
) -> int:
    include_seed_gold = include_seed_gold or prefill_coach
    rows = build_workbook_rows(
        load_seed_rows(input_jsonl),
        prefill_coach=prefill_coach,
        include_seed_gold=include_seed_gold,
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        write_workbook_csv(f, rows, include_seed_gold=include_seed_gold)
    return len(rows)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export coach-friendly seed labeling CSV workbook.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument(
        "--prefill-coach",
        action="store_true",
        help="Copy seed gold labels into coach columns for review mode. Default leaves coach fields blank.",
    )
    parser.add_argument(
        "--include-seed-gold",
        action="store_true",
        help="Include seed_gold_* reference columns. Default omits them for blind coach labeling.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    row_count = export_workbook(
        input_jsonl=args.input_jsonl,
        output_csv=args.output_csv,
        prefill_coach=args.prefill_coach,
        include_seed_gold=args.include_seed_gold,
    )
    print(json.dumps({"output_csv": str(args.output_csv), "row_count": row_count}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
