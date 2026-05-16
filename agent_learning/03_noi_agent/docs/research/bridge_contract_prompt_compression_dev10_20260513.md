# Bridge Contract Prompt Compression Dev10 Result (2026-05-13)

## Purpose

This experiment checks whether the Bridge Contract generation prompt is overloaded. Instead of replacing the existing prompt directly, we add compact/minimal offline conditions and compare them with the long Bridge Contract and DBox-inspired guard variants.

This is AI self-review for development triage only. It is not coach gold labeling and not a formal paper headline result.

## Data and Conditions

Input data:

```text
docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl
```

The 10 selected cases cover different bridge buckets:

```text
state_representation_semantics
transition_recurrence_source
predicate_check_semantics
boundary_update_order
modeling_object_relation
aggregation_contribution_summary
data_structure_operation_semantics
correctness_invariant
implementation_boundary
policy_request
```

Conditions:

```text
dbox_inspired_guard
bridge_contract_guard
bridge_contract_compact_guard
bridge_contract_minimal_guard
```

Final output directory:

```text
evals/aichat/ad_hoc_runs/prompt_compression_dev10_20260513_final/
```

## Integrity

The final merged run passed integrity checks:

```text
case_count = 10
condition_count = 4
combined_row_count = 40
final_response_row_count = 40
review_row_count = 40
empty_final_response_rows = 0
stage_warning_rows = 0
headline_ready = true
analysis_ready = true
```

## Prompt Length

```text
long = 2848 chars
compact = 934 chars, about 33% of long
minimal = 719 chars, about 25% of long
```

## AI Self-Review Summary

| condition | overall | core6 | student_ready_pass | minor leakage | major/answer leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| dbox_inspired_guard | 3.90 | 1.98 | 9/10 | 1 | 0 |
| bridge_contract_compact_guard | 3.80 | 1.97 | 8/10 | 2 | 0 |
| bridge_contract_minimal_guard | 3.70 | 1.93 | 8/10 | 1 | 1 |
| bridge_contract_guard | 3.20 | 1.82 | 4/10 | 3 | 2 |

## Main Observations

1. `bridge_contract_compact_guard` clearly improves over the long `bridge_contract_guard`:
   - student-ready rises from 4/10 to 8/10;
   - major/answer leakage drops from 2 to 0;
   - overall rises from 3.20 to 3.80.

2. `bridge_contract_minimal_guard` should not be adopted directly:
   - its quality is higher than the long prompt;
   - but it has one major leakage case;
   - this suggests that excessive compression can weaken critical-bridge control.

3. `dbox_inspired_guard` remains a strong baseline:
   - AI self-review marks 9/10 responses as student-ready;
   - major/answer leakage is 0;
   - DBox-inspired decomposition should remain a formal strong baseline candidate.

4. The main issue with the long Bridge Contract prompt may not be lack of safety, but overloaded rule control that can produce answer-slot or over-complete reasoning:
   - asking directly which direction to move next;
   - asking directly where a recurrence comes from;
   - turning local observation into a near-complete transition or boundary-update prompt.

## Current Recommendation

Do not move `bridge_contract_minimal` into the formal main table.

`bridge_contract_compact` is worth including in the next coach blind-review candidate set, because it approaches DBox-inspired quality in this dev10 AI self-review and clearly improves over the long Bridge Contract.

Next steps:

```text
1. Keep long bridge_contract_guard as a historical/ablation comparison.
2. Add bridge_contract_compact_guard to the next coach blind-review candidate set.
3. Do not replace the formal prompt until human blind review confirms the signal.
4. If coach review supports compact, consider using compact as the Bridge Contract variant in held-out experiments.
```

## Boundary

This result is AI self-review only. It should not be treated as a formal paper conclusion. Its role is to select candidate prompts and show that longer prompts are not necessarily better. Whether compact should be adopted must be decided by later coach blind review and held-out evaluation.
