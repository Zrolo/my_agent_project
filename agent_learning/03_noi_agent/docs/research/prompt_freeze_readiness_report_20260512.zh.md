# Prompt / Judge / Rubric Freeze Readiness Report

日期：2026-05-12

本报告用于判断 Research v1 是否可以进入正式 50-case held-out 主实验前的 prompt / judge / rubric freeze。结论先行：

> 当前项目已经完成 P1 dev ablation、Repair stress、DBox-inspired baseline、strong prompt-only baseline、static lint dev gate、模型运行配置协议和双语文档治理的基础工作，但还不应直接声明所有 prompt 已冻结。现在应进入 **freeze readiness review**：确认哪些组件可以作为 `v1.0-dev` 固定，哪些组件只能作为 dev/appendix 条件，哪些必须先补 regression 或人工确认。

## 当前结论

| 层 | 当前状态 | 是否可直接进入 held-out headline | 原因 |
|---|---|---:|---|
| `enhanced_prompt_only` | runner 已接入，dev ablation 已覆盖 | 有条件可以 | 它是 strong prompt baseline，必须保留；但仍需项目负责人确认 prompt 版本并锁定 |
| `dbox_inspired_decomposition_tutor` | runner 已接入，DBox reproduction gap 已记录 | 有条件可以 | 可作为文献启发 baseline；不是 DBox reproduction；进入主实验前需固定 prompt 文本 |
| `dbox_inspired_decomposition_tutor + guard` | dev ablation 已覆盖 | 有条件可以 | 用于公平比较 Guard 信号是否跨 generator 可用；guard-only 不代表最终回复已被改写 |
| `bridge_contract_predicted` | dev ablation 已覆盖 | 暂不建议单独作为 headline 安全结论 | 质量信号强，但 dev review 显示仍有 critical bridge leakage；可进入主表但结论必须限于质量/控制信号，不得声称安全 |
| `bridge_contract_predicted + guard` | dev ablation 已覆盖 | 暂不建议声称 Guard 已解决泄露 | Leakage Guard 对 answer-slot / filled-table / worked-example recall 仍不稳定；需要 coach calibration |
| `bridge_contract_predicted + guard + repair` | dev ablation 和 Repair stress 已覆盖 | 有条件进入主表或 appendix | Repair stress 有正向 pilot evidence，但自然样本触发率、repair_still_leaks 和质量损失仍需 held-out 报告 |
| `bridge_contract_safe_scaffold` | 离线 appendix 条件 | 不建议进主表 | 安全但质量低；适合作为 high-risk fallback / stress appendix |
| Response review rubric v2 | 中英双语已更新，加入负担字段 | 有条件可以 | 需要教练确认后作为 50-case 盲评 rubric |
| Static lint dev gate | summary 已实现 | 可以作为 screening，不可作为 gold | 它是高召回复查信号，不是人工 leakage label |
| Model/runtime config | protocol 已新增 | 有条件可以 | 主实验需固定 tutor 模型、thinking mode、judge / guard / repair stack，见 `model_runtime_configuration_v1.zh.md` |

## 不应冻结为最终结论的内容

以下内容只能作为 dev / pilot evidence：

- 20-case fair mini-study；
- 10-case dev ablation；
- 3-case prompt-controlled ablation；
- Repair stress all20 before/after；
- short constructed response smoke；
- static lint dev gate；
- answer-slot Guard prompt patch 后的自盲评。

这些结果可以用于修 prompt、选主实验条件和设计 regression，但不能直接成为最终论文 headline。

## Freeze 前必须满足的条件

进入 50-case held-out 前，至少需要满足：

