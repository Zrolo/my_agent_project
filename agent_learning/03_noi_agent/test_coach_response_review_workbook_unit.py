import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import export_coach_response_review_workbook as response_workbook


class CoachResponseReviewWorkbookTests(unittest.TestCase):
    def test_build_review_rows_hides_baseline_identity_and_uses_final_response(self):
        result_rows = [
            {
                "case_id": "case_1",
                "problem_ref": "P1048",
                "student_message": "状态怎么设？",
                "problem_context": "采药。",
                "recent_dialogue": "user: 我知道要 DP",
                "tutor_mode": "bridge_contract",
                "guard_mode": "predicted",
                "models": {"tutor_model_provider": "deepseek", "chat_thinking_mode": "disabled"},
                "candidate_response_text": "状态设 dp[j]。",
                "final_response_text": "先说说时间变化后要保留什么。",
                "final_response_source": "repair",
            }
        ]

        rows, key_rows = response_workbook.build_review_rows(result_rows, shuffle_seed=7)

        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual("case_1", row["case_id"])
        self.assertEqual("先说说时间变化后要保留什么。", row["response_text"])
        self.assertNotIn("bridge_contract", row.values())
        self.assertNotIn("deepseek", row.values())
        self.assertEqual("case_1", key_rows[0]["case_id"])
        self.assertEqual(row["anonymized_response_id"], key_rows[0]["anonymized_response_id"])
        self.assertEqual("bridge_contract", key_rows[0]["tutor_mode"])
        self.assertEqual("disabled", key_rows[0]["chat_thinking_mode"])
        self.assertEqual("repair", key_rows[0]["final_response_source"])

    def test_build_review_rows_uses_id_salt_to_avoid_cross_run_collisions(self):
        result_rows = [
            {
                "case_id": "case_1",
                "student_message": "状态怎么设？",
                "final_response_text": "先说说时间变化后要保留什么。",
                "tutor_mode": "bridge_contract",
                "guard_mode": "predicted",
                "pipeline_mode": "tutor_only",
                "final_response_source": "candidate",
            }
        ]

        rows_a, key_rows_a = response_workbook.build_review_rows(
            result_rows,
            shuffle_seed=7,
            id_salt="micro_example_policy_a",
        )
        rows_b, key_rows_b = response_workbook.build_review_rows(
            result_rows,
            shuffle_seed=7,
            id_salt="micro_example_policy_b",
        )

        self.assertNotEqual(rows_a[0]["anonymized_response_id"], rows_b[0]["anonymized_response_id"])
        self.assertEqual(rows_a[0]["anonymized_response_id"], key_rows_a[0]["anonymized_response_id"])
        self.assertEqual(rows_b[0]["anonymized_response_id"], key_rows_b[0]["anonymized_response_id"])

    def test_write_review_csv_has_rubric_columns(self):
        rows, _ = response_workbook.build_review_rows(
            [{"case_id": "case_1", "student_message": "不会", "final_response_text": "先贴题面。"}],
            shuffle_seed=1,
        )
        output = io.StringIO()

        response_workbook.write_review_csv(output, rows)

        output.seek(0)
        reader = csv.DictReader(output)
        self.assertIn("coach_bridge_identification_score", reader.fieldnames)
        self.assertIn("coach_leakage_label", reader.fieldnames)
        self.assertIn("coach_preference_rank", reader.fieldnames)

    def test_main_writes_blind_workbook_and_key(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "results.jsonl"
            output_csv = Path(tmpdir) / "review.csv"
            key_csv = Path(tmpdir) / "review.key.csv"
            input_path.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "student_message": "不会",
                        "final_response_text": "先贴题面。",
                        "tutor_mode": "current_system",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            exit_code = response_workbook.main(
                [
                    "--input-jsonl",
                    str(input_path),
                    "--output-csv",
                    str(output_csv),
                    "--key-csv",
                    str(key_csv),
                    "--shuffle-seed",
                    "3",
                    "--id-salt",
                    "unit_test_run",
                ]
            )

            self.assertEqual(0, exit_code)
            self.assertTrue(output_csv.exists())
            self.assertTrue(key_csv.exists())
            self.assertIn("anonymized_response_id", output_csv.read_text(encoding="utf-8-sig"))
            self.assertIn("current_system", key_csv.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
