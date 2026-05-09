import json
import unittest
from pathlib import Path


class RuntimeBridgeContractSchemaTests(unittest.TestCase):
    def test_runtime_contract_schema_is_compact_and_not_full_human_schema(self):
        schema = json.loads(Path("docs/research/runtime_bridge_contract_schema_v1.json").read_text(encoding="utf-8"))
        properties = schema["properties"]
        required = set(schema["required"])

        expected = {
            "turn_type",
            "diagnosis_uncertainty",
            "algorithm_topic_l1",
            "algorithm_topic_l2",
            "primary_bridge_family",
            "selected_focus_id",
            "selected_focus_confidence",
            "max_scaffold_level",
            "help_forms",
            "forbidden_content",
            "leakage_risk",
            "confidence",
        }
        human_only = {
            "secondary_bridge_family",
            "secondary_bridge_subtype_id",
            "coach_free_notes",
            "new_focus_candidate",
            "evidence_quote",
        }

        self.assertTrue(expected.issubset(required))
        self.assertFalse(human_only & set(properties))
        self.assertEqual(2, properties["help_forms"]["maxItems"])
        self.assertEqual(3, properties["forbidden_content"]["maxItems"])


if __name__ == "__main__":
    unittest.main()