1. `prompt_patch_log.md` 中每个进入主实验的 tutor prompt 都有明确版本名和 human approval。
2. `judge_prompt_patch_log.md` 中 Runtime Leakage Guard 和主要 Offline Grader prompt 至少标为 `v1.0-dev frozen for held-out` 或清楚说明仍为 dev-only。
3. `response_review_rubric_v2.zh.md` / `.md` 作为 50-case 盲评标准锁定。
4. `model_runtime_configuration_v1.zh.md` / `.md` 锁定主实验 tutor model、thinking mode、judge / guard / repair stack。
5. `dev_gate` 继续保留在 summary 中，但论文写法必须说明它不是 coach gold。
6. 50-case held-out 数据集创建后，不再根据该批结果回头修改同一批主实验 prompt / judge / rubric / model runtime。
7. 每个主实验 condition 都必须记录：
   - `tutor_mode`
   - `pipeline_mode`
   - prompt version
   - judge prompt version
   - repair prompt version, if applicable
   - tutor model provider
   - chat thinking mode
   - judge model
   - final response source
   - static lint risk
   - stage errors

## 建议主实验条件

主表建议控制在 8 个左右：

| Condition | 用途 |
|---|---|
| `current_system` | deployment baseline |
| `enhanced_prompt_only` | strong prompt-only baseline |
| `codehelp_codeaid_no_direct_solution_tutor` | programming guardrail baseline |
| `dbox_inspired_decomposition_tutor + guard` | 文献启发 decomposition + fair guard baseline |
| `bridge_inspired_expert_decision_tutor` | expert-decision baseline |
| `single_llm_structured + guard` | strong single-LLM + guard baseline |
| `bridge_contract_predicted + guard` | missing-bridge-aware guarded method |
| `bridge_contract_predicted + guard + repair` | missing-bridge-aware guarded + repair method |

Appendix / stress 条件：

- `dbox_inspired_decomposition_tutor`
- `bridge_contract_predicted`
- `bridge_contract_shuffled`
- `bridge_contract_oracle`
- `bridge_contract_safe_scaffold`
- `risk_triggered_simulation`

## 当前阻塞项

| 阻塞项 | 影响 | 建议处理 |
---|---|---|
| Leakage Guard 对 answer-slot / filled-trace / worked-example recall 不稳定 | 不能声称 Guard 已可靠防泄露 | held-out 中同时报告 coach label、LLM Guard label 和 static lint |
| Repair stress 仍有 `repair_stress_004` major leakage | 不能声称 Repair 完全解决泄露 | 加入 regression；报告 repair_still_leaks_rate |
| Bridge Contract 单独生成仍可能质量高但泄露 | 不能把 Bridge Contract 写成安全机制 | 写成 pedagogical organization / controllable signal；安全另由 guard/repair/route 评估 |
| `bridge_contract_safe_scaffold` 质量低 | 不适合主表证明教学质量 | 作为 high-risk deterministic fallback appendix |
| 历史双语文档仍有 23 个 legacy debt | 不阻塞实验，但影响外部协作整洁度 | 逐步补齐核心历史文档 |

## 推荐下一步

1. 将本报告作为 freeze readiness checkpoint。
2. 项目负责人审阅 `prompt_patch_log.md` 和 `judge_prompt_patch_log.md`，决定哪些 prompt 进入 `v1.0-dev frozen`。
3. 项目负责人审阅 `model_runtime_configuration_v1.zh.md`，决定主实验是否统一使用 `deepseek_flash` + `profile_default`。
4. 建立 50-case held-out 数据集和 dataset card。
5. 做 Coach A 全标 + Coach B 至少 20 条复标。
6. 在冻结版本上跑主实验，不再根据 held-out 结果回头调 prompt。

## 论文写法

可以写：

> Before held-out evaluation, we used development ablations and repair stress tests to select baseline conditions and freeze prompt/rubric versions. Development results were not used as headline claims.

中文：

> 在 held-out 评测前，我们使用开发集消融和 Repair stress test 选择主实验条件，并冻结 prompt / rubric 版本。开发阶段结果不作为论文主结论。

不要写：

> 我们已经证明 Bridge Contract + Guard + Repair 最优。

当前证据只能支持：

> Bridge Contract、Guard、Repair 和文献启发 baseline 已经具备进入 50-case held-out 公平比较的研究条件，但最终结论必须等待冻结版本上的 held-out 结果、双教练标注和 judge calibration。
