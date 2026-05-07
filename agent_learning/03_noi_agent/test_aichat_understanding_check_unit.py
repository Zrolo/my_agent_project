import json
import unittest
from unittest.mock import patch

from noi_agent import generate_understanding_check, grade_understanding_check


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, payload):
        self.choices = [_FakeChoice(json.dumps(payload, ensure_ascii=False))]


class AIChatUnderstandingCheckTests(unittest.TestCase):
    def test_generate_understanding_check_uses_current_problem_not_generic_choice(self):
        captured = {}

        def fake_completion(**kwargs):
            captured.update(kwargs)
            return _FakeResponse({
                "status": "ok",
                "question": "你现在代码最后输出的是哪条边？题目真正要的是哪两个部落之间的距离？",
                "target_focus": "区分已合并边和未合并的跨部落最短边",
            })

        with patch("noi_agent._chat_completion_create", side_effect=fake_completion):
            result = generate_understanding_check(
                messages=[
                    {"role": "user", "content": "为什么输出不对？"},
                    {"role": "assistant", "content": "先对齐题目要的量和代码输出的量。"},
                ],
                problem_title="P4047 部落划分",
                problem_context="求 k 个部落划分后，最近两个部落之间距离的最大值。",
                student_code="for (...) aaaaa(i); printf(\"%.2lf\", k.top());",
                chat_model_provider="deepseek",
            )

        self.assertEqual("ok", result["status"])
        self.assertIn("题目真正要的是", result["question"])
        self.assertNotIn("哪一种表现最能说明", result["question"])
        self.assertEqual("deepseek", captured["provider_id"])
        prompt_text = captured["system_prompt"] + "\n" + captured["messages"][0]["content"]
        self.assertIn("当前题目", prompt_text)
        self.assertIn("学生代码", prompt_text)
        self.assertIn("不要生成通用学习习惯选择题", prompt_text)

    def test_grade_understanding_check_returns_passed_with_short_feedback(self):
        def fake_completion(**kwargs):
            return _FakeResponse({
                "status": "passed",
                "feedback": "说清楚了：你区分了代码输出的已合并边和题目要的跨部落距离。",
                "can_review": True,
            })

        with patch("noi_agent._chat_completion_create", side_effect=fake_completion):
            result = grade_understanding_check(
                question="你现在代码最后输出的是哪条边？题目真正要的是哪两个部落之间的距离？",
                answer="代码输出的是合并进树里的边，题目要的是剩下 k 个部落后下一条连接不同部落的最短边。",
                problem_title="P4047 部落划分",
                problem_context="求 k 个部落划分后，最近两个部落之间距离的最大值。",
                student_code="",
                chat_model_provider="kimi",
            )

        self.assertEqual("passed", result["status"])
        self.assertTrue(result["can_review"])
        self.assertIn("区分", result["feedback"])

    def test_grade_understanding_check_softens_harsh_failed_feedback(self):
        def fake_completion(**kwargs):
            return _FakeResponse({
                "status": "failed",
                "feedback": "你选错了城市，解释也很混乱。关键关系：拥堵度上限为 1 时，叶子节点最容易漏覆盖。",
                "followup": "重新说一下叶子节点为什么需要被覆盖。",
                "can_review": False,
            })

        with patch("noi_agent._chat_completion_create", side_effect=fake_completion):
            result = grade_understanding_check(
                question="拥堵度上限为 1 时，哪个城市最容易被遗漏覆盖？为什么？",
                answer="应该是 1 号城市，因为它离 3、4、6 比较远。",
                problem_title="树上核心城市",
                problem_context="选 k 个连通核心城市，使非核心城市到核心城市最大距离最小。",
                student_code="",
                chat_model_provider="deepseek",
            )

        self.assertEqual("failed", result["status"])
        self.assertNotIn("你选错了", result["feedback"])
        self.assertNotIn("混乱", result["feedback"])
        self.assertIn("还差一点", result["feedback"])
        self.assertIn("关键关系", result["feedback"])

    def test_generate_understanding_check_does_not_fallback_to_generic_quiz_on_llm_failure(self):
        with patch("noi_agent._chat_completion_create", side_effect=RuntimeError("boom")):
            result = generate_understanding_check(
                messages=[{"role": "user", "content": "我说清楚了。"}],
                problem_title="",
                problem_context="",
                student_code="",
            )

        self.assertEqual("unavailable", result["status"])
        self.assertNotIn("哪一种表现最能说明", result.get("question", ""))
        self.assertIn("先继续问 AIChat", result["message"])


if __name__ == "__main__":
    unittest.main()
