# CP-MissingBridgeBench: EAIT-Facing Manuscript Draft v0.2

## 使用边界

本文档在 `paper_submission_manuscript_dialogue_state_v3_eait_v0_1.zh.md` 基础上，叠加 `dynamic_writing_skill_eait_cp_missingbridgebench_recent_20260519.md` 的 recent EAIT corpus 写作规则，形成 Education and Information Technologies 面向的中文论文初稿 v0.2。它不新增实验、不新增 citation、不修改任何实验数字、不改变 evidence class，也不修改线上 AIChat、active mode、prompt 或主实验数据。本文是 evaluation framework / benchmark paper 草稿，不是线上部署系统论文。

## Abstract

Large language models are increasingly used as programming tutors, but pedagogically useful help is not captured by direct-answer avoidance alone. In competitive programming, students often need support before completing a local reasoning bridge; if the tutor completes that bridge too early, learning can be undermined even without final code or a full solution. We introduce CP-MissingBridgeBench, a turn-level evaluation framework for missing-bridge scaffolding and critical-bridge leakage in LLM tutoring. Each case combines problem context, recent dialogue, a student message, and a case-specific rubric that defines success criteria, forbidden content, acceptable reveal, and expected next student action. The dialogue-state v3 evidence package contains 50 reviewed candidate cases, 7 anonymized offline tutoring harnesses, and 350 AI responses evaluated through expert blind review, priority adjudication, paired uncertainty analysis, slice analysis, Repair stress testing, DBox+Repair fairness sensitivity, and DeepSeek-backed LLM-grader calibration. Main claims are restricted to the 31-case `main_scaffold_eval` slice. Under the primary human-review view, the benchmark reveals quality-safety-burden trade-offs: DBox-inspired decomposition is a strong baseline, no-direct-solution prompting does not eliminate critical bridge leakage, and Bridge Contract compact + Guard/Repair shows favorable but bounded overall-quality and high-severity leakage-control trends. Sensitivity, stress, and calibration analyses are supporting evidence, not main-result substitutes. Human review remains necessary for high-risk bridge-leakage judgment.

## 1. Introduction

Students need help before completing a reasoning bridge, but premature completion undermines learning. 这不是一个简单的“给不给答案”问题。对正在解题的学生来说，合格 tutor 需要提供足够的提示、澄清和下一步行动支持；但如果 tutor 直接替学生跨过当前最关键的中间推理，学习活动就可能从主动建构变成被动接收。

算法竞赛辅导把这种张力放大了。学生的问题往往很短，近期对话、局部代码和题目约束中却包含丰富状态：学生可能已经理解题意，但尚未说清状态含义；可能已经想到二分，但还没有形成 check 谓词；也可能在调试时缺少能定位错误的证据。一个回复即使没有给最终代码，也可能通过过完整的提示、微型例子或反问，提前说穿学生本应自己推出的关键桥梁。

本文将学生当前理解与下一步有效解题动作之间尚未跨过的局部推理称为 missing bridge。Critical bridge leakage 指 tutor 没有直接给完整题解或代码，却提前补完了当前 missing bridge。它不同于普通 answer leakage：一个回复可以不泄露最终答案，但仍然泄露最关键的中间推理；也可以提供背景、轻提示或聚焦问题，而不越过学生应当完成的桥梁。

因此，评估 LLM tutor 不能只问“有没有直接给答案”。更适合 turn-level tutoring 的问题是：回复是否贴合学生当前状态，是否帮助学生迈出下一步，是否避免过早完成当前 missing bridge，以及是否把下一轮学生行动控制在合理负担内。这个评价任务需要 case-specific human judgment，因为同一句提示在不同题目、不同学生状态和不同对话阶段中可能具有不同教学含义。

本文提出 CP-MissingBridgeBench，一个面向算法竞赛 LLM Tutor 的 turn-level 评测框架。每条 case 包含题目上下文、近期对话、学生当前问题和 case-specific rubric。Rubric 明确 success criteria、forbidden content、critical bridge boundary、acceptable reveal 和 expected student next action，使评审者能够围绕当前教学目标评价回复，而不是只凭泛泛的“像不像好老师”打分。

