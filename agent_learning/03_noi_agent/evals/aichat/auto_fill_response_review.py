"""Create development-only AI preliminary labels for response-review workbooks.

This helper is intentionally simple and conservative. It is for dev triage, not
coach gold labels.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from evals.aichat.export_coach_response_review_workbook_xlsx import export_xlsx


DEFAULT_OUTPUT_SUFFIX = ".ai_prelim.csv"


def _read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _choice_key(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if "｜" in text:
        return text.split("｜", 1)[0].strip()
    return text


def _numeric_choice(value, default: float = 0.0) -> float:
    key = _choice_key(value)
    try:
        return float(key)
    except (TypeError, ValueError):
        return default


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def _refuses_complete_answer(text: str) -> bool:
    return _contains_any(
        text,
        [
            "不能直接给完整",
            "不能直接给出完整",
            "不直接给完整",
            "不直接给出完整",
            "不会直接给完整",
            "不会直接给出完整",
            "不提供完整",
            "不要直接给完整",
            "不能把完整",
            "不把完整",
            "直接给完整代码反而",
            "直接给完整思路反而",
            "直接给完整答案反而",
        ],
    )


def _score_row(row: dict) -> dict:
    response = str(row.get("response_text") or "")
    compact = " ".join(response.split())
    has_action = _contains_any(compact, ["请", "先", "试", "观察", "判断", "回答", "列出", "说"])
    has_micro = _contains_any(compact, ["例子", "样例", "micro", "观察", "模拟", "假设"])
    high_burden = _contains_any(compact, ["完整表格", "完整推导", "多步", "全部", "完整模拟", "写代码"])
    vague_or_overwithheld = _contains_any(
        compact,
        ["再想想", "自己思考", "你觉得呢", "请补充题号", "请贴代码", "需要更多上下文", "无法判断"],
    )
    has_code_artifact = _contains_any(compact, ["代码如下", "#include", "```cpp", "```python", "def ", "for (", "while ("])
    claims_full_answer = _contains_any(
        compact,
        [
            "完整代码如下",
            "完整题解如下",
            "完整思路如下",
            "标准解如下",
            "完整代码：",
            "完整题解：",
            "完整思路：",
            "给出完整代码",
            "给出完整题解",
            "给出完整思路",
            "直接给你完整",
            "告诉你完整",
        ],
    )
    answer_or_code = has_code_artifact or (claims_full_answer and not _refuses_complete_answer(compact))
    major_bridge = _contains_any(
        compact,
        [
            "状态设",
            "转移方程",
            "check 返回 true",
            "check返回true",
            "边界更新",
            "加在 u",
            "端点u和v",
            "减在 lca",
            "减掉来抵消",
            "标记上应该有什么关系",
            "lazy 表示",
            "lazy标记就是",
            "子节点还没有",
            "倒序是为了",
            "已经包含了当前物品",
            "上一轮的状态",
            "当前行",
            "当前轮",
        ],
    )
    minor_bridge = not major_bridge and _contains_any(
        compact,
        ["dp[", "lazy", "check", "正序", "倒序", "LCA", "标记", "公式"],
    )

    if answer_or_code:
        leakage_label = "answer_leakage｜答案/代码泄露：给出完整题解、完整步骤或可提交代码"
        leakage_score = "0｜差：直接补完关键桥，或给完整答案/代码"
        reveal = "unjustified｜无教学理由：过早或过完整替学生补完当前关键桥"
        overall = "1｜不可用：不建议给学生看"
        would_show = "no｜不愿意：不应给学生看"
    elif major_bridge:
        leakage_label = "major_bridge_leakage｜严重桥梁泄露：直接补完当前关键桥"
        leakage_score = "0｜差：直接补完关键桥，或给完整答案/代码"
        reveal = "unjustified｜无教学理由：过早或过完整替学生补完当前关键桥"
        overall = "2｜勉强：问题较多，只能作为弱参考"
        would_show = "no｜不愿意：不应给学生看"
    elif minor_bridge:
        leakage_label = "minor_bridge_leakage｜轻微桥梁泄露：提示偏强但学生仍要推理"
        leakage_score = "1｜一般：给了偏强线索，但学生仍需自己推理"
        reveal = "borderline｜边界：有一定透露，但是否过早或过完整不确定"
        overall = "3｜可用：有帮助，但需要接受一些明显不足"
        would_show = "borderline｜勉强：需要人工改一下或有明显风险"
    else:
        leakage_label = "no_leakage｜无泄露：没有说穿当前关键桥"
        leakage_score = "2｜好：没有说穿当前关键桥"
        reveal = "no_reveal｜未透露：没有实质透露当前关键桥"
        overall = "4｜较好：可以给学生看，只有小问题" if has_action else "3｜可用：有帮助，但需要接受一些明显不足"
        would_show = "yes｜愿意：可以直接给学生看" if has_action else "borderline｜勉强：需要人工改一下或有明显风险"

    burden = (
        "high｜高：需要完整表格、多步推导、完整模拟、完整规则或代码"
        if high_burden
        else "low｜低：一两个关键词、局部判断或一句短句；选择题仅限不夹答案的低风险判断"
    )
    bridge_score = "2｜好：直接针对学生当前缺失的桥梁/卡点" if response else "0｜差：没有抓住当前卡点，或答非所问"
    grounded = "2｜好：明显利用题目、学生话语或近期对话证据" if response else "0｜差：像通用回答，和上下文关系弱"
    scaffold = "2｜好：帮助强度合适，不太弱也不过强" if not (answer_or_code or major_bridge) and has_action else "1｜一般：略弱或略强，但仍有教学价值"
    if answer_or_code or major_bridge:
        sufficiency = "1｜一般：略保守或略空泛，但学生仍能继续"
    elif vague_or_overwithheld and not has_micro:
        sufficiency = "0｜差：过度保留，安全但没帮助，或只让学生再想想"
    elif has_action:
        sufficiency = "2｜好：信息足够推进，既不泄露也不空泛"
    else:
        sufficiency = "1｜一般：略保守或略空泛，但学生仍能继续"
    clarity = "2｜好：学生下一步明确、具体、低输入成本，可用短回复完成" if has_action else "1｜一般：有下一步，但较宽、较多、略费力或不够具体"
    focus = "2｜好：始终围绕一个主要焦点推进" if len(response) < 900 else "1｜一般：基本单焦点，但有少量漂移"
    micro_app = "applicable｜适用：这条回复使用或应该使用微型例子" if has_micro else "not_applicable｜不适用：本轮不需要单独评价微型例子"
    micro_score = (
        "1｜一般：例子相关，但更像一次临时小任务"
        if has_micro and not major_bridge
        else ("0｜差：例子和卡点关系弱，或直接替学生补完关键桥" if has_micro else "")
    )

    scored = dict(row)
    scored.update(
        {
            "coach_bridge_identification_score": bridge_score,
            "coach_groundedness_score": grounded,
            "coach_scaffold_appropriateness_score": scaffold,
            "coach_scaffold_sufficiency_score": sufficiency,
            "coach_bridge_leakage_control_score": leakage_score,
            "coach_next_step_clarity_score": clarity,
            "coach_single_focus_coherence_score": focus,
            "coach_bridge_oriented_micro_example_score": micro_score,
            "coach_micro_example_applicability": micro_app,
            "coach_leakage_label": leakage_label,
            "coach_bridge_reveal_justification": reveal,
            "coach_preference_rank": "",
            "coach_overall_quality_score": overall,
            "coach_would_show_to_student": would_show,
            "coach_student_response_burden": burden,
            "coach_reviewer_confidence": "medium｜中：基本确定，但可能有边界",
            "coach_needs_discussion": "yes｜需要讨论" if major_bridge or answer_or_code else "no｜不需要讨论",
            "coach_notes": (
                "AI self-review, not coach gold: heuristic preliminary label for dev triage; "
                "请教练复核关键桥泄露、教学正当性和同题排序。"
            ),
            "review_status": "ai_prelim_reviewed｜AI 预评，待教练复核",
        }
    )
    return scored


def _rank_score(row: dict) -> tuple[float, float, float, float, float]:
    leakage_key = _choice_key(row.get("coach_leakage_label"))
    leakage_bonus = {
        "no_leakage": 2.0,
        "minor_bridge_leakage": 1.0,
        "major_bridge_leakage": 0.0,
        "answer_leakage": -1.0,
    }.get(leakage_key, 0.0)
    show_key = _choice_key(row.get("coach_would_show_to_student"))
    show_bonus = {"yes": 2.0, "borderline": 1.0, "no": 0.0}.get(show_key, 0.0)
    burden_key = _choice_key(row.get("coach_student_response_burden"))
    burden_bonus = {"low": 2.0, "medium": 1.0, "high": 0.0}.get(burden_key, 0.0)
    return (
        _numeric_choice(row.get("coach_overall_quality_score")),
        show_bonus,
        leakage_bonus,
        _numeric_choice(row.get("coach_scaffold_sufficiency_score")),
        burden_bonus,
    )


def _assign_preference_ranks(rows: list[dict]) -> None:
    rows_by_case: dict[str, list[dict]] = {}
    for row in rows:
        rows_by_case.setdefault(str(row.get("case_id") or ""), []).append(row)
    for case_rows in rows_by_case.values():
        ranked = sorted(
            enumerate(case_rows),
            key=lambda item: (_rank_score(item[1]), -item[0]),
            reverse=True,
        )
        for rank, (_, row) in enumerate(ranked, 1):
            row["coach_preference_rank"] = str(rank)


def auto_fill_review_csv(
    *,
    input_csv: Path,
    output_csv: Path | None = None,
    output_xlsx: Path | None = None,
) -> int:
    fieldnames, rows = _read_rows(input_csv)
    output_csv = output_csv or input_csv.with_name(input_csv.stem + DEFAULT_OUTPUT_SUFFIX)
    scored_rows = [_score_row(row) for row in rows]
    _assign_preference_ranks(scored_rows)
    _write_rows(output_csv, fieldnames, scored_rows)
    if output_xlsx is not None:
        export_xlsx(input_csv=output_csv, output_xlsx=output_xlsx)
    return len(scored_rows)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-prelim fill a response-review CSV for dev triage.")
    parser.add_argument("--input-csv", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--output-xlsx", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    output_csv = args.output_csv or args.input_csv.with_name(args.input_csv.stem + DEFAULT_OUTPUT_SUFFIX)
    row_count = auto_fill_review_csv(
        input_csv=args.input_csv,
        output_csv=output_csv,
        output_xlsx=args.output_xlsx,
    )
    print(json.dumps({"output_csv": str(output_csv), "output_xlsx": str(args.output_xlsx or ""), "row_count": row_count}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
