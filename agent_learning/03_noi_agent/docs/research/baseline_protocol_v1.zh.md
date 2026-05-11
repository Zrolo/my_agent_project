# Baseline Protocol v1

本文档定义 Research v1 的 baseline 体系，避免论文只和自家 `current_system` 比较造成 weak-baseline bias。

## 核心判断

`current_system` 仍然重要，但它只能作为 **deployment baseline**：

```text
它说明当前线上 AIChat 的真实状态和失败模式。
它不能单独证明 Bridge Contract / Guard / Repair 具有科研优势。
```

Research v1 的主实验必须同时包含：

- 当前产品基线；
- 强 prompt-only baseline；
- 文献启发 baseline；
- Bridge Contract 方法组；
- shuffled / oracle contract 负控与上界消融；
- Guard / Repair 安全控制消融；
- latency / LLM call count 成本指标。

论文不应写成：

```text
Bridge Contract + Guard + Repair 优于 current_system。
```

更稳的写法是：

```text
CP-MissingBridgeBench 比较不同 tutoring harness 在教学质量、关键桥梁泄露和调用成本之间的权衡。
```

## Baseline Layers

### Level 0: Deployment Baseline

| Baseline | 说明 | 主用途 |
| --- | --- | --- |
| `current_system` | 当前线上 AIChat 流程：rules、legacy judge、Pedagogical Judge v2 soft control、main LLM、自报 level hard gate、output guards | 固定产品现状，说明真实部署系统的失败模式 |

写作约束：

```text
`current_system` is a deployment baseline, not the sole research baseline.
```

### Level 1: Simple LLM Tutor Baseline

| Baseline | 说明 | 主用途 |
| --- | --- | --- |
| `vanilla_llm_tutor` | 只给普通算法竞赛教练身份和“不直接给完整答案”的基础约束 | 测量最小 tutor prompt 的能力 |

示例 prompt 约束：

```text
你是一名算法竞赛辅导老师。请帮助学生理解当前问题，但不要直接给完整题解或完整代码。
```

### Level 2: Strong Prompt-Only Baselines

| Baseline | 说明 | 主用途 |
| --- | --- | --- |
| `single_llm_structured` | 一个 LLM 同时输出 runtime bridge contract、学生回复和 self-check | 回答“为什么不让一个 LLM 一次性做完？” |
| `enhanced_prompt_only` | 加入强教学提示词，但不给具体 Bridge Contract | 隔离 prompt wording effect |

`enhanced_prompt_only` 应包含：

- Socratic guidance；
- no direct answer；
- single focus；
- bridge-oriented micro-example；
- ask student to infer；
- avoid full code / full solution；
- respect student-known state。

这个 baseline 是最重要的强对照之一。若它接近或超过 Bridge Contract，论文不能声称“架构本身导致质量提升”。

### Level 3: Literature-Inspired Baselines

这些 baseline 不声称完全复现公开论文系统，而是实现 **literature-inspired tutoring conditions**。原因是目前没有公开 baseline 直接覆盖中文算法竞赛逐轮 missing-bridge tutoring。

| Baseline | 文献启发 | 设计意图 |
| --- | --- | --- |
| `socratic_no_answer_tutor` | MathDial / tutoring dialogue scaffolding | 只用问题和最小提示引导，不直接给答案 |
| `mrbench_taxonomy_prompt` | MRBench / AI tutor pedagogical taxonomy | 按多维教学质量要求生成回复 |
| `codehelp_codeaid_no_direct_solution_tutor` | CodeHelp / CodeAid programming guardrails | 检验普通 no-direct-solution guardrail 是否已经足够 |
| `dbox_inspired_decomposition_tutor` | DBox / algorithmic programming co-decomposition | 单轮 step-tree-style 分解式脚手架，只帮当前一个子步骤 |
| `bridge_inspired_expert_decision_tutor` | Bridge / novice-expert decision modeling | 内部先判断学生错误、remediation strategy、teaching intention，再生成回复 |

