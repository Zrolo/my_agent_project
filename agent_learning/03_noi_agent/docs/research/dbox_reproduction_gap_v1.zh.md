# DBox Reproduction Gap v1

本文档说明 Research v1 中 `dbox_inspired_decomposition_tutor` 的定位。结论很明确：

```text
我们实现 DBox-inspired decomposition baseline，不复现 DBox。
```

## DBox 原系统是什么

DBox 是一个面向 algorithmic programming learning 的交互式 learner-LLM co-decomposition 系统。它的核心不是一句 prompt，而是一套学习工作区：

- 学生和 LLM 共同构建 step tree；
- 系统支持 solution formation 和 solution implementation 两个阶段；
- step tree 节点有状态，例如 correct、incorrect、missing、can be divided、system generated；
- 学生可以围绕节点继续拆分、修改或实现；
- 系统提供 progressive hints；
- 反复失败后才可能 reveal substep 或 reveal code；
- 系统将代码与 step tree 对齐；
- 原论文通过真实学生 study 评估 learning gain、cognitive engagement、critical thinking 等学习结果。

这些能力属于多轮交互式系统，而不是单轮回复生成条件。

官方材料包 `pn2271.zip` 进一步确认 DBox 至少包含四类后端/前端交互：From Editor to Step Tree、Check Step Tree、Copy to Comments、Check Match。Prompt 和源码中出现了 `general_hint`、`detailed_hint`、`correctStep`、`correct_code`、code mapping 等字段。因此我们的单轮 baseline 只能借鉴 step-tree/status/general hint 原则，不能启用 reveal-like 或 answer-bearing 字段。

## 我们的 benchmark 是什么

CP-MissingBridgeBench 当前评测对象是单轮算法竞赛辅导回复：

```text
给定学生当前 turn、题目上下文和近期对话
-> 系统生成一条 tutor response
-> 教练盲评教学质量、关键桥梁泄露、微型例子质量和是否适合给学生看
```

当前 benchmark 不包含：

- 学生编辑 step tree 的交互界面；
- 多轮 co-decomposition；
- 节点状态更新；
- repeated failed attempts；
- reveal substep / reveal code 的触发条件；
- 代码与 step tree 的实时对齐；
- 真实学生学习收益评估。

因此，Research v1 不能声称复现 DBox，也不能直接与 DBox 原论文的 learning gain、engagement 或 critical thinking 结果比较。

## 我们实现什么

Research v1 实现的是 `dbox_inspired_decomposition_tutor`。它只把 DBox 的一个核心原则适配到单轮离线评测：

```text
用分解式脚手架帮助学生把当前大问题缩小成一个可回答的当前子步骤。
```

该 baseline 内部生成结构化对象：

```json
{
  "baseline_group": "literature_inspired_decomposition",
  "decomposition_view": [
    {"step_id": "s1", "step_name": "...", "status": "known_or_not_relevant"},
    {"step_id": "s2", "step_name": "...", "status": "current_stuck_step"},
    {"step_id": "s3", "step_name": "...", "status": "defer"}
  ],
  "current_substep": "...",
  "hint_level": "general_question",
  "student_visible_response": "..."
}
```

学生可见回复不展示完整 step tree，只做：

- 把当前大问题拆成一个更小的当前子步骤；
- 让学生补完当前 substep；
- 给 first-level general hint、guiding question 或 decomposition micro-task；
- 保留学生自己完成关键关系的空间。

## Progressive Hint 限制

Because our benchmark is single-turn and does not observe repeated failed attempts, the DBox-inspired baseline uses only first-level decomposition guidance and question-based hints.

因此当前 baseline 禁止：

- reveal substep；
- reveal code；
- detailed pseudocode；
- 完整 step tree answer；
- 完整算法；
- 完整代码；
- 完整状态定义；
- 完整转移方程；
- 完整 check 条件；
- 完整边界更新规则；
- 直接补完当前 critical bridge。

特别地，官方材料中的 `detailed_hint`、`correctStep`、`correct_code`、pseudocode 和 code-line mapping 不进入学生可见回复；它们只作为说明 DBox 原系统复杂度和 reproduction gap 的材料依据。

## 为什么这个 baseline 仍然有用

`dbox_inspired_decomposition_tutor` 的作用不是证明我们复现了 DBox，而是防止 weak-baseline bias。它帮助回答：

- 分解式脚手架是否已经足够强？
- missing-bridge contract 是否在 decomposition prompting 之外提供额外价值？
- Guard 是否对 decomposition baseline 同样有效？
- Bridge Contract 的优势是否只出现在高泄露风险或复杂卡点样本中？

## 公平比较要求

主实验至少应包含：

```text
current_system
enhanced_prompt_only
dbox_inspired_decomposition_tutor
dbox_inspired_decomposition_tutor + guard
bridge_contract_predicted
bridge_contract_predicted + guard
bridge_contract_predicted + guard + repair
```

`dbox_inspired_decomposition_tutor + guard` 必须进入主表，避免 Guard/Repair 只加在我们方法上造成不公平。

Appendix 可选加入：

```text
dbox_inspired_decomposition_tutor + guard + repair
codehelp_codeaid_no_direct_solution_tutor
bridge_inspired_expert_decision_tutor
```

## 进入 50-case 主实验门槛

进入正式 50-case held-out 主实验前，DBox-inspired baseline 必须先完成 3-case smoke 和 10-20 case dev ablation，并满足：

- 能稳定输出可评分回复；
- 不频繁给完整解法；
- major leakage 不明显高于 `enhanced_prompt_only`；
- 质量不明显低于 `enhanced_prompt_only`；
- prompt 已冻结并记录版本。

## 论文表述

英文：

```text
We implement a DBox-inspired decomposition baseline, not a reproduction of DBox.
```

中文：

```text
我们不复现 DBox，因为 DBox 是交互式 learner-LLM co-decomposition 系统，包含 step-tree 界面、渐进提示、代码与步骤对齐和真实学生学习收益评估。我们的 benchmark 是单轮算法竞赛辅导回复评测，因此只实现 DBox-inspired decomposition baseline，用来检验分解式脚手架是否已经足够强，以及 missing-bridge contract 是否在其之外提供额外价值。
```

## Source Anchors

- [DBox arXiv / ar5iv](https://ar5iv.org/html/2502.19133v1)
- [DBox ACM DL](https://dl.acm.org/doi/abs/10.1145/3706598.3713748)
- [DBox official materials review](dbox_official_materials_review_v1.zh.md)
