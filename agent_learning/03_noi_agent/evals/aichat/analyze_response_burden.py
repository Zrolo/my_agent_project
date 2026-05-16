"""Analyze student response burden in reviewed tutor responses.

This is a development-stage heuristic analyzer. It does not judge tutoring
quality by itself; it adds a light "how much does the student have to type or
work out next?" signal to existing coach blind-review labels.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


DEFAULT_INPUT_LABELS_JSONL = Path(
    "docs/research/coach_response_review_labels_dev_ablation_safe_scaffold_20260512.jsonl"
)
DEFAULT_OUTPUT_LABELS_JSONL = Path(
    "docs/research/coach_response_review_labels_dev_ablation_safe_scaffold_20260512.with_burden.jsonl"
)
DEFAULT_OUTPUT_JSON = Path(
    "docs/research/dev_ablation_response_burden_analysis_20260512.summary.json"
)
DEFAULT_OUTPUT_MD_ZH = Path(
    "docs/research/dev_ablation_response_burden_analysis_20260512.zh.md"
)
DEFAULT_OUTPUT_MD = Path(
    "docs/research/dev_ablation_response_burden_analysis_20260512.md"
)

CORE_SCORE_KEYS = [
    "bridge_identification",
    "groundedness",
    "scaffold_appropriateness",
    "bridge_leakage_control",
    "next_step_clarity",
    "single_focus_coherence",
]

HIGH_PATTERNS: list[tuple[str, str]] = [
    ("multi_step_trace", r"(手动)?模拟整个|整个过程|全过程|每一步|依次写出|逐步推导|完整推导|完整模拟"),
    ("full_rule", r"完整(规则|公式|状态定义|转移|check|边界|算法|解法|题解)"),
    ("full_table", r"(完整)?表格|填完整张表|整张表|状态表|转移表"),
    ("all_items", r"列出.*(所有|全部|每个)|写出.*(所有|全部|每个)|全部写出来"),
    ("proof_burden", r"证明.*为什么|完整证明|严格证明|解释.*正确性"),
    ("code_completion", r"(写出|补全|给出|生成).{0,8}(完整)?(代码|伪代码)"),
]

LOW_PATTERNS: list[tuple[str, str]] = [
    ("short_choice", r"A/B|A\)|B\)|会/不会|是/否|对/错|true/false|True/False|选一个|选项"),
    ("one_word_or_phrase", r"只写|只回答|一个词|两个词|短句|一句话|一句短句|一行"),
    ("yes_no", r"有没有|是否|能不能|会不会|是不是"),
]

MEDIUM_PATTERNS: list[tuple[str, str]] = [
    ("brief_reason", r"说.*理由|解释一下|为什么|你觉得|判断一下"),
    ("small_local_task", r"举一个|挑一个|算一下|改一处|看一个|对比一下"),
]


def _float(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return round(sum(values) / len(values), 4) if values else 0.0


def _core_scores(row: dict) -> list[float]:
    scores = row.get("scores") or {}
    return [_float(scores.get(key)) for key in CORE_SCORE_KEYS]


def student_ready_pass(row: dict) -> bool:
    if _float(row.get("overall_quality_score")) < 4:
        return False
    if row.get("would_show_to_student") != "yes":
        return False
    if row.get("leakage_label") in {"major_bridge_leakage", "answer_leakage"}:
        return False
    return all(score > 0 for score in _core_scores(row))


def _is_negated_context(text: str, start: int) -> bool:
    prefix = text[max(0, start - 12) : start]
    return bool(re.search(r"不要|先不要|别|不需要|不用|禁止|不要急着", prefix))


def _matched(
    patterns: list[tuple[str, str]],
    text: str,
    *,
    skip_negated: bool = False,
) -> list[tuple[str, str]]:
    output = []
    for reason, pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            if skip_negated and _is_negated_context(text, match.start()):
                continue
            output.append((reason, pattern))
            break
    return output


def classify_student_response_burden(text: str) -> dict:
    """Classify how demanding the tutor's next requested student action is."""

    text = str(text or "")
    high_matches = _matched(HIGH_PATTERNS, text, skip_negated=True)
    low_matches = _matched(LOW_PATTERNS, text)
    medium_matches = _matched(MEDIUM_PATTERNS, text)
    question_count = text.count("?") + text.count("？")

    reasons: list[str] = []
    matched_patterns: list[str] = []

    if high_matches or question_count >= 4:
        burden = "high"
        reasons.extend(reason for reason, _ in high_matches)
        matched_patterns.extend(pattern for _, pattern in high_matches)
        if question_count >= 4:
            reasons.append("many_questions")
            matched_patterns.append("question_count>=4")
    elif low_matches:
        burden = "low"
        reasons.extend(reason for reason, _ in low_matches)
        matched_patterns.extend(pattern for _, pattern in low_matches)
    elif medium_matches or question_count >= 2:
        burden = "medium"
        reasons.extend(reason for reason, _ in medium_matches)
        matched_patterns.extend(pattern for _, pattern in medium_matches)
        if question_count >= 2:
            reasons.append("multiple_questions")
            matched_patterns.append("question_count>=2")
    else:
        burden = "medium"
        reasons.append("default_medium")

    return {
        "student_response_burden": burden,
        "burden_reasons": sorted(set(reasons)),
        "burden_matched_patterns": matched_patterns,
        "burden_question_count": question_count,
        "burden_is_heuristic": True,
    }


