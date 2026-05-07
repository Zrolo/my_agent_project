import os
import json
import tempfile
import unittest

from fastapi.testclient import TestClient

import api_server
import auth
import database


class TeacherLearningDiagnosisApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        self.original_accounts_file = auth.ACCOUNTS_FILE
        database.DB_PATH = os.path.join(self.temp_dir.name, "teacher_learning_diagnosis.db")
        auth.ACCOUNTS_FILE = os.path.join(self.temp_dir.name, "accounts.json")
        with open(auth.ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        database.init_db()
        api_server.app.dependency_overrides.clear()
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "teacher_diag", "role": "teacher"}
        )
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        database.DB_PATH = self.original_db_path
        auth.ACCOUNTS_FILE = self.original_accounts_file
        self.temp_dir.cleanup()

    def _seed_student_learning(self, student_id: str = "stu_diag"):
        classify_algo = lambda tag: "algo"
        database.upsert_luogu_problemset(
            {
                "pid": "P3371",
                "title": "单源最短路径",
                "difficulty": 4,
                "tags": ["最短路", "Dijkstra"],
            },
            classify_algo,
        )
        database.upsert_luogu_problemset(
            {
                "pid": "P4779",
                "title": "单源最短路径标准版",
                "difficulty": 4,
                "tags": ["最短路", "Dijkstra"],
            },
            classify_algo,
        )
        database.upsert_luogu_problemset(
            {
                "pid": "P5905",
                "title": "全源最短路",
                "difficulty": 5,
                "tags": ["最短路"],
            },
            classify_algo,
        )
        database.create_student_problem_completion(
            student_id=student_id,
            problem_id="P1119",
            problem_title="P1119 灾后重建",
            problem_url="https://www.luogu.com.cn/problem/P1119",
            reported_completion="self_solved",
            result_status="accepted",
            key_step_summary="按修复时间逐个加入村庄，用新村庄作为 k 更新 i 到 j。",
            session_id="chat-p1119",
        )
        database.create_student_problem_completion(
            student_id=student_id,
            problem_id="P3371",
            problem_title="P3371 单源最短路",
            problem_url="https://www.luogu.com.cn/problem/P3371",
            reported_completion="aichat_assisted",
            result_status="sample_passed",
            key_step_summary="知道要用最短路，但还不确定松弛顺序怎么写。",
            session_id="chat-p3371",
        )
        checkin_id = database.create_checkin(
            student_id=student_id,
            problem_url="https://www.luogu.com.cn/problem/P3371",
            problem_title="P3371 单源最短路",
            oj_source="luogu",
            completion_status="hinted",
            bottleneck_text="我知道是最短路，但不会把松弛过程写进代码。",
            error_types=["代码实现"],
            submission_result="WA",
            session_id="checkin-p3371",
        )
        database.create_review(
            checkin_id=checkin_id,
            student_id=student_id,
            error_tags=["implementation"],
            diagnosis="知道算法但不会落到代码。",
            next_action="先写出 dist 的含义，再写一轮松弛。",
            suggested_topic="最短路实现",
            error_layer="implementation",
            main_block="松弛过程没有落实到代码",
            key_bridge="dist 含义与松弛条件",
        )
        review = database.get_review_by_checkin(checkin_id)
        database.update_review_bridge_path(review["id"], "main_clear")
        database.create_problem_bottleneck_event(
            student_id=student_id,
            problem_ref="P3371",
            session_id="chat-p3371",
            source_event="closure_quiz",
            result_status="failed",
            bottleneck_type="implementation",
            evidence="学生知道最短路，但不会把松弛条件写成代码。",
        )
        database.record_aichat_conversation_message(
            student_id=student_id,
            student_username="stu_diag",
            student_real_name="学生诊断",
            problem_id="P3371",
            session_id="chat-p3371",
            role="student",
            content="我知道用 Dijkstra，但是不知道 dist 和松弛条件怎么写。",
        )
        database.upsert_aichat_session_summary(
            session_id="chat-p3371",
            student_id=student_id,
            student_username="stu_diag",
            student_real_name="学生诊断",
            problem_id="P3371",
            message_count=4,
            student_turn_count=2,
            ai_turn_count=2,
            has_understanding_evidence=True,
            understanding_evidence_types=["method_sketch"],
            same_gap_loop=True,
            same_gap_loop_type="stuck_loop",
            latest_tutor_action="give_micro_scaffold",
            latest_rule_max_level="L2",
            latest_judge_action_subtype="give_micro_scaffold",
            last_student_message="我知道用 Dijkstra，但是不知道 dist 和松弛条件怎么写。",
        )

    def _move_completion_to_days_ago(self, student_id: str, problem_id: str, days_ago: int):
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE student_problem_completions
            SET created_at = datetime('now', ?)
            WHERE student_id = ? AND problem_id = ?
            """,
            (f"-{days_ago} days", student_id, problem_id),
        )
        conn.commit()
        conn.close()

    def test_student_dossier_returns_15_day_series_and_learning_sections(self):
        self._seed_student_learning()

        response = self.client.get("/api/teacher/student-dossier?student_id=stu_diag&days=15")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("stu_diag", payload["student"]["student_id"])
        self.assertEqual(15, payload["window_days"])
        self.assertEqual(15, len(payload["daily_series"]))
        self.assertEqual(2, payload["summary"]["completed_count"])
        self.assertEqual(1, payload["summary"]["self_solved_count"])
        self.assertEqual(1, payload["summary"]["aichat_assisted_count"])
        self.assertEqual(1, payload["summary"]["review_passed_count"])
        self.assertTrue(payload["summary"]["needs_attention"])
        self.assertGreaterEqual(max(row["completed_count"] for row in payload["daily_series"]), 2)
        self.assertGreater(max(row["independence_score"] for row in payload["daily_series"]), 0)
        self.assertGreater(max(row["quality_score"] for row in payload["daily_series"]), 0)
        self.assertTrue(payload["issue_summary"])
        self.assertIn("知道算法", payload["next_teacher_action"])
        self.assertTrue(payload["problem_completions"])
        self.assertTrue(payload["reviews"])
        self.assertTrue(payload["aichat_sessions"])
        self.assertIn("period_comparison", payload)
        self.assertIn("independence_delta", payload["period_comparison"])
        self.assertIn("independence_trend_label", payload["period_comparison"])
        self.assertIn("next_practice_recommendations", payload)
        self.assertTrue(payload["next_practice_recommendations"])
        first_recommendation = payload["next_practice_recommendations"][0]
        self.assertEqual("P4779", first_recommendation["pid"])
        self.assertIn("同类巩固", first_recommendation["reason"])
        self.assertNotIn("P3371", [item["pid"] for item in payload["next_practice_recommendations"]])

    def test_student_dossier_uses_account_display_name(self):
        self._seed_student_learning("stu_named")
        with open(auth.ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "stu_named": {
                        "id": "stu_named",
                        "role": "student",
                        "username": "stu_named",
                        "display_name": "真实姓名",
                    }
                },
                f,
            )

        response = self.client.get("/api/teacher/student-dossier?student_id=stu_named&days=15")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("真实姓名", payload["student"]["display_name"])

    def test_student_dossier_without_records_returns_empty_series(self):
        response = self.client.get("/api/teacher/student-dossier?student_id=empty_stu&days=15")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual(15, len(payload["daily_series"]))
        self.assertEqual(0, payload["summary"]["completed_count"])
        self.assertFalse(payload["summary"]["needs_attention"])
        self.assertEqual([], payload["issue_summary"])
        self.assertIn("课堂观察", payload["next_teacher_action"])

    def test_class_learning_diagnosis_aggregates_attention_and_practice(self):
        self._seed_student_learning("stu_diag")

        response = self.client.get("/api/teacher/class-learning-diagnosis?days=15")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertIn("attention_students", payload)
        self.assertIn("class_issue_summary", payload)
        self.assertIn("practice_summary", payload)
        self.assertGreaterEqual(payload["practice_summary"]["completed_count"], 2)
        self.assertGreaterEqual(payload["practice_summary"]["aichat_assisted_count"], 1)
        self.assertTrue(any(row["student_id"] == "stu_diag" for row in payload["attention_students"]))
        self.assertTrue(any(row["category"] == "代码实现卡住" for row in payload["class_issue_summary"]))
        first_issue = payload["class_issue_summary"][0]
        self.assertIn("resource_suggestions", first_issue)
        self.assertIn("recommended_exercise", first_issue["resource_suggestions"])
        self.assertIn("mini_lesson", first_issue["resource_suggestions"])
        self.assertIn("classroom_activity", first_issue["resource_suggestions"])

    def test_teacher_can_create_and_list_student_notes(self):
        create_response = self.client.post(
            "/api/teacher/student-notes",
            json={
                "student_id": "stu_diag",
                "note": "下次让他先口头说 dist 含义。",
                "status": "continue_followup",
                "next_followup_at": "2026-05-10",
                "intervention_type": "mini_lesson",
                "target_issue": "代码实现卡住",
            },
        )

        self.assertEqual(200, create_response.status_code)
        self.assertEqual("ok", create_response.json()["status"])

        list_response = self.client.get("/api/teacher/student-notes?student_id=stu_diag")

        self.assertEqual(200, list_response.status_code)
        notes = list_response.json()["notes"]
        self.assertEqual(1, len(notes))
        self.assertEqual("stu_diag", notes[0]["student_id"])
        self.assertIn("dist", notes[0]["note"])
        self.assertEqual("continue_followup", notes[0]["status"])
        self.assertEqual("mini_lesson", notes[0]["intervention_type"])
        self.assertEqual("代码实现卡住", notes[0]["target_issue"])
        self.assertIn("followup_observation", notes[0])
        self.assertIn("观察", notes[0]["followup_observation"]["label"])


if __name__ == "__main__":
    unittest.main()