写作约束：

```text
We derive literature-inspired baselines from prior tutoring and programming-education systems.
We do not claim direct reproduction unless code, data, and settings are actually matched.
```

`dbox_inspired_decomposition_tutor` 是 DBox-inspired baseline，不是 DBox reproduction。它参考官方材料中的 step tree、节点状态和 `general_hint` 原则，但不实现交互式 step-tree UI、多轮节点编辑、progressive reveal、代码与 step 对齐或真实学生学习收益评估。由于当前 benchmark 是单轮任务，DBox-inspired baseline 只允许 first-level general hint、guiding question 或 decomposition micro-task，不启用 reveal substep / reveal code，也不暴露 `detailed_hint`、`correctStep`、`correct_code` 或 pseudocode。

### Level 4: Missing-Bridge-Aware Methods

| Method | 说明 | 主用途 |
| --- | --- | --- |
| `bridge_contract_predicted` | 使用 Bridge Judge 预测 compact contract，再由 tutor 生成回复 | 测试 predicted missing-bridge diagnosis 是否带来额外价值 |
| `bridge_contract_predicted + guard` | 生成后调用 Leakage Guard | 测试 critical bridge leakage 检测是否有帮助 |
| `bridge_contract_predicted + guard + repair` | Guard 要求 rewrite/block 时 repair 一次 | 测试修复是否降低泄露且保留教学质量 |

这些是主方法组，但论文主张不应预设它们必然超过强 prompt baseline。

### Level 5: Negative Controls And Upper Bounds

| Condition | 说明 | 主用途 |
| --- | --- | --- |
| `bridge_contract_shuffled` | 使用其他 case 的 oracle contract | 负控：检测模型是否真的依赖具体 contract |
| `bridge_contract_oracle` | 使用 coach reference contract | 上界/分析条件：估计正确诊断信息的潜在价值 |
| `oracle_contract_with_guard` | oracle contract + predicted guard | 检查正确诊断是否仍会诱导泄露 |

解释规则：

- 如果 `bridge_contract_predicted` 不高于 `enhanced_prompt_only`，说明预测诊断信息没有超过强 prompt。
- 如果 `bridge_contract_predicted` 高于 `bridge_contract_shuffled`，说明具体 contract 内容不是装饰。
- 如果 `bridge_contract_oracle` 没有最高，不代表 schema 无效；可能说明 contract 注入、微型例子设计或 leakage control 仍有问题。
- `bridge_contract_oracle` 不是公平 runtime baseline，只能作为 analysis / upper-bound condition。

## Main Experiment Matrix

正式 50-case held-out 主实验建议至少包含：

| Group | System |
| --- | --- |
| Deployment | `current_system` |
| Prompt-only | `enhanced_prompt_only` |
| Literature-inspired | `socratic_no_answer_tutor` |
| Literature-inspired | `codehelp_codeaid_no_direct_solution_tutor` |
| Literature-inspired | `dbox_inspired_decomposition_tutor` |
| Literature-inspired + safety | `dbox_inspired_decomposition_tutor + guard` |
| Literature-inspired | `bridge_inspired_expert_decision_tutor` |
| Ours | `bridge_contract_predicted` |
| Ours + safety | `bridge_contract_predicted + guard` |
| Ours + safety | `bridge_contract_predicted + guard + repair` |

如果篇幅允许，加入：

- `vanilla_llm_tutor`
- `single_llm_structured`
- `mrbench_taxonomy_prompt`

## Ablation Matrix

用于拆分 effect 的消融实验建议包含：

