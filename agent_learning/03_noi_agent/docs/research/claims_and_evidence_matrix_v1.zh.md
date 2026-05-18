# Claims And Evidence Matrix v1

本矩阵用于约束论文主张。每个 claim 都必须对应证据；证据不足的 claim 只能写成 pilot observation、hypothesis 或 future work。

## 状态说明

| Status | 含义 |
|---|---|
| `supported_pilot` | 已有 pilot 或 smoke 证据，但不足以作为最终结论 |
| `needs_main_experiment` | 需要 50-case held-out 或更完整主实验 |
| `needs_judge_validation` | 需要 coach reference 校准 grader |
| `needs_repair_stress` | 需要专门 repair stress test |
| `needs_freeze` | 需要 prompt / judge / rubric freeze 后才能进入 held-out |
| `future_work` | 当前 Research v1 不应作为主结论 |

## Claim Matrix

| Claim | 当前证据 | 缺口 | 下一步证据 | Status |
|---|---|---|---|---|
| Missing bridge 比单纯算法标签更适合描述算法竞赛辅导卡点 | 已有 bridge schema、focus registry、20-case pilot、coach workbook；50-case held-out draft 已建并通过结构校验 | 还缺 Coach A 审查、Coach B 复标、裁决和冻结后的主实验 | Coach A 审查 50 条 draft；Coach B 标 20 条；agreement + adjudication；冻结后主实验 | `needs_main_experiment` |
| Critical bridge leakage 是传统完整答案泄露之外的重要风险 | mini-study 和 response review 中已出现“未给完整代码但说穿关键桥”的样例 | 还缺稳定 leakage label 和 grader 校准 | coach leakage labels；offline leakage grader precision/recall/F1；critical false negative rate | `needs_judge_validation` |
| Current AIChat 可以作为 baseline，但不能代表完整 Bridge-aware Tutor | `aichat_current_flow_v1.md` 已固定当前线上流程；v2 Judge 多为 soft control | 需要持续避免文档中混淆 online active 与 offline research | implementation status matrix；scope lock；paper wording audit | `supported_pilot` |
| Strong single-LLM baseline 必须纳入主实验 | 20-case mini-study 显示 `single_llm_structured` 很强 | 还缺 single-LLM + guard / repair 变体 | 主实验矩阵加入 `single_llm_structured + guard` 和 `single_llm_structured + guard + repair` | `needs_main_experiment` |
| 仅用 `current_system` 会造成 weak-baseline risk | 外部审查和 3-case prompt-controlled ablation 均显示强 prompt baseline 很可能解释相当一部分质量提升 | 还缺文献启发 baseline 和正式 50-case held-out 对比 | 新增 baseline protocol；加入 `enhanced_prompt_only`、`socratic_no_answer_tutor`、`codehelp_codeaid_no_direct_solution_tutor`、`dbox_inspired_decomposition_tutor`、`dbox_inspired_decomposition_tutor + guard`、`bridge_inspired_expert_decision_tutor`；扩展 prompt-controlled ablation | `needs_main_experiment` |
| Bridge Contract 可能提升脚手架贴合度和控制可解释性 | 已有 bridge_contract runner、contract schema、部分盲评样例 | 还不能证明优于 prompt-tuned single LLM | held-out comparison；response blind review；qualitative error analysis | `needs_main_experiment` |
| Leakage Guard 可以检测 critical bridge leakage 并提供运行时干预信号 | 已有 Leakage Judge 和 guard pipeline；当前 guard-only 条件除 block fallback 外不改写最终学生可见回复 | 需要证明 guard 准确且不是靠 oracle forbidden content；若要声称降低最终泄露，需要 repair/block 或 same-candidate before/after 证据 | predicted-only guard；coach leakage labels；precision/recall/F1；false positive rewrite rate；same-candidate repair stress | `needs_judge_validation` |
| Repair 可以降低泄露且保留部分教学质量 | 已有 Repair Generator、before/after 工具；20-case repair stress 教练盲评已完成：20 对全部标注，修复后质量更好 14、持平 3、更差 3；泄露减轻 19、持平 1；候选重大/答案泄露率 100%，修复后 5% | 这是高泄露压力样本和单教练盲评，不是自然 50-case held-out；`repair_stress_004` 仍 major leakage；部分修复会损害例子正确性或教学质量 | 把 `repair_stress_004` 和低质量 repair 作为 regression；在 50-case held-out 中单独报告自然触发率、repair quality delta、repair_still_leaks_rate | `supported_pilot` |
| Risk-triggered routing 可以降低延迟成本 | 已有 routing policy 文档和 control harness policy | 还缺 simulation 数据 | full multi-judge vs risk-triggered simulation；p50/p95 latency；LLM calls；under/over-trigger rate | `future_work` |
| LLM Judge 可用于开放式语义评测 | 已有 agent eval 方法论文档 | 还缺正式 calibration protocol 和 UNKNOWN 处理 | `llm_judge_calibration_protocol_v1.zh.md`；judge validation report | `needs_judge_validation` |
| Prompt 改进与架构改进可以被区分 | 已有 prompt patch log 雏形；3-case prompt-controlled ablation 盲评显示 `enhanced_prompt_only` 平均质量很强，说明 prompt wording 本身可能解释相当一部分提升；同时 `bridge_contract_predicted` 明显好于 `bridge_contract_shuffled`，说明具体 contract 内容仍可能有价值 | 3-case 样本太小；还需要 10-20 case prompt-controlled ablation、dev/test split 和 prompt freeze | 20 old seeds = dev/regression；扩展 prompt-controlled ablation；50 new seeds = held-out；prompt/judge patch logs | `needs_main_experiment` |
| Static lint / dev gate 可以防止高风险 condition 直接进入 headline 主表 | 离线 summary 已加入 `dev_gate`；answer-slot、filled-trace、worked-example、repair-still-leaks、critical leakage 或错误行会触发 `review_required`；短生成 smoke 三个 condition 均被拦为需要复查 | static lint 是高召回复查信号，不是 coach gold；仍需人工复查和 grader calibration | 把 dev gate 用作 50-case 前的筛选规则；报告每个 condition 的 `automatic_headline_ready` 和 reasons | `supported_pilot` |
| Research v1 文档应保持中英文成对 | 已新增 bilingual documentation policy 和 validator；当前 129 个 research Markdown 中新增文档无单语违规，23 个历史未配对文档记录为 legacy debt | 历史文档仍需逐步补齐；validator 目前允许 legacy allowlist | 新增文档必须 `.md` / `.zh.md` 成对；逐步补齐核心 legacy 文档 | `supported_pilot` |
| 控制论/feedback harness 有助于组织系统 | 已有 `control_harness_policy_v1.md` | 不能作为主创新；需要避免 concept creep | 只作为 system design principle 和 deployment simulation | `supported_pilot` |

