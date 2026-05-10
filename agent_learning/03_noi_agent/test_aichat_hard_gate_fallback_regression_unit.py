import os
import unittest
from unittest.mock import patch

from noi_agent import analyze_student_turn, enforce_level_gate, _detect_risks, _is_only_restating


def _message_with_problem_context(student_message: str, problem_context: str) -> list[dict]:
    return [
        {
            "role": "user",
            "content": "\n".join(
                [
                    "[学生原始问题]",
                    student_message,
                    "",
                    "[当前题目上下文：只用于离线研究诊断，不要直接照抄题解]",
                    f"题面/题意/约束: {problem_context}",
                    "",
                    "请围绕学生当前卡点生成或评估渐进脚手架。",
                ]
            ),
        }
    ]


class AIChatHardGateFallbackRegressionTests(unittest.TestCase):
    def test_paired_contrast_question_is_not_multi_question(self):
        messages = _message_with_problem_context(
            "01 背包为什么容量要倒着枚举？正着枚举不是也能更新吗？",
            "每个物品只能选一次。",
        )

        risks = _detect_risks(messages[-1]["content"], messages)

        self.assertNotIn("multi_question", risks)

    def test_paired_contrast_question_keeps_l2_scaffold_available(self):
        messages = _message_with_problem_context(
            "01 背包为什么容量要倒着枚举？正着枚举不是也能更新吗？",
            "每个物品只能选一次。",
        )

        with patch.dict(os.environ, {"NOI_JUDGE_V2_ENABLED": "0"}, clear=False):
            result = analyze_student_turn(messages[-1]["content"], messages, pedagogical_judgement=None)

        self.assertEqual("L2", result["level_control"]["max_level"])
        self.assertNotEqual("multi_question", result["risk_control"]["highest_risk"])

    def test_student_knows_algorithm_but_not_mapping_is_not_only_restating(self):
        text = "题目说合并两个集合，我知道可能是并查集，但不知道这个操作在代码里对应哪一步。"

        self.assertFalse(_is_only_restating(text))

    def test_student_knows_algorithm_but_not_mapping_keeps_l2_scaffold_available(self):
        messages = _message_with_problem_context(
            "题目说合并两个集合，我知道可能是并查集，但不知道这个操作在代码里对应哪一步。",
            "动态维护若干集合的合并与查询。",
        )

        with patch.dict(os.environ, {"NOI_JUDGE_V2_ENABLED": "0"}, clear=False):
            result = analyze_student_turn(messages[-1]["content"], messages, pedagogical_judgement=None)

        self.assertEqual("L2", result["level_control"]["max_level"])

    def test_l1_hard_gate_fallback_does_not_default_to_problem_ref_or_code_line(self):
        _level, reply = enforce_level_gate(
            "L2",
            "L1",
            "这是一段被硬闸门降级的回复。\n\n[LEVEL:L2]",
        )

        self.assertNotIn("题号", reply)
        self.assertNotIn("代码行", reply)


if __name__ == "__main__":
    unittest.main()
