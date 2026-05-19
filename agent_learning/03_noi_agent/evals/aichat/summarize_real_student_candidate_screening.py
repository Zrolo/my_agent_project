#!/usr/bin/env python3
"""Summarize real-student online AIChat candidate-turn screening rows.

This script reads the lightweight screening CSV for the 137 candidate turns.
It does not read or modify dialogue-state v3 main experiment data.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


DEFAULT_INPUT = Path("docs/research/real_student_online_candidate_screening_form_v1.csv")
DEFAULT_OUTPUT_JSON = Path("docs/research/real_student_candidate_screening_summary_20260519.json")
DEFAULT_OUTPUT_MD = Path("docs/research/real_student_candidate_screening_summary_20260519.zh.md")

COUNT_FIELDS = [
    "context_sufficiency",
    "rough_bridge_family",
    "surface_anchor",
    "help_seeking_type",
    "likely_slice",
    "candidate_for_deep_annotation",
    "exclusion_reason",
    "privacy_review_status",
    "consent_eligibility",
]


def _clean(value: str | None) -> str:
    value = (value or "").strip()
    return value if value else "(blank)"


def _counter(rows: Iterable[dict[str, str]], field: str) -> dict[str, int]:
    counts = Counter(_clean(row.get(field)) for row in rows)
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _unique_count(rows: Iterable[dict[str, str]], field: str) -> int:
    values = {_clean(row.get(field)) for row in rows}
    values.discard("(blank)")
    return len(values)


def _selected(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if _clean(row.get("candidate_for_deep_annotation")).lower() == "yes"
    ]


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    selected = _selected(rows)
    summary: dict[str, object] = {
        "total_rows": len(rows),
        "unique_sessions": _unique_count(rows, "session_id_hash"),
        "unique_students": _unique_count(rows, "student_id_hash"),
        "unique_problems": _unique_count(rows, "problem_id_hash"),
        "counts": {field: _counter(rows, field) for field in COUNT_FIELDS},
        "selected_deep_candidates_count": len(selected),
        "selected_deep_candidates_by_bridge_family": _counter(selected, "rough_bridge_family"),
        "selected_deep_candidates_by_surface_anchor": _counter(selected, "surface_anchor"),
        "selected_deep_candidates_by_student": _counter(selected, "student_id_hash"),
        "selected_deep_candidates_by_problem": _counter(selected, "problem_id_hash"),
        "boundary": {
            "candidate_turns": "137 candidate turns are a screening pool, not a deep annotation sample.",
            "deep_sample": "30 selected cases are a deep annotation sample, not all online AIChat data.",
            "evidence_role": "ecological validity only; not a main result or learning outcome study.",
        },
    }
    return summary


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


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
    return f"""# Real-Student Online Candidate-Turn Screening Summary 20260519

## 使用边界

本报告汇总 real-student online AIChat candidate-turn screening CSV 的轻量筛查统计。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

137 条 candidate turns 是 screening pool，不是 deep annotation sample。30 条 selected cases 是 deep annotation sample，不是全部线上 AIChat 数据。本报告只能作为 ecological validity 的数据漏斗和抽样说明，可放入 Discussion / Appendix，不能作为 main result。

## Data Funnel

| layer | unit | count | boundary |
| --- | --- | ---: | --- |
| Online log corpus summary | raw AIChat message rows | 1156 | source-corpus background only |
| Online log corpus summary | sessions | 87 | source-corpus background only |
| Online log corpus summary | paired user-assistant turns | 578 | source-corpus background only |
| Candidate-turn screening | expected substantial candidate turns | 137 | lightweight screening pool |
| Candidate-turn screening | actual screening rows in CSV | {summary["total_rows"]} | generated from screening form |
| Deep pilot annotation | selected deep candidates in CSV | {summary["selected_deep_candidates_count"]} | complete annotation only after privacy review |

## Coverage Summary

| metric | value |
| --- | ---: |
| total rows | {summary["total_rows"]} |
| unique sessions | {summary["unique_sessions"]} |
| unique students | {summary["unique_students"]} |
| unique problems | {summary["unique_problems"]} |
| selected deep candidates count | {summary["selected_deep_candidates_count"]} |

## Context Sufficiency Counts

{_table_from_counts(counts.get("context_sufficiency", {}), "context_sufficiency")}

## Rough Bridge Family Counts

{_table_from_counts(counts.get("rough_bridge_family", {}), "rough_bridge_family")}

## Surface Anchor Counts

{_table_from_counts(counts.get("surface_anchor", {}), "surface_anchor")}

## Help-Seeking Type Counts

{_table_from_counts(counts.get("help_seeking_type", {}), "help_seeking_type")}

## Likely Slice Counts

{_table_from_counts(counts.get("likely_slice", {}), "likely_slice")}

## Candidate For Deep Annotation Counts

{_table_from_counts(counts.get("candidate_for_deep_annotation", {}), "candidate_for_deep_annotation")}

## Exclusion Reason Counts

{_table_from_counts(counts.get("exclusion_reason", {}), "exclusion_reason")}

## Privacy Review Status Counts

{_table_from_counts(counts.get("privacy_review_status", {}), "privacy_review_status")}

## Consent Eligibility Counts

{_table_from_counts(counts.get("consent_eligibility", {}), "consent_eligibility")}

## Selected Deep Candidates By Bridge Family

{_table_from_counts(summary["selected_deep_candidates_by_bridge_family"], "rough_bridge_family")}

## Selected Deep Candidates By Surface Anchor

{_table_from_counts(summary["selected_deep_candidates_by_surface_anchor"], "surface_anchor")}

## Selected Deep Candidates By Student

{_table_from_counts(summary["selected_deep_candidates_by_student"], "student_id_hash")}

## Selected Deep Candidates By Problem

{_table_from_counts(summary["selected_deep_candidates_by_problem"], "problem_id_hash")}

## Interpretation Boundary

The 137 substantial candidate turns form a lightweight screening pool. They are used to describe the availability and diversity of real-student online AIChat dialogue-state candidates, not to report deep rubric annotations. The selected deep cases are chosen from this pool for privacy-reviewed case-specific annotation and are not the full online corpus.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize real-student online AIChat candidate-turn screening CSV."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_csv(args.input)
    summary = summarize(rows)
    json_text = json.dumps(summary, ensure_ascii=False, indent=2)
    args.output_json.write_text(json_text + "\n", encoding="utf-8")
    args.output_md.write_text(render_markdown(summary), encoding="utf-8")
    print(json_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
