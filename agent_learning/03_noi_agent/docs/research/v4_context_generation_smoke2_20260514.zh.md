# v4 Context Generation Smoke2 20260514

English version: `v4_context_generation_smoke2_20260514.md`

本报告记录 `bridgebench_cp_heldout_v4_50_draft.jsonl` 的 2-case × 5-condition generation-only smoke。它只用于检查 v4 上下文链路和回复完整性，不作为论文结论。

## 配置

- 输入：`docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl`
- 输出目录：`evals/aichat/ad_hoc_runs/v4_context_generation_smoke2_20260514`
- 条件集：`dbox_bridge_hybrid`
- case 数：2
- condition 数：5
- 预期行数：10
- 实际行数：10
- 空回复：0
- 完整性：通过

## 主要观察

- `generation_context_source=parsed_recent_dialogue`，`generation_message_count=3`，说明 runner 确实把 synthetic follow-up 的近期对话解析成历史消息，再把当前学生问题作为最后一轮 user message。
- v4 的上下文错配问题在 smoke 层面已基本修复：模型现在能看到上一轮 AI probe 和当前学生短回复，而不是只靠题面猜。
- 但质量风险仍然存在：部分 condition 仍出现 definition-first / answer-slot 式回复，例如直接引导学生定义 `dp[i][j]` 或追问表格格子的完整语义。这说明上下文对齐修复不能替代 leakage / scaffold rubric。

## 结论

v4 可以继续作为 generation-only 主 scaffold dev run 的候选输入，但正式发车前仍需保留“状态/表示语义是否被直接说穿”的检查。当前 smoke 不证明任何 condition 优劣，只说明数据链路比 v3 更适合评测后续辅导轮。
