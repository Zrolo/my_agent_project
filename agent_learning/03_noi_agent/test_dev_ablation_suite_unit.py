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
        self.assertNotIn("bridge_contract_safe_scaffold", condition_ids)

    def test_edf_core_condition_set_contains_only_core_edf_comparisons(self):
        conditions = run_dev_ablation_suite.build_conditions(condition_set="edf_core")
        condition_ids = [condition["condition_id"] for condition in conditions]

        self.assertEqual(
            [
                "enhanced_prompt_only_clean",
                "dbox_inspired_guard",
                "edf_inspired_clean",
                "edf_inspired_guard",
                "bridge_contract_guard",
                "bridge_contract_guard_repair",
            ],
            condition_ids,
        )
        edf_condition = next(condition for condition in conditions if condition["condition_id"] == "edf_inspired_clean")
        self.assertEqual("edf_inspired_adaptive_scaffolding_tutor", edf_condition["tutor_mode"])
        self.assertEqual("tutor_only_no_diagnosis", edf_condition["pipeline_mode"])

    def test_prompt_compression_condition_set_compares_long_compact_minimal_and_dbox(self):
        conditions = run_dev_ablation_suite.build_conditions(condition_set="prompt_compression")
        condition_ids = [condition["condition_id"] for condition in conditions]

        self.assertEqual(
            [
                "dbox_inspired_guard",
                "bridge_contract_guard",
                "bridge_contract_compact_guard",
                "bridge_contract_minimal_guard",
            ],
            condition_ids,
        )
        compact = next(condition for condition in conditions if condition["condition_id"] == "bridge_contract_compact_guard")
        minimal = next(condition for condition in conditions if condition["condition_id"] == "bridge_contract_minimal_guard")
        self.assertEqual("bridge_contract_compact", compact["tutor_mode"])
        self.assertEqual("bridge_contract_minimal", minimal["tutor_mode"])
        self.assertEqual("tutor_plus_guard", compact["pipeline_mode"])
        self.assertEqual("tutor_plus_guard", minimal["pipeline_mode"])

    def test_dbox_bridge_hybrid_condition_set_compares_clean_guard_and_hybrid(self):
        conditions = run_dev_ablation_suite.build_conditions(condition_set="dbox_bridge_hybrid")
        condition_ids = [condition["condition_id"] for condition in conditions]

        self.assertEqual(
            [
                "enhanced_prompt_only_clean",
                "dbox_inspired_clean",
                "dbox_inspired_guard",
                "bridge_contract_compact_guard",
                "bridge_guided_dbox_style_guard",
            ],
            condition_ids,
        )
        hybrid = next(
            condition for condition in conditions if condition["condition_id"] == "bridge_guided_dbox_style_guard"
        )
        self.assertEqual("bridge_guided_dbox_style_tutor", hybrid["tutor_mode"])
        self.assertEqual("tutor_plus_guard", hybrid["pipeline_mode"])

    def test_guard_repair_fairness_addon_contains_missing_clean_guard_repair_controls(self):
        conditions = run_dev_ablation_suite.build_conditions(condition_set="guard_repair_fairness_addon")
        condition_ids = [condition["condition_id"] for condition in conditions]

        self.assertEqual(
            [
                "enhanced_prompt_only_guard",
                "enhanced_prompt_only_guard_repair",
                "dbox_inspired_guard_repair",
                "bridge_contract_compact_clean",
                "bridge_contract_compact_guard_repair",
            ],
            condition_ids,
        )
        bridge_clean = next(
            condition for condition in conditions if condition["condition_id"] == "bridge_contract_compact_clean"
        )
        bridge_repair = next(
            condition for condition in conditions if condition["condition_id"] == "bridge_contract_compact_guard_repair"
        )
        dbox_repair = next(
            condition for condition in conditions if condition["condition_id"] == "dbox_inspired_guard_repair"
        )
        self.assertEqual("bridge_contract_compact", bridge_clean["tutor_mode"])
        self.assertEqual("tutor_only", bridge_clean["pipeline_mode"])
        self.assertEqual("bridge_contract_compact", bridge_repair["tutor_mode"])
        self.assertEqual("tutor_plus_guard_plus_repair", bridge_repair["pipeline_mode"])
        self.assertEqual("dbox_inspired_decomposition_tutor", dbox_repair["tutor_mode"])
        self.assertEqual("tutor_plus_guard_plus_repair", dbox_repair["pipeline_mode"])

    def test_include_safe_scaffold_adds_appendix_condition_without_changing_defaults(self):
        condition_ids = [
            condition["condition_id"]
            for condition in run_dev_ablation_suite.build_default_conditions(include_safe_scaffold=True)
        ]

        self.assertIn("bridge_contract_safe_scaffold", condition_ids)
        safe_condition = next(
            condition for condition in condition_ids if condition == "bridge_contract_safe_scaffold"
        )
        self.assertEqual("bridge_contract_safe_scaffold", safe_condition)
        matching_conditions = [
            condition
            for condition in run_dev_ablation_suite.build_default_conditions(include_safe_scaffold=True)
            if condition["condition_id"] == "bridge_contract_safe_scaffold"
        ]
        self.assertEqual(
            [
                {
                    "condition_id": "bridge_contract_safe_scaffold",
                    "tutor_mode": "bridge_contract",
                    "pipeline_mode": "deterministic_safe_scaffold",
                    "guard_mode": "predicted",
                }
            ],
            matching_conditions,
        )

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
                condition_set="custom",
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

    def test_run_suite_can_select_edf_core_condition_set(self):
        calls = []

        def fake_run_condition(rows, condition, **kwargs):
            calls.append(condition["condition_id"])
            return [
                {
                    "case_id": rows[0]["id"],
                    "tutor_mode": condition["tutor_mode"],
                    "guard_mode": condition.get("guard_mode", "predicted"),
                    "pipeline_mode": condition["pipeline_mode"],
                    "models": {"tutor_model_provider": kwargs["chat_model_provider"]},
                    "candidate_response_text": "candidate",
                    "final_response_text": "final",
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
            key_csv.write_text("anonymized_response_id,tutor_mode\nresp_1,x\n", encoding="utf-8")
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
            manifest = run_dev_ablation_suite.run_dev_ablation_suite(
                input_jsonl=seed,
                output_dir=tmp / "dev_ablation",
                condition_set="edf_core",
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
                "enhanced_prompt_only_clean",
                "dbox_inspired_guard",
                "edf_inspired_clean",
                "edf_inspired_guard",
                "bridge_contract_guard",
                "bridge_contract_guard_repair",
            ],
            calls,
        )
        self.assertEqual("edf_core", manifest["condition_set"])

    def test_heldout_main_condition_set_matches_freeze_decision_main_table(self):
        conditions = run_dev_ablation_suite.build_conditions(condition_set="heldout_main")
        condition_ids = [condition["condition_id"] for condition in conditions]

        self.assertEqual(
            [
                "current_system_deployment",
                "enhanced_prompt_only_clean",
                "codehelp_codeaid_clean",
                "dbox_inspired_guard",
                "bridge_inspired_expert_decision_clean",
                "single_llm_structured_guard",
                "bridge_contract_guard",
                "bridge_contract_guard_repair",
            ],
            condition_ids,
        )
        current = conditions[0]
        self.assertEqual("current_system", current["tutor_mode"])
        self.assertEqual("tutor_only_no_diagnosis", current["pipeline_mode"])
        bridge_repair = conditions[-1]
        self.assertEqual("bridge_contract", bridge_repair["tutor_mode"])
        self.assertEqual("tutor_plus_guard_plus_repair", bridge_repair["pipeline_mode"])

    def test_dialogue_state_v3_main_condition_set_matches_reviewed_candidate_freeze_gate(self):
        conditions = run_dev_ablation_suite.build_conditions(condition_set="dialogue_state_v3_main")
        condition_ids = [condition["condition_id"] for condition in conditions]

        self.assertEqual(
            [
                "enhanced_prompt_only_clean",
                "codehelp_codeaid_clean",
                "dbox_inspired_clean",
                "dbox_inspired_guard",
                "bridge_guided_dbox_style_guard",
                "bridge_contract_compact_guard",
                "bridge_contract_compact_guard_repair",
            ],
            condition_ids,
        )
        hybrid = conditions[4]
        self.assertEqual("bridge_guided_dbox_style_tutor", hybrid["tutor_mode"])
        self.assertEqual("tutor_plus_guard", hybrid["pipeline_mode"])
        compact_repair = conditions[-1]
        self.assertEqual("bridge_contract_compact", compact_repair["tutor_mode"])
        self.assertEqual("tutor_plus_guard_plus_repair", compact_repair["pipeline_mode"])

    def test_cli_accepts_dialogue_state_v3_main_condition_set(self):
        args = run_dev_ablation_suite._parse_args(["--condition-set", "dialogue_state_v3_main"])

        self.assertEqual("dialogue_state_v3_main", args.condition_set)

    def test_dialogue_state_v3_repair_fairness_addon_contains_only_dbox_repair(self):
        conditions = run_dev_ablation_suite.build_conditions(
            condition_set="dialogue_state_v3_repair_fairness_addon"
        )

        self.assertEqual(
            [
                {
                    "condition_id": "dbox_inspired_guard_repair",
                    "tutor_mode": "dbox_inspired_decomposition_tutor",
                    "pipeline_mode": "tutor_plus_guard_plus_repair",
                    "guard_mode": "predicted",
                }
            ],
            conditions,
        )

    def test_cli_accepts_dialogue_state_v3_repair_fairness_addon_condition_set(self):
        args = run_dev_ablation_suite._parse_args(
            ["--condition-set", "dialogue_state_v3_repair_fairness_addon"]
        )

        self.assertEqual("dialogue_state_v3_repair_fairness_addon", args.condition_set)

    def test_run_suite_can_filter_case_ids_and_condition_ids_for_targeted_rerun(self):
        calls = []

        def fake_run_condition(rows, condition, **kwargs):
            calls.append((condition["condition_id"], [row["id"] for row in rows]))
            return [
                {
                    "case_id": row["id"],
                    "tutor_mode": condition["tutor_mode"],
                    "guard_mode": condition.get("guard_mode", "predicted"),
                    "pipeline_mode": condition["pipeline_mode"],
                    "models": {"tutor_model_provider": kwargs["chat_model_provider"]},
                    "candidate_response_text": f"candidate::{row['id']}",
                    "final_response_text": f"final::{row['id']}",
                    "final_response_source": "candidate",
                    "llm_call_count": 1,
                    "latency_ms": {"total_latency_ms": 12.0},
                    "stage_errors": {},
                }
                for row in rows
            ]

        def fake_summary(rows):
            return {"case_count": len(rows), "completed_count": len(rows), "groups": {}}

        def fake_write_summary(json_path, md_path, summary, md_zh_path=None):
            json_path.write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")
            md_path.write_text("# Summary\n", encoding="utf-8")
            md_zh_path.write_text("# 摘要\n", encoding="utf-8")

        def fake_export_review(input_jsonl, output_csv, key_csv, shuffle_seed=17, id_salt=""):
            output_csv.write_text("case_id,response_text\ncase_b,hello\n", encoding="utf-8")
            key_csv.write_text("anonymized_response_id,tutor_mode\nresp_1,x\n", encoding="utf-8")
            return 1

        def fake_export_xlsx(input_csv, output_xlsx):
            output_xlsx.write_text("xlsx placeholder", encoding="utf-8")
            return 1

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            seed = tmp / "seed.jsonl"
            seed.write_text(
                "\n".join(
                    [
                        json.dumps({"id": "case_a", "student_message": "A"}, ensure_ascii=False),
                        json.dumps({"id": "case_b", "student_message": "B"}, ensure_ascii=False),
                        json.dumps({"id": "case_c", "student_message": "C"}, ensure_ascii=False),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            manifest = run_dev_ablation_suite.run_dev_ablation_suite(
                input_jsonl=seed,
                output_dir=tmp / "targeted_rerun",
                condition_set="edf_core",
                case_ids=["case_b"],
                condition_ids=["dbox_inspired_guard"],
                chat_model_provider="deepseek_flash",
                run_condition_fn=fake_run_condition,
                summarize_fn=fake_summary,
                write_summary_fn=fake_write_summary,
                export_review_fn=fake_export_review,
                export_xlsx_fn=fake_export_xlsx,
            )

        self.assertEqual([("dbox_inspired_guard", ["case_b"])], calls)
        self.assertEqual(1, manifest["case_count"])
        self.assertEqual(1, manifest["condition_count"])
        self.assertEqual(["case_b"], manifest["selected_case_ids"])
        self.assertEqual(["dbox_inspired_guard"], manifest["selected_condition_ids"])
        self.assertEqual(1, manifest["combined_row_count"])

    def test_run_suite_rejects_unknown_targeted_filters(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            seed = tmp / "seed.jsonl"
            seed.write_text(
                json.dumps({"id": "case_a", "student_message": "A"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Unknown case_id"):
                run_dev_ablation_suite.run_dev_ablation_suite(
                    input_jsonl=seed,
                    output_dir=tmp / "bad_case",
                    condition_set="edf_core",
                    case_ids=["missing_case"],
                )

            with self.assertRaisesRegex(ValueError, "Unknown condition_id"):
                run_dev_ablation_suite.run_dev_ablation_suite(
                    input_jsonl=seed,
                    output_dir=tmp / "bad_condition",
                    condition_set="edf_core",
                    condition_ids=["missing_condition"],
                )


if __name__ == "__main__":
    unittest.main()
