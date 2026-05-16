"""Export a small calibration/re-check workbook for dialogue-state v3 case review."""

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
DEFAULT_REPORT_JSON = Path("docs/research/dialogue_state_v3_calibration_6_report_20260515.json")
DEFAULT_REPORT_ZH = Path("docs/research/dialogue_state_v3_calibration_6_report_20260515.zh.md")
DEFAULT_REPORT_EN = Path("docs/research/dialogue_state_v3_calibration_6_report_20260515.md")
LEGACY_REPORT_JSON = Path("docs/research/dialogue_state_v3_case_review_calibration_6_20260515.json")
LEGACY_REPORT_ZH = Path("docs/research/dialogue_state_v3_case_review_calibration_6_20260515.zh.md")
LEGACY_REPORT_EN = Path("docs/research/dialogue_state_v3_case_review_calibration_6_20260515.md")

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

COACH_A_ROUND1_RECHECK_PREFIXES = [
    "dialogue_v3_027_",
    "dialogue_v3_028_",
    "dialogue_v3_029_",
    "dialogue_v3_030_",
    "dialogue_v3_031_",
    "dialogue_v3_032_",
    "dialogue_v3_033_",
    "dialogue_v3_034_",
    "dialogue_v3_035_",
    "dialogue_v3_036_",
    "dialogue_v3_037_",
    "dialogue_v3_038_",
    "dialogue_v3_039_",
    "dialogue_v3_040_",
    "dialogue_v3_044_",
    "dialogue_v3_045_",
    "dialogue_v3_046_",
    "dialogue_v3_047_",
]


def select_calibration_cases(rows: list[dict]) -> list[dict]:
    """Select fixed coach-calibration rows, with context coverage as fallback."""
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


def select_cases_by_prefixes(rows: list[dict], prefixes: list[str]) -> list[dict]:
    """Select rows by fixed case-id prefixes, preserving prefix order."""
    selected = []
    missing = []
    for prefix in prefixes:
        match = next((row for row in rows if str(row.get("case_id") or "").startswith(prefix)), None)
        if match is None:
            missing.append(prefix)
        else:
            selected.append(match)
    if missing:
        raise ValueError(f"Missing case_id prefixes: {missing}")
    return selected


def build_report(
    rows: list[dict],
    *,
    source_path: Path,
    required_case_prefixes: list[str] | None = None,
    reference_label_status: str = "calibration_case_source_review_only",
    selection_label: str | None = None,
) -> dict:
    required_prefixes = required_case_prefixes or CALIBRATION_CASE_PREFIXES
    case_ids = [str(row.get("case_id") or "") for row in rows]
    selected_fixed_prefixes = [
        prefix
        for prefix in required_prefixes
        if any(case_id.startswith(prefix) for case_id in case_ids)
    ]
    case_id_prefix_ok = selected_fixed_prefixes == required_prefixes
    context_coverage_ok = set(CALIBRATION_CONTEXTS).issubset(
        {str(row.get("context_type") or "") for row in rows}
    )
    if selection_label:
        selection_mode = selection_label
    else:
        selection_mode = "fixed_case_recheck" if case_id_prefix_ok else "context_coverage_fallback"
    return {
        "source_jsonl": str(source_path),
        "row_count": len(rows),
        "case_ids": case_ids,
        "required_case_prefixes": required_prefixes,
        "selected_fixed_prefixes": selected_fixed_prefixes,
        "case_id_prefix_ok": case_id_prefix_ok,
        "selection_mode": selection_mode,
        "context_coverage_ok": context_coverage_ok,
        "context_type_counts": dict(Counter(row.get("context_type") for row in rows)),
        "followability_counts": dict(Counter(row.get("student_scaffold_followability") for row in rows)),
        "reference_label_status": reference_label_status,
        "ok": len(rows) == len(required_prefixes) and (case_id_prefix_ok or context_coverage_ok),
    }


