# Paper Results Interpretation Guardrails (20260517)

## Safe Claims

- CP-MissingBridgeBench reveals quality, safety, and student-burden trade-offs across LLM tutoring harnesses.
- DBox-inspired decomposition is a strong baseline and should not be treated as weak.
- Under the `main_scaffold_eval` + `priority60 adjudicated + Coach A` primary view, `bridge_contract_compact_guard_repair` has the highest overall score and stable critical/answer leakage control; however, most paired CIs cross zero, so this should be written as a trend/trade-off advantage.
- Both `bridge_contract_compact_guard` and `bridge_contract_compact_guard_repair` reduce main-slice critical/answer leakage to 0; Repair-enabled overall is slightly higher, but the main experiment does not prove Repair causality.
- Student-ready, rank preference, and would-show labels are sensitive to rater strictness. Report Coach A/B agreement, adjudication, and sensitivity analysis.

## Unsafe Claims

- Bridge Contract is significantly and universally better than all baselines.
- Guard-only reduced leakage in final student-visible responses.
- Repair causality is proven by the 50-case main experiment.
- Either Coach A or Coach B is gold.
- Priority60 adjudication is final adjudicated gold.
- DBox/CodeHelp/CodeAid are faithful reproductions of prior systems; they are literature-inspired baselines.

## Guard-Only Wording

In the current `tutor_plus_guard` path, a Leakage Judge `rewrite` action does not change `final_response_text`; only `block` triggers deterministic safe fallback. In the main run, `block=0`. Therefore `dbox_inspired_guard`, `bridge_guided_dbox_style_guard`, and `bridge_contract_compact_guard` should be called guard-instrumented / guard-checked variants, not guard-rewritten variants.

Recommended wording: guard-only conditions primarily provide a leakage-risk detection signal; unless block fallback fires, they do not rewrite the final student-visible response. Guard-only results therefore cannot be interpreted as actual output repair.

## Repair Wording

`bridge_contract_compact_guard_repair` is a repair-enabled condition and is the strongest current result, but Repair fires only on a subset of cases and different conditions may generate different candidates. The main experiment supports condition-level trade-offs, not a same-candidate causal Repair claim.

Recommended wording: Repair-enabled Bridge Contract condition shows the strongest overall/leakage trade-off in the current human-review candidate evidence. A same-candidate stress test is required to estimate the causal Repair effect.

## Taxonomy / Coverage Guardrail

Do not write that CP-MissingBridgeBench only evaluates DP states, recurrences, checks, boundaries, lazy propagation, difference marking, and local code.

Safe wording: those are concrete surface anchors in algorithm contexts. The main taxonomy is Research v1 operational cognitive bridge families plus tutor leakage mechanisms. Bridge buckets such as `state_representation_semantics` and `predicate_check_semantics` are operational cognitive bridge families, not surface anchors.

The paper should emphasize that the current 50-case set covers representation, transition/action mapping, predicate/decision semantics, ordering/dependency, modeling, aggregation/contribution, data-structure operation, correctness/invariant, implementation, debugging evidence, and policy-request families. Coverage limitations should also be explicit: math property / modular invariant, counting / inclusion-exclusion, geometry predicate relation, search pruning / deduplication, and reflection / transfer are still under-sampled.

## Next Priorities

1. Report paired uncertainty: W/T/L, mean delta, bootstrap CI, and paired permutation.
2. Add a targeted 30-40-row adjudication round for headline-sensitive disagreements.
3. Complete the Repair same-candidate stress test.
4. Run a minimal DBox+Repair supplemental human review to address fairness-add-on risk.
5. Calibrate LLM graders and describe them only as auxiliary graders.
