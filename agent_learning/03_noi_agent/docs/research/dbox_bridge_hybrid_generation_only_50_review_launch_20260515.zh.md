# DBox / Bridge Hybrid 50-case 评审启动清单

本轮是 development / regression 阶段的 50-case generation-only 评测，不是正式论文 headline result。它的目标是判断哪些条件值得进入后续冻结后的正式 held-out 实验，以及定位 Bridge Contract、DBox-inspired scaffold 和 Guard 的主要失败模式。

## 数据生成结果

- Clean run pack: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged`
- Manifest: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/manifest.json`
- Combined JSONL: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/combined_dev_ablation.jsonl`
- 中文 summary: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/combined_dev_ablation_summary.zh.md`
- 英文 summary: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/combined_dev_ablation_summary.md`
- 完整性检查: `docs/research/dbox_bridge_hybrid_generation_only_50_integrity_20260515.zh.md`

完整性状态：

- 50 cases × 5 conditions = 250 rows
- final response 非空: 250 / 250
- stage errors: 0
- `[LEVEL:...]` 内部标签残留: 0
- 已对 `heldout_v4_luogu_018 × bridge_guided_dbox_style_guard` 做 targeted rerun 并合并

## 本轮条件

1. `enhanced_prompt_only_clean`
2. `dbox_inspired_clean`
3. `dbox_inspired_guard`
4. `bridge_contract_compact_guard`
5. `bridge_guided_dbox_style_guard`

其中 `bridge_guided_dbox_style_guard` 是当前候选混合方向：保留 Bridge 的 missing-bridge / forbidden-content 控制信号，同时借鉴 DBox-style 当前子步骤脚手架。

## 给人类教练的盲评文件

请给教练使用：

- `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_dev_ablation.zh.xlsx`

不要给教练使用：

- `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_dev_ablation.key.csv`

key 文件包含真实 condition，用于后续分析，不应出现在盲评环节。

## AI 初筛文件

AI 初筛填写表：

- `docs/research/coach_response_review_workbook_dbox_bridge_hybrid_generation_only_50_20260515.ai_prelim.zh.xlsx`

AI 初筛标签：

- `docs/research/coach_response_review_labels_dbox_bridge_hybrid_generation_only_50_20260515.ai_prelim.csv`
- `docs/research/coach_response_review_labels_dbox_bridge_hybrid_generation_only_50_20260515.ai_prelim.jsonl`

AI 初筛分析报告：

- `docs/research/dbox_bridge_hybrid_generation_only_50_ai_prelim_analysis_20260515.zh.md`
- `docs/research/dbox_bridge_hybrid_generation_only_50_ai_prelim_analysis_20260515.md`

注意：AI 初筛是启发式 dev triage，不是 coach gold label，也不应直接作为论文结果。

## AI 初筛的主要信号

AI 初筛显示：

- `bridge_guided_dbox_style_guard` 的 student-ready pass 最高：41 / 50。
- `bridge_guided_dbox_style_guard` 的 overall / core6 / micro7 也暂时最高。
- `bridge_contract_compact_guard` 在启发式初筛中没有超过 `dbox_inspired_guard`。
- 所有条件仍有 minor / major / answer 风险提示，需要人工复核。
- Guard 的作用不能只看均值，需要检查它是否真的改进了具体高风险回复。

这些信号支持下一步重点看：

1. `bridge_guided_dbox_style_guard` 是否真的比纯 DBox 更贴合 missing bridge。
2. `bridge_contract_compact_guard` 是否过于“按 contract 生硬执行”，导致教学自然度弱。
3. DBox-style scaffold 是否因为更像真实教学对话而获得更高分。
4. 静态风险是否误报 worked example 和 filled trace。
5. Guard 的 rewrite 是否真的降低泄露，还是只是让回复变保守。

## 建议的人类评审顺序

建议教练不要从 250 行从头填到尾，而是分三步：

1. 先每个 case 看 5 条匿名回复，按同题排序填 `coach_preference_rank`。
2. 再标 `would_show_to_student`、`leakage_label`、`overall_quality_score`。
3. 最后只对边界样本补 `coach_notes`，重点解释为什么泄露、为什么空泛、为什么接不住上下文。

优先复核的样本：

- AI 初筛标记为 `major_bridge_leakage` 或 `answer_leakage` 的行。
- `show=no` 或 `show=borderline` 的行。
- 同一 case 内 5 个 condition 差距明显的行。
- `bridge_contract_compact_guard` 与 `bridge_guided_dbox_style_guard` 排名相反的 case。

## 下一步

1. 人类教练完成盲评表。
2. 用 key 文件合并分析人类盲评结果。
3. 重点比较：
   - `dbox_inspired_guard` vs `dbox_inspired_clean`
   - `bridge_contract_compact_guard` vs `dbox_inspired_guard`
   - `bridge_guided_dbox_style_guard` vs `dbox_inspired_guard`
   - `bridge_guided_dbox_style_guard` vs `bridge_contract_compact_guard`
4. 根据人类结果决定是否保留 `bridge_guided_dbox_style_guard` 进入正式 50-case held-out 主表。
