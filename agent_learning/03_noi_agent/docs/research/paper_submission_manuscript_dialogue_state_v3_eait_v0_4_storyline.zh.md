# CP-MissingBridgeBench: EAIT-Facing Manuscript Draft v0.4 Storyline

## 使用边界

本文档在 `paper_submission_manuscript_dialogue_state_v3_eait_v0_3_humanized.zh.md` 基础上重写故事线，目标是把稿件从“证据包说明书”推进为面向 Education and Information Technologies 的 educational-technology narrative。修改只涉及叙事顺序、段落衔接、示例解释和 citation placeholder；不新增实验、不新增正式 citation、不修改任何数字、不改变 evidence class，也不修改线上 AIChat、active mode、prompt 或主实验数据。

## Abstract

Programming tutors based on large language models can provide immediate and detailed help, but the educational problem is not only whether they avoid final answers. In competitive programming, a learner may ask for help while still missing a local reasoning bridge, such as the meaning of a DP state or the predicate in a binary-search check. If the tutor completes that bridge too early, the response can undermine learning even without giving code. CP-MissingBridgeBench addresses this gap by evaluating turn-level scaffolding and critical-bridge leakage with case-specific human review. The dialogue-state v3 evidence package contains 50 reviewed cases, 7 anonymized offline tutoring conditions, and 350 AI responses. Each case pairs problem context and recent dialogue with a rubric defining the missing bridge, forbidden content, acceptable reveal, and expected next student action. Main claims are restricted to the 31-case `main_scaffold_eval` slice. Under the primary human-review view, the benchmark shows a quality-safety-burden trade-off: DBox-inspired decomposition is a strong baseline; no-direct-solution prompting does not remove critical bridge leakage; and Bridge Contract compact + Guard/Repair shows favorable but bounded trends in overall quality and high-severity leakage control. Sensitivity, stress, and calibration analyses remain supporting evidence, and human review remains necessary for high-risk bridge-leakage judgment.

## 1. Introduction

Consider a competitive-programming tutoring dialogue in which a student says, “I know this may need binary search, but I do not know how to write `check(x)`.” A helpful tutor could ask what `x` represents, what condition should become easier or harder as `x` changes, and what evidence from the problem constraints should be tested. A less careful tutor might answer with the full monotonic predicate. That response may contain no final code, yet it has already crossed the bridge the student needed to build.

The same pattern appears in DP and graph problems. A student may have the transition formula almost in reach but still not know what the state should mean; or may be implementing LCA but not yet understand which ancestor relationship is being queried. At these moments, the best help is neither silence nor a complete explanation. It is a scaffold that makes the next step reachable while leaving the central reasoning step with the learner.

This is the tutoring tension addressed in this paper. Students often need help before they complete a reasoning bridge, but that is also when a tutor can most easily over-help. In programming tutoring, avoiding final code is therefore not enough. A response can obey a no-direct-code rule and still leak the critical intermediate idea by spelling out the predicate, state semantics, invariant, update rule, or debugging evidence that the student was supposed to infer.

We refer to the local, not-yet-crossed reasoning step as a missing bridge. Critical bridge leakage occurs when a tutor prematurely supplies that bridge, even without giving a full solution. This differs from ordinary answer leakage: a response may avoid the final answer while still revealing the decisive intermediate reasoning, or it may offer a small hint while preserving the student's work.

The evaluation problem is consequently case-specific. A hint that is acceptable after a student has already stated the monotonic predicate may be over-revealing before the student has identified it. A useful turn-level evaluation must therefore ask whether the response matches the student's current state, gives enough help for the next move, avoids completing the current missing bridge, and keeps the next student action manageable.

CP-MissingBridgeBench is designed around this problem. Each case contains the problem context, recent dialogue, current student message, and a rubric that specifies success criteria, forbidden content, the critical bridge boundary, acceptable reveal, and expected student next action. Expert reviewers are asked to evaluate the current pedagogical boundary, not merely whether the reply sounds clear or friendly.

