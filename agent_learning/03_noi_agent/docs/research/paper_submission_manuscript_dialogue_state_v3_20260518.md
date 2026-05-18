# CP-MissingBridgeBench: Turn-Level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation for LLM Tutors in Competitive Programming

## Draft Status

This is a single-file submission manuscript skeleton assembled from the dialogue-state v3 evidence package. It adds no experiment, changes no data, and does not connect online active mode. It is intended as a paper-writing surface, not as a replacement for the underlying evidence reports.

Main interpretation boundaries:

- The primary headline uses only the 31-case `main_scaffold_eval` slice.
- Coach A, Coach B, and priority60 adjudication are expert reference views, not gold.
- Guard-only is guard-instrumented runtime signal, not final-response rewrite.
- Repair causal evidence comes from same-candidate stress testing.
- DBox+Repair is targeted fairness sensitivity, not a full main condition.
- DeepSeek LLM grader calibration is auxiliary and cannot replace human review.

## Abstract

Large language models are increasingly used as programming tutors, but avoiding final code or direct answers is not sufficient for pedagogically safe help. In competitive programming, a short hint can still reveal the key intermediate reasoning step the student should derive next. We call this local reasoning gap a missing bridge, and define critical bridge leakage as prematurely completing that bridge without necessarily giving the full solution.

We introduce CP-MissingBridgeBench, a turn-level evaluation framework for LLM tutors in competitive programming. Each case includes problem context, recent dialogue, a student message, and a case-specific rubric specifying success criteria, forbidden content, acceptable reveal, and the expected next student action. Our dialogue-state v3 evidence package contains 50 reviewed candidate cases, 7 anonymized tutoring-harness conditions, and 350 AI responses double-reviewed by two coaches with priority adjudication, paired uncertainty, slice analysis, Repair same-candidate stress testing, DBox+Repair fairness sensitivity, and DeepSeek LLM-grader calibration.

The evidence shows that CP-MissingBridgeBench reveals quality-safety-burden trade-offs across tutoring harnesses. DBox-inspired decomposition is a strong baseline; no-direct-solution prompting does not eliminate critical bridge leakage; and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view. At the same time, student-ready and rank judgments are rater-sensitive, Guard-only is only instrumentation in the current pipeline, Repair reduces leakage in same-candidate stress testing with a student-burden trade-off, and LLM graders remain auxiliary rather than replacements for human review.

## 1. Introduction

Large language models are increasingly used as programming tutors, but evaluating their help remains difficult. A response can be polite, concise, and compliant with a "do not give the answer" instruction while still removing the central reasoning work the student should perform. This problem is especially sharp in competitive programming, where learning often depends on crossing a small but decisive reasoning gap: understanding what a state represents, why a transition is valid, what a feasibility check means, which boundary should move, or what evidence would isolate a bug.

We call this gap a missing bridge: the local reasoning bridge between what the student currently knows and the next useful solving action. We define critical bridge leakage as a tutoring failure in which the model does not necessarily reveal the full solution or code, but prematurely completes that missing bridge for the student. This makes critical bridge leakage different from ordinary answer leakage. A tutor may avoid final code and still say too much; conversely, a tutor may reveal limited context or ask a focused question without leaking the bridge.

Existing programming-help safeguards often focus on direct answer or code avoidance. This is necessary but insufficient for turn-level tutoring. In competitive programming, a short hint can be overly complete if it gives away the current invariant, predicate meaning, update rule, or proof step. At the same time, overly cautious refusal can be pedagogically empty. The relevant evaluation target is therefore not only "did the model give the answer?", but whether the response preserves an appropriate amount of student reasoning while still providing useful, grounded scaffolding.

We introduce CP-MissingBridgeBench, a turn-level evaluation framework for LLM tutors in competitive programming. Each case includes the problem context, recent dialogue, the student's current message, and a case-specific rubric specifying success criteria, forbidden content, acceptable reveal, and the expected next student action. The benchmark evaluates tutor responses along quality, safety, and student-burden dimensions rather than reducing tutoring to a single scalar score.

