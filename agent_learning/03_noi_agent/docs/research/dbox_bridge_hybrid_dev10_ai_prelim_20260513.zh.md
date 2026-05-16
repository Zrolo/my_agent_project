# DBox/Bridge 混合消融 10-case AI 初评报告（2026-05-13）

本报告记录 `dbox_bridge_hybrid` 10-case dev 消融。它用于开发阶段筛查，不作为正式论文 held-out 结论，也不是 coach gold label。

## 实验设置

- 数据：`docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl` 前 10 条。
- 生成模型：`deepseek_flash`，`chat_thinking_mode=disabled`。
- Judge：默认 `deepseek`，thinking disabled。
- 原始结果：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/combined_dev_ablation.jsonl`。
- 盲评表：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx`。
- 分析报告：`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_dev10_20260513_final/ai_prelim_analysis.zh.md`。

## 条件

| condition | 目的 |
| --- | --- |
| `enhanced_prompt_only_clean` | 强 prompt-only baseline，不用 Bridge Judge 或 Guard。 |
| `dbox_inspired_clean` | DBox-inspired 单轮 step-tree-style decomposition baseline，不加 Guard。 |
| `dbox_inspired_guard` | DBox-inspired baseline + Leakage Guard，检验 Guard 是否改善 decomposition baseline。 |
| `bridge_contract_compact_guard` | 当前 Bridge Contract compact + Guard。 |
| `bridge_guided_dbox_style_guard` | 新增混合方案：Bridge Contract 负责诊断/禁止内容，DBox-style 负责学生可见脚手架。 |

## AI 初评汇总

| condition | n | overall | core6 | sufficiency | micro7 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `enhanced_prompt_only_clean` | 10 | 3.8 | 1.95 | 2.0 | 1.7571 | 8 | 8 | 8/2/0 | 8/2/0 |
| `dbox_inspired_clean` | 10 | 3.4 | 1.8667 | 1.8 | 1.6714 | 6 | 6 | 6/2/2 | 6/2/2 |
| `dbox_inspired_guard` | 10 | 3.5 | 1.9 | 1.9 | 1.7285 | 6 | 6 | 6/3/1 | 6/3/1 |
| `bridge_contract_compact_guard` | 10 | 4.0 | 2.0 | 2.0 | 1.8428 | 10 | 10 | 10/0/0 | 10/0/0 |
| `bridge_guided_dbox_style_guard` | 10 | 3.9 | 1.9833 | 2.0 | 1.8285 | 9 | 9 | 9/1/0 | 9/1/0 |

## 延迟与稳定性

| condition | LLM calls/turn | P50 latency |
| --- | ---: | ---: |
| `enhanced_prompt_only_clean` | 1.0 | 7.45s |
| `dbox_inspired_clean` | 1.0 | 3.96s |
| `dbox_inspired_guard` | 3.4 | 14.99s |
| `bridge_contract_compact_guard` | 3.0 | 11.35s |
| `bridge_guided_dbox_style_guard` | 3.6 | 17.44s |

完整合并结果 50/50 都有最终回复。`bridge_guided_dbox_style_guard` 有 1 条 Leakage Judge timeout，但该条仍有最终回复，报告中应作为稳定性风险记录。

## 初步结论

1. `dbox_inspired_clean` 可以作为“不加 Guard 的 DBox-inspired baseline”，但在本轮 AI 初评里并不是最强 baseline：它有 2 条 major bridge leakage，student-ready pass 为 6/10。
2. `dbox_inspired_guard` 略优于 `dbox_inspired_clean`，但仍有 1 条 major bridge leakage；这说明 Guard 对 decomposition baseline 有帮助，但还不充分。
3. `bridge_contract_compact_guard` 在 AI 初评中最好：overall 4.0、safe_ready 10/10、major/answer leakage 0。这个结果支持继续保留 Bridge Contract compact + Guard 作为主实验候选。
4. 新增 `bridge_guided_dbox_style_guard` 接近 `bridge_contract_compact_guard`，但更慢，且出现 1 条 minor leakage 和 1 条 Leakage Judge timeout；它暂时更适合做 appendix/dev 候选，不建议直接替代主方案。
5. 这些结论只用于 dev 决策。正式判断仍需要教练盲评、50-case held-out、部分双教练标注和 Judge calibration。

## 对后续实验的影响

- DBox original-style no-Guard baseline 应保留为 `dbox_inspired_clean`，用于回答“DBox-style decomposition 本身是否已足够强”。
- 主实验里至少应保留 `dbox_inspired_guard`，因为它是更公平的 guarded decomposition baseline。
- `bridge_contract_compact_guard` 暂时是主方案候选。
- `bridge_guided_dbox_style_guard` 不应扩大为默认主线，除非后续人类盲评证明它稳定超过 compact Bridge Contract。