The dialogue-state v3 evidence package contains 50 reviewed candidate cases, 7 anonymized offline tutoring harness conditions, and 350 AI responses. Two coaches completed blind review over the full set. The package also includes priority adjudication, paired uncertainty, slice analysis, a same-candidate Repair stress test, DBox+Repair fairness sensitivity, and DeepSeek LLM-grader calibration. The main headline is restricted to the 31-case `main_scaffold_eval` slice; all-50 aggregates, non-main slices, stress tests, and calibration analyses are reported only according to their evidence class.

The paper makes three bounded contributions. First, it frames missing-bridge preservation as an educational-technology evaluation problem for competitive-programming tutoring. Second, it provides a case-specific human-review workflow for judging quality, safety, student burden, leakage boundaries, and rater sensitivity together. Third, it reports dialogue-state v3 evidence showing quality-safety-burden trade-offs: DBox-inspired decomposition is a strong baseline, and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view. These results are not claims of significant comprehensive superiority or validation of an online deployed tutor.

## 2. Related Work

### 2.1 AI Tutoring / ITS For Programming

Work on AI tutoring and intelligent tutoring systems for programming has long treated feedback as more than correctness delivery. Programming tutors are valuable when they help learners interpret errors, organize concepts, and take the next productive step. This tradition gives CP-MissingBridgeBench its educational frame: the object of evaluation is not only response correctness, but the way a tutor shapes the learner's next reasoning move. 【占位：EAIT programming ITS / programming GenAI review】

The gap is at the turn level. Existing programming-tutor evaluations commonly operate at the level of systems, interventions, user experience, or learning outcomes. CP-MissingBridgeBench instead asks whether a single response preserves the student's current reasoning work in a competitive-programming dialogue.

### 2.2 LLM Feedback And Scaffolding

LLM feedback can be fluent, immediate, and richly detailed. Those same qualities create a risk in programming education: a response may appear supportive because it is clear and complete, while being too complete for the student's present state. In the binary-search vignette, the difference between asking the student to articulate the monotonic condition and giving the full predicate is small in wording but large pedagogically. 【占位：LLM feedback / adaptive feedback / teacher-feedback comparison】

The gap is the boundary of appropriate scaffolding. Prior work motivates AI feedback as a learning support, but CP-MissingBridgeBench evaluates whether support preserves the specific cognitive work that belongs to the student at that moment.

### 2.3 Rubric-Based Expert Evaluation

Open-ended educational feedback is difficult to evaluate without a rubric. In CP-MissingBridgeBench, each case fixes success criteria, forbidden content, acceptable reveal, and expected student next action before scoring begins. Coach A/B review and priority60 adjudication are therefore treated as expert reference views with sensitivity reporting, not as a single final gold label. 【占位：rubric validation / expert review / human annotation】

The gap is case-specific pedagogical judgment. Bridge leakage is not a surface feature of a response alone; it depends on what the student has already shown and what they should do next. The benchmark therefore makes human review part of the evaluation design rather than a post-hoc check.

### 2.4 LLM Graders And Calibration

Automatic graders may help scale review, but they cannot be assumed to handle high-risk pedagogical boundaries. In this evidence package, DeepSeek-backed calibration is used only as auxiliary-grader calibration. The case-specific bridge rubric improves some low-stakes signals, but priority60 critical recall remains 0 and the major leakage false-negative rate remains 1.000. 【占位：AI assessment support / LLM evaluator calibration】

The gap is reliability at the boundary that matters most. CP-MissingBridgeBench does not ask whether an LLM grader can produce a plausible score; it asks whether automatic grading can safely identify high-risk critical bridge leakage. The current evidence keeps that role auxiliary.

### 2.5 Algorithmic-Programming Scaffolding And Benchmarks

Algorithmic-programming scaffolding and benchmark work provides the closest technical context. DBox-inspired decomposition serves here as a strong baseline, but the paper does not claim to reproduce the full interactive, multi-turn, step-tree DBox system. MRBench-like pedagogical benchmark work also helps situate tutor evaluation around educational dimensions and human annotation. More broadly, programming benchmarks and leakage-robustness work make clear that task completion, final-answer leakage, and intermediate bridge leakage should be defined separately. 【占位：DBox / tutor evaluation taxonomy / CP benchmark / answer-leakage robustness】

The gap is the competitive-programming middle step. CP-MissingBridgeBench focuses on case-specific leakage of the student's missing reasoning bridge, not on general task completion, generic tutor quality, or final-answer disclosure alone.

