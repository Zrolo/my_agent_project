import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import validate_coach_workbook as validator


class CoachWorkbookValidationTests(unittest.TestCase):
    def test_validate_rows_accepts_registered_focus_and_multilabel_help_forms(self):
        rows = [
            {
                "case_id": "case_1",
                "coach_problem_solving_state": "problem_representation_unclear",
                "coach_bridge_family": "representation_bridge",
                "coach_secondary_bridge_family": "",
                "coach_known_focus": "state_design",
                "coach_bridge_subtype": "dp_state_design",
                "coach_help_seeking_type": "instrumental_help",
                "coach_allowed_help_level": "L2",
                "coach_help_forms": "guiding_question;micro_example",
                "coach_needs_new_focus": "false",
                "coach_confidence": "4",
                "review_status": "labeled",
            }
        ]

        errors = validator.validate_rows(rows, focus_ids={"state_design"})

        self.assertEqual([], errors)

    def test_validate_rows_reports_invalid_enums_and_unknown_focus(self):
        rows = [
            {
                "case_id": "case_bad",
                "coach_problem_solving_state": "not_a_state",
                "coach_bridge_family": "representation_bridge",
                "coach_known_focus": "made_up_focus",
                "coach_help_seeking_type": "instrumental_help",
                "coach_allowed_help_level": "L4",
                "coach_help_forms": "micro_example;made_up_form",
                "coach_needs_new_focus": "maybe",
                "coach_confidence": "9",
                "review_status": "done",
            }
        ]

        errors = validator.validate_rows(rows, focus_ids={"state_design"})
        fields = {error["field"] for error in errors}

        self.assertIn("coach_problem_solving_state", fields)
        self.assertIn("coach_known_focus", fields)
        self.assertIn("coach_allowed_help_level", fields)
        self.assertIn("coach_help_forms", fields)
        self.assertIn("coach_needs_new_focus", fields)
        self.assertIn("coach_confidence", fields)
        self.assertIn("review_status", fields)

    def test_main_outputs_json_report_for_workbook(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workbook_path = Path(tmpdir) / "workbook.csv"
            registry_path = Path(tmpdir) / "focus_registry.json"
            registry_path.write_text(
                json.dumps({"focuses": [{"focus_id": "state_design"}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            with workbook_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "case_id",
                        "coach_known_focus",
                        "coach_allowed_help_level",
                        "review_status",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "case_id": "case_1",
                        "coach_known_focus": "unknown",
                        "coach_allowed_help_level": "L2",
                        "review_status": "labeled",
                    }
                )
            stdout = io.StringIO()

            exit_code = validator.main(
                [
                    "--input-csv",
                    str(workbook_path),
                    "--focus-registry",
                    str(registry_path),
                ],
                stdout=stdout,
            )

        self.assertEqual(0, exit_code)
        report = json.loads(stdout.getvalue())
        self.assertEqual(1, report["row_count"])
        self.assertEqual(0, report["error_count"])


if __name__ == "__main__":
    unittest.main()
