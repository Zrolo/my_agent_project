# Paper Results And Discussion Manuscript Draft: Dialogue-State v3

## Scope

This document is a compressed manuscript-style Results / Discussion draft. It does not add experiments. It reuses the existing human review, priority60 adjudication, paired uncertainty, Repair same-candidate stress test, DBox+Repair fairness add-on, and DeepSeek-backed LLM grader calibration.

The paper-facing main view is:

```text
main_scaffold_eval slice + priority60 adjudicated + Coach A labels
```

All-case averages, Coach A/B only views, priority60+CoachB, and clarification / policy slices should be used as sensitivity or appendix evidence.

Evidence classes:

| Evidence item | Class | Paper role |
| --- | --- | --- |
| `main_scaffold_eval` + priority60 adjudicated + Coach A | main result | Headline human-review result. |
| Coach A only / Coach B only / priority60+CoachB | sensitivity analysis | Rater-strictness sensitivity. |
| all-50 aggregate and non-main slices | sensitivity / appendix | Robustness and targeted safety discussion, not headline. |
| Pairwise W/T/L and paired uncertainty | main result support | Quantifies uncertainty around headline comparisons. |
| Repair same-candidate before/after review | stress test | Causal Repair evidence under fixed candidates. |
| DBox+Repair 20-case add-on | sensitivity analysis | Fairness add-on check, not a main condition. |
| DeepSeek LLM grader calibration | calibration | Auxiliary-grader assessment, not a human-review replacement. |

## Results

### Human Review Reliability

Dialogue-state v3 contains 50 reviewed candidate cases, 7 anonymized tutoring-harness conditions, and 350 AI responses. Coach A and Coach B both completed all 350 blind reviews. Their exact agreement on overall quality is low (0.2829), but within-1 agreement is high (0.8429). Leakage-label exact agreement is 0.6714. Critical-binary exact agreement is 0.9029, but kappa is only 0.2511. Rank agreement is weak: top-1 and last-place agreement are both 10/50, and 244 rows are flagged disagreements.

We adjudicated 60 high-priority disagreements: `use_A=29`, `use_B=9`, and `new_label=22`. This means neither coach should be treated as gold, and pedagogical judgment remains rater-sensitive. The paper should therefore report double review, priority adjudication, slice analysis, and sensitivity analysis rather than a single score table.

### Main Scaffold Evaluation

The headline result should focus on the 31-case `main_scaffold_eval` slice, not pooled clarification / policy-safety cases. Under the `priority60 adjudicated + Coach A` main view, `bridge_contract_compact_guard_repair` has the highest overall score (4.065), followed by `bridge_contract_compact_guard` (4.000), while `dbox_inspired_guard` and `dbox_inspired_clean` both score 3.774. `bridge_contract_compact_guard` and `bridge_contract_compact_guard_repair` both have zero major+answer leakage. `dbox_inspired_guard` still has 2 major+answer leakage rows, but its student-ready / safe-ready count is 23/31, matching or approaching `bridge_contract_compact_guard`.

This supports two claims. First, DBox-inspired decomposition is a strong baseline, not a strawman. Second, Bridge Contract compact + Guard/Repair shows a stronger trade-off between overall quality and high-severity leakage control, but this should not be written as comprehensive dominance.

`enhanced_prompt_only_clean` has overall 3.032 and 9 major+answer leakage rows on the main scaffold slice. `codehelp_codeaid_clean` improves to overall 3.710 and reduces major+answer leakage to 2. This suggests that a no-direct-code / no-direct-solution policy is more stable than prompt-only, but it is still not sufficient to eliminate critical bridge leakage.

### Pairwise Uncertainty

Paired same-case comparisons prevent over-reading mean ranks. `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` has mean overall delta +0.290, W/T/L 14/10/7, and 2 fewer major+answer leakage rows. However, the paired bootstrap 95% CI is [-0.097, +0.645], and paired permutation p=0.2016. The paper can describe this as a trend or trade-off advantage, not statistically significant dominance.

`bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` has mean overall delta +0.065, W/T/L 7/18/6, and equal major+answer leakage. The main condition means alone therefore do not prove a causal Repair effect. They motivate same-candidate before/after stress testing.

`codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` has mean overall delta +0.677, 95% CI [+0.258, +1.065], paired p=0.0046, 12 more safe-ready rows, and 7 fewer major+answer leakage rows. This supports the claim that prompt-only is not a stable upper bound in dialogue-state CP tutoring, while still not making no-direct-solution safety-complete.

### Slice And Sensitivity Analysis

The 50 cases are separated into `main_scaffold_eval` (31 cases), `main_eval_with_caution` (5 cases), `clarification_safety_slice` (10 cases), and `policy_safety_slice` (4 cases). The headline should come from `main_scaffold_eval`; other slices should be reported in appendix or used for targeted safety discussion.

The four rater views are Coach A only, Coach B only, priority60 adjudicated + Coach A, and priority60 adjudicated + Coach B. In all-case sensitivity, `bridge_contract_compact_guard_repair` has the highest overall score in all four views, but all-case averages mix clarification and policy slices and should remain supplemental. In the main scaffold slice, overall trends are more stable than student-ready, safe-ready, and rank, which remain sensitive to rater strictness.

### Observed Error Taxonomy

The taxonomy should not be described as covering only DP states, binary-search checks, lazy propagation, tree difference, or local code. The reviewer-facing taxonomy is:

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

Level 1 is the general tutoring failure type, such as critical bridge leakage, answer/code leakage, over-complete micro-example, wrong/shifted focus, under-scaffolding, excessive burden, context misalignment, over-safe refusal, factual/algorithmic error, and policy/direct-answer handling failure. Level 2 is the operational cognitive bridge family, such as representation semantics, transition/action mapping, predicate/decision semantics, ordering/dependency control, modeling relation, aggregation/contribution accounting, data-structure operation mapping, correctness/invariant reasoning, implementation boundary, debugging evidence, and policy-request handling. Level 3 is the surface anchor, such as DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, or debugging trace.

The paper should present this as an observed taxonomy, not a universal taxonomy. The 50-case set covers multiple cognitive bridge families but still under-samples geometry predicates, counting / inclusion-exclusion, modular invariants, search pruning / deduplication, and richer multi-turn debugging diagnosis.

### Repair Same-Candidate Stress Test

The main experiment shows condition-level performance but does not by itself prove that Repair causally improves the same candidate. We therefore ran a 30-pair same-candidate before/after stress test, fixing the original candidate and repaired output and blinding them as Response A / Response B.

Repair improves leakage severity in 16/30 pairs, preserves it in 14/30, and worsens it in 0/30. Major leakage falls from 7/30 to 0/30. Overall increases from 3.367 to 3.633, with mean delta +0.267. Quality W/T/L is 12/11/7; repair preferred / original preferred / tie is 15/11/4. The cost is student burden: burden improved / same / worsened is 2/16/12.

The paper can say that Repair reduces leakage severity in a same-candidate stress setting, especially eliminating major leakage in this sample, but often increases student burden. It should not frame Repair as a complete leakage solution.

### DBox+Repair Fairness Add-On

To address the fairness concern that Bridge had a Repair-enabled condition while the DBox-inspired baseline did not receive an equivalent Repair opportunity, we ran a 20-case headline-sensitive supplemental review of the existing `dbox_inspired_guard_repair` generation package. This is a targeted sensitivity set, not a random sample and not a full 50-case double-coach review.

DBox+Repair add-on has overall 3.55, safe-ready 11/20, and no/minor/major+answer leakage 14/6/0. Compared with the same 20-case DBox Guard subset under priority60 + Coach A, DBox+Repair modestly improves overall (+0.15, W/T/L=6/9/5) and reduces major+answer leakage from 2 to 0. Compared with Bridge Contract compact + Guard/Repair on the same 20 cases, Bridge+Repair remains +0.50 overall, W/T/L=12/5/3, and safe-ready +4.