## 3. Methods / Evaluation

### 3.1 Benchmark Construct

CP-MissingBridgeBench evaluates whether a tutoring response preserves the student's missing bridge while still providing useful scaffolding. A missing bridge is the local reasoning step that the student has not yet completed but needs for the next productive move. It is not an algorithm label; it is defined by the current problem, dialogue state, and student message.

As a running example, suppose the student has already suspected binary search but has not yet formulated `check(x)`. The missing bridge is not “binary search” itself. It is the monotonic predicate: what candidate `x` means, what property should be tested, and why the test becomes easier or harder as `x` changes. Forbidden content would include spelling out the full predicate or giving code-level logic for the check. Acceptable reveal might include asking the student to define what `x` stands for or to compare two candidate values. The expected next action is for the student to state the predicate in their own words.

Critical bridge leakage occurs when the tutor supplies that local reasoning step too early. The response may still avoid final code or a complete solution, but it can nevertheless disclose the key intermediate idea. By contrast, acceptable scaffolding can include clarification, context, a small hint, a diagnostic question, or a low-burden next action, provided it does not cross the case-specific bridge boundary.

Observed errors are organized with a three-part taxonomy:

```text
cognitive bridge family + leakage mechanism + surface anchor
```

The cognitive bridge family captures the transferable reasoning type, the leakage mechanism describes how the response over-reveals, and the surface anchor records the concrete algorithmic setting. The taxonomy is operational and observed within this benchmark; it is not presented as a universal taxonomy of competitive-programming tutoring.

### 3.2 Dialogue-State v3 Cases And Slices

Dialogue-state v3 contains 50 reviewed candidate cases. Each case keeps the problem context, recent dialogue, student message, and case-specific rubric together, so the response is judged against the actual tutoring situation rather than against an isolated problem statement. The running binary-search example illustrates why this matters: the same sentence about monotonicity may be a useful hint after the student has named the predicate, but a leakage case before that bridge has been crossed.

| slice | case_n | paper use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | 主脚手架质量、泄露和学生负担比较 |
| `main_eval_with_caution` | 5 | sensitivity / appendix |
| `clarification_safety_slice` | 10 | 澄清、不脑补和上下文不足时的安全询问 |
| `policy_safety_slice` | 4 | 学生直接要答案/代码时的安全重定向 |

The main headline uses only `main_scaffold_eval`. The other slices and the all-50 aggregate are treated as sensitivity or appendix evidence. This separation avoids mixing ordinary scaffolding, clarification safety, and direct-answer policy handling into one headline number.

### 3.3 Offline Human-Review Harnesses

The main human review compares 7 anonymized conditions and 350 responses. Coaches reviewed the responses blind to condition names. After unblinding, the conditions are interpreted as follows:

| condition | role | interpretation boundary |
| --- | --- | --- |
| `enhanced_prompt_only_clean` | strong prompt-only baseline | 强教学提示词 baseline，不含 case-specific Bridge Contract。 |
| `codehelp_codeaid_clean` | no-direct-solution programming-help baseline | 检验“不直接给代码/题解”是否足以避免 critical bridge leakage。 |
| `dbox_inspired_clean` | literature-inspired decomposition baseline | DBox-inspired 单轮分解式脚手架，不声称复现 DBox。 |
| `dbox_inspired_guard` | DBox-inspired + guard-instrumented variant | Guard-only 在当前主实验中主要提供 runtime leakage signal，不改写最终回复。 |
| `bridge_guided_dbox_style_guard` | bridge-guided decomposition variant | 用 bridge signal 引导 DBox-style 回复；仍是 guard-instrumented 条件。 |
| `bridge_contract_compact_guard` | Bridge Contract compact + guard-instrumented method | 使用 compact bridge contract 和 guard signal；Guard-only 不是 rewrite condition。 |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard/Repair method | 学生可见回复可来自 Repair stage；主实验均值说明 condition-level trend，不单独证明 Repair 因果。 |

These are offline evaluation harnesses, not online AIChat configurations and not evidence of active-mode deployment. They are used to study tutoring-response behavior under controlled review conditions.

### 3.4 Case-Specific Rubric And Blind Review

