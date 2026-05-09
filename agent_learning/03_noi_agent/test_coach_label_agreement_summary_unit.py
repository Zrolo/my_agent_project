import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat.summarize_coach_label_agreement import summarize_agreement


class CoachLabelAgreementSummaryTests(unittest.TestCase):
    def test_summarize_agreement_reports_exact_and_relaxed_matches(self):
        annotator_a = [
            {
                "case_id": "case_1",
                "student_problem_solving_state": "method_application_gap",
                "primary_bridge_family": "predicate_condition_bridge",
                "secondary_bridge_family": "implementation_boundary_bridge",
                "registered_focus_id": "check_condition",
                "secondary_registered_focus_id": "binary_search_bound_direction",
                "max_scaffold_level": "L2",
            },
            {
                "case_id": "case_2",
                "student_problem_solving_state": "correctness_reasoning_gap",
                "primary_bridge_family": "correctness_invariant_bridge",
                "registered_focus_id": "greedy_exchange_argument",
                "max_scaffold_level": "L2",
            },
        ]
        annotator_b = [
            {
                "case_id": "case_1",
                "student_problem_solving_state": "method_application_gap",
                "primary_bridge_family": "implementation_boundary_bridge",
                "secondary_bridge_family": "predicate_condition_bridge",
                "registered_focus_id": "binary_search_bound_direction",
                "secondary_registered_focus_id": "check_condition",
                "max_scaffold_level": "L2",
            },
            {
                "case_id": "case_2",
                "student_problem_solving_state": "method_application_gap",
                "primary_bridge_family": "method_application_gap",
                "registered_focus_id": "method_selection",
                "max_scaffold_level": "L3",
            },
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            a_path = Path(tmpdir) / "a.jsonl"
            b_path = Path(tmpdir) / "b.jsonl"
            a_path.write_text("\n".join(json.dumps(row) for row in annotator_a) + "\n", encoding="utf-8")
            b_path.write_text("\n".join(json.dumps(row) for row in annotator_b) + "\n", encoding="utf-8")

            summary = summarize_agreement(a_path, b_path)

        self.assertEqual(2, summary["paired_count"])
        self.assertEqual(0.5, summary["exact_agreement"]["student_problem_solving_state"])
        self.assertEqual(0.0, summary["exact_agreement"]["primary_bridge_family"])
        self.assertEqual(0.5, summary["relaxed_agreement"]["bridge_family_primary_or_secondary"])
        self.assertEqual(0.5, summary["relaxed_agreement"]["focus_primary_or_secondary"])
        self.assertEqual(0.5, summary["exact_agreement"]["max_scaffold_level"])
        self.assertEqual(["case_2"], summary["needs_adjudication_case_ids"])


if __name__ == "__main__":
    unittest.main()
