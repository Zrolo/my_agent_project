import os
import tempfile
import unittest

from fastapi.testclient import TestClient

import api_server
import database


class StudentFeedbackDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "feedback_test.db")
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_create_and_list_student_feedback_orders_newest_first(self):
        first_id = database.create_student_feedback(
            student_id="stu001",
            category="aichat",
            rating=4,
            content="AIChat 能帮我拆题，但有时候希望解释更连贯。",
            page_context="/app/workspace/chat",
        )
        second_id = database.create_student_feedback(
            student_id="stu002",
            category="checkin",
            rating=5,
            content="打卡复盘可以让我知道下次怎么改。",
            page_context="/app/workspace/checkin",
        )

        rows = database.list_student_feedback(limit=10)

        self.assertEqual([second_id, first_id], [row["id"] for row in rows[:2]])
        self.assertEqual("stu002", rows[0]["student_id"])
        self.assertEqual("checkin", rows[0]["category"])
        self.assertEqual(5, rows[0]["rating"])
        self.assertIn("下次怎么改", rows[0]["content"])


class StudentFeedbackApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "feedback_api_test.db")
        database.init_db()
        api_server.app.dependency_overrides.clear()
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_student_can_submit_feedback_and_teacher_can_read_it(self):
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_feedback", "role": "student"}
        )
        submit_response = self.client.post(
            "/api/student/feedback",
            json={
                "category": "aichat",
                "rating": 3,
                "content": "希望 AIChat 少一点重复提问，多结合我上一句回答。",
                "page_context": "/app/workspace/chat",
            },
        )

        self.assertEqual(200, submit_response.status_code)
        self.assertEqual("ok", submit_response.json()["status"])

        api_server.app.dependency_overrides.clear()
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "teacher_feedback", "role": "teacher"}
        )
        list_response = self.client.get("/api/teacher/student-feedback")

        self.assertEqual(200, list_response.status_code)
        feedback = list_response.json()["feedback"]
        self.assertEqual(1, len(feedback))
        self.assertEqual("stu_feedback", feedback[0]["student_id"])
        self.assertEqual("aichat", feedback[0]["category"])
        self.assertEqual(3, feedback[0]["rating"])
        self.assertIn("重复提问", feedback[0]["content"])

    def test_student_feedback_rejects_too_short_content_with_chinese_message(self):
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_feedback", "role": "student"}
        )

        response = self.client.post(
            "/api/student/feedback",
            json={
                "category": "other",
                "rating": 4,
                "content": "好",
            },
        )

        self.assertEqual(422, response.status_code)
        self.assertIn("至少写 5 个字", response.text)


if __name__ == "__main__":
    unittest.main()
