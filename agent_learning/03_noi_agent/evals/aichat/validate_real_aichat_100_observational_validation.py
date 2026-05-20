#!/usr/bin/env python3
"""Validate Real-AIChat-100 observational validation CSV files.

This script only checks the external-validation manifest/template shape. It
does not read private packets, does not recompute dialogue-state v3 tables, and
does not call online AIChat.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_INPUT = Path("docs/research/real_aichat_100_observational_validation_template_v1.csv")
DEFAULT_SCHEMA = Path("docs/research/real_aichat_100_observational_validation_schema_v1.json")

RAW_OR_IDENTITY_FIELD_NAMES = {
    "raw_student_text",
    "full_student_code",
    "full_aichat_response",
    "phone",
    "email",
    "school",
    "real_name",
    "hash_salt",
    "reversible_mapping",
}

MAY_BE_EMPTY_FIELDS = {"exclusion_reason", "notes_no_raw_text"}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _enum_by_field(schema: dict) -> dict[str, set[str]]:
    return {
        field: set(spec.get("enum", []))
        for field, spec in schema.get("properties", {}).items()
        if isinstance(spec, dict) and spec.get("enum")
    }


def validate(rows: list[dict[str, str]], header: list[str], schema: dict) -> dict[str, object]:
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

    forbidden_headers = [field for field in header if field in RAW_OR_IDENTITY_FIELD_NAMES]
    if forbidden_headers:
        errors.append(
            "Raw or identity fields are not allowed in this public template/manifest: "
            + ", ".join(forbidden_headers)
        )

    enum_by_field = _enum_by_field(schema)
    seen_case_ids: dict[str, int] = {}

    for index, row in enumerate(rows, start=2):
        row_id = _clean(row.get("real_aichat_case_id")) or f"line_{index}"
        if row_id in seen_case_ids:
            errors.append(
                f"{row_id}: duplicate real_aichat_case_id; first seen on line {seen_case_ids[row_id]}"
            )
        else:
            seen_case_ids[row_id] = index

        for field in required:
            if field in MAY_BE_EMPTY_FIELDS:
                continue
            if not _clean(row.get(field)):
                errors.append(f"{row_id}: required field '{field}' is empty")

        for field, allowed in enum_by_field.items():
            value = _clean(row.get(field))
            if value and value not in allowed:
                errors.append(
                    f"{row_id}: invalid value for '{field}': {value!r}; allowed={sorted(allowed)}"
                )

        if _clean(row.get("observed_current_aichat_response_role")) != "observed_only_not_condition":
            errors.append(
                f"{row_id}: observed_current_aichat_response_role must be observed_only_not_condition"
            )

        if _clean(row.get("public_reporting_allowed")) == "yes" and _clean(
            row.get("consent_reporting_gate")
        ) not in {"eligible", "consented"}:
            errors.append(
                f"{row_id}: public_reporting_allowed=yes requires consent_reporting_gate=eligible/consented"
            )

        if _clean(row.get("privacy_review_status")) == "failed" and _clean(
            row.get("public_reporting_allowed")
        ) != "no":
            errors.append(
                f"{row_id}: privacy_review_status=failed requires public_reporting_allowed=no"
            )

        if _clean(row.get("candidate_for_replay")) == "yes" and _clean(
            row.get("context_sufficiency_light")
        ) not in {"sufficient", "partial"}:
            errors.append(
                f"{row_id}: candidate_for_replay=yes requires context_sufficiency_light=sufficient/partial"
            )

    return {
        "ok": not errors,
        "total_rows": len(rows),
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Real-AIChat-100 observational ecological-validity manifest/template."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output-json", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    header, rows = read_csv(args.input)
    schema = read_schema(args.schema)
    result = validate(rows, header, schema)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output_json:
        args.output_json.write_text(text + "\n", encoding="utf-8")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
