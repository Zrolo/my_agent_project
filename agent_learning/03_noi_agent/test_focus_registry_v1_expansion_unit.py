import json
import unittest
from pathlib import Path


class FocusRegistryExpansionTests(unittest.TestCase):
    def test_registry_contains_competitive_programming_focus_additions(self):
        data = json.loads(Path("docs/research/focus_registry_v1.json").read_text(encoding="utf-8"))
        focus_ids = [item["focus_id"] for item in data["focuses"]]

        expected = {
            "prefix_sum_1d",
            "prefix_sum_2d",
            "difference_array_range_update",
            "monotonic_stack_mapping",
            "dfs_parent_guard",
            "rolling_array_overwrite_order",
            "interval_dp_order",
            "relax_semantics",
            "shortest_path_method_choice",
            "dag_topological_dp_order",
            "tree_dp_child_merge",
            "bfs_augmented_state",
            "sweepline_event_modeling",
            "modular_multiplication_overflow",
            "kmp_prefix_function_semantics",
            "combinatorial_recurrence",
            "segment_tree_pushup",
            "dijkstra_stale_entry",
            "local_condition_completion",
            "direct_answer_request_policy",
            "constraint_to_graph_edge",
            "graph_vertices_edges_modeling",
            "binary_search_answer_monotonicity",
            "binary_search_bound_direction",
            "greedy_exchange_argument",
            "bruteforce_bottleneck_analysis",
            "wa_counterexample_construction",
            "tle_bottleneck_analysis",
            "initialization_base_case",
            "io_format_parsing",
            "critical_bridge_request_policy",
            "local_completion_policy",
            "union_find_operation_mapping",
            "heap_push_pop_mapping",
            "topological_zero_indegree_reason",
        }

        self.assertTrue(expected.issubset(set(focus_ids)))
        self.assertEqual(len(focus_ids), len(set(focus_ids)))
        self.assertFalse([item["focus_id"] for item in data["focuses"] if not item.get("bridge_family_v2")])


if __name__ == "__main__":
    unittest.main()
