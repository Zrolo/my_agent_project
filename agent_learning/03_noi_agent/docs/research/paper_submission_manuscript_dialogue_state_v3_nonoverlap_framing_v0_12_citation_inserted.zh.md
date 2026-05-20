# CP-MissingBridgeBench: Evaluating Critical-Bridge Leakage in LLM Tutors for Competitive Programming

## Abstract

LLM tutors for competitive programming can offer timely help, but useful help must preserve the learner's opportunity to complete the next reasoning step. Critical bridge leakage names a tutoring-specific failure in which a response prematurely supplies an intermediate bridge, such as a DP-state meaning, binary-search predicate, invariant, update rule, or debugging cue, even without final code. CP-MissingBridgeBench is a high-resolution, human-reviewed diagnostic benchmark for evaluating this risk in turn-level competitive-programming tutoring. The fixed offline dialogue-state evaluation contains 50 reviewed cases, 7 anonymized offline harnesses, and 350 response-level outputs; the headline scaffold analysis is limited to the 31-case `main_scaffold_eval` slice, corresponding to 217 response-level reviews, while remaining slices are sensitivity or appendix evidence. Each case pairs problem context, recent dialogue, and a case-specific rubric specifying the missing bridge, forbidden content, acceptable reveal, and expected next student action. Under the primary human-review view, DBox-inspired decomposition remains a strong offline baseline, no-direct-solution prompting does not eliminate critical bridge leakage, and Bridge Contract compact + Guard/Repair shows favorable but bounded trends in overall quality and high-severity leakage control. We further specify an external real-log ecological-validation layer: Real-AIChat-100 is observational and checks taxonomy/rubric transfer, while optional Real-AIChat-Replay-30/50 would generate offline counterfactual responses from the fixed harnesses on the same real-student starting states. These layers are not online deployment experiments, do not evaluate learning outcomes, and do not update the dialogue-state v3 main results. The findings suggest that pedagogical safety in LLM tutoring should be evaluated at the level of learners' reasoning opportunities, not only at the level of final-answer disclosure.

## 1. Introduction

Consider a competitive-programming tutoring dialogue in which a student says, "I know this may need binary search, but I do not know how to write `check(x)`." A helpful tutor could ask what `x` represents, what condition should become easier or harder as `x` changes, and what evidence from the problem constraints should be tested. A less careful tutor might answer with the full monotonic predicate. That response may contain no final code, yet it has already crossed the bridge the student needed to build.

The same pattern appears in DP and graph problems. A student may have the transition formula almost in reach but still not know what the state should mean; or may be implementing LCA but not yet understand which ancestor relationship is being queried. At these moments, the best help is neither silence nor a complete explanation. It is a scaffold that makes the next step reachable while leaving the central reasoning step with the learner.

This is the tutoring tension addressed in this paper. Students often need help before they complete a reasoning bridge, but that is also when a tutor can most easily over-help. In programming tutoring, avoiding final code is therefore not enough. A response can obey a no-direct-code rule and still leak the critical intermediate idea by spelling out the predicate, state semantics, invariant, update rule, or debugging evidence that the student was supposed to infer.

We refer to the local, not-yet-crossed reasoning step as a missing bridge. Critical bridge leakage occurs when a tutor prematurely supplies that bridge, even without giving a full solution. This differs from final-answer leakage: a response may avoid the final answer while still revealing the decisive intermediate reasoning, or it may offer a small hint while preserving the student's work.

### Positioning Against Nearby Work

This paper is intentionally narrower than nearby tutor-leakage and algorithmic-programming scaffolding work. Work on tutor leakage under adversarial student attacks asks whether a tutor can be induced to reveal final answers or complete solutions. CP-MissingBridgeBench instead studies ordinary turn-level tutoring, where the student is asking for help and the risk is premature completion of a critical intermediate bridge.

DBox-style work addresses a different educational design problem: how LLMs can support learners in decomposing algorithmic programming tasks. CP-MissingBridgeBench does not propose a DBox-style decomposition system. It evaluates case-specific tutor responses, including a DBox-inspired condition used as a strong offline baseline, to ask whether each response preserves the learner's current missing reasoning bridge.

This is a pedagogical-safety framing, not a general AI-safety benchmark. The evaluation problem is case-specific: a hint that is acceptable after a student has already stated the monotonic predicate may be over-revealing before the student has identified it. A useful turn-level evaluation must therefore ask whether the response matches the student's current state, gives enough help for the next move, avoids completing the current missing bridge, and keeps the next student action manageable.

CP-MissingBridgeBench is designed around this problem. Each case contains the problem context, recent dialogue, current student message, and a rubric that specifies success criteria, forbidden content, the critical bridge boundary, acceptable reveal, and expected student next action. Expert reviewers are asked to evaluate the current pedagogical boundary, not merely whether the reply sounds clear or friendly.

The dialogue-state v3 evaluation set contains 50 reviewed candidate cases, 7 anonymized offline tutoring harness conditions, and 350 AI responses. Two coaches completed blind review over the full set. The evaluation set also includes priority adjudication, paired uncertainty, slice analysis, a same-candidate Repair stress test, DBox+Repair fairness sensitivity, and DeepSeek LLM-grader calibration. The main headline is restricted to the 31-case `main_scaffold_eval` slice; all-50 aggregates, non-main slices, stress tests, and calibration analyses are reported only according to their evidence class.

The paper makes three bounded contributions. First, it frames missing-bridge preservation as an educational-technology evaluation problem for competitive-programming tutoring. Second, it provides a case-specific human-review workflow for judging quality, safety, student burden, leakage boundaries, and rater sensitivity together. Third, it reports dialogue-state v3 evidence showing quality-safety-burden trade-offs: DBox-inspired decomposition is a strong baseline, and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view. These results are not claims that one method wins across all baselines, nor do they validate an online deployed tutor.

## 2. Related Work

### 2.1 AI Tutoring / ITS For Programming

Prior work on AI tutoring and intelligent tutoring systems for programming treats feedback as more than correctness delivery. Programming tutors are evaluated by how they help learners interpret errors, organize concepts, receive adaptive support, and make progress in realistic learning settings. This literature gives CP-MissingBridgeBench its educational frame: a tutoring response should be judged not only by whether it is correct, but by how it shapes the learner's next reasoning move \cite{chrysafiadi2023fuzzyITS,wang2023realContextITS,gong2025genAIDFProgramming,guner2025chatgptProgramming}.

The limitation for the present paper is that system-level tutoring evaluations do not, by themselves, identify when a single response completes the learner's current missing bridge. CP-MissingBridgeBench therefore positions the unit of analysis at the turn level: it asks whether a response in a competitive-programming dialogue preserves the student's case-specific reasoning work while still offering usable help.

### 2.2 LLM Feedback And Scaffolding

Prior work on LLM feedback and scaffolding shows why generative feedback is attractive in educational settings: it can be immediate, fluent, specific, and adaptive to the learner's expressed difficulty. In programming contexts, those strengths can support explanation, debugging, decomposition, and reflection. They also create a pedagogical risk, because the response that sounds most complete may also be the one that removes the student's opportunity to formulate the next idea \cite{gong2025genAIDFProgramming,guo2024chatgptTeacherFeedback,ma2025dbox}.

The limitation is that feedback quality and feedback appropriateness are not the same construct. CP-MissingBridgeBench is positioned around the boundary of appropriate scaffolding: in the binary-search vignette, asking the student to articulate the monotonic condition can be acceptable, while giving the predicate itself can be leakage. The benchmark therefore evaluates whether LLM feedback preserves the cognitive work that belongs to the learner at that moment.

### 2.3 Rubric-Based Expert Evaluation

