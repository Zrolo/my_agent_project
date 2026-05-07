import os
import tempfile
import unittest

from fastapi.testclient import TestClient

import api_server
import database


class StudentCompletionRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "student_completion_test.db")
        database.init_db()
        api_server.app.dependency_overrides.clear()
        self.client = TestClient(api_server.app)

    def tearDown(self):
        api_server.app.dependency_overrides.clear()
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_student_can_record_problem_completion_with_evidence(self):
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_finish", "role": "student"}
        )

        response = self.client.post(
            "/api/student/problem-completions",
            json={
                "problem_id": "P1119",
                "problem_title": "P1119 灾后重建",
                "problem_url": "https://www.luogu.com.cn/problem/P1119",
                "reported_completion": "self_solved",
                "result_status": "accepted",
                "key_step_summary": "按修复时间逐步加入村庄，用新村庄 k 松弛所有 i,j。",
                "session_id": "chat-p1119",
            },
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual("self_solved", payload["record"]["reported_completion"])
        self.assertEqual("已经写下关键做法，后续可以配合小验证确认是否真正掌握。", payload["record"]["confidence_note"])
        self.assertEqual(3, payload["record"]["points_awarded"])
        self.assertIn("+3 积分", payload["message"])

        records = database.list_student_problem_completions(student_id="stu_finish")
        self.assertEqual(1, len(records))
        self.assertEqual("P1119", records[0]["problem_id"])
        self.assertIn("逐步加入村庄", records[0]["key_step_summary"])
        self.assertEqual(3, records[0]["points_awarded"])

    def test_classroom_taught_completion_gets_light_points_without_independent_bonus(self):
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_classroom", "role": "student"}
        )

        response = self.client.post(
            "/api/student/problem-completions",
            json={
                "problem_id": "P1119",
                "problem_title": "P1119 灾后重建",
                "reported_completion": "classroom_taught",
                "result_status": "accepted",
                "key_step_summary": "老师讲完后，我记住要按修复时间逐个加入村庄。",
            },
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("classroom_taught", payload["record"]["reported_completion"])
        self.assertEqual("课堂讲解后完成", payload["record"]["reported_completion_label"])
        self.assertEqual(2, payload["record"]["points_awarded"])
        self.assertIn("+2 积分", payload["message"])

    def test_uncertain_completion_does_not_award_points(self):
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_unsure", "role": "student"}
        )

        response = self.client.post(
            "/api/student/problem-completions",
            json={
                "problem_id": "P0001",
                "reported_completion": "unsure",
                "result_status": "unsure",
                "key_step_summary": "这题还没完全弄明白。",
            },
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual(0, payload["record"]["points_awarded"])
        self.assertNotIn("+", payload["message"])

    def test_student_can_list_problem_completion_history(self):
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_finish", "role": "student"}
        )
        database.create_student_problem_completion(
            student_id="stu_finish",
            problem_id="P1119",
            problem_title="灾后重建",
            problem_url="https://www.luogu.com.cn/problem/P1119",
            reported_completion="aichat_assisted",
            result_status="accepted",
            key_step_summary="按修复时间逐步加入村庄，每次用新村庄更新最短路。",
        )

        response = self.client.get("/api/student/problem-completions")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual(1, len(payload["records"]))
        self.assertEqual("P1119", payload["records"][0]["problem_id"])
        self.assertEqual("aichat_assisted", payload["records"][0]["reported_completion"])

    def test_student_home_includes_rolling_completion_summary(self):
        database.create_student_problem_completion(
            student_id="stu_home_finish",
            problem_id="P1119",
            problem_title="P1119 灾后重建",
            problem_url="https://www.luogu.com.cn/problem/P1119",
            reported_completion="self_solved",
            result_status="accepted",
            key_step_summary="用新修好村庄做中转点更新最短路。",
            session_id="s1",
        )
        database.create_student_problem_completion(
            student_id="stu_home_finish",
            problem_id="P2249",
            problem_title="P2249 查找",
            problem_url="https://www.luogu.com.cn/problem/P2249",
            reported_completion="aichat_assisted",
            result_status="sample_passed",
            key_step_summary="check(mid) 要说明是否还能往左找。",
            session_id="s2",
        )
        api_server.app.dependency_overrides[api_server.require_student] = (
            lambda: {"user_id": "stu_home_finish", "role": "student"}
        )

        response = self.client.get("/api/student/home")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        labels = [item["label"] for item in payload["stats"]]
        self.assertIn("近 15 天做题记录", labels)
        self.assertEqual(2, payload["completion_summary"]["last_15_days"])
        self.assertEqual(1, payload["completion_summary"]["self_solved_15_days"])
        self.assertEqual("这段时间已有做题记录，建议每题补一句关键做法，方便之后回顾。", payload["completion_summary"]["support_trend"])
        self.assertIn("independence_ratio", payload["completion_summary"])
        self.assertIn("exit_trigger_summary", payload)
        self.assertLessEqual(len(payload["recent_completions"]), 3)

    def test_completion_summary_does_not_call_zero_aichat_assistance_more(self):
        database.create_student_problem_completion(
            student_id="stu_small_hint_only",
            problem_id="P1119",
            problem_title="P1119 灾后重建",
            problem_url="https://www.luogu.com.cn/problem/P1119",
            reported_completion="small_hint",
            result_status="accepted",
            key_step_summary="用 floyd",
            session_id="s1",
        )

        summary = database.get_student_completion_summary("stu_small_hint_only", days=15)

        self.assertEqual(1, summary["last_15_days"])
        self.assertEqual(0, summary["aichat_assisted_15_days"])
        self.assertNotIn("AIChat 帮助后完成较多", summary["support_trend"])
        self.assertIn("补一句关键做法", summary["support_trend"])
        self.assertEqual(1, summary["weak_summary_15_days"])

    def test_completion_summary_tracks_support_fadeout_evidence(self):
        for method in ("self_solved", "small_hint", "aichat_assisted", "editorial_completed"):
            database.create_student_problem_completion(
                student_id="stu_fadeout",
                problem_id=f"P-{method}",
                problem_title=f"题目 {method}",
                problem_url="",
                reported_completion=method,
                result_status="accepted",
                key_step_summary="能说清这题最关键的做法。",
            )

        student_summary = database.get_student_completion_summary("stu_fadeout", days=15)
        self.assertEqual(2, student_summary["independent_or_small_hint_15_days"])
        self.assertEqual(2, student_summary["supported_or_editorial_15_days"])
        self.assertEqual(0.5, student_summary["independence_ratio"])
        self.assertIn("自己完成", student_summary["support_fadeout_label"])

        class_summary = database.get_class_completion_summary(days=15)
        self.assertEqual(2, class_summary["independent_or_small_hint_15_days"])
        self.assertEqual(2, class_summary["supported_or_editorial_15_days"])
        self.assertEqual(0.5, class_summary["independence_ratio"])

    def test_exit_trigger_summary_counts_verification_and_review_events(self):
        database.create_problem_bottleneck_event(
            student_id="stu_exit",
            problem_ref="P1119",
            session_id="chat-p1119",
            source_event="aichat_exit_ready",
            result_status="ready",
            bottleneck_type="understanding_ready",
            evidence="学生已经说清对象、更新方式和复杂度比较。",
        )
        database.create_problem_bottleneck_event(
            student_id="stu_exit",
            problem_ref="P1119",
            session_id="chat-p1119",
            source_event="problem_closure_passed",
            result_status="passed",
            bottleneck_type="complexity_analysis",
            evidence="能代入 N、M、Q 比较 Floyd 与 Dijkstra。",
        )
        database.create_problem_bottleneck_event(
            student_id="other_student",
            problem_ref="P2249",
            session_id="chat-p2249",
            source_event="problem_closure_failed",
            result_status="failed",
            bottleneck_type="boundary_edge_cases",
            evidence="没有说清 lower_bound 的边界。",
        )

        student_summary = database.get_student_exit_trigger_summary("stu_exit", days=15)
        self.assertEqual(1, student_summary["exit_ready_count"])
        self.assertEqual(1, student_summary["closure_passed_count"])
        self.assertEqual(0, student_summary["closure_failed_count"])
        self.assertEqual(2, student_summary["total_exit_events"])

        class_summary = database.get_class_exit_trigger_summary(days=15)
        self.assertEqual(1, class_summary["exit_ready_count"])
        self.assertEqual(1, class_summary["closure_passed_count"])
        self.assertEqual(1, class_summary["closure_failed_count"])
        self.assertEqual(3, class_summary["total_exit_events"])

    def test_teacher_stats_include_attention_pool_with_data_insufficient(self):
        database.create_student_problem_completion(
            student_id="active_student",
            problem_id="P1119",
            problem_title="P1119 灾后重建",
            problem_url="",
            reported_completion="self_solved",
            result_status="accepted",
            key_step_summary="用新村庄逐步松弛所有点对距离。",
            session_id="s1",
        )
        database.record_aichat_message(
            student_id="needs_help",
            problem_id="P1119",
            session_id="s2",
            role="user",
            content="我还是不知道为什么不用每次 Dijkstra。",
            problem_title="P1119 灾后重建",
            has_problem_context=True,
        )
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "teacher_radar", "role": "teacher"}
        )

        response = self.client.get("/api/teacher/stats")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertIn("attention_students", payload)
        reasons = [item["reason"] for item in payload["attention_students"]]
        self.assertTrue(any("缺少验证证据" in reason or "学习证据不足" in reason for reason in reasons))
        self.assertIn("completion_summary", payload)
        self.assertEqual(1, payload["completion_summary"]["self_solved_15_days"])
        self.assertIn("independence_ratio", payload["completion_summary"])
        self.assertIn("exit_trigger_summary", payload)


if __name__ == "__main__":
    unittest.main()