This paper makes four contributions:

1. We define missing bridge as a turn-level representation of the student's current reasoning gap in competitive-programming tutoring.
2. We define critical bridge leakage, a safety-and-pedagogy failure mode beyond direct answer or code leakage.
3. We construct a case-specific human-review protocol with success criteria, forbidden content, acceptable reveal, expected next action, double review, priority adjudication, and sensitivity reporting.
4. We evaluate strong prompt-only, no-direct-solution, DBox-inspired, Bridge-guided, Bridge Contract, Guard, and Repair harnesses under a common dialogue-state v3 evidence package, emphasizing quality-safety-burden trade-offs rather than absolute system victory.

## 2. Related Work

Prior work on dialogue tutoring and Socratic guidance studies how models can ask questions, elicit explanations, and scaffold student reasoning rather than directly provide final answers [macina2023mathdial; maurya2024mrbench; wang2023bridge]. CP-MissingBridgeBench shares this emphasis on preserving learner reasoning, but focuses on competitive-programming turns where the critical unit is often a localized bridge: a state meaning, transition source, check predicate, invariant, or debugging evidence target.

Programming-help systems and benchmarks often include guardrails against providing full solutions or code [liffiton2023codehelp; kazemitabaar2024codeaid]. These constraints are important, but our results show why they are not enough for competitive-programming tutoring: in dialogue-state v3, a no-direct-solution baseline is stronger than prompt-only, yet still produces critical bridge leakage.

DBox and related step-based programming tutors emphasize decomposing programming tasks, tracking substeps, and supporting learners through structured hints [ma2025dbox]. We use DBox as a literature anchor for a DBox-inspired decomposition baseline. Our condition is not a DBox reproduction: it does not implement the interactive step-tree UI, multi-turn co-decomposition, progressive reveal, code-step alignment, or student learning-gain study from the original system.

Adaptive scaffolding systems such as EDF/Copa organize tutoring around evidence, decision, and feedback, using learner-state estimates and dialogue policies to decide how to respond [cohn2026edf]. CP-MissingBridgeBench is related in spirit but differs in domain and granularity: it evaluates single-turn competitive-programming tutor responses with recent dialogue and problem context, not multi-turn classroom learning outcomes.

Rubric-based evaluation and LLM-as-judge methods provide scalable ways to compare open-ended responses [zheng2023llmjudge; kim2023prometheus; maurya2024mrbench; gunjal2025rar]. CP-MissingBridgeBench adopts structured rubrics, but our calibration shows that automatic graders remain insufficient for high-stakes critical bridge leakage. Agent-evaluation work similarly argues that evaluations should measure whole harnesses rather than isolated model calls [anthropic2026agentevals].

## 3. Benchmark and Review Protocol

CP-MissingBridgeBench evaluates a specific failure mode in competitive-programming tutoring: the student has expressed a partial idea or blocker, but still lacks the key reasoning bridge between their current state and the next useful solving action. A missing bridge is not a fixed algorithm label. The same DP problem, for example, may involve different missing bridges at different turns: state semantics, transition source, boundary initialization, correctness reasoning, or implementation debugging.

Critical bridge leakage occurs when a tutor does not directly provide a full solution or full code, but prematurely reveals the intermediate reasoning that the student should still derive. This is different from ordinary informative tutoring. A good tutor may provide context, light hints, checks, or low-burden next steps. The leakage risk comes from completing the current missing bridge too early.

The taxonomy uses three layers:

```text
cognitive bridge family + leakage mechanism + surface anchor
```

`state_representation_semantics`, `transition_recurrence_source`, and `predicate_check_semantics` are operational cognitive bridge families. DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, and debugging trace are surface anchors that instantiate broader cognitive bridges and leakage mechanisms in concrete algorithmic contexts. The benchmark should therefore not be described as only covering DP/check/lazy/tree/local-code scenes.

