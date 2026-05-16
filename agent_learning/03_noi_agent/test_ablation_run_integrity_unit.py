import csv
import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import check_ablation_run_integrity


class AblationRunIntegrityTests(unittest.TestCase):
    def test_integrity_report_flags_empty_final_response_and_stage_warnings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            combined = root / "combined.jsonl"
            review = root / "review.csv"
            manifest = root / "manifest.json"
            rows = [
                {
                    "case_id": "case_1",
                    "condition_id": "enhanced_prompt_only_clean",
                    "final_response_text": "请先判断一个小例子。",
                    "stage_errors": {},
                },
                {
                    "case_id": "case_1",
                    "condition_id": "dbox_inspired_guard",
                    "final_response_text": "",
                    "final_response_source": "none",
                    "error": "bridge_judge_failed",
                    "stage_errors": {"bridge_judge": "timeout"},
                },
                {
                    "case_id": "case_2",
                    "condition_id": "enhanced_prompt_only_clean",
                    "final_response_text": "先说一句你的判断。",
                    "stage_errors": {"leakage_judge": "timeout"},
                },
                {
                    "case_id": "case_2",
                    "condition_id": "dbox_inspired_guard",
                    "final_response_text": "把当前问题拆小一步。",
                    "stage_errors": {},
                },
            ]
            combined.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                encoding="utf-8",
            )
            with review.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["case_id", "anonymized_response_id"])
                writer.writeheader()
                writer.writerow({"case_id": "case_1", "anonymized_response_id": "r1"})
                writer.writerow({"case_id": "case_2", "anonymized_response_id": "r2"})
                writer.writerow({"case_id": "case_2", "anonymized_response_id": "r3"})
            manifest.write_text(
                json.dumps(
                    {
                        "input_jsonl": str(root / "seed.jsonl"),
                        "output_dir": str(root / "pilot"),
                        "condition_set": "edf_core",
                        "case_count": 2,
                        "condition_count": 2,
                        "conditions": [
                            {"condition_id": "enhanced_prompt_only_clean"},
                            {"condition_id": "dbox_inspired_guard"},
                        ],
                        "combined_jsonl": str(combined),
                        "review_csv": str(review),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            report = check_ablation_run_integrity.check_run_integrity(manifest)

        self.assertEqual(4, report["expected_row_count"])
        self.assertEqual(4, report["combined_row_count"])
        self.assertEqual(3, report["final_response_row_count"])
        self.assertEqual(3, report["review_row_count"])
        self.assertFalse(report["headline_ready"])
        self.assertIn("empty_final_response_rows", report["blocking_reasons"])
        self.assertEqual(
            [{"case_id": "case_1", "condition_id": "dbox_inspired_guard"}],
            report["empty_final_response_rows"],
        )
        self.assertEqual(
            [{"case_id": "case_1", "condition_id": "dbox_inspired_guard"}],
            report["targeted_rerun_pairs"],
        )
        self.assertEqual(1, len(report["targeted_rerun_commands"]))
        self.assertIn("--condition-id dbox_inspired_guard", report["targeted_rerun_commands"][0])
        self.assertIn("--case-id case_1", report["targeted_rerun_commands"][0])
        self.assertEqual(
            [{"case_id": "case_2", "condition_id": "enhanced_prompt_only_clean", "stage_errors": {"leakage_judge": "timeout"}}],
            report["stage_warning_rows"],
        )

    def test_integrity_report_flags_missing_pairs_and_review_row_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            combined = root / "combined.jsonl"
            review = root / "review.csv"
            manifest = root / "manifest.json"
            combined.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "condition_id": "enhanced_prompt_only_clean",
                        "final_response_text": "ok",
                        "stage_errors": {},
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            with review.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["case_id", "anonymized_response_id"])
                writer.writeheader()
            manifest.write_text(
                json.dumps(
                    {
                        "case_count": 1,
                        "condition_count": 2,
                        "conditions": [
                            {"condition_id": "enhanced_prompt_only_clean"},
                            {"condition_id": "dbox_inspired_guard"},
                        ],
                        "combined_jsonl": str(combined),
                        "review_csv": str(review),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            report = check_ablation_run_integrity.check_run_integrity(manifest)

        self.assertEqual(2, report["expected_row_count"])
        self.assertEqual([{"case_id": "case_1", "condition_id": "dbox_inspired_guard"}], report["missing_pairs"])
        self.assertIn("missing_condition_case_pairs", report["blocking_reasons"])
        self.assertIn("review_row_count_mismatch", report["blocking_reasons"])

    def test_integrity_resolves_manifest_paths_relative_to_cwd_when_available(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = root / "runs" / "pilot"
            run_dir.mkdir(parents=True)
            combined = run_dir / "combined.jsonl"
            review = run_dir / "review.csv"
            manifest = run_dir / "manifest.json"
            combined.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "condition_id": "enhanced_prompt_only_clean",
                        "final_response_text": "ok",
                        "stage_errors": {},
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            with review.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["case_id", "anonymized_response_id"])
                writer.writeheader()
                writer.writerow({"case_id": "case_1", "anonymized_response_id": "r1"})
            manifest.write_text(
                json.dumps(
                    {
                        "case_count": 1,
                        "condition_count": 1,
                        "conditions": [{"condition_id": "enhanced_prompt_only_clean"}],
                        "combined_jsonl": str(combined),
                        "review_csv": str(review),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            report = check_ablation_run_integrity.check_run_integrity(manifest)

        self.assertTrue(report["analysis_ready"])
        self.assertEqual(1, report["combined_row_count"])


if __name__ == "__main__":
    unittest.main()