def _write_report_markdown(report: dict, path: Path, *, language: str) -> None:
    is_zh = language == "zh"
    is_targeted = "targeted_recheck" in str(report.get("selection_mode") or "") or str(
        report.get("reference_label_status") or ""
    ).endswith("recheck_only")
    title = (
        "Dialogue-State v3 Targeted Re-check Workbook"
        if is_targeted and not is_zh
        else "Dialogue-State v3 Case Review Calibration Workbook"
        if not is_zh
        else "Dialogue-State v3 Targeted Re-check Workbook（定向复核）"
        if is_targeted
        else "Dialogue-State v3 Case Review Calibration Workbook（6 条校准）"
    )
    intro = (
        "本表用于定向复核前一轮 case/source 审核后仍需处理的样本；它不是正式 50-case 审核结果，也不评价 AI 回复。"
        if is_zh and is_targeted
        else "This workbook is for a targeted re-check of cases that still needed action after a prior case/source review pass. It is not the formal 50-case review result and does not score AI responses."
        if is_targeted
        else "本表用于让教练先试填或复核 case/source 审核字段。当前默认选取固定的 6 条校准/修订样本，不是 F1-F4 全类别分层样本；它不是正式 50-case 审核结果，也不评价 AI 回复。"
        if is_zh
        else "This workbook is for a small coach calibration or re-check pass on case/source review fields. The default selection uses six fixed calibration/revision cases, not a stratified F1-F4 coverage sample. It is not the formal 50-case review result and does not score AI responses."
    )
    lines = [
        f"# {title}",
        "",
        intro,
        "",
        f"- row_count: {report['row_count']}",
        f"- source_jsonl: `{report['source_jsonl']}`",
        f"- reference_label_status: `{report['reference_label_status']}`",
        f"- selection_mode: `{report['selection_mode']}`",
        f"- case_id_prefix_ok: `{report['case_id_prefix_ok']}`",
        f"- context_coverage_ok: `{report['context_coverage_ok']}`",
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
    parser.add_argument(
        "--case-id-prefix",
        action="append",
        default=None,
        help="Case-id prefix to include. Repeat to export a targeted re-check workbook.",
    )
    parser.add_argument(
        "--coach-a-round1-recheck",
        action="store_true",
        help="Export the fixed 18 Coach A round1 revised cases for targeted re-check.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    source_rows = _load_jsonl(args.source_jsonl)
    if args.coach_a_round1_recheck:
        prefixes = COACH_A_ROUND1_RECHECK_PREFIXES
        rows = select_cases_by_prefixes(source_rows, prefixes)
        reference_label_status = "coach_A_round1_targeted_recheck_only"
        selection_label = "coach_A_round1_targeted_recheck"
    elif args.case_id_prefix:
        prefixes = args.case_id_prefix
        rows = select_cases_by_prefixes(source_rows, prefixes)
        reference_label_status = "targeted_case_source_recheck_only"
        selection_label = "explicit_case_prefixes"
    else:
        prefixes = CALIBRATION_CASE_PREFIXES
        rows = select_calibration_cases(source_rows)
        reference_label_status = "calibration_case_source_review_only"
        selection_label = None
    export_dialogue_state_review_workbook(rows, args.output_zh_xlsx, language="zh")
    export_dialogue_state_review_workbook(rows, args.output_en_xlsx, language="en")
    report = build_report(
        rows,
        source_path=args.source_jsonl,
        required_case_prefixes=prefixes,
        reference_label_status=reference_label_status,
        selection_label=selection_label,
    )
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_report_markdown(report, args.report_zh, language="zh")
    _write_report_markdown(report, args.report_en, language="en")
    if args.report_json == DEFAULT_REPORT_JSON:
        LEGACY_REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.report_zh == DEFAULT_REPORT_ZH:
        _write_report_markdown(report, LEGACY_REPORT_ZH, language="zh")
    if args.report_en == DEFAULT_REPORT_EN:
        _write_report_markdown(report, LEGACY_REPORT_EN, language="en")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