Dialogue-state v3 evidence package 包含 50 个 reviewed candidate cases、7 个匿名 offline tutoring harness conditions 和 350 条 AI responses。两位教练完成全量盲评，并配套 priority adjudication、paired uncertainty、slice analysis、Repair same-candidate stress test、DBox+Repair fairness sensitivity 和 DeepSeek LLM-grader calibration。主 headline 只使用 31-case `main_scaffold_eval` slice；all-50 aggregate、非主 slice、stress test 和 calibration 均按其 evidence class 报告。

本文贡献有三点。第一，提出 missing bridge 和 critical bridge leakage 作为算法竞赛 LLM tutor 的可标注评测对象。第二，构建 case-specific human-review workflow，将质量、安全、学生负担、泄露边界和评分者敏感性放入同一评测协议。第三，在 dialogue-state v3 evidence package 上报告有边界的实证结果：CP-MissingBridgeBench 揭示 quality-safety-burden trade-offs；DBox-inspired decomposition 是 strong baseline；Bridge Contract compact + Guard/Repair 在 primary human-review view 下呈现 favorable overall-quality 和 high-severity leakage-control trends，但不能解释为显著全面胜出或线上部署验证。

## 2. Related Work

### 2.1 AI Tutoring / ITS For Programming

AI tutoring / intelligent tutoring systems for programming 关注如何用系统化反馈、学生模型和交互式脚手架支持编程学习。这类工作为本文提供了教育技术背景：tutor 的价值不只在于给出正确答案，还在于根据学生当前理解提供适当支持。CP-MissingBridgeBench 延续这一教育目标，但把评测单位压缩到算法竞赛逐轮对话中的局部 missing bridge，并把“帮助学生继续推理”和“提前替学生完成推理”的边界显式化。

### 2.2 LLM Feedback And Scaffolding

LLM feedback and scaffolding 相关工作说明，生成式模型可以生成大量、及时、形式多样的反馈，但 AI feedback 与教师反馈并不等价。对编程学习尤其如此：同一段反馈可能同时具有提示、解释、纠错和答案接近效应。本文沿用这种谨慎立场：LLM tutor 的回复不能只按流畅度、礼貌程度或信息量评价，而要看它是否保留学生应完成的认知工作。No-direct-answer 或 no-direct-code 规则是必要约束，但不足以判断脚手架是否教学上安全。

### 2.3 Rubric-Based Expert Evaluation

Rubric-based expert evaluation 相关工作强调，开放式教育任务往往需要明确 rubric、专家判断和可靠性报告。CP-MissingBridgeBench 的 case-specific rubric 正是为此设计：每条 case 在评分前定义 success criteria、forbidden content、acceptable reveal 和 expected student next action。Coach A/B 评审与 priority60 adjudication 被报告为 expert reference views 和 rater-sensitivity evidence，而不是 final gold。

### 2.4 LLM Graders And Calibration

LLM graders and calibration 相关工作为开放式回复评测提供了可扩展路径，但本文不把自动评分视为人类教练的替代。DeepSeek-backed LLM grader calibration 只作为 auxiliary-grader calibration：case-specific rubric 可以改善部分辅助信号，但 priority60 critical recall 为 0、major leakage false-negative rate 为 1.000，说明 critical bridge leakage 的高风险判断仍需人类评审和裁决。

### 2.5 Algorithmic-Programming Scaffolding And Benchmarks

Algorithmic-programming scaffolding and benchmarks 为本文提供了更接近的领域参照。DBox-inspired decomposition 被用作 strong baseline，但本文不声称复现 DBox 的交互式、多轮、step-tree 系统；MRBench 类 pedagogical benchmark 说明 tutor evaluation 可以围绕教育维度与人类标注组织。更广义的算法编程评测与泄露鲁棒性问题也提醒我们，任务完成、最终答案泄露和教学中间桥梁泄露需要分开定义。CP-MissingBridgeBench 的定位是 CP-specific bridge / leakage benchmark，而不是通用 tutoring taxonomy、完整线上 tutor 系统或 final-answer leakage robustness benchmark。

## 3. Methods / Evaluation

### 3.1 Benchmark Construct