Prior work on rubric-based expert evaluation emphasizes that open-ended educational artifacts require explicit criteria if human judgment is to be interpretable. CP-MissingBridgeBench follows this logic by fixing, for each case, the success criteria, forbidden content, critical bridge boundary, acceptable reveal, and expected next student action before scoring. Coach A/B review and priority60 adjudication are treated as expert reference views with sensitivity reporting, not as a single definitive label \cite{gonzalezMujico2024rubricFrameworks,li2025aiExplainsGrading,maurya2025mrbench}.

The limitation addressed here is that bridge leakage is not a surface feature of a response alone. The same phrase may be a helpful hint in one dialogue state and a premature reveal in another. CP-MissingBridgeBench therefore makes case-specific human review part of the evaluation design, so that each response is judged against the student's demonstrated state and the next reasoning opportunity.

### 2.4 Answer Leakage And Tutor Robustness

Prior work on tutor leakage and robustness is most relevant when it asks whether an LLM tutor reveals final answers or complete solutions, especially under adversarial student behavior. That line of work is important for academic integrity and tutor safety, but it evaluates a different leakage object and often a different interaction regime from ordinary help-seeking \cite{zhao2026answerLeakage}.

The limitation is the intermediate reasoning layer. Work centered on final-answer disclosure under adversarial attacks does not evaluate whether an ordinary tutoring response prematurely completes the student's current critical bridge. CP-MissingBridgeBench is positioned between harmless hinting and final-solution disclosure: its target is the case-specific reasoning bridge that the learner still needs to cross.

### 2.5 Algorithmic-Programming Scaffolding And DBox

Prior work on algorithmic-programming scaffolding is close to CP-MissingBridgeBench because it treats decomposition as part of learning to solve programming problems. DBox-style work studies LLM-supported co-decomposition for algorithmic programming. This is a relevant comparison point for CP tutoring because decomposition can make hidden reasoning steps explicit and can structure the learner's next move \cite{ma2025dbox,maurya2025mrbench}.

The limitation is that decomposition support and leakage-boundary evaluation are different research objects. CP-MissingBridgeBench uses a DBox-inspired single-turn condition as a strong offline baseline, but it does not claim to reproduce the complete interactive DBox system. The paper's position is evaluative: it asks whether DBox-inspired and bridge-guided responses preserve critical bridges under case-specific human review.

### 2.6 LLM Graders And Calibration

Prior work on AI-supported assessment and LLM graders motivates automatic scoring as a possible way to scale feedback review, triage, or low-risk evaluation. At the same time, educational assessment work treats human judgment as especially important when the evaluated construct is nuanced, contextual, or high consequence. CP-MissingBridgeBench follows that distinction by treating DeepSeek-backed judging as auxiliary calibration rather than a replacement for human review \cite{atasoy2025chatgptEvaluator,li2025aiExplainsGrading,maurya2025mrbench}.

The limitation is reliability at the boundary that matters most. In this benchmark, the practical question is not whether an LLM grader can produce a plausible score, but whether it can identify high-risk critical bridge leakage. The current evidence keeps automatic grading auxiliary because the critical cases remain the ones that most require human adjudication.

## 3. Methods / Evaluation

### 3.1 Task Definition: Critical Bridge Leakage

Critical bridge leakage is not the same as final-answer leakage. It is the premature completion of a case-specific reasoning bridge that the learner has not yet crossed. In a competitive-programming tutoring turn, that bridge may be a DP state meaning, a binary-search predicate, an invariant, an aggregation argument, a data-structure operation, or the debugging evidence needed to locate a fault.

CP-MissingBridgeBench evaluates whether a tutoring response preserves the student's missing bridge while still providing useful scaffolding. A missing bridge is the local reasoning step that the student has not yet completed but needs for the next productive move. It is not an algorithm label; it is defined by the current problem, dialogue state, and student message.

As a running example, suppose the student has already suspected binary search but has not yet formulated `check(x)`. The missing bridge is not "binary search" itself. It is the monotonic predicate: what candidate `x` means, what property should be tested, and why the test becomes easier or harder as `x` changes. Forbidden content would include spelling out the full predicate or giving code-level logic for the check. Acceptable reveal might include asking the student to define what `x` stands for or to compare two candidate values. The expected next action is for the student to state the predicate in their own words.

Table 1 is a conceptual illustration only; it introduces the evaluation construct and does not add experimental cases or results.

| student state | missing bridge | acceptable reveal | critical leakage |
| --- | --- | --- | --- |
| The student suspects binary search but cannot define `check(x)`. | The monotonic predicate and the meaning of candidate `x`. | Ask what `x` represents, what should become easier or harder as `x` changes, and what property the predicate must test. | Give the full predicate, the check inequality, or code-level logic for the predicate. |
| The student has a recurrence intuition but cannot name the DP state. | The state semantics and which previous state contributes to the transition. | Ask what each dimension records and which earlier choice must be known before the transition. | State the exact DP meaning and transition formula the student has not yet derived. |
| The student knows a tree-path update needs marking but not how tree-difference marking works. | The endpoint, LCA, and cancellation rule that makes path contributions aggregate correctly. | Ask which nodes should receive positive and negative marks and where the path contribution should stop. | Give the exact endpoint/LCA marking rule or the full contribution/cancellation pattern. |

Critical bridge leakage occurs when the tutor supplies that local reasoning step too early. The response may still avoid final code or a complete solution, but it can nevertheless disclose the key intermediate idea. By contrast, acceptable scaffolding can include clarification, context, a small hint, a diagnostic question, or a low-burden next action, provided it does not cross the case-specific bridge boundary.

Observed errors are organized with a three-part taxonomy:

```text
cognitive bridge family + leakage mechanism + surface anchor
```

The cognitive bridge family captures the transferable reasoning type, the leakage mechanism describes how the response over-reveals, and the surface anchor records the concrete algorithmic setting. The taxonomy is operational and observed within this benchmark; it is not presented as a universal taxonomy of competitive-programming tutoring.


### 3.2 Sample Adequacy And Evidence Boundaries

CP-MissingBridgeBench is designed as a high-resolution diagnostic benchmark rather than a population-level prevalence estimate. The 50 reviewed dialogue-state cases are costly units: each case requires problem context, recent dialogue, a student-state interpretation, case-specific forbidden content, acceptable reveal, expected next student action, and human review across anonymized tutoring responses. This design makes the sample appropriate for studying whether tutoring harnesses preserve learner reasoning opportunities under controlled human review, but it should not be interpreted as estimating how often critical bridge leakage occurs across all competitive-programming tutoring interactions.

The sample is therefore adequate for bounded diagnostic claims: it can reveal quality-safety-burden trade-offs, identify where no-direct-solution rules still leak intermediate reasoning, and test whether case-specific rubrics make critical bridge boundaries reviewable. It is not adequate for claims about population prevalence, full CP tutoring coverage, deployed AIChat superiority, or long-term learning outcomes. The evidence hierarchy below fixes these boundaries before results are interpreted.

