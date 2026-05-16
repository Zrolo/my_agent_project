import json
import tempfile
import unittest
from pathlib import Path

from evals.aichat import prepare_llm_grader_calibration_pack as pack


class LlmGraderCalibrationPackTests(unittest.TestCase):
    def test_builds_three_grader_tasks_with_unknown_policy(self):
        rows = [
            {
                "case_id": "case_1",
                "anonymized_response_id": "resp_1",
                "condition_id": "dbox_inspired_guard",
                "problem_statement": "题面",
                "student_message": "状态到底记录什么？",
                "recent_dialogue": "AI: 先说你卡在哪。\n学生: 状态。",
                "context_ai_reply": "先说你卡在哪。",
                "response_text": "先判断一格状态需要保留什么。",
                "success_criteria": "学生能说出当前一格记录的信息。",
                "forbidden_content": "不能直接写完整状态定义。",
                "critical_bridge_boundary": "直接给状态语义即泄露。",
                "acceptable_reveal": "可以问一格要保留什么。",
                "expected_student_next_action": "学生用一句话回答。",
                "overall_quality_score": 4,
                "would_show_to_student": "yes",
                "leakage_label": "no_leakage",
                "bridge_reveal_justification": "no_reveal",
                "student_response_burden": "low",
                "scores": {"scaffold_sufficiency": 2},
            }
        ]

        tasks = pack.build_calibration_tasks(rows)

        self.assertEqual(3, len(tasks))
        grader_types = {task["grader_type"] for task in tasks}
        self.assertEqual(set(pack.GRADER_TYPES), grader_types)
        case_specific = next(
            task
            for task in tasks
            if task["grader_type"] == "case_specific_bridge_rubric_judge"
        )
        self.assertTrue(case_specific["case_specific_rubric_present"])
        self.assertIn("UNKNOWN / INSUFFICIENT_CONTEXT", case_specific["prompt"])
        self.assertIn("Critical bridge boundary", case_specific["prompt"])
        self.assertIn("直接给状态语义即泄露", case_specific["prompt"])
        self.assertEqual("no_leakage", case_specific["coach_reference"]["leakage_label"])

    def test_main_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            labels = tmp / "labels.jsonl"
            output = tmp / "calibration.jsonl"
            labels.write_text(
                json.dumps(
                    {
                        "case_id": "case_1",
                        "anonymized_response_id": "resp_1",
                        "response_text": "先观察。",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            exit_code = pack.main(
                ["--labels-jsonl", str(labels), "--output-jsonl", str(output), "--limit", "1"]
            )

            self.assertEqual(0, exit_code)
            self.assertEqual(3, len(output.read_text(encoding="utf-8").splitlines()))


if __name__ == "__main__":
    unittest.main()
