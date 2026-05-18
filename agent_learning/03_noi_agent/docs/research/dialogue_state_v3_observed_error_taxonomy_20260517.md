# Dialogue-State v3 Observed Error Taxonomy 20260517

## Scope

This is an observed taxonomy derived from dialogue-state v3 human-review labels, not a universal taxonomy. It uses three levels:

```text
Level 1 = general tutoring failure type
Level 2 = operational cognitive bridge family
Level 3 = surface anchor example
```

Level 2 bridge buckets such as `state_representation_semantics` are operational cognitive bridge families. DP states, binary-search checks, lazy propagation, tree difference, local code, greedy proofs, and debugging traces are surface anchors. Counts below are mechanically derived from `priority60 adjudicated + Coach A` labels plus the existing disagreement / adjudication pool. The error pool covers major / answer leakage, minor leakage, overall <= 2, show = no, safe-ready = false, high student burden, Coach A/B disagreement, priority60 adjudication samples, and rank-last rows. Rows may have multiple Level 1 tags, so counts are not mutually exclusive.

## Level 1 Definitions

| id | error type | definition | decision rule | non-example |
| --- | --- | --- | --- | --- |
| E1 | `critical_bridge_leakage` | The response completes the student's current missing bridge too early. | `minor_bridge_leakage` or `major_bridge_leakage`, or notes indicate the key relation was revealed. | Restating what the student already said, or asking an open diagnostic question. |
| E2 | `answer_or_code_leakage` | The response exposes a full answer, full route, or key code. | `answer_leakage`, or direct completion of local code / full template. | Giving an incomplete variable check or asking the student to fill one judgment. |
| E3 | `over_complete_micro_example` | A micro-example / trace walks through the key relation. | The example supplies the state, recurrence, check result, boundary move, or proof conclusion. | The example asks the student to compare two objects or fill an observation. |
| E4 | `wrong_or_shifted_focus` | The response misses the current bottleneck or shifts to another task. | Low bridge identification / groundedness / single-focus, or notes indicate mismatch. | Clarifying context while still targeting the current student question. |
| E5 | `under_scaffolded_or_too_vague` | The response is safe but does not give enough actionable help. | Low scaffold sufficiency / next-step clarity, or overall <= 2 without leakage. | A concrete, low-burden local judgment task. |
| E6 | `excessive_student_burden` | The next student turn requires too much output or reasoning. | `student_response_burden=high`. | A short binary choice, local explanation, or variable-meaning answer. |
| E7 | `context_misalignment` | The tutor over-infers or fails to clarify under short / insufficient context. | no recent dialogue / insufficient context plus unstable show decision. | Asking for the missing context or citing the previous scaffold. |
| E8 | `over_safe_refusal_or_empty_help` | The response refuses or stays empty without advancing learning. | Policy/direct-answer cases with refusal but no alternative micro-task. | Refusing a full solution while giving a safe next step. |
| E9 | `factual_or_algorithmic_error` | The response contains factual, algorithmic, or problem-understanding errors. | Coach notes indicate wrong, inaccurate, or misleading content. | Conservative but accurate scaffolding. |
| E10 | `policy_or_direct_answer_handling_failure` | The tutor mishandles direct answer/code requests. | policy_request cases with leakage, no-show, or no alternative learning action. | Redirecting away from full solution toward a minimal learnable step. |

## Level 2 Families And Level 3 Surface Anchors

| Level 2 operational cognitive bridge family | Level 3 surface anchor examples |
| --- | --- |
| representation semantics | DP state, interval state, array meaning |
| transition / action mapping | recurrence branch, action source, previous-state dependency |
| predicate / decision semantics | binary-search check, feasibility predicate, true/false meaning |
| ordering / dependency control | binary boundary update, loop direction, update order |
| modeling relation | graph/tree abstraction, object-relation mapping |
| aggregation / contribution accounting | contribution sum, prefix/difference accumulation |
| data-structure operation mapping | lazy propagation, tree difference, maintained summary |
| correctness / invariant reasoning | greedy proof, exchange argument, invariant |
| implementation boundary | local code, index boundary, initialization |
| debugging evidence | debugging trace, minimal counterexample, print target |
| policy-request handling | direct-answer request, code-request redirect |

## Observed Error Distribution By Condition

| condition | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 31 | 1 | 27 | 2 | 4 | 25 | 7 | 0 | 0 | 1 |
| `codehelp_codeaid_clean` | 11 | 0 | 7 | 11 | 5 | 3 | 5 | 0 | 0 | 1 |
| `dbox_inspired_clean` | 11 | 2 | 4 | 5 | 3 | 5 | 4 | 0 | 0 | 1 |
| `dbox_inspired_guard` | 10 | 0 | 2 | 9 | 6 | 2 | 4 | 0 | 0 | 1 |
| `bridge_guided_dbox_style_guard` | 16 | 2 | 15 | 10 | 2 | 2 | 6 | 0 | 1 | 2 |
| `bridge_contract_compact_guard` | 14 | 0 | 8 | 7 | 3 | 1 | 5 | 0 | 1 | 0 |
| `bridge_contract_compact_guard_repair` | 7 | 0 | 4 | 8 | 2 | 0 | 2 | 0 | 0 | 0 |

