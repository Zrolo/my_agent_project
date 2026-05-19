# Paper Section Draft: Results And Discussion For Dialogue-State v3

## 4 Results

Evidence classes are kept separate throughout the section: `main_scaffold_eval` + priority60 adjudicated + Coach A is the main result; rater views, all-case aggregates, and non-main slices are sensitivity / appendix evidence; Repair same-candidate before/after review is a stress test; DBox+Repair is a 20-case fairness sensitivity add-on; and DeepSeek LLM grader calibration is auxiliary-grader calibration, not a human-review replacement.

### 4.1 Human Review Reliability

Dialogue-state v3 contains 50 reviewed candidate cases, 7 anonymized tutoring-harness conditions, and 350 AI responses. Both coaches completed all 350 blind reviews. Coach A/B exact agreement on overall quality is 0.2829, but within-1 agreement reaches 0.8429. Leakage-label exact agreement is 0.6714. Critical-binary exact agreement is 0.9029, but kappa is only 0.2511. Rank agreement is also weak: top-1 and last-place agreement are both 10/50.

We adjudicated 60 high-priority disagreements: `use_A=29`, `use_B=9`, and `new_label=22`. This means neither coach should be treated as gold, and pedagogical judgment remains rater-sensitive, especially for student-ready, safe-ready, and rank preference. We therefore report priority adjudication, slice analysis, paired uncertainty, and rater-view sensitivity.

### 4.2 Main Scaffold Evaluation

The main result uses the 31-case `main_scaffold_eval` slice and the `priority60 adjudicated + Coach A` reference view. It does not pool clarification / policy-safety cases into the headline result. Table 1 summarizes the main slice.

| condition | overall | student-ready | safe-ready | major+answer leakage |
| --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 3.032 | 7/31 | 7/31 | 9 |
| `codehelp_codeaid_clean` | 3.710 | 19/31 | 19/31 | 2 |
| `dbox_inspired_clean` | 3.774 | 21/31 | 21/31 | 2 |
| `dbox_inspired_guard` | 3.774 | 23/31 | 23/31 | 2 |
| `bridge_guided_dbox_style_guard` | 3.742 | 20/31 | 20/31 | 2 |
| `bridge_contract_compact_guard` | 4.000 | 23/31 | 23/31 | 0 |
| `bridge_contract_compact_guard_repair` | 4.065 | 22/31 | 22/31 | 0 |

`bridge_contract_compact_guard_repair` has the highest overall score, while both Bridge Contract compact variants reduce major+answer leakage to 0 in the main scaffold slice. However, DBox-inspired decomposition remains a strong baseline: `dbox_inspired_guard` matches or approaches Bridge Contract compact on student-ready and safe-ready counts. The result should therefore be read as a quality-safety-burden trade-off, not as a one-harness victory claim.

The comparison between `enhanced_prompt_only_clean` and `codehelp_codeaid_clean` is also informative. A no-direct-code / no-direct-solution baseline is substantially stronger than prompt-only on this slice, but it still has 2 major+answer leakage rows. This supports the core motivation of critical bridge leakage: avoiding direct answers or code is not sufficient to avoid premature completion of the student's missing bridge.

### 4.3 Paired Uncertainty And Sensitivity

Same-case paired comparisons temper the headline result. `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` has mean overall delta +0.290, W/T/L 14/10/7, and 2 fewer major+answer leakage rows, but its paired bootstrap 95% CI is [-0.097, +0.645] and paired permutation p=0.2016. This supports a trend-level trade-off advantage, not a strong statistical superiority claim.

`bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` has mean overall delta +0.065, W/T/L 7/18/6, and equal major+answer leakage. The main condition comparison alone therefore does not establish a causal Repair effect.

By contrast, `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` has mean overall delta +0.677, 95% CI [+0.258, +1.065], paired p=0.0046, 12 more safe-ready rows, and 7 fewer major+answer leakage rows. This supports the conclusion that prompt-only is not a stable upper bound in dialogue-state CP tutoring.

The all-case sensitivity analysis shows that `bridge_contract_compact_guard_repair` has the highest overall score under Coach A only, Coach B only, priority60+CoachA, and priority60+CoachB. However, all-case averages mix main scaffold, clarification, and policy slices, so they are reported only as supplemental robustness. Student-ready, safe-ready, and rank remain sensitive to rater strictness.

### 4.4 Observed Error Taxonomy

The observed error taxonomy is not a list of concrete algorithms. It is organized as:

```text
general tutoring failure type x operational cognitive bridge family x surface anchor
```

General failure types include critical bridge leakage, answer/code leakage, over-complete micro-examples, shifted focus, under-scaffolding, excessive burden, context misalignment, over-safe refusal, factual/algorithmic error, and policy/direct-answer handling failure. Operational cognitive bridge families include representation semantics, transition/action mapping, predicate/decision semantics, ordering/dependency control, modeling relation, aggregation/contribution accounting, data-structure operation mapping, correctness/invariant reasoning, implementation boundary, debugging evidence, and policy-request handling. DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, and debugging trace are surface anchors, not the taxonomy itself.

This supports generalization beyond a small set of algorithm examples, while remaining honest about coverage. The 50-case set is an observed high-risk CP tutoring evidence candidate, not universal CP tutoring coverage.

