import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat.summarize_coach_label_agreement import main, render_report_en, render_report_zh, summarize_agreement


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

    def test_render_reports_include_needs_adjudication_cases(self):
        summary = {
            "annotator_a_jsonl": "a.jsonl",
            "annotator_b_jsonl": "b.jsonl",
            "annotator_a_count": 2,
            "annotator_b_count": 2,
            "paired_count": 2,
            "unpaired_a_case_ids": [],
            "unpaired_b_case_ids": [],
            "exact_agreement": {
                "student_problem_solving_state": 0.5,
                "primary_bridge_family": 0.0,
                "registered_focus_id": 0.5,
                "max_scaffold_level": 0.5,
                "leakage_risk": None,
            },
            "relaxed_agreement": {
                "bridge_family_primary_or_secondary": 0.5,
                "focus_primary_or_secondary": 0.5,
            },
            "needs_adjudication_count": 1,
            "needs_adjudication_case_ids": ["case_2"],
        }

        zh = render_report_zh(summary)
        en = render_report_en(summary)

        self.assertIn("case_2", zh)
        self.assertIn("需要裁决", zh)
        self.assertIn("case_2", en)
        self.assertIn("Needs Adjudication", en)

    def test_main_writes_json_and_bilingual_markdown(self):
        annotator_a = [
            {
                "case_id": "case_1",
                "student_problem_solving_state": "method_application_gap",
                "primary_bridge_family": "predicate_condition_bridge",
                "registered_focus_id": "check_condition",
                "max_scaffold_level": "L2",
            }
        ]
        annotator_b = [
            {
                "case_id": "case_1",
                "student_problem_solving_state": "method_application_gap",
                "primary_bridge_family": "predicate_condition_bridge",
                "registered_focus_id": "check_condition",
                "max_scaffold_level": "L2",
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            a_path = tmp / "a.jsonl"
            b_path = tmp / "b.jsonl"
            output_json = tmp / "agreement.json"
            output_md_zh = tmp / "agreement.zh.md"
            output_md = tmp / "agreement.md"
            a_path.write_text("\n".join(json.dumps(row) for row in annotator_a) + "\n", encoding="utf-8")
            b_path.write_text("\n".join(json.dumps(row) for row in annotator_b) + "\n", encoding="utf-8")

            exit_code = main(
                [
                    "--annotator-a-jsonl",
                    str(a_path),
                    "--annotator-b-jsonl",
                    str(b_path),
                    "--output-json",
                    str(output_json),
                    "--output-md-zh",
                    str(output_md_zh),
                    "--output-md",
                    str(output_md),
                ],
                stdout=io.StringIO(),
            )

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            zh_text = output_md_zh.read_text(encoding="utf-8")
            en_text = output_md.read_text(encoding="utf-8")

        self.assertEqual(0, exit_code)
        self.assertEqual(1, payload["paired_count"])
        self.assertIn("Coach Label Agreement Summary", zh_text)
        self.assertIn("Coach Label Agreement Summary", en_text)


if __name__ == "__main__":
    unittest.main()
