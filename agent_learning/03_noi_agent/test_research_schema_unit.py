import json
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "docs" / "research" / "turn_annotation_schema_v1.json"
TRACE_SCHEMA_PATH = BASE_DIR / "docs" / "research" / "aichat_trace_schema_v1.json"
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

    def test_aichat_trace_schema_covers_latency_and_routing_fields(self):
        schema = json.loads(TRACE_SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual("AIChatTraceV1", schema["title"])
        required = set(schema["required"])
        self.assertTrue(
            {
                "trace_id",
                "student_id_hash",
                "problem_id",
                "route_name",
                "llm_call_count",
                "model_names",
                "prompt_hashes",
                "total_latency_ms",
                "final_level",
                "final_route_decision",
            }.issubset(required)
        )
        for latency_field in (
            "legacy_judge_latency_ms",
            "rules_latency_ms",
            "pedagogical_judge_v2_latency_ms",
            "classifier_latency_ms",
            "main_llm_latency_ms",
            "hard_gate_latency_ms",
            "output_guard_latency_ms",
        ):
            self.assertIn(latency_field, required)


if __name__ == "__main__":
    unittest.main()
