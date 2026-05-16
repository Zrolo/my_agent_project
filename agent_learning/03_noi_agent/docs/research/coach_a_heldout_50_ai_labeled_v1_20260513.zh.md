# Coach A Held-out 50 AI 标注首版（2026-05-13）

## 总览

- 标注行数：50
- review_status：全部为 `labeled`
- reference 类型：`single_coach_reference` / `raw`
- 输出 JSONL：`docs/research/coach_a_heldout_50_ai_labeled_v1_20260513.jsonl`
- 口径：使用 `bridge_subtype_registry_v2.json` 中未 deprecated 的抽象 subtype；算法语境放在 `registered_focus_id`、`primary_bridge_subtype_note` 和自由备注中。

## Subtype 分布

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
- `correctness.monotonic_structure_dominance`: 1
- `debug.tle_bottleneck_localization`: 1
- `ds.component_merge_query_mapping`: 1
- `ds.priority_candidate_operation_mapping`: 1
- `goal.constraint_decomposition`: 1
- `implementation.initialization_base_case`: 1
- `implementation.io_format_parsing`: 1
- `implementation.loop_boundary`: 1
- `method.monotone_answer_search_signal`: 1
- `method.selection_signal`: 1
- `modeling.constraint_to_edge`: 1
- `modeling.graph_vertices_edges`: 1
- `modeling.objects_relations`: 1
- `ordering.single_use_update_order`: 1
- `predicate.local_if_boundary_condition`: 1
- `state.deferred_update_semantics`: 1
- `state.encoded_set_semantics`: 1
- `transition.child_to_parent_merge`: 1
- `transition.take_or_skip_cases`: 1
- `unknown`: 1

## Family 分布

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

## Leakage Risk 分布

- `high`: 37
- `medium`: 10
- `low`: 3

## Confidence 分布

- `3`: 7
- `4`: 15
- `5`: 28

## 低置信 Case（coach_confidence <= 3）

- heldout_cp_007（3，transition.combinatorial_recurrence）
- heldout_cp_018（3，goal.constraint_decomposition）
- heldout_cp_022（3，modeling.objects_relations）
- heldout_cp_031（3，aggregation.cumulative_range_query）
- heldout_cp_034（3，aggregation.cumulative_range_query）
- heldout_cp_038（3，implementation.integer_overflow）
- heldout_cp_043（3，debug.minimal_failing_case）

## Needs New Focus Case

- heldout_cp_018: binary_search_answer_range_bounds（goal.constraint_decomposition）
- heldout_cp_031: fenwick_index_range_semantics（aggregation.cumulative_range_query）
- heldout_cp_034: rolling_hash_weight_alignment（aggregation.cumulative_range_query）
- heldout_cp_038: modular_normalization_negative_remainder（implementation.integer_overflow）
- heldout_cp_043: debug_invariant_probe（debug.minimal_failing_case）

## 可能歧义 / 多桥 Case

- heldout_cp_003: acceptable_non_unique；主=method.stateful_subproblem_signal
- heldout_cp_004: acceptable_non_unique；主=method.stateful_subproblem_signal
- heldout_cp_007: acceptable_non_unique；主=transition.combinatorial_recurrence
- heldout_cp_008: acceptable_non_unique；主=transition.combinatorial_recurrence
- heldout_cp_014: acceptable_non_unique；主=predicate.boundary_update_direction
- heldout_cp_015: multi_bridge_case；主=predicate.feasibility_truth_direction，次=correctness.local_choice_exchange_argument
- heldout_cp_018: needs_new_focus; acceptable_non_unique；主=goal.constraint_decomposition
- heldout_cp_019: acceptable_non_unique；主=predicate.boundary_update_direction
- heldout_cp_022: acceptable_non_unique；主=modeling.objects_relations
- heldout_cp_024: acceptable_non_unique；主=state.augmented_process_state
- heldout_cp_026: multi_bridge_case；主=debug.wa_counterexample_construction，次=correctness.local_choice_exchange_argument
- heldout_cp_027: multi_bridge_case；主=ds.priority_candidate_operation_mapping，次=correctness.local_choice_exchange_argument
- heldout_cp_029: acceptable_non_unique；主=correctness.local_choice_exchange_argument
- heldout_cp_031: needs_new_focus; acceptable_non_unique；主=aggregation.cumulative_range_query
- heldout_cp_033: acceptable_non_unique；主=correctness.monotonic_structure_dominance
- heldout_cp_034: needs_new_focus; acceptable_non_unique；主=aggregation.cumulative_range_query
- heldout_cp_038: needs_new_focus; acceptable_non_unique；主=implementation.integer_overflow
- heldout_cp_042: acceptable_non_unique；主=debug.minimal_failing_case
- heldout_cp_043: needs_new_focus; multi_bridge_case；主=debug.minimal_failing_case，次=correctness.settled_candidate_invariant

## Schema 痛点

- `heldout_cp_007`：网格 DP 的一般“前驱来源”没有非常精确的 subtype，本版近似到 `transition.combinatorial_recurrence`。
- `heldout_cp_018`：二分答案初始上下界更像“答案范围/约束边界”，现有 `predicate.boundary_update_direction` 偏更新方向，因此标为 `goal.constraint_decomposition` 并建议新增 focus。
- `heldout_cp_031`：Fenwick 每个位置维护哪段属于“维护摘要语义”，覆盖文档中已列为候选但 registry 尚未收录，本版近似到 `aggregation.cumulative_range_query`。
- `heldout_cp_034`：滚动哈希子串权重对齐没有现成 focus，本版近似到累计/贡献查询形状。
- `heldout_cp_038`：负数取模归一化不是整数溢出，当前实现边界 subtype 不够贴，本版用 `implementation.integer_overflow` 近似并标注 needs_new_focus。
- `heldout_cp_043`：把中间变量转成可打印局部不变量缺少专门调试 subtype，本版近似到 `debug.minimal_failing_case`。
- 策略型样本（如 `heldout_cp_044`、`heldout_cp_047`、`heldout_cp_048`、`heldout_cp_050`）没有具体 bridge-specific forbidden content，本版保留空数组，主要依赖 `general_forbidden_content` 和 policy subtype。