Dialogue-state v3 contains 50 reviewed candidate cases. Each case preserves the current dialogue state rather than presenting only an isolated problem statement and question. The 50 cases are separated by paper use:

| slice | case_n | paper use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | Main scaffold-quality, leakage, and burden comparison |
| `main_eval_with_caution` | 5 | Sensitivity / appendix |
| `clarification_safety_slice` | 10 | Clarification, non-over-inference, and context-insufficient safety |
| `policy_safety_slice` | 4 | Safety redirection for direct answer/code requests |

Before scoring each case, reviewers use a case-specific rubric specifying `success_criteria`, `forbidden_content`, `critical_bridge_boundary`, `acceptable_reveal`, and `expected_student_next_action`. This makes the review conditional on the student's current state and turn-level teaching goal, rather than on a generic notion of whether a response sounds helpful.

## 4. Experimental Setup

The main human review compares 7 anonymized conditions, for 350 responses in total. Coaches do not see condition names during blind review. After de-anonymization, the conditions are:

| condition | role | interpretation boundary |
| --- | --- | --- |
| `enhanced_prompt_only_clean` | Strong prompt-only baseline | No case-specific Bridge Contract. |
| `codehelp_codeaid_clean` | No-direct-solution baseline | Tests whether no-direct-code / no-direct-solution guardrails are sufficient. |
| `dbox_inspired_clean` | Literature-inspired decomposition baseline | DBox-inspired single-turn scaffold; not a DBox reproduction. |
| `dbox_inspired_guard` | DBox-inspired + guard-instrumented variant | Guard-only provides runtime leakage signal; it does not rewrite final responses. |
| `bridge_guided_dbox_style_guard` | Bridge-guided decomposition variant | Uses bridge signal to guide a DBox-style response; still guard-instrumented. |
| `bridge_contract_compact_guard` | Bridge Contract compact + guard-instrumented method | Uses compact bridge contract and guard signal; Guard-only is not a rewrite condition. |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard/Repair method | The student-visible response may come from Repair; main means are condition-level trends. |

All conditions are offline evaluation harnesses, not the online default AIChat system.

Coach A and Coach B each completed a full blind review of all 350 responses. Reviewers read the problem context, case-specific rubric, recent dialogue, student message, and candidate response. They then fill primary metrics, diagnostic metrics, and reliability fields. Coach A, Coach B, and priority60 adjudication are expert reference / adjudicated sensitivity views, not gold.

Primary metrics include `overall_quality`, `student_ready_pass`, `safe_ready_pass`, `critical_leakage_label`, `scaffold_sufficiency`, and `student_response_burden`. The paper organizes evidence by class: main result, sensitivity, slice analysis, paired uncertainty, stress test, fairness sensitivity, and calibration.

## 5. Results

### 5.1 Human Review Reliability

Dialogue-state v3 contains 50 reviewed candidate cases, 7 anonymized tutoring-harness conditions, and 350 AI responses. Coach A and Coach B both completed all 350 blind reviews. Overall-quality exact agreement is 0.2829, while within-1 agreement is 0.8429. Leakage-label exact agreement is 0.6714. Critical-binary exact agreement is 0.9029, but kappa is 0.2511. Rank preference is more divided, with top-1 and last-place agreement both at 10/50.

We adjudicated 60 high-priority disagreements: `use_A=29`, `use_B=9`, and `new_label=22`. This means no single coach label should be treated as gold, and student-ready, safe-ready, and rank are rater-sensitive outcomes. We therefore report the primary view together with paired uncertainty, slice analysis, and rater-view sensitivity.

### 5.2 Main Scaffold Evaluation

The main result uses only the 31-case `main_scaffold_eval` slice. The primary metrics under `priority60 adjudicated + Coach A` are:

