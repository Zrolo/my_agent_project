# Paper Results Interpretation Guardrails (20260517)

## Safe Claims

- CP-MissingBridgeBench reveals quality, safety, and student-burden trade-offs across LLM tutoring harnesses.
- DBox-inspired decomposition is a strong baseline and should not be treated as weak.
- Under the `main_scaffold_eval` + `priority60 adjudicated + Coach A` primary view, `bridge_contract_compact_guard_repair` has the highest overall score and a favorable critical/answer leakage-control signal; however, most paired CIs cross zero, so this should be written as a trend/trade-off advantage.
- Both `bridge_contract_compact_guard` and `bridge_contract_compact_guard_repair` reduce main-slice critical/answer leakage to 0; Repair-enabled overall is slightly higher, but the main experiment itself does not prove Repair causality. The same-candidate stress test now provides fixed-candidate Repair leakage-reduction evidence.
- The DBox+Repair 20-case targeted fairness add-on has no major/answer leakage and modestly improves overall / sufficiency over the same-case DBox Guard subset; it is sensitivity evidence, not a full 50-case fair-baseline conclusion.
- Student-ready, rank preference, and would-show labels are sensitive to rater strictness. Report Coach A/B agreement, adjudication, and sensitivity analysis.

## Unsafe Claims

- Bridge Contract is significantly and universally better than all baselines.
- Guard-only reduced leakage in final student-visible responses.
- Repair causality is proven by the 50-case main experiment.
- Either Coach A or Coach B is gold.
- Priority60 adjudication is final adjudicated gold.
- DBox/CodeHelp/CodeAid are faithful reproductions of prior systems; they are literature-inspired baselines.
- DBox+Repair has completed full 50-case double-coach validation, or Bridge+Repair has a confirmed advantage over every repair-enabled baseline.

## Guard-Only Wording

In the current `tutor_plus_guard` path, a Leakage Judge `rewrite` action does not change `final_response_text`; only `block` triggers deterministic safe fallback. In the main run, `block=0`. Therefore `dbox_inspired_guard`, `bridge_guided_dbox_style_guard`, and `bridge_contract_compact_guard` should be called guard-instrumented / guard-checked variants, not guard-rewritten variants.

Recommended wording: guard-only conditions primarily provide a leakage-risk detection signal; unless block fallback fires, they do not rewrite the final student-visible response. Guard-only results therefore cannot be interpreted as actual output repair.

## Repair Wording

`bridge_contract_compact_guard_repair` is a repair-enabled condition and is the strongest current result, but Repair fires only on a subset of cases and different conditions may generate different candidates. The main experiment supports condition-level trade-offs, not a same-candidate causal Repair claim.

Recommended wording: Repair-enabled Bridge Contract condition shows the strongest overall/leakage trade-off in the current human-review candidate evidence. In a same-candidate stress test, Repair reduced leakage severity without worsening any pair, but increased student burden in a substantial minority of pairs.

## DBox+Repair Fairness Wording

The DBox+Repair add-on addresses a fairness risk: if the main method has Repair, the strong baseline should receive at least one repair-enabled check. The current result is a 20-case headline-sensitive targeted review, not a full 50-case double-coach add-on.

Recommended wording: A targeted DBox+Repair add-on reduced major/answer leakage on headline-sensitive cases and did not overturn the Bridge Contract compact + Guard/Repair trend under the primary Coach-A-adjudicated view. Report it as fairness sensitivity evidence, not as a new main condition.

## Taxonomy / Coverage Guardrail

Do not write that CP-MissingBridgeBench only evaluates DP states, recurrences, checks, boundaries, lazy propagation, difference marking, and local code.

Safe wording: those are concrete surface anchors in algorithm contexts. The main taxonomy is Research v1 operational cognitive bridge families plus tutor leakage mechanisms. Bridge buckets such as `state_representation_semantics` and `predicate_check_semantics` are operational cognitive bridge families, not surface anchors.

The paper should emphasize that the current 50-case set covers representation, transition/action mapping, predicate/decision semantics, ordering/dependency, modeling, aggregation/contribution, data-structure operation, correctness/invariant, implementation, debugging evidence, and policy-request families. Coverage limitations should also be explicit: math property / modular invariant, counting / inclusion-exclusion, geometry predicate relation, search pruning / deduplication, and reflection / transfer are still under-sampled.

## Next Priorities

1. Report paired uncertainty: W/T/L, mean delta, bootstrap CI, and paired permutation.
2. Calibrate LLM graders and describe them only as auxiliary graders.
3. Add the Repair stress result and DBox+Repair fairness sensitivity to Results / Discussion while reporting burden trade-offs.
4. If time allows, add a targeted 30-40-row adjudication round for headline-sensitive disagreements.
5. If time allows, expand DBox+Repair to 50 cases or second-review risk cases.
