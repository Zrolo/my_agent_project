import json
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "docs" / "research" / "turn_annotation_schema_v1.json"
DOC_PATH = BASE_DIR / "docs" / "research" / "research_schema_v1.md"


class ResearchSchemaTests(unittest.TestCase):
    def test_turn_annotation_schema_file_is_valid_json(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual("CPMissingBridgeTurnAnnotationV1", schema["title"])
        self.assertEqual("object", schema["type"])

    def test_turn_annotation_schema_requires_research_core_fields(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        required = set(schema["required"])
        self.assertTrue(
            {
                "schema_version",
                "turn",
                "context",
                "coach_label",
                "system_prediction",
                "system_response",
                "response_evaluation",
                "next_turn_learning_evidence",
                "privacy",
            }.issubset(required)
        )

    def test_turn_annotation_schema_contains_bridge_and_leakage_enums(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        defs = schema["$defs"]

        self.assertIn("representation_bridge", defs["bridge_family"]["enum"])
        self.assertIn("predicate_bridge", defs["bridge_family"]["enum"])
        self.assertIn("unknown_bridge", defs["bridge_family"]["enum"])
        self.assertIn("major_bridge_leakage", defs["leakage_label"]["enum"])
        self.assertIn("answer_leakage", defs["leakage_label"]["enum"])

    def test_research_schema_doc_names_paper_variables(self):
        text = DOC_PATH.read_text(encoding="utf-8")

        for phrase in (
            "CP-MissingBridgeBench",
            "coach_label",
            "system_prediction",
            "response_evaluation",
            "next_turn_learning_evidence",
            "baseline_group",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
