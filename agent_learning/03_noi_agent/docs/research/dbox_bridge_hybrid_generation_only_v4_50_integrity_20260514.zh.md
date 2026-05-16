# DBox / Bridge Hybrid v4 50-case Generation-only Integrity 20260514

English version: `dbox_bridge_hybrid_generation_only_v4_50_integrity_20260514.md`

本报告记录 `bridgebench_cp_heldout_v4_50_draft.jsonl` 上的 50-case × 5-condition generation-only 运行。它只检查生成链路、完整性、上下文字段和自动风险诊断，不作为论文质量结论。

## 输入与输出

- 输入数据：`docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl`
- 最终 merged 输出目录：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged`
- 盲评表：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/coach_response_review_workbook_dev_ablation.zh.xlsx`
- key 文件：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/coach_response_review_workbook_dev_ablation.key.csv`
- 条件数：5
- case 数：50
- 预期回复：250
- 最终回复：250

盲评表已包含 `problem_statement`、`context_ai_reply`、`recent_dialogue` 和 `response_text`，可以让教练看到原题、上下文 AI 回复、近期对话和要评分的 AI 回复。

## Conditions

| condition | role |
| --- | --- |
| `enhanced_prompt_only_clean` | strong prompt-only baseline |
| `dbox_inspired_clean` | DBox-inspired no-Guard baseline |
| `dbox_inspired_guard` | DBox-inspired + Leakage Guard baseline |
| `bridge_contract_compact_guard` | 当前 Bridge Contract 主候选 |
| `bridge_guided_dbox_style_guard` | hybrid dev / appendix 候选 |

## 完整性结果

最终 merged integrity check：

- `expected_row_count=250`
- `combined_row_count=250`
- `final_response_row_count=250`
- `review_row_count=250`
- `missing_pairs=[]`
- `duplicate_pairs=[]`
- `empty_final_response_rows=[]`
- `stage_warning_rows=[]`
- `analysis_ready=true`

原始运行中 `bridge_guided_dbox_style_guard` 有 12 条空回复：5 条来自 `hint_level must be general_question` 的 schema 错误，7 条来自 `APIConnectionError`。定向补跑后 11 条恢复；`heldout_v4_luogu_029` 需要第二次定向补跑并增加 retry 后恢复。这说明 hybrid condition 的结构化输出稳定性弱于其他 4 个 condition，后续更适合放入 appendix 或 dev analysis，而不是主表核心结论。

## 自动诊断摘要

以下数字来自 runtime Guard / static lint，只能作为 dev 筛查，不等于教练盲评或论文结论。

| condition | p50 latency | p95 latency | avg LLM calls | runtime critical leakage | final static risk |
| --- | ---: | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 16.23s | 39.87s | 1.00 | N/A | 0.36 |
| `dbox_inspired_clean` | 11.99s | 43.31s | 1.04 | N/A | 0.26 |
| `dbox_inspired_guard` | 17.33s | 37.61s | 3.02 | 0.10 | 0.28 |
| `bridge_contract_compact_guard` | 15.31s | 25.59s | 3.02 | 0.06 | 0.26 |
| `bridge_guided_dbox_style_guard` | 22.28s | 73.53s | 3.26 | 0.10 | 0.30 |

整体自动诊断：

- runtime leakage rate：0.287
- runtime critical bridge leakage rate：0.087
- answer/code leakage rate：0.0
- final static risk rate：0.292
- total p50 latency：16.36s
- total p95 latency：43.43s

## 解释边界

- 这不是 human coach review，不能写成 headline result。
- No-Guard 条件没有 runtime leakage judge，因此它们的 runtime leakage 指标是 N/A；只能比较 static lint 与后续教练盲评。
- Guard 条件的 `rewrite` 目前记录为 intervention signal，但本轮没有 Repair condition，不能证明 Repair 效果。
- `bridge_contract_compact_guard` 在自动诊断上 critical leakage 低于 `dbox_inspired_guard`，但这仍需教练盲评确认，尤其要看是否存在过强 micro-example 或 definition-first 泄露。

## 下一步

1. 对这 250 条做 AI preliminary review，只用于 dev 筛查。
2. 输出一个未填写的教练盲评表，供人类教练抽样或全量复核。
3. 若需要正式比较 Guard / Repair，需要另补公平矩阵：`enhanced_prompt_only_guard`、`enhanced_prompt_only_guard_repair`、`dbox_inspired_guard_repair`、`bridge_contract_compact_clean`、`bridge_contract_compact_guard_repair`。
4. `bridge_guided_dbox_style_guard` 暂不建议进主表核心比较，除非教练盲评显示其质量明显反转。
