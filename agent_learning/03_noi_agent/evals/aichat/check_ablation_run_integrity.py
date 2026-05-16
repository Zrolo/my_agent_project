"""Check ablation-run artifacts before analysis or paper reporting.

This checker is intentionally conservative: any missing condition-case pair,
empty final response, or review-workbook mismatch blocks headline readiness.
Stage errors with a non-empty final response are kept as warnings.
"""

from __future__ import annotations

import argparse
import csv
import json
import shlex
from collections import Counter
from pathlib import Path


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


def _read_csv_row_count(path: Path | None) -> int | None:
    if path is None or not path.exists():
        return None
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _manifest_path(base_dir: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    if path.exists():
        return path
    return base_dir / path


def _row_pair(row: dict) -> tuple[str, str]:
    return (str(row.get("case_id") or ""), str(row.get("condition_id") or ""))


def _public_pair(pair: tuple[str, str]) -> dict:
    return {"case_id": pair[0], "condition_id": pair[1]}


def _dedupe_public_pairs(pairs: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for pair in pairs:
        key = (str(pair.get("case_id") or ""), str(pair.get("condition_id") or ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append({"case_id": key[0], "condition_id": key[1]})
    return deduped


def _targeted_rerun_commands(manifest: dict, manifest_path: Path, pairs: list[dict]) -> list[str]:
    if not pairs or not manifest.get("input_jsonl"):
        return []
    output_root = manifest.get("output_dir")
    if output_root:
        retry_root = f"{output_root}_targeted_rerun"
    else:
        retry_root = str(manifest_path.parent / "targeted_rerun")
    condition_set = manifest.get("condition_set") or "default"
    by_condition: dict[str, list[str]] = {}
    for pair in pairs:
        by_condition.setdefault(pair["condition_id"], []).append(pair["case_id"])

    commands = []
    for condition_id, case_ids in sorted(by_condition.items()):
        parts = [
            "python3",
            "-m",
            "evals.aichat.run_dev_ablation_suite",
            "--input-jsonl",
            str(manifest["input_jsonl"]),
            "--output-dir",
            str(Path(retry_root) / condition_id),
            "--condition-set",
            condition_set,
            "--condition-id",
            condition_id,
        ]
        for case_id in case_ids:
            parts.extend(["--case-id", case_id])
        commands.append(" ".join(shlex.quote(part) for part in parts))
    return commands


def check_run_integrity(manifest_path: Path) -> dict:
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base_dir = manifest_path.parent
    combined_path = _manifest_path(base_dir, manifest.get("combined_jsonl"))
    if combined_path is None:
        raise ValueError("manifest missing combined_jsonl")
    review_csv_path = _manifest_path(base_dir, manifest.get("review_csv"))
    rows = _read_jsonl(combined_path)

    conditions = [condition.get("condition_id", "") for condition in manifest.get("conditions") or []]
    if not conditions:
        conditions = sorted({str(row.get("condition_id") or "") for row in rows if row.get("condition_id")})
    case_ids = sorted({str(row.get("case_id") or "") for row in rows if row.get("case_id")})
    manifest_case_count = int(manifest.get("case_count") or len(case_ids))
    expected_row_count = manifest_case_count * len(conditions)

    present_pairs = [_row_pair(row) for row in rows]
    pair_counts = Counter(present_pairs)
    duplicate_pairs = [_public_pair(pair) for pair, count in sorted(pair_counts.items()) if count > 1]
    expected_pairs = {(case_id, condition_id) for case_id in case_ids for condition_id in conditions}
    missing_pairs = [_public_pair(pair) for pair in sorted(expected_pairs - set(pair_counts))]

    empty_final_response_rows = [
        _public_pair(_row_pair(row))
        for row in rows
        if not str(row.get("final_response_text") or "").strip()
    ]
    stage_warning_rows = [
        {
            "case_id": str(row.get("case_id") or ""),
            "condition_id": str(row.get("condition_id") or ""),
            "stage_errors": row.get("stage_errors") or {},
        }
        for row in rows
        if str(row.get("final_response_text") or "").strip() and row.get("stage_errors")
    ]
    final_response_row_count = len(rows) - len(empty_final_response_rows)
    review_row_count = _read_csv_row_count(review_csv_path)

    blocking_reasons = []
    if len(rows) != expected_row_count:
        blocking_reasons.append("combined_row_count_mismatch")
    if missing_pairs:
        blocking_reasons.append("missing_condition_case_pairs")
    if duplicate_pairs:
        blocking_reasons.append("duplicate_condition_case_pairs")
    if empty_final_response_rows:
        blocking_reasons.append("empty_final_response_rows")
    if review_row_count is None:
        blocking_reasons.append("missing_review_csv")
    elif review_row_count != final_response_row_count:
        blocking_reasons.append("review_row_count_mismatch")
    targeted_rerun_pairs = _dedupe_public_pairs(missing_pairs + empty_final_response_rows)

    return {
        "manifest": str(manifest_path),
        "combined_jsonl": str(combined_path),
        "review_csv": str(review_csv_path) if review_csv_path else "",
        "case_count": manifest_case_count,
        "condition_count": len(conditions),
        "conditions": conditions,
        "expected_row_count": expected_row_count,
        "combined_row_count": len(rows),
        "final_response_row_count": final_response_row_count,
        "review_row_count": review_row_count,
        "missing_pairs": missing_pairs,
        "duplicate_pairs": duplicate_pairs,
        "empty_final_response_rows": empty_final_response_rows,
        "targeted_rerun_pairs": targeted_rerun_pairs,
        "targeted_rerun_commands": _targeted_rerun_commands(manifest, manifest_path, targeted_rerun_pairs),
        "stage_warning_rows": stage_warning_rows,
        "blocking_reasons": blocking_reasons,
        "warning_reasons": ["stage_errors_present"] if stage_warning_rows else [],
        "headline_ready": not blocking_reasons and not stage_warning_rows,
        "analysis_ready": not blocking_reasons,
    }


def write_markdown_report(report: dict, output_md: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Ablation Run Integrity Report",
        "",
        f"- Manifest: `{report['manifest']}`",
        f"- Expected rows: {report['expected_row_count']}",
        f"- Combined rows: {report['combined_row_count']}",
        f"- Final response rows: {report['final_response_row_count']}",
        f"- Review rows: {report['review_row_count']}",
        f"- Analysis ready: {report['analysis_ready']}",
        f"- Headline ready: {report['headline_ready']}",
        "",
        "## Blocking Reasons",
        "",
        json.dumps(report["blocking_reasons"], ensure_ascii=False, indent=2),
        "",
        "## Warnings",
        "",
        json.dumps(report["warning_reasons"], ensure_ascii=False, indent=2),
        "",
        "## Empty Final Response Rows",
        "",
        json.dumps(report["empty_final_response_rows"], ensure_ascii=False, indent=2),
        "",
        "## Targeted Rerun Pairs",
        "",
        json.dumps(report["targeted_rerun_pairs"], ensure_ascii=False, indent=2),
        "",
        "## Targeted Rerun Commands",
        "",
        "```bash",
        "\n".join(report["targeted_rerun_commands"]),
        "```",
        "",
        "## Stage Warning Rows",
        "",
        json.dumps(report["stage_warning_rows"], ensure_ascii=False, indent=2),
        "",
    ]
    output_md.write_text("\n".join(lines), encoding="utf-8")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check ablation-run output integrity.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    report = check_run_integrity(args.manifest)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        write_markdown_report(report, args.output_md)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["analysis_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
