# Prompt Freeze Decision 20260512

本文件记录 Research v1 从 dev ablation 进入 50-case held-out 前的阶段性冻结决策。它不是最终论文结果，也不是线上 AIChat 上线决策。

## 2026-05-16 更新

本文件保留 2026-05-12 的早期 freeze 决策。Coach A case/source gate 通过后，dialogue-state v3 50-case reviewed candidate 的下一轮 response generation 已收敛到新的 7-condition 主表：

```text
dialogue_state_v3_main
```

该更新记录见 [dialogue_state_v3_prompt_rubric_freeze_gate_20260516.zh.md](dialogue_state_v3_prompt_rubric_freeze_gate_20260516.zh.md)。后续若基于 reviewed candidate 生成 50-case 回复，应优先使用该 2026-05-16 gate，而不是本文件中的早期 8-condition `heldout_main` 候选矩阵。

## 决策摘要

当前决策是 **条件冻结主实验候选 prompt / judge / rubric，进入 50-case held-out 准备阶段**。

含义：

- 可以停止继续新增 baseline 或大改 prompt；
- 可以用 dev / regression 结果确定主实验条件；
- 50-case held-out 开跑后，不再用该批结果回头调同一批 prompt / judge / rubric；
- 所有 dev 结果只能作为开发证据，不作为论文 headline。

## 线上上线备注

2026-05-12，线上学生 AIChat 已将 `enhanced_prompt_only_clean` 作为可选“教练引导”回答方式上线。默认“简洁提示”仍对应 `current_system`。

该产品改动不改变本文件的 freeze 决策：

- `教练引导` 是线上 prompt-only UX option，不是 held-out 实验证据；
- 它没有接入 Bridge Judge、Runtime Bridge Contract、Leakage Guard、Repair 或 risk-triggered routing；
- 50-case held-out 主实验仍必须使用本文件冻结的 offline condition、固定模型配置和盲审协议；
- 如果后续使用真实线上日志，必须按 `aichat_prompt_mode` 分层，不能把 `教练引导` 轮次并入旧 `current_system`。

## 主实验候选条件

建议 50-case 主表控制在 8 个左右：

| Condition | 地位 | 决策 |
|---|---|---|
| `current_system` | deployment baseline | 保留，用于说明当前线上系统真实失败模式 |
| `enhanced_prompt_only` | strong prompt-only baseline | 保留，用于控制 prompt wording effect |
| `codehelp_codeaid_no_direct_solution_tutor` | programming guardrail baseline | 保留，用于检验 no-direct-solution 是否足够 |
| `dbox_inspired_decomposition_tutor + guard` | literature-inspired decomposition + safety baseline | 保留，作为最重要的算法编程教育强 baseline |
| `bridge_inspired_expert_decision_tutor` | expert-decision baseline | 保留，用于对照通用专家决策注入 |
| `single_llm_structured + guard` | strong single-LLM baseline | 保留，用于回答“为什么不用一个 LLM 做完” |
| `bridge_contract_predicted + guard` | missing-bridge-aware guarded method | 保留，用于评估 Bridge Contract + Guard |
| `bridge_contract_predicted + guard + repair` | missing-bridge-aware guarded + repair method | 保留，用于评估 Repair trade-off |

## Appendix / Dev 条件

以下条件暂不进主表，放入 appendix、stress 或 dev 分析：

- `dbox_inspired_decomposition_tutor`
- `bridge_contract_predicted`
- `bridge_contract_shuffled`
- `bridge_contract_oracle`
- `bridge_contract_safe_scaffold`
- `edf_inspired_adaptive_scaffolding_tutor`
- `edf_inspired_adaptive_scaffolding_tutor + guard`
- `risk_triggered_simulation`

EDF-inspired 当前仅作为 dev / appendix 候选。10-case AI 预评中，它低于 `dbox_inspired_decomposition_tutor + guard` 和 `bridge_contract_predicted + guard + repair`，且 Guard 没有改善 EDF，因此不建议进入 50-case 主表。

## 可冻结内容

以下内容可以进入 `v1.0-dev frozen for held-out` 候选状态，等待项目负责人最终确认：

- response review rubric v2；
- short constructed response interaction policy；
- enhanced prompt-only prompt；
- DBox-inspired prompt；
- CodeHelp/CodeAid-style prompt；
- Bridge-inspired expert-decision prompt；
- Bridge Contract tutor prompt；
- Leakage Guard prompt；
- Repair prompt；
- model/runtime configuration protocol；
- blind review export schema, including `上下文 AI 回复` and `AI 回复（要评分）` columns。

## 不能声称已经解决的内容

即使进入 freeze，也不能写：

- Guard 已可靠防止 critical bridge leakage；
- Repair 已可靠解决泄露；
- Bridge Contract 架构本身导致全部质量提升；
- EDF/Copa 或 DBox 已被完整复现；
- dev ablation 结果是正式 held-out 结论。

当前更稳的写法是：

> Development ablations were used to select and freeze evaluation conditions. Final claims require the frozen 50-case held-out evaluation, coach reference labels, and judge calibration.

中文：

> 开发集消融用于选择和冻结评测条件；最终结论必须等待冻结版本上的 50-case held-out、教练 reference labels 和 Judge calibration。

## 工程决策

- 离线 runner 继续记录 `stage_errors`，但对可恢复的 Leakage Judge schema omission 做归一化，避免把 `leakage_level > 0` 且 `leaked_elements=[]` 的输出直接变成无效 stage。
- 归一化只用于实验可分析性，不改变 prompt 要求。Leakage Judge prompt 仍要求 positive leakage 必须说明泄露元素。
- Static lint 继续作为 high-recall review trigger，不作为 coach gold。

## Go / No-go

进入 50-case held-out 前还需要：

1. 项目负责人确认本文件主实验矩阵；
2. 项目负责人确认 prompt / judge / rubric 版本；
3. 50-case held-out 草稿经过教练审查；
4. Coach A 全标，Coach B 至少 20 条复标；
5. judge calibration protocol 有可执行输出。

若以上未满足，仍停留在 dev / pre-held-out 阶段。