| evidence layer | unit and count | role in paper | boundary |
| --- | --- | --- | --- |
| Fixed offline benchmark | 50 reviewed dialogue-state cases; 7 anonymized offline harnesses; 350 response-level outputs | Main human-review evidence package | Offline diagnostic benchmark, not online deployment evidence |
| Headline scaffold analysis | 31 `main_scaffold_eval` cases; 217 response-level reviews | Primary scaffold-quality, leakage, and burden comparison | 217 reviews are same-case condition outputs, not separate case-level samples |
| Remaining dialogue-state slices | 19 non-headline cases; 133 response-level reviews | Sensitivity / appendix for caution, clarification safety, and policy-safety targets | Not mixed into headline scaffold ranking |
| Supporting checks | paired uncertainty, Repair same-candidate stress, DBox+Repair targeted add-on, LLM-grader calibration | Stress, fairness sensitivity, and auxiliary calibration | Not promoted to main result or causal online-system evidence |
| Online AIChat log corpus background | 1156 message rows; 87 sessions; 578 paired user-assistant turns | Source-corpus background from our own system | Not a condition comparison or learning-outcome study |
| Candidate-turn screening pool | 137 substantial candidate turns; 59 candidate sessions | Lightweight screening for context sufficiency and possible bridge-family coverage | Not full rubric annotation |
| Selected pilot candidate set | 30 selected pilot candidate cases; 11 hashed students; 15 hashed problems | Candidate set for taxonomy/rubric transfer after privacy and consent/reporting gates | Not main result; no comparison to the seven offline harnesses |
| 5-case human coach dry run | 5 internally reviewed real-student pilot cases | Process check for whether the coach-facing form can be completed on real AIChat cases | Process evidence only; case-level labels and score distributions suppressed while consent/reporting gate is pending |
| 9-case focus review and 2-case adjudication workflow | 9 focus cases selected from the 30-case packet; 2 rows adjudicated after second-coach review | Internal workflow check for coach-review and adjudication closure on real AIChat cases | Workflow status only; no public case-level labels, leakage rates, or model-quality distributions |
| Real-AIChat-100 observational validation | 80-100 target turns from AIChat candidate turns, or `N <= 100` if fewer satisfy criteria | Ecological validity and taxonomy/rubric transfer | Observational only; not condition comparison and not learning-outcome evidence |
| Real-AIChat-Replay-30/50 | 30 context-sufficient cases first, optional 50 if feasible | Real-log-grounded offline counterfactual validation using fixed harnesses | Auxiliary validation only; not merged into dialogue-state v3 main tables |
| Real trajectory subset | 20-30 real multi-turn trajectories, if collected | Context-sufficiency and short-horizon interpretation | Not learning outcome evidence and not deployed-system effectiveness |

The offline benchmark covers multiple bridge families and evaluation targets without treating them as one homogeneous population. The table below summarizes coverage from existing dialogue-state v3 case metadata; it does not add cases, change slices, or change any reported numbers.

| slice | case_n | bridge-family coverage from case metadata | expected tutor moves | context readiness / case type | paper role |
| --- | ---: | --- | --- | --- | --- |
| `clarification_safety_slice` | 10 | state representation (6), transition / recurrence source (4) | `clarify_context` | no recent dialogue, vague question, short context with problem metadata | clarification and non-hallucination safety |
| `main_scaffold_eval` | 31 | transition (1), predicate check (5), boundary/order (3), modeling (2), aggregation/contribution (4), data-structure operation (5), correctness/invariant (5), implementation boundary (4), debugging evidence (2) | `continue_prior_scaffold`, `micro_scaffold` | recent dialogue ends with assistant; problem context present; several code/pronoun-dependent cases | headline scaffold analysis |
| `main_eval_with_caution` | 5 | boundary/order (2), modeling relation (3) | `micro_scaffold` | scaffold-like cases retained with caution | sensitivity / appendix |
| `policy_safety_slice` | 4 | debugging evidence (1), policy request (3) | `safe_refusal` | direct-answer/code or policy-risk redirection cases | policy-safety appendix |

This coverage table supports diagnostic breadth across bridge families and surface anchors, but it does not claim exhaustive taxonomy coverage. The benchmark is strongest when read as a case-specific human-review instrument: it asks whether each response preserves the learner's current missing bridge, not whether the sample represents all possible CP tutoring interactions.

### 3.3 Unit Of Analysis

The unit of analysis is fixed separately for each evidence layer. The 50 dialogue-state v3 items are reviewed case-level tutoring situations, not a set of student participants. The 350 outputs are response-level outputs generated by applying 7 anonymized offline harnesses to the 50 cases; they are not independent case-level samples. The 217 reviews in the headline scaffold slice are response-level reviews nested within 31 `main_scaffold_eval` cases, not independent student samples.

The real-student AIChat layers use different units. Real-AIChat-100 would consist of real dialogue turns or case-level target turns from our own system, not a student-level learning sample. Real-AIChat-Replay-30/50 would use the same real-student starting states for offline counterfactual response generation, not online deployment. Real trajectory subsets, if used, are short-horizon context checks and not evidence of learning or long-term achievement gains.

The completed real-student review steps are treated as workflow units rather than results units. Five real-student pilot cases were reviewed internally by a human coach using the coach-facing form aligned with the 50-case rubric. A separate 9-case focus workflow was then closed internally after second-coach review and 2-case adjudication. These steps support only process claims that the review and adjudication workflow can be executed on real AIChat cases; they do not report leakage rates, score distributions, learning outcomes, or deployed-system performance.

### 3.4 Dialogue-State v3 Cases And Slices

Dialogue-state v3 contains 50 reviewed candidate cases. Each case keeps the problem context, recent dialogue, student message, and case-specific rubric together, so the response is judged against the actual tutoring situation rather than against an isolated problem statement. The running binary-search example illustrates why this matters: the same sentence about monotonicity may be a useful hint after the student has named the predicate, but a leakage case before that bridge has been crossed.

The dataset is organized at two levels: 50 case-level tutoring situations and 350 response-level outputs. Since each case is evaluated under 7 anonymized conditions, the 31-case main scaffold slice yields 217 tutor responses for the headline scaffold analysis.

The case-level tutoring situation is the primary unit for slice assignment, while response-level outputs are generated by applying the 7 anonymized conditions to each case. Condition differences are therefore interpreted with same-case paired comparisons rather than as separate case-level samples.

| slice | case_n | response_count | evaluation_target | paper use |
| --- | ---: | ---: | --- | --- |
| `main_scaffold_eval` | 31 | 217 | ordinary scaffold quality, leakage control, and student burden | 主脚手架质量、泄露和学生负担比较 |
| `main_eval_with_caution` | 5 | 35 | scaffold-like cases retained with caution | sensitivity / appendix |
| `clarification_safety_slice` | 10 | 70 | insufficient-context clarification and non-hallucination | 澄清、不脑补和上下文不足时的安全询问 |
| `policy_safety_slice` | 4 | 28 | direct-answer/code request redirection | 学生直接要答案/代码时的安全重定向 |
| all cases | 50 | 350 | full reviewed corpus across heterogeneous targets | sensitivity / appendix only |

The main headline uses only `main_scaffold_eval`. The other slices and the all-50 aggregate are treated as sensitivity or appendix evidence. This separation avoids mixing ordinary scaffolding, clarification safety, and direct-answer policy handling into one headline number.

The full 50-case corpus is not discarded. Non-main slices are reported separately because they test different evaluation targets.

### 3.5 Offline Human-Review Harnesses

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

These are offline evaluation harnesses, not online AIChat configurations and not evidence of active-mode deployment. They are used to study tutoring-response behavior under controlled review conditions. The DBox-inspired rows should be read as baseline harnesses in this offline review design, not as a claim about the full DBox system.

### 3.6 Case-Specific Rubric And Blind Review

Each case is scored against a rubric fixed before review. The rubric includes `success_criteria`, `forbidden_content`, `critical_bridge_boundary`, `acceptable_reveal`, and `expected_student_next_action`. In the running example, the rubric would separate a legitimate prompt such as "what must become true as `x` increases?" from a forbidden response that gives the full check predicate. This design makes the review concrete: the coach judges whether a response is appropriate for this student, this dialogue state, and this next learning step.

Coach A and Coach B each reviewed all 350 responses. For every response, they saw the problem context, rubric, recent dialogue, student message, and candidate reply, then assigned main metrics, diagnostic labels, and reliability fields. Forced notes were required for major / answer leakage, `show=no`, `overall_quality<=2`, first or last rank within a case, low confidence, and samples needing discussion.

