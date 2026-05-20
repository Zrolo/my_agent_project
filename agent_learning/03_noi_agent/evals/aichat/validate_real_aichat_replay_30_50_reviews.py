#!/usr/bin/env python3
"""Validate Real-AIChat-Replay-30/50 blind coach-review CSV files.

Observed current AIChat responses may appear only as observed references and
are not counted as offline harness responses. This script does not run replay,
does not generate responses, and does not touch online AIChat.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


DEFAULT_INPUT = Path("docs/research/real_aichat_replay_30_50_coach_review_template_v1.csv")
DEFAULT_SCHEMA = Path("docs/research/real_aichat_replay_30_50_coach_review_schema_v1.json")
MAX_OFFLINE_HARNESSES_PER_CASE = 7

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

DANGEROUS_NAMING_TOKENS = {
    "baseline",
    "control",
    "online_condition",
    "online condition",
    "baseline condition",
    "control condition",
}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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

    enum_by_field = {
        field: set(spec.get("enum", []))
        for field, spec in properties.items()
        if isinstance(spec, dict) and spec.get("enum")
    }

    seen_response_ids: dict[str, int] = {}
    offline_harnesses_by_case: dict[str, set[str]] = defaultdict(set)

    for index, row in enumerate(rows, start=2):
        row_id = _clean(row.get("anonymized_response_id")) or f"line_{index}"
        case_id = _clean(row.get("replay_case_id"))

        if row_id in seen_response_ids:
            errors.append(
                f"{row_id}: duplicate anonymized_response_id; first seen on line {seen_response_ids[row_id]}"
            )
        else:
            seen_response_ids[row_id] = index

        for field in required:
            if not _clean(row.get(field)):
                errors.append(f"{row_id}: required field '{field}' is empty")

        for field, allowed in enum_by_field.items():
            value = _clean(row.get(field))
            if value and value not in allowed:
                errors.append(
                    f"{row_id}: invalid value for '{field}': {value!r}; allowed={sorted(allowed)}"
                )

        response_role = _clean(row.get("response_role"))
        if _clean(row.get("condition_hidden_from_reviewer")) != "yes":
            errors.append(
                f"{row_id}: condition_hidden_from_reviewer must be yes for blind coach review"
            )

        if response_role == "offline_harness_response":
            offline_harnesses_by_case[case_id].add(_clean(row.get("harness_name_private_or_redacted")))

        for field in ["condition_name_private_or_redacted", "harness_name_private_or_redacted"]:
            value = _clean(row.get(field)).lower()
            if any(token in value for token in DANGEROUS_NAMING_TOKENS):
                warnings.append(
                    f"{row_id}: dangerous naming token in {field}; avoid baseline/control/online-condition wording"
                )

    for case_id, harnesses in offline_harnesses_by_case.items():
        if len(harnesses) > MAX_OFFLINE_HARNESSES_PER_CASE:
            errors.append(
                f"{case_id}: more than 7 offline harness responses counted ({len(harnesses)})"
            )

    return {
        "ok": not errors,
        "total_rows": len(rows),
        "errors": errors,
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Real-AIChat-Replay-30/50 blind coach-review CSV."
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
