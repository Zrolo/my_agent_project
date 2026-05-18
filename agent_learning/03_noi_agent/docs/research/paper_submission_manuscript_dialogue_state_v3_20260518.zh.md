# CP-MissingBridgeBench: Turn-Level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation for LLM Tutors in Competitive Programming

## Draft Status

本文档是 dialogue-state v3 evidence package 组装出的单文件投稿 manuscript skeleton。它不新增实验、不修改数据、不接入线上 active mode。它只是论文写作表面，不替代底层 evidence reports。

主要解释边界：

- 主 headline 只使用 31-case `main_scaffold_eval` slice。
- Coach A、Coach B 和 priority60 adjudication 是 expert reference views，不是 gold。
- Guard-only 是 guard-instrumented runtime signal，不是 final-response rewrite。
- Repair 因果证据来自 same-candidate stress test。
- DBox+Repair 是 targeted fairness sensitivity，不是 full main condition。
- DeepSeek LLM grader calibration 只能作为辅助证据，不能替代人审。

## Abstract

大语言模型正在被用于编程辅导，但“不直接给代码或最终答案”并不等于教学上安全。在算法竞赛辅导中，一个很短的提示也可能提前说穿学生本应自己推出的关键中间推理。我们将学生当前理解到下一步有效解题动作之间缺失的局部推理称为 missing bridge，并将未给完整题解或代码、但提前补完该桥梁的行为定义为 critical bridge leakage。

我们提出 CP-MissingBridgeBench，一个面向算法竞赛 LLM Tutor 的 turn-level 评测框架。每条 case 包含题目上下文、近期对话、学生当前问题，以及 case-specific rubric，明确 success criteria、forbidden content、acceptable reveal 和 expected student next action。dialogue-state v3 evidence package 包含 50 条 reviewed candidate cases、7 个匿名 tutoring-harness conditions 和 350 条 AI responses，由两位教练完成全量盲评，并配套 priority adjudication、paired uncertainty、slice analysis、Repair same-candidate stress test、DBox+Repair fairness sensitivity 和 DeepSeek LLM-grader calibration。

当前证据支持克制结论：CP-MissingBridgeBench 能揭示不同 tutoring harness 的 quality-safety-burden trade-off；DBox-inspired decomposition 是强 baseline；no-direct-solution prompting 不能消除 critical bridge leakage；Bridge Contract compact + Guard/Repair 在主人工评审口径下呈现有利的整体质量和高严重度泄露控制趋势。同时，student-ready 和 rank 对评分者口径敏感，Guard-only 在当前 pipeline 中只是 instrumentation，Repair 的因果证据来自 same-candidate stress test 且伴随 student-burden trade-off，LLM grader 只能作为辅助信号。

## 1. Introduction

大语言模型越来越多地被用作编程 Tutor，但评估它们是否真正“帮得合适”并不简单。一个回复可以礼貌、简洁、遵守“不直接给答案”的要求，却仍然移除学生本应完成的核心推理工作。这个问题在算法竞赛中尤其明显：学习往往取决于跨过一个很小但关键的推理缺口，例如理解状态含义、转移为何成立、check 谓词代表什么、二分边界为何移动，或该看什么证据来定位 bug。

我们把这个缺口称为 missing bridge：学生当前理解与下一步有效解题动作之间的局部推理桥梁。我们把 critical bridge leakage 定义为一种辅导失败：模型不一定给出完整题解或代码，但提前替学生补完了这个 missing bridge。它不同于普通 answer leakage。Tutor 可能没有给最终代码却仍然说太多；反过来，Tutor 也可以给少量上下文或提出聚焦问题，而不泄露桥梁。

现有 programming-help safeguard 通常关注避免直接答案或代码。这是必要的，但不足以覆盖 turn-level tutoring。在算法竞赛中，一个短提示如果直接给出了当前 invariant、predicate meaning、update rule 或 proof step，也可能过度完整。另一方面，过度谨慎的拒答也可能没有教学价值。因此，评测目标不应只是“模型有没有给答案”，而应是回复是否在提供有效脚手架的同时保留了适当的学生推理空间。

