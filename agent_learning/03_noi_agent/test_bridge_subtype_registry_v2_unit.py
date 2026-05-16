import json
import unittest
from pathlib import Path

from evals.aichat.coach_labeling_schema_v2 import BRIDGE_SPECIFIC_FORBIDDEN_CONTENT, BRIDGE_SUBTYPES


class BridgeSubtypeRegistryV2Tests(unittest.TestCase):
    def test_registry_covers_schema_subtypes_and_required_fields(self):
        data = json.loads(Path("docs/research/bridge_subtype_registry_v2.json").read_text(encoding="utf-8"))
        subtypes = data["subtypes"]
        subtype_ids = {item["subtype_id"] for item in subtypes}

        self.assertTrue(set(BRIDGE_SUBTYPES).issubset(subtype_ids))
        self.assertEqual(len(subtype_ids), len(subtypes))
        for item in subtypes:
            self.assertIsInstance(item["subtype_id"], str)
            self.assertIsInstance(item["family"], str)
            self.assertIsInstance(item["description"], str)
            self.assertIsInstance(item["examples"], list)
            self.assertTrue(item["examples"])

    def test_registry_contains_new_policy_and_competitive_programming_subtypes(self):
        data = json.loads(Path("docs/research/bridge_subtype_registry_v2.json").read_text(encoding="utf-8"))
        subtype_ids = {item["subtype_id"] for item in data["subtypes"]}

        expected = {
            "modeling.constraint_to_edge",
            "modeling.graph_vertices_edges",
            "modeling.interval_to_events",
            "method.monotone_answer_search_signal",
            "method.stateful_subproblem_signal",
            "method.local_choice_rule_signal",
            "state.table_or_memo_cell_semantics",
            "state.encoded_set_semantics",
            "state.deferred_update_semantics",
            "state.augmented_process_state",
            "predicate.feasibility_truth_direction",
            "predicate.boundary_update_direction",
            "predicate.improvement_update_condition",
            "ordering.subproblem_size_dependency_order",
            "aggregation.cumulative_range_query",
            "aggregation.inclusion_exclusion_query",
            "aggregation.boundary_delta_update",
            "ds.priority_candidate_operation_mapping",
            "ds.component_merge_query_mapping",
            "ds.dominated_candidate_stack_mapping",
            "ordering.rolling_array_overwrite_order",
            "correctness.local_choice_exchange_argument",
            "correctness.settled_candidate_invariant",
            "correctness.monotonic_structure_dominance",
            "complexity.bruteforce_bottleneck",
            "complexity.replace_inner_loop_with_structure",
            "debug.wa_counterexample_construction",
            "debug.tle_bottleneck_localization",
            "implementation.initialization_base_case",
            "implementation.io_format_parsing",
            "policy.critical_bridge_request",
            "policy.local_completion_request",
        }

        self.assertTrue(expected.issubset(subtype_ids))

    def test_active_schema_uses_abstract_bridge_subtypes_not_algorithm_slots(self):
        active_subtype_ids = set(BRIDGE_SUBTYPES)

        abstract_replacements = {
            "state.failure_link_or_prefix_semantics",
            "predicate.obsolete_candidate_guard",
            "ordering.single_use_update_order",
            "aggregation.path_contribution_marking",
            "implementation.traversal_back_edge_guard",
            "correctness.settled_candidate_invariant",
            "method.monotone_answer_search_signal",
            "method.stateful_subproblem_signal",
            "method.local_choice_rule_signal",
            "state.table_or_memo_cell_semantics",
            "state.encoded_set_semantics",
            "state.deferred_update_semantics",
            "state.augmented_process_state",
            "predicate.feasibility_truth_direction",
            "predicate.boundary_update_direction",
            "predicate.improvement_update_condition",
            "ordering.subproblem_size_dependency_order",
            "aggregation.cumulative_range_query",
            "aggregation.inclusion_exclusion_query",
            "aggregation.boundary_delta_update",
            "ds.priority_candidate_operation_mapping",
            "ds.component_merge_query_mapping",
            "ds.dominated_candidate_stack_mapping",
            "correctness.local_choice_exchange_argument",
        }
        retired_algorithm_slots = {
            "state.kmp_prefix_function_semantics",
            "predicate.dijkstra_stale_entry_guard",
            "ordering.reverse_capacity_loop",
            "aggregation.tree_path_difference_marking",
            "implementation.dfs_parent_guard",
            "correctness.shortest_path_invariant",
            "method.binary_search_answer_signal",
            "method.dp_state_candidate_signal",
            "method.greedy_candidate_signal",
            "state.dp_state_semantics",
            "state.mask_semantics",
            "state.lazy_tag_semantics",
            "state.search_augmented_state",
            "predicate.check_truth_direction",
            "predicate.binary_search_bound_update",
            "predicate.relax_condition",
            "ordering.interval_dp_order",
            "aggregation.prefix_sum_1d",
            "aggregation.prefix_sum_2d",
            "aggregation.difference_array_range_update",
            "ds.heap_push_pop_mapping",
            "ds.union_find_operation_mapping",
            "ds.monotonic_stack_mapping",
            "correctness.greedy_exchange_argument",
        }

        self.assertTrue(abstract_replacements.issubset(active_subtype_ids))
        self.assertTrue(retired_algorithm_slots.isdisjoint(active_subtype_ids))

    def test_deprecated_algorithm_specific_subtypes_have_replacements(self):
        data = json.loads(Path("docs/research/bridge_subtype_registry_v2.json").read_text(encoding="utf-8"))
        deprecated = {
            item["subtype_id"]: item
            for item in data["subtypes"]
            if item.get("status") == "deprecated"
        }

        for subtype_id in {
            "state.kmp_prefix_function_semantics",
            "predicate.dijkstra_stale_entry_guard",
            "ordering.reverse_capacity_loop",
            "aggregation.tree_path_difference_marking",
            "implementation.dfs_parent_guard",
            "correctness.shortest_path_invariant",
            "method.binary_search_answer_signal",
            "method.dp_state_candidate_signal",
            "method.greedy_candidate_signal",
            "state.dp_state_semantics",
            "state.mask_semantics",
            "state.lazy_tag_semantics",
            "state.search_augmented_state",
            "predicate.check_truth_direction",
            "predicate.binary_search_bound_update",
            "predicate.relax_condition",
            "ordering.interval_dp_order",
            "aggregation.prefix_sum_1d",
            "aggregation.prefix_sum_2d",
            "aggregation.difference_array_range_update",
            "ds.heap_push_pop_mapping",
            "ds.union_find_operation_mapping",
            "ds.monotonic_stack_mapping",
            "correctness.greedy_exchange_argument",
        }:
            self.assertIn(subtype_id, deprecated)
            self.assertIn(deprecated[subtype_id].get("replaced_by"), BRIDGE_SUBTYPES)

    def test_bridge_specific_forbidden_content_uses_abstract_leakage_shapes(self):
        self.assertIn("no_exact_boundary_update_rule", BRIDGE_SPECIFIC_FORBIDDEN_CONTENT)
        self.assertIn("no_exact_guard_condition", BRIDGE_SPECIFIC_FORBIDDEN_CONTENT)
        self.assertIn("no_fully_worked_micro_trace", BRIDGE_SPECIFIC_FORBIDDEN_CONTENT)
        self.assertIn("no_full_invariant_proof", BRIDGE_SPECIFIC_FORBIDDEN_CONTENT)

        forbidden_text = "\n".join(BRIDGE_SPECIFIC_FORBIDDEN_CONTENT.values())
        for algorithm_word in ["Dijkstra", "SPFA", "Floyd", "并查集", "线段树"]:
            self.assertNotIn(algorithm_word, forbidden_text)


if __name__ == "__main__":
    unittest.main()
