# Coach A Held-out 50 AI Draft Labels (2026-05-13)

## Overview

- Labeled rows: 50
- `review_status`: all `labeled`
- Reference type: `single_coach_reference` / `raw`
- Output JSONL: `docs/research/coach_a_heldout_50_ai_labeled_v1_20260513.jsonl`
- Labeling policy: uses active abstract subtypes from `bridge_subtype_registry_v2.json`; concrete algorithm context is recorded through `registered_focus_id`, subtype notes, and free-text notes.

## Subtype Distribution

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

## Family Distribution

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

## Leakage Risk Distribution

- `high`: 37
- `medium`: 10
- `low`: 3

## Confidence Distribution

- `3`: 7
- `4`: 15
- `5`: 28

## Low-Confidence Cases

- `heldout_cp_007`
- `heldout_cp_018`
- `heldout_cp_022`
- `heldout_cp_031`
- `heldout_cp_034`
- `heldout_cp_038`
- `heldout_cp_043`

## Needs-New-Focus Cases

- `heldout_cp_018`: `binary_search_answer_range_bounds`
- `heldout_cp_031`: `fenwick_index_range_semantics`
- `heldout_cp_034`: `rolling_hash_weight_alignment`
- `heldout_cp_038`: `modular_normalization_negative_remainder`
- `heldout_cp_043`: `debug_invariant_probe`

## Potentially Ambiguous / Multi-Bridge Cases

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

## Schema Pain Points

- `heldout_cp_007`: general grid-DP predecessor source does not have a very precise subtype; this draft approximates it as `transition.combinatorial_recurrence`.
- `heldout_cp_018`: binary-search initial answer bounds are closer to answer-range / constraint-bound reasoning than boundary-update direction; this draft uses `goal.constraint_decomposition` and suggests a new focus.
- `heldout_cp_031`: the segment represented by each Fenwick index is closer to maintained-summary semantics, which is listed as a candidate in the coverage review but is not yet in the registry; this draft approximates it as `aggregation.cumulative_range_query`.
- `heldout_cp_034`: rolling-hash substring weight alignment has no existing focus; this draft approximates it as an aggregation / contribution query shape.
- `heldout_cp_038`: negative modular normalization is not integer overflow; the current implementation-boundary subtype is imperfect, so this draft uses `implementation.integer_overflow` and marks `needs_new_focus`.
- `heldout_cp_043`: converting intermediate variables into a printable local invariant lacks a dedicated debugging subtype; this draft approximates it as `debug.minimal_failing_case`.
- Policy-style cases such as `heldout_cp_044`, `heldout_cp_047`, `heldout_cp_048`, and `heldout_cp_050` do not have concrete bridge-specific forbidden content; this draft relies mainly on `general_forbidden_content` and policy subtypes.

## Interpretation

This is an AI-assisted first-pass Coach A draft. It is useful for development and triage, but final paper metrics should still rely on human coach review, overlap labeling, adjudication, and grader calibration.
