import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import export_coach_seed_labeling_workbook as workbook


class CoachSeedLabelingWorkbookTests(unittest.TestCase):
    def test_build_workbook_rows_defaults_to_blind_coach_fields_without_seed_gold(self):
        rows = [
            {
                "id": "case_1",
                "problem_ref": "P1048",
                "topic": "state_design",
                "student_message": "我不知道 dp 数组每一格表示什么。",
                "problem_context": "采药。",
                "gold_student_state": "problem_representation_unclear",
                "gold_bridge_family": "representation_bridge",
                "gold_known_focus": "state_design",
                "gold_help_seeking_type": "instrumental_help",
                "gold_missing_link": "状态格子含义缺失。",
                "gold_allowed_help_level": "L2",
                "gold_forbidden_completion": "不能直接给完整 dp 定义。",
                "needs_new_focus": False,
            }
        ]

        exported = workbook.build_workbook_rows(rows)

        self.assertEqual(1, len(exported))
        row = exported[0]
        self.assertEqual("case_1", row["case_id"])
        self.assertNotIn("seed_gold_known_focus", row)
        self.assertNotIn("seed_gold_bridge_family", row)
        self.assertEqual("", row["coach_bridge_family"])
        self.assertEqual("", row["coach_known_focus"])
        self.assertEqual("", row["coach_forbidden_content"])
        self.assertEqual("unlabeled", row["review_status"])

    def test_build_workbook_rows_can_include_seed_gold_for_internal_review(self):
        rows = [
            {
                "id": "case_1",
                "student_message": "线段树 lazy 是什么？",
                "gold_bridge_family": "representation_bridge",
                "gold_known_focus": "lazy_semantics",
            }
        ]

        exported = workbook.build_workbook_rows(rows, include_seed_gold=True)

        self.assertEqual("lazy_semantics", exported[0]["seed_gold_known_focus"])
        self.assertEqual("representation_bridge", exported[0]["seed_gold_bridge_family"])
        self.assertEqual("", exported[0]["coach_known_focus"])

    def test_build_workbook_rows_can_prefill_coach_fields_for_review_mode(self):
        rows = [
            {
                "id": "case_1",
                "student_message": "check 怎么写？",
                "gold_student_state": "strategy_application_gap",
                "gold_bridge_family": "predicate_bridge",
                "gold_known_focus": "check_condition",
                "gold_help_seeking_type": "instrumental_help",
                "gold_missing_link": "mid 到可行性判断的映射缺失。",
                "gold_allowed_help_level": "L2",
                "gold_forbidden_completion": "不能直接给完整 check。",
                "needs_new_focus": False,
            }
        ]

        exported = workbook.build_workbook_rows(rows, prefill_coach=True)

        row = exported[0]
        self.assertEqual("check_condition", row["seed_gold_known_focus"])
        self.assertEqual("predicate_bridge", row["coach_bridge_family"])
        self.assertEqual("check_condition", row["coach_known_focus"])
        self.assertEqual("mid 到可行性判断的映射缺失。", row["coach_missing_bridge_description"])
        self.assertEqual("L2", row["coach_allowed_help_level"])
        self.assertEqual("review_seed_gold", row["review_status"])

    def test_write_csv_preserves_chinese_text_and_blind_header_order(self):
        rows = workbook.build_workbook_rows(
            [
                {
                    "id": "case_1",
                    "student_message": "线段树 lazy 是什么？",
                    "gold_bridge_family": "representation_bridge",
                    "gold_known_focus": "lazy_semantics",
                }
            ]
        )
        output = io.StringIO()

        workbook.write_workbook_csv(output, rows)

        output.seek(0)
        reader = csv.DictReader(output)
        loaded = list(reader)
        self.assertEqual(workbook.BLIND_WORKBOOK_COLUMNS, reader.fieldnames)
        self.assertEqual("线段树 lazy 是什么？", loaded[0]["student_message"])
        self.assertNotIn("seed_gold_known_focus", loaded[0])

    def test_write_csv_can_emit_review_header_with_seed_gold(self):
        rows = workbook.build_workbook_rows(
            [
                {
                    "id": "case_1",
                    "student_message": "线段树 lazy 是什么？",
                    "gold_known_focus": "lazy_semantics",
                }
            ],
            include_seed_gold=True,
        )
        output = io.StringIO()

        workbook.write_workbook_csv(output, rows, include_seed_gold=True)

        output.seek(0)
        reader = csv.DictReader(output)
        loaded = list(reader)
        self.assertEqual(workbook.REVIEW_WORKBOOK_COLUMNS, reader.fieldnames)
        self.assertEqual("lazy_semantics", loaded[0]["seed_gold_known_focus"])

    def test_main_writes_csv_from_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "seed.jsonl"
            output_path = Path(tmpdir) / "workbook.csv"
            input_path.write_text(
                json.dumps({"id": "case_1", "student_message": "不会"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            exit_code = workbook.main(
                [
                    "--input-jsonl",
                    str(input_path),
                    "--output-csv",
                    str(output_path),
                ]
            )

            self.assertEqual(0, exit_code)
            content = output_path.read_text(encoding="utf-8-sig")
            self.assertIn("case_id", content)
            self.assertIn("case_1", content)


if __name__ == "__main__":
    unittest.main()