Coach A, Coach B, and priority60 adjudication are expert reference or adjudicated sensitivity views. None is treated as a single definitive label. Disagreement is part of the evidence: it shows where pedagogical judgment is sensitive and where the paper must report uncertainty rather than a single settled label.

### 3.7 Metrics

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

### 3.8 Analysis Hierarchy And Evidence Manifest

The analysis was organized by evidence role before manuscript claims were assigned. The purpose of this hierarchy is to keep the educational interpretation aligned with what each comparison can support. The 31-case `main_scaffold_eval` slice provides the main scaffold evaluation. Rater-specific views, non-main slices, and all-50 summaries are used to examine sensitivity. Same-case comparisons are used to describe uncertainty around condition differences. Repair before/after comparisons and DBox+Repair review are kept as supporting checks rather than promoted into headline evidence.

| evidence class | use |
| --- | --- |
| main result | `main_scaffold_eval` + priority60 adjudicated + Coach A 主口径 |
| sensitivity | Coach A only、Coach B only、priority60 + Coach A、priority60 + Coach B、all-case appendix |
| slice analysis | main scaffold、caution、clarification safety、policy safety 分开报告 |
| paired uncertainty | 同 case 条件比较的 W/T/L、mean delta、bootstrap CI 和 permutation test |
| stress test | Repair same-candidate before/after 因果压力测试 |
| fairness sensitivity | DBox+Repair 20-case targeted add-on |
| calibration | DeepSeek LLM grader calibration，作为 auxiliary grader 评估 |

The evidence manifest and reproduction scripts provide the audit trail for the reported tables: `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`, `evals/aichat/reproduce_dialogue_state_v3_tables.py`, and `evals/aichat/verify_dialogue_state_v3_reports.py`. This traceability is methodological support, not a separate result. Sensitivity, stress, and calibration results are not promoted to main results.

### 3.9 External Validation Protocols

The external validation plan adds protocol layers without changing the fixed dialogue-state v3 benchmark. Real-AIChat-100 is an observational ecological-validity layer drawn from our own AIChat / teaching-system candidate turns. It does not compare the 7 offline harnesses. Its purpose is to examine whether the bridge-family taxonomy, surface anchors, context-sufficiency labels, and case-specific rubric fields transfer to real student dialogue turns.

As a preliminary workflow check, a 5-case real-student dry run has been completed by a human coach using the same coach-facing dimensions as the 50-case response-review rubric. A later 9-case focus-review workflow from the 30-case packet has also been closed internally: 7 rows received second-coach review status and 2 rows were resolved through adjudication. These workflow checks are not reported as result tables because the consent/reporting gate remains closed. Public reporting is limited to process status and gate counts, with 0 cases reportable as public case-level evidence.

The observed current AIChat response is treated as `observed_current_aichat_response`: an observed current-system response already shown to the student. It is not one of the 7 offline harnesses, not a control arm, not a deployment comparison arm, and not a Repair output. If privacy or consent/reporting gates remain pending, this layer can report only aggregate/process counts and schema readiness.

Real-AIChat-Replay-30/50 is the only external layer that would permit a same-starting-state offline comparison of the fixed harnesses on real-log-grounded cases. Replay-30 would first select 30 context-sufficient cases from Real-AIChat-100; Replay-50 is optional if time and review capacity allow. Replay responses would be generated offline, hidden from students, randomized for blind coach review, and reported only as auxiliary counterfactual validation. Replay results would not be merged into dialogue-state v3 main results.

Safe wording block:

```text
The observed current AIChat response is treated as an observed current-system response rather than as a baseline condition. Real-AIChat-100 is used to examine ecological validity and rubric transfer. Real-AIChat-Replay, where conducted, uses the same real-student starting states to generate offline counterfactual responses from the fixed harnesses; it is reported as auxiliary validation and is not merged into the dialogue-state v3 main results.
```

## 4. Results

The results are organized around six evaluation questions. Headline results use 31 case-level situations and 217 response-level reviews from the `main_scaffold_eval` slice under priority60 adjudicated + Coach A. The all-case aggregate is sensitivity evidence. Rater views, non-main slices, and all-50 summaries are sensitivity or appendix evidence. Repair before/after comparisons are stress evidence; DBox+Repair is a targeted fairness sensitivity add-on; DeepSeek LLM-grader calibration is auxiliary and remains outside the human adjudication role.

### 4.1 RQ1: How Stable Is Human Review For Critical-Bridge Judgments?

The first question is whether expert review yields a single unambiguous view of response quality and leakage. Both coaches reviewed all 350 responses from the 50 reviewed candidate cases and 7 anonymized tutoring harness conditions. Overall exact agreement between Coach A and Coach B is 0.2829, while within-1 agreement is 0.8429. Leakage-label exact agreement is 0.6714. Critical-binary exact agreement is 0.9029, but kappa is 0.2511.

The priority adjudication set contains 60 high-priority disagreements: `use_A=29`, `use_B=9`, and `new_label=22`. These results support human review with explicit sensitivity reporting. They do not justify treating Coach A, Coach B, or priority60 adjudication as a single settled reference. Detailed rank agreement, including top-1 and last-place agreement both at 10/50, is reserved for the appendix. The evidence boundary for this section is methodological: human review is necessary, but rater-sensitive outcomes must be reported with uncertainty.

### 4.2 RQ2: Which Offline Harnesses Best Balance Helpfulness And Leakage Control On The Main Scaffold Slice?

The headline evaluation compares the 7 anonymized conditions on the 31-case `main_scaffold_eval` slice under the `priority60 adjudicated + Coach A` view. Clarification and policy-safety cases are not mixed into this headline.

| condition | overall | student-ready | safe-ready | major+answer leakage |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.032 | 7/31 | 7/31 | 9 |
| `codehelp_codeaid_clean` | 3.710 | 19/31 | 19/31 | 2 |
| `dbox_inspired_clean` | 3.774 | 21/31 | 21/31 | 2 |
| `dbox_inspired_guard` | 3.774 | 23/31 | 23/31 | 2 |
| `bridge_guided_dbox_style_guard` | 3.742 | 20/31 | 20/31 | 2 |
| `bridge_contract_compact_guard` | 4.000 | 23/31 | 23/31 | 0 |
| `bridge_contract_compact_guard_repair` | 4.065 | 22/31 | 22/31 | 0 |

In this slice, `bridge_contract_compact_guard_repair` has the highest overall score, and both Bridge Contract compact variants have 0 major+answer leakage. At the same time, DBox-inspired decomposition remains a strong baseline: `dbox_inspired_guard` is close to the Bridge Contract compact variants on student-ready and safe-ready counts. The table therefore supports a quality-safety-burden trade-off rather than a single-condition victory.

The contrast between `codehelp_codeaid_clean` and `enhanced_prompt_only_clean` also supports the educational problem statement. A no-direct-code / no-direct-solution baseline is stronger than prompt-only, but it still has 2 major+answer leakage cases in the main slice. Condition-level ranks and non-main slice tables are reserved for the appendix. The evidence boundary is that this table does not establish broad superiority of Bridge Contract over all baselines and does not validate online deployment; all conditions are offline evaluation harnesses.

### 4.3 RQ3: How Much Uncertainty Remains In Same-Case Pairwise Comparisons?

Same-case paired comparisons ask whether observed differences remain persuasive when conditions are compared on the same cases. For `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard`, mean overall delta is +0.290, W/T/L is 14/10/7, and major+answer leakage is lower by 2 cases. The paired bootstrap 95% CI is [-0.097, +0.645], and the paired permutation p-value is 0.2016.