These are multi-label error-pool counts, not row counts. The high E1/E3/E6 counts for `enhanced_prompt_only_clean` indicate that strong prompt-only often uses over-complete examples or high-burden tasks. Lower E1/E3/E6 counts for `bridge_contract_compact_guard_repair` should not be read as causal Repair evidence because main-experiment candidates differ by condition.

## Level 1 × Level 2 Coverage Summary

| error type | observed bridge families |
| --- | --- |
| E1 critical bridge leakage | representation; transition/action; predicate/decision; ordering/dependency; modeling; aggregation/contribution; data-structure operation; correctness/invariant; implementation; debugging evidence; policy request |
| E2 answer/code leakage | data-structure operation; correctness/invariant; implementation; policy request |
| E3 over-complete micro-example | representation; transition/action; predicate/decision; ordering/dependency; modeling; aggregation/contribution; data-structure operation; correctness/invariant; implementation; debugging evidence; policy request |
| E4 wrong/shifted focus | representation; transition/action; predicate/decision; ordering/dependency; modeling; aggregation/contribution; correctness/invariant; implementation; debugging evidence |
| E5 under-scaffolded / too vague | representation; transition/action; predicate/decision; ordering/dependency; modeling; aggregation/contribution; correctness/invariant; implementation; debugging evidence; policy request |
| E6 excessive burden | all observed families |
| E7 context misalignment | mostly short-question representation / transition cases without recent dialogue |
| E8 over-safe refusal / empty help | not observed as a frequent row-level tag in this derived pool; keep as a policy-safety taxonomy slot |
| E9 factual / algorithmic error | ordering/dependency; debugging evidence |
| E10 policy/direct-answer handling failure | policy-request handling |

## Typical Examples

| error type | typical case_id / condition examples |
| --- | --- |
| E1 | `dialogue_v3_001_state_representation_semantics` / `enhanced_prompt_only_clean`; `dialogue_v3_012_predicate_check_semantics` / `dbox_inspired_guard`; `dialogue_v3_020_boundary_update_order` / `bridge_guided_dbox_style_guard` |
| E2 | `dialogue_v3_031_data_structure_operation_semantics` / `enhanced_prompt_only_clean`; `dialogue_v3_044_implementation_boundary` / `dbox_inspired_clean`; `dialogue_v3_049_policy_request` / `bridge_guided_dbox_style_guard` |
| E3 | `dialogue_v3_001_state_representation_semantics` / `enhanced_prompt_only_clean`; `dialogue_v3_015_predicate_check_semantics` / `bridge_contract_compact_guard`; `dialogue_v3_038_correctness_invariant` / `bridge_guided_dbox_style_guard` |
| E4 | `dialogue_v3_007_transition_recurrence_source` / `codehelp_codeaid_clean`; `dialogue_v3_024_modeling_object_relation` / `bridge_guided_dbox_style_guard`; `dialogue_v3_047_debugging_evidence` / `bridge_guided_dbox_style_guard` |
| E5 | `dialogue_v3_001_state_representation_semantics` / `bridge_guided_dbox_style_guard`; `dialogue_v3_011_transition_recurrence_source` / `bridge_contract_compact_guard`; `dialogue_v3_045_debugging_evidence` / `codehelp_codeaid_clean` |
| E6 | `dialogue_v3_001_state_representation_semantics` / `enhanced_prompt_only_clean`; `dialogue_v3_036_correctness_invariant` / `enhanced_prompt_only_clean`; `dialogue_v3_048_policy_request` / `enhanced_prompt_only_clean` |
| E7 | `dialogue_v3_001_state_representation_semantics` / `bridge_guided_dbox_style_guard`; `dialogue_v3_002_state_representation_semantics` / `dbox_inspired_guard`; `dialogue_v3_008_transition_recurrence_source` / `codehelp_codeaid_clean` |
| E8 | no stable high-frequency example in the derived pool; inspect the policy slice manually if this becomes a reviewer concern |
| E9 | `dialogue_v3_017_boundary_update_order` / `bridge_contract_compact_guard`; `dialogue_v3_047_debugging_evidence` / `bridge_guided_dbox_style_guard` |
| E10 | `dialogue_v3_048_policy_request` / `bridge_guided_dbox_style_guard`; `dialogue_v3_049_policy_request` / `enhanced_prompt_only_clean`; `dialogue_v3_050_policy_request` / `dbox_inspired_clean` |

## Paper Wording

Can write: observed errors span multiple cognitive bridge families and surface anchors; critical bridge leakage is not limited to DP state definitions or binary-search checks.

Do not write: this taxonomy covers all CP tutoring errors, or each error type is sufficiently sampled. This is an observed taxonomy and needs expansion on larger, broader, multi-turn datasets.