我们提出 CP-MissingBridgeBench，一个面向算法竞赛 LLM Tutor 的 turn-level 评测框架。每条 case 包含题目上下文、近期对话、学生当前问题和 case-specific rubric，后者指定 success criteria、forbidden content、acceptable reveal 和 expected student next action。该 benchmark 同时评估 quality、safety 和 student burden，而不是把 tutoring 压成单一分数。

本文贡献有四点：

1. 定义 missing bridge，用于表示算法竞赛辅导中学生当前缺失的局部推理桥梁。
2. 定义 critical bridge leakage，刻画超出 direct answer / code leakage 的教学安全失败模式。
3. 构建 case-specific human-review protocol，包含 success criteria、forbidden content、acceptable reveal、expected next action、double review、priority adjudication 和 sensitivity reporting。
4. 在同一 dialogue-state v3 evidence package 下比较 prompt-only、no-direct-solution、DBox-inspired、Bridge-guided、Bridge Contract、Guard 和 Repair harnesses，强调 quality-safety-burden trade-off，而不是绝对系统胜利。

## 2. Related Work

关于 dialogue tutoring 和 Socratic guidance 的工作研究模型如何通过提问、引出解释和脚手架来保护学生推理，而不是直接给最终答案 [macina2023mathdial; maurya2024mrbench; wang2023bridge]。CP-MissingBridgeBench 共享“保留学习者推理”的目标，但聚焦算法竞赛 turn，其中关键单元常常是局部桥梁：状态含义、转移来源、check 谓词、invariant 或 debugging evidence target。

Programming-help systems 和 benchmarks 通常包含避免 full solution 或 code 的 guardrails [liffiton2023codehelp; kazemitabaar2024codeaid]。这些约束重要，但我们的结果说明它们还不够：在 dialogue-state v3 中，no-direct-solution baseline 比 prompt-only 更强，但仍出现 critical bridge leakage。

DBox 和相关 step-based programming tutors 强调把编程任务分解成步骤，并通过结构化提示支持学习者 [ma2025dbox]。我们将 DBox 作为 DBox-inspired decomposition baseline 的文献锚点。但当前 condition 不是 DBox reproduction：它不实现 interactive step-tree UI、多轮 co-decomposition、progressive reveal、code-step alignment 或 student learning-gain study。

EDF/Copa 等 adaptive scaffolding systems 围绕 evidence、decision 和 feedback 组织辅导，并用 learner-state estimates 和 dialogue policies 决定如何回应 [cohn2026edf]。CP-MissingBridgeBench 与其精神相近，但领域和粒度不同：我们评估的是带近期对话和题目上下文的单轮算法竞赛 Tutor 回复，而不是多轮课堂学习效果。

Rubric-based evaluation 和 LLM-as-judge 方法为开放式回复评测提供了可扩展路径 [zheng2023llmjudge; kim2023prometheus; maurya2024mrbench; gunjal2025rar]。CP-MissingBridgeBench 采用结构化 rubric，但我们的校准显示，自动 grader 对高风险 critical bridge leakage 仍不够可靠。Agent evaluation 工作也强调评测应该覆盖整个 harness，而不是单独模型调用 [anthropic2026agentevals]。

## 3. Benchmark and Review Protocol

CP-MissingBridgeBench 评测算法竞赛辅导中的一个特定失败模式：学生已经表达了部分想法或卡点，但还缺少从当前状态到下一步有效解题动作之间的关键 reasoning bridge。Missing bridge 不是固定算法标签。同一个 DP 题在不同 tutoring turn 中可能涉及不同 missing bridge：state semantics、transition source、boundary initialization、correctness reasoning 或 implementation debugging。

Critical bridge leakage 指 Tutor 没有直接给完整题解或代码，却提前透露了学生本应继续推导的中间推理。它不同于普通 informative tutoring。好的 Tutor 可以提供上下文、轻提示、检查问题或低负担下一步。风险来自过早补完当前 missing bridge。

Taxonomy 使用三层：

```text
cognitive bridge family + leakage mechanism + surface anchor
```

`state_representation_semantics`、`transition_recurrence_source` 和 `predicate_check_semantics` 是 operational cognitive bridge families。DP state、binary-search check、lazy propagation、tree difference、local code、greedy proof 和 debugging trace 是 surface anchors，用于在具体算法语境中实例化更抽象的 cognitive bridge 和 leakage mechanism。因此，benchmark 不能被描述成只覆盖 DP/check/lazy/tree/local-code 场景。