For `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard`, mean overall delta is +0.065, W/T/L is 7/18/6, and major+answer leakage is the same. By contrast, `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` has a mean overall delta of +0.677, 95% CI [+0.258, +1.065], paired p=0.0046, 12 more safe-ready cases, and 7 fewer major+answer leakage cases.

These comparisons support a trend-level trade-off advantage for Bridge Contract compact + Guard/Repair over DBox-inspired Guard, and a clearer improvement of no-direct-solution programming help over prompt-only. All-case sensitivity analysis is reserved for the appendix and is used only to check whether the bounded trend interpretation is fragile across rater views; it is not used for headline ranking. The evidence boundary is important: the paired analysis does not support a strong superiority claim for Bridge Contract compact + Guard/Repair over DBox-inspired Guard, and the main condition comparison does not establish a causal Repair effect.

### 4.4 RQ4: What Kinds Of Tutoring Failures Does The Benchmark Surface?

The error analysis asks whether failures can be described beyond isolated algorithm scenes, such as "this is a DP case" or "this is a binary-search case." The observed error taxonomy is organized as:

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

General tutoring failure types include critical bridge leakage, answer/code leakage, over-complete micro-examples, shifted focus, under-scaffolding, excessive burden, context misalignment, over-safe refusal, factual/algorithmic error, and policy/direct-answer handling failure. Operational cognitive bridge families include representation semantics, transition/action mapping, predicate/decision semantics, ordering/dependency control, modeling relation, aggregation/contribution accounting, data-structure operation mapping, correctness/invariant reasoning, implementation boundary, debugging evidence, and policy-request handling. DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, and debugging trace are surface anchors rather than taxonomy categories.

This taxonomy supports analysis at the level of reusable cognitive bridge families and leakage mechanisms. It also explains why a no-direct-code rule may miss leakage: the leaked object is often an intermediate representation, predicate, invariant, or debugging cue. Extended taxonomy examples and reviewer notes are reserved for the appendix. The evidence boundary is that the taxonomy is observed and operational for this benchmark; it is not a universal taxonomy and does not claim exhaustive coverage of all tutoring failures.

### 4.5 RQ5: What Does Repair Add, And What Cost Does It Introduce?

Repair is evaluated separately from main condition means because the main experiment compares outputs from different conditions. The same-candidate stress test fixes the original candidate and blinds the comparison between before_repair and after_repair. In the 30-pair same-candidate before/after stress test, Repair improves leakage severity in 16/30 pairs, preserves it in 14/30, and worsens it in 0/30. Major leakage falls from 7/30 to 0/30. Overall quality rises from 3.367 to 3.633, with mean delta +0.267. The burden trade-off is burden improved / same / worsened = 2/16/12.

DBox+Repair fairness is a targeted 20-case sensitivity add-on, not a new main condition. `dbox_inspired_guard_repair` has overall 3.55, safe-ready 11/20, and no/minor/major+answer leakage 14/6/0. Relative to the same-case DBox Guard subset, it modestly improves overall (+0.15, W/T/L=6/9/5) and reduces major+answer leakage from 2 to 0. Relative to Bridge Contract compact + Guard/Repair on the same 20 cases, Bridge+Repair keeps +0.50 overall, W/T/L=12/5/3, and safe-ready +4.

These findings support Repair as same-candidate stress evidence for leakage reduction, while also showing a practical educational-technology cost: reducing leakage can increase student response burden. Full paired Repair notes and per-case DBox+Repair review details are reserved for the appendix. The evidence boundary is that DBox+Repair is not a full main condition, the analysis does not prove Bridge superiority over every repair-enabled baseline, and Repair causality is not inferred from the main condition means.

### 4.6 RQ6: Can LLM Graders Adjudicate Bridge Leakage?

LLM-grader calibration asks whether automatic graders can provide reliable auxiliary signals for critical bridge leakage. The calibration reported here uses DeepSeek `deepseek-v4-flash` with thinking disabled, aligned with the offline judge stack. Against the priority60 reference, the DeepSeek case-specific bridge-rubric judge improves some auxiliary metrics over the generic rubric: leakage-label accuracy is 0.617 vs 0.583, student-ready agreement is 0.467 vs 0.433, and safe-ready agreement is 0.533 vs 0.400.

However, both generic and case-specific DeepSeek graders have critical recall 0 and major leakage false-negative rate 1.000. They fail to retrieve rows that human adjudication marks as `major_bridge_leakage` or `answer_leakage`. Case-specific bridge rubrics can therefore improve some low-stakes automatic-grading signals, but DeepSeek-backed LLM graders are not adequate for high-stakes critical-bridge leakage evaluation.

Prompt variants and auxiliary calibration tables are reserved for the appendix. The evidence boundary is that tutor generation, judge/guard, and repair are all in the fixed DeepSeek-family offline stack, so this calibration has same-backend coupling and should not be read as cross-backend validation. Human review and adjudication remain necessary.

## 5. Discussion

### 5.1 The Safety Framing Is Pedagogical And Tutoring-Specific

The safety framing in this paper is deliberately narrow. Critical bridge leakage is a tutoring-specific pedagogical safety failure: it concerns whether a tutor preserves a learner's reasoning opportunity in a competitive-programming turn. It is not a broad account of safety across all AI-supported educational settings, and it is not a benchmark for adversarial attacks. This scope matters because critical bridge leakage can occur in ordinary help-seeking dialogue, not only when a student tries to extract an answer.

### 5.2 No-Direct-Answer Rules Are Insufficient

Direct-answer avoidance is not enough for turn-level tutoring safety. A tutor can avoid final code and still reveal the state meaning, transition source, predicate semantics, update rule, correctness reason, or debugging evidence that the student needs to construct. In competitive programming, these intermediate pieces are often the real learning target.

This matters for system design. A policy that simply says "do not give the answer" leaves too much unspecified. The tutor still needs to know which part of the reasoning should remain with the learner and what kind of prompt would keep that work alive.

### 5.3 Human Review Is Necessary For Case-Specific Bridge Boundaries

Critical bridge leakage depends on the problem, the recent dialogue, what the student has already expressed, and what the next learning step should be. Without a case-specific rubric, it is difficult to tell whether a piece of information is a useful hint, necessary background, acceptable reveal, or premature bridge completion.

The review protocol makes these boundaries explicit at the case level. Coach disagreement is not merely noise; it is evidence that some judgments are pedagogically sensitive. For that reason, the paper reports reliability, priority adjudication, slice analysis, and sensitivity views instead of presenting one coach or priority60 adjudication as a single definitive reference.

### 5.4 Repair Is Promising But Burden-Bearing

Guard-only variants are guard-instrumented / guard-checked variants. They expose leakage risk, but the rewrite signal does not replace `final_response_text` except under block fallback. Guard-only results should therefore not be described as final-response repair evidence.

Repair is more directly evaluated in the same-candidate stress test. The test shows reduced leakage severity, but it also shows cases where student burden worsens. From an educational design perspective, this matters: a repaired response should not merely say less. It should keep the next student action clear, feasible, and appropriately demanding.

### 5.5 Automatic Graders Remain Auxiliary

LLM graders may help with scale, triage, or low-risk signals, but the dialogue-state v3 calibration shows that they cannot currently adjudicate high-risk critical bridge leakage alone. In the priority60 reference, critical recall is 0 and the major leakage false-negative rate is 1.000. That failure mode is too serious for automatic grading to take over expert review.

For EAIT readers, the broader point is that scalable educational evaluation still needs human judgment when the construct concerns a learner's reasoning opportunity. Rubric transparency and calibration reporting are safeguards, not optional details.

### 5.6 Practical Implications For Educational Technology Design

The design implication is not to make tutors withhold help. It is to make help controllable. In competitive-programming tutoring, feedback strength, bridge boundary, next action, and student burden have to be designed together. Bridge Contract-style constraints are useful because they force generation, review, and repair to refer to the same case-specific tutoring target.

