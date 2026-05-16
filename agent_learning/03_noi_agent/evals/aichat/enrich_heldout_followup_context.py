"""Create a v4 held-out draft with richer follow-up context.

The v3 draft intentionally kept 10 short no-dialogue cases, but the context
readiness audit showed they should be treated as clarification/safety cases
rather than main scaffolding cases. This module creates a separate v4 draft
that keeps the same Luogu-grounded student questions while adding a minimal
prior student/AI exchange so the current short question becomes a plausible
follow-up turn.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from evals.aichat.audit_case_context_readiness import audit_case_row, summarize_audit_rows
from evals.aichat.generate_luogu_heldout_v2_50 import export_source_and_case_review_workbook
from evals.aichat.validate_heldout_50_dataset import validate_dataset


DEFAULT_INPUT_JSONL = Path("docs/research/bridgebench_cp_heldout_v3_50_draft.jsonl")
DEFAULT_OUTPUT_JSONL = Path("docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl")
DEFAULT_REVIEW_XLSX = Path("docs/research/heldout_v4_50_source_and_case_review.zh.xlsx")
DEFAULT_REPORT_JSON = Path("docs/research/bridgebench_cp_heldout_v4_50_generation_report_20260514.json")
DEFAULT_REPORT_ZH_MD = Path("docs/research/bridgebench_cp_heldout_v4_50_generation_report_20260514.zh.md")
DEFAULT_REPORT_MD = Path("docs/research/bridgebench_cp_heldout_v4_50_generation_report_20260514.md")
DEFAULT_VALIDATION_JSON = Path("docs/research/bridgebench_cp_heldout_v4_50_validation_report_20260514.json")


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


def _last_assistant_reply(recent_dialogue: str) -> str:
    for line in reversed(str(recent_dialogue or "").splitlines()):
        text = line.strip()
        lower = text.lower()
        if lower.startswith("ai:") or lower.startswith("assistant:") or text.startswith("AI："):
            separator = "：" if "：" in text else ":"
            return text.split(separator, 1)[1].strip()
    return ""


def _bridge_probe_dialogue(row: dict) -> tuple[str, str]:
    bucket = str(row.get("bridge_bucket") or "")
    student_message = str(row.get("student_message") or "")
    compact_message = "".join(student_message.split()).lower()
    if bucket.startswith("state_") or "representation" in bucket:
        student = "我看完题面和样例了，大概知道要用动态规划，但不知道该从哪一步开始。"
        if "dp" in compact_message or "这一格" in compact_message:
            assistant = "先别急着写转移。你可以先定位到表里的一个格子：它应该回答的是“到这个阶段为止的什么信息”？"
        elif "数组" in compact_message or "存什么" in compact_message:
            assistant = "先不看代码。你可以先想这个数组每个位置是在记录一个结果、一个限制，还是一个仍要继续比较的候选？"
        elif "哪些量" in compact_message:
            assistant = "先别把所有量都塞进状态。你可以先列两个会影响后面决策的量，再判断哪些只是临时计算。"
        elif "维度" in compact_message:
            assistant = "先把维度当作“会影响后续选择的信息”来筛。你现在最不确定的是要不要记录位置、容量，还是额外状态？"
        elif "不会设" in compact_message:
            assistant = "先从样例里挑一个中间时刻。你不需要马上写公式，只要先说后面决策会依赖哪些已经发生的信息。"
        else:
            assistant = "先别急着写公式。你现在最不确定的是状态表示、转移来源，还是实现细节？只说最卡的一点就行。"
    elif bucket.startswith("transition_"):
        student = "我能看懂题意，也知道大概要递推，但具体推的时候分不清来源。"
        if "分支" in compact_message:
            assistant = "先别急着合并成公式。你可以先把当前位置的选择拆成两类：保留当前对象，还是把它排除？"
        elif "前一个状态" in compact_message:
            assistant = "先别写完整递推。你可以先想：当前目标如果已经被确定，上一层/上一步需要少掉哪一部分信息？"
        elif "从哪转" in compact_message:
            assistant = "先盯住一个目标状态。别写完整式子，只问：到达它之前，最后一步可能发生了哪种操作？"
        elif "递推" in compact_message:
            assistant = "先把递推拆成“当前要算谁”和“它依赖谁”。你可以先说目标量，再说一个可能来源。"
        else:
            assistant = "先把问题缩小：你现在卡的是前一个状态从哪来、分支怎么拆，还是循环顺序？只说最卡的一点就行。"
    elif "predicate" in bucket or "check" in bucket:
        student = "我知道可能要判一个条件，但总是不确定这个条件应该代表什么。"
        assistant = "先别写代码。你现在最不确定的是 true 的含义、false 的含义，还是边界怎么动？只说最卡的一点。"
    elif "implementation" in bucket or "debug" in bucket:
        student = "我写了一点代码，但不确定错在思路还是实现细节。"
        assistant = "先把问题缩小到一个位置：你现在最不确定的是初始化、循环边界、变量含义，还是某一行判断？"
    else:
        student = "我看了题面，样例大概能跟，但自己写的时候不知道先卡在哪里。"
        assistant = "先别急着写完整思路。你现在最不确定的是表示、关系、判定，还是实现？只说一个最卡的点。"
    return f"学生：{student}\nAI：{assistant}", assistant


def _next_case_id(index: int, version: str) -> str:
    return f"heldout_{version}_luogu_{index:03d}"


def enrich_rows_for_followup_scaffold(rows: list[dict], *, version: str = "v4") -> list[dict]:
    enriched: list[dict] = []
    for index, row in enumerate(rows, 1):
        new_row = dict(row)
        original_case_id = str(row.get("case_id") or row.get("id") or "")
        new_row["source_case_id"] = original_case_id
        new_row["case_id"] = _next_case_id(index, version)
        new_row["id"] = new_row["case_id"]

        audit = audit_case_row(row)
        if audit["context_sufficiency"] == "insufficient" and audit["expected_tutor_move"] == "clarify_context":
            recent_dialogue, prior_ai = _bridge_probe_dialogue(row)
            new_row["recent_dialogue"] = recent_dialogue
            new_row["context_ai_reply"] = prior_ai
            new_row["turn_position"] = "followup"
            new_row["context_type"] = "followup_after_context_probe"
            new_row["student_scaffold_followability"] = "F2"
            new_row["expected_tutor_move"] = "continue_prior_scaffold"
            new_row["prior_ai_scaffold"] = prior_ai
            new_row["student_reply_to_prior_scaffold"] = str(row.get("student_message") or "")
            new_row["context_enrichment_status"] = "synthetic_followup_context_added"
        else:
            new_row["context_enrichment_status"] = "context_preserved"
            if new_row.get("recent_dialogue") and not new_row.get("context_ai_reply"):
                new_row["context_ai_reply"] = _last_assistant_reply(new_row["recent_dialogue"])
        new_row["reference_label_status"] = "draft_needs_coach_review"
        enriched.append(new_row)
    return enriched


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def _render_report(summary: dict, *, language: str) -> str:
    audit_summary = summary["context_readiness_summary"]
    status_counts = summary["context_enrichment_status_counts"]
    if language == "zh":
        return "\n".join(
            [
                "# BridgeBench CP Held-out v4 50 Draft Generation Report 20260514",
                "",
                "English version: `bridgebench_cp_heldout_v4_50_generation_report_20260514.md`",
                "",
                "v4 是在 v3 基础上生成的 follow-up scaffold 版本，不覆盖 v3。它专门修复 v3 前 10 条短问无上下文样本导致模型容易脑补的问题。",
                "",
                "## Summary",
                "",
                f"- 行数：{summary['row_count']}",
                f"- 上下文增强状态：{status_counts}",
                f"- 上下文充分性：{audit_summary['context_sufficiency_counts']}",
                f"- 推荐用途：{audit_summary['recommended_use_counts']}",
                "",
                "## 使用边界",
                "",
                "- v4 的新增近期对话是 synthetic-but-grounded：基于真实题面和原学生短问补一个最小上一轮 AI probe。",
                "- v4 更适合用于 50-case generation-only 和 scaffold 主实验前的 dev run。",
                "- v3 仍保留为混合数据，可以单独报告 `clarification_safety_slice`。",
                "- v4 仍是 `draft_needs_coach_review`，不能称为 gold。",
            ]
        )
    return "\n".join(
        [
            "# BridgeBench CP Held-out v4 50 Draft Generation Report 20260514",
            "",
            "中文版本：`bridgebench_cp_heldout_v4_50_generation_report_20260514.zh.md`",
            "",
            "v4 is generated from v3 without overwriting it. It enriches the first 10 short no-dialogue cases with a minimal prior AI probe so they can function as follow-up scaffold cases.",
            "",
            "## Summary",
            "",
            f"- Rows: {summary['row_count']}",
            f"- Context enrichment status: {status_counts}",
            f"- Context sufficiency: {audit_summary['context_sufficiency_counts']}",
            f"- Recommended use: {audit_summary['recommended_use_counts']}",
            "",
            "## Boundary",
            "",
            "- The new recent dialogues are synthetic-but-grounded: they add a minimal prior AI probe based on the real problem and the original short student question.",
            "- v4 is better suited for the 50-case generation-only dev run and scaffold comparison.",
            "- v3 remains available as a mixed dataset and can still support the `clarification_safety_slice` analysis.",
            "- v4 remains `draft_needs_coach_review`; it is not gold.",
        ]
    )


def build_summary(rows: list[dict]) -> dict:
    audit_rows = [audit_case_row(row) for row in rows]
    return {
        "row_count": len(rows),
        "context_enrichment_status_counts": dict(Counter(row.get("context_enrichment_status", "") for row in rows)),
        "context_readiness_summary": summarize_audit_rows(audit_rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create v4 held-out draft with follow-up context enrichment.")
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT_JSONL)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT_JSONL)
    parser.add_argument("--review-xlsx", type=Path, default=DEFAULT_REVIEW_XLSX)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-zh-md", type=Path, default=DEFAULT_REPORT_ZH_MD)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--validation-json", type=Path, default=DEFAULT_VALIDATION_JSON)
    parser.add_argument("--version", default="v4")
    args = parser.parse_args(argv)

    rows = load_jsonl(args.input_jsonl)
    enriched = enrich_rows_for_followup_scaffold(rows, version=args.version)
    write_jsonl(args.output_jsonl, enriched)
    export_source_and_case_review_workbook(enriched, args.review_xlsx)
    summary = build_summary(enriched)
    args.report_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report_zh_md.write_text(_render_report(summary, language="zh") + "\n", encoding="utf-8")
    args.report_md.write_text(_render_report(summary, language="en") + "\n", encoding="utf-8")
    validation = validate_dataset(args.output_jsonl)
    args.validation_json.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_jsonl": str(args.output_jsonl),
                "row_count": len(enriched),
                "context_enrichment_status_counts": summary["context_enrichment_status_counts"],
                "validation_ok": validation.get("ok"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
