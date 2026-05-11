# Claims And Evidence Matrix v1

本矩阵用于约束论文主张。每个 claim 都必须对应证据；证据不足的 claim 只能写成 pilot observation、hypothesis 或 future work。

## 状态说明

| Status | 含义 |
|---|---|
| `supported_pilot` | 已有 pilot 或 smoke 证据，但不足以作为最终结论 |
| `needs_main_experiment` | 需要 50-case held-out 或更完整主实验 |
| `needs_judge_validation` | 需要 coach reference 校准 grader |
| `needs_repair_stress` | 需要专门 repair stress test |
| `future_work` | 当前 Research v1 不应作为主结论 |

## Claim Matrix

| Claim | 当前证据 | 缺口 | 下一步证据 | Status |
|---|---|---|---|---|
| Missing bridge 比单纯算法标签更适合描述算法竞赛辅导卡点 | 已有 bridge schema、focus registry、20-case pilot、coach workbook | 还缺 50-case held-out 和双教练一致性 | 50 条 stratified seed；Coach A 全标；Coach B 标 20 条；agreement + adjudication | `needs_main_experiment` |
| Critical bridge leakage 是传统完整答案泄露之外的重要风险 | mini-study 和 response review 中已出现“未给完整代码但说穿关键桥”的样例 | 还缺稳定 leakage label 和 grader 校准 | coach leakage labels；offline leakage grader precision/recall/F1；critical false negative rate | `needs_judge_validation` |
| Current AIChat 可以作为 baseline，但不能代表完整 Bridge-aware Tutor | `aichat_current_flow_v1.md` 已固定当前线上流程；v2 Judge 多为 soft control | 需要持续避免文档中混淆 online active 与 offline research | implementation status matrix；scope lock；paper wording audit | `supported_pilot` |
| Strong single-LLM baseline 必须纳入主实验 | 20-case mini-study 显示 `single_llm_structured` 很强 | 还缺 single-LLM + guard / repair 变体 | 主实验矩阵加入 `single_llm_structured + guard` 和 `single_llm_structured + guard + repair` | `needs_main_experiment` |
| 仅用 `current_system` 会造成 weak-baseline risk | 外部审查和 3-case prompt-controlled ablation 均显示强 prompt baseline 很可能解释相当一部分质量提升 | 还缺文献启发 baseline 和正式 50-case held-out 对比 | 新增 baseline protocol；加入 `enhanced_prompt_only`、`socratic_no_answer_tutor`、`codehelp_codeaid_no_direct_solution_tutor`、`dbox_inspired_decomposition_tutor`、`dbox_inspired_decomposition_tutor + guard`、`bridge_inspired_expert_decision_tutor`；扩展 prompt-controlled ablation | `needs_main_experiment` |
| Bridge Contract 可能提升脚手架贴合度和控制可解释性 | 已有 bridge_contract runner、contract schema、部分盲评样例 | 还不能证明优于 prompt-tuned single LLM | held-out comparison；response blind review；qualitative error analysis | `needs_main_experiment` |
| Leakage Guard 可以降低 critical bridge leakage | 已有 Leakage Judge 和 guard pipeline | 需要证明 guard 准确且不是靠 oracle forbidden content | predicted-only guard；coach leakage labels；precision/recall/F1；false positive rewrite rate | `needs_judge_validation` |
| Repair 可以降低泄露且保留教学质量 | 已有 Repair Generator、before/after 工具；20-case repair stress 自动结果显示 20/20 触发 repair，二次 guard 19/20 pass，1 条树差分 worked example 仍失败 | 自动二检不是 gold；还不能证明教学质量，部分 repaired response 可能仍是低质量 micro-example 或临时任务 | 教练填写 all20 before/after blind review；paired quality/leakage/student-ready analysis；对 `repair_stress_004` 加 regression | `needs_repair_stress_review` |
| Risk-triggered routing 可以降低延迟成本 | 已有 routing policy 文档和 control harness policy | 还缺 simulation 数据 | full multi-judge vs risk-triggered simulation；p50/p95 latency；LLM calls；under/over-trigger rate | `future_work` |
| LLM Judge 可用于开放式语义评测 | 已有 agent eval 方法论文档 | 还缺正式 calibration protocol 和 UNKNOWN 处理 | `llm_judge_calibration_protocol_v1.zh.md`；judge validation report | `needs_judge_validation` |
| Prompt 改进与架构改进可以被区分 | 已有 prompt patch log 雏形；3-case prompt-controlled ablation 盲评显示 `enhanced_prompt_only` 平均质量很强，说明 prompt wording 本身可能解释相当一部分提升；同时 `bridge_contract_predicted` 明显好于 `bridge_contract_shuffled`，说明具体 contract 内容仍可能有价值 | 3-case 样本太小；还需要 10-20 case prompt-controlled ablation、dev/test split 和 prompt freeze | 20 old seeds = dev/regression；扩展 prompt-controlled ablation；50 new seeds = held-out；prompt/judge patch logs | `needs_main_experiment` |
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

1. 50-case held-out test set。
2. Partial double annotation and adjudication。
3. 强 prompt-only 和文献启发 baseline。
4. `single_llm_structured + guard / repair` baseline。
5. LLM Judge calibration report。
6. Repair stress test 扩展与 before/after 盲评。
7. Prompt / judge prompt freeze logs。