Human review also plays a design role, not only an audit role. It defines the leakage boundary, reveals trade-offs between safe-but-unhelpful and helpful-but-leaky responses, and calibrates automatic graders for low-stakes use. This kind of human-in-the-loop evaluation is better suited to critical bridge leakage than model self-evaluation or a single automatic score.

### 5.7 Real-Student AIChat As Ecological-Validity And Replay-Planning Layers

The real-student AIChat material should be read as ecological-validity and replay-planning support, not as a system-performance experiment. Its `observed_current_aichat_response` field, also described in Chinese as `线上已展示 AIChat 回复（观察项，非实验条件）`, records the response that the existing online AIChat had already shown to the student. It is not one of the seven offline harnesses, not a baseline, not a control arm, and not a Repair output.

This distinction protects both the paper's evidence hierarchy and the educational interpretation. Real-AIChat-100 can show whether real student questions from our own teaching system can be expressed as dialogue-state cases with a missing bridge, surface anchor, context sufficiency judgment, and case-specific rubric. It cannot show that the deployed AIChat is superior, that active mode is validated, or that student learning outcomes improve.

Real-AIChat-Replay-30/50 would answer a different auxiliary question: whether the same fixed offline harnesses show different bridge-preserving behavior when the starting states come from real AIChat turns. Because replay responses would be generated offline and hidden from students, this evidence would remain a counterfactual validation layer rather than an online intervention. Any future shadow-mode or risk-triggered deployment should be reported as a separate deployment-readiness study rather than merged into the dialogue-state v3 main result.

### 5.8 Limitations

This study has eight main limitations. First, the headline slice is 31 cases / 217 response-level reviews and should be interpreted as bounded expert-reviewed evidence, not exhaustive CP tutoring coverage; the 217 reviews are response-level outputs nested within 31 case-level situations. Second, the 50 cases are curated high-risk dialogue-state cases rather than a random sample of all CP tutoring interactions, so the benchmark does not estimate population prevalence of critical bridge leakage. Third, student-ready, safe-ready, and rank outcomes are rater-sensitive, so sensitivity views are necessary. Fourth, priority60 adjudication is not a single definitive reference; it reduces uncertainty for high-priority disagreements but does not remove all rater differences. Fifth, DBox+Repair is a targeted 20-case sensitivity review, not a full 50-case double-coach condition. Sixth, DeepSeek-backed LLM-grader calibration has high critical false-negative risk and same-backend coupling, so automatic graders and judges remain auxiliary rather than replacements for human coaches. Seventh, the paper evaluates offline tutoring harnesses and separate real-AIChat ecological-validity protocols; it does not evaluate long-term learning outcomes, deployed AIChat superiority, online active-mode effectiveness, or population-level usage effects. Eighth, Real-AIChat-100 selection and Replay-30/50 generation/review require their own privacy, consent/reporting, selection-bias, and double-review checks before they can be reported beyond aggregate/process counts.

## 6. Conclusion

CP-MissingBridgeBench turns missing-bridge preservation and critical bridge leakage into reviewable constructs for competitive-programming LLM tutoring. It addresses a concrete educational-technology problem: how an LLM tutor can help a learner move forward without crossing the reasoning bridge for them.

The dialogue-state v3 evaluation set supports a bounded conclusion. On the 31-case `main_scaffold_eval` headline slice, DBox-inspired decomposition is a strong baseline; no-direct-solution prompting does not fully prevent critical bridge leakage; and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view. Those findings must be read together with paired uncertainty, rater sensitivity, Guard-only instrumentation boundaries, Repair stress-test boundaries, DBox+Repair fairness sensitivity, and LLM-grader limitations.

The paper does not claim that 50 cases cover all CP tutoring or that coach labels or priority60 adjudication provide one settled reference. It also does not treat guard instrumentation as rewrite evidence, infer Repair causality from main condition means, or assign LLM graders the role of human adjudication. Its contribution is a reproducible case-specific human-review benchmark for studying how LLM tutoring can support programming learners while preserving their opportunity to complete the missing bridge.

## 7. Ethics, Privacy, Data Availability, And AI Writing Disclosure

This manuscript uses the existing dialogue-state v3 evidence package and does not modify the main experiment, add a condition, recompute the main tables, or change online AIChat behavior. The fixed offline benchmark can make public its metadata, schemas, rubric definitions, aggregate tables, reproduction scripts, evidence manifest, and anonymized condition descriptions, subject to venue policy and author review.

Raw dialogue text, student code, full AIChat responses, identity fields, hash salts, reversible mappings, and any material that could identify a student, school, account, phone number, email address, or private learning context are not public release materials. If a real-student example is needed for the manuscript, it should be paraphrased, anonymized, and checked against the consent/reporting gate rather than copied from the private packet.

The real-student AIChat pilot remains a separate ecological-validity layer. The 5-case dry run and the 9-case focus/adjudication workflow can be described only as internal workflow closure, not as reportable model-performance evidence. While the consent/reporting gate is pending, this layer may report only aggregate/process counts, schema readiness, screening flow, and field-sufficiency issues. It must not report case-level leakage labels, individual hash tables, full student messages, complete code snippets, complete observed current-system responses, or identifiable examples.

The completed 5-case human coach dry run follows the same privacy boundary. The authors may say that the dry-run workflow was completed internally and passed structure validation, but they should not publish the private score distributions, leakage labels, coach notes, or paraphrased examples until consent/reporting eligibility is explicitly completed and documented.

AI writing assistance was used for drafting, editing, checklist generation, and evidence organization. The scientific claims, citation choices, numerical results, data boundaries, privacy choices, and final wording remain the responsibility of the human authors. Before submission, the manuscript still needs venue-specific checks for AI writing disclosure, citation verification, result-number verification, ethics/privacy review, and data availability wording.

## Appendix A. Case Inventory Table

This appendix table lists the 50 case-level tutoring situations used to organize the response-level review. It is a transparency inventory, not a new experimental condition. The `slice` and `slice_assignment_rationale` columns come from the dialogue-state v3 context-readiness audit; `bridge_family`, `surface_anchor`, `student_message_short`, and the case source fields come from the reviewed candidate case file. The 217 tutor responses in the headline scaffold analysis are generated by applying the 7 anonymized offline harnesses to the 31 `main_scaffold_eval` cases; the case-level unit remains the 31 tutoring situations, not the 217 response rows.

The `slice_assignment_rationale` column uses audit tags. These tags indicate whether the case primarily tests ordinary scaffolding, clarification safety, cautionary scaffold interpretation, or policy redirection.

| audit tag pattern | human-readable interpretation |
| --- | --- |
| `no_recent_dialogue` / `vague_question` | insufficient context, clarification expected |
| `recent_dialogue_ends_with_assistant` / `has_problem_context` | ordinary scaffold continuation |
| `pronoun_dependent_question` | depends on prior assistant context |
| `has_code_excerpt` | implementation/debugging context available |
| `safe_refusal` | direct-answer/code or policy-risk redirection |

Audit note on `dialogue_v3_045_debugging_evidence`: the context-readiness audit assigns this row to `policy_safety_slice` with `expected_tutor_move=safe_refusal` and `current_question_specificity=policy_request`, while the reviewed candidate case file records `expected_tutor_move=prerequisite_repair`. The slice is not reassigned here; the row is flagged as `needs_manual_audit` for human confirmation before submission.

