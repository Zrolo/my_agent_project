#!/usr/bin/env python3
"""Close out CP-MissingBridgeBench v2 100-case / 700-response review evidence.

This script consumes existing private analyzer outputs and writes aggregate-only
closeout reports plus a freeze manifest. It does not recompute dialogue-state v3
main tables, modify production AIChat, or expose raw student text.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


DESIGN_LABELS = {
    "enhanced_prompt_only_clean": "Prompt-only",
    "codehelp_codeaid_clean": "No-direct-solution help",
    "dbox_inspired_clean": "DBox-inspired",
    "dbox_inspired_guard": "DBox-inspired + Guard",
    "bridge_guided_dbox_style_guard": "Bridge-guided DBox-style + Guard",
    "bridge_contract_compact_guard": "Bridge Contract + Guard",
    "bridge_contract_compact_guard_repair": "Bridge Contract + Guard/Repair",
}

DESIGN_ORDER = [
    "enhanced_prompt_only_clean",
    "codehelp_codeaid_clean",
    "dbox_inspired_clean",
    "dbox_inspired_guard",
    "bridge_guided_dbox_style_guard",
    "bridge_contract_compact_guard",
    "bridge_contract_compact_guard_repair",
]

EXPECTED_CASE_COUNT = 100
EXPECTED_ROW_COUNT = 700
EXPECTED_ROWS_PER_CASE = 7
EXPECTED_ROWS_PER_DESIGN = 100

REQUIRED_REVIEW_FIELDS = [
    "case_id",
    "anonymized_response_id",
    "response_text",
    "overall_quality_score",
    "would_show_to_student",
    "leakage_label",
    "bridge_reveal_justification",
    "student_response_burden",
    "review_status",
    "reviewer_confidence",
]

REQUIRED_SCORE_FIELDS = [
    "bridge_identification",
    "bridge_leakage_control",
    "groundedness",
    "next_step_clarity",
    "scaffold_appropriateness",
    "scaffold_sufficiency",
    "single_focus_coherence",
]

OPTIONAL_SCORE_FIELDS = [
    "bridge_oriented_micro_example",
]

ALLOWED_VALUES = {
    "leakage_label": {"no_leakage", "minor_bridge_leakage", "major_bridge_leakage", "answer_leakage"},
    "would_show_to_student": {"yes", "borderline", "no"},
    "student_response_burden": {"low", "medium", "high"},
    "review_status": {"labeled"},
    "reviewer_confidence": {"low", "medium", "high"},
    "bridge_reveal_justification": {"no_reveal", "pedagogically_justified", "borderline", "unjustified", "unclear"},
}

REQUIRED_PAIRS = [
    ("bridge_contract_compact_guard", "dbox_inspired_guard"),
    ("bridge_guided_dbox_style_guard", "dbox_inspired_guard"),
    ("bridge_contract_compact_guard_repair", "dbox_inspired_guard"),
    ("bridge_contract_compact_guard_repair", "bridge_contract_compact_guard"),
    ("dbox_inspired_guard", "dbox_inspired_clean"),
    ("enhanced_prompt_only_clean", "dbox_inspired_guard"),
    ("codehelp_codeaid_clean", "dbox_inspired_guard"),
]

PUBLIC_PRIVACY_BOUNDARY = (
    "Aggregate-only reporting. Public outputs must not include raw student text, "
    "full student code, complete AIChat responses, real identity fields, hash salts, "
    "or reversible mappings."
)

SAFE_SECOND_REVIEW_KEYS = {
    "status",
    "interpretation",
    "reviewed_rows",
    "sampled_rows",
    "overlap_case_count",
    "paired_cases",
    "agreement_rate",
    "exact_agreement_rate",
    "weighted_kappa",
    "cohen_kappa",
    "krippendorff_alpha",
    "disagreements_count",
    "adjudicated_count",
    "passed",
}

PRIVATE_VALUE_MARKERS = (
    ".local_private",
    "/Users",
    "raw_student_text",
    "full_student_code",
    "full_aichat_response",
    "hash_salt",
    "reversible_mapping",
)


def reader_label(design_id: str) -> str:
    return DESIGN_LABELS.get(design_id, design_id)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_redact_path(path: Path) -> bool:
    path_text = str(path)
    return path.is_absolute() or ".local_private" in path.parts or path_text.startswith("/Users") or "/Users/" in path_text


def artifact_record(path: Path) -> dict:
    exists = path.exists()
    record = {
        "label": path.name,
        "private_path_redacted": should_redact_path(path),
        "exists": exists,
        "bytes": path.stat().st_size if exists else None,
        "sha256": sha256_file(path) if exists else None,
    }
    if not record["private_path_redacted"]:
        record["path"] = str(path)
    return record


def public_safe_scalar(value: object) -> bool:
    if isinstance(value, bool) or value is None:
        return True
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        return len(value) <= 300 and not any(marker in value for marker in PRIVATE_VALUE_MARKERS)
    return False


def sanitize_second_review_summary(second_review_summary: dict | None) -> dict:
    if not second_review_summary:
        return {
            "status": "not_linked_in_closeout_run",
            "interpretation": "Report as single-coach expert review unless a second-review artifact is provided.",
        }

    sanitized = {
        key: value
        for key, value in second_review_summary.items()
        if key in SAFE_SECOND_REVIEW_KEYS and public_safe_scalar(value)
    }
    if sanitized:
        return sanitized
    return {
        "status": "second_review_summary_redacted",
        "interpretation": "A second-review artifact was provided, but no public aggregate fields were safe to report.",
    }


def overall_quality_bucket(value: object) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if score <= 2:
        return "low_1_2"
    if score < 4:
        return "mid_3"
    return "high_4_5"


def row_design_id(row: dict) -> str:
    return str(row.get("condition_id") or row.get("system") or "").strip()


def is_nonempty(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def number_in_range(value: object, *, low: float, high: float) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return low <= number <= high


def extract_main_results(payload: dict) -> dict:
    system_summary = payload.get("system_summary") or {}
    rows = []
    for design_id in DESIGN_ORDER:
        item = system_summary.get(design_id) or {}
        if not item:
            continue
        rows.append(
            {
                "design_id": design_id,
                "design_label": reader_label(design_id),
                "n": item.get("n", 0),
                "overall_quality_mean": item.get("overall_quality_mean", 0.0),
                "student_ready_count": item.get("student_ready_pass_count", 0),
                "safe_ready_count": item.get("student_ready_safe_pass_count", 0),
                "major_plus_answer_leakage_count": item.get("major_or_answer_leakage_count", 0),
                "answer_leakage_count": item.get("answer_leakage_count", 0),
                "scaffold_sufficiency_mean": item.get("scaffold_sufficiency_mean", 0.0),
                "burden_low_medium_high": (
                    f"{item.get('student_response_burden_low_count', 0)}/"
                    f"{item.get('student_response_burden_medium_count', 0)}/"
                    f"{item.get('student_response_burden_high_count', 0)}"
                ),
            }
        )
    return {"designs": rows}


def extract_required_pairwise(payload: dict) -> list[dict]:
    comparisons = payload.get("paired_comparisons") or {}
    output = []
    for left, right in REQUIRED_PAIRS:
        key = f"{left}__vs__{right}"
        if key not in comparisons:
            continue
        item = comparisons[key]
        output.append(
            {
                "comparison": f"{reader_label(left)} - {reader_label(right)}",
                "left_design_id": left,
                "right_design_id": right,
                "paired_cases": item.get("paired_cases", 0),
                "delta_overall": item.get("mean_diff", 0.0),
                "w_t_l": f"{item.get('wins', 0)}/{item.get('ties', 0)}/{item.get('losses', 0)}",
                "ci95": item.get("bootstrap_ci95", [0.0, 0.0]),
            }
        )
    return output


def summarize_case_metadata(rows: Iterable[dict[str, str]]) -> dict:
    rows = list(rows)
    if not rows:
        return {
            "row_count": 0,
            "context_sufficiency_counts": {},
            "reasoning_focus_counts": {},
            "help_seeking_context_counts": {},
        }

    def first_value(row: dict[str, str], keys: list[str]) -> str:
        for key in keys:
            value = str(row.get(key) or "").strip()
            if value:
                return value
        return ""

    context_counts = Counter(first_value(row, ["context_sufficiency", "context_sufficiency_light"]) for row in rows)
    reasoning_counts = Counter(first_value(row, ["reasoning_focus", "rough_bridge_family", "coach_missing_bridge_family"]) for row in rows)
    help_counts = Counter(first_value(row, ["help_seeking_context", "help_seeking_type"]) for row in rows)
    return {
        "row_count": len(rows),
        "context_sufficiency_counts": dict(sorted(context_counts.items())),
        "reasoning_focus_counts": dict(sorted(reasoning_counts.items())),
        "help_seeking_context_counts": dict(sorted(help_counts.items())),
    }


def summarize_failure_modes(labels_rows: Iterable[dict[str, str]]) -> dict:
    rows = list(labels_rows)
    by_design = defaultdict(Counter)
    discussion_by_design = Counter()
    notes_by_design = Counter()
    major_or_answer_aggregate = defaultdict(
        lambda: {
            "total": 0,
            "by_leakage": Counter(),
            "by_show": Counter(),
            "by_overall_bucket": Counter(),
        }
    )
    for row in rows:
        design_id = str(row.get("condition_id") or row.get("system") or "")
        leakage = str(row.get("leakage_label") or "")
        burden = str(row.get("student_response_burden") or "")
        show = str(row.get("would_show_to_student") or "")
        if leakage:
            by_design[design_id][f"leakage:{leakage}"] += 1
        if burden:
            by_design[design_id][f"burden:{burden}"] += 1
        if show:
            by_design[design_id][f"show:{show}"] += 1
        if str(row.get("needs_discussion") or "") == "yes":
            discussion_by_design[design_id] += 1
        if str(row.get("notes") or "").strip():
            notes_by_design[design_id] += 1
        if leakage in {"major_bridge_leakage", "answer_leakage"}:
            aggregate = major_or_answer_aggregate[design_id]
            aggregate["total"] += 1
            aggregate["by_leakage"][leakage] += 1
            aggregate["by_show"][show or "unknown"] += 1
            aggregate["by_overall_bucket"][overall_quality_bucket(row.get("overall_quality_score"))] += 1
    return {
        "counts_by_design": {reader_label(key): dict(value) for key, value in sorted(by_design.items())},
        "needs_discussion_by_design": {reader_label(key): value for key, value in sorted(discussion_by_design.items())},
        "notes_count_by_design": {reader_label(key): value for key, value in sorted(notes_by_design.items())},
        "major_or_answer_aggregate_by_design": {
            reader_label(key): {
                "total": value["total"],
                "by_leakage": dict(sorted(value["by_leakage"].items())),
                "by_show": dict(sorted(value["by_show"].items())),
                "by_overall_bucket": dict(sorted(value["by_overall_bucket"].items())),
            }
            for key, value in sorted(major_or_answer_aggregate.items())
        },
    }


def build_review_reliability(integrity_audit: dict | None, second_review_summary: dict | None) -> dict:
    integrity_audit = integrity_audit or {}
    observed = integrity_audit.get("observed") or {}
    missing_required = integrity_audit.get("missing_required_fields") or {}
    missing_scores = integrity_audit.get("missing_score_fields") or {}
    return {
        "primary_review_rows": observed.get("row_count", 0),
        "primary_validation_passed": integrity_audit.get("passed"),
        "completed_rows_missing_required_fields": sum(missing_required.values()) + sum(missing_scores.values()),
        "integrity_audit_summary": {
            "source": integrity_audit.get("source"),
            "passed": integrity_audit.get("passed"),
            "row_count": observed.get("row_count", 0),
            "case_count": observed.get("case_count", 0),
            "unique_response_id_count": observed.get("unique_response_id_count", 0),
            "duplicate_response_id_count": integrity_audit.get("duplicate_response_id_count", 0),
            "cases_missing_designs_total": integrity_audit.get("cases_missing_designs_total", 0),
            "cases_with_duplicate_designs": integrity_audit.get("cases_with_duplicate_designs", 0),
        },
        "second_review_summary": sanitize_second_review_summary(second_review_summary),
        "authority_boundary": (
            "Coach review is treated as expert review evidence, not final gold. "
            "Second review or adjudication, when linked, is a bounded reliability check."
        ),
    }


def build_integrity_audit(
    payload: dict,
    labels_rows: Iterable[dict],
    external_validation: dict | None = None,
) -> dict:
    """Compute aggregate-only integrity checks from reviewed label rows.

    The public audit intentionally reports counts, not row-level case IDs,
    student text, code, or AI responses.
    """

    rows = list(labels_rows)
    case_ids = [str(row.get("case_id") or "").strip() for row in rows if is_nonempty(row.get("case_id"))]
    response_ids = [
        str(row.get("anonymized_response_id") or "").strip()
        for row in rows
        if is_nonempty(row.get("anonymized_response_id"))
    ]
    response_counter = Counter(response_ids)
    duplicate_response_id_count = sum(count - 1 for count in response_counter.values() if count > 1)

    missing_required_fields = Counter()
    invalid_allowed_values = Counter()
    missing_score_fields = Counter()
    missing_optional_score_fields = Counter()
    invalid_numeric_scores = Counter()
    design_counts = Counter()
    case_counts = Counter()
    case_design_counts = Counter()
    unexpected_design_count = 0

    for row in rows:
        for field in REQUIRED_REVIEW_FIELDS:
            if not is_nonempty(row.get(field)):
                missing_required_fields[field] += 1

        design_id = row_design_id(row)
        if not design_id:
            missing_required_fields["condition_id/system"] += 1
        else:
            design_counts[design_id] += 1
            if design_id not in DESIGN_ORDER:
                unexpected_design_count += 1

        case_id = str(row.get("case_id") or "").strip()
        if case_id:
            case_counts[case_id] += 1
            if design_id:
                case_design_counts[(case_id, design_id)] += 1

        for field, allowed_values in ALLOWED_VALUES.items():
            value = str(row.get(field) or "").strip()
            if value and value not in allowed_values:
                invalid_allowed_values[field] += 1

        if is_nonempty(row.get("overall_quality_score")) and not number_in_range(
            row.get("overall_quality_score"), low=1, high=5
        ):
            invalid_numeric_scores["overall_quality_score"] += 1

        scores = row.get("scores") or {}
        if not isinstance(scores, dict):
            scores = {}
            missing_required_fields["scores"] += 1
        for score_field in REQUIRED_SCORE_FIELDS:
            if not is_nonempty(scores.get(score_field)):
                missing_score_fields[score_field] += 1
            elif not number_in_range(scores.get(score_field), low=0, high=2):
                invalid_numeric_scores[f"scores.{score_field}"] += 1
        for score_field in OPTIONAL_SCORE_FIELDS:
            if not is_nonempty(scores.get(score_field)):
                missing_optional_score_fields[score_field] += 1
            elif not number_in_range(scores.get(score_field), low=0, high=2):
                invalid_numeric_scores[f"scores.{score_field}"] += 1

    cases_with_wrong_row_count = sum(1 for count in case_counts.values() if count != EXPECTED_ROWS_PER_CASE)
    cases_missing_designs_total = 0
    cases_with_duplicate_designs = 0
    for case_id in case_counts:
        present_designs = {design_id for (row_case_id, design_id), count in case_design_counts.items() if row_case_id == case_id}
        cases_missing_designs_total += len(set(DESIGN_ORDER) - present_designs)
        if any(case_design_counts[(case_id, design_id)] > 1 for design_id in DESIGN_ORDER):
            cases_with_duplicate_designs += 1

    design_counts_by_label = {reader_label(design_id): design_counts.get(design_id, 0) for design_id in DESIGN_ORDER}
    design_count_mismatches = {
        reader_label(design_id): {
            "expected": EXPECTED_ROWS_PER_DESIGN,
            "observed": design_counts.get(design_id, 0),
        }
        for design_id in DESIGN_ORDER
        if design_counts.get(design_id, 0) != EXPECTED_ROWS_PER_DESIGN
    }

    payload_row_count = int(payload.get("row_count") or 0)
    payload_case_count = int(payload.get("case_count") or 0)
    external_summary = None
    if external_validation:
        external_summary = {
            "source": "external_validation_artifact",
            "passed": external_validation.get("passed"),
            "completed_rows": external_validation.get("completed_rows", external_validation.get("total_rows")),
        }

    checks = {
        "labels_rows_present": len(rows) > 0,
        "row_count_matches_expected": len(rows) == EXPECTED_ROW_COUNT,
        "case_count_matches_expected": len(set(case_ids)) == EXPECTED_CASE_COUNT,
        "payload_row_count_matches_labels": payload_row_count == len(rows),
        "payload_case_count_matches_labels": payload_case_count == len(set(case_ids)),
        "each_design_has_expected_rows": not design_count_mismatches,
        "each_case_has_expected_rows": cases_with_wrong_row_count == 0,
        "each_case_has_all_designs": cases_missing_designs_total == 0,
        "no_duplicate_case_design_pairs": cases_with_duplicate_designs == 0,
        "no_duplicate_response_ids": duplicate_response_id_count == 0,
        "no_missing_required_fields": not missing_required_fields and not missing_score_fields,
        "allowed_values_valid": not invalid_allowed_values,
        "numeric_scores_valid": not invalid_numeric_scores,
        "no_unexpected_designs": unexpected_design_count == 0,
    }
    passed = all(checks.values())
    return {
        "source": "computed_from_review_labels",
        "expected": {
            "row_count": EXPECTED_ROW_COUNT,
            "case_count": EXPECTED_CASE_COUNT,
            "rows_per_case": EXPECTED_ROWS_PER_CASE,
            "rows_per_design": EXPECTED_ROWS_PER_DESIGN,
            "designs": [reader_label(design_id) for design_id in DESIGN_ORDER],
        },
        "observed": {
            "row_count": len(rows),
            "case_count": len(set(case_ids)),
            "unique_response_id_count": len(response_counter),
            "design_counts_by_label": design_counts_by_label,
        },
        "checks": checks,
        "missing_required_fields": dict(sorted(missing_required_fields.items())),
        "missing_score_fields": dict(sorted(missing_score_fields.items())),
        "missing_optional_score_fields": dict(sorted(missing_optional_score_fields.items())),
        "invalid_allowed_values": dict(sorted(invalid_allowed_values.items())),
        "invalid_numeric_scores": dict(sorted(invalid_numeric_scores.items())),
        "duplicate_response_id_count": duplicate_response_id_count,
        "cases_with_wrong_row_count": cases_with_wrong_row_count,
        "cases_missing_designs_total": cases_missing_designs_total,
        "cases_with_duplicate_designs": cases_with_duplicate_designs,
        "unexpected_design_count": unexpected_design_count,
        "design_count_mismatches": design_count_mismatches,
        "external_validation_summary": external_summary,
        "passed": passed,
    }


def build_freeze_manifest(
    *,
    input_paths: list[Path],
    output_paths: list[Path],
    closeout_summary: dict,
    evidence_role: str,
    freeze_date: str,
) -> dict:
    return {
        "manifest_id": f"cp_missingbridgebench_v2_evidence_freeze_{freeze_date.replace('-', '')}",
        "freeze_date": freeze_date,
        "evidence_role": evidence_role,
        "closeout_summary": {
            "case_count": closeout_summary.get("case_count"),
            "row_count": closeout_summary.get("row_count"),
            "privacy_boundary": closeout_summary.get("privacy_boundary", PUBLIC_PRIVACY_BOUNDARY),
        },
        "inputs": [artifact_record(path) for path in input_paths],
        "outputs": [artifact_record(path) for path in output_paths],
        "do_not_release": [
            "raw student text",
            "full student code",
            "complete AIChat responses",
            "identity fields",
            "hash salts",
            "reversible mappings",
            "private workbooks",
        ],
        "result_boundary": (
            "v2 closeout evidence; does not recompute or modify dialogue-state v3 main results; "
            "does not modify online AIChat; does not establish learning outcomes."
        ),
    }


def render_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def render_closeout_report_zh(closeout_summary: dict) -> str:
    main_rows = [
        [
            row["design_label"],
            row["n"],
            row["overall_quality_mean"],
            row["student_ready_count"],
            row["safe_ready_count"],
            row["major_plus_answer_leakage_count"],
            row["answer_leakage_count"],
            row["burden_low_medium_high"],
        ]
        for row in closeout_summary.get("main_results", {}).get("designs", [])
    ]
    pair_rows = [
        [
            row["comparison"],
            row["paired_cases"],
            row["delta_overall"],
            row["w_t_l"],
            row["ci95"],
        ]
        for row in closeout_summary.get("required_pairwise", [])
    ]
    metadata = closeout_summary.get("case_metadata_summary") or {}
    reliability = closeout_summary.get("human_review_reliability") or {}
    integrity = closeout_summary.get("integrity_audit") or {}
    return "\n\n".join(
        [
            "# CP-MissingBridgeBench v2 实验收尾报告（aggregate）",
            "本报告只汇总 v2 100-case / 700-response 人审实验的 aggregate 结果；不公开学生原文、完整代码、完整 AIChat 回复、真实身份、hash salt 或可逆映射。",
            f"- case count: {closeout_summary.get('case_count')}\n- response rows: {closeout_summary.get('row_count')}\n- evidence role: {closeout_summary.get('evidence_role')}",
            "## 主结果摘要",
            render_table(
                [
                    "design",
                    "n",
                    "overall",
                    "student-ready",
                    "safe-ready",
                    "major+answer",
                    "answer",
                    "burden low/medium/high",
                ],
                main_rows,
            ),
            "## 关键配对比较",
            render_table(["comparison", "cases", "Δ overall", "W/T/L", "CI95"], pair_rows),
            "## 样本结构摘要",
            "```json\n" + json.dumps(metadata, ensure_ascii=False, indent=2) + "\n```",
            "## 700 条评审行完整性审计",
            "```json\n" + json.dumps(integrity, ensure_ascii=False, indent=2) + "\n```",
            "## 人审可靠性边界",
            "```json\n" + json.dumps(reliability, ensure_ascii=False, indent=2) + "\n```",
            "## 解释边界",
            "- v2 closeout 不修改 dialogue-state v3 主结果。\n"
            "- v2 closeout 不证明线上部署效果或学习效果。\n"
            "- 如果 DBox-inspired + Guard 在 v2 中领先，应直接报告为强 baseline，而不是改写成 Bridge Contract 方法胜利。\n"
            "- Bridge Contract / Repair 变体应作为被评估设计和失败分析对象报告，除非结果支持更强 claim。",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-summary-json", type=Path, required=True)
    parser.add_argument("--labels-jsonl", type=Path)
    parser.add_argument("--validation-json", type=Path)
    parser.add_argument("--case-metadata-csv", type=Path)
    parser.add_argument("--second-review-summary-json", type=Path)
    parser.add_argument("--input-artifact", action="append", type=Path, default=[])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--freeze-date", default="2026-05-22")
    args = parser.parse_args()

    payload = read_json(args.analysis_summary_json)
    metadata_rows = read_csv_rows(args.case_metadata_csv) if args.case_metadata_csv and args.case_metadata_csv.exists() else []
    second_review = (
        read_json(args.second_review_summary_json)
        if args.second_review_summary_json and args.second_review_summary_json.exists()
        else None
    )
    labels_rows = []
    if args.labels_jsonl and args.labels_jsonl.exists():
        labels_rows = [
            json.loads(line)
            for line in args.labels_jsonl.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    external_validation = read_json(args.validation_json) if args.validation_json and args.validation_json.exists() else None
    integrity_audit = build_integrity_audit(payload, labels_rows, external_validation)

    closeout_summary = {
        "case_count": payload.get("case_count"),
        "row_count": payload.get("row_count"),
        "evidence_role": "v2 benchmark/evaluation closeout; not dialogue-state v3 main result",
        "privacy_boundary": PUBLIC_PRIVACY_BOUNDARY,
        "main_results": extract_main_results(payload),
        "required_pairwise": extract_required_pairwise(payload),
        "case_metadata_summary": summarize_case_metadata(metadata_rows),
        "failure_mode_summary": summarize_failure_modes(labels_rows),
        "integrity_audit": integrity_audit,
        "human_review_reliability": build_review_reliability(integrity_audit, second_review),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "cp_missingbridgebench_v2_experiment_closeout_summary_20260522.json"
    report_path = args.output_dir / "cp_missingbridgebench_v2_experiment_closeout_report_20260522.zh.md"
    manifest_path = args.output_dir / "cp_missingbridgebench_v2_evidence_freeze_manifest_20260522.json"

    summary_path.write_text(json.dumps(closeout_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_closeout_report_zh(closeout_summary) + "\n", encoding="utf-8")

    input_paths = [args.analysis_summary_json]
    if args.validation_json:
        input_paths.append(args.validation_json)
    if args.case_metadata_csv:
        input_paths.append(args.case_metadata_csv)
    if args.labels_jsonl:
        input_paths.append(args.labels_jsonl)
    input_paths.extend(args.input_artifact)

    manifest = build_freeze_manifest(
        input_paths=input_paths,
        output_paths=[summary_path, report_path],
        closeout_summary=closeout_summary,
        evidence_role=closeout_summary["evidence_role"],
        freeze_date=args.freeze_date,
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str(summary_path), "report": str(report_path), "manifest": str(manifest_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