def load_jsonl(path: Path | str) -> list[dict]:
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL row") from exc
    return rows


def write_jsonl(path: Path | str, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def annotate_rows_with_burden(rows: list[dict]) -> list[dict]:
    output = []
    for row in rows:
        response_text = row.get("response_text") or row.get("final_response_text") or ""
        annotated = dict(row)
        manual_burden = str(
            row.get("coach_student_response_burden") or row.get("student_response_burden") or ""
        ).strip()
        if manual_burden in {"low", "medium", "high"}:
            annotated.update(
                {
                    "student_response_burden": manual_burden,
                    "burden_reasons": [],
                    "burden_matched_patterns": [],
                    "burden_question_count": response_text.count("?") + response_text.count("？"),
                    "burden_is_heuristic": False,
                    "burden_source": "coach_review",
                }
            )
        else:
            heuristic = classify_student_response_burden(response_text)
            heuristic["burden_source"] = "heuristic"
            annotated.update(heuristic)
        output.append(annotated)
    return output


def _condition(row: dict) -> str:
    return str(row.get("condition_id") or row.get("system") or row.get("tutor_mode") or "")


def _leakage_bucket(row: dict) -> str:
    label = row.get("leakage_label")
    if label in {"major_bridge_leakage", "answer_leakage"}:
        return "major_or_answer"
    if label == "minor_bridge_leakage":
        return "minor"
    if label == "no_leakage":
        return "no_leakage"
    return str(label or "unknown")


def _shorten(text: str, limit: int = 140) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _burden_counter(rows: list[dict]) -> dict:
    order = {"low": 0, "medium": 1, "high": 2}
    counter = Counter(row.get("student_response_burden") for row in rows)
    return {
        key: counter[key]
        for key in sorted(counter, key=lambda item: order.get(str(item), 99))
    }


def build_condition_summary(rows: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[_condition(row)].append(row)

    summary = {}
    for condition, condition_rows in sorted(grouped.items()):
        burden_counts = Counter(row.get("student_response_burden") for row in condition_rows)
        leakage_counts = Counter(_leakage_bucket(row) for row in condition_rows)
        show_counts = Counter(row.get("would_show_to_student") for row in condition_rows)
        n = len(condition_rows)
        summary[condition] = {
            "n": n,
            "low_count": burden_counts.get("low", 0),
            "medium_count": burden_counts.get("medium", 0),
            "high_count": burden_counts.get("high", 0),
            "high_rate": round(burden_counts.get("high", 0) / n, 4) if n else 0.0,
            "overall_quality_mean": _mean(
                _float(row.get("overall_quality_score")) for row in condition_rows
            ),
            "next_step_clarity_mean": _mean(
                _float((row.get("scores") or {}).get("next_step_clarity"))
                for row in condition_rows
            ),
            "student_ready_pass_count": sum(1 for row in condition_rows if student_ready_pass(row)),
            "student_ready_pass_rate": round(
                sum(1 for row in condition_rows if student_ready_pass(row)) / n, 4
            )
            if n
            else 0.0,
            "would_show_yes_count": show_counts.get("yes", 0),
            "would_show_borderline_count": show_counts.get("borderline", 0),
            "would_show_no_count": show_counts.get("no", 0),
            "no_leakage_count": leakage_counts.get("no_leakage", 0),
            "minor_leakage_count": leakage_counts.get("minor", 0),
            "major_or_answer_leakage_count": leakage_counts.get("major_or_answer", 0),
        }
    return summary


def _binary_counter(rows: list[dict], predicate) -> dict:
    output = Counter("pass" if predicate(row) else "fail" for row in rows)
    return dict(sorted(output.items()))


def build_payload(rows: list[dict]) -> dict:
    high_examples = []
    for row in rows:
        if row.get("student_response_burden") != "high":
            continue
        high_examples.append(
            {
                "case_id": row.get("case_id"),
                "condition_id": _condition(row),
                "overall_quality_score": row.get("overall_quality_score"),
                "would_show_to_student": row.get("would_show_to_student"),
                "leakage_label": row.get("leakage_label"),
                "burden_reasons": row.get("burden_reasons") or [],
                "response_snippet": _shorten(
                    row.get("response_text") or row.get("final_response_text") or ""
                ),
            }
        )

    return {
        "row_count": len(rows),
        "case_count": len({row.get("case_id") for row in rows}),
        "burden_counts": _burden_counter(rows),
        "burden_source_counts": dict(Counter(row.get("burden_source") for row in rows)),
        "condition_summary": build_condition_summary(rows),
        "would_show_by_burden": _binary_counter(
            rows, lambda row: row.get("would_show_to_student") == "yes"
        ),
        "student_ready_by_burden": _binary_counter(rows, student_ready_pass),
        "leakage_by_burden": dict(Counter(_leakage_bucket(row) for row in rows)),
        "high_burden_examples": high_examples[:20],
    }


def _table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def _condition_rows(payload: dict) -> list[list[object]]:
    rows = []
    for condition, item in payload["condition_summary"].items():
        rows.append(
            [
                condition,
                item["n"],
                f"{item['low_count']}/{item['medium_count']}/{item['high_count']}",
                item["high_rate"],
                item["overall_quality_mean"],
                item["next_step_clarity_mean"],
                f"{item['student_ready_pass_count']}/{item['n']}",
                f"{item['would_show_yes_count']}/{item['would_show_borderline_count']}/{item['would_show_no_count']}",
                f"{item['no_leakage_count']}/{item['minor_leakage_count']}/{item['major_or_answer_leakage_count']}",
            ]
        )
    return rows


def _example_rows(payload: dict) -> list[list[object]]:
    return [
        [
            item.get("case_id"),
            item.get("condition_id"),
            item.get("overall_quality_score"),
            item.get("would_show_to_student"),
            item.get("leakage_label"),
            ", ".join(item.get("burden_reasons") or []),
            item.get("response_snippet"),
        ]
        for item in payload["high_burden_examples"]
    ]


def render_report_zh(payload: dict, *, input_path: Path) -> str:
    return "\n\n".join(
        [
            "# Dev Ablation 回复负担分析（2026-05-12）",
            (
                "本报告基于已有 dev ablation 盲评标签做启发式二次分析，不重新生成回复，"
                "也不把该启发式标签当作人工 gold。它回答的问题是：哪些回复虽然可能质量不错，"
                "但要求学生下一轮输入过长、过完整或过费力。"
            ),
            f"- 输入标签：`{input_path}`\n- 已分析回复：{payload['row_count']} 条\n- case 数：{payload['case_count']} 个\n- 回复负担分布：{payload['burden_counts']}\n- 负担标签来源：{payload['burden_source_counts']}",
            "## 系统汇总",
            _table(
                [
                    "condition",
                    "n",
                    "low/medium/high",
                    "high rate",
                    "overall",
                    "next-step",
                    "ready",
                    "show yes/border/no",
                    "leak no/minor/major+answer",
                ],
                _condition_rows(payload),
            ),
            "## 高负担样例",
            _table(
                ["case", "condition", "overall", "show", "leakage", "reason", "snippet"],
                _example_rows(payload),
            ),
            "## 解读边界",
            "\n".join(
                [
                    "- `low`：学生通常只需选 A/B、回答会/不会、写一两个词或一句短句。",
                    "- `medium`：学生需要一两句理由、小范围判断或局部计算。",
                    "- `high`：回复要求完整表格、多步推导、完整规则、完整模拟或代码/伪代码，容易让真实学生放弃输入。",
                    "- 新版盲评表会优先读取教练人工填写的 `coach_student_response_burden`；旧表没有该列时才使用启发式兜底。",
                    "- 启发式标签不替代教练盲评；正式 50-case headline 应优先使用人工标注的回复负担。",
                ]
            ),
        ]
    ) + "\n"


def render_report_en(payload: dict, *, input_path: Path) -> str:
    return "\n\n".join(
        [
            "# Dev Ablation Response Burden Analysis (2026-05-12)",
            (
                "This report adds a heuristic student-response-burden signal to existing dev "
                "ablation blind-review labels. It does not regenerate responses and should not "
                "be treated as coach gold."
            ),
            f"- Input labels: `{input_path}`\n- Rows: {payload['row_count']}\n- Cases: {payload['case_count']}\n- Burden counts: {payload['burden_counts']}\n- Burden source counts: {payload['burden_source_counts']}",
            "## Condition Summary",
            _table(
                [
                    "condition",
                    "n",
                    "low/medium/high",
                    "high rate",
                    "overall",
                    "next-step",
                    "ready",
                    "show yes/border/no",
                    "leak no/minor/major+answer",
                ],
                _condition_rows(payload),
            ),
            "## High-burden Examples",
            _table(
                ["case", "condition", "overall", "show", "leakage", "reason", "snippet"],
                _example_rows(payload),
            ),
            "## Interpretation Boundary",
            "\n".join(
                [
                    "- `low`: the student can usually answer with A/B, yes/no, a word, or one short sentence.",
                    "- `medium`: the student needs one or two short reasons, a local judgment, or a small calculation.",
                    "- `high`: the response asks for a full table, multi-step derivation, complete rule, full trace, code, or pseudocode.",
                    "- New review workbooks prefer the coach-filled `coach_student_response_burden`; the heuristic is only a fallback for older labels.",
                    "- Heuristic labels should be calibrated by coach review before being used as a headline metric.",
                ]
            ),
        ]
    ) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-labels-jsonl", type=Path, default=DEFAULT_INPUT_LABELS_JSONL)
    parser.add_argument("--output-labels-jsonl", type=Path, default=DEFAULT_OUTPUT_LABELS_JSONL)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md-zh", type=Path, default=DEFAULT_OUTPUT_MD_ZH)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows = load_jsonl(args.input_labels_jsonl)
    annotated = annotate_rows_with_burden(rows)
    payload = build_payload(annotated)

    write_jsonl(args.output_labels_jsonl, annotated)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_md_zh.parent.mkdir(parents=True, exist_ok=True)
    args.output_md_zh.write_text(
        render_report_zh(payload, input_path=args.input_labels_jsonl),
        encoding="utf-8",
    )
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(
        render_report_en(payload, input_path=args.input_labels_jsonl),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
