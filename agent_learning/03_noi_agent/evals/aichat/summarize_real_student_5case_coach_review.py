#!/usr/bin/env python3
"""Create a public-safe aggregate summary for 5-case coach review.

This script reads the local-only coach-review packet and writes aggregate
summary files that do not include student text, code, AI responses, case ids,
student hashes, or problem hashes. It does not read, recompute, or modify
dialogue-state v3 main experiment data.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


DEFAULT_INPUT = Path(".local_private/real_student_online_5case_coach_review_packet_20260519.csv")
DEFAULT_SCHEMA = Path("docs/research/real_student_online_5case_coach_review_schema_v1.json")
DEFAULT_OUTPUT_JSON = Path("docs/research/real_student_online_5case_coach_review_public_summary_20260519.json")
DEFAULT_OUTPUT_MD = Path("docs/research/real_student_online_5case_coach_review_public_summary_20260519.zh.md")


def _clean(value: str | None) -> str:
    value = (value or "").strip()
    return value if value else "(blank)"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _counter(rows: Iterable[dict[str, str]], field: str) -> dict[str, int]:
    counts = Counter(_clean(row.get(field)) for row in rows)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _reviewed(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if _clean(row.get("coach_review_status")) == "reviewed"]


def _reportable(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if _clean(row.get("coach_review_status")) == "reviewed"
        and _clean(row.get("coach_privacy_review_status")) == "passed_for_internal_review"
        and _clean(row.get("consent_reporting_gate")) == "eligible"
    ]


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    reviewed = _reviewed(rows)
    reportable = _reportable(rows)
    suppress_leakage = len(reviewed) == 0 or len(reportable) < len(reviewed)

    summary: dict[str, object] = {
        "total_rows": len(rows),
        "reviewed_rows_count": len(reviewed),
        "reportable_after_consent_count": len(reportable),
        "leakage_counts_suppressed": suppress_leakage,
        "counts": {
            "coach_review_status": _counter(rows, "coach_review_status"),
            "coach_privacy_review_status": _counter(rows, "coach_privacy_review_status"),
            "coach_context_sufficiency": _counter(rows, "coach_context_sufficiency"),
            "coach_matches_existing_taxonomy": _counter(rows, "coach_matches_existing_taxonomy"),
            "adjudication_needed": _counter(rows, "adjudication_needed"),
            "consent_reporting_gate": _counter(rows, "consent_reporting_gate"),
        },
        "boundary": {
            "evidence_role": "5-case dry run process evidence only; not a main result or learning-outcome study.",
            "privacy": "Public summary excludes student text, code, AI responses, case ids, student hashes, and problem hashes.",
            "consent": "Case-level or leakage-result reporting is suppressed until consent/reporting gate is complete.",
        },
    }
    if not suppress_leakage:
        summary["coach_current_aichat_leakage_concern_counts"] = _counter(
            reviewed, "coach_current_aichat_leakage_concern"
        )
    return summary


def _table_from_counts(counts: dict[str, int], key_label: str, value_label: str = "count") -> str:
    if not counts:
        return f"| {key_label} | {value_label} |\n| --- | ---: |\n| *(none)* | 0 |"
    lines = [f"| {key_label} | {value_label} |", "| --- | ---: |"]
    for key, value in counts.items():
        lines.append(f"| `{key}` | {value} |")
    return "\n".join(lines)


def render_markdown(summary: dict[str, object]) -> str:
    counts = summary["counts"]
    assert isinstance(counts, dict)
    lines = [
        "# Real-Student Online 5-Case Coach Review Public Summary 20260519",
        "",
        "## 使用边界",
        "",
        "本报告是 5-case real-student online dry run 的公开安全 aggregate summary。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。",
        "",
        "本报告不包含学生原文、recent dialogue、完整代码、当前 AIChat 回复、case ids、student hashes 或 problem hashes。",
        "",
        "## Process Counts",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| total dry-run rows | {summary['total_rows']} |",
        f"| coach-reviewed rows | {summary['reviewed_rows_count']} |",
        f"| reportable after consent/status gate | {summary['reportable_after_consent_count']} |",
        f"| leakage counts suppressed | {str(summary['leakage_counts_suppressed']).lower()} |",
        "",
        "## Coach Review Status Counts",
        "",
        _table_from_counts(counts.get("coach_review_status", {}), "coach_review_status"),
        "",
        "## Privacy Review Status Counts",
        "",
        _table_from_counts(counts.get("coach_privacy_review_status", {}), "coach_privacy_review_status"),
        "",
        "## Context Sufficiency Counts",
        "",
        _table_from_counts(counts.get("coach_context_sufficiency", {}), "coach_context_sufficiency"),
        "",
        "## Taxonomy Fit Counts",
        "",
        _table_from_counts(counts.get("coach_matches_existing_taxonomy", {}), "coach_matches_existing_taxonomy"),
        "",
        "## Adjudication Counts",
        "",
        _table_from_counts(counts.get("adjudication_needed", {}), "adjudication_needed"),
        "",
        "## Consent Reporting Gate Counts",
        "",
        _table_from_counts(counts.get("consent_reporting_gate", {}), "consent_reporting_gate"),
        "",
    ]
    if summary.get("leakage_counts_suppressed"):
        lines.extend(
            [
                "## Leakage Counts",
                "",
                "Suppressed. Current rows are not reportable deep-pilot evidence until consent/status gate is complete.",
                "",
            ]
        )
    else:
        counts_obj = summary.get("coach_current_aichat_leakage_concern_counts", {})
        assert isinstance(counts_obj, dict)
        lines.extend(
            [
                "## Leakage Counts",
                "",
                _table_from_counts(counts_obj, "coach_current_aichat_leakage_concern"),
                "",
            ]
        )

    lines.extend(
        [
            "## Claim Gate",
            "",
            "- no new experiment",
            "- no new main condition",
            "- no dialogue-state v3 table update",
            "- no evidence-class change",
            "- no student-visible response change",
            "- no learning-outcome claim",
            "- no case-level reporting while consent/status gate is pending",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize local-only 5-case coach review into public-safe aggregate files."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    read_schema(args.schema)
    rows = read_csv(args.input)
    summary = summarize(rows)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_md.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