CP-MissingBridgeBench 评估的是算法竞赛逐轮辅导中的 missing bridge preservation 与 critical bridge leakage control。Missing bridge 是学生当前还没有跨过去、但完成下一步解题动作所必需的认知桥。它不是固定算法标签，而是当前学生状态下的局部推理缺口。

Critical bridge leakage 指 tutor 没有直接给完整代码或完整题解，却提前替学生说穿了本应由学生自己推出的关键中间推理。合格辅导可以提供上下文、澄清、轻提示、检查问题或低负担下一步；泄露风险来自过早完成当前 missing bridge。

本文使用三层 taxonomy 解释错误：

```text
cognitive bridge family + leakage mechanism + surface anchor
```

其中 cognitive bridge family 表示可迁移的认知桥类型，leakage mechanism 表示泄露方式，surface anchor 表示它在具体算法语境中的表面实例。本文不把 taxonomy 写成 universal CP tutoring taxonomy，也不把具体算法场景当作 taxonomy 本体。

### 3.2 Dialogue-State v3 Cases And Slices

Dialogue-state v3 包含 50 个 reviewed candidate cases。每个 case 保留题目上下文、近期对话、学生当前问题和 case-specific rubric，而不是只给孤立题目与单句问题。50 cases 按论文用途分为：

| slice | case_n | paper use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | 主脚手架质量、泄露和学生负担比较 |
| `main_eval_with_caution` | 5 | sensitivity / appendix |
| `clarification_safety_slice` | 10 | 澄清、不脑补和上下文不足时的安全询问 |
| `policy_safety_slice` | 4 | 学生直接要答案/代码时的安全重定向 |

主 headline 只使用 `main_scaffold_eval`。`main_eval_with_caution`、`clarification_safety_slice`、`policy_safety_slice` 和 all-50 aggregate 只作为 sensitivity / appendix evidence。这个 slice hierarchy 是本文避免把不同教学情境混成单一 headline 的主要方法。

### 3.3 Offline Human-Review Harnesses

主 human review 比较 7 个匿名 condition，共 350 条回复。教练盲评时不看 condition 名称。解盲后的 condition 解释边界如下：

| condition | role | interpretation boundary |
| --- | --- | --- |
| `enhanced_prompt_only_clean` | strong prompt-only baseline | 强教学提示词 baseline，不含 case-specific Bridge Contract。 |
| `codehelp_codeaid_clean` | no-direct-solution programming-help baseline | 检验“不直接给代码/题解”是否足以避免 critical bridge leakage。 |
| `dbox_inspired_clean` | literature-inspired decomposition baseline | DBox-inspired 单轮分解式脚手架，不声称复现 DBox。 |
| `dbox_inspired_guard` | DBox-inspired + guard-instrumented variant | Guard-only 在当前主实验中主要提供 runtime leakage signal，不改写最终回复。 |
| `bridge_guided_dbox_style_guard` | bridge-guided decomposition variant | 用 bridge signal 引导 DBox-style 回复；仍是 guard-instrumented 条件。 |
| `bridge_contract_compact_guard` | Bridge Contract compact + guard-instrumented method | 使用 compact bridge contract 和 guard signal；Guard-only 不是 rewrite condition。 |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard/Repair method | 学生可见回复可来自 Repair stage；主实验均值说明 condition-level trend，不单独证明 Repair 因果。 |

这些 condition 都是 offline evaluation harness，不等于线上默认 AIChat，也不表示线上 active mode 已接入这些模块。本文把它们作为教育技术评价对象，而不是部署配置说明。

### 3.4 Case-Specific Rubric And Blind Review

每条 case 在评分前先固定 case-specific rubric，至少包含 `success_criteria`、`forbidden_content`、`critical_bridge_boundary`、`acceptable_reveal` 和 `expected_student_next_action`。这个设计使评审不是按泛泛偏好打分，而是按当前学生状态、题目上下文和本轮教学目标评价回复。

Coach A 和 Coach B 都完成了 350 条全量盲评。评分流程包括阅读题目上下文、case-specific rubric、近期对话、学生当前问题和待评分回复，然后填写主指标、诊断指标和可靠性字段。对 major / answer leakage、`show=no`、`overall_quality<=2`、同题排序第一或最后、低置信度和需要讨论的样本，评审填写强制备注。