Dialogue-state v3 包含 50 条 reviewed candidate cases。每条 case 保留当前对话状态，而不是只给孤立题面和问题。50 条 case 按 paper use 分为：

| slice | case_n | paper use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | Main scaffold-quality, leakage, and burden comparison |
| `main_eval_with_caution` | 5 | Sensitivity / appendix |
| `clarification_safety_slice` | 10 | Clarification, non-over-inference, and context-insufficient safety |
| `policy_safety_slice` | 4 | Safety redirection for direct answer/code requests |

评分前，reviewer 使用 case-specific rubric，至少包括 `success_criteria`、`forbidden_content`、`critical_bridge_boundary`、`acceptable_reveal` 和 `expected_student_next_action`。这使得评分依赖学生当前状态和 turn-level teaching goal，而不是泛泛判断回复是否“像个好 Tutor”。

## 4. Experimental Setup

主 human review 比较 7 个匿名 conditions，共 350 条回复。教练盲评时看不到 condition name。解盲后，conditions 可描述为：

| condition | role | interpretation boundary |
| --- | --- | --- |
| `enhanced_prompt_only_clean` | Strong prompt-only baseline | 没有 case-specific Bridge Contract。 |
| `codehelp_codeaid_clean` | No-direct-solution baseline | 测试 no-direct-code / no-direct-solution guardrails 是否足够。 |
| `dbox_inspired_clean` | Literature-inspired decomposition baseline | DBox-inspired single-turn scaffold；不是 DBox reproduction。 |
| `dbox_inspired_guard` | DBox-inspired + guard-instrumented variant | Guard-only 提供 runtime leakage signal；不改写 final response。 |
| `bridge_guided_dbox_style_guard` | Bridge-guided decomposition variant | 用 bridge signal 引导 DBox-style response；仍是 guard-instrumented。 |
| `bridge_contract_compact_guard` | Bridge Contract compact + guard-instrumented method | 使用 compact bridge contract 和 guard signal；Guard-only 不是 rewrite condition。 |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard/Repair method | 学生可见回复可能来自 Repair；主均值只能说明 condition-level trend。 |

所有 conditions 都是 offline evaluation harnesses，不是线上默认 AIChat system。

Coach A 和 Coach B 各自完成了 350 条回复的全量盲评。Reviewer 阅读题目上下文、case-specific rubric、近期对话、学生问题和 candidate response，然后填写 primary metrics、diagnostic metrics 和 reliability fields。Coach A、Coach B 和 priority60 adjudication 是 expert reference / adjudicated sensitivity views，不是 gold。

Primary metrics 包括 `overall_quality`、`student_ready_pass`、`safe_ready_pass`、`critical_leakage_label`、`scaffold_sufficiency` 和 `student_response_burden`。论文按证据类别组织：main result、sensitivity、slice analysis、paired uncertainty、stress test、fairness sensitivity 和 calibration。

## 5. Results

### 5.1 Human Review Reliability

Dialogue-state v3 包含 50 条 reviewed candidate cases、7 个匿名 tutoring-harness conditions 和 350 条 AI responses。Coach A 和 Coach B 都完成了全部 350 条盲评。Overall-quality exact agreement 是 0.2829，within-1 agreement 是 0.8429。Leakage-label exact agreement 是 0.6714。Critical-binary exact agreement 是 0.9029，但 kappa 是 0.2511。Rank preference 分歧更大，top-1 和 last-place agreement 都是 10/50。

我们裁决了 60 条高优先级分歧：`use_A=29`、`use_B=9`、`new_label=22`。这说明不能把任一教练标签称为 gold，student-ready、safe-ready 和 rank 是 rater-sensitive outcomes。因此，论文同时报告 primary view、paired uncertainty、slice analysis 和 rater-view sensitivity。

### 5.2 Main Scaffold Evaluation

主结果只使用 31-case `main_scaffold_eval` slice。`priority60 adjudicated + Coach A` 主口径指标如下：

