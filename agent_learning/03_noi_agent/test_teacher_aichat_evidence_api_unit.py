import os
import tempfile
import unittest

from fastapi.testclient import TestClient

import api_server
import database


class TeacherAIChatEvidenceApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "teacher_aichat_evidence.db")
        database.init_db()
        api_server.app.dependency_overrides.clear()
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "teacher_evidence", "role": "teacher"}
        )
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def _seed_session(self, *, student_id="stu_a", session_id="session_a", problem_id="P1119"):
        student_msg_id = database.record_aichat_conversation_message(
            student_id=student_id,
            student_username="student_a",
            student_real_name="张三",
            problem_id=problem_id,
            session_id=session_id,
            role="student",
            content="P1119 我知道用 Floyd，但不知道怎么按时间加村庄。",
            content_type="text",
        )
        database.record_aichat_conversation_message(
            student_id=student_id,
            student_username="student_a",
            student_real_name="张三",
            problem_id=problem_id,
            session_id=session_id,
            role="ai_coach",
            content="你已经抓到 Floyd 了，先看每个修好的村庄能不能作为中转点。",
            content_type="text",
            model_provider="deepseek_flash",
            model_name="deepseek-v4-flash",
        )
        database.record_aichat_judge_shadow_event(
            conversation_message_id=student_msg_id,
            student_id=student_id,
            student_username="student_a",
            student_real_name="张三",
            problem_id=problem_id,
            session_id=session_id,
            user_input="P1119 我知道用 Floyd，但不知道怎么按时间加村庄。",
            messages=[{"role": "user", "content": "P1119 我知道用 Floyd"}],
            rule_max_level="L2",
            rule_tutor_action="ask_one_question",
            rule_risk_tags=["bridge_attempt"],
            judge_primary_intent="learning",
            judge_phase="application_gap",
            judge_action_category="scaffolding",
            judge_action_subtype="give_micro_scaffold",
            judge_allowed_help_level="L2",
            judge_confidence=0.86,
            agreement_action_exact=False,
            agreement_action_family=True,
            agreement_help_level=True,
            agreement_would_override=True,
            final_tutor_action="give_micro_scaffold",
        )
        database.upsert_aichat_session_summary(
            session_id=session_id,
            student_id=student_id,
            student_username="student_a",
            student_real_name="张三",
            problem_id=problem_id,
            message_count=2,
            student_turn_count=1,
            ai_turn_count=1,
            has_understanding_evidence=True,
            understanding_evidence_types=["object_relation", "method_sketch", "debug_evidence"],
            same_gap_loop=True,
            same_gap_loop_type="evidence_seeking_loop",
            latest_tutor_action="give_micro_scaffold",
            latest_rule_max_level="L2",
            latest_judge_action_subtype="give_micro_scaffold",
            last_student_message="P1119 我知道用 Floyd，但不知道怎么按时间加村庄。",
        )

    def test_teacher_aichat_students_endpoint_returns_student_list(self):
        self._seed_session(student_id="stu_a", session_id="session_a", problem_id="P1119")

        response = self.client.get("/api/teacher/aichat_students")

        self.assertEqual(200, response.status_code)
        students = response.json()["students"]
        self.assertEqual(1, len(students))
        self.assertEqual("stu_a", students[0]["student_id"])
        self.assertEqual("student_a", students[0]["student_username"])
        self.assertEqual(1, students[0]["total_sessions"])
        self.assertEqual(2, students[0]["total_messages"])
        self.assertEqual("P1119", students[0]["recent_problem_id"])

    def test_teacher_aichat_sessions_endpoint_orders_sessions_newest_first(self):
        self._seed_session(student_id="stu_a", session_id="session_old", problem_id="P1119")
        self._seed_session(student_id="stu_a", session_id="session_new", problem_id="P401")

        response = self.client.get("/api/teacher/aichat_sessions?student_id=stu_a")

        self.assertEqual(200, response.status_code)
        sessions = response.json()["sessions"]
        self.assertEqual(["session_new", "session_old"], [row["session_id"] for row in sessions[:2]])
        self.assertEqual("P401", sessions[0]["problem_id"])
        self.assertTrue(sessions[0]["same_point_loop_detected"])
        self.assertEqual("give_micro_scaffold", sessions[0]["last_ai_action"])
        self.assertEqual(3, sessions[0]["evidence_count"])
        self.assertTrue(sessions[0]["evidence_flags"]["method_sketch"])

    def test_teacher_aichat_session_detail_endpoint_contains_all_three_parts(self):
        self._seed_session(student_id="stu_a", session_id="session_a", problem_id="P1119")

        response = self.client.get("/api/teacher/aichat_session_detail?session_id=session_a")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("session_a", payload["summary"]["session_id"])
        self.assertEqual(["student", "ai_coach"], [row["role"] for row in payload["messages"]])
        self.assertEqual(1, len(payload["judge_events"]))
        self.assertEqual("give_micro_scaffold", payload["judge_events"][0]["judge_action_subtype"])
        self.assertEqual("learning", payload["judge_events"][0]["judge_primary_intent"])


if __name__ == "__main__":
    unittest.main()
