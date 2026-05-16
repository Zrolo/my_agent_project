# Held-out v2 上下文一致性审计（2026-05-14）

## 结论

旧版 `bridgebench_cp_heldout_v2_50_draft.jsonl` 及其派生盲评表不能作为严格的“完整上下文一致”盲审结论使用。它们最多可作为按“学生当前问题 + AI 回复”进行的开发阶段粗评。

## 审计结果

- v2 数据集：`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- v2 case 数：`50`
- v2 context alignment：`{'no_recent_dialogue': 10, 'recent_dialogue_last_student_mismatch': 40}`
- 人类盲评表：`/Users/kongyouli/Downloads/coach_response_review_workbook_dev_ablation_zh5_filled.xlsx`
- 盲评表行数：`537`
- 盲评表 context alignment：`{'no_recent_dialogue': 136, 'unparseable_recent_dialogue': 1, 'recent_dialogue_last_student_mismatch': 400}`
- 学生可见回复残留 `[LEVEL:Lx]` 行数：`48`

## 根因

旧生成器在 `recent_dialogue` 末尾额外生成了一句“当前学生问题”，同时 `student_message` 又独立生成另一句学生问题。结果是：AI 回复通常在回答 `student_message`，但评审者如果按 `recent_dialogue` 最后一轮来理解，就会觉得上下文接不上。

## 修复

1. `recent_dialogue` 现在只表示当前问题之前的上下文；非 N/A 情况下默认结束在 AI 的追问或提示，不再额外塞入另一个学生当前问题。
2. held-out 校验器新增 `recent_dialogue_last_student_mismatch` 检查；后续出现这类错配会直接校验失败。
3. offline runner 会剥离学生可见回复里的 `[LEVEL:L0-L4]` 内部标签，避免盲评和真实体验被内部控制标记污染。
4. 已生成 clean v3 数据集：`/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/research/bridgebench_cp_heldout_v3_50_draft.jsonl`，校验结果为 `ok=true`，alignment 统计：`{'no_recent_dialogue': 10, 'aligned_prior_context_ends_with_assistant': 40}`。

## 使用建议

- 旧 zh5 人类盲审结果：只保留为 development diagnostic，不进入正式论文 headline result。
- 后续 50-case generation-only 和盲评：使用 v3 clean dataset 重新跑。
- 如果需要复用旧评分，只能在报告中明确写成 `current-message-only rough review`，不能称为完整上下文盲评。
