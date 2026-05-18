# Dev Ablation 10-case 盲评分析

## 数据概况

- 盲评行数：110
- case 数：10
- 系统条件数：11
- 所有行 `review_status=labeled`。
- 这是 dev ablation 结果，用于选择主实验系统和修 prompt，不应作为最终 held-out 结论。

## 系统汇总

| 系统 | n | 总体质量均值 | core 可用均值 | 微例均值 | student-ready | safe-pass | 愿意给学生看 | 重大/答案泄露 | 轻微泄露 | 无泄露 | rank1 | 平均rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only | 10 | 3.4 | 1.533 | 0.889 | 4 | 1 | 4 | 4 | 5 | 1 | 1 | 6.4 |
| socratic_no_answer | 10 | 2.7 | 1.367 | 0.333 | 0 | 0 | 6 | 0 | 0 | 10 | 0 | 8.6 |
| codehelp_codeaid | 10 | 3.3 | 1.55 | 1.0 | 4 | 0 | 8 | 0 | 6 | 4 | 0 | 6.3 |
| dbox_inspired | 10 | 3.4 | 1.567 | 0.5 | 5 | 0 | 6 | 3 | 5 | 2 | 0 | 7.5 |
| dbox_inspired+guard | 10 | 3.7 | 1.567 | 1.25 | 6 | 0 | 7 | 0 | 7 | 3 | 0 | 5.9 |
| bridge_inspired | 10 | 3.7 | 1.65 | 1.0 | 6 | 2 | 9 | 0 | 4 | 6 | 0 | 5.7 |
| single_llm | 10 | 3.6 | 1.667 | 1.333 | 6 | 1 | 9 | 0 | 5 | 5 | 0 | 5.6 |
| single_llm+guard | 10 | 3.4 | 1.533 | 0.8 | 5 | 1 | 6 | 2 | 4 | 4 | 1 | 6.1 |
| bridge_contract | 10 | 4.3 | 1.683 | 1.6 | 6 | 0 | 6 | 3 | 7 | 0 | 4 | 3.7 |
| bridge_contract+guard | 10 | 4.0 | 1.667 | 1.444 | 7 | 1 | 7 | 2 | 7 | 1 | 2 | 4.8 |
| bridge_contract+guard+repair | 10 | 3.5 | 1.533 | 1.667 | 6 | 3 | 7 | 1 | 3 | 6 | 2 | 5.4 |

## 关键配对比较（总体质量 A-B）

| 比较 | 配对case | 均值差 | 胜/平/负 |
| --- | --- | --- | --- |
| bridge_contract+guard+repair - dbox_inspired+guard | 10 | -0.2 | 3/5/2 |
| bridge_contract+guard - dbox_inspired+guard | 10 | 0.3 | 6/1/3 |
| bridge_contract - dbox_inspired | 10 | 0.9 | 7/2/1 |
| bridge_contract+guard+repair - enhanced_prompt_only | 10 | 0.1 | 5/1/4 |
| dbox_inspired+guard - enhanced_prompt_only | 10 | 0.3 | 5/2/3 |
| bridge_contract+guard+repair - single_llm+guard | 10 | 0.1 | 5/1/4 |

## 主要观察

- `bridge_contract` 的总体质量最高（4.3），且 rank1 最多（4/10），但 10 条全部存在 minor 或 major bridge leakage，说明它会把教学组织做得好，同时提示偏强。
- `bridge_contract+guard+repair` 的无泄露数量最高之一（6/10），safe-pass 最高（3/10），但总体质量降到 3.5。这个条件的最终回复更安全，但不能把收益直接归因于 guard-only；Repair/Guard 链路可能带来安全收益，也可能牺牲自然度或有效性，需 same-candidate before/after 验证。
- `dbox_inspired+guard` 是强 baseline：无重大/答案泄露，student-ready 6/10，总体质量 3.7。它应该进入 50-case 主实验。
- `socratic_no_answer` 最安全（10/10 no_leakage），但 student-ready 为 0，说明过度克制会变成无效教学。
- `enhanced_prompt_only` 并不稳定：总体质量 3.4，但重大/答案泄露 4/10，说明强 prompt 不能替代 bridge leakage 评测。
- `single_llm+guard` 在这批样本中没有稳定优于 `single_llm`，这提示 guard 的效果需要 same-candidate before/after 或更大样本验证。

## 需要谨慎解读

- 部分维度没有全量填写：`scaffold_appropriateness` 为 92/110，`bridge_leakage_control` 为 96/110，`bridge_oriented_micro_example` 为 48/110；均值应按可用分数解释。
- 只有 10 个 case，系统差异不能写成正式显著结论。
- 本批样本已经用于 dev 和 prompt 诊断，不能当最终 test set。

## 下一步建议

1. 保留主实验候选：`enhanced_prompt_only`、`dbox_inspired+guard`、`bridge_inspired`、`single_llm+guard`、`bridge_contract+guard`、`bridge_contract+guard+repair`。
2. 对 `bridge_contract` 系列修 prompt：质量高但泄露偏强，重点约束“完整微型例子把桥讲穿”。
3. 对 Repair 做质量保护：禁止错误小例子、空泛追问、填空栏位不完整。
4. 冻结 dev prompt 后进入 50-case held-out，不要继续新增系统条件。
