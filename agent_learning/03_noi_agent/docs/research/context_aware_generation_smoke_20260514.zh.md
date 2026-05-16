# 上下文感知生成 Smoke 报告 20260514

English version: `context_aware_generation_smoke_20260514.md`

## 目的

这份报告记录了离线生成流程修复后的两轮 development smoke。修复目标是让离线 runner 更接近线上 AIChat：先放入近期对话，再追加当前学生问题和题目上下文。这里的结果不作为论文结论，只用于确认数据链路是否修好，以及在跑 50-case 大实验前暴露剩余风险。

## 本轮运行

| 运行 | 输入 | 条件集 | 行数 | 主要验证点 | 完整性 |
| --- | --- | --- | ---: | --- | --- |
| `context_aware_smoke10_20260514` | `bridgebench_cp_heldout_v3_50_draft.jsonl` 前 10 条 | `dbox_bridge_hybrid` | 50 | 无近期对话 case | 通过 |
| `context_aware_followup_smoke5_20260514` | 选取的 follow-up case | `dbox_bridge_hybrid` | 25 | 有近期对话并解析进 messages | 通过 |

条件：`enhanced_prompt_only_clean`, `dbox_inspired_clean`, `dbox_inspired_guard`, `bridge_contract_compact_guard`, `bridge_guided_dbox_style_guard`。

相关产物：

- `evals/aichat/ad_hoc_runs/context_aware_smoke10_20260514/`
- `evals/aichat/ad_hoc_runs/context_aware_followup_smoke5_20260514/`
- `docs/research/context_aware_smoke10_integrity_20260514.json`
- `docs/research/context_aware_followup_smoke5_integrity_20260514.json`

## 已通过的部分

- v3 held-out 数据已经不再出现 `recent_dialogue` 最后一轮学生话和 `student_message` 错配的问题。
- 离线 runner 在存在 `recent_dialogue` 时，会先把近期对话解析成 user/assistant messages，再追加当前学生问题。
- follow-up smoke 的 25 行全部记录为 `generation_context_source=parsed_recent_dialogue`。
- follow-up smoke 中，多数行使用 3 条 message 生成，长上下文 case 使用 5 条 message 生成，说明近期对话确实进入了生成上下文。
- 没有空回复。
- 没有缺失或重复的 case/condition 组合。
- 学生可见回复中没有残留 `[LEVEL:Lx]` 这类内部标签。
- 盲评 CSV/XLSX 已新增 `context_alignment_flag`，后续分析可以先区分 `no_recent_dialogue`、`aligned_prior_context_ends_with_assistant` 和错配样本，再解释教练评分。

## 暴露的问题

上下文链路已经修好，但回复质量和关键桥泄露风险还没有完全解决。follow-up smoke 中，多数回复能接住当前学生问题和前一轮 AI 问法，但在“贡献汇总 / 差分 / 标记”类高风险 case 上仍然有过度提示现象。特别是 P3948 风格的路径/区间标记 case，部分回复仍然把“区间贡献转成端点差分标记”的关系说得过完整。

这说明：之前盲评分数差，确实有一部分来自上下文错配；但不是全部来自上下文错配。即使上下文正确，prompt / guard 对 fully-worked micro-example、answer-slot、filled-trace 这类泄露的控制仍需要继续校准。

## 当前解释

这轮 smoke 只能算 development check，不能作为正式论文结果。它说明我们可以从“数据完整性修复”进入“小规模上下文感知输出复查”，但还不应该直接把结果当成 50-case headline test。

建议的下一道门槛：

1. 先查看 5 条 follow-up case 的 review workbook。
2. 判断“贡献汇总 / 差分 / 标记”类过度提示是否在当前 dev prompt 下可以接受。
3. 如果不可接受，应在 dev set 上修 prompt / guard，然后重跑同一组 smoke。
4. 如果可接受，再用同一套 context-aware runner 跑 50-case generation-only。
