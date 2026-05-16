import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


EXACT_FIELDS = [
    "student_problem_solving_state",
    "primary_bridge_family",
    "registered_focus_id",
    "max_scaffold_level",
    "leakage_risk",
]


def load_jsonl_by_case_id(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        row = json.loads(line)
        case_id = row.get("case_id")
        if not case_id:
            raise ValueError(f"Missing case_id at {path}:{line_number}")
        rows[str(case_id)] = row
    return rows


def _clean(value: object) -> str:
    return str(value or "").strip()


def _ratio(count: int, total: int) -> float | None:
    if total <= 0:
        return None
    return round(count / total, 3)


def _exact_agreement(paired_rows: list[tuple[dict, dict]], field: str) -> float | None:
    comparable = [(a, b) for a, b in paired_rows if _clean(a.get(field)) or _clean(b.get(field))]
    if not comparable:
        return None
    matches = sum(1 for a, b in comparable if _clean(a.get(field)) == _clean(b.get(field)))
    return _ratio(matches, len(comparable))


def _bridge_family_values(row: dict) -> set[str]:
    return {
        value
        for value in (
            _clean(row.get("primary_bridge_family")),
            _clean(row.get("secondary_bridge_family")),
        )
        if value
    }


def _focus_values(row: dict) -> set[str]:
    return {
        value
        for value in (
            _clean(row.get("registered_focus_id")),
            _clean(row.get("secondary_registered_focus_id")),
        )
        if value and value not in {"unknown", "not_applicable"}
    }


def _set_overlap_agreement(paired_rows: list[tuple[dict, dict]], value_fn) -> float | None:
    comparable = [(value_fn(a), value_fn(b)) for a, b in paired_rows if value_fn(a) or value_fn(b)]
    if not comparable:
        return None
    matches = sum(1 for a_values, b_values in comparable if bool(a_values & b_values))
    return _ratio(matches, len(comparable))


def _needs_adjudication(a: dict, b: dict) -> bool:
    if _clean(a.get("student_problem_solving_state")) != _clean(b.get("student_problem_solving_state")):
        return True
    if not (_bridge_family_values(a) & _bridge_family_values(b)):
        return True
    a_focus = _focus_values(a)
    b_focus = _focus_values(b)
    if (a_focus or b_focus) and not (a_focus & b_focus):
        return True
    if _clean(a.get("max_scaffold_level")) != _clean(b.get("max_scaffold_level")):
        return True
    return False


def summarize_agreement(annotator_a_jsonl: Path, annotator_b_jsonl: Path) -> dict:
    a_rows = load_jsonl_by_case_id(annotator_a_jsonl)
    b_rows = load_jsonl_by_case_id(annotator_b_jsonl)
    paired_case_ids = sorted(set(a_rows) & set(b_rows))
    paired_rows = [(a_rows[case_id], b_rows[case_id]) for case_id in paired_case_ids]
    exact = {field: _exact_agreement(paired_rows, field) for field in EXACT_FIELDS}
    relaxed = {
        "bridge_family_primary_or_secondary": _set_overlap_agreement(paired_rows, _bridge_family_values),
        "focus_primary_or_secondary": _set_overlap_agreement(paired_rows, _focus_values),
    }
    needs_adjudication = [
        case_id
        for case_id in paired_case_ids
        if _needs_adjudication(a_rows[case_id], b_rows[case_id])
    ]
    return {
        "annotator_a_jsonl": str(annotator_a_jsonl),
        "annotator_b_jsonl": str(annotator_b_jsonl),
        "annotator_a_count": len(a_rows),
        "annotator_b_count": len(b_rows),
        "paired_count": len(paired_case_ids),
        "unpaired_a_case_ids": sorted(set(a_rows) - set(b_rows)),
        "unpaired_b_case_ids": sorted(set(b_rows) - set(a_rows)),
        "exact_agreement": exact,
        "relaxed_agreement": relaxed,
        "needs_adjudication_count": len(needs_adjudication),
        "needs_adjudication_case_ids": needs_adjudication,
    }


def _format_rate(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.3f}"


def _metric_rows(summary: dict) -> list[tuple[str, str, float | None]]:
    exact = summary.get("exact_agreement") or {}
    relaxed = summary.get("relaxed_agreement") or {}
    return [
        ("student_problem_solving_state", "exact", exact.get("student_problem_solving_state")),
        ("primary_bridge_family", "exact", exact.get("primary_bridge_family")),
        ("registered_focus_id", "exact", exact.get("registered_focus_id")),
        ("max_scaffold_level", "exact", exact.get("max_scaffold_level")),
        ("leakage_risk", "exact", exact.get("leakage_risk")),
        (
            "bridge_family_primary_or_secondary",
            "relaxed",
            relaxed.get("bridge_family_primary_or_secondary"),
        ),
        ("focus_primary_or_secondary", "relaxed", relaxed.get("focus_primary_or_secondary")),
    ]


def render_report_zh(summary: dict) -> str:
    lines = [
        "# Coach Label Agreement Summary",
        "",
        "本报告汇总两个教练 reference JSONL 在 overlap case 上的一致性。它用于寻找需要裁决的样本，不代表任何一个教练标签是绝对真值。",
        "",
        "## 输入",
        "",
        f"- Coach A JSONL: `{summary.get('annotator_a_jsonl', '')}`",
        f"- Coach B JSONL: `{summary.get('annotator_b_jsonl', '')}`",
        f"- Coach A rows: {summary.get('annotator_a_count', 0)}",
        f"- Coach B rows: {summary.get('annotator_b_count', 0)}",
        f"- Paired overlap rows: {summary.get('paired_count', 0)}",
        "",
        "## 一致性指标",
        "",
        "| 字段 | 类型 | agreement |",
        "|---|---|---:|",
    ]
    for field, metric_type, value in _metric_rows(summary):
        lines.append(f"| `{field}` | {metric_type} | {_format_rate(value)} |")

    needs = summary.get("needs_adjudication_case_ids") or []
    lines.extend(
        [
            "",
            "## 需要裁决的样本",
            "",
            f"- needs_adjudication_count: {summary.get('needs_adjudication_count', len(needs))}",
        ]
    )
    if needs:
        lines.append("- case_ids: " + ", ".join(f"`{case_id}`" for case_id in needs))
    else:
        lines.append("- case_ids: none")

    unpaired_a = summary.get("unpaired_a_case_ids") or []
    unpaired_b = summary.get("unpaired_b_case_ids") or []
    lines.extend(
        [
            "",
            "## 未配对样本",
            "",
            "- Coach A only: " + (", ".join(f"`{case_id}`" for case_id in unpaired_a) if unpaired_a else "none"),
            "- Coach B only: " + (", ".join(f"`{case_id}`" for case_id in unpaired_b) if unpaired_b else "none"),
            "",
            "## 使用边界",
            "",
            "- 该报告用于 adjudication planning；",
            "- 不把 single-coach reference 当作唯一真值；",
            "- 正式 headline 前应裁决低置信、多桥梁、help level 和 leakage risk 重大分歧。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_report_en(summary: dict) -> str:
    lines = [
        "# Coach Label Agreement Summary",
        "",
        "This report summarizes agreement between two coach-reference JSONL files on overlap cases. It is used to identify cases needing adjudication; it does not treat either coach label as absolute truth.",
        "",
        "## Inputs",
        "",
        f"- Coach A JSONL: `{summary.get('annotator_a_jsonl', '')}`",
        f"- Coach B JSONL: `{summary.get('annotator_b_jsonl', '')}`",
        f"- Coach A rows: {summary.get('annotator_a_count', 0)}",
        f"- Coach B rows: {summary.get('annotator_b_count', 0)}",
        f"- Paired overlap rows: {summary.get('paired_count', 0)}",
        "",
        "## Agreement Metrics",
        "",
        "| Field | Type | agreement |",
        "|---|---|---:|",
    ]
    for field, metric_type, value in _metric_rows(summary):
        lines.append(f"| `{field}` | {metric_type} | {_format_rate(value)} |")

    needs = summary.get("needs_adjudication_case_ids") or []
    lines.extend(
        [
            "",
            "## Needs Adjudication",
            "",
            f"- needs_adjudication_count: {summary.get('needs_adjudication_count', len(needs))}",
        ]
    )
    if needs:
        lines.append("- case_ids: " + ", ".join(f"`{case_id}`" for case_id in needs))
    else:
        lines.append("- case_ids: none")

    unpaired_a = summary.get("unpaired_a_case_ids") or []
    unpaired_b = summary.get("unpaired_b_case_ids") or []
    lines.extend(
        [
            "",
            "## Unpaired Cases",
            "",
            "- Coach A only: " + (", ".join(f"`{case_id}`" for case_id in unpaired_a) if unpaired_a else "none"),
            "- Coach B only: " + (", ".join(f"`{case_id}`" for case_id in unpaired_b) if unpaired_b else "none"),
            "",
            "## Boundary",
            "",
            "- Use this report for adjudication planning.",
            "- Do not treat a single-coach reference as the only truth.",
            "- Before headline claims, adjudicate low-confidence, multi-bridge, help-level, and leakage-risk disagreements.",
        ]
    )
    return "\n".join(lines) + "\n"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize agreement between two coach v2 JSONL label files.")
    parser.add_argument("--annotator-a-jsonl", type=Path, required=True)
    parser.add_argument("--annotator-b-jsonl", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md-zh", type=Path)
    parser.add_argument("--output-md", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None, *, stdout: TextIO | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    summary = summarize_agreement(args.annotator_a_jsonl, args.annotator_b_jsonl)
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    if args.output_md_zh:
        args.output_md_zh.parent.mkdir(parents=True, exist_ok=True)
        args.output_md_zh.write_text(render_report_zh(summary), encoding="utf-8")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_report_en(summary), encoding="utf-8")
    output = stdout or sys.stdout
    output.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
