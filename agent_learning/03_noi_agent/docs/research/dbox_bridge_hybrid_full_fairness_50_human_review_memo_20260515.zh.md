# DBox / Bridge Hybrid Full Fairness 50-case 人工盲评备忘

日期：2026-05-15

本备忘基于人工教练填写的本地文件：

`/Users/kongyouli/Downloads/coach_response_review_workbook_dev_ablation_zh7_human_coach_reviewed.xlsx`

对应隐藏 key：

`evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_full_fairness_50_20260514/coach_response_review_workbook_dev_ablation.key.csv`

完整机器分析见：

- `docs/research/dbox_bridge_hybrid_full_fairness_50_human_review_analysis_20260515.zh.md`
- `docs/research/dbox_bridge_hybrid_full_fairness_50_human_review_analysis_20260515.md`

## 数据状态

- 50 个 dev cases。
- 10 个匿名 condition。
- 500 条人工盲评回复。
- 已填写 500 条总体质量、泄露标签、是否愿意给学生看等核心字段。
- `coach_bridge_oriented_micro_example_score` 有 6 条缺失，影响 `micro7` 均值的精确性，但不影响总体质量、core6、泄露和 student-ready 主结论。

本批仍是 dev/regression evidence，不是正式 held-out headline result。

## 最重要的结果

### 1. DBox-inspired clean 是当前最高质量强 baseline

`dbox_inspired_clean`：

- overall：3.76，最高。
- core6：1.7067，最高。
- ready：29/50。
- major/answer leakage：1/50。

解释：DBox-style decomposition 的确是强 baseline，不是弱对照。论文里必须承认它的强度。

### 2. Bridge Contract compact clean 的 student-ready 数最高

`bridge_contract_compact_clean`：

- overall：3.62。
- core6：1.6867。
- ready：31/50，最高。
- major/answer leakage：1/50。
- rank1：10。

解释：Bridge Contract 并没有“失败”。它在学生可展示性上很强，但仍有硬泄露样本，不能写成天然更安全。

### 3. Bridge-guided DBox-style guard 是最稳的安全候选

`bridge_guided_dbox_style_guard`：

- overall：3.68。
- ready：23/50。
- show no：0/50。
- major/answer leakage：0/50。
- no/minor/major+answer：46/4/0。

解释：这个 hybrid 不是最高质量，但它避免了硬失败，更像“安全上线候选”或“主实验保守方法”。它值得保留到下一轮正式比较。

### 4. Guard 不应被包装成稳定质量提升模块

配对结果显示：

- `dbox_inspired_guard - dbox_inspired_clean`：overall -0.08。
- `bridge_contract_compact_guard - bridge_contract_compact_clean`：overall -0.08。
- `enhanced_prompt_only_guard - enhanced_prompt_only_clean`：overall +0.08。

解释：Guard 对质量没有稳定正向效果。它的主要价值应限定为风险控制、拦截和部署安全，而不是“提升教学质量”。

### 5. Repair 当前仍是高风险模块

尤其是：

- `enhanced_prompt_only_guard_repair - enhanced_prompt_only_guard`：overall -0.56，W/T/L = 7/18/25。
- `bridge_contract_compact_guard_repair` 的 sufficiency 最高，但 overall 没有明显提升。

解释：Repair 有时减少泄露，但会牺牲自然度、针对性或学生可展示性。下一步不能把 Repair 放进默认主方法，除非做 same-candidate before/after stress test。

## 对论文方向的影响

这份人工盲评不说明“我们的框架垃圾”，也不说明“Bridge Contract 必赢”。它说明更严谨的论文主张应该是：

> CP-MissingBridgeBench 能揭示 strong decomposition baseline、Bridge Contract、Guard、Repair 在教学质量、关键桥泄露和学生可展示性之间的 trade-off。

当前最稳的论文写法不是：

> Bridge Contract beats DBox-inspired baseline.

而是：

> DBox-inspired decomposition is a strong baseline. Bridge Contract compact and bridge-guided DBox-style variants provide different safety/quality trade-offs, especially around critical bridge leakage.

## 建议进入下一轮的 condition

建议主表保留：

1. `enhanced_prompt_only_clean`：强 prompt baseline。
2. `dbox_inspired_clean`：当前最高质量 decomposition baseline。
3. `dbox_inspired_guard`：公平检验 Guard 是否对 DBox 也有帮助。
4. `bridge_contract_compact_clean`：Bridge Contract compact 的纯生成效果。
5. `bridge_guided_dbox_style_guard`：当前最安全的 hybrid 候选。

建议放入 appendix 或 stress test：

1. `bridge_contract_compact_guard_repair`：用于分析 Repair 是否提高 sufficiency，但不宜默认主方法。
2. `dbox_inspired_guard_repair`：用于公平比较 Repair 是否跨 generator 有效。
3. `enhanced_prompt_only_guard_repair`：保留为反例，说明 Repair 可能显著损害质量。

## 需要修正或补做

1. 补齐 6 条缺失的 `bridge_oriented_micro_example_score`，或在报告中明确 micro7 对缺失值做了跳过。
2. 对 15 条 major/answer leakage 做人工 case memo，区分：
   - 过完整 micro-example；
   - 直接补完关键桥；
   - 局部代码/实现槽位泄露；
   - Repair 改写后反而泄露。
3. 暂停大改 tutor prompt。先修评测报告、case memo 和 condition selection。
4. Repair 只进入 same-candidate before/after stress test，不进入默认主方法。
5. 下一轮正式 held-out 前冻结 prompt 和 grader。

## 结论

这批结果对论文不是坏事。它把论文从“证明一个自家框架赢”推向更稳的方向：

> 用 CP-MissingBridgeBench 严格评估强 baseline 与多种 tutoring harness 的质量、安全和可展示性权衡。

DBox-inspired 强，反而能增强论文说服力；因为你们不是只赢弱 baseline，而是在强 baseline 面前讨论 missing bridge 和 critical bridge leakage 的真实价值。
