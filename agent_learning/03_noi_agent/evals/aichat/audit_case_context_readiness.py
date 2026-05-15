"""Audit CP tutoring cases for context readiness before response ablations.

This deterministic audit separates cases that can fairly test tutoring quality
from cases that should primarily test clarification or safety behavior.
It does not call an LLM and does not change prompts or online AIChat.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


DEFAULT_INPUT_JSONL = Path("docs/research/bridgebench_cp_heldout_v3_50_draft.jsonl")
DEFAULT_OUTPUT_JSON = Path("docs/research/heldout_v3_50_context_readiness_audit_20260514.json")
DEFAULT_OUTPUT_JSONL = Path("docs/research/heldout_v3_50_context_readiness_audit_20260514.jsonl")
DEFAULT_OUTPUT_CSV = Path("docs/research/heldout_v3_50_context_readiness_audit_20260514.csv")
DEFAULT_OUTPUT_ZH_MD = Path("docs/research/heldout_v3_50_context_readiness_audit_20260514.zh.md")
DEFAULT_OUTPUT_MD = Path("docs/research/heldout_v3_50_context_readiness_audit_20260514.md")

VAGUE_PATTERNS = [
    "怎么列",
    "是哪种",
    "是哪一个",
    "是什么",
    "为什么这样",
    "为什么能这样",
    "这里怎么",
    "这个怎么",
    "这个咋",
    "哪一步",
    "分支",
    "前一个状态",
    "上一层",
    "这一步",
]

SPECIFIC_PATTERNS = [
    "check",
    "true",
    "false",
    "边界",
    "状态",
    "转移",
    "初始化",
    "为什么要",
    "从后往前",
    "lazy",
    "pushdown",
    "lca",
    "差分",
    "溢出",
    "数组",
    "wa",
    "tle",
    "re",
    "代码",
    "这一行",
]

POLICY_PATTERNS = [
    "完整代码",
    "直接给",
    "给答案",
    "直接答案",
    "题解",
    "帮我写完",
    "ac代码",
    "可提交代码",
]


def load_jsonl(path: Path) -> list[dict]:
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


def _compact_text(value: str | None) -> str:
    return "".join(str(value or "").split()).lower()


def _parse_dialogue(dialogue: str | None) -> list[tuple[str, str]]:
    text = str(dialogue or "").strip()
    if not text or text.upper() == "N/A":
        return []
    parsed: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        separator = "：" if "：" in line else ":"
        if separator not in line:
            continue
        role, content = line.split(separator, 1)
        role_key = role.strip().lower()
        if role_key in {"学生", "student", "user"}:
            parsed.append(("user", content.strip()))
        elif role_key in {"ai", "assistant", "教练", "老师", "助手"}:
            parsed.append(("assistant", content.strip()))
    return parsed


def _question_specificity(student_message: str, has_recent_dialogue: bool) -> str:
    compact = _compact_text(student_message)
    if any(pattern.lower() in compact for pattern in POLICY_PATTERNS):
        return "policy_request"
    if has_recent_dialogue and (len(compact) <= 24 or any(pattern in compact for pattern in VAGUE_PATTERNS)):
        return "pronoun_dependent"
    if len(compact) <= 16 or any(pattern in compact for pattern in VAGUE_PATTERNS):
        return "vague"
    if any(pattern.lower() in compact for pattern in SPECIFIC_PATTERNS) or len(compact) >= 35:
        return "specific"
    return "medium"


def audit_case_row(row: dict) -> dict:
    case_id = str(row.get("case_id") or row.get("id") or "")
    student_message = str(row.get("student_message") or "")
    recent_dialogue = str(row.get("recent_dialogue") or "")
    parsed_dialogue = _parse_dialogue(recent_dialogue)
    has_recent_dialogue = bool(parsed_dialogue)
    question_specificity = _question_specificity(student_message, has_recent_dialogue)
    has_problem_context = bool(
        str(
            row.get("problem_context")
            or row.get("problem_statement")
            or row.get("problem_statement_public_summary")
            or ""
        ).strip()
    )
    has_code = bool(str(row.get("student_code") or row.get("student_code_excerpt") or "").strip() not in {"", "N/A"})
    bridge_bucket = str(row.get("bridge_bucket") or row.get("category") or "")
    reasons: list[str] = []

    if not has_recent_dialogue:
        reasons.append("no_recent_dialogue")
    elif parsed_dialogue[-1][0] == "assistant":
        reasons.append("recent_dialogue_ends_with_assistant")
    else:
        last_user = _compact_text(parsed_dialogue[-1][1])
        current = _compact_text(student_message)
        if last_user == current:
            reasons.append("recent_dialogue_contains_current_student_message")
        else:
            reasons.append("recent_dialogue_last_student_differs")

    if question_specificity in {"vague", "pronoun_dependent"}:
        reasons.append(f"{question_specificity}_question")
    if question_specificity == "vague" and not has_recent_dialogue:
        reasons.append("short_vague_question_without_dialogue")
    if has_code:
        reasons.append("has_code_excerpt")
    if has_problem_context:
        reasons.append("has_problem_context")

    if question_specificity == "policy_request" or "direct_answer" in bridge_bucket:
        context_sufficiency = "partial"
        expected_tutor_move = "safe_refusal"
        model_should_infer_bridge = "no"
    elif question_specificity == "vague" and not has_recent_dialogue:
        context_sufficiency = "insufficient"
        expected_tutor_move = "clarify_context"
        model_should_infer_bridge = "no"
    elif question_specificity == "pronoun_dependent" and has_recent_dialogue:
        context_sufficiency = "sufficient" if parsed_dialogue[-1][0] == "assistant" else "partial"
        expected_tutor_move = "continue_prior_scaffold"
        model_should_infer_bridge = "yes" if context_sufficiency == "sufficient" else "low_confidence_only"
    elif has_code:
        context_sufficiency = "sufficient"
        expected_tutor_move = "micro_scaffold"
        model_should_infer_bridge = "yes"
    elif question_specificity == "specific":
        context_sufficiency = "partial" if not has_recent_dialogue else "sufficient"
        expected_tutor_move = "micro_scaffold"
        model_should_infer_bridge = "low_confidence_only" if context_sufficiency == "partial" else "yes"
    else:
        context_sufficiency = "partial"
        expected_tutor_move = "micro_scaffold"
        model_should_infer_bridge = "low_confidence_only"

    if context_sufficiency == "insufficient":
        recommended_use = "clarification_safety_slice"
    elif expected_tutor_move == "safe_refusal":
        recommended_use = "policy_safety_slice"
    elif context_sufficiency == "partial":
        recommended_use = "main_eval_with_caution"
    else:
        recommended_use = "main_scaffold_eval"

    return {
        "case_id": case_id,
        "problem_ref": row.get("problem_ref", ""),
        "problem_source_id": row.get("problem_source_id", ""),
        "bridge_bucket": bridge_bucket,
        "student_message": student_message,
        "recent_dialogue_status": reasons[0],
        "context_sufficiency": context_sufficiency,
        "current_question_specificity": question_specificity,
        "expected_tutor_move": expected_tutor_move,
        "model_should_infer_bridge": model_should_infer_bridge,
        "recommended_use": recommended_use,
        "audit_reasons": reasons,
    }


def summarize_audit_rows(rows: Iterable[dict]) -> dict:
    items = list(rows)
    return {
        "row_count": len(items),
        "context_sufficiency_counts": dict(Counter(row["context_sufficiency"] for row in items)),
        "question_specificity_counts": dict(Counter(row["current_question_specificity"] for row in items)),
        "expected_tutor_move_counts": dict(Counter(row["expected_tutor_move"] for row in items)),
        "model_should_infer_bridge_counts": dict(Counter(row["model_should_infer_bridge"] for row in items)),
        "recommended_use_counts": dict(Counter(row["recommended_use"] for row in items)),
        "recent_dialogue_status_counts": dict(Counter(row["recent_dialogue_status"] for row in items)),
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "problem_ref",
        "problem_source_id",
        "bridge_bucket",
        "student_message",
        "recent_dialogue_status",
        "context_sufficiency",
        "current_question_specificity",
        "expected_tutor_move",
        "model_should_infer_bridge",
        "recommended_use",
        "audit_reasons",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["audit_reasons"] = ";".join(row.get("audit_reasons") or [])
            writer.writerow({key: out.get(key, "") for key in fieldnames})


def _format_counts(counts: dict) -> str:
    return ", ".join(f"`{key}`={value}" for key, value in sorted(counts.items())) or "none"


def infer_dataset_label(path: Path) -> str:
    match = re.search(r"heldout_(v\d+)_", str(path))
    if match:
        return match.group(1)
    return "v3"


def render_report(summary: dict, *, language: str, dataset_label: str = "v3") -> str:
    title = f"Held-out {dataset_label} 50 Context Readiness Audit 20260514"
    zh_filename = f"heldout_{dataset_label}_50_context_readiness_audit_20260514.zh.md"
    en_filename = f"heldout_{dataset_label}_50_context_readiness_audit_20260514.md"
    if language == "zh":
        return "\n".join(
            [
                f"# {title}",
                "",
                f"English version: `{en_filename}`",
                "",
                "这份报告是 deterministic 数据审计，不调用 LLM，也不修改 prompt。目的不是评价模型，而是先判断每个 case 本身是否足够支撑“根据学生当前问题回答”的评测。",
                "",
                "## Summary",
                "",
                f"- 行数：{summary['row_count']}",
                f"- 上下文充分性：{_format_counts(summary['context_sufficiency_counts'])}",
                f"- 学生问题具体性：{_format_counts(summary['question_specificity_counts'])}",
                f"- 期望教学动作：{_format_counts(summary['expected_tutor_move_counts'])}",
                f"- 是否应推断 bridge：{_format_counts(summary['model_should_infer_bridge_counts'])}",
                f"- 推荐用途：{_format_counts(summary['recommended_use_counts'])}",
                "",
                "## Interpretation",
                "",
                "- `insufficient` 样本不应直接进入“谁的辅导质量最好”的主比较；它们更适合测试系统是否会澄清、是否少脑补。",
                "- `partial` 样本可以用于 dev，但正式分析时应单独标记或做 sensitivity analysis。",
                "- `sufficient` 样本更适合作为 scaffolding 主评测样本。",
                "- 如果短问题无近期对话，例如“分支该怎么列？”，好回复应优先澄清或给最小观察任务，而不是直接展开题解桥梁。",
            ]
        )
    return "\n".join(
        [
            f"# {title}",
            "",
            f"中文版本：`{zh_filename}`",
            "",
            "This is a deterministic data audit. It does not call an LLM and does not modify prompts. Its purpose is to check whether each case provides enough context to fairly evaluate whether a tutor answers the student's current question.",
            "",
            "## Summary",
            "",
            f"- Rows: {summary['row_count']}",
            f"- Context sufficiency: {_format_counts(summary['context_sufficiency_counts'])}",
            f"- Question specificity: {_format_counts(summary['question_specificity_counts'])}",
            f"- Expected tutor move: {_format_counts(summary['expected_tutor_move_counts'])}",
            f"- Should infer bridge: {_format_counts(summary['model_should_infer_bridge_counts'])}",
            f"- Recommended use: {_format_counts(summary['recommended_use_counts'])}",
            "",
            "## Interpretation",
            "",
            "- `insufficient` cases should not be used as primary evidence for tutoring quality; they mainly test clarification and hallucination control.",
            "- `partial` cases can be used in development, but formal analysis should mark them or run sensitivity analysis.",
            "- `sufficient` cases are better suited for the main scaffolding comparison.",
            "- For short questions without dialogue, such as asking how to list branches, a good response should clarify or give a minimal observation task instead of expanding the hidden bridge directly.",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit context readiness for CP tutoring cases.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_JSONL)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-zh-md", type=Path, default=DEFAULT_OUTPUT_ZH_MD)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--dataset-label", default=None)
    args = parser.parse_args(argv)

    cases = load_jsonl(args.input_jsonl)
    audit_rows = [audit_case_row(row) for row in cases]
    summary = summarize_audit_rows(audit_rows)
    payload = {"input_jsonl": str(args.input_jsonl), **summary, "rows": audit_rows}
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_jsonl(args.output_jsonl, audit_rows)
    write_csv(args.output_csv, audit_rows)
    dataset_label = args.dataset_label or infer_dataset_label(args.input_jsonl)
    args.output_zh_md.write_text(
        render_report(summary, language="zh", dataset_label=dataset_label) + "\n",
        encoding="utf-8",
    )
    args.output_md.write_text(
        render_report(summary, language="en", dataset_label=dataset_label) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output_json": str(args.output_json), "row_count": len(audit_rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
