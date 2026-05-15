# Dialogue-State v3 50-Case Refresh 20260515

English version: `dialogue_state_v3_50_refresh_20260515.md`

## 结论

本轮刷新后，`bridgebench_cp_dialogue_state_v3_50_draft.jsonl` 更适合作为下一步 follow-up scaffolding 主实验候选集。它仍是 `draft_needs_coach_review`，不是 gold，也不能直接作为论文 headline result。

相比此前的 v4 generation-only 草稿，本版本的重点不是只修短问无上下文，而是把 50 条 case 明确拆成初始提问和后续辅导轮：

- 初始提问：10 条；
- 后续辅导轮：40 条；
- F1 能跟上：7 条；
- F2 部分/勉强跟上：18 条；
- F3 较难跟上：10 条；
- F4 前置概念断层：5 条。

## 本轮修正

此前 `dialogue_state_v3` 虽然有 F1-F4 和 follow-up 类型，但当前学生回复实际过短，且部分 `recent_dialogue_bucket` 是字段标记而不是内容真实满足。本轮修正了两个问题：

1. 当前学生回复按真实文本重新满足长度分布：`short=20`、`medium_short=15`、`medium_long=10`、`long=5`。
2. 标记为 long context 的样本现在真的包含多轮近期对话，而不是只写一个字段。
3. 中英文 case/source 复核表新增结构化审核列，用于统计 `accept / revise / drop / discuss`，避免只留下不可汇总的自由备注。

新增结构化审核列包括：

- `source_ok`
- `context_coherent`
- `student_message_realistic`
- `followability_ok`
- `missing_bridge_ok`
- `forbidden_content_ok`
- `success_criteria_ok`
- `leakage_boundary_ok`
- `case_decision`
- `issue_type`
- `coach_fix_suggestion`
- `reviewer_confidence`

## 校验结果

生成文件：

- 数据集：`bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- 中文教练复核表：`dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- 英文教练复核表：`dialogue_state_v3_50_source_and_case_review.en.xlsx`
- dialogue-state 校验：`dialogue_state_v3_validation_report_20260515.json`
- held-out 风格校验：`dialogue_state_v3_heldout_style_validation_report_20260515.json`
- 上下文审计：`dialogue_state_v3_50_context_readiness_audit_20260515.zh.md`

通过的门禁：

- `row_count=50`
- `problem_source_platform_counts={"luogu": 50}`
- 桥梁类别配额满足原计划
- 当前学生问题长度分布为 `20/15/10/5`
- 近期对话分布为 `none=10`、`short=25`、`long=15`
- 学生代码片段数量为 17，满足至少 10 条代码/错误代码场景
- `turn_position_counts={"initial": 10, "followup": 40}`
- `reference_label_status=draft_needs_coach_review`

## 与 heldout v4 的关系

`bridgebench_cp_heldout_v4_50_draft.jsonl` 保留为历史草稿。它适合说明“短问无上下文”的修复过程，但只有 10 条显式 follow-up metadata；如果下一步目标是测试 AIChat 能否承接学生对上一轮脚手架的回答，优先使用 `dialogue_state_v3`。

## 下一步

1. 先让教练或研究者复核 `dialogue_state_v3_50_source_and_case_review.zh.xlsx`；如需外部英文审查，使用 `dialogue_state_v3_50_source_and_case_review.en.xlsx`。重点看题面、学生当前回复、近期对话、F1-F4 标签、missing bridge、forbidden content 是否一致，并填写结构化审核列。
2. 复核通过后，导出正式 generation-only 输入。
3. 再跑固定 condition 矩阵，不再混用旧 v4 表。
4. 生成 AI 回复后导出 response review workbook，盲评表必须显示原题题面、近期对话、上下文 AI 回复、当前学生回复、目标 AI 回复、case-specific rubric。
5. 当前所有结果只作为 dev / data-preparation evidence，不作为论文正式结论。