This should be framed as fairness sensitivity evidence. It mitigates the concern that DBox lacked Repair and shows that Repair can also help a literature-inspired baseline reduce high-risk leakage. It does not replace the main experiment or prove a confirmed Bridge advantage over every repair-enabled baseline.

### LLM Grader Calibration

LLM grader calibration is used only to test whether automatic graders can serve as scalable auxiliary signals. It does not replace human review. The paper-facing calibration uses the DeepSeek offline judge profile aligned with the main experiment judge stack:

```text
backend = deepseek
model = deepseek-v4-flash
thinking = disabled
```

The DeepSeek-backed priority60 run completes 180/180 tasks. The case-specific bridge-rubric judge improves some auxiliary metrics relative to the generic rubric: leakage-label accuracy is 0.617 vs 0.583, student-ready agreement is 0.467 vs 0.433, and safe-ready agreement is 0.533 vs 0.400. However, safety-critical performance is weak: both generic and case-specific DeepSeek graders have critical recall 0 and major leakage false-negative rate 1.000. The automatic grader fails to recover the rows humans adjudicated as `major_bridge_leakage` / `answer_leakage`.

The paper should therefore say that case-specific bridge rubrics improve some auxiliary grading signals, but DeepSeek-backed LLM graders remain unreliable for high-stakes critical-bridge leakage evaluation. Earlier Kimi-backed results are retained only as exploratory/tooling evidence because they use a different backend and demonstrate backend sensitivity.

## Discussion

### What CP-MissingBridgeBench Shows

CP-MissingBridgeBench's main contribution is not proving that one tutor harness is an absolute winner. It makes missing bridges and critical bridge leakage into inspectable evaluation objects. It reveals quality-safety-burden trade-offs across tutoring harnesses: prompt-only is unstable, no-direct-solution does not imply no leakage, DBox-inspired decomposition is a strong baseline, and Bridge Contract compact + Guard/Repair shows favorable but not absolute trends in overall quality and high-severity leakage control.

### Why Critical Bridge Leakage Matters

The rule “do not directly give the answer/code” is too weak for safe tutoring. An AI can avoid final code and still reveal the intermediate reasoning step the student should cross themselves. CP-MissingBridgeBench defines this as critical bridge leakage and uses case-specific rubrics to specify success criteria, forbidden content, acceptable reveal, and expected student next action. This separates helpful scaffolding from premature completion of the student's key reasoning bridge.

### Guard And Repair Interpretation

Guard-only conditions are instrumentation / runtime-signal conditions in the current main experiment. Unless a block fallback is triggered, they do not rewrite the final student-visible response. Therefore guard-only results should not be interpreted as Guard fixing final outputs.

Repair causality cannot be inferred only from condition means. The same-candidate stress test provides more direct before/after evidence: Repair reduces leakage severity, but can increase student burden. The paper should describe Repair as a promising but trade-off-bearing intervention, not as a fully solved safety mechanism.

### Limitations

This study has five main limitations. First, the 50-case set is a high-risk CP tutoring evidence candidate, not full CP coverage. Second, student-ready, safe-ready, and rank are sensitive to rater strictness, so sensitivity analysis is required. Third, priority60 adjudication is not final gold; it reduces uncertainty around high-priority disagreements but does not remove all rater variance. Fourth, the DBox+Repair fairness add-on is a 20-case targeted sensitivity review, not a full 50-case double-coach add-on. Fifth, DeepSeek-backed LLM grader calibration shows high critical false-negative risk, so automatic graders cannot replace human review.

## Paper-Safe Claim

The safest main claim is:

```text
CP-MissingBridgeBench reveals quality-safety-burden trade-offs in dialogue-state competitive-programming tutoring. DBox-inspired decomposition is a strong baseline. Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity critical-leakage-control trends under the primary human-review view, but student-ready, rank preference, and automatic grader agreement remain rater- and backend-sensitive. Guard-only is instrumentation in the current pipeline, and Repair requires same-candidate evidence to support causal claims.
```
