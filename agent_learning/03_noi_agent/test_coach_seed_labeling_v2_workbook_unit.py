import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from evals.aichat import export_coach_seed_labeling_workbook_v2 as workbook_v2


def _option_values(workbook, option_group: str) -> list[str]:
    sheet = workbook["下拉选项"]
    for column in range(1, sheet.max_column + 1):
        if sheet.cell(row=1, column=column).value == option_group:
            return [
                sheet.cell(row=row, column=column).value
                for row in range(2, sheet.max_row + 1)
                if sheet.cell(row=row, column=column).value
            ]
    raise AssertionError(f"Missing option group: {option_group}")


class CoachSeedLabelingV2WorkbookTests(unittest.TestCase):
    def test_export_xlsx_has_v2_columns_and_no_placeholder_ones(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "coach_v2.xlsx"

            row_count = workbook_v2.export_xlsx(
                seed_jsonl=Path("docs/research/bridgebench_cp_seed_v1.jsonl"),
                focus_registry=Path("docs/research/focus_registry_v1.json"),
                output_xlsx=output_path,
            )

            workbook = load_workbook(output_path)

        self.assertEqual(50, row_count)
        self.assertIn("标注表", workbook.sheetnames)
        self.assertIn("标签说明", workbook.sheetnames)
        sheet = workbook["标注表"]
        machine_headers = [cell.value for cell in sheet[2]]

        self.assertIn("turn_type", machine_headers)
        self.assertIn("policy_risk_type", machine_headers)
        self.assertIn("registered_focus_id", machine_headers)
        self.assertIn("student_already_stated_bridge", machine_headers)
        self.assertIn("bridge_specific_forbidden_content", machine_headers)
        self.assertIn("coach_note_tags", machine_headers)
        self.assertIn("coach_free_notes", machine_headers)
        self.assertNotIn("coach_known_focus", machine_headers)
        self.assertNotIn("coach_forbidden_content", machine_headers)
        self.assertNotIn("coach_notes", machine_headers)

        recent_dialogue_col = machine_headers.index("recent_dialogue") + 1
        code_col = machine_headers.index("student_code_excerpt") + 1
        self.assertEqual("N/A", sheet.cell(row=3, column=recent_dialogue_col).value)
        self.assertEqual("N/A", sheet.cell(row=3, column=code_col).value)

        review_status_col = machine_headers.index("review_status") + 1
        self.assertEqual("未标：还没有完成这一行（unlabeled）", sheet.cell(row=3, column=review_status_col).value)

    def test_export_xlsx_uses_chinese_dropdown_labels_and_v21_options(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "coach_v2.xlsx"
            workbook_v2.export_xlsx(
                seed_jsonl=Path("docs/research/bridgebench_cp_seed_v1.jsonl"),
                focus_registry=Path("docs/research/focus_registry_v1.json"),
                output_xlsx=output_path,
            )

            workbook = load_workbook(output_path)

        turn_type_options = _option_values(workbook, "turn_type")
        scaffold_options = _option_values(workbook, "max_scaffold_level")
        policy_risk_options = _option_values(workbook, "policy_risk_type")
        self.assertIn("可诊断学习轮：学生给出具体卡点或尝试，可判断下一步（diagnosable_learning_turn）", turn_type_options)
        self.assertIn("完整代码请求：要求可提交代码或大段代写（complete_code_request）", turn_type_options)
        self.assertIn("关键桥请求：直接索要状态、转移、check、公式、标记规则（critical_bridge_request）", turn_type_options)
        self.assertFalse(any("direct_answer_request" in value for value in turn_type_options))
        self.assertIn("澄清/要证据：只要题面、尝试、代码、错误现象，不给实质解题提示（L0）", scaffold_options)
        self.assertFalse(any("L4_forbidden" in value for value in scaffold_options))
        self.assertIn("完整代码风险：可能代写可提交代码（complete_code_risk）", policy_risk_options)
        self.assertGreaterEqual(len(workbook["标注表"].data_validations.dataValidation), 18)

        state_options = _option_values(workbook, "student_problem_solving_state")
        self.assertIn(
            "方法应用/变式卡住：知道方向、算法或知识点，但不会落到当前题的关键步骤（method_application_gap）",
            state_options,
        )

    def test_export_xlsx_can_limit_trial_workbook_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "coach_v2_20.xlsx"

            row_count = workbook_v2.export_xlsx(
                seed_jsonl=Path("docs/research/bridgebench_cp_seed_v1.jsonl"),
                focus_registry=Path("docs/research/focus_registry_v1.json"),
                output_xlsx=output_path,
                limit=20,
            )

            workbook = load_workbook(output_path)

        sheet = workbook["标注表"]
        self.assertEqual(20, row_count)
        self.assertEqual(22, sheet.max_row)
        self.assertEqual("cp_bridge_001", sheet["A3"].value)
        self.assertEqual("cp_bridge_020", sheet["A22"].value)


if __name__ == "__main__":
    unittest.main()
