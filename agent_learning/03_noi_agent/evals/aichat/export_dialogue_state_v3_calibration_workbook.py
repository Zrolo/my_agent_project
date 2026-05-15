"""Export a small calibration workbook for dialogue-state v3 case review."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evals.aichat.generate_dialogue_state_v3_50 import _load_jsonl
from evals.aichat.generate_dialogue_state_v3_50 import export_dialogue_state_review_workbook


DEFAULT_SOURCE_JSONL = Path("docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl")
DEFAULT_OUTPUT_ZH_XLSX = Path("docs/research/dialogue_state_v3_case_review_calibration_6.zh.xlsx")
DEFAULT_OUTPUT_EN_XLSX = Path("docs/research/dialogue_state_v3_case_review_calibration_6.en.xlsx")
DEFAULT_REPORT_JSON = Path("docs/research/dialogue_state_v3_case_review_calibration_6_20260515.json")
DEFAULT_REPORT_ZH = Path("docs/research/dialogue_state_v3_case_review_calibration_6_20260515.zh.md")
DEFAULT_REPORT_EN = Path("docs/research/dialogue_state_v3_case_review_calibration_6_20260515.md")

CALIBRATION_CONTEXTS = [
    "initial_question",
    "followup_after_correct_short_answer",
    "followup_after_partial_answer",
    "followup_after_wrong_answer",
    "followup_after_prerequisite_gap",
    "policy_direct_answer_special",
]

CALIBRATION_CASE_PREFIXES = [
    "dialogue_v3_001_",
    "dialogue_v3_011_",
    "dialogue_v3_018_",
    "dialogue_v3_026_",
    "dialogue_v3_043_",
    "dialogue_v3_048_",
]


def select_calibration_cases(rows: list[dict]) -> list[dict]:
    """Select one representative row for each case/source review category."""
    by_prefix = []
    for prefix in CALIBRATION_CASE_PREFIXES:
        match = next((row for row in rows if str(row.get("case_id") or "").startswith(prefix)), None)
        if match is None:
            break
        by_prefix.append(match)
    if len(by_prefix) == len(CALIBRATION_CASE_PREFIXES):
        return by_prefix

    selected = []
    for context_type in CALIBRATION_CONTEXTS:
        match = next((row for row in rows if row.get("context_type") == context_type), None)
        if match is None:
            raise ValueError(f"Missing calibration context_type: {context_type}")
        selected.append(match)
    return selected


def build_report(rows: list[dict], *, source_path: Path) -> dict:
    return {
        "source_jsonl": str(source_path),
        "row_count": len(rows),
        "case_ids": [row.get("case_id") for row in rows],
        "context_type_counts": dict(Counter(row.get("context_type") for row in rows)),
        "followability_counts": dict(Counter(row.get("student_scaffold_followability") for row in rows)),
        "reference_label_status": "calibration_case_source_review_only",
        "ok": len(rows) == len(CALIBRATION_CONTEXTS),
    }


def _write_report_markdown(report: dict, path: Path, *, language: str) -> None:
    is_zh = language == "zh"
    lines = [
        "# Dialogue-State v3 Case Review Calibration Workbook"
        if not is_zh
        else "# Dialogue-State v3 Case Review Calibration Workbook（6 条校准）",
        "",
        (
            "本表用于让教练先试填 case/source 审核字段。它不是正式 50-case 审核结果，也不评价 AI 回复。"
            if is_zh
            else "This workbook is for a small coach calibration pass on case/source review fields. It is not the formal 50-case review result and does not score AI responses."
        ),
        "",
        f"- row_count: {report['row_count']}",
        f"- source_jsonl: `{report['source_jsonl']}`",
        f"- reference_label_status: `{report['reference_label_status']}`",
        f"- context_type_counts: `{report['context_type_counts']}`",
        f"- followability_counts: `{report['followability_counts']}`",
        "",
        "## Case IDs",
        "",
        *[f"- `{case_id}`" for case_id in report["case_ids"]],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export dialogue-state v3 case/source calibration workbook.")
    parser.add_argument("--source-jsonl", type=Path, default=DEFAULT_SOURCE_JSONL)
    parser.add_argument("--output-zh-xlsx", type=Path, default=DEFAULT_OUTPUT_ZH_XLSX)
    parser.add_argument("--output-en-xlsx", type=Path, default=DEFAULT_OUTPUT_EN_XLSX)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-zh", type=Path, default=DEFAULT_REPORT_ZH)
    parser.add_argument("--report-en", type=Path, default=DEFAULT_REPORT_EN)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    rows = select_calibration_cases(_load_jsonl(args.source_jsonl))
    export_dialogue_state_review_workbook(rows, args.output_zh_xlsx, language="zh")
    export_dialogue_state_review_workbook(rows, args.output_en_xlsx, language="en")
    report = build_report(rows, source_path=args.source_jsonl)
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_report_markdown(report, args.report_zh, language="zh")
    _write_report_markdown(report, args.report_en, language="en")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
