# v4 Generation-only AI Preliminary Review 20260514

English version: `v4_generation_only_ai_prelim_review_20260514.md`

本报告汇总 `dbox_bridge_hybrid_generation_only_v4_50_20260514_merged` 的开发阶段 AI 预评。它用于筛查风险、安排教练复核优先级，不是 coach gold，不替代人类教练盲评，也不能作为论文 headline result。

## 输入

- 运行目录：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged`
- 原始回复：`combined_dev_ablation.jsonl`
- 未填写盲评表：`coach_response_review_workbook_dev_ablation.zh.xlsx`
- AI 预评表：`coach_response_review_workbook_dev_ablation.ai_prelim_gpt55_xhigh.zh.xlsx`
- AI 标签：`ai_prelim_gpt55_xhigh_labels.jsonl`
- AI 预评分析：`ai_prelim_gpt55_xhigh_analysis.zh.md`

## 完整性

- AI labels：250 行
- AI-filled CSV：250 行
- unique `(case_id, condition_id)`：250
- 覆盖：50 cases × 5 conditions

## AI 预评主要结果

| condition | overall | core6 | ready | safe_ready | leak no/minor/major+answer | show yes/border/no | burden low/medium/high |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `enhanced_prompt_only_clean` | 3.04 | 1.63 | 12 | 10 | 25/14/11 | 12/27/11 | 0/34/16 |
| `dbox_inspired_clean` | 3.44 | 1.81 | 27 | 25 | 30/15/5 | 27/18/5 | 14/35/1 |
| `dbox_inspired_guard` | 3.38 | 1.79 | 25 | 22 | 28/16/6 | 25/19/6 | 22/27/1 |
| `bridge_contract_compact_guard` | 3.56 | 1.8467 | 29 | 28 | 39/11/0 | 29/20/1 | 8/35/7 |
| `bridge_guided_dbox_style_guard` | 3.62 | 1.8833 | 34 | 33 | 41/6/3 | 34/12/4 | 8/40/2 |

AI 预评观察：

- `bridge_contract_compact_guard` 在 AI 预评中没有 major / answer leakage，但 medium/high burden 较多，需要教练判断是否“安全但偏重”。
- `bridge_guided_dbox_style_guard` 的 ready 数最高，但仍有 3 条 major 风险，并且 generation-only 阶段出现过结构化输出不稳定，需要谨慎降级为 dev / appendix 候选。
- `enhanced_prompt_only_clean` 在 AI 预评中 major 风险和 high burden 都偏高，主要风险是完整微例、完整证明或直接补边界更新。
- 这些数字只能作为 dev triage；正式判断必须看人类教练盲评。

## 高风险人工复核包

根据 AI 预评，筛选规则为：

```text
case selected if any response has AI-prelim major/answer/code leakage or would_show_to_student=no
```

输出：

- 高风险盲评表：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/coach_response_review_workbook_v4_high_risk_case_pack_blind.zh.xlsx`
- 高风险 key：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/coach_response_review_workbook_v4_high_risk_case_pack_blind.key.csv`
- 高风险 summary：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_v4_50_20260514_merged/v4_high_risk_case_pack_summary.json`

高风险包规模：

- selected case count：19
- selected row count：95
- risk response count：27

教练复核时建议优先看：

1. AI 预评标为 major / no-show 的样本，判断是否真的是关键桥泄露。
2. `bridge_contract_compact_guard` 的 medium/high burden 样本，判断是否安全但过重。
3. `bridge_guided_dbox_style_guard` 的 high-ready 但 major-risk 样本，判断是否值得保留为 appendix。
4. `heldout_v4_luogu_046 / bridge_contract_compact_guard` 这类事实错误样本，作为 prompt / regression 负例。

## 下一步

本轮已经完成 generation-only + AI prelim review。下一步应让人类教练先审高风险包，而不是直接全量 250 行开评。高风险包复核后，再决定是否：

- 继续全量 250 行教练盲评；
- 删除或降级 `bridge_guided_dbox_style_guard`；
- 增补公平 Guard / Repair 矩阵；
- 修改 prompt 并重新进入 dev，而不是进入正式 held-out。
