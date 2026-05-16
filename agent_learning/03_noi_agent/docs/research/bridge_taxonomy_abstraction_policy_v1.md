# Bridge Taxonomy Abstraction Policy v1

This document defines the granularity boundary for `bridge_subtype`, `registered_focus_id`, and `forbidden_content` in Research v1.

## Core Rule

Do not turn bridge subtypes into an algorithm list.

Algorithm information should live in:

- `algorithm_topic_l1`
- `algorithm_topic_l2`
- the retrieval context for `registered_focus_id`
- free-text fields such as `primary_bridge_subtype_note` and `missing_bridge_instance`

Bridge labels should capture:

- the transferable reasoning relation the student is missing;
- whether that relation is about state semantics, transition source, predicate condition, dependency order, contribution aggregation, invariant, implementation boundary, debugging evidence, etc.;
- which kind of critical relation the tutor must not directly complete in this turn.

## Why This Matters

If the subtype layer contains `Dijkstra stale-entry guard`, it immediately raises questions:

- Why not SPFA?
- Why not Floyd?
- Why not Tarjan, Dinic, or Kruskal?

That means the taxonomy has mixed an algorithm instance into the bridge layer. The fix is not to add every algorithm. The fix is to abstract the bridge:

```text
predicate.obsolete_candidate_guard
```

This covers whether a popped or selected candidate from a multi-candidate structure is still valid. A stale priority-queue entry in Dijkstra is one example.

## Current Abstract Replacements

| Old label | New label | Meaning |
| --- | --- | --- |
| `predicate.dijkstra_stale_entry_guard` | `predicate.obsolete_candidate_guard` | Whether a candidate from a queue/heap/multi-candidate structure is stale or invalid |
| `state.kmp_prefix_function_semantics` | `state.failure_link_or_prefix_semantics` | State semantics for fallback, prefix, or shared-history information |
| `ordering.reverse_capacity_loop` | `ordering.single_use_update_order` | Avoid reusing a state written earlier in the same update round |
| `aggregation.tree_path_difference_marking` | `aggregation.path_contribution_marking` | Compress path/interval contributions into boundary or node marks and aggregate later |
| `implementation.dfs_parent_guard` | `implementation.traversal_back_edge_guard` | Avoid backtracking, revisiting, or cycling during traversal |
| `correctness.shortest_path_invariant` | `correctness.settled_candidate_invariant` | Why a selected/settled candidate will not be overturned later |

Old labels remain in `bridge_subtype_registry_v2.json` as `deprecated` compatibility aliases, so historical labels can still validate. New coach workbooks should not prioritize those old labels.

## Forbidden Content Style

`bridge_specific_forbidden_content` should describe abstract leakage shapes, not algorithm-specific recipes.

Recommended labels:

- `no_exact_state_definition`
- `no_exact_recurrence`
- `no_exact_check_condition`
- `no_exact_boundary_update_rule`
- `no_exact_guard_condition`
- `no_exact_modeling_plan`
- `no_full_invariant_proof`
- `no_exact_contribution_formula`
- `no_exact_iteration_template`
- `no_exact_data_structure_template`
- `no_complete_local_condition`
- `no_fully_worked_micro_trace`

Example:

```text
Avoid: Do not directly give the Dijkstra stale-entry condition.
Prefer: Use no_exact_guard_condition, and explain in missing_bridge_instance that this case is about deciding whether a popped candidate still matches the current dist value.
```

## Annotation Guidance

Coaches should label in this order:

1. Choose `primary_bridge_family`.
2. Choose an abstract `primary_bridge_subtype_id`.
3. Use `algorithm_topic_l1/l2` or `registered_focus_id` to record algorithm context.
4. Write the concrete algorithm context in `primary_bridge_subtype_note`.
5. Use `bridge_specific_forbidden_content` to record the abstract type of content that must not be directly revealed.

This keeps the taxonomy from expanding into an algorithm ontology while preserving the CP-specific analysis needed for the paper.
