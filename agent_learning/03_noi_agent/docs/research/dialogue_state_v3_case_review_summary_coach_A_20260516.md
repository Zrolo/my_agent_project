# Dialogue-State v3 Case/Source Review Summary

This report summarizes structured fields from the coach case/source review workbook. It does not evaluate AI response quality.

- input_xlsx: `/Users/kongyouli/Downloads/dialogue_state_v3_50_source_and_case_review_zh6_case_source_reviewed (1).xlsx`
- sheet_name: `bucket_sheets`
- row_count: 50
- reviewed_count: 50
- needs_followup_count: 18

## Case Decisions

`{'accept': 32, 'revise': 18}`

## Issue Types

`{'none': 32, 'context_mismatch': 11, 'bridge_label_issue': 7}`

## Reviewer Confidence

`{'high': 42, 'medium': 8}`

## Cases Needing Follow-up

| case_id | sheet | decision | issue | confidence | suggestion |
|---|---|---|---|---|---|
| `dialogue_v3_027_aggregation_contribution_summary` | 贡献汇总 | revise | context_mismatch | high | 当前学生回复在说 true/另一边/边界方向，不像在回应“追踪一次操作影响哪些位置”。把学生当前问题改成围绕加减标记、抵消点或前缀汇总的位置。 |
| `dialogue_v3_028_aggregation_contribution_summary` | 贡献汇总 | revise | context_mismatch | high | 当前学生回复在说 true/另一边/边界方向，不像在回应“追踪一次操作影响哪些位置”。把学生当前问题改成围绕加减标记、抵消点或前缀汇总的位置。 |
| `dialogue_v3_029_aggregation_contribution_summary` | 贡献汇总 | revise | context_mismatch | high | 当前学生回复在说 true/另一边/边界方向，不像在回应“追踪一次操作影响哪些位置”。把学生当前问题改成围绕加减标记、抵消点或前缀汇总的位置。 |
| `dialogue_v3_030_aggregation_contribution_summary` | 贡献汇总 | revise | context_mismatch | high | 当前学生回复在说 true/另一边/边界方向，不像在回应“追踪一次操作影响哪些位置”。把学生当前问题改成围绕加减标记、抵消点或前缀汇总的位置。 |
| `dialogue_v3_031_data_structure_operation_semantics` | 数据结构 | revise | context_mismatch | high | 学生回复是二分/边界方向话术，不是在谈 update/query 维护什么摘要。要改成“节点里到底存什么/更新后哪个量要保持正确”。 |
| `dialogue_v3_032_data_structure_operation_semantics` | 数据结构 | revise | context_mismatch | high | 学生回复是二分/边界方向话术，不是在谈 update/query 维护什么摘要。要改成“节点里到底存什么/更新后哪个量要保持正确”。 |
| `dialogue_v3_033_data_structure_operation_semantics` | 数据结构 | revise | bridge_label_issue | medium | 学生已经转到调试“该打印哪个中间量”，不只是数据结构语义。若留在本桶，应让当前问题直接问一次 update/query 后维护量是什么。 |
| `dialogue_v3_034_data_structure_operation_semantics` | 数据结构 | revise | bridge_label_issue | medium | 当前问题更像实现边界或更新顺序错误，不是单纯数据结构维护语义。建议改学生话术，聚焦“查询为什么能由这些维护量拼出来”。 |
| `dialogue_v3_035_data_structure_operation_semantics` | 数据结构 | revise | bridge_label_issue | medium | “初始化/下标/更新顺序”把样本推向实现边界了。要么换桶，要么把当前问题改成结构里哪个摘要量被更新错了。 |
| `dialogue_v3_036_correctness_invariant` | 正确性不变量 | revise | context_mismatch | high | 近期对话在讲交换/不变量，但学生当前回复转成样例不对、打印中间量或更新顺序。要把当前问题改回“为什么相邻选择互换不会变差/保持什么不变量”。 |
| `dialogue_v3_037_correctness_invariant` | 正确性不变量 | revise | context_mismatch | high | 近期对话在讲交换/不变量，但学生当前回复转成样例不对、打印中间量或更新顺序。要把当前问题改回“为什么相邻选择互换不会变差/保持什么不变量”。 |
| `dialogue_v3_038_correctness_invariant` | 正确性不变量 | revise | context_mismatch | high | 近期对话在讲交换/不变量，但学生当前回复转成样例不对、打印中间量或更新顺序。要把当前问题改回“为什么相邻选择互换不会变差/保持什么不变量”。 |
| `dialogue_v3_039_correctness_invariant` | 正确性不变量 | revise | context_mismatch | high | 近期对话在讲交换/不变量，但学生当前回复转成样例不对、打印中间量或更新顺序。要把当前问题改回“为什么相邻选择互换不会变差/保持什么不变量”。 |
| `dialogue_v3_040_correctness_invariant` | 正确性不变量 | revise | context_mismatch | high | 近期对话在讲交换/不变量，但学生当前回复转成样例不对、打印中间量或更新顺序。要把当前问题改回“为什么相邻选择互换不会变差/保持什么不变量”。 |
| `dialogue_v3_044_implementation_boundary` | 实现边界 | revise | bridge_label_issue | medium | 学生说的是“一个字符/空格怎么处理”，但 missing_bridge 和成功标准还停在泛泛边界初值。建议改成“输出图中单个字符位置如何对应题面格子”。 |
| `dialogue_v3_045_debugging_evidence` | 调试证据 | revise | bridge_label_issue | high | 学生现在卡的是维护量/不变量在题面里指什么，不是怎么构造反例。要么换成概念语义桶，要么把学生话术改成“该造哪个最小反例”。 |
| `dialogue_v3_046_debugging_evidence` | 调试证据 | revise | bridge_label_issue | high | 学生明说不懂“可行性/状态语义”，当前缺口是概念解释，不是调试证据。建议把 missing_bridge 改为状态/判定语义，或改学生问题。 |
| `dialogue_v3_047_debugging_evidence` | 调试证据 | revise | bridge_label_issue | high | 这条当前问题在问“这一格记录的含义”，更像状态表示，不是 WA/TLE 证据设计。建议换桶或把问题改成具体要检查哪个中间变量。 |