| case_id | slice | bridge_family | surface_anchor | student_message_short | expected_tutor_move | slice_assignment_rationale |
| --- | --- | --- | --- | --- | --- | --- |
| `dialogue_v3_001_state_representation_semantics` | `clarification_safety_slice` | `state_representation_bridge` | `state_semantics` | 这个状态怎么想？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_002_state_representation_semantics` | `clarification_safety_slice` | `state_representation_bridge` | `state_semantics` | dp 这一格是啥意思？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_003_state_representation_semantics` | `clarification_safety_slice` | `state_representation_bridge` | `state_semantics` | 数组里到底存什么？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_004_state_representation_semantics` | `clarification_safety_slice` | `state_representation_bridge` | `state_semantics` | 状态维度怎么定？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_005_state_representation_semantics` | `clarification_safety_slice` | `state_representation_bridge` | `state_semantics` | 这里要记哪些量？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_006_state_representation_semantics` | `clarification_safety_slice` | `state_representation_bridge` | `state_semantics` | 我不会设状态。 | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_007_transition_recurrence_source` | `clarification_safety_slice` | `transition_recurrence_bridge` | `transition_design` | 分支该怎么列？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_008_transition_recurrence_source` | `clarification_safety_slice` | `transition_recurrence_bridge` | `transition_design` | 这里从哪转来？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_009_transition_recurrence_source` | `clarification_safety_slice` | `transition_recurrence_bridge` | `transition_design` | 这一步怎么递推？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_010_transition_recurrence_source` | `clarification_safety_slice` | `transition_recurrence_bridge` | `transition_design` | 前一个状态是哪种？ | `clarify_context` | no_recent_dialogue; vague_question; short_vague_question_without_dialogue; has_problem_context |
| `dialogue_v3_011_transition_recurrence_source` | `main_scaffold_eval` | `transition_recurrence_bridge` | `transition_design` | 我能想到一个来源，但没对应到具体题面动作。 | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_problem_context |
| `dialogue_v3_012_predicate_check_semantics` | `main_scaffold_eval` | `predicate_check_bridge` | `check_truth_direction` | 是不是 true 代表这个候选还可行？ | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_problem_context |
| `dialogue_v3_013_predicate_check_semantics` | `main_scaffold_eval` | `predicate_check_bridge` | `check_truth_direction` | true 就是这个候选值能满足限制。 | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_problem_context |
| `dialogue_v3_014_predicate_check_semantics` | `main_scaffold_eval` | `predicate_check_bridge` | `check_truth_direction` | 我理解 true 应该是当前候选能过限制。 | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_problem_context |
| `dialogue_v3_015_predicate_check_semantics` | `main_scaffold_eval` | `predicate_check_bridge` | `check_truth_direction` | 是不是 true 代表这个候选还可行？ | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_problem_context |
| `dialogue_v3_016_predicate_check_semantics` | `main_scaffold_eval` | `predicate_check_bridge` | `check_truth_direction` | true 就是这个候选值能满足限制。 | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_problem_context |
| `dialogue_v3_017_boundary_update_order` | `main_scaffold_eval` | `boundary_order_bridge` | `boundary_update` | 应该是看哪一边还是旧状态，避免被这轮更新覆盖。 | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_problem_context |
| `dialogue_v3_018_boundary_update_order` | `main_eval_with_caution` | `boundary_order_bridge` | `boundary_update` | 好像和旧值顺序有关，但从大到小还是从小到大我还没想明白。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_019_boundary_update_order` | `main_scaffold_eval` | `boundary_order_bridge` | `boundary_update` | 我知道要保护旧值，但不知道顺序怎么避免覆盖。 | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_problem_context |
| `dialogue_v3_020_boundary_update_order` | `main_eval_with_caution` | `boundary_order_bridge` | `boundary_update` | 我能看出要看更新前后，可是不知道哪一个值会被覆盖。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_021_boundary_update_order` | `main_scaffold_eval` | `boundary_order_bridge` | `boundary_update` | 好像和旧值顺序有关，但从大到小还是从小到大我还没想明白。 还分不清新旧值。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_022_modeling_object_relation` | `main_scaffold_eval` | `modeling_bridge` | `modeling_objects_relations` | 我能列出对象，但它们之间到底是覆盖、相邻还是依赖，我不确定。 关系我还没列清。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_023_modeling_object_relation` | `main_eval_with_caution` | `modeling_bridge` | `modeling_objects_relations` | 对象我大概知道，可关系怎么连还没想明白。 对象之间怎么连不确定。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_024_modeling_object_relation` | `main_eval_with_caution` | `modeling_bridge` | `modeling_objects_relations` | 我知道题面里有哪些东西，但不知道该抽成哪种关系。 覆盖关系我说不准。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_025_modeling_object_relation` | `main_scaffold_eval` | `modeling_bridge` | `modeling_objects_relations` | 我能列出对象，但它们之间到底是覆盖、相邻还是依赖，我不确定。 关系我还没列清。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_026_modeling_object_relation` | `main_eval_with_caution` | `modeling_bridge` | `modeling_objects_relations` | 对象是时间段还是选择本身？我感觉关系有点反。 覆盖关系我搞反了。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_027_aggregation_contribution_summary` | `main_scaffold_eval` | `aggregation_contribution_bridge` | `contribution_marking` | 对 [L,R] 加 X 的影响我能看出来，但不知道标记应该落在 L、R 还是抵消位置。这里我经常写成凭感觉加减。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_028_aggregation_contribution_summary` | `main_scaffold_eval` | `aggregation_contribution_bridge` | `contribution_marking` | 我能看出一次操作会影响一路上的值，但不知道哪些位置是直接加，哪些位置是为了抵消。这里换一个询问我就乱。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_029_aggregation_contribution_summary` | `main_scaffold_eval` | `aggregation_contribution_bridge` | `contribution_marking` | 单个星球或区间的影响我能跟，但要把很多次影响汇总起来时，我不知道应该在哪些位置打标记。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_030_aggregation_contribution_summary` | `main_scaffold_eval` | `aggregation_contribution_bridge` | `contribution_marking` | 路径上的贡献怎么累起来我懂一点，但到前缀汇总或公共点附近时，不知道加减点应该放在哪里。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_031_data_structure_operation_semantics` | `main_scaffold_eval` | `data_structure_bridge` | `ds_operation_semantics` | 我知道要 update/query，但不知道结构里每个节点到底该存什么摘要，才能回答题目要的数量或最值。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_032_data_structure_operation_semantics` | `main_scaffold_eval` | `data_structure_bridge` | `ds_operation_semantics` | 一次修改之后，节点里的值要怎么保持正确我没想清。查询时为什么能直接拿这些维护量拼出答案？ | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_033_data_structure_operation_semantics` | `main_scaffold_eval` | `data_structure_bridge` | `ds_operation_semantics` | 我写了个小版本，query 输出和手算差一点。我想先知道一次 update 后，结构里哪个摘要量应该发生变化。 | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_034_data_structure_operation_semantics` | `main_scaffold_eval` | `data_structure_bridge` | `ds_operation_semantics` | 我不太明白查询为什么能由这些维护量拼出来。是不是要先确认每个节点维护的对象和合并含义？ | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_035_data_structure_operation_semantics` | `main_scaffold_eval` | `data_structure_bridge` | `ds_operation_semantics` | 更新后结果不稳，我怀疑不是下标问题，而是某个维护量没更新对。应该先检查哪个摘要量？ | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_036_correctness_invariant` | `main_scaffold_eval` | `correctness_bridge` | `correctness_invariant` | 我试着比较两个相邻选择，但不知道要看总目标值还是局部贡献，感觉还没形成交换理由。样例能跟，可是一换顺序我就不知道为什... | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_037_correctness_invariant` | `main_scaffold_eval` | `correctness_bridge` | `correctness_invariant` | 如果把这两个选择顺序换一下，我不确定哪个量不会变差。样例能跟，但证明这一步不会写，我想先确认比较的对象到底是哪一个，... | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_code_excerpt; has_problem_context |
| `dialogue_v3_038_correctness_invariant` | `main_scaffold_eval` | `correctness_bridge` | `correctness_invariant` | 我能猜到要保持某个不变量，但不知道相邻两步交换后到底保持了什么，为什么答案不会更差。现在我只是凭直觉说贪心可行，换一... | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_039_correctness_invariant` | `main_scaffold_eval` | `correctness_bridge` | `correctness_invariant` | 我现在只会说这个贪心看起来对，但说不出局部选择换一下会不会影响全局目标。能不能先让我比较一个很小的相邻交换，看交换前... | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_040_correctness_invariant` | `main_scaffold_eval` | `correctness_bridge` | `correctness_invariant` | 我想用交换法想这题，但卡在比较两种相邻选择：到底要证明哪个指标不变或不变差？我怕一上来就写证明会变成背模板，所以想先... | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_041_implementation_boundary` | `main_scaffold_eval` | `implementation_bridge` | `implementation_boundary` | 我把这一步写进代码了，不过有一组样例不对，可能是初始化或者下标错了。 我对《[NOIP 2005 普及组] 循环》的... | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_code_excerpt; has_problem_context |
| `dialogue_v3_042_implementation_boundary` | `main_scaffold_eval` | `implementation_bridge` | `implementation_boundary` | 我写了个小版本，输出和手算差一点，不知道该先查哪一个中间量。 我想先知道应该打印哪个中间量，别一上来就整段重写。 我... | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_043_implementation_boundary` | `main_scaffold_eval` | `implementation_bridge` | `implementation_boundary` | 我这里卡在最基础的地方：空格算几下，字母又怎么数？能先拿一个字母带我核一下吗？ 我先想把一个字母和一个空格的按键次数... | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_044_implementation_boundary` | `main_scaffold_eval` | `implementation_bridge` | `implementation_boundary` | 立体图里一个方块画到字符图上时，我不知道单个字符位置到底对应题面里的哪一格、哪条边或哪个角。样例图我能看，但自己画时... | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_045_debugging_evidence` | `policy_safety_slice` | `debugging_bridge` | `debugging_evidence` | 我知道要调试，但不知道“最小反例”该怎么选。能不能先让我挑一个很小输入，看哪个中间量应该是多少？我现在不是想改完整代... | `safe_refusal` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context; audit_expected_tutor_move=safe_refusal; reviewed_candidate_expected_tutor_move=prerequisite_repair; needs_manual_audit |
| `dialogue_v3_046_debugging_evidence` | `main_scaffold_eval` | `debugging_bridge` | `debugging_evidence` | 这题我样例能跟一点，但不知道该先手算哪一秒、哪个魔法值或距离变量。能先帮我把检查点缩小吗？我现在调试时只会整段跑，看... | `micro_scaffold` | recent_dialogue_ends_with_assistant; has_code_excerpt; has_problem_context |
| `dialogue_v3_047_debugging_evidence` | `main_scaffold_eval` | `debugging_bridge` | `debugging_evidence` | 网络连接这题我不知道该造哪种最小坏地址来查错，也不知道该先检查解析结果还是连接表。比如样例能过，但一遇到前导零、端口... | `continue_prior_scaffold` | recent_dialogue_ends_with_assistant; pronoun_dependent_question; has_code_excerpt; has_problem_context |
| `dialogue_v3_048_policy_request` | `policy_safety_slice` | `policy_bridge` | `policy_safe_response` | 可以直接给我完整做法吗？如果不行，就告诉我最该先补哪一步。 你可以先不给答案，但最好给我一个能马上动手验证的小检查点... | `safe_refusal` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_049_policy_request` | `policy_safety_slice` | `policy_bridge` | `policy_safe_response` | 能不能直接告诉我完整思路或者代码，我赶时间。 如果不能给完整代码，那请先把我应该补充的最小信息说清楚。 我希望先确认... | `safe_refusal` | recent_dialogue_ends_with_assistant; has_problem_context |
| `dialogue_v3_050_policy_request` | `policy_safety_slice` | `policy_bridge` | `policy_safe_response` | 我现在有点想直接看完整题解和代码，不然不知道从哪里继续。 我不是想跳过学习，只是《[CSP-J 2024] 接龙》卡... | `safe_refusal` | recent_dialogue_ends_with_assistant; has_problem_context |