| condition | overall | student-ready | safe-ready | major+answer leakage |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.032 | 7/31 | 7/31 | 9 |
| `codehelp_codeaid_clean` | 3.710 | 19/31 | 19/31 | 2 |
| `dbox_inspired_clean` | 3.774 | 21/31 | 21/31 | 2 |
| `dbox_inspired_guard` | 3.774 | 23/31 | 23/31 | 2 |
| `bridge_guided_dbox_style_guard` | 3.742 | 20/31 | 20/31 | 2 |
| `bridge_contract_compact_guard` | 4.000 | 23/31 | 23/31 | 0 |
| `bridge_contract_compact_guard_repair` | 4.065 | 22/31 | 22/31 | 0 |

`bridge_contract_compact_guard_repair` 在主口径下 overall 最高，两个 Bridge Contract compact 条件都没有 major+answer leakage。同时，`dbox_inspired_guard` 达到 23/31 student-ready 和 safe-ready，接近或持平 Bridge Contract compact guard。因此，该结果应写成 quality-safety-burden trade-off：Bridge Contract compact + Guard/Repair 呈现有利的 overall 和 high-severity leakage-control trend，而 DBox-inspired decomposition 仍是强 baseline。

`codehelp_codeaid_clean` 明显强于 `enhanced_prompt_only_clean`，但仍有 2 条 major+answer leakage。这支撑 critical bridge leakage 的核心动机：不直接给代码或完整题解，并不能防止提前补完学生当前 missing bridge。

### 5.3 Paired Uncertainty

Same-case paired comparisons 限制了 claim 强度。`bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` 的 mean overall delta 是 +0.290，W/T/L 为 14/10/7，并少 2 条 major+answer leakage；但 paired bootstrap 95% CI 是 [-0.097, +0.645]，paired permutation p=0.2016。这支持 favorable trend / trade-off wording，不支持 significant dominance。

`bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` 的 mean overall delta 是 +0.065，W/T/L 为 7/18/6，major+answer leakage 相同。因此，主实验 condition 均值本身不能建立 Repair 因果效果。

`codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` 的 mean overall delta 是 +0.677，95% CI 为 [+0.258, +1.065]，paired p=0.0046，并多 12 条 safe-ready、少 7 条 major+answer leakage。Prompt-only 在 dialogue-state CP tutoring 中不够稳定，但 no-direct-solution 仍不是 safety-complete。

### 5.4 Slice and Sensitivity Analysis

All-50 sensitivity 显示 `bridge_contract_compact_guard_repair` 在 Coach A only、Coach B only、priority60+CoachA 和 priority60+CoachB 四种口径下 overall 都最高，但该平均混合了不同 paper use 的 slices，因此只能作为补充 robustness。Main scaffold slice 展现相对一致的 overall trend。Student-ready、safe-ready 和 rank 对评分者严格程度更敏感。论文不应依赖单一 rater view。

### 5.5 Observed Error Taxonomy

Observed error taxonomy 使用 `general tutoring failure type x operational cognitive bridge family x surface anchor`。Level 1 包括 critical bridge leakage、answer/code leakage、over-complete micro-example、wrong/shifted focus、under-scaffolded、excessive burden、context misalignment、over-safe refusal、factual/algorithmic error 和 policy/direct-answer handling failure。Level 2 包括 representation semantics、transition/action mapping、predicate/decision semantics、ordering/dependency control、modeling relation、aggregation/contribution accounting、data-structure operation mapping、correctness/invariant reasoning、implementation boundary、debugging evidence 和 policy-request handling。DP state、binary-search check、lazy propagation、tree difference、local code、greedy proof 和 debugging trace 是 Level 3 surface anchors。

因此，taxonomy 不是具体算法场景列表。它是 observed operational taxonomy，不是 universal taxonomy。

### 5.6 Repair and DBox+Repair Sensitivity

Repair 因果证据来自 30-pair same-candidate before/after stress test。Repair 在 16/30 pairs 中改善 leakage severity，14/30 保持不变，0/30 变差。Major leakage 从 7/30 降到 0/30，mean overall 从 3.367 上升到 3.633。代价是 student burden：burden improved / same / worsened 为 2/16/12。

