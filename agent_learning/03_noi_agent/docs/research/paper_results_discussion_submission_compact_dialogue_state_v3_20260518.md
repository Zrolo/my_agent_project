# Paper Results / Discussion Submission Compact: Dialogue-State v3 20260518

## Scope

This document is a submission-compact Results / Discussion draft. It does not add experiments or modify data. It reuses the dialogue-state v3 evidence package: human review, priority60 adjudication, paired uncertainty, Repair same-candidate stress, DBox+Repair targeted fairness sensitivity, and DeepSeek LLM grader calibration.

The primary result view is fixed as:

```text
main_scaffold_eval slice + priority60 adjudicated + Coach A
```

Coach A only, Coach B only, priority60 + Coach B, all-50 aggregates, and non-main slices are sensitivity / appendix evidence. All "trend" wording in this document is bounded by the evidence package and should not be read as broad significant superiority.

## 4 Results

### 4.1 Human Review Reliability

Dialogue-state v3 contains 50 reviewed candidate cases, 7 anonymized tutoring-harness conditions, and 350 AI responses. Coach A and Coach B both completed all 350 blind reviews. Overall-quality exact agreement is 0.2829, while within-1 agreement is 0.8429. Leakage-label exact agreement is 0.6714. Critical-binary exact agreement is 0.9029, but kappa is 0.2511. Rank preference is more divided, with top-1 and last-place agreement both at 10/50.

We adjudicated 60 high-priority disagreements: `use_A=29`, `use_B=9`, and `new_label=22`. This means no single coach label should be treated as gold, and student-ready, safe-ready, and rank are rater-sensitive outcomes. We therefore report the primary view together with paired uncertainty, slice analysis, and rater-view sensitivity.

### 4.2 Main Scaffold Evaluation

The main result uses only the 31-case `main_scaffold_eval` slice. Table 1 reports the primary metrics under `priority60 adjudicated + Coach A`.

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

### 4.3 Paired Uncertainty

Same-case paired comparisons constrain the strength of the claims. `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` has mean overall delta +0.290, W/T/L 14/10/7, and 2 fewer major+answer leakage rows, but its paired bootstrap 95% CI is [-0.097, +0.645] with paired permutation p=0.2016. This supports favorable trend / trade-off wording, not significant dominance.

`bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` has mean overall delta +0.065, W/T/L 7/18/6, and equal major+answer leakage. The main experiment condition mean therefore cannot by itself establish a causal Repair effect.

`codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` has mean overall delta +0.677, 95% CI [+0.258, +1.065], paired p=0.0046, 12 more safe-ready rows, and 7 fewer major+answer leakage rows. Prompt-only is not stable enough in dialogue-state CP tutoring, but no-direct-solution remains not safety-complete.

### 4.4 Slice And Sensitivity Analysis

The 50 cases are separated into `main_scaffold_eval`, `main_eval_with_caution`, `clarification_safety_slice`, and `policy_safety_slice`. All-50 sensitivity shows `bridge_contract_compact_guard_repair` with the highest overall score under Coach A only, Coach B only, priority60+CoachA, and priority60+CoachB, but this average mixes slices with different paper uses and is therefore supplemental robustness only.

The main scaffold slice shows a relatively consistent overall trend. Student-ready, safe-ready, and rank are more sensitive to rater strictness. The paper should not rely on a single rater view.

### 4.5 Observed Error Taxonomy

The observed error taxonomy uses:

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

Level 1 includes critical bridge leakage, answer/code leakage, over-complete micro-example, wrong/shifted focus, under-scaffolded, excessive burden, context misalignment, over-safe refusal, factual/algorithmic error, and policy/direct-answer handling failure. Level 2 includes representation semantics, transition/action mapping, predicate/decision semantics, ordering/dependency control, modeling relation, aggregation/contribution accounting, data-structure operation mapping, correctness/invariant reasoning, implementation boundary, debugging evidence, and policy-request handling. DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, and debugging trace are Level 3 surface anchors.

Thus, the taxonomy is not a list of concrete algorithm scenes. It is an observed operational taxonomy, not a universal taxonomy.

### 4.6 Repair And DBox+Repair Sensitivity

