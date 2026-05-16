# Dialogue-State v3 10-case Dev 实验状态（2026-05-13）

本文档记录 dialogue-state v3 数据实验的当前状态。它是开发阶段记录，不是论文正式结论。

## 目的

本轮先暂停论文写作，验证新的 dialogue-state v3 数据能否进入现有离线消融链路，并生成可供教练盲评的回复表。

本轮重点检查：

- v3 follow-up case 是否能进入 `heldout_main` 条件集；
- 盲评表是否包含原题题面、近期对话、上下文 AI 回复、学生当前回复、目标 AI 回复；
- 8 个主实验 condition 是否都能产出可评分回复；
- 是否存在空回复、缺 condition、stage error；
- AI 预评能否作为 dev triage 的初筛信号。

## 数据与条件

输入数据：

`docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`

本轮 dev subset 包含 10 个 case，覆盖：

- initial question；
- F1 能跟上；
- F2 部分跟上；
- F3 错误跟随；
- F4 前置概念缺口；
- 代码尝试；
- 直接要答案/代码风险。

运行条件集：

`heldout_main`

包含 8 个 condition：

- `current_system_deployment`
- `enhanced_prompt_only_clean`
- `codehelp_codeaid_clean`
- `dbox_inspired_guard`
- `bridge_inspired_expert_decision_clean`
- `single_llm_structured_guard`
- `bridge_contract_guard`
- `bridge_contract_guard_repair`

## 修复的问题

本轮 smoke 发现两个数据链路问题，已修复并加入单测：

1. `context_ai_reply` 没有从中文近期对话中抽取出来。
   - 原因：runner 只识别 `assistant:` / `ai:`，没有识别中文 `AI：`。
   - 修复：`run_bridge_offline_eval.py` 支持 `AI：`、`助手：` 等中文前缀。
   - 生成脚本也显式写入 `context_ai_reply`。

2. combined JSONL 没有保留原题和 v3 follow-up 元数据。
   - 影响：盲评表里的原题链接、题面、学生跟随状态、上一轮 AI 脚手架等列可能为空。
   - 修复：runner 结果行保留题源字段和 dialogue-state v3 元数据。

相关测试：

```text
python3 -m unittest \
  test_dialogue_state_v3_generation_unit.py \
  test_dialogue_state_v3_validation_unit.py \
  test_bridge_offline_eval_runner_unit.py \
  test_coach_response_review_workbook_unit.py \
  test_coach_response_review_xlsx_unit.py
```

结果：64 tests OK。

## 输出位置

干净的 10-case dev run：

`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/`

关键文件：

- `manifest.json`
- `combined_dev_ablation.jsonl`
- `combined_dev_ablation_summary.zh.md`
- `combined_dev_ablation_summary.md`
- `coach_response_review_workbook_dev_ablation.zh.xlsx`
- `coach_response_review_workbook_dev_ablation.key.csv`
- `coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx`
- `dev10_ai_prelim_analysis.zh.md`
- `dev10_ai_prelim_analysis.md`
- `integrity_report.json`

## 完整性结果

最终合并后的 run pack：

```json
{
  "expected_row_count": 80,
  "combined_row_count": 80,
  "final_response_row_count": 80,
  "review_row_count": 80,
  "blocking_reasons": [],
  "warning_reasons": [],
  "analysis_ready": true,
  "headline_ready": true
}
```

这里的 `headline_ready=true` 只表示该 run pack 在工程完整性上没有缺行或空回复，不表示可以作为论文 headline 结果。

## AI 预评结果边界

AI 预评文件：

`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/dev10_ai_prelim_analysis.zh.md`

本轮 AI 预评只是 dev triage，用于快速筛查可疑回复和候选 condition，不是 coach gold label。

初步信号：

- 80 条回复均已自动预评；
- `single_llm_structured_guard` 在启发式预评中表现最好；
- `bridge_contract_guard_repair` 比 `bridge_contract_guard` 有轻微提升；
- `dbox_inspired_guard` 仍有边界泄露风险；
- major/answer 级风险样例需要人工回看，尤其要区分真正泄露、局部合理解释和 heuristic 误判。

不要据此写正式结论。正式结果仍需：

- 教练盲评；
- 50-case held-out；
- prompt / grader freeze；
- judge calibration；
- 部分双教练标注。

## 下一步

建议按以下顺序继续：

1. 抽查 10-case AI 预评中的 major/answer 风险样例，判断是否是 heuristic 误判。
2. 让教练填写或复核 `coach_response_review_workbook_dev_ablation.zh.xlsx`，至少先审 10 case。
3. 根据 10-case 教练反馈决定是否最后修 prompt；修完后冻结 prompt 和 rubric。
4. 再运行 50-case held-out 主实验。
5. 50-case 正式盲评前，不再继续扩 baseline 或新模块。