## 论文写法约束

### 可以写成结论

只有满足以下条件的 claim 可以进入 Results / Conclusion：

- 在 held-out test 上有数据；
- 使用 coach reference 或校准后的 grader；
- prompt 和 judge prompt 已冻结；
- baseline 公平；
- 指标同时覆盖质量、泄露和成本中的相关维度。

### 只能写成 pilot observation

以下情况只能写成 pilot / preliminary observation：

- 只来自 20 old seeds；
- prompt tuning 后没有 held-out 复验；
- 只有单教练主观判断；
- 没有 blind review；
- repair 没有实际触发；
- 使用 oracle forbidden content。

### 只能写成 future work

以下内容当前不进入主结论：

- 真实线上 risk-triggered active mode；
- 长期学习收益；
- 长期学生画像；
- 完整 NOI/OI 算法 ontology；
- 自动 prompt patch；
- full multi-judge every turn 的线上默认策略。

## 当前最急的证据缺口

1. Coach review and freeze of the 50-case held-out draft。
2. Partial double annotation and adjudication。
3. 强 prompt-only 和文献启发 baseline。
4. `single_llm_structured + guard / repair` baseline。
5. LLM Judge calibration report。
6. Prompt / judge prompt freeze logs。
7. 逐步补齐 23 个 legacy 单语研究文档的中英文配对。
