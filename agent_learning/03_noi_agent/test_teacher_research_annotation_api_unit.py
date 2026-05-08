import json
import os
import tempfile
import unittest

from fastapi.testclient import TestClient

import api_server
import database


class TeacherResearchAnnotationApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "teacher_research_annotation.db")
        database.init_db()
        api_server.app.dependency_overrides.clear()
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "coach_001", "role": "teacher"}
        )
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def _seed_aichat_turn(self):
        user_id = database.record_aichat_message(
            "student_a",
            "P2678",
            "session_binsearch",
            "user",
            "我知道要二分答案，但是 check(mid) 到底返回 true 还是 false 我总写反。",
            problem_title="跳石头",
            problem_url="https://www.luogu.com.cn/problem/P2678",
            has_problem_context=True,
            has_student_code=False,
        )
        assistant_id = database.record_aichat_message(
            "student_a",
            "P2678",
            "session_binsearch",
            "assistant",
            "先别急着写代码。你先说说 mid 代表的是一个限制，还是一个已经确定的答案？",
            problem_title="跳石头",
            problem_url="https://www.luogu.com.cn/problem/P2678",
            has_problem_context=True,
            has_student_code=False,
        )
        database.record_aichat_message(
            "student_a",
            "P2678",
            "session_binsearch",
            "user",
            "那 mid 应该是候选的最小距离。",
            problem_title="跳石头",
        )
        return user_id, assistant_id

    def _seed_aichat_context_turn(self):
        database.record_aichat_message(
            "student_a",
            "P2678",
            "session_context",
            "user",
            "这题我知道是二分答案吗？",
            problem_title="跳石头",
        )
        database.record_aichat_message(
            "student_a",
            "P2678",
            "session_context",
            "assistant",
            "先别急着确认题型，你看题面里哪个量像候选答案？",
            problem_title="跳石头",
        )
        user_id = database.record_aichat_message(
            "student_a",
            "P2678",
            "session_context",
            "user",
            "我知道要二分答案，但是 check(mid) 到底返回 true 还是 false 我总写反。",
            problem_title="跳石头",
        )
        assistant_id = database.record_aichat_message(
            "student_a",
            "P2678",
            "session_context",
            "assistant",
            "这里先只看一句话：mid 如果能做到，答案应该往更大试还是更小试？",
            problem_title="跳石头",
        )
        database.record_aichat_message(
            "student_a",
            "P2678",
            "session_context",
            "user",
            "如果能做到，应该试更大。",
            problem_title="跳石头",
        )
        return user_id, assistant_id

    def test_research_samples_endpoint_returns_student_turn_samples_from_aichat_messages(self):
        user_id, assistant_id = self._seed_aichat_turn()

        response = self.client.get("/api/teacher/research/aichat-samples?limit=20")

        self.assertEqual(200, response.status_code)
        samples = response.json()["samples"]
        first = samples[0]
        self.assertEqual(f"aichat_message_{user_id}", first["sample_id"])
        self.assertEqual("student_a", first["student_id"])
        self.assertEqual("P2678", first["problem_ref"])
        self.assertEqual("跳石头", first["problem_title"])
        self.assertEqual(user_id, first["student_message_id"])
        self.assertEqual(assistant_id, first["assistant_message_id"])
        self.assertIn("check(mid)", first["student_message"])
        self.assertIn("mid 代表", first["assistant_reply"])
        self.assertFalse(first["annotated"])

    def test_research_samples_include_session_context_window_for_turn_level_judgement(self):
        user_id, assistant_id = self._seed_aichat_context_turn()

        response = self.client.get("/api/teacher/research/aichat-samples?limit=20")

        self.assertEqual(200, response.status_code)
        samples = response.json()["samples"]
        sample = next(item for item in samples if item["student_message_id"] == user_id)
        context = sample["context_messages"]
        self.assertGreaterEqual(len(context), 4)
        self.assertIn("这题我知道是二分答案吗", context[0]["content"])
        self.assertTrue(any(item["id"] == user_id and item["is_current_student"] for item in context))
        self.assertTrue(any(item["id"] == assistant_id and item["is_target_assistant"] for item in context))
        self.assertTrue(any("如果能做到，应该试更大" in item["content"] for item in context))

    def test_teacher_can_save_annotation_and_export_jsonl(self):
        user_id, _assistant_id = self._seed_aichat_turn()
        sample_id = f"aichat_message_{user_id}"

        save_response = self.client.post(
            "/api/teacher/research/bridge-annotations",
            json={
                "sample_id": sample_id,
                "student_message_id": user_id,
                "student_state": "strategy_application_gap",
                "bridge_family": "predicate_bridge",
                "known_focus": "check_condition",
                "help_seeking_type": "instrumental_help",
                "missing_link": "学生缺少把候选答案 mid 翻译成可行性判断的关系。",
                "allowed_help_level": "L2",
                "forbidden_completion": "不能直接给完整 check 条件和边界更新方向。",
                "needs_new_focus": False,
                "confidence": 4,
                "notes": "典型二分答案 check 卡点。",
            },
        )

        self.assertEqual(200, save_response.status_code)
        self.assertTrue(save_response.json()["annotation"]["saved"])

        export_response = self.client.get("/api/teacher/research/bridge-annotations/export?format=jsonl")

        self.assertEqual(200, export_response.status_code)
        self.assertIn("application/x-ndjson", export_response.headers["content-type"])
        lines = [line for line in export_response.text.splitlines() if line.strip()]
        self.assertEqual(1, len(lines))
        exported = json.loads(lines[0])
        self.assertEqual(sample_id, exported["sample_id"])
        self.assertEqual("strategy_application_gap", exported["gold_student_state"])
        self.assertEqual("predicate_bridge", exported["gold_bridge_family"])
        self.assertEqual("check_condition", exported["gold_known_focus"])
        self.assertIn("check(mid)", exported["student_message"])
        self.assertIn("不能直接给完整 check", exported["gold_forbidden_completion"])

    def test_teacher_can_export_annotations_as_csv(self):
        user_id, _assistant_id = self._seed_aichat_turn()
        self.client.post(
            "/api/teacher/research/bridge-annotations",
            json={
                "sample_id": f"aichat_message_{user_id}",
                "student_message_id": user_id,
                "student_state": "strategy_application_gap",
                "bridge_family": "predicate_bridge",
                "known_focus": "check_condition",
                "help_seeking_type": "instrumental_help",
                "missing_link": "学生缺少把候选答案 mid 翻译成可行性判断的关系。",
                "allowed_help_level": "L2",
                "forbidden_completion": "不能直接给完整 check 条件和边界更新方向。",
                "needs_new_focus": False,
                "confidence": 4,
                "notes": "",
            },
        )

        response = self.client.get("/api/teacher/research/bridge-annotations/export?format=csv")

        self.assertEqual(200, response.status_code)
        self.assertIn("text/csv", response.headers["content-type"])
        self.assertIn("sample_id,gold_student_state,gold_bridge_family", response.text)
        self.assertIn("aichat_message_", response.text)


if __name__ == "__main__":
    unittest.main()
