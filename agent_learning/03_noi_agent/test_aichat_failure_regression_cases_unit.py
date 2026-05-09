import json
import unittest
from pathlib import Path


REGRESSION_CASES_PATH = Path("docs/research/aichat_failure_regression_cases_micro_example_policy_v1.jsonl")


class AIChatFailureRegressionCasesTests(unittest.TestCase):
    def _load_cases(self) -> list[dict]:
        rows = []
        for line in REGRESSION_CASES_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def test_micro_example_policy_failures_should_be_recorded_as_regression_cases(self):
        cases = self._load_cases()
        by_id = {case["case_id"]: case for case in cases}

        self.assertIn("cp_bridge_006", by_id)
        self.assertIn("cp_bridge_010", by_id)

        self.assertEqual("prompt_or_template_leakage", by_id["cp_bridge_006"]["failure_type"])
        self.assertIn("must_not_expose_internal_prompt", by_id["cp_bridge_006"]["expected_regression_checks"])

        self.assertEqual("safe_but_useless_rule_fallback", by_id["cp_bridge_010"]["failure_type"])
        self.assertIn("must_provide_concrete_next_step", by_id["cp_bridge_010"]["expected_regression_checks"])

    def test_regression_cases_should_preserve_coach_labels_and_notes(self):
        required_fields = {
            "case_id",
            "response_id",
            "dataset_id",
            "coach_quality_label",
            "coach_leakage_label",
            "coach_note_summary",
            "failure_type",
            "expected_regression_checks",
            "why_it_matters",
        }

        for case in self._load_cases():
            with self.subTest(case_id=case.get("case_id")):
                self.assertTrue(required_fields.issubset(case))
                self.assertTrue(case["expected_regression_checks"])
                self.assertIn(case["coach_quality_label"], {"bad", "okay", "good", "uncertain"})


if __name__ == "__main__":
    unittest.main()
