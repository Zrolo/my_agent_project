# Dialogue-State v3 Case/Source 审核汇总

本报告汇总教练在 case/source 审核表中填写的结构化字段；它不评价 AI 回复质量。

- input_xlsx: `/Users/kongyouli/Downloads/dialogue_state_v3_case_review_coach_A_round1_recheck_18_zh_rechecked.xlsx`
- sheet_name: `bucket_sheets`
- row_count: 18
- reviewed_count: 18
- needs_followup_count: 3

## 样本处理决定

`{'accept': 15, 'revise': 3}`

## 问题类型

`{'blank': 15, 'problem_bridge_mismatch': 3}`

## 审核置信度

`{'high': 14, 'medium': 4}`

## 需要后续处理的样本

| case_id | sheet | 决定 | 问题类型 | 置信度 | 修改建议 |
|---|---|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | 数据结构 | revise | problem_bridge_mismatch | high | P2672 更像贪心/贡献选择题，当前 update/query 和“节点摘要量”不贴题；建议改成贡献汇总/正确性样本，或换成真有数据结构维护操作的题。 |
| `dialogue_v3_036_correctness_invariant` | 正确性不变量 | revise | problem_bridge_mismatch | high | P10709 本质更像“状态表示/转移递推”的相邻限制 DP，不适合用相邻交换证明；建议换成 DP 桥梁桶，或换一题真正需要交换论证的贪心题。 |
| `dialogue_v3_037_correctness_invariant` | 正确性不变量 | revise | problem_bridge_mismatch | medium | P10728 更像排序后判断支配关系/维护扫描不变量，不是“两个选择顺序互换”；建议把 missing_bridge 改成支配关系判定，或换贪心交换题。 |
