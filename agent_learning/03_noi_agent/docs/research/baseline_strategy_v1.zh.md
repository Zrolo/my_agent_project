# Baseline Strategy v1

本文档回答一个核心科研风险：

```text
如果只把 current_system 当 baseline，论文会不会站不住？
```

结论：

```text
current_system 只能作为 deployment baseline，不能作为唯一科研 baseline。
Research v1 必须加入强 prompt-only、DBox-inspired、CodeHelp/CodeAid-style、Bridge-inspired 等 literature-adapted baselines。
```

## 为什么 current_system 不够

`current_system` 有价值，因为它代表当前线上 AIChat 的真实部署状态。但它不能单独证明 Bridge Contract / Guard / Repair 的科研优势。

如果论文只比较：

```text
current_system
vs
bridge_contract_predicted + guard + repair
```

审稿人很可能质疑：

```text
你们只是赢了一个弱的自家旧系统。
换成强 Socratic prompt、DBox-style decomposition prompt 或 no-direct-solution guardrail 后，结果还成立吗？
```

因此主实验必须避免 weak-baseline bias。

## Baseline Set

最低主实验建议包含：

| Baseline | 类型 | 作用 |
|---|---|---|
| `current_system` | deployment baseline | 固定当前线上系统状态和失败模式 |
| `enhanced_prompt_only` | strong prompt-only baseline | 排除“只是 prompt wording 更强”的解释 |
| `codehelp_codeaid_no_direct_solution_tutor` | programming guardrail baseline | 检验普通 no-direct-solution 是否已足够 |
| `dbox_inspired_decomposition_tutor` | DBox-inspired baseline | 检验分解式脚手架是否已足够强 |
| `dbox_inspired_decomposition_tutor + guard` | guard-instrumented decomposition baseline | 公平测试 Guard 信号是否跨 generator 可用；guard-only 不代表最终回复已被改写 |
| `bridge_inspired_expert_decision_tutor` | Bridge-inspired baseline | 检验通用专家决策 prompt 是否接近 Bridge Contract |
| `bridge_contract_predicted` | ours | 检验 predicted missing-bridge contract |
| `bridge_contract_predicted + guard` | ours + safety instrumentation | 检验 critical bridge leakage guard 信号；除 block fallback 外不解释为输出修复 |
| `bridge_contract_predicted + guard + repair` | ours + safety | 检验 repair 的质量-泄露权衡 |

如果主表太大，可以主文放 7 个系统，将完整消融放 appendix。

## Literature-adapted 不等于 reproduction

当前 Research v1 不声称复现 DBox、CodeHelp、CodeAid、Bridge、MathDial 或 MRBench。原因是这些工作与我们的任务在语言、数据、交互形式和实验协议上不完全一致。

论文中应写：

```text
We implement literature-adapted baselines, not direct reproductions.
```

## 每个 baseline 检验什么

| Claim | Required comparison | 如果结果不支持 |
|---|---|---|
| current system 有真实失败模式 | `current_system` human review | 只能说明当前产品弱，不作为主贡献 |
| prompt wording 本身很重要 | `enhanced_prompt_only` vs `single_llm_structured` | prompt effect 较小 |
| decomposition scaffold 是强 baseline | `dbox_inspired_decomposition_tutor` vs `enhanced_prompt_only` | DBox-inspired 可能不是默认强策略 |
| Guard 信号跨 generator 可用 | `dbox + guard` vs `dbox`；`bridge + guard` vs `bridge`；same-candidate guard/repair stress | Guard-only 结论只能限定为检测/干预信号；最终输出修复需要 repair/block 证据 |
| contract 内容真的重要 | `bridge_contract_predicted` vs `bridge_contract_shuffled` | Bridge Contract 可能只是 prompt wrapper |
| critical bridge leakage 有必要 | answer/code leakage 低，但 minor/major bridge leakage 高 | 如果没有 bridge leakage，核心指标会被削弱 |
| repair 有用 | repair stress before/after | 如果质量下降，报告 trade-off 而非单向胜利 |

## 如果强 baseline 赢了怎么办

这不一定推翻论文。

如果 `dbox_inspired_decomposition_tutor + guard` 或 `enhanced_prompt_only` 最强，论文结论可以改为：

```text
强 prompt 或 decomposition scaffold 是更好的默认生成路径；
missing bridge schema 和 critical bridge leakage 仍然作为 evaluation / guard / routing 信号有价值。
```

因此论文不要押：

```text
Bridge Contract 一定是最强系统。
```

论文应押：

```text
CP-MissingBridgeBench 能公平揭示不同 tutor harness 的质量、泄露和成本权衡。
```

## 与现有文档关系

详细 baseline 定义见：

- [baseline_protocol_v1.zh.md](baseline_protocol_v1.zh.md)
- [baseline_protocol_v1.md](baseline_protocol_v1.md)

DBox-inspired 边界见：

- [dbox_reproduction_gap_v1.zh.md](dbox_reproduction_gap_v1.zh.md)
- [dbox_official_materials_review_v1.zh.md](dbox_official_materials_review_v1.zh.md)
