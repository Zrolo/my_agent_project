# Prompt-Controlled Ablation 盲评分析 2026-05-11

本报告分析 3 个样本 × 5 个变体的盲评结果，用于回答：Bridge Contract 组质量提升，到底来自模块结构、具体诊断信息，还是来自更强的通用教学提示词？

> 本结果只作为 dev / pilot evidence，不作为最终 held-out test 结论。样本数只有 3 个，适合发现方向和设计下一轮实验，不适合做显著性声称。

## 系统汇总

| Variant | N | Overall | Core6 | Micro7 | Rank1 | Ready | No leak | Minor | Major |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single_llm_structured | 3 | 3.3333 | 1.6667 | 1.6667 | 0 | 2 | 2 | 1 | 0 |
| enhanced_prompt_only | 3 | 4.3333 | 2.0 | 2.0 | 1 | 3 | 3 | 0 | 0 |
| bridge_contract_predicted | 3 | 4.0 | 1.8333 | 1.7619 | 2 | 2 | 2 | 0 | 1 |
| bridge_contract_shuffled | 3 | 2.6667 | 1.5555 | 1.4286 | 0 | 1 | 0 | 1 | 2 |
| bridge_contract_oracle | 3 | 3.3333 | 1.6667 | 1.5714 | 0 | 1 | 1 | 1 | 1 |

## Effect 分解

| Effect | Comparison | Overall Δ | Core6 Δ | Micro7 Δ | W/T/L |
| --- | --- | --- | --- | --- | --- |
| prompt_effect | enhanced_prompt_only - single_llm_structured | 1.0 | 0.3333 | 0.3333 | 2/0/1 |
| predicted_contract_vs_prompt | bridge_contract_predicted - enhanced_prompt_only | -0.3333 | -0.1667 | -0.2381 | 2/0/1 |
| predicted_contract_vs_shuffled | bridge_contract_predicted - bridge_contract_shuffled | 1.3333 | 0.2778 | 0.3333 | 2/1/0 |
| oracle_contract_vs_predicted | bridge_contract_oracle - bridge_contract_predicted | -0.6667 | -0.1667 | -0.1905 | 1/0/2 |
| oracle_contract_vs_shuffled | bridge_contract_oracle - bridge_contract_shuffled | 0.6667 | 0.1111 | 0.1429 | 2/1/0 |

解释口径：

- **Prompt effect**：`enhanced_prompt_only - single_llm_structured` 的总体质量差为 `1.0`。如果它为正，说明仅加入更强教学提示词就能提升质量。
- **Predicted contract effect over prompt**：`bridge_contract_predicted - enhanced_prompt_only` 的总体质量差为 `-0.3333`。如果它为正，才说明预测 Bridge Contract 在通用强 prompt 之外有额外平均收益。
- **Contract validity effect**：`bridge_contract_predicted - bridge_contract_shuffled` 的总体质量差为 `1.3333`。如果它为正，说明具体 contract 内容不是纯装饰，错误 contract 会伤害质量。

## 逐 case 最好 / 最差

| Case | Best Variant | Best Quality | Best Leakage | Worst Variant | Worst Quality | Worst Leakage |
| --- | --- | --- | --- | --- | --- | --- |
| cp_bridge_001 | bridge_contract_predicted | 5.0 | no_leakage | bridge_contract_shuffled | 2.0 | major_bridge_leakage |
| cp_bridge_002 | bridge_contract_predicted | 5.0 | no_leakage | single_llm_structured | 1.0 | no_leakage |
| cp_bridge_003 | enhanced_prompt_only | 5.0 | no_leakage | bridge_contract_shuffled | 2.0 | major_bridge_leakage |

## 当前结论

1. **prompt wording 很可能解释了相当一部分质量提升。** 在这 3 个样本里，`enhanced_prompt_only` 的平均总体质量最高，并且没有 major leakage。这说明不能把 Bridge Contract 组在 fair 20-case 中的提升全部归因于模块架构。
2. **具体 contract 仍然可能有价值。** `bridge_contract_predicted` 在 2/3 个 case 中拿到第一，并且明显好于 `bridge_contract_shuffled`。这说明模型不是只被“请用微型例子、不要泄露”这种通用提示影响；错误 contract 会把回复带偏。
3. **oracle contract 没有自动成为上界。** `bridge_contract_oracle` 在这个小样本中没有超过 predicted contract，说明 contract 注入方式、微型例子设计和泄露控制同样重要；“金标 contract”如果被主模型展开得太完整，也可能变成泄露。
4. **这轮实验支持下一步扩到 10–20 case。** 现在最重要的不是立刻声称架构有效，而是把 prompt-only、predicted contract、shuffled contract、oracle contract 在更多样本上做配对盲评。

## 对论文写法的影响

论文里应避免写“Bridge Contract 架构本身导致质量提升”。更稳的表述是：

> Bridge Contract variants 的收益可能混合了通用教学 prompt、具体 missing bridge 诊断信息、以及模块化控制信号。本消融用于将这些因素拆开。初步 3-case 结果显示，强 prompt 本身已经很强；但 shuffled contract 表现较差，说明具体 contract 内容仍可能带来额外价值。

下一步正式报告应继续使用三类 effect：

- prompt effect: `enhanced_prompt_only - single_llm_structured`
- predicted diagnosis effect: `bridge_contract_predicted - enhanced_prompt_only`
- contract validity effect: `bridge_contract_predicted - bridge_contract_shuffled`