Coach A、Coach B 和 priority60 adjudication 都是 expert reference / adjudicated sensitivity views，不能称为 final gold。A/B disagreement 被视为 pedagogical judgment 的真实敏感性；论文通过双评、priority adjudication、slice analysis 和 sensitivity analysis 报告这种不确定性。

### 3.5 Metrics

主指标包括：

| metric | role |
| --- | --- |
| `overall_quality` | 1-5 总体辅导质量判断 |
| `student_ready_pass` | 综合判断是否愿意给学生看 |
| `safe_ready_pass` | 安全与可用性门槛 |
| `critical_leakage_label` | `no_leakage` / `minor_bridge_leakage` / `major_bridge_leakage` / `answer_leakage` |
| `scaffold_sufficiency` | 防止“安全但没帮助” |
| `student_response_burden` | 学生下一轮需要付出的输入和推理负担 |

诊断指标用于解释错误和校准 LLM grader，不作为唯一胜负依据。配对比较报告 win/tie/loss、mean delta、safe-ready delta、major+answer leakage delta 和 uncertainty。

### 3.6 Analysis Hierarchy And Evidence Manifest

论文结果按 evidence class 组织：

| evidence class | use |
| --- | --- |
| main result | `main_scaffold_eval` + priority60 adjudicated + Coach A 主口径 |
| sensitivity | Coach A only、Coach B only、priority60 + Coach A、priority60 + Coach B、all-case appendix |
| slice analysis | main scaffold、caution、clarification safety、policy safety 分开报告 |
| paired uncertainty | 同 case 条件比较的 W/T/L、mean delta、bootstrap CI 和 permutation test |
| stress test | Repair same-candidate before/after 因果压力测试 |
| fairness sensitivity | DBox+Repair 20-case targeted add-on |
| calibration | DeepSeek LLM grader calibration，作为 auxiliary grader 评估 |

主证据链由 `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`、`evals/aichat/reproduce_dialogue_state_v3_tables.py` 和 `evals/aichat/verify_dialogue_state_v3_reports.py` 固定。本文不把 sensitivity、stress 或 calibration 写成 main result。

## 4. Results

本节显式区分 evidence class：`main_scaffold_eval` + priority60 adjudicated + Coach A 是 main result；rater views、all-case aggregate 和非主 slices 是 sensitivity / appendix evidence；Repair same-candidate before/after review 是 stress test；DBox+Repair 是 20-case fairness sensitivity add-on；DeepSeek LLM grader calibration 是 auxiliary-grader calibration，不替代 human review。

### 4.1 Human Review Reliability

Dialogue-state v3 包含 50 个 reviewed candidate cases、7 个匿名 tutoring harness conditions 和 350 条 AI 回复。两位教练均完成 350 条全量盲评。Coach A/B 的 overall exact agreement 为 0.2829，但 within-1 agreement 达到 0.8429；leakage-label exact agreement 为 0.6714；critical-binary exact agreement 为 0.9029，但 kappa 只有 0.2511。rank agreement 也较弱，top-1 与 last-place agreement 均为 10/50。

对 60 条高优先级分歧进行 priority adjudication，其中 `use_A=29`、`use_B=9`、`new_label=22`。这表明任一单独教练评分都不应被视为 final gold，也说明 pedagogical judgment 在 student-ready、safe-ready 和 rank preference 上具有 rater sensitivity。因此后续结果同时报告 priority adjudication、slice analysis、paired uncertainty 和 rater-view sensitivity。

### 4.2 Main Scaffold Evaluation On 31 Cases

主结果使用 `main_scaffold_eval` 31 cases 和 `priority60 adjudicated + Coach A` 主口径，而不是把 clarification / policy safety cases 混入 headline。表 1 总结了主 slice 的主要指标。

| condition | overall | student-ready | safe-ready | major+answer leakage |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.032 | 7/31 | 7/31 | 9 |
| `codehelp_codeaid_clean` | 3.710 | 19/31 | 19/31 | 2 |
| `dbox_inspired_clean` | 3.774 | 21/31 | 21/31 | 2 |
| `dbox_inspired_guard` | 3.774 | 23/31 | 23/31 | 2 |
| `bridge_guided_dbox_style_guard` | 3.742 | 20/31 | 20/31 | 2 |
| `bridge_contract_compact_guard` | 4.000 | 23/31 | 23/31 | 0 |
| `bridge_contract_compact_guard_repair` | 4.065 | 22/31 | 22/31 | 0 |

