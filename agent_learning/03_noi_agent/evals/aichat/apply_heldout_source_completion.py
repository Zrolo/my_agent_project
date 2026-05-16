"""Merge completed real-source metadata back into a held-out JSONL draft."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from evals.aichat.export_heldout_source_completion_workbook import (
    DEFAULT_INPUT_JSONL,
    SOURCE_METADATA_FIELDS,
    load_jsonl,
)


DEFAULT_SOURCE_CSV = Path("docs/research/heldout_50_source_completion_workbook_20260513.csv")
DEFAULT_OUTPUT_JSONL = Path("docs/research/bridgebench_cp_heldout_v1_50_with_sources_20260513.jsonl")


def load_source_rows(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {str(row.get("case_id") or ""): row for row in rows if row.get("case_id")}


def _is_complete_source_row(row: dict) -> bool:
    required = [
        "problem_source_platform",
        "problem_source_id",
        "problem_source_url",
        "problem_statement",
        "problem_statement_public_summary",
        "problem_statement_rights_note",
        "problem_statement_access_level",
    ]
    return all(str(row.get(field) or "").strip() for field in required)


def apply_source_completion(
    *,
    input_jsonl: Path = DEFAULT_INPUT_JSONL,
    source_csv: Path = DEFAULT_SOURCE_CSV,
    output_jsonl: Path = DEFAULT_OUTPUT_JSONL,
    require_complete: bool = False,
) -> dict[str, int]:
    rows = load_jsonl(input_jsonl)
    source_by_case_id = load_source_rows(source_csv)
    updated = []
    missing_source_rows = 0
    incomplete_rows = 0

    for row in rows:
        case_id = str(row.get("case_id") or row.get("id") or "")
        source_row = source_by_case_id.get(case_id)
        if not source_row:
            missing_source_rows += 1
            if require_complete:
                continue
            updated.append(row)
            continue
        if not _is_complete_source_row(source_row):
            incomplete_rows += 1
            if require_complete:
                continue
        merged = dict(row)
        for field in SOURCE_METADATA_FIELDS:
            value = source_row.get(field)
            if value is not None and str(value).strip():
                merged[field] = str(value).strip()
        updated.append(merged)

    if require_complete and (missing_source_rows or incomplete_rows or len(updated) != len(rows)):
        raise ValueError(
            "source completion is incomplete: "
            f"missing_source_rows={missing_source_rows}, incomplete_rows={incomplete_rows}"
        )

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    output_jsonl.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in updated) + "\n",
        encoding="utf-8",
    )
    return {
        "updated": len(updated),
        "missing_source_rows": missing_source_rows,
        "incomplete_rows": incomplete_rows,
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply held-out source-completion CSV to JSONL.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_JSONL)
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        summary = apply_source_completion(
            input_jsonl=args.input_jsonl,
            source_csv=args.source_csv,
            output_jsonl=args.output_jsonl,
            require_complete=args.require_complete,
        )
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "output_jsonl": str(args.output_jsonl), **summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