| condition | overall | student-ready | safe-ready | major+answer leakage |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.032 | 7/31 | 7/31 | 9 |
| `codehelp_codeaid_clean` | 3.710 | 19/31 | 19/31 | 2 |
| `dbox_inspired_clean` | 3.774 | 21/31 | 21/31 | 2 |
| `dbox_inspired_guard` | 3.774 | 23/31 | 23/31 | 2 |
| `bridge_guided_dbox_style_guard` | 3.742 | 20/31 | 20/31 | 2 |
| `bridge_contract_compact_guard` | 4.000 | 23/31 | 23/31 | 0 |
| `bridge_contract_compact_guard_repair` | 4.065 | 22/31 | 22/31 | 0 |

`bridge_contract_compact_guard_repair` has the highest overall score under the primary view, and both Bridge Contract compact conditions have zero major+answer leakage. At the same time, `dbox_inspired_guard` reaches 23/31 student-ready and safe-ready, matching or approaching Bridge Contract compact guard. The result should therefore be framed as a quality-safety-burden trade-off: Bridge Contract compact + Guard/Repair shows favorable overall and high-severity leakage-control trends, while DBox-inspired decomposition remains a strong baseline.

`codehelp_codeaid_clean` is substantially stronger than `enhanced_prompt_only_clean`, but still has 2 major+answer leakage rows. This supports the core motivation for critical bridge leakage: avoiding direct code or a full solution does not prevent premature completion of the student's current missing bridge.

### 5.3 Paired Uncertainty

Same-case paired comparisons constrain the strength of the claims. `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` has mean overall delta +0.290, W/T/L 14/10/7, and 2 fewer major+answer leakage rows, but its paired bootstrap 95% CI is [-0.097, +0.645] with paired permutation p=0.2016. This supports favorable trend / trade-off wording, not significant dominance.

`bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` has mean overall delta +0.065, W/T/L 7/18/6, and equal major+answer leakage. The main experiment condition mean therefore cannot by itself establish a causal Repair effect.

`codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` has mean overall delta +0.677, 95% CI [+0.258, +1.065], paired p=0.0046, 12 more safe-ready rows, and 7 fewer major+answer leakage rows. Prompt-only is not stable enough in dialogue-state CP tutoring, but no-direct-solution remains not safety-complete.

### 5.4 Slice and Sensitivity Analysis

All-50 sensitivity shows `bridge_contract_compact_guard_repair` with the highest overall score under Coach A only, Coach B only, priority60+CoachA, and priority60+CoachB, but this average mixes slices with different paper uses and is therefore supplemental robustness only. The main scaffold slice shows a relatively consistent overall trend. Student-ready, safe-ready, and rank are more sensitive to rater strictness. The paper should not rely on a single rater view.

### 5.5 Observed Error Taxonomy

The observed error taxonomy uses `general tutoring failure type x operational cognitive bridge family x surface anchor`. Level 1 includes critical bridge leakage, answer/code leakage, over-complete micro-example, wrong/shifted focus, under-scaffolded, excessive burden, context misalignment, over-safe refusal, factual/algorithmic error, and policy/direct-answer handling failure. Level 2 includes representation semantics, transition/action mapping, predicate/decision semantics, ordering/dependency control, modeling relation, aggregation/contribution accounting, data-structure operation mapping, correctness/invariant reasoning, implementation boundary, debugging evidence, and policy-request handling. DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, and debugging trace are Level 3 surface anchors.

Thus, the taxonomy is not a list of concrete algorithm scenes. It is an observed operational taxonomy, not a universal taxonomy.

### 5.6 Repair and DBox+Repair Sensitivity

Repair causality comes from the 30-pair same-candidate before/after stress test. Repair improves leakage severity in 16/30 pairs, preserves it in 14/30, and worsens it in 0/30. Major leakage falls from 7/30 to 0/30, and mean overall increases from 3.367 to 3.633. The cost is student burden: burden improved / same / worsened is 2/16/12.