Each case is scored against a rubric fixed before review. The rubric includes `success_criteria`, `forbidden_content`, `critical_bridge_boundary`, `acceptable_reveal`, and `expected_student_next_action`. In the running example, the rubric would separate a legitimate prompt such as “what must become true as `x` increases?” from a forbidden response that gives the full check predicate. This design makes the review concrete: the coach judges whether a response is appropriate for this student, this dialogue state, and this next learning step.

Coach A and Coach B each reviewed all 350 responses. For every response, they saw the problem context, rubric, recent dialogue, student message, and candidate reply, then assigned main metrics, diagnostic labels, and reliability fields. Forced notes were required for major / answer leakage, `show=no`, `overall_quality<=2`, first or last rank within a case, low confidence, and samples needing discussion.

Coach A, Coach B, and priority60 adjudication are expert reference or adjudicated sensitivity views. None is treated as final gold. Disagreement is part of the evidence: it shows where pedagogical judgment is sensitive and where the paper must report uncertainty rather than a single definitive label.

### 3.5 Metrics

The main metrics are:

| metric | role |
| --- | --- |
| `overall_quality` | 1-5 总体辅导质量判断 |
| `student_ready_pass` | 综合判断是否愿意给学生看 |
| `safe_ready_pass` | 安全与可用性门槛 |
| `critical_leakage_label` | `no_leakage` / `minor_bridge_leakage` / `major_bridge_leakage` / `answer_leakage` |
| `scaffold_sufficiency` | 防止“安全但没帮助” |
| `student_response_burden` | 学生下一轮需要付出的输入和推理负担 |

Diagnostic metrics are used to explain failures and calibrate automatic graders. They are not used as the sole basis for condition ranking. Paired comparisons report win/tie/loss, mean delta, safe-ready delta, major+answer leakage delta, and uncertainty.

### 3.6 Analysis Hierarchy And Evidence Manifest

The analysis follows the evidence hierarchy below:

| evidence class | use |
| --- | --- |
| main result | `main_scaffold_eval` + priority60 adjudicated + Coach A 主口径 |
| sensitivity | Coach A only、Coach B only、priority60 + Coach A、priority60 + Coach B、all-case appendix |
| slice analysis | main scaffold、caution、clarification safety、policy safety 分开报告 |
| paired uncertainty | 同 case 条件比较的 W/T/L、mean delta、bootstrap CI 和 permutation test |
| stress test | Repair same-candidate before/after 因果压力测试 |
| fairness sensitivity | DBox+Repair 20-case targeted add-on |
| calibration | DeepSeek LLM grader calibration，作为 auxiliary grader 评估 |

The evidence chain is fixed by `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`, `evals/aichat/reproduce_dialogue_state_v3_tables.py`, and `evals/aichat/verify_dialogue_state_v3_reports.py`. Sensitivity, stress, and calibration results are not promoted to main results.

## 4. Results

The results follow the evaluation questions implied by the benchmark. The 31-case `main_scaffold_eval` slice under priority60 adjudicated + Coach A is the main result. Rater views, all-case aggregates, and non-main slices are sensitivity or appendix evidence. Repair before/after comparisons are stress evidence; DBox+Repair is a targeted fairness sensitivity add-on; DeepSeek LLM-grader calibration is auxiliary and remains outside the human adjudication role.

### 4.1 RQ1: How Stable Is Human Review For Critical-Bridge Judgments?

What we tested: We first examined whether expert review produces a single unambiguous view of response quality and leakage, or whether bridge-leakage judgment remains sensitive to rater perspective.

What we observed: Dialogue-state v3 includes 50 reviewed candidate cases, 7 anonymized tutoring harness conditions, and 350 AI responses. Both coaches reviewed all 350 responses. Overall exact agreement between Coach A and Coach B is 0.2829, while within-1 agreement is 0.8429. Leakage-label exact agreement is 0.6714. Critical-binary exact agreement is 0.9029, but kappa is 0.2511. Rank agreement is also limited, with top-1 and last-place agreement both at 10/50.

The priority adjudication set contains 60 high-priority disagreements: `use_A=29`, `use_B=9`, and `new_label=22`.

What this supports: These findings support the use of human review with explicit sensitivity reporting. They show that expert judgment is informative but not reducible to one unproblematic gold label.

