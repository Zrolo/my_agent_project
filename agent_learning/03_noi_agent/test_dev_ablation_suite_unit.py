import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import run_dev_ablation_suite


class DevAblationSuiteTests(unittest.TestCase):
    def test_default_conditions_include_prompt_dbox_and_bridge_guard_comparisons(self):
        condition_ids = [condition["condition_id"] for condition in run_dev_ablation_suite.DEFAULT_CONDITIONS]

        self.assertIn("enhanced_prompt_only_clean", condition_ids)
        self.assertIn("dbox_inspired_clean", condition_ids)
        self.assertIn("dbox_inspired_guard", condition_ids)
        self.assertIn("bridge_contract_clean", condition_ids)
        self.assertIn("bridge_contract_guard", condition_ids)
        self.assertIn("bridge_contract_guard_repair", condition_ids)

    def test_run_suite_writes_condition_outputs_combined_summary_and_review_pack(self):
        calls = []

        def fake_run_condition(rows, condition, **kwargs):
            calls.append((condition["condition_id"], len(rows), kwargs["chat_model_provider"]))
            return [
                {
                    "case_id": rows[0]["id"],
                    "tutor_mode": condition["tutor_mode"],
                    "guard_mode": condition.get("guard_mode", "predicted"),
                    "pipeline_mode": condition["pipeline_mode"],
                    "models": {
                        "tutor_mode": condition["tutor_mode"],
                        "pipeline_mode": condition["pipeline_mode"],
                        "tutor_model_provider": kwargs["chat_model_provider"],
                    },
                    "condition_id": condition["condition_id"],
                    "candidate_response_text": f"candidate::{condition['condition_id']}",
                    "final_response_text": f"final::{condition['condition_id']}",
                    "final_response_source": "candidate",
                    "llm_call_count": 1,
                    "latency_ms": {"total_latency_ms": 12.0},
                    "stage_errors": {},
                }
            ]

        def fake_summary(rows):
            return {"case_count": len(rows), "completed_count": len(rows), "groups": {}}

        def fake_write_summary(json_path, md_path, summary, md_zh_path=None):
            json_path.write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")
            md_path.write_text("# Summary\n", encoding="utf-8")
            md_zh_path.write_text("# 摘要\n", encoding="utf-8")

        def fake_export_review(input_jsonl, output_csv, key_csv, shuffle_seed=17, id_salt=""):
            output_csv.write_text("case_id,response_text\ncase_1,hello\n", encoding="utf-8")
            key_csv.write_text("anonymized_response_id,condition_id\nresp_1,x\n", encoding="utf-8")
            return 1

        def fake_export_xlsx(input_csv, output_xlsx):
            output_xlsx.write_text("xlsx placeholder", encoding="utf-8")
            return 1

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            seed = tmp / "seed.jsonl"
            seed.write_text(
                json.dumps({"id": "case_1", "student_message": "状态怎么设？"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            output_dir = tmp / "dev_ablation"
            conditions = [
                {
                    "condition_id": "enhanced_prompt_only_clean",
                    "tutor_mode": "enhanced_prompt_only",
                    "pipeline_mode": "tutor_only_no_diagnosis",
                    "guard_mode": "predicted",
                },
                {
                    "condition_id": "dbox_inspired_guard",
                    "tutor_mode": "dbox_inspired_decomposition_tutor",
                    "pipeline_mode": "tutor_plus_guard",
                    "guard_mode": "predicted",
                },
            ]

            manifest = run_dev_ablation_suite.run_dev_ablation_suite(
                input_jsonl=seed,
                output_dir=output_dir,
                conditions=conditions,
                chat_model_provider="deepseek_flash",
                run_condition_fn=fake_run_condition,
                summarize_fn=fake_summary,
                write_summary_fn=fake_write_summary,
                export_review_fn=fake_export_review,
                export_xlsx_fn=fake_export_xlsx,
                limit=1,
            )

            self.assertEqual(
                [
                    ("enhanced_prompt_only_clean", 1, "deepseek_flash"),
                    ("dbox_inspired_guard", 1, "deepseek_flash"),
                ],
                calls,
            )
            self.assertEqual(2, manifest["combined_row_count"])
            self.assertTrue(Path(manifest["combined_jsonl"]).exists())
            self.assertTrue(Path(manifest["summary_json"]).exists())
            self.assertTrue(Path(manifest["review_csv"]).exists())
            self.assertTrue(Path(manifest["review_xlsx"]).exists())
            combined_rows = [
                json.loads(line)
                for line in Path(manifest["combined_jsonl"]).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(
                ["enhanced_prompt_only_clean", "dbox_inspired_guard"],
                [row["condition_id"] for row in combined_rows],
            )


if __name__ == "__main__":
    unittest.main()