`bridge_contract_compact_guard_repair` 在该 slice 上 overall 最高，两个 Bridge Contract compact variants 的 major+answer leakage 均为 0。这个结果应解释为 favorable but bounded trend。DBox-inspired decomposition 仍是 strong baseline：`dbox_inspired_guard` 在 student-ready 和 safe-ready counts 上接近 Bridge Contract compact。本文因此报告 quality-safety-burden trade-off，而不是单一 harness 的胜利。

`codehelp_codeaid_clean` 相比 `enhanced_prompt_only_clean` 的结果也支持核心动机：no-direct-code / no-direct-solution baseline 明显强于 prompt-only，但在该 slice 上仍有 2 条 major+answer leakage。避免直接答案或代码并不足以避免 premature completion of the student's missing bridge。

### 4.3 Pairwise Uncertainty And Sensitivity

Same-case paired comparisons 限制了 headline 的强度。`bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` 的 mean overall delta 为 +0.290，W/T/L 为 14/10/7，并少 2 条 major+answer leakage；但 paired bootstrap 95% CI 为 [-0.097, +0.645]，paired permutation p=0.2016。因此该比较支持 trend-level trade-off advantage，不支持 strong statistical superiority claim。

`bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` 的 mean overall delta 为 +0.065，W/T/L 为 7/18/6，major+answer leakage 相同。主实验 condition comparison 本身不能建立 Repair 的因果效果。

相比之下，`codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` 的 mean overall delta 为 +0.677，95% CI 为 [+0.258, +1.065]，paired p=0.0046，safe-ready 多 12 条，major+answer leakage 少 7 条。这支持 prompt-only 不是 dialogue-state CP tutoring 中稳定上界的结论。

All-case sensitivity analysis 显示，`bridge_contract_compact_guard_repair` 在 Coach A only、Coach B only、priority60+CoachA 和 priority60+CoachB 下 overall score 最高。但 all-case averages 混合 main scaffold、clarification 和 policy slices，因此只作为 supplemental robustness 报告。Student-ready、safe-ready 和 rank 仍受 rater strictness 影响。

### 4.4 Observed Error Taxonomy

Observed error taxonomy 不是具体算法列表，而是：

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

General failure types 包括 critical bridge leakage、answer/code leakage、over-complete micro-examples、shifted focus、under-scaffolding、excessive burden、context misalignment、over-safe refusal、factual/algorithmic error 和 policy/direct-answer handling failure。Operational cognitive bridge families 包括 representation semantics、transition/action mapping、predicate/decision semantics、ordering/dependency control、modeling relation、aggregation/contribution accounting、data-structure operation mapping、correctness/invariant reasoning、implementation boundary、debugging evidence 和 policy-request handling。DP state、binary-search check、lazy propagation、tree difference、local code、greedy proof 和 debugging trace 是 surface anchors，不是 taxonomy 本体。

这个 taxonomy 支持论文把错误解释提升到 operational cognitive bridge family 和 leakage mechanism 层面，同时保持覆盖边界：50-case set 是 observed high-risk CP tutoring evidence candidate，不是 universal CP tutoring coverage。

### 4.5 Repair Stress And DBox+Repair Fairness

Repair evidence 与主实验 condition means 分开报告。因为主实验比较的是不同 condition 输出，它不能单独证明 Repair 对同一个 candidate 的因果改善。30-pair same-candidate before/after stress test 固定同一原始 candidate，并盲化比较 before_repair 与 after_repair。Repair improves leakage severity in 16/30 pairs, preserves it in 14/30, and worsens it in 0/30。Major leakage 从 7/30 降至 0/30。Overall 从 3.367 增至 3.633，mean delta 为 +0.267。Burden trade-off 为 burden improved / same / worsened = 2/16/12。

