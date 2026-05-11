import csv
import json
import tempfile
import unittest
from pathlib import Path

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
        self.assertIn("关键桥梁泄露", zh)
        self.assertIn("Repair Before/After Blind Review Analysis", en)
        self.assertIn("repaired wins", en)


if __name__ == "__main__":
    unittest.main()
