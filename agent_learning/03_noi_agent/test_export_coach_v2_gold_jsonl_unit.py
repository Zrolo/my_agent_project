import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from evals.aichat import export_coach_v2_gold_jsonl as exporter
from evals.aichat.coach_labeling_schema_v2 import option_label


class ExportCoachV2GoldJsonlTests(unittest.TestCase):
    def test_build_gold_row_extracts_machine_ids_from_chinese_labels(self):
        row = {
            "case_id": "cp_bridge_001",
            "student_message": "我知道要 LCA，但不知道每条路径到底在哪里加减标记。",
            "problem_context": "树上多条路径统计每个点经过次数。",
            "turn_type": option_label("critical_bridge_request"),
            "diagnosis_uncertainty": option_label("low"),
            "student_problem_solving_state": option_label("method_application_gap"),
            "student_attempt_level": option_label("partial_attempt"),
            "student_already_knows": "LCA",
            "student_already_stated_bridge": option_label("not_stated"),
            "policy_risk_type": option_label("critical_bridge_completion_risk"),
            "primary_bridge_family": option_label("aggregation_contribution_bridge"),
            "primary_bridge_subtype_id": option_label("aggregation.tree_path_difference_marking"),
            "registered_focus_id": "tree_path_difference",
            "focus_match_status": option_label("matched_existing"),
            "help_seeking_type": f"{option_label('strategy_hint_request')};{option_label('concept_explanation')}",
            "max_scaffold_level": option_label("L2"),
            "help_forms": f"{option_label('micro_example')};{option_label('guiding_question')}",
            "general_forbidden_content": option_label("no_full_solution"),
            "bridge_specific_forbidden_content": option_label("no_exact_contribution_formula"),
            "leakage_risk": option_label("high"),
            "evidence_quote": "“不知道每条路径到底在哪里加减标记”",
            "coach_confidence": "5",
            "review_status": option_label("labeled"),
        }

        gold = exporter.build_gold_row(row)

        self.assertEqual("cp_bridge_001", gold["case_id"])
        self.assertEqual("critical_bridge_request", gold["turn_type"])
        self.assertEqual("method_application_gap", gold["student_problem_solving_state"])
        self.assertEqual("aggregation_contribution_bridge", gold["primary_bridge_family"])
        self.assertEqual("aggregation.tree_path_difference_marking", gold["primary_bridge_subtype_id"])
        self.assertEqual("tree_path_difference", gold["registered_focus_id"])
        self.assertEqual(["strategy_hint_request", "concept_explanation"], gold["help_seeking_type"])
        self.assertEqual(["micro_example", "guiding_question"], gold["help_forms"])
        self.assertEqual("L2", gold["max_scaffold_level"])
        self.assertEqual("single_coach_reference", gold["label_reference_type"])
        self.assertEqual("raw", gold["label_adjudication_status"])
        self.assertFalse(gold["is_adjudicated_gold"])

    def test_export_workbook_to_jsonl_writes_only_labeled_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workbook_path = Path(tmpdir) / "labels.xlsx"
            output_path = Path(tmpdir) / "gold.jsonl"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "标注表"
            headers = [
                "case_id",
                "student_message",
                "turn_type",
                "primary_bridge_family",
                "primary_bridge_subtype_id",
                "registered_focus_id",
                "review_status",
                "evidence_quote",
            ]
            sheet.append([""] * len(headers))
            sheet.append(headers)
            sheet.append(
                [
                    "case_labeled",
                    "状态怎么设？",
                    option_label("critical_bridge_request"),
                    option_label("representation_state_bridge"),
                    option_label("state.dp_state_semantics"),
                    "state_design",
                    option_label("labeled"),
                    "状态怎么设",
                ]
            )
            sheet.append(
                [
                    "case_unlabeled",
                    "不会",
                    "",
                    "",
                    "",
                    "",
                    option_label("unlabeled"),
                    "",
                ]
            )
            workbook.save(workbook_path)

            count = exporter.export_workbook_to_jsonl(workbook_path, output_path)
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(1, count)
        self.assertEqual("case_labeled", rows[0]["case_id"])
        self.assertEqual("representation_state_bridge", rows[0]["primary_bridge_family"])


if __name__ == "__main__":
    unittest.main()