The DBox+Repair targeted fairness add-on covers 20 headline-sensitive cases, not a full 50-case double-coach main experiment. DBox+Repair has overall 3.55, safe-ready 11/20, and no/minor/major+answer leakage 14/6/0. Relative to the same-case DBox Guard subset, it modestly improves overall by +0.15 and reduces major+answer leakage from 2 to 0. Relative to Bridge Contract compact + Guard/Repair on the same 20 cases, Bridge+Repair remains +0.50 overall, W/T/L 12/5/3, and +4 safe-ready.

Together, these results support Repair as a leakage-reduction intervention in fixed-candidate stress testing and show that Repair can also help the DBox-inspired baseline. They also show a burden trade-off, and DBox+Repair remains sensitivity evidence only.

### 5.7 DeepSeek LLM Grader Calibration

LLM grader calibration only evaluates whether automatic graders can serve as scalable auxiliary signals. The paper-facing calibration uses DeepSeek `deepseek-v4-flash` with thinking disabled.

On the priority60 reference, the case-specific bridge-rubric judge improves some auxiliary metrics over a generic rubric: leakage-label accuracy is 0.617 vs 0.583, student-ready agreement is 0.467 vs 0.433, and safe-ready agreement is 0.533 vs 0.400. Safety-critical metrics remain unacceptable: both generic and case-specific DeepSeek graders have critical recall 0 and major leakage false-negative rate 1.000.

Therefore, the LLM grader cannot replace human review or adjudication. Kimi-backed calibration is retained only as an exploratory/tooling record because it uses a different backend and shows backend sensitivity.

## 6. Discussion

CP-MissingBridgeBench's main contribution is not proving that one harness is the absolute winner. It makes missing bridges and critical bridge leakage explicit, annotatable, and reproducible evaluation objects. The current evidence package shows that prompt-only is unstable, no-direct-solution does not imply no critical bridge leakage, DBox-inspired decomposition is a strong baseline, and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view.

The rule "do not give the answer or code" is too coarse for tutoring. A tutor can avoid full code and the final answer while still revealing the intermediate reasoning bridge the student should derive. CP-MissingBridgeBench captures this risk through case-specific rubrics that define success criteria, forbidden content, acceptable reveal, and expected student next action, separating helpful scaffolding from premature bridge completion.

Guard-only conditions are instrumentation / runtime signal in the current main experiment. When the Leakage Judge returns `rewrite`, it does not alter `final_response_text`; only `block` triggers fallback, and block=0 in this main run. Guard-only should therefore not be described as fixing final outputs.

Repair can be described as a leakage-reduction intervention supported by same-candidate stress evidence, but not as a causal effect proven by main-experiment condition means alone. It reduces leakage severity while often increasing student burden.

This study has clear limitations. First, the 50-case set is a high-risk dialogue-state CP tutoring evidence candidate, not full CP tutoring coverage. Second, student-ready, safe-ready, and rank are sensitive to rater strictness. Third, priority60 adjudication is not gold; it only reduces uncertainty for high-priority disagreements. Fourth, DBox+Repair is a 20-case targeted sensitivity add-on, not a full main condition. Fifth, the DeepSeek-backed LLM grader has high critical false-negative risk and cannot replace human review.

## 7. Conclusion

This paper argues that competitive-programming tutoring needs an evaluation target finer than direct answer or code leakage. The central pedagogical risk is often local: a tutor can preserve the final answer while still completing the student's current missing bridge. CP-MissingBridgeBench makes this risk explicit through case-specific rubrics, human review, and evidence-class reporting.

The current contribution is a reproducible evaluation framework and evidence package for studying missing-bridge preservation, not a claim that one tutor harness has fully solved competitive-programming tutoring. Future work should broaden the benchmark across more topics, student states, and real dialogue distributions; add stronger multi-rater adjudication for rater-sensitive outcomes; run fuller repair-enabled baseline comparisons where needed; and improve automatic graders for critical bridge leakage without treating them as gold.

## Reproducibility Checklist

Run before submission:

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_submission.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
```

The evidence chain is documented in `dialogue_state_v3_evidence_manifest_20260518.json`.