| Comparison | 解释 |
| --- | --- |
| `enhanced_prompt_only - single_llm_structured` | prompt effect |
| `bridge_contract_predicted - enhanced_prompt_only` | predicted diagnosis effect beyond strong prompt |
| `bridge_contract_predicted - bridge_contract_shuffled` | contract validity effect |
| `bridge_contract_oracle - bridge_contract_predicted` | diagnosis upper-bound sanity check |
| `bridge_contract_predicted + guard - bridge_contract_predicted` | guard effect |
| `bridge_contract_predicted + guard + repair - bridge_contract_predicted + guard` | repair effect |

Repair effect 必须同时报告：

- quality delta；
- major leakage delta；
- student-ready pass delta；
- false-positive rewrite rate；
- repair latency；
- still-leaks-after-repair rate。

## DBox-inspired Baseline Gate

`dbox_inspired_decomposition_tutor` 进入 50-case held-out 主实验前，必须先完成：

1. 3-case smoke；
2. 10-20 case dev ablation；
3. prompt freeze 和版本记录。

进入主实验的最低条件：

- 能稳定输出可评分回复；
- 不频繁给完整解法；
- major leakage 不明显高于 `enhanced_prompt_only`；
- 质量不明显低于 `enhanced_prompt_only`；
- 只使用 first-level general hint、guiding question 或 decomposition micro-task；
- 不启用 reveal substep / reveal code。

## Metrics

每个 baseline 至少报告：

| 指标 | 目的 |
| --- | --- |
| `overall_quality` | 教练整体质量判断 |
| `core6_mean` | 六个核心教学维度 |
| `bridge_oriented_micro_example` | 是否通过例子引导可迁移桥梁关系 |
| `student_ready_pass` | 是否可直接给学生看 |
| `minor_bridge_leakage_rate` | 轻微关键桥泄露 |
| `major_bridge_leakage_rate` | 严重关键桥泄露 |
| `answer_code_leakage_rate` | 完整答案/代码泄露 |
| `p50_latency` / `p95_latency` | 延迟 |
| `llm_call_count` | 调用成本 |
| `stage_error_rate` | 稳定性 |

## Current Pilot Interpretation

3-case prompt-controlled ablation 已显示：

- `enhanced_prompt_only` 平均总体质量最高，说明强 prompt wording 本身可能解释相当一部分质量提升；
- `bridge_contract_predicted` 在 2/3 case 排名第一，且明显好于 `bridge_contract_shuffled`，说明具体 contract 内容仍可能有价值；
- `bridge_contract_oracle` 没有自动成为上界，说明正确诊断如果被 tutor 展开得太完整，也可能造成 critical bridge leakage。

因此当前最稳结论是：

```text
Bridge Contract variants 的收益混合了 prompt wording、具体诊断信息和模块化控制信号。
Research v1 必须用强 baseline 和负控消融把这些因素拆开。
```

## Writing Rules

### 可以写

```text
We include the current deployed AIChat as a deployment baseline, but not as the sole research baseline.
```

```text
We compare Bridge Contract variants against strong prompt-only and literature-inspired tutoring baselines to avoid weak-baseline bias.
```

```text
The shuffled-contract negative control tests whether the model uses the concrete missing-bridge diagnosis rather than generic tutoring instructions.
```

### 不应写

```text
Our method is better because it beats the current system.
```

```text
Bridge Contract architecture alone causes the quality gain.
```

```text
Oracle contract is a fair runtime baseline.
```

```text
We reproduce MathDial / MRBench / DBox / Bridge.
```

除非真的复现其公开代码、数据和实验设置，否则只能写 `literature-inspired`。

## Immediate Next Steps

1. 扩展 prompt-controlled ablation：3 case -> 10-20 case。
2. 实现或文档化 `socratic_no_answer_tutor`、`dbox_inspired_decomposition_tutor`、`bridge_inspired_expert_decision_tutor`。
3. 在 50-case held-out 主实验前冻结 strong prompt 和 judge prompt。
4. 主表降级 `current_system` 为 deployment baseline，并加入强 baseline。
5. 把论文 RQ 改成比较质量、泄露和成本 trade-off，而不是证明某个架构必胜。