Repair causality comes from the 30-pair same-candidate before/after stress test. Repair improves leakage severity in 16/30 pairs, preserves it in 14/30, and worsens it in 0/30. Major leakage falls from 7/30 to 0/30, and mean overall increases from 3.367 to 3.633. The cost is student burden: burden improved / same / worsened is 2/16/12.

The DBox+Repair targeted fairness add-on covers 20 headline-sensitive cases, not a full 50-case double-coach main experiment. DBox+Repair has overall 3.55, safe-ready 11/20, and no/minor/major+answer leakage 14/6/0. Relative to the same-case DBox Guard subset, it modestly improves overall by +0.15 and reduces major+answer leakage from 2 to 0. Relative to Bridge Contract compact + Guard/Repair on the same 20 cases, Bridge+Repair remains +0.50 overall, W/T/L 12/5/3, and +4 safe-ready.

Together, these results support Repair as a leakage-reduction intervention in fixed-candidate stress testing and show that Repair can also help the DBox-inspired baseline. They also show a burden trade-off, and DBox+Repair remains sensitivity evidence only.

### 4.7 DeepSeek LLM Grader Calibration

LLM grader calibration only evaluates whether automatic graders can serve as scalable auxiliary signals. The paper-facing calibration uses DeepSeek `deepseek-v4-flash` with thinking disabled.

On the priority60 reference, the case-specific bridge-rubric judge improves some auxiliary metrics over a generic rubric: leakage-label accuracy is 0.617 vs 0.583, student-ready agreement is 0.467 vs 0.433, and safe-ready agreement is 0.533 vs 0.400. Safety-critical metrics remain unacceptable: both generic and case-specific DeepSeek graders have critical recall 0 and major leakage false-negative rate 1.000.

Therefore, the LLM grader cannot replace human review or adjudication. Kimi-backed calibration is retained only as an exploratory/tooling record because it uses a different backend and shows backend sensitivity.

## 5 Discussion

### 5.1 What The Benchmark Shows

CP-MissingBridgeBench's main contribution is not proving that one harness is the absolute winner. It makes missing bridges and critical bridge leakage explicit, annotatable, and reproducible evaluation objects. The current evidence package shows that prompt-only is unstable, no-direct-solution does not imply no critical bridge leakage, DBox-inspired decomposition is a strong baseline, and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view.

### 5.2 Why Critical Bridge Leakage Matters

The rule "do not give the answer or code" is too coarse for tutoring. A tutor can avoid full code and the final answer while still revealing the intermediate reasoning bridge the student should derive. CP-MissingBridgeBench captures this risk through case-specific rubrics that define success criteria, forbidden content, acceptable reveal, and expected student next action, separating helpful scaffolding from premature bridge completion.

### 5.3 Guard And Repair

Guard-only conditions are instrumentation / runtime signal in the current main experiment. When the Leakage Judge returns `rewrite`, it does not alter `final_response_text`; only `block` triggers fallback, and block=0 in this main run. Guard-only should therefore not be described as fixing final outputs.

Repair can be described as a leakage-reduction intervention supported by same-candidate stress evidence, but not as a causal effect proven by main-experiment condition means alone. It reduces leakage severity while often increasing student burden.

### 5.4 Limitations

This study has clear limitations. First, the 50-case set is a high-risk dialogue-state CP tutoring evidence candidate, not full CP tutoring coverage. Second, student-ready, safe-ready, and rank are sensitive to rater strictness. Third, priority60 adjudication is not gold; it only reduces uncertainty for high-priority disagreements. Fourth, DBox+Repair is a 20-case targeted sensitivity add-on, not a full main condition. Fifth, the DeepSeek-backed LLM grader has high critical false-negative risk and cannot replace human review.

## Paper-Safe Takeaway

```text
CP-MissingBridgeBench reveals quality-safety-burden trade-offs in dialogue-state competitive-programming tutoring. DBox-inspired decomposition is a strong baseline. Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity critical-leakage-control trends under the primary human-review view, while student-ready, rank preference, Repair interpretation, DBox+Repair fairness, and LLM grader calibration require explicit sensitivity or stress-test reporting.
```
