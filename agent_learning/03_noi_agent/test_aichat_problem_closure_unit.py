import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
import database


class AIChatProblemClosureDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "closure_test.db")
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_create_and_grade_problem_closure(self):
        closure_id = database.create_aichat_problem_closure(
            student_id="stu001",
            problem_id="P4047",
            session_id="session-1",
            problem_title="P4047 部落划分",
            question="合并到剩下 k 个部落时，下一条未合并的最短边表示什么？",
            target_focus="区分内部合并边和跨部落最短边",
        )

        row = database.get_aichat_problem_closure(closure_id)
        self.assertEqual("quiz_ready", row["status"])
        self.assertEqual("P4047", row["problem_id"])
        self.assertEqual("区分内部合并边和跨部落最短边", row["target_focus"])

        updated = database.grade_aichat_problem_closure(
            closure_id=closure_id,
            student_id="stu001",
            status="passed",
            answer="这条边是当前两个不同部落之间最短的距离，不应该再合并进去。",
            feedback="说清楚了。",
            followup="",
            points_awarded=2,
            next_review_at="2026-04-29T12:00:00",
        )

        self.assertEqual("passed", updated["status"])
        self.assertEqual(2, updated["points_awarded"])
        self.assertEqual("2026-04-29T12:00:00", updated["next_review_at"])
        self.assertIn("不应该再合并", updated["answer"])


class AIChatProblemClosureApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "closure_api_test.db")
        database.init_db()
        api_server.app.dependency_overrides.clear()
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_closure", "role": "student"}
        )
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_start_and_grade_problem_closure_uses_recent_aichat_context(self):
        database.record_aichat_message(
            student_id="stu_closure",
            problem_id="P4047",
            session_id="session-closure",
            role="user",
            content="我明白了，停在 k 个部落以后要看下一条跨部落边。",
            problem_title="P4047 部落划分",
            has_problem_context=True,
            has_student_code=True,
        )

        captured = {}

        def fake_generate(**kwargs):
            captured["generate"] = kwargs
            return {
                "status": "ok",
                "question": "为什么合并到剩下 k 个部落后，下一条未合并的最短边就是答案？",
                "target_focus": "最小生成树截断后的跨部落距离",
            }

        with patch("api_server.generate_understanding_check", side_effect=fake_generate):
            start_response = self.client.post(
                "/api/chat/problem-closure/start",
                json={
                    "problem_id": "P4047",
                    "session_id": "session-closure",
                    "problem_title": "P4047 部落划分",
                    "problem_context": "求 k 个部落划分后最近两个部落距离最大。",
                    "student_code": "sort(a.begin(), a.end(), cmp);",
                    "chat_model_provider": "deepseek",
                },
            )

        self.assertEqual(200, start_response.status_code)
        start_payload = start_response.json()
        self.assertEqual("ok", start_payload["status"])
        self.assertGreater(start_payload["closure_id"], 0)
        self.assertIn("下一条未合并", start_payload["question"])
        self.assertEqual("deepseek", captured["generate"]["chat_model_provider"])
        self.assertIn("停在 k 个部落", captured["generate"]["messages"][0]["content"])
        trigger_summary = database.get_student_exit_trigger_summary("stu_closure", days=15)
        self.assertEqual(1, trigger_summary["closure_quiz_count"])

        def fake_grade(**kwargs):
            captured["grade"] = kwargs
            return {
                "status": "passed",
                "feedback": "说清楚了：你抓住了跨部落边这个量。",
                "followup": "",
                "can_review": True,
            }

        with patch("api_server.grade_understanding_check", side_effect=fake_grade):
            grade_response = self.client.post(
                "/api/chat/problem-closure/grade",
                json={
                    "closure_id": start_payload["closure_id"],
                    "answer": "因为再合并就会把两个部落连成一个，所以这条边正是两个部落之间最近距离。",
                    "problem_id": "P4047",
                    "session_id": "session-closure",
                    "problem_title": "P4047 部落划分",
                    "problem_context": "求 k 个部落划分后最近两个部落距离最大。",
                    "student_code": "sort(a.begin(), a.end(), cmp);",
                    "chat_model_provider": "deepseek",
                },
            )

        self.assertEqual(200, grade_response.status_code)
        grade_payload = grade_response.json()
        self.assertEqual("passed", grade_payload["status"])
        self.assertEqual(2, grade_payload["points_awarded"])
        self.assertTrue(grade_payload["can_start_next_problem"])
        self.assertIn("复习", grade_payload["next_review_message"])
        self.assertEqual(start_payload["question"], captured["grade"]["question"])
        trigger_summary = database.get_student_exit_trigger_summary("stu_closure", days=15)
        self.assertEqual(1, trigger_summary["closure_passed_count"])


if __name__ == "__main__":
    unittest.main()