What it does not support: These results do not justify treating Coach A, Coach B, or priority60 adjudication as final gold. They also do not remove the need to report uncertainty for student-ready, safe-ready, and ranking outcomes.

### 4.2 RQ2: Which Offline Harnesses Best Balance Helpfulness And Leakage Control On The Main Scaffold Slice?

What we tested: The headline evaluation compares the 7 anonymized conditions on the 31-case `main_scaffold_eval` slice under the `priority60 adjudicated + Coach A` view. Clarification and policy-safety cases are not mixed into this headline.

What we observed:

| condition | overall | student-ready | safe-ready | major+answer leakage |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.032 | 7/31 | 7/31 | 9 |
| `codehelp_codeaid_clean` | 3.710 | 19/31 | 19/31 | 2 |
| `dbox_inspired_clean` | 3.774 | 21/31 | 21/31 | 2 |
| `dbox_inspired_guard` | 3.774 | 23/31 | 23/31 | 2 |
| `bridge_guided_dbox_style_guard` | 3.742 | 20/31 | 20/31 | 2 |
| `bridge_contract_compact_guard` | 4.000 | 23/31 | 23/31 | 0 |
| `bridge_contract_compact_guard_repair` | 4.065 | 22/31 | 22/31 | 0 |

`bridge_contract_compact_guard_repair` has the highest overall score in this slice, and both Bridge Contract compact variants have 0 major+answer leakage. DBox-inspired decomposition remains a strong baseline: `dbox_inspired_guard` is close to the Bridge Contract compact variants on student-ready and safe-ready counts.

What this supports: The main scaffold result supports a quality-safety-burden trade-off. It also supports the educational claim that no-direct-solution prompting is not sufficient: `codehelp_codeaid_clean` is stronger than prompt-only, but it still has 2 major+answer leakage cases in the main slice.

What it does not support: The table does not establish significant comprehensive superiority of Bridge Contract over all baselines. It also does not validate online deployment, since all conditions are offline evaluation harnesses.

### 4.3 RQ3: How Much Uncertainty Remains In Same-Case Pairwise Comparisons?

What we tested: Same-case paired comparisons test whether observed condition differences remain strong when each condition is compared on the same cases rather than only through aggregate means.

What we observed: For `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard`, mean overall delta is +0.290, W/T/L is 14/10/7, and major+answer leakage is lower by 2 cases. However, the paired bootstrap 95% CI is [-0.097, +0.645], and the paired permutation p-value is 0.2016.

For `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard`, mean overall delta is +0.065, W/T/L is 7/18/6, and major+answer leakage is the same.

By contrast, `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` has a mean overall delta of +0.677, 95% CI [+0.258, +1.065], paired p=0.0046, 12 more safe-ready cases, and 7 fewer major+answer leakage cases.

What this supports: Pairwise analysis supports a trend-level trade-off advantage for Bridge Contract compact + Guard/Repair over DBox-inspired Guard, and a clearer improvement of no-direct-solution programming help over prompt-only.

What it does not support: It does not support a strong statistical superiority claim for Bridge Contract compact + Guard/Repair over DBox-inspired Guard. It also does not establish a causal Repair effect from the main condition comparison.

All-case sensitivity analysis shows `bridge_contract_compact_guard_repair` with the highest overall score under Coach A only, Coach B only, priority60+CoachA, and priority60+CoachB. Because all-case averages mix main scaffold, clarification, and policy slices, they remain supplemental. Student-ready, safe-ready, and rank outcomes are still sensitive to rater strictness.

### 4.4 RQ4: What Kinds Of Tutoring Failures Does The Benchmark Surface?

What we tested: The error analysis asks whether failures can be described beyond isolated algorithm scenes, such as “this is a DP case” or “this is a binary-search case.”

What we observed: The observed error taxonomy is organized as:

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

General tutoring failure types include critical bridge leakage, answer/code leakage, over-complete micro-examples, shifted focus, under-scaffolding, excessive burden, context misalignment, over-safe refusal, factual/algorithmic error, and policy/direct-answer handling failure. Operational cognitive bridge families include representation semantics, transition/action mapping, predicate/decision semantics, ordering/dependency control, modeling relation, aggregation/contribution accounting, data-structure operation mapping, correctness/invariant reasoning, implementation boundary, debugging evidence, and policy-request handling. DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, and debugging trace are surface anchors rather than taxonomy categories.