### 4.5 Repair And DBox+Repair Fairness

Because the main experiment compares different condition outputs, it cannot by itself prove that Repair causally improves the same candidate. We therefore ran a 30-pair same-candidate before/after stress test. Repair improves leakage severity in 16/30 pairs, preserves it in 14/30, and worsens it in 0/30. Major leakage falls from 7/30 to 0/30. Overall increases from 3.367 to 3.633, with mean delta +0.267. The trade-off is burden: burden improved / same / worsened is 2/16/12.

To address baseline fairness, we also ran a 20-case targeted review of `dbox_inspired_guard_repair`. DBox+Repair has overall 3.55, safe-ready 11/20, and no/minor/major+answer leakage 14/6/0. Relative to the same-case DBox Guard subset, it modestly improves overall (+0.15, W/T/L=6/9/5) and reduces major+answer leakage from 2 to 0. Relative to Bridge Contract compact + Guard/Repair on the same 20 cases, Bridge+Repair remains +0.50 overall, W/T/L=12/5/3, and safe-ready +4.

These results support Repair as a leakage-reduction intervention with burden trade-offs. They do not make DBox+Repair a full main condition, nor do they prove Bridge superiority over every repair-enabled baseline.

### 4.6 DeepSeek-Backed LLM Grader Calibration

LLM grader calibration is used only to assess whether automatic graders can provide auxiliary signals. The paper-facing calibration uses DeepSeek `deepseek-v4-flash` with thinking disabled, matching the main experiment's offline judge stack. Because tutor generation, judge/guard, and repair are all implemented within a fixed DeepSeek-family offline stack, this calibration is backend-coupled and should not be interpreted as cross-backend validation.

On the priority60 reference, the DeepSeek case-specific bridge-rubric judge improves some auxiliary metrics relative to a generic rubric: leakage-label accuracy is 0.617 vs 0.583, student-ready agreement is 0.467 vs 0.433, and safe-ready agreement is 0.533 vs 0.400. However, both generic and case-specific DeepSeek graders have critical recall 0 and major leakage false-negative rate 1.000. The automatic grader fails to recover the rows humans adjudicated as `major_bridge_leakage` / `answer_leakage`.

Thus, case-specific bridge rubrics can improve some auxiliary automatic-grading signals, but DeepSeek-backed LLM graders are not reliable enough for high-stakes critical-bridge leakage evaluation. Human review and adjudication remain necessary. Earlier Kimi-backed outputs are treated only as exploratory/tooling evidence and illustrate backend sensitivity. Cross-backend grader calibration, including GPT-5.4-backed grading, is future work or a revision add-on rather than a silent replacement for the current DeepSeek calibration.

## 5 Discussion

### 5.1 What The Benchmark Contributes

CP-MissingBridgeBench does not primarily claim that one tutoring harness is an absolute winner. Its contribution is to make missing bridges and critical bridge leakage explicit evaluation objects for dialogue-state competitive-programming tutoring. The benchmark distinguishes systems by quality, leakage control, and student burden. In the current evidence, prompt-only is unstable, no-direct-solution is not safety-complete, DBox-inspired decomposition is a strong baseline, and Bridge Contract compact + Guard/Repair shows a favorable but bounded trend in overall quality and high-severity leakage control.

### 5.2 Why Critical Bridge Leakage Is Different From Answer Leakage

Direct-answer avoidance is too coarse for tutoring. A response may avoid final code and still reveal the key intermediate reasoning step the student should infer. CP-MissingBridgeBench captures this through case-specific rubrics that define success criteria, forbidden content, acceptable reveal, and expected student next action. This separates helpful scaffolding from premature completion of the student's missing bridge.

### 5.3 Guard And Repair

Guard-only variants in the current pipeline are guard-instrumented, not guard-rewritten. When the Leakage Judge returns `rewrite`, `final_response_text` is not changed; only `block` would trigger fallback, and the main experiment observed no block fallback. Guard-only results should therefore be interpreted as runtime leakage signals, not as evidence that Guard repaired final responses.

Repair has more direct support from same-candidate stress testing. It reduces leakage severity without worsening any pair in the 30-pair stress set, but it often increases student burden. Repair should therefore be described as promising but trade-off-bearing, not as a complete solution.

### 5.4 Limitations

First, the 50-case set is a high-risk CP tutoring evidence candidate, not exhaustive CP coverage. Second, student-ready, safe-ready, and rank are rater-sensitive, so the paper must report sensitivity views. Third, priority60 adjudication is not final gold; it reduces uncertainty for high-priority disagreements but does not remove all rater variance. Fourth, the DBox+Repair add-on is a 20-case targeted sensitivity review, not a full 50-case double-coach add-on. Fifth, DeepSeek-backed LLM grader calibration has high critical false-negative risk and same-backend coupling, so automatic graders cannot replace human review.

## Paper-Safe Takeaway

The safest conclusion is:

```text
CP-MissingBridgeBench reveals quality-safety-burden trade-offs in dialogue-state competitive-programming tutoring. DBox-inspired decomposition is a strong baseline. Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity critical-leakage-control trends under the primary human-review view, but student-ready, rank preference, and automatic grader agreement remain rater- and backend-sensitive. Guard-only is instrumentation in the current pipeline, and Repair requires same-candidate evidence to support causal claims.
```