DBox+Repair targeted fairness add-on 覆盖 20 条 headline-sensitive cases，不是 full 50-case double-coach main experiment。DBox+Repair overall 为 3.55，safe-ready 为 11/20，no/minor/major+answer leakage 为 14/6/0。相对同 case DBox Guard subset，它 modestly improves overall by +0.15，并把 major+answer leakage 从 2 降到 0。相对同 20 cases 的 Bridge Contract compact + Guard/Repair，Bridge+Repair 仍高 +0.50 overall，W/T/L 为 12/5/3，并多 4 条 safe-ready。

这些结果支持 Repair 在 fixed-candidate stress testing 中作为 leakage-reduction intervention，也说明 Repair 可帮助 DBox-inspired baseline。但它同时带来 burden trade-off，且 DBox+Repair 仍只是 sensitivity evidence。

### 5.7 DeepSeek LLM Grader Calibration

LLM grader calibration 只评估自动 grader 是否可作为 scalable auxiliary signals。论文主 calibration 使用 DeepSeek `deepseek-v4-flash`，关闭 thinking。

在 priority60 reference 上，case-specific bridge-rubric judge 相比 generic rubric 改善了一些辅助指标：leakage-label accuracy 为 0.617 vs 0.583，student-ready agreement 为 0.467 vs 0.433，safe-ready agreement 为 0.533 vs 0.400。安全关键指标仍不可接受：generic 和 case-specific DeepSeek graders 的 critical recall 都是 0，major leakage false-negative rate 都是 1.000。

因此，LLM grader 不能替代 human review 或 adjudication。Kimi-backed calibration 只保留为 exploratory/tooling record，因为它使用不同 backend 且显示 backend sensitivity。

## 6. Discussion

CP-MissingBridgeBench 的主贡献不是证明某个 harness 是 absolute winner。它让 missing bridges 和 critical bridge leakage 变成明确、可标注、可复核的评测对象。当前 evidence package 显示：prompt-only 不稳定；no-direct-solution 不等于 no critical bridge leakage；DBox-inspired decomposition 是强 baseline；Bridge Contract compact + Guard/Repair 在主人工评审口径下呈现有利的 overall-quality 和 high-severity leakage-control trend。

“不要给答案或代码”对 tutoring 来说太粗。Tutor 可以避免 full code 和 final answer，却仍然透露学生本应推导的 intermediate reasoning bridge。CP-MissingBridgeBench 通过 case-specific rubric 捕捉这个风险，区分 helpful scaffolding 和 premature bridge completion。

Guard-only conditions 在当前主实验中是 instrumentation / runtime signal。当 Leakage Judge 返回 `rewrite` 时，它不改变 `final_response_text`；只有 `block` 会触发 fallback，而本轮 main run 中 block=0。因此，Guard-only 不应被描述为 fixing final outputs。

Repair 可以被描述为由 same-candidate stress evidence 支持的 leakage-reduction intervention，但不能被写成由 main-experiment condition means 单独证明的因果效果。它降低 leakage severity，但经常增加 student burden。

本研究有明确限制。第一，50-case set 是 high-risk dialogue-state CP tutoring evidence candidate，不是 full CP tutoring coverage。第二，student-ready、safe-ready 和 rank 对评分者严格程度敏感。第三，priority60 adjudication 不是 gold；它只是降低高优先级分歧的不确定性。第四，DBox+Repair 是 20-case targeted sensitivity add-on，不是 full main condition。第五，DeepSeek-backed LLM grader 有较高 critical false-negative risk，不能替代人审。

## 7. Conclusion

本文认为，算法竞赛辅导需要比 direct answer / code leakage 更细的评测对象。核心教学风险往往是局部的：Tutor 可以不泄露最终答案，却仍然补完学生当前的 missing bridge。CP-MissingBridgeBench 通过 case-specific rubric、人类评审和 evidence-class reporting，让这个风险变成可审计的评测对象。

当前贡献是一个用于研究 missing-bridge preservation 的可复核 evaluation framework 和 evidence package，而不是宣称某个 tutor harness 已经完整解决算法竞赛辅导。后续工作应扩展 benchmark 的题型、学生状态和真实对话分布；对 rater-sensitive outcomes 做更充分的多评审裁决；在必要时补全 repair-enabled baseline comparison；并改进 critical bridge leakage 的自动评审，同时不能把自动评审当成 gold。

## Reproducibility Checklist

投稿前运行：

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_submission.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
```

证据链记录在 `dialogue_state_v3_evidence_manifest_20260518.json`。
