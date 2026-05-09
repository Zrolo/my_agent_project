import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.aichat.coach_labeling_schema_v2 import extract_option_id, split_option_ids
from evals.aichat.validate_coach_workbook_v2 import load_csv_rows, load_xlsx_rows


DEFAULT_INPUT_XLSX = Path("docs/research/coach_seed_labeling_workbook_v2_20.zh.xlsx")
DEFAULT_OUTPUT_JSONL = Path("docs/research/coach_seed_labeling_v2_gold_20.jsonl")

MULTI_VALUE_FIELDS = {
    "help_seeking_type",
    "help_forms",
    "general_forbidden_content",
    "bridge_specific_forbidden_content",
    "coach_note_tags",
}

SINGLE_OPTION_FIELDS = {
    "turn_type",
    "diagnosis_uncertainty",
    "student_problem_solving_state",
    "student_attempt_level",
    "student_already_stated_bridge",
    "policy_risk_type",
    "primary_bridge_family",
    "primary_bridge_subtype_id",
    "secondary_bridge_family",
    "secondary_bridge_subtype_id",
    "evidence_type",
    "registered_focus_id",
    "secondary_registered_focus_id",
    "focus_match_status",
    "max_scaffold_level",
    "leakage_risk",
    "review_status",
}

TEXT_FIELDS = {
    "case_id",
    "problem_ref",
    "student_message",
    "problem_context",
    "recent_dialogue",
    "student_code_excerpt",
    "student_already_knows",
    "primary_bridge_subtype_note",
    "missing_bridge_instance",
    "evidence_quote",
    "new_focus_candidate",
    "coach_confidence",
    "coach_free_notes",
}


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _load_rows(path: Path) -> list[dict]:
    if path.suffix.lower() == ".xlsx":
        return load_xlsx_rows(path)
    return load_csv_rows(path)


def build_gold_row(row: dict) -> dict:
    gold: dict = {
        "label_reference_type": "single_coach_reference",
        "label_adjudication_status": "raw",
        "is_adjudicated_gold": False,
    }
    for field in TEXT_FIELDS:
        value = _clean_text(row.get(field))
        if value:
            gold[field] = value
    for field in SINGLE_OPTION_FIELDS:
        value = extract_option_id(row.get(field))
        if value:
            gold[field] = value
    for field in MULTI_VALUE_FIELDS:
        values = split_option_ids(row.get(field))
        if values:
            gold[field] = values
    return gold


def export_workbook_to_jsonl(input_path: Path, output_path: Path) -> int:
    rows = _load_rows(input_path)
    labeled_rows = [row for row in rows if extract_option_id(row.get("review_status")) == "labeled"]
    gold_rows = [build_gold_row(row) for row in labeled_rows]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in gold_rows) + ("\n" if gold_rows else ""),
        encoding="utf-8",
    )
    return len(gold_rows)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export labeled coach workbook v2 rows to JSONL gold labels.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_XLSX)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    row_count = export_workbook_to_jsonl(args.input, args.output_jsonl)
    print(json.dumps({"output_jsonl": str(args.output_jsonl), "row_count": row_count}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