What this supports: The taxonomy supports analysis at the level of reusable cognitive bridge families and leakage mechanisms. It helps explain why a no-direct-code rule may miss leakage: the leaked object is often an intermediate representation, predicate, invariant, or debugging cue.

What it does not support: The taxonomy is not a universal CP tutoring taxonomy and does not claim exhaustive coverage of all tutoring failures.

### 4.5 RQ5: What Does Repair Add, And What Cost Does It Introduce?

What we tested: Repair is evaluated separately from main condition means because the main experiment compares outputs from different conditions. The same-candidate stress test fixes the original candidate and blinds the comparison between before_repair and after_repair.

What we observed: In the 30-pair same-candidate before/after stress test, Repair improves leakage severity in 16/30 pairs, preserves it in 14/30, and worsens it in 0/30. Major leakage falls from 7/30 to 0/30. Overall quality rises from 3.367 to 3.633, with mean delta +0.267. The burden trade-off is burden improved / same / worsened = 2/16/12.

DBox+Repair fairness is a targeted 20-case sensitivity add-on, not a new main condition. `dbox_inspired_guard_repair` has overall 3.55, safe-ready 11/20, and no/minor/major+answer leakage 14/6/0. Relative to the same-case DBox Guard subset, it modestly improves overall (+0.15, W/T/L=6/9/5) and reduces major+answer leakage from 2 to 0. Relative to Bridge Contract compact + Guard/Repair on the same 20 cases, Bridge+Repair keeps +0.50 overall, W/T/L=12/5/3, and safe-ready +4.

What this supports: Repair is promising as same-candidate stress evidence for leakage reduction. It also surfaces a practical educational-technology cost: reducing leakage can increase student response burden.

What it does not support: It does not make DBox+Repair a full main condition, prove Bridge superiority over every repair-enabled baseline, or show Repair causality from the main condition means.

### 4.6 RQ6: Can LLM Graders Replace Expert Review For Bridge Leakage?

What we tested: LLM-grader calibration asks whether automatic graders can provide reliable auxiliary signals for critical bridge leakage. The paper-facing calibration uses DeepSeek `deepseek-v4-flash` with thinking disabled, aligned with the offline judge stack.

What we observed: Against the priority60 reference, the DeepSeek case-specific bridge-rubric judge improves some auxiliary metrics over the generic rubric: leakage-label accuracy is 0.617 vs 0.583, student-ready agreement is 0.467 vs 0.433, and safe-ready agreement is 0.533 vs 0.400. However, both generic and case-specific DeepSeek graders have critical recall 0 and major leakage false-negative rate 1.000. They fail to retrieve rows that human adjudication marks as `major_bridge_leakage` or `answer_leakage`.

What this supports: Case-specific bridge rubrics can improve some low-stakes automatic-grading signals.

What it does not support: DeepSeek-backed LLM graders are not adequate for high-stakes critical-bridge leakage evaluation. Because tutor generation, judge/guard, and repair are all in the fixed DeepSeek-family offline stack, this calibration also has same-backend coupling and should not be read as cross-backend validation. Human review and adjudication remain necessary.

## 5. Discussion

### 5.1 No-Direct-Answer Rules Are Insufficient

The central educational-technology implication is that direct-answer avoidance is not enough for turn-level tutoring safety. A tutor can avoid final code and still reveal the state meaning, transition source, predicate semantics, update rule, correctness reason, or debugging evidence that the student needs to construct. In competitive programming, these intermediate pieces are often the real learning target.

This matters for system design. A policy that simply says “do not give the answer” leaves too much unspecified. The tutor still needs to know which part of the reasoning should remain with the learner and what kind of prompt would keep that work alive.

### 5.2 Human Review Is Necessary For Case-Specific Bridge Boundaries

Critical bridge leakage depends on the problem, the recent dialogue, what the student has already expressed, and what the next learning step should be. Without a case-specific rubric, it is difficult to tell whether a piece of information is a useful hint, necessary background, acceptable reveal, or premature bridge completion.

