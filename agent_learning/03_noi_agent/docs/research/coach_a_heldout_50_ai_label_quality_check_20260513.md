# Coach A Held-out 50 AI Label Quality Check (2026-05-13)

## Conclusion

This check covers `coach_a_heldout_50_ai_labeled_v1_20260513.jsonl`. The file is usable as an **AI-assisted draft reference** for development analysis, but it should not be described as final gold labels.

Check summary:

- Rows: 50
- Case IDs match `bridgebench_cp_heldout_v1_50_draft.jsonl`: yes
- Duplicate case IDs: 0
- Deprecated bridge subtypes: 0
- Family-subtype mismatches: 0
- `needs_new_focus` without candidate name: 0
- Invalid confidence values: 0
- Human priority review recommended for 7 low-confidence cases, 5 needs-new-focus cases, and several multi-bridge / ambiguous cases.

## Dataset Gate

`bridgebench_cp_heldout_v1_50_draft.jsonl` passed the held-out 50 dataset validation:

- row_count: 50
- category coverage:
  - `binary_search_boundary`: 4
  - `binary_search_predicate`: 5
  - `data_structure_semantics`: 5
  - `debugging_evidence`: 4
  - `dp_state`: 5
  - `dp_transition`: 5
  - `graph_tree_modeling`: 5
  - `greedy_correctness`: 5
  - `implementation_boundary`: 5
  - `policy_request`: 7
- recent dialogue distribution:
  - none: 10
  - short: 25
  - long: 15
- student code excerpt distribution:
  - none: 38
  - present: 12
- dev seed case id overlap: 0 errors

## Label Distribution

### Bridge Family

- `predicate_condition_bridge`: 8
- `debugging_evidence_bridge`: 6
- `representation_state_bridge`: 6
- `implementation_boundary_bridge`: 5
- `correctness_invariant_bridge`: 4
- `method_selection_bridge`: 4
- `transition_recurrence_bridge`: 4
- `unknown_or_not_applicable`: 4
- `modeling_bridge`: 3
- `aggregation_contribution_bridge`: 2
- `data_structure_operation_bridge`: 2
- `goal_constraint_bridge`: 1
- `ordering_dependency_bridge`: 1

### Bridge Subtype

- `predicate.boundary_update_direction`: 4
- `correctness.local_choice_exchange_argument`: 3
- `debug.minimal_failing_case`: 3
- `policy.direct_answer_request`: 3
- `predicate.feasibility_truth_direction`: 3
- `aggregation.cumulative_range_query`: 2
- `debug.wa_counterexample_construction`: 2
- `implementation.integer_overflow`: 2
- `method.stateful_subproblem_signal`: 2
- `state.augmented_process_state`: 2
- `state.table_or_memo_cell_semantics`: 2
- `transition.combinatorial_recurrence`: 2
- Other subtypes: 1 each

### Leakage Risk

- `high`: 37
- `medium`: 10
- `low`: 3

### Coach Confidence

- `5`: 28
- `4`: 15
- `3`: 7

## Priority Human Review Cases

### Low-Confidence Cases

- `heldout_cp_007`
- `heldout_cp_018`
- `heldout_cp_022`
- `heldout_cp_031`
- `heldout_cp_034`
- `heldout_cp_038`
- `heldout_cp_043`

### Needs-New-Focus Cases

- `heldout_cp_018`: `binary_search_answer_range_bounds`
- `heldout_cp_031`: `fenwick_index_range_semantics`
- `heldout_cp_034`: `rolling_hash_weight_alignment`
- `heldout_cp_038`: `modular_normalization_negative_remainder`
- `heldout_cp_043`: `debug_invariant_probe`

### Multi-Bridge / Acceptably Non-Unique Cases

- `heldout_cp_003`
- `heldout_cp_004`
- `heldout_cp_007`
- `heldout_cp_008`
- `heldout_cp_014`
- `heldout_cp_015`
- `heldout_cp_018`
- `heldout_cp_019`
- `heldout_cp_022`
- `heldout_cp_024`
- `heldout_cp_026`
- `heldout_cp_027`
- `heldout_cp_029`
- `heldout_cp_031`
- `heldout_cp_033`
- `heldout_cp_034`
- `heldout_cp_038`
- `heldout_cp_042`
- `heldout_cp_043`

## Note

`heldout_cp_049` is a `debugging_evidence_bridge` case with empty `bridge_specific_forbidden_content`, while `general_forbidden_content` includes `no_guess_without_context` and `no_full_solution`.

This is not a hard schema error, because insufficient-debugging-evidence turns may not have a concrete formula or bridge relation to forbid. If future labels require bridge-specific forbidden content for all non-policy cases, consider adding a debugging-specific forbidden label such as:

```text
no_specific_bug_fix_without_evidence
```

Do not add this label only for this single case before the formal 50-case stage, because that would expand the schema again.

## Research Interpretation

This AI draft is suitable for:

- dev-stage reference drafting;
- provisional reference for response generation;
- schema pain-point discovery;
- supporting later Coach A / Coach B review.

It is not suitable for:

- final gold-label claims;
- headline agreement metrics;
- bypassing human review before final held-out conclusions.

## Next Step

Proceed to **50-case response generation ablation**:

1. Freeze the condition set.
2. Generate system responses for all 50 cases.
3. Export an anonymized Chinese blind-review workbook.
4. Ask coaches to review response quality and leakage.
5. Run paired analysis and quality-leakage-cost trade-off analysis.
