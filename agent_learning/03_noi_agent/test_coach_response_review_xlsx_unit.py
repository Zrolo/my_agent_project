import csv
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from evals.aichat import export_coach_response_review_workbook_xlsx as xlsx_export


class CoachResponseReviewXlsxTests(unittest.TestCase):
    def test_export_xlsx_uses_chinese_headers_and_dropdown_options(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_csv = Path(tmpdir) / "review.csv"
            output_xlsx = Path(tmpdir) / "review.zh.xlsx"
            with input_csv.open("w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=xlsx_export.REVIEW_COLUMNS, lineterminator="\n")
                writer.writeheader()
                writer.writerow(
                    {
                        "case_id": "case_1",
                        "anonymized_response_id": "resp_001",
                        "problem_ref": "P1048",
                        "student_message": "我不知道状态怎么设。",
                        "problem_context": "采药。",
                        "recent_dialogue": "",
                        "response_text": "先想一格 dp 应该存什么。",
                        "review_status": "unlabeled",
                    }
                )

            row_count = xlsx_export.export_xlsx(input_csv=input_csv, output_xlsx=output_xlsx)
            workbook = load_workbook(output_xlsx)

        self.assertEqual(1, row_count)
        self.assertIn("盲评表", workbook.sheetnames)
        self.assertIn("评分说明", workbook.sheetnames)
        self.assertIn("下拉选项", workbook.sheetnames)
        sheet = workbook["盲评表"]
        self.assertEqual("学生当前问题", sheet["D1"].value)
        self.assertEqual("AI 回复（要评分）", sheet["G1"].value)
        self.assertEqual("是否抓住卡点 0-2", sheet["H1"].value)
        self.assertEqual("coach_bridge_identification_score", sheet["H2"].value)
        self.assertEqual("case_1", sheet["A3"].value)
        self.assertEqual("桥梁导向微型例子 0-2", sheet["N1"].value)
        self.assertEqual("coach_bridge_oriented_micro_example_score", sheet["N2"].value)
        self.assertEqual("unlabeled", sheet["R3"].value)
        self.assertTrue(sheet.freeze_panes)
        self.assertGreaterEqual(len(sheet.data_validations.dataValidation), 10)
        options = workbook["下拉选项"]
        self.assertEqual("2｜好：直接针对学生当前缺失的桥梁/卡点", options["A2"].value)
        self.assertEqual("2｜好：例子能引导学生抽象可迁移的桥梁关系", options["G2"].value)
        self.assertEqual("no_leakage｜无泄露：没有说穿当前关键桥", options["H2"].value)
        guide = workbook["评分说明"]
        self.assertIn("0-2", guide["A1"].value)


if __name__ == "__main__":
    unittest.main()
