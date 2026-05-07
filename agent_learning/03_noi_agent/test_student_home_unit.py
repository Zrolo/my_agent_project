import os
import tempfile
import unittest

from fastapi.testclient import TestClient

import api_server
import database


class StudentHomeApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "student_home_test.db")
        database.init_db()
        api_server.app.dependency_overrides.clear()
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_teacher_can_publish_markdown_announcement_for_student_home(self):
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "teacher_home", "role": "teacher"}
        )

        response = self.client.post(
            "/api/teacher/announcements",
            json={
                "title": "本周训练提醒",
                "body_markdown": "请先完成 **最短路** 复习，再做 P1119。",
                "pinned": True,
            },
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual("本周训练提醒", payload["announcement"]["title"])

        list_response = self.client.get("/api/teacher/announcements")
        self.assertEqual(200, list_response.status_code)
        rows = list_response.json()["announcements"]
        self.assertEqual(1, len(rows))
        self.assertIn("**最短路**", rows[0]["body_markdown"])

    def test_student_home_returns_compact_learning_snapshot(self):
        database.create_teacher_announcement(
            title="训练安排",
            body_markdown="今天先复习 Floyd，再完成一道同类题。",
            created_by="teacher_home",
        )
        database.record_aichat_message(
            student_id="stu_home",
            problem_id="P1119",
            session_id="s1",
            role="user",
            content="我觉得应该用 Dijkstra，但复杂度好像不对。",
            problem_title="P1119 灾后重建",
            problem_url="https://www.luogu.com.cn/problem/P1119",
            has_problem_context=True,
        )
        database.create_aichat_problem_closure(
            student_id="stu_home",
            problem_id="P1119",
            session_id="s1",
            problem_title="P1119 灾后重建",
            question="请估算 Floyd 和每次 Dijkstra 的总复杂度差多少。",
            target_focus="复杂度意识",
            status="quiz_ready",
        )
        database.create_aichat_problem_closure(
            student_id="stu_home",
            problem_id="P4047",
            session_id="s2",
            problem_title="P4047 部落划分",
            question="为什么输出的是下一条未合并边？",
            target_focus="最小生成树边界",
            status="passed",
        )
        database.grade_aichat_problem_closure(
            closure_id=2,
            student_id="stu_home",
            status="passed",
            answer="要看刚好剩 k 个连通块后的下一条边。",
            feedback="过关",
            points_awarded=5,
            next_review_at="2026-05-01T09:00:00",
        )
        database.create_student_problem_completion(
            student_id="stu_home",
            problem_id="P1119",
            problem_title="P1119 灾后重建",
            reported_completion="self_solved",
            result_status="accepted",
            key_step_summary="按修复时间逐步加入村庄，用新村庄松弛所有点对距离。",
            session_id="s1",
        )
        database.create_problem_bottleneck_event(
            student_id="stu_home",
            problem_ref="P1119",
            session_id="s1",
            source_event="problem_closure",
            result_status="needs_review",
            bottleneck_type="complexity_awareness",
            quiz_format="small_verification",
            target_focus="复杂度意识",
        )

        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_home", "role": "student"}
        )
        response = self.client.get("/api/student/home")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("训练安排", payload["announcement"]["title"])
        self.assertEqual("problem_closure", payload["continue_learning"]["kind"])
        self.assertEqual("继续结束验证", payload["continue_learning"]["action_label"])
        stat_labels = [item["label"] for item in payload["stats"]]
        self.assertIn("积分", stat_labels)
        self.assertIn("近 15 天做题记录", stat_labels)
        points_stat = next(item for item in payload["stats"] if item["label"] == "积分")
        self.assertEqual(8, points_stat["value"])
        self.assertIn("completion_summary", payload)
        self.assertIn("recent_completions", payload)
        self.assertEqual("复杂度意识", payload["recent_bottlenecks"][0]["label"])
        self.assertLessEqual(len(payload["recent_bottlenecks"]), 3)
        self.assertLessEqual(len(payload["review_reminders"]), 2)

    def test_student_home_empty_state_is_student_friendly(self):
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "new_student", "role": "student"}
        )

        response = self.client.get("/api/student/home")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertIsNone(payload["announcement"])
        self.assertEqual("empty", payload["continue_learning"]["kind"])
        self.assertEqual("开始问 AI", payload["continue_learning"]["action_label"])
        self.assertEqual([], payload["recent_bottlenecks"])
        self.assertEqual([], payload["review_reminders"])


if __name__ == "__main__":
    unittest.main()
