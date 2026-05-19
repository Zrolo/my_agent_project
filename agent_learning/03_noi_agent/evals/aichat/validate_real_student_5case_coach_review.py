#!/usr/bin/env python3
"""Validate local-only 5-case real-student coach review packets.

This validator checks the schema and reporting gates for the real-student
online dry-run coach review packet. It does not read, recompute, or modify
dialogue-state v3 main experiment data.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_INPUT = Path(".local_private/real_student_online_5case_coach_review_packet_20260519.csv")
DEFAULT_SCHEMA = Path("docs/research/real_student_online_5case_coach_review_schema_v1.json")
DEFAULT_EXPECTED_ROWS = 5

OPTIONALLY_EMPTY_FIELDS = {
    "recent_dialogue_redacted",
    "student_code_excerpt_redacted",
    "coach_context_sufficiency",
    "coach_missing_bridge_family",
    "coach_missing_bridge_instance",
    "coach_forbidden_content",
    "coach_acceptable_reveal",
    "coach_expected_next_student_action",
    "coach_current_aichat_leakage_concern",
    "coach_matches_existing_taxonomy",
    "coach_new_bridge_candidate",
    "coach_observed_next_turn_progress",
    "coach_field_sufficiency_notes",
    "coach_disagrees_with_ai_preannotation",
    "adjudication_needed",
    "coach_notes",
}

REVIEWED_REQUIRED_FIELDS = {
    "coach_privacy_review_status",
    "coach_context_sufficiency",
    "coach_current_aichat_leakage_concern",
    "coach_matches_existing_taxonomy",
    "coach_disagrees_with_ai_preannotation",
    "adjudication_needed",
}

BRIDGE_REQUIRED_WHEN_CONTEXT_AVAILABLE = {
    "coach_missing_bridge_family",
    "coach_missing_bridge_instance",
    "coach_forbidden_content",
    "coach_acceptable_reveal",
    "coach_expected_next_student_action",
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
    warnings: list[str] = []
    required = list(schema.get("required", []))
    properties = schema.get("properties", {})

    missing_columns = [field for field in required if field not in header]
    extra_columns = [field for field in header if field not in properties]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    if extra_columns:
        errors.append(f"Unexpected columns not in schema: {', '.join(extra_columns)}")

    if len(rows) != expected_rows:
        errors.append(f"Expected {expected_rows} coach-review rows, found {len(rows)}")

    enum_by_field = {
        field: set(spec.get("enum", []))
        for field, spec in properties.items()
        if isinstance(spec, dict) and spec.get("enum")
    }

    seen_candidate_ids: dict[str, int] = {}
    reviewed_rows = 0
    reportable_after_consent = 0

    for index, row in enumerate(rows, start=2):
        row_id = _clean(row.get("candidate_turn_id")) or f"line_{index}"
        if row_id in seen_candidate_ids:
            errors.append(
                f"{row_id}: duplicate candidate_turn_id; first seen on line {seen_candidate_ids[row_id]}"
            )
        else:
            seen_candidate_ids[row_id] = index

        for field in required:
            if field in OPTIONALLY_EMPTY_FIELDS:
                continue
            if not _clean(row.get(field)):
                errors.append(f"{row_id}: required field '{field}' is empty")

        for field, allowed in enum_by_field.items():
            value = _clean(row.get(field))
            if value not in allowed:
                errors.append(
                    f"{row_id}: invalid value for '{field}': {value!r}; allowed={sorted(allowed)}"
                )

        if _clean(row.get("consent_reporting_gate")) != "eligible":
            warnings.append(
                f"{row_id}: not reportable deep-pilot evidence until consent_reporting_gate=eligible"
            )

        review_status = _clean(row.get("coach_review_status"))
        if review_status == "reviewed":
            reviewed_rows += 1
            for field in REVIEWED_REQUIRED_FIELDS:
                if not _clean(row.get(field)):
                    errors.append(f"{row_id}: reviewed row requires {field}")
            if _clean(row.get("coach_privacy_review_status")) != "passed_for_internal_review":
                errors.append(
                    f"{row_id}: reviewed row requires coach_privacy_review_status=passed_for_internal_review"
                )

            context = _clean(row.get("coach_context_sufficiency"))
            if context in {"sufficient", "partial"}:
                for field in BRIDGE_REQUIRED_WHEN_CONTEXT_AVAILABLE:
                    if not _clean(row.get(field)):
                        errors.append(f"{row_id}: context={context} requires {field}")
            elif context in {"insufficient", "unclear"}:
                if _clean(row.get("coach_current_aichat_leakage_concern")) not in {
                    "unclear",
                    "not_judged_insufficient_context",
                }:
                    errors.append(
                        f"{row_id}: context={context} requires leakage concern to be unclear or not_judged_insufficient_context"
                    )

            if _clean(row.get("consent_reporting_gate")) == "eligible":
                reportable_after_consent += 1

    return {
        "ok": not errors,
        "total_rows": len(rows),
        "expected_rows": expected_rows,
        "reviewed_rows_count": reviewed_rows,
        "reportable_after_consent_count": reportable_after_consent,
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate local-only real-student online 5-case coach-review packet."
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
