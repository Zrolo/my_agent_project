#!/usr/bin/env python3
"""Select a public Real-AIChat-100 observational manifest from screening rows.

This selector uses only the public candidate-turn screening CSV fields. It does
not read private packets, does not copy raw student text/code/AIChat responses,
does not call online AIChat, and does not touch dialogue-state v3 main results.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


DEFAULT_INPUT = Path("docs/research/real_student_online_candidate_screening_form_v1.csv")
DEFAULT_OUTPUT_CSV = Path("docs/research/real_aichat_100_observational_validation_manifest_20260520.csv")
DEFAULT_OUTPUT_JSON = Path("docs/research/real_aichat_100_selection_summary_20260520.json")
DEFAULT_OUTPUT_MD = Path("docs/research/real_aichat_100_selection_log_20260520.zh.md")
DEFAULT_TARGET_COUNT = 100
ANNOTATION_DATE = "2026-05-20"
ANNOTATOR_ID = "auto_selection_from_screening_v1_20260520"
REDACTED = "redacted_in_public_manifest"

MANIFEST_FIELDS = [
    "real_aichat_case_id",
    "source_candidate_turn_id",
    "student_id_hash_private_or_redacted",
    "problem_id_hash_private_or_redacted",
    "session_id_hash_private_or_redacted",
    "cp_tutoring_relevance",
    "substantial_turn",
    "context_sufficiency_light",
    "rough_bridge_family",
    "surface_anchor",
    "help_seeking_type",
    "missing_bridge_identifiable",
    "observed_current_aichat_response_available",
    "observed_current_aichat_response_role",
    "possible_bridge_leakage_concern",
    "candidate_for_replay",
    "candidate_for_trajectory_subset",
    "privacy_review_status",
    "consent_reporting_gate",
    "public_reporting_allowed",
    "selection_reason",
    "exclusion_reason",
    "annotator_id",
    "annotation_date",
    "notes_no_raw_text",
]

COVERAGE_FIELDS = [
    "rough_bridge_family",
    "surface_anchor",
    "help_seeking_type",
    "likely_slice",
    "context_sufficiency",
]


def _clean(value: str | None) -> str:
    return (value or "").strip()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def is_eligible(row: dict[str, str]) -> bool:
    privacy = _clean(row.get("privacy_review_status"))
    return (
        _clean(row.get("is_cp_related")) == "yes"
        and _clean(row.get("is_substantial_turn")) == "yes"
        and _clean(row.get("context_sufficiency")) in {"sufficient", "partial"}
        and privacy in {"pending", "passed"}
        and _clean(row.get("consent_eligibility")) != "not_eligible"
    )


def select_candidates(rows: list[dict[str, str]], target_count: int = DEFAULT_TARGET_COUNT) -> list[dict[str, str]]:
    indexed_rows = [dict(row, __source_index=str(index)) for index, row in enumerate(rows)]
    eligible = [row for row in indexed_rows if is_eligible(row)]
    target = min(target_count, len(eligible))
    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()

    counts = {
        "student_id_hash": Counter(),
        "problem_id_hash": Counter(),
        "session_id_hash": Counter(),
        "rough_bridge_family": Counter(),
        "surface_anchor": Counter(),
        "help_seeking_type": Counter(),
    }

    def add(row: dict[str, str]) -> bool:
        row_id = _clean(row.get("candidate_turn_id"))
        if not row_id or row_id in selected_ids or len(selected) >= target:
            return False
        selected.append(row)
        selected_ids.add(row_id)
        for field, counter in counts.items():
            counter[_clean(row.get(field))] += 1
        return True

    def balance_key(row: dict[str, str]) -> tuple[int, int, int, int, int, int]:
        return (
            counts["student_id_hash"][_clean(row.get("student_id_hash"))],
            counts["problem_id_hash"][_clean(row.get("problem_id_hash"))],
            counts["session_id_hash"][_clean(row.get("session_id_hash"))],
            counts["rough_bridge_family"][_clean(row.get("rough_bridge_family"))],
            counts["surface_anchor"][_clean(row.get("surface_anchor"))],
            int(row["__source_index"]),
        )

    for row in eligible:
        if _clean(row.get("candidate_for_deep_annotation")) == "yes":
            add(row)

    for field in COVERAGE_FIELDS:
        values = sorted(
            {_clean(row.get(field)) for row in eligible if _clean(row.get(field))},
            key=lambda value: (sum(1 for row in eligible if _clean(row.get(field)) == value), value),
        )
        for value in values:
            candidates = [
                row
                for row in eligible
                if _clean(row.get(field)) == value and _clean(row.get("candidate_turn_id")) not in selected_ids
            ]
            if candidates:
                add(min(candidates, key=balance_key))

    for field in ["student_id_hash", "problem_id_hash", "session_id_hash"]:
        values = sorted(
            {_clean(row.get(field)) for row in eligible if _clean(row.get(field))},
            key=lambda value: (sum(1 for row in eligible if _clean(row.get(field)) == value), value),
        )
        for value in values:
            candidates = [
                row
                for row in eligible
                if _clean(row.get(field)) == value and _clean(row.get("candidate_turn_id")) not in selected_ids
            ]
            if candidates:
                add(min(candidates, key=balance_key))

    while len(selected) < target:
        remaining = [row for row in eligible if _clean(row.get("candidate_turn_id")) not in selected_ids]
        if not remaining:
            break
        add(min(remaining, key=balance_key))

    return selected


def _map_privacy_status(value: str) -> str:
    value = _clean(value)
    if value == "excluded_privacy_risk":
        return "failed"
    if value in {"pending", "passed", "needs_redaction", "failed"}:
        return value
    return "pending"


def _map_consent_gate(value: str) -> str:
    value = _clean(value)
    if value in {"pending", "eligible", "not_eligible", "consented", "unknown"}:
        return value
    return "unknown"


def _missing_bridge_identifiable(row: dict[str, str]) -> str:
    bridge = _clean(row.get("rough_bridge_family"))
    if bridge in {"", "unclear"}:
        return "unclear"
    return "yes"


def _candidate_for_replay(row: dict[str, str]) -> str:
    if _clean(row.get("context_sufficiency")) not in {"sufficient", "partial"}:
        return "no"
    if _missing_bridge_identifiable(row) != "yes":
        return "no"
    if _map_privacy_status(_clean(row.get("privacy_review_status"))) == "failed":
        return "no"
    return "yes"


def build_manifest_rows(
    selected_rows: list[dict[str, str]], annotation_date: str = ANNOTATION_DATE
) -> list[dict[str, str]]:
    manifest_rows: list[dict[str, str]] = []
    for index, row in enumerate(selected_rows, start=1):
        privacy = _map_privacy_status(_clean(row.get("privacy_review_status")))
        consent = _map_consent_gate(_clean(row.get("consent_eligibility")))
        public_allowed = "yes" if privacy == "passed" and consent in {"eligible", "consented"} else "no"
        manifest_rows.append(
            {
                "real_aichat_case_id": f"real_aichat_100_20260520_{index:03d}",
                "source_candidate_turn_id": _clean(row.get("candidate_turn_id")),
                "student_id_hash_private_or_redacted": REDACTED,
                "problem_id_hash_private_or_redacted": REDACTED,
                "session_id_hash_private_or_redacted": REDACTED,
                "cp_tutoring_relevance": "yes" if _clean(row.get("is_cp_related")) == "yes" else "unclear",
                "substantial_turn": "yes" if _clean(row.get("is_substantial_turn")) == "yes" else "no",
                "context_sufficiency_light": _clean(row.get("context_sufficiency")) or "unclear",
                "rough_bridge_family": _clean(row.get("rough_bridge_family")) or "unclear",
                "surface_anchor": _clean(row.get("surface_anchor")),
                "help_seeking_type": _clean(row.get("help_seeking_type")) or "other",
                "missing_bridge_identifiable": _missing_bridge_identifiable(row),
                "observed_current_aichat_response_available": "yes",
                "observed_current_aichat_response_role": "observed_only_not_condition",
                "possible_bridge_leakage_concern": "not_assessed",
                "candidate_for_replay": _candidate_for_replay(row),
                "candidate_for_trajectory_subset": "no",
                "privacy_review_status": privacy,
                "consent_reporting_gate": consent,
                "public_reporting_allowed": public_allowed,
                "selection_reason": (
                    "Deterministic stratified purposive selection from the 137-turn screening pool; "
                    f"coverage fields: rough_bridge_family={_clean(row.get('rough_bridge_family'))}, "
                    f"surface_anchor={_clean(row.get('surface_anchor'))}, "
                    f"help_seeking_type={_clean(row.get('help_seeking_type'))}, "
                    f"context_sufficiency={_clean(row.get('context_sufficiency'))}. "
                    "Not selected by observed AIChat quality, Bridge Contract/Repair support, or paper-favorable outcome."
                ),
                "exclusion_reason": "",
                "annotator_id": ANNOTATOR_ID,
                "annotation_date": annotation_date,
                "notes_no_raw_text": (
                    "Public manifest row contains no raw student text, complete code, complete AIChat response, "
                    "identity mapping, hash salt, or reversible mapping; row-level hashes are redacted."
                ),
            }
        )
    return manifest_rows


def _counter(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(_clean(row.get(field)) for row in rows).items()))


def build_summary(
    source_rows: list[dict[str, str]],
    selected_rows: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
    target_count: int,
) -> dict[str, object]:
    eligible = [row for row in source_rows if is_eligible(row)]
    return {
        "summary_id": "real_aichat_100_selection_summary_20260520",
        "selection_date": ANNOTATION_DATE,
        "source_screening_rows": len(source_rows),
        "eligible_screening_rows": len(eligible),
        "target_count": target_count,
        "selected_manifest_rows": len(manifest_rows),
        "source_unique_sessions_selected": len({_clean(row.get("session_id_hash")) for row in selected_rows}),
        "source_unique_students_selected": len({_clean(row.get("student_id_hash")) for row in selected_rows}),
        "source_unique_problems_selected": len({_clean(row.get("problem_id_hash")) for row in selected_rows}),
        "selected_context_sufficiency_counts": _counter(selected_rows, "context_sufficiency"),
        "selected_rough_bridge_family_counts": _counter(selected_rows, "rough_bridge_family"),
        "selected_surface_anchor_counts": _counter(selected_rows, "surface_anchor"),
        "selected_help_seeking_type_counts": _counter(selected_rows, "help_seeking_type"),
        "selected_likely_slice_counts": _counter(selected_rows, "likely_slice"),
        "selected_privacy_review_status_counts": _counter(selected_rows, "privacy_review_status"),
        "selected_consent_eligibility_counts": _counter(selected_rows, "consent_eligibility"),
        "manifest_candidate_for_replay_counts": _counter(manifest_rows, "candidate_for_replay"),
        "manifest_public_reporting_allowed_counts": _counter(manifest_rows, "public_reporting_allowed"),
        "boundary": {
            "main_result": "no",
            "condition_comparison": "no",
            "learning_outcome_study": "no",
            "dialogue_state_v3_table_update": "no",
            "raw_text_or_full_response_included": "no",
            "row_level_hashes_public": "no",
        },
    }


def _md_table(counts: dict[str, int], name: str) -> str:
    lines = [f"### {name}", "", "| value | count |", "| --- | ---: |"]
    for value, count in counts.items():
        lines.append(f"| `{value}` | {count} |")
    return "\n".join(lines)


def write_summary_md(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Real-AIChat-100 Selection Log 20260520",
        "",
        "## 使用边界",
        "",
        "本日志记录从 137 条 real-student online AIChat candidate-turn screening pool 中生成 Real-AIChat-100 observational validation manifest 的选择结果。它不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，不调用线上 AIChat，不生成 Replay responses，也不评估 learning outcome。",
        "",
        "公开 manifest 不包含学生原文、完整代码、完整 AIChat 回复、真实身份、hash salt、可逆映射或 row-level hash 表。`observed_current_aichat_response` 只表示线上已展示回复的观察项，非实验条件。",
        "",
        "## Selection Summary",
        "",
        "| field | value |",
        "| --- | ---: |",
        f"| source screening rows | {summary['source_screening_rows']} |",
        f"| eligible screening rows | {summary['eligible_screening_rows']} |",
        f"| target count | {summary['target_count']} |",
        f"| selected manifest rows | {summary['selected_manifest_rows']} |",
        f"| selected unique sessions | {summary['source_unique_sessions_selected']} |",
        f"| selected unique students | {summary['source_unique_students_selected']} |",
        f"| selected unique problems | {summary['source_unique_problems_selected']} |",
        "",
        "## Selection Rule",
        "",
        "选择规则为 deterministic stratified purposive sampling：先保留现有 30 条 selected pilot candidate cases，再覆盖 rough bridge family、surface anchor、help-seeking type、likely slice、context sufficiency、student、problem 和 session，最后用低集中度优先的确定性排序补足到目标数量。选择不依据 observed AIChat response 好坏，不依据是否支持 Bridge Contract / Repair，也不依据是否支持论文主结论。",
        "",
        _md_table(summary["selected_context_sufficiency_counts"], "Context Sufficiency Counts"),
        "",
        _md_table(summary["selected_rough_bridge_family_counts"], "Rough Bridge Family Counts"),
        "",
        _md_table(summary["selected_surface_anchor_counts"], "Surface Anchor Counts"),
        "",
        _md_table(summary["selected_help_seeking_type_counts"], "Help-Seeking Type Counts"),
        "",
        _md_table(summary["selected_likely_slice_counts"], "Likely Slice Counts"),
        "",
        _md_table(summary["selected_privacy_review_status_counts"], "Privacy Review Status Counts"),
        "",
        _md_table(summary["selected_consent_eligibility_counts"], "Consent Eligibility Counts"),
        "",
        _md_table(summary["manifest_candidate_for_replay_counts"], "Candidate For Replay Counts"),
        "",
        _md_table(summary["manifest_public_reporting_allowed_counts"], "Public Reporting Allowed Counts"),
        "",
        "## Reporting Boundary",
        "",
        "- Real-AIChat-100 is observational ecological-validity validation only.",
        "- It is not a 7-harness condition-comparison experiment.",
        "- It is not a main result and does not update dialogue-state v3 tables.",
        "- Consent/reporting gate is pending for the selected rows, so public reporting is limited to aggregate/process counts.",
        "- Replay candidates are only candidates; no Replay-30/50 generation or coach review is created by this selection step.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select Real-AIChat-100 observational validation manifest.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--target-count", type=int, default=DEFAULT_TARGET_COUNT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _, source_rows = read_csv(args.input)
    selected_rows = select_candidates(source_rows, target_count=args.target_count)
    manifest_rows = build_manifest_rows(selected_rows)
    summary = build_summary(source_rows, selected_rows, manifest_rows, args.target_count)

    write_csv(args.output_csv, manifest_rows, MANIFEST_FIELDS)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary_md(args.output_md, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