## Appendix B. Real-Student AIChat External-Validation Boundary

The real-student online AIChat material is included only as an ecological-validity, taxonomy-transfer, and replay-planning layer. The data source is our own online AIChat / teaching system. The pilot and replay protocols do not use Luogu discussion areas, public forums, third-party Q&A sites, social media, or any other public community data.

The online data funnel is reported at three levels. Layer 1 summarizes the online log corpus: 1156 raw AIChat message rows, 87 sessions, and 578 paired user-assistant turns. Layer 2 screens 137 substantial candidate turns across 59 candidate sessions; this is a lightweight candidate-turn screening pool, not a deep annotation sample. Layer 3 contains 30 selected pilot candidate cases covering 11 hashed students and 15 hashed problems; these cases are candidates for full taxonomy/rubric annotation after privacy and consent/reporting gates.

A 5-case human coach dry run has been completed as an internal process check. The public-safe status is: 5 cases reviewed internally, 0 structure-validation errors, 5 cases passing privacy review for internal review, and 0 cases reportable after the consent/status gate. The private workbook and private score summary remain local; case-level labels, leakage distributions, score distributions, student text, code, full AIChat replies, and coach notes are not reported in the manuscript while the reporting gate is pending.

A 30-case internal coach-review packet has also been prepared with full problem statements. Fifteen problem statements come from the local `latest.ndjson` snapshot and fifteen come from author-specified JMYSOJ problem pages for problems not present in the local snapshot. These problem statements are used only to make real-student cases reviewable by coaches; the full 30-case packet has not completed full human review and is not reported as a result.

Within that 30-case packet, an internal triage workflow selected 9 focus cases for second-coach review. The focus workflow has been closed internally: 7 rows received second-coach review status, and the remaining 2 rows were resolved through a separate adjudication packet. The post-adjudication public status remains gate-limited: the workflow is closed, but `reportable case-level evidence = 0` because the consent/reporting gate is not complete. These counts are workflow status only, not leakage rates, score distributions, or model-performance results.

Real-AIChat-100, if constructed, would select 80-100 target turns from the candidate pool, or `N <= 100` if fewer cases satisfy privacy, consent/reporting, and context criteria. It is observational only: it checks whether real AIChat target turns can be described using CP-MissingBridgeBench bridge families, surface anchors, context-sufficiency labels, and case-specific rubric fields. It does not compare the seven offline harnesses.

Real-AIChat-Replay-30/50, if conducted, would select 30 context-sufficient Real-AIChat-100 cases first, with optional expansion to 50. Replay would generate offline counterfactual responses from the fixed harnesses on the same real-student starting states and send anonymized responses to blind coach review. Replay is auxiliary validation and is not merged into the dialogue-state v3 main results.

The field `observed_current_aichat_response` means the current system response already shown by online AIChat. In the Chinese coach-review template, the same field is labeled `线上已展示 AIChat 回复（观察项，非实验条件）`. This field must not be described as a baseline, experimental condition, control arm, online comparison arm, or Repair output. It is an observed response used to test whether the benchmark rubric can be applied to real dialogue-state cases.

The real AIChat layers do not add a main experiment condition, do not recompute dialogue-state v3 tables, do not evaluate learning outcomes, and do not validate deployed-system superiority. Before consent/reporting gates are complete, public reporting is limited to aggregate counts, workflow status, schema readiness, and field-sufficiency observations. Case-level labels and examples remain non-reportable.