DBox+Repair fairness 是 targeted 20-case sensitivity add-on，不是新的 main condition。`dbox_inspired_guard_repair` 的 overall 为 3.55，safe-ready 为 11/20，no/minor/major+answer leakage 为 14/6/0。相对于 same-case DBox Guard subset，它 modestly improves overall (+0.15, W/T/L=6/9/5) 并将 major+answer leakage 从 2 降至 0。相对于同 20 cases 上的 Bridge Contract compact + Guard/Repair，Bridge+Repair 保持 +0.50 overall，W/T/L=12/5/3，safe-ready +4。

这些结果支持 Repair 作为 leakage-reduction intervention 的 same-candidate stress evidence，并显示 student-burden trade-off。它们不把 DBox+Repair 升格为 full main condition，也不证明 Bridge superiority over every repair-enabled baseline。

### 4.6 LLM Grader Calibration

LLM grader calibration 只用于评估 automatic graders 是否能提供 auxiliary low-stakes signals。Paper-facing calibration 使用 DeepSeek `deepseek-v4-flash` with thinking disabled，与主实验的 offline judge stack 对齐。由于 tutor generation、judge/guard 和 repair 都位于 fixed DeepSeek-family offline stack，这个 calibration 存在 same-backend coupling，不能解释为 cross-backend validation。

在 priority60 reference 上，DeepSeek case-specific bridge-rubric judge 相比 generic rubric 改善了部分辅助指标：leakage-label accuracy 为 0.617 vs 0.583，student-ready agreement 为 0.467 vs 0.433，safe-ready agreement 为 0.533 vs 0.400。但 generic 和 case-specific DeepSeek graders 的 critical recall 都是 0，major leakage false-negative rate 都是 1.000。Automatic grader 没能找回人类裁决为 `major_bridge_leakage` / `answer_leakage` 的 rows。

因此，case-specific bridge rubrics 可以改善部分 auxiliary automatic-grading signals，但 DeepSeek-backed LLM graders 不足以承担 high-stakes critical-bridge leakage evaluation。Human review and adjudication remain necessary。Earlier Kimi-backed outputs 只作为 exploratory/tooling evidence，说明 backend sensitivity；cross-backend grader calibration 是 future work 或 revision add-on，而不是当前证据的静默替换。

## 5. Discussion

### 5.1 No-Direct-Answer Rules Are Insufficient

CP-MissingBridgeBench 的核心教育技术启示是：direct-answer avoidance 不是 turn-level tutoring safety 的充分条件。一个回复可以不提供最终代码或完整题解，却仍然提前揭示当前最关键的状态语义、转移来源、谓词含义、更新规则、正确性证据或调试定位线索。对算法竞赛学习而言，这些中间推理往往正是学生需要自己跨过的 bridge。

因此，AI tutoring evaluation 需要从“是否给答案”转向“是否保留适当的学生推理空间”。这并不意味着 tutor 应该少帮助学生；相反，合格回复应当提供足够且贴合的脚手架，同时避免替学生完成当前 missing bridge。

### 5.2 Critical Bridge Leakage Requires Case-Specific Human Judgment

Critical bridge leakage 依赖当前题目、近期对话、学生已经说出的理解和本轮教学目标。没有 case-specific rubric，很难判断某条信息是合格提示、必要背景、可接受揭示，还是 premature bridge completion。本文的 human-review protocol 把 success criteria、forbidden content、acceptable reveal 和 expected student next action 固定在 case 层面，使评审可以围绕当前学生状态作出判断。

Coach A/B disagreement 也说明这类判断本身具有 rater sensitivity。本文不把这种差异隐藏为噪声，也不把任一教练或 priority60 adjudication 称为 final gold；相反，论文把 reliability、priority adjudication、slice analysis 和 sensitivity views 作为结果解释的一部分。

### 5.3 Repair Is Promising But Burden-Bearing

Guard-only variants 在当前 pipeline 中是 guard-instrumented / guard-checked variants。它们暴露 leakage risk，但 rewrite signal 不替换 `final_response_text`，除非触发 block fallback。因此 Guard-only 结果不能被写成 final-response repair evidence。

