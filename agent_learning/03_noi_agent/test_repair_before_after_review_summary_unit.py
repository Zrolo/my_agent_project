import csv
import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from evals.aichat import summarize_repair_before_after_review as summary


class RepairBeforeAfterReviewSummaryTests(unittest.TestCase):
    def _write_csv(self, path: Path, rows: list[dict]) -> None:
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_summarize_pairs_candidate_and_repaired_labels(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            workbook = tmp / "review.csv"
            key = tmp / "review.key.csv"
            labels = tmp / "labels.jsonl"
            self._write_csv(
                workbook,
                [
                    {
                        "case_id": "case_dp",
                        "anonymized_response_id": "resp_before",
                        "student_message": "dp 每格表示什么？",
                        "response_text": "dp[t] 表示最大价值。",
                    },
                    {
                        "case_id": "case_dp",
                        "anonymized_response_id": "resp_after",
                        "student_message": "dp 每格表示什么？",
                        "response_text": "先看 t=0/3/5 时格子该记录什么。",
                    },
                ],
            )
            self._write_csv(
                key,
                [
                    {
                        "anonymized_response_id": "resp_before",
                        "case_id": "case_dp",
                        "final_response_source": "candidate_before_repair",
                        "repair_applied": "false",
                    },
                    {
                        "anonymized_response_id": "resp_after",
                        "case_id": "case_dp",
                        "final_response_source": "repaired_final_response",
                        "repair_applied": "true",
                    },
                ],
            )
            labels.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "anonymized_response_id": "resp_before",
                                "case_id": "case_dp",
                                "overall_quality": "bad",
                                "leakage_label": "major_bridge_leakage",
                                "notes": "直接说出状态定义。",
                                "review_status": "labeled",
                            },
                            ensure_ascii=False,
                        ),
                        json.dumps(
                            {
                                "anonymized_response_id": "resp_after",
                                "case_id": "case_dp",
                                "overall_quality": "good",
                                "leakage_label": "no_leakage",
                                "notes": "让学生自己抽象状态含义。",
                                "review_status": "labeled",
                            },
                            ensure_ascii=False,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = summary.summarize(
                workbook_csv=workbook,
                key_csv=key,
                labels_path=labels,
            )

        self.assertEqual(1, result["pair_count"])
        self.assertEqual(1, result["quality"]["repaired_wins"])
        self.assertEqual(1, result["leakage"]["repaired_improves"])
        self.assertEqual(2.0, result["quality"]["average_delta"])
        self.assertEqual(-2.0, result["leakage"]["average_severity_delta"])
        self.assertEqual("case_dp", result["pairs"][0]["case_id"])

    def test_reports_have_chinese_and_english_research_language(self):
        result = {
            "pair_count": 1,
            "labeled_pair_count": 1,
            "quality": {"repaired_wins": 1, "ties": 0, "repaired_losses": 0, "average_delta": 1.0},
            "leakage": {
                "repaired_improves": 1,
                "ties": 0,
                "repaired_worse": 0,
                "average_severity_delta": -2.0,
                "candidate_major_or_answer_rate": 1.0,
                "repaired_major_or_answer_rate": 0.0,
            },
            "student_ready": {"repaired_improves": 1, "ties": 0, "repaired_worse": 0},
            "pairs": [
                {
                    "case_id": "case_dp",
                    "candidate": {
                        "overall_quality": "bad",
                        "leakage_label": "major_bridge_leakage",
                        "notes": "直接说出状态定义。",
                    },
                    "repaired": {
                        "overall_quality": "good",
                        "leakage_label": "no_leakage",
                        "notes": "让学生自己抽象状态含义。",
                    },
                    "quality_delta": 2,
                    "leakage_severity_delta": -2,
                }
            ],
        }

        zh = summary.render_markdown_zh(result)
        en = summary.render_markdown(result)

        self.assertIn("Repair 前后对照盲评分析", zh)
        self.assertIn("修复后更好", zh)
        self.assertIn("修复后更愿意给学生看", zh)
        self.assertIn("关键桥梁泄露", zh)
        self.assertIn("Repair Before/After Blind Review Analysis", en)
        self.assertIn("repaired wins", en)
        self.assertIn("student-ready improves after repair", en)

    def test_summarize_reads_new_review_workbook_fields_without_labels_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            workbook = tmp / "review.csv"
            key = tmp / "review.key.csv"
            labels = tmp / "missing_labels.jsonl"
            self._write_csv(
                workbook,
                [
                    {
                        "case_id": "repair_stress_004",
                        "anonymized_response_id": "resp_before",
                        "response_text": "端点各加 1，LCA 减 2。",
                        "coach_overall_quality_score": "1｜不可用：不建议给学生看",
                        "coach_leakage_label": "major_bridge_leakage｜严重桥梁泄露：直接补完当前关键桥",
                        "coach_would_show_to_student": "no｜不愿意：不应给学生看",
                        "coach_notes": "直接说穿标记规则。",
                        "review_status": "labeled｜已评完",
                    },
                    {
                        "case_id": "repair_stress_004",
                        "anonymized_response_id": "resp_after",
                        "response_text": "你先画路径，判断端点和汇合点各自该抵消什么。",
                        "coach_overall_quality_score": "4｜较好：可以给学生看，只有小问题",
                        "coach_leakage_label": "minor_bridge_leakage｜轻微桥梁泄露：提示偏强但学生仍要推理",
                        "coach_would_show_to_student": "yes｜愿意：可以直接给学生看",
                        "coach_notes": "仍有一点强，但保留了推理空间。",
                        "review_status": "labeled｜已评完",
                    },
                ],
            )
            self._write_csv(
                key,
                [
                    {
                        "anonymized_response_id": "resp_before",
                        "case_id": "repair_stress_004",
                        "final_response_source": "candidate_before_repair",
                        "repair_applied": "false",
                    },
                    {
                        "anonymized_response_id": "resp_after",
                        "case_id": "repair_stress_004",
                        "final_response_source": "repair",
                        "repair_applied": "true",
                    },
                ],
            )

            result = summary.summarize(workbook_csv=workbook, key_csv=key, labels_path=labels)

        self.assertEqual(1, result["pair_count"])
        self.assertEqual(1, result["labeled_pair_count"])
        self.assertEqual(1, result["quality"]["repaired_wins"])
        self.assertEqual(3.0, result["quality"]["average_delta"])
        self.assertEqual(1, result["leakage"]["repaired_improves"])
        self.assertEqual(-1.0, result["leakage"]["average_severity_delta"])
        self.assertEqual(1, result["student_ready"]["repaired_improves"])

    def test_loads_filled_xlsx_workbook_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "review.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "盲评表"
            sheet.append(["匿名回复编号", "总体质量 1-5"])
            sheet.append(["anonymized_response_id", "coach_overall_quality_score"])
            sheet.append(["resp_x", "5｜优秀：非常愿意给学生看"])
            workbook.save(path)

            rows = summary.load_review_rows(path)

        self.assertEqual("resp_x", rows[0]["anonymized_response_id"])
        self.assertEqual("5｜优秀：非常愿意给学生看", rows[0]["coach_overall_quality_score"])


if __name__ == "__main__":
    unittest.main()