The review protocol makes these boundaries explicit at the case level. Coach disagreement is not merely noise; it is evidence that some judgments are pedagogically sensitive. For that reason, the paper reports reliability, priority adjudication, slice analysis, and sensitivity views instead of presenting one coach or priority60 adjudication as final gold.

### 5.3 Repair Is Promising But Burden-Bearing

Guard-only variants are guard-instrumented / guard-checked variants. They expose leakage risk, but the rewrite signal does not replace `final_response_text` except under block fallback. Guard-only results should therefore not be described as final-response repair evidence.

Repair is more directly evaluated in the same-candidate stress test. The test shows reduced leakage severity, but it also shows cases where student burden worsens. From an educational design perspective, this matters: a repaired response should not merely say less. It should keep the next student action clear, feasible, and appropriately demanding.

### 5.4 Automatic Graders Remain Auxiliary

LLM graders may help with scale, triage, or low-risk signals, but the dialogue-state v3 calibration shows that they cannot currently adjudicate high-risk critical bridge leakage alone. In the priority60 reference, critical recall is 0 and the major leakage false-negative rate is 1.000. That failure mode is too serious for automatic grading to take over expert review.

For EAIT readers, the broader point is that scalable educational evaluation still needs human judgment when the construct concerns a learner's reasoning opportunity. Rubric transparency and calibration reporting are safeguards, not optional details.

### 5.5 Practical Implications For Educational Technology Design

The design implication is not to make tutors withhold help. It is to make help controllable. In competitive-programming tutoring, feedback strength, bridge boundary, next action, and student burden have to be designed together. Bridge Contract-style constraints are useful because they force generation, review, and repair to refer to the same case-specific tutoring target.

Human review also plays a design role, not only an audit role. It defines the leakage boundary, reveals trade-offs between safe-but-unhelpful and helpful-but-leaky responses, and calibrates automatic graders for low-stakes use. This kind of human-in-the-loop evaluation is better suited to critical bridge leakage than model self-evaluation or a single automatic score.

### 5.6 Limitations

This study has six main limitations. First, the 50-case set is a high-risk CP tutoring evidence candidate, not exhaustive CP coverage. Second, student-ready, safe-ready, and rank outcomes are rater-sensitive, so sensitivity views are necessary. Third, priority60 adjudication is not final gold; it reduces uncertainty for high-priority disagreements but does not remove all rater differences. Fourth, DBox+Repair is a targeted 20-case sensitivity review, not a full 50-case double-coach condition. Fifth, DeepSeek-backed LLM-grader calibration has high critical false-negative risk and same-backend coupling, so automatic graders are unsuitable for high-stakes bridge-leakage adjudication. Sixth, the paper evaluates offline tutoring harnesses and does not validate online default AIChat or active-mode deployment.

## 6. Conclusion

CP-MissingBridgeBench turns missing-bridge preservation and critical bridge leakage into reviewable constructs for educational-technology evaluation. It addresses a concrete tutoring problem: how an LLM tutor can help a learner move forward without crossing the reasoning bridge for them.

The dialogue-state v3 evidence package supports a bounded conclusion. On the 31-case `main_scaffold_eval` headline slice, DBox-inspired decomposition is a strong baseline; no-direct-solution prompting does not fully prevent critical bridge leakage; and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view. Those findings must be read together with paired uncertainty, rater sensitivity, Guard-only instrumentation boundaries, Repair stress-test boundaries, DBox+Repair fairness sensitivity, and LLM-grader limitations.

The paper does not claim that 50 cases cover all CP tutoring or that coach labels or priority60 adjudication are final gold. It also does not treat guard instrumentation as rewrite evidence, infer Repair causality from main condition means, or assign LLM graders the role of human review. Its contribution is a reproducible benchmark and evaluation framework for studying how LLM tutoring can support programming learners while preserving their opportunity to complete the missing bridge.

## 7. Ethics, Data Governance, And AI Writing Disclosure

This draft uses the existing evidence package and its reproduction boundaries. AI writing assistance was used for drafting, editing, checklist generation, and evidence organization. The scientific claims, citations, numerical results, data boundaries, and final wording remain the responsibility of the human authors. Before submission, the manuscript still needs venue-specific checks for AI writing disclosure, privacy and data statements, citation verification, and result-number verification.
