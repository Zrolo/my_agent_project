#!/usr/bin/env python3
"""Validate real-student online AIChat candidate-turn screening CSV.

This validator is only for the real-student online pilot screening layer.
It does not read, recompute, or modify dialogue-state v3 main experiment data.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_INPUT = Path("docs/research/real_student_online_candidate_screening_form_v1.csv")
DEFAULT_SCHEMA = Path("docs/research/real_student_online_candidate_screening_schema_v1.json")
DEFAULT_EXPECTED_ROWS = 137

CONDITIONALLY_EMPTY_FIELDS = {
    "candidate_selection_reason",
    "exclusion_reason",
    "notes",
}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(rows: list[dict[str, str]], header: list[str], schema: dict, expected_rows: int) -> dict[str, object]:
    errors: list[str] = []
    required = list(schema.get("required", []))
    properties = schema.get("properties", {})

    missing_columns = [field for field in required if field not in header]
    extra_columns = [field for field in header if field not in properties]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    if extra_columns:
        errors.append(f"Unexpected columns not in schema: {', '.join(extra_columns)}")

    if len(rows) != expected_rows:
        errors.append(f"Expected {expected_rows} screening rows, found {len(rows)}")

    enum_by_field = {
        field: set(spec.get("enum", []))
        for field, spec in properties.items()
        if isinstance(spec, dict) and spec.get("enum")
    }

    for index, row in enumerate(rows, start=2):
        row_id = _clean(row.get("candidate_turn_id")) or f"line_{index}"

        for field in required:
            if field in CONDITIONALLY_EMPTY_FIELDS:
                continue
            if not _clean(row.get(field)):
                errors.append(f"{row_id}: required field '{field}' is empty")

        for field, allowed in enum_by_field.items():
            value = _clean(row.get(field))
            if value and value not in allowed:
                errors.append(
                    f"{row_id}: invalid value for '{field}': {value!r}; allowed={sorted(allowed)}"
                )

        selected = _clean(row.get("candidate_for_deep_annotation")) == "yes"
        if selected:
            if not _clean(row.get("candidate_selection_reason")):
                errors.append(
                    f"{row_id}: candidate_for_deep_annotation=yes requires candidate_selection_reason"
                )
            if _clean(row.get("privacy_review_status")) != "passed":
                errors.append(
                    f"{row_id}: selected deep annotation candidate requires privacy_review_status=passed"
                )
            if _clean(row.get("consent_eligibility")) == "not_eligible":
                errors.append(
                    f"{row_id}: selected deep annotation candidate cannot have consent_eligibility=not_eligible"
                )

    selected_rows = [
        row for row in rows if _clean(row.get("candidate_for_deep_annotation")) == "yes"
    ]
    result = {
        "ok": not errors,
        "total_rows": len(rows),
        "expected_rows": expected_rows,
        "selected_deep_candidates_count": len(selected_rows),
        "errors": errors,
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate real-student online AIChat candidate-turn screening CSV."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--expected-rows", type=int, default=DEFAULT_EXPECTED_ROWS)
    parser.add_argument("--output-json", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    header, rows = read_csv(args.input)
    schema = read_schema(args.schema)
    result = validate(rows, header, schema, args.expected_rows)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output_json:
        args.output_json.write_text(text + "\n", encoding="utf-8")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
