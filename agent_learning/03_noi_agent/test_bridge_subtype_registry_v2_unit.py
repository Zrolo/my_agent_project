import json
import unittest
from pathlib import Path

from evals.aichat.coach_labeling_schema_v2 import BRIDGE_SUBTYPES


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
            "method.binary_search_answer_signal",
            "method.dp_state_candidate_signal",
            "method.greedy_candidate_signal",
            "ordering.rolling_array_overwrite_order",
            "correctness.greedy_exchange_argument",
            "correctness.shortest_path_invariant",
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


if __name__ == "__main__":
    unittest.main()
