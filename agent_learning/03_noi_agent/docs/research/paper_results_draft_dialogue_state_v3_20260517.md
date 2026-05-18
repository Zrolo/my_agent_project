# Paper Results Draft: Dialogue-State v3 20260517

## 1. Human Review Reliability

Dialogue-state v3 contains 50 reviewed candidate cases, 7 anonymized conditions, and 350 AI responses. Coach A and Coach B both reviewed all 350 responses. A/B agreement shows `overall exact=0.2829` but `overall within 1=0.8429`; `leakage exact=0.6714`; `critical binary exact=0.9029` but `critical binary kappa=0.2511`; rank agreement is low, with top-1 and last-place agreement both 10/50 and 244 flagged disagreement rows.

We adjudicated 60 high-priority disagreement rows: `use_A=29`, `use_B=9`, `new_label=22`. This means neither coach can be treated as gold. The paper should frame this as rater-sensitive pedagogical judgment controlled through double review, priority adjudication, slice analysis, and sensitivity analysis.

## 2. Main Scaffold Evaluation

The main headline should focus on the 31-case `main_scaffold_eval` slice, not pooled clarification / policy safety cases. Under the primary `priority60 adjudicated + Coach A` view:

- `bridge_contract_compact_guard_repair` has the highest overall score: 4.065.
- `bridge_contract_compact_guard` and `bridge_contract_compact_guard_repair` both have 0 major+answer leakage.
- `dbox_inspired_guard` has student-ready / safe-ready of 23, matching or approaching `bridge_contract_compact_guard`, so DBox-inspired decomposition is a strong baseline.
- `enhanced_prompt_only_clean` is less stable, with lower overall and higher major+answer leakage.
- `codehelp_codeaid_clean` is stronger than enhanced prompt-only but still has critical bridge leakage, showing that no-direct-solution is not enough.

## 3. Pairwise Uncertainty

Paired comparisons show `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` at `Δ overall=+0.290`, W/T/L=14/10/7, with 2 fewer major+answer leaks, but bootstrap CI `[-0.097, +0.645]` crosses 0 and paired p=0.2016. This supports trend / trade-off advantage, not significant dominance.

`bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` has `Δ overall=+0.065`, W/T/L=7/18/6, and the same major+answer leakage. The main experiment does not support a causal Repair claim.

`codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` has `Δ overall=+0.677`, CI `[+0.258, +1.065]`, indicating that no-direct-solution baselines are stronger than prompt-only but still insufficient for critical-leakage control.

## 4. Sensitivity Analysis

The four rater views are Coach A only, Coach B only, priority60 adjudicated + Coach A, and priority60 adjudicated + Coach B. In all-case sensitivity, `bridge_contract_compact_guard_repair` has the highest overall score in all four views. However, all-case averages mix clarification and policy slices, so they are supplementary.

Within `main_scaffold_eval`, the overall trend is relatively stable, but student-ready and rank are sensitive to rater strictness. Coach B is stricter and compresses score gaps; the paper should not report only one table.

## 5. Slice Analysis

| slice | case_n | paper use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | Main scaffold-quality comparison |
| `main_eval_with_caution` | 5 | Sensitivity / appendix |
| `clarification_safety_slice` | 10 | Clarification and non-over-inference analysis |
| `policy_safety_slice` | 4 | Direct-answer / direct-code safety redirection |

Results should be reported by slice rather than pooled into one headline.

## 6. Observed Error Taxonomy

The observed error taxonomy uses:

```text
general tutoring failure type × operational cognitive bridge family × surface anchor
```

Observed errors include critical bridge leakage, answer/code leakage, over-complete micro-examples, wrong/shifted focus, under-scaffolding, excessive burden, context misalignment, over-safe refusal, factual/algorithmic error, and policy handling failure. Observed bridge families include representation semantics, transition/action mapping, predicate/decision semantics, ordering/dependency, modeling relation, aggregation/contribution, data-structure operation, correctness/invariant, implementation, debugging evidence, and policy-request handling. DP states, binary-search checks, lazy propagation, tree difference, and local code are surface anchors, not the taxonomy itself.

## 7. Repair Same-Candidate Stress Test Result

The main experiment supports condition-level performance but not same-candidate Repair causality. We therefore ran a 30-pair same-candidate before/after stress test, fixing the original candidate and repaired output and blinding them as Response A / Response B.

