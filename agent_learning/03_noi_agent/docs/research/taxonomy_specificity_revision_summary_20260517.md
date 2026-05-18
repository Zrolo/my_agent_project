# Taxonomy Specificity Revision Summary 20260517

English companion for `taxonomy_specificity_revision_summary_20260517.zh.md`.

This pass revised P0/P1 paper-facing and reviewer-facing wording only. It did not add experiments, change online AIChat behavior, modify main experiment data, or expand annotation dropdowns.

The revised framing is:

```text
cognitive bridge family + leakage mechanism + surface anchor
```

Bridge buckets such as `state_representation_semantics`, `transition_recurrence_source`, and `predicate_check_semantics` are Research v1 operational cognitive bridge families. Concrete algorithm instances such as DP states, binary-search checks, lazy propagation, tree-difference marking, and local code are surface anchors.

## Modified Files

| File | Change |
| --- | --- |
| `docs/research/evaluation_protocol_v3.zh.md` / `.md` | Reframed Case Memo categories as abstract leakage mechanisms and clarified bridge bucket vs surface anchor. |
| `docs/research/response_review_rubric_v3.zh.md` / `.md` | Added a section explaining that leakage mechanisms are not algorithm categories. |
| `docs/research/dialogue_state_v3_human_review_result_packet_20260517.zh.md` / `.md` | Added Taxonomy Scope and coverage limitations. |
| `docs/research/paper_results_interpretation_guardrails_20260517.zh.md` / `.md` | Added Taxonomy / Coverage Guardrail. |
| `docs/research/coach_blind_review_instructions_v1.zh.md` / `.md` | Added reviewer guidance that examples are surface anchors and added proof/debug/modeling/complexity boundary cases. |
| `evals/aichat/export_coach_response_review_workbook_xlsx.py` | Revised workbook instruction wording to present examples as abstract category plus surface anchor. |
| `evals/aichat/coach_labeling_schema_v2.py` | Broadened the `critical_bridge_completion_risk` description without adding dropdown values. |

## Historical Reports Not Rewritten

Historical ad-hoc analyses, early dev case lists, and older repair-stress reports were left untouched because they are historical memos rather than current paper taxonomy definitions. New paper-facing documents now clarify that DP/check/lazy/code wording in those memos is surface-anchor shorthand, not the full taxonomy.

## Paper Framing

The paper should describe CP-MissingBridgeBench as evaluating operational cognitive bridge families and tutor leakage mechanisms. Concrete algorithm patterns are examples, not the taxonomy boundary.

## Coverage Limitations

The current dialogue-state v3 set covers representation, transition/action mapping, predicate/decision, ordering/dependency, modeling, aggregation/contribution, data-structure operation, correctness/invariant, implementation, debugging evidence, and policy-request families. It under-samples math property / modular invariant, counting / inclusion-exclusion, geometry predicate relation, search pruning / deduplication, reflection / transfer, richer multi-turn debugging diagnosis, and broader non-DP/non-data-structure mathematical reasoning.
