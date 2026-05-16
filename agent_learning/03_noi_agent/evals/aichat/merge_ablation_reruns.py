"""Merge successful targeted ablation reruns back into a complete run pack.

The source run is never modified. Successful retry rows replace matching
condition-case pairs in a new output directory, then summary and review
workbook artifacts are regenerated from the merged JSONL.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from evals.aichat.export_coach_response_review_workbook import export_response_review_workbook
from evals.aichat.export_coach_response_review_workbook_xlsx import export_xlsx
from evals.aichat.run_bridge_offline_eval import write_result_rows
from evals.aichat.summarize_bridge_offline_eval import summarize_bridge_offline_results, write_summary_files


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


def _manifest_path(base_dir: Path, value: str | None) -> Path:
    if not value:
        raise ValueError("manifest missing combined_jsonl")
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    return base_dir / path


def _pair(row: dict) -> tuple[str, str]:
    return (str(row.get("case_id") or ""), str(row.get("condition_id") or ""))


def _public_pair(pair: tuple[str, str]) -> dict:
    return {"case_id": pair[0], "condition_id": pair[1]}


def _load_manifest(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_manifest_rows(manifest_path: Path) -> tuple[dict, list[dict]]:
    manifest_path = Path(manifest_path)
    manifest = _load_manifest(manifest_path)
    combined_path = _manifest_path(manifest_path.parent, manifest.get("combined_jsonl"))
    return manifest, _read_jsonl(combined_path)


def merge_ablation_reruns(
    *,
    source_manifest: Path,
    retry_manifests: list[Path],
    output_dir: Path,
    shuffle_seed: int = 17,
    summarize_fn: Callable = summarize_bridge_offline_results,
    write_summary_fn: Callable = write_summary_files,
    export_review_fn: Callable = export_response_review_workbook,
    export_xlsx_fn: Callable = export_xlsx,
) -> dict:
    if not retry_manifests:
        raise ValueError("At least one --retry-manifest is required")

    source_manifest = Path(source_manifest)
    output_dir = Path(output_dir)
    source, source_rows = _load_manifest_rows(source_manifest)
    retry_rows: list[dict] = []
    for retry_manifest in retry_manifests:
        _, rows = _load_manifest_rows(Path(retry_manifest))
        retry_rows.extend(rows)

    retry_by_pair = {_pair(row): row for row in retry_rows}
    merged_rows = []
    replaced_pairs = []
    skipped_retry_pairs = []
    source_pairs = {_pair(row) for row in source_rows}

    for row in source_rows:
        pair = _pair(row)
        retry_row = retry_by_pair.get(pair)
        if retry_row and str(retry_row.get("final_response_text") or "").strip():
            merged_rows.append(retry_row)
            replaced_pairs.append(_public_pair(pair))
        else:
            merged_rows.append(row)
            if retry_row:
                skipped_retry_pairs.append(_public_pair(pair))

    for pair, retry_row in sorted(retry_by_pair.items()):
        if pair not in source_pairs:
            skipped_retry_pairs.append(_public_pair(pair))

    output_dir.mkdir(parents=True, exist_ok=True)
    combined_jsonl = output_dir / "combined_dev_ablation.jsonl"
    write_result_rows(combined_jsonl, merged_rows)

    summary = summarize_fn(merged_rows)
    summary_json = output_dir / "combined_dev_ablation_summary.json"
    summary_md = output_dir / "combined_dev_ablation_summary.md"
    summary_md_zh = output_dir / "combined_dev_ablation_summary.zh.md"
    write_summary_fn(summary_json, summary_md, summary, summary_md_zh)

    review_csv = output_dir / "coach_response_review_workbook_dev_ablation.csv"
    review_key_csv = output_dir / "coach_response_review_workbook_dev_ablation.key.csv"
    review_row_count = export_review_fn(
        input_jsonl=combined_jsonl,
        output_csv=review_csv,
        key_csv=review_key_csv,
        shuffle_seed=shuffle_seed,
        id_salt=output_dir.name,
    )
    review_xlsx = output_dir / "coach_response_review_workbook_dev_ablation.zh.xlsx"
    export_xlsx_fn(input_csv=review_csv, output_xlsx=review_xlsx)

    manifest = {
        "source_manifest": str(source_manifest),
        "retry_manifests": [str(path) for path in retry_manifests],
        "input_jsonl": source.get("input_jsonl", ""),
        "output_dir": str(output_dir),
        "case_count": source.get("case_count"),
        "condition_set": source.get("condition_set"),
        "condition_count": source.get("condition_count"),
        "conditions": source.get("conditions") or [],
        "combined_row_count": len(merged_rows),
        "combined_jsonl": str(combined_jsonl),
        "summary_json": str(summary_json),
        "summary_md": str(summary_md),
        "summary_md_zh": str(summary_md_zh),
        "review_csv": str(review_csv),
        "review_key_csv": str(review_key_csv),
        "review_xlsx": str(review_xlsx),
        "review_row_count": review_row_count,
        "replaced_pairs": replaced_pairs,
        "skipped_retry_pairs": skipped_retry_pairs,
        "merged_from_targeted_rerun": True,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge successful targeted ablation reruns into a new run pack.")
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--retry-manifest", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--shuffle-seed", type=int, default=17)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    manifest = merge_ablation_reruns(
        source_manifest=args.source_manifest,
        retry_manifests=args.retry_manifest,
        output_dir=args.output_dir,
        shuffle_seed=args.shuffle_seed,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