Repair improved leakage severity in 16/30 pairs, preserved it in 14/30, and worsened it in 0/30. Major leakage fell from 7/30 to 0/30. Overall increased from 3.367 to 3.633, with mean delta +0.267; quality W/T/L was 12/11/7; repair preferred/original preferred/tie was 15/11/4. However, burden improved/same/worse was 2/16/12, so the leakage benefit comes with a student-burden trade-off. This should be reported as stress-test evidence, not as a reinterpretation of main-experiment means as the sole causal proof.

## 8. DBox+Repair Fairness Add-On

To address the fairness risk that Bridge had a Repair-enabled condition while the DBox-inspired baseline did not receive an equivalent Repair opportunity, we ran a 20-case headline-sensitive supplemental review of the existing `dbox_inspired_guard_repair` generation package. This is a targeted sensitivity set, not a random sample and not a full 50-case double-coach review.

The add-on has overall 3.55, safe-ready 11/20, no/minor/major+answer leakage 14/6/0, and burden low/medium/high 8/9/3. Compared with the same 20-case DBox Guard subset under the priority60 + Coach A view, DBox+Repair modestly improves overall (+0.15, W/T/L=6/9/5) and reduces major+answer leakage from 2 to 0. It does not overturn the Bridge Contract compact + Guard/Repair trend on the same 20 cases: Bridge+Repair vs DBox+Repair is +0.50 overall, W/T/L=12/5/3, and safe-ready +4.

The paper should frame this as fairness sensitivity evidence. DBox+Repair mitigates the concern that DBox lacked Repair and shows Repair can also help a literature-inspired baseline reduce high-risk leakage. It does not replace the main experiment and does not prove a confirmed Bridge advantage over every repair-enabled baseline.

## 9. LLM Grader Calibration Result

LLM graders are scalable auxiliary graders only. We compare `likert_only_judge`, `generic_rubric_judge`, and `case_specific_bridge_rubric_judge` against priority60 adjudicated labels and adj+CoachA/B sample20 references, reporting overall agreement/correlation, leakage accuracy, critical binary precision/recall/F1, major leakage false negative rate, student-ready agreement, safe-ready agreement, and unknown rate.

The DeepSeek-backed priority60 adjudicated main view is complete with 180/180 tasks. The case-specific bridge-rubric judge has leakage accuracy 0.617, above the generic rubric's 0.583; ready agreement is 0.467 vs 0.433; safe-ready agreement is 0.533 vs 0.400. The safety-critical metrics remain weak: both generic and case-specific DeepSeek graders have critical recall 0 and major leakage false-negative rate 1.000. It therefore cannot replace human review.

The DeepSeek-backed adj+CoachA sample20 and adj+CoachB sample20 runs are both complete with 60/60 tasks. These two sample20 reference views contain no human critical-positive rows, so they are only rater-view sensitivity checks for overall, ready / safe-ready, and non-critical leakage-label agreement; they should not be used for critical recall claims. The earlier Kimi-backed calibration is retained only as an exploratory/tooling record because it does not match the main experiment's fixed DeepSeek judge stack.

## 10. What We Can And Cannot Claim

Can write:

- CP-MissingBridgeBench distinguishes quality-safety-burden trade-offs.
- DBox-inspired decomposition is a strong baseline.
- Bridge Contract compact + Guard/Repair is stable in overall and critical-leakage control.
- Student-ready is rater-sensitive.
- No-direct-code does not imply no critical bridge leakage.
- Prompt-only is not stable enough in dialogue-state CP tutoring.
- Concrete algorithm patterns are surface anchors, not the taxonomy itself.
- The DBox+Repair 20-case targeted add-on mitigates the fairness-add-on risk, but remains sensitivity evidence.
- The case-specific bridge-rubric judge improves some DeepSeek auxiliary grading signals, but priority60 critical false-negative risk remains high and it cannot replace human coaches or adjudication.

Cannot write:

- Bridge Contract has universal significant dominance over all baselines.
- Guard-only fixes final outputs.
- Repair fully solves leakage.
- Coach A / Coach B is gold.
- Priority60 is final gold.
- The 50-case set covers all CP tutoring situations.
- DBox+Repair has completed full 50-case double-coach validation.
- LLM grader labels can replace human review or serve as gold labels.

## 11. Limitations

There are five main limitations. First, the 50-case set is a high-risk CP tutoring evidence candidate, not full CP coverage. Second, student-ready and rank are rater-sensitive. Third, Guard-only is instrumentation in the current pipeline, not rewrite. Fourth, Repair is now supported by same-candidate stress evidence and DBox+Repair targeted sensitivity, but DBox+Repair is still not a full 50-case double-coach add-on. Fifth, LLM grader calibration shows that case-specific rubrics help, but DeepSeek-backed priority60 critical false negatives remain high and automatic graders cannot replace human review.
