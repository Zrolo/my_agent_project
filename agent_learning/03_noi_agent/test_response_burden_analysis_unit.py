import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import analyze_response_burden


class ResponseBurdenAnalysisTests(unittest.TestCase):
    def test_classifies_short_choice_as_low_burden(self):
        result = analyze_response_burden.classify_student_response_burden(
            "只看容量 4：正序时会不会用到刚更新过的容量 2？回答“会/不会”就行。"
        )

        self.assertEqual("low", result["student_response_burden"])
        self.assertIn("short_choice", result["burden_reasons"])

    def test_classifies_full_table_or_multistep_request_as_high_burden(self):
        result = analyze_response_burden.classify_student_response_burden(
            "请手动模拟整个过程，依次写出每一步的表格，并总结完整规则。"
        )

        self.assertEqual("high", result["student_response_burden"])
        self.assertIn("multi_step_trace", result["burden_reasons"])

    def test_does_not_treat_negated_full_rule_constraint_as_high_burden(self):
        result = analyze_response_burden.classify_student_response_burden(
            "先不要写完整公式、完整流程或代码。请列出当前步骤需要观察的两个事实。"
        )

        self.assertNotEqual("high", result["student_response_burden"])
        self.assertNotIn("full_rule", result["burden_reasons"])

    def test_build_payload_summarizes_burden_by_condition_and_ready_pass(self):
        rows = [
            {
                "case_id": "case_1",
                "condition_id": "enhanced_prompt_only_clean",
                "response_text": "回答 A/B 就行。",
                "overall_quality_score": 4,
                "would_show_to_student": "yes",
                "leakage_label": "no_leakage",
                "scores": {
                    "bridge_identification": 2,
                    "groundedness": 2,
                    "scaffold_appropriateness": 2,
                    "bridge_leakage_control": 2,
                    "next_step_clarity": 2,
                    "single_focus_coherence": 2,
                },
            },
            {
                "case_id": "case_2",
                "condition_id": "bridge_contract_guard",
                "response_text": "请完整推导整个 check 条件，并写出所有边界更新规则。",
                "overall_quality_score": 2,
                "would_show_to_student": "no",
                "leakage_label": "major_bridge_leakage",
                "scores": {
                    "bridge_identification": 2,
                    "groundedness": 2,
                    "scaffold_appropriateness": 0,
                    "bridge_leakage_control": 0,
                    "next_step_clarity": 1,
                    "single_focus_coherence": 2,
                },
            },
        ]

        annotated = analyze_response_burden.annotate_rows_with_burden(rows)
        payload = analyze_response_burden.build_payload(annotated)

        self.assertEqual(2, payload["row_count"])
        self.assertEqual({"high": 1, "low": 1}, payload["burden_counts"])
        self.assertEqual({"heuristic": 2}, payload["burden_source_counts"])
        self.assertEqual(
            1,
            payload["condition_summary"]["bridge_contract_guard"]["high_count"],
        )
        self.assertEqual({"pass": 1, "fail": 1}, payload["student_ready_by_burden"])
        self.assertEqual(
            {"major_or_answer": 1, "no_leakage": 1},
            payload["leakage_by_burden"],
        )

    def test_manual_review_burden_takes_priority_over_heuristic(self):
        rows = [
            {
                "case_id": "case_1",
                "condition_id": "bridge_contract_clean",
                "coach_student_response_burden": "low",
                "response_text": "请完整推导整个过程，并写出每一步的表格。",
            }
        ]

        annotated = analyze_response_burden.annotate_rows_with_burden(rows)

        self.assertEqual("low", annotated[0]["student_response_burden"])
        self.assertEqual("coach_review", annotated[0]["burden_source"])
        self.assertEqual([], annotated[0]["burden_reasons"])

    def test_main_writes_jsonl_and_reports(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_jsonl = tmp / "labels.jsonl"
            output_jsonl = tmp / "labels_with_burden.jsonl"
            output_json = tmp / "summary.json"
            output_zh = tmp / "report.zh.md"
            output_en = tmp / "report.md"
            input_jsonl.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "condition_id": "dbox_inspired_clean",
                        "response_text": "先选 A/B，然后说一句理由。",
                        "overall_quality_score": 4,
                        "would_show_to_student": "yes",
                        "leakage_label": "no_leakage",
                        "scores": {
                            "bridge_identification": 2,
                            "groundedness": 2,
                            "scaffold_appropriateness": 2,
                            "bridge_leakage_control": 2,
                            "next_step_clarity": 2,
                            "single_focus_coherence": 2,
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            analyze_response_burden.main(
                [
                    "--input-labels-jsonl",
                    str(input_jsonl),
                    "--output-labels-jsonl",
                    str(output_jsonl),
                    "--output-json",
                    str(output_json),
                    "--output-md-zh",
                    str(output_zh),
                    "--output-md",
                    str(output_en),
                ]
            )

            annotated = [
                json.loads(line)
                for line in output_jsonl.read_text(encoding="utf-8").splitlines()
            ]
            summary = json.loads(output_json.read_text(encoding="utf-8"))
            report_en = output_en.read_text(encoding="utf-8")
            report_zh = output_zh.read_text(encoding="utf-8")

            self.assertEqual("low", annotated[0]["student_response_burden"])
            self.assertEqual(1, summary["condition_summary"]["dbox_inspired_clean"]["low_count"])
            self.assertIn("Response Burden", report_en)
            self.assertIn("回复负担", report_zh)


if __name__ == "__main__":
    unittest.main()