Repair 的更直接证据来自 same-candidate stress test。该测试显示 Repair 可以降低 leakage severity，但 burden worsened 的情况也存在。教育技术上，这意味着自动修复不应只追求“少泄露”，还需要关注学生下一轮需要承担的输入负担、推理负担和行动清晰度。

### 5.4 LLM Graders Remain Auxiliary

LLM graders 对开放式教育回复评测有扩展价值，但 dialogue-state v3 的 calibration 表明，critical bridge leakage 这种高风险边界不能由当前 automatic grader 单独裁决。尤其在 priority60 reference 上，critical recall 为 0、major leakage false-negative rate 为 1.000，使自动评分更适合作为低风险辅助信号、筛查工具或未来改进对象，而不是替代人类教练。

对 EAIT 读者而言，这一点也提醒我们：教育技术系统的可扩展评估不能只依赖模型自评或同后端评分。对于影响学生推理机会的安全/教学边界，人类专家判断、rubric transparency 和 calibration reporting 仍然必要。

### 5.5 Practical Implications For Educational Technology Design

本文的设计启示不是“让 tutor 说得更少”，而是让 tutor 的帮助更可控。对算法竞赛辅导系统而言，帮助强度、桥梁边界、下一步行动和学生负担需要共同设计。Bridge Contract 类约束的价值在于把这些要素显式化，使生成、评审和修复都围绕同一个 case-specific tutoring target 运行。

同时，human review 不只是事后验收。它在本文中承担三个教育技术功能：界定 case-specific leakage boundary，识别 safe-but-unhelpful 与 helpful-but-leaky 的取舍，并校准 automatic grader 的低风险辅助用途。这种人机协作评估模式比单独依赖自动分数更适合 critical bridge leakage 这类高风险教学边界。

### 5.6 Limitations

第一，50-case set 是 high-risk CP tutoring evidence candidate，不是 exhaustive CP coverage。第二，student-ready、safe-ready 和 rank are rater-sensitive，因此论文必须报告 sensitivity views。第三，priority60 adjudication 不是 final gold；它降低高优先级分歧的不确定性，但不消除全部评分者差异。第四，DBox+Repair add-on 是 20-case targeted sensitivity review，不是 full 50-case double-coach add-on。第五，DeepSeek-backed LLM grader calibration 存在 high critical false-negative risk 和 same-backend coupling，automatic graders 不能替代 human review。第六，本文评估 offline tutoring harnesses，不验证线上默认 AIChat 或 active-mode deployment。

## 6. Conclusion

CP-MissingBridgeBench 将 missing-bridge preservation 和 critical bridge leakage 转化为可标注、可复核的教育技术评测对象。它关注的不是某个 tutor harness 是否“赢下”算法竞赛辅导，而是 LLM tutor 如何在 helpfulness、leakage control 和 student reasoning burden 之间形成取舍。

Dialogue-state v3 evidence package 支持一个有边界的结论：在 31-case `main_scaffold_eval` headline slice 上，DBox-inspired decomposition 是 strong baseline；no-direct-solution prompting 不能完全避免 critical bridge leakage；Bridge Contract compact + Guard/Repair 在 primary human-review view 下呈现 favorable overall-quality 和 high-severity leakage-control trends。但 paired uncertainty、rater sensitivity、Guard-only instrumentation boundary、Repair stress-test boundary、DBox+Repair fairness sensitivity 和 LLM-grader limitations 都必须同时报告。

本文不声称 50 cases 覆盖所有 CP tutoring，不把 Coach labels 或 priority60 adjudication 写成 final gold，不把 Guard-only 写成最终输出修复，不从主实验均值单独推出 Repair 因果，也不把 LLM grader 作为人类评审替代。当前贡献是一个可复核的 benchmark / evaluation framework，用于更精确地分析 LLM tutoring 如何在不替学生跨过 missing bridge 的前提下提供有效脚手架。

## 7. Ethics, Data Governance, And AI Writing Disclosure

本文草稿沿用 existing evidence package 的数据与复现边界。AI writing assistance 仅用于 drafting、editing、checklist generation 和 evidence organization；科学主张、引用、数字、数据边界和最终表述需要人类作者核验并负责。投稿前仍需依据目标 venue policy 检查 AI writing disclosure、privacy/data statements、citation verification log 和 result-number verification log。
