import time
import unittest

from fastapi.testclient import TestClient

import api_server
import review_engine
from auth import create_token
from database import (
    LEARNING_STATUS_SELF_CHECK_REQUIRED,
    create_checkin,
    create_pending_review,
    create_review,
    create_review_quiz,
    get_quiz_by_id,
    get_confirm_pool_entry,
    increment_confirm_pool_skip,
    init_db,
    record_quiz_attempt,
    update_quiz_status,
    update_review_learning_status,
    upsert_confirm_pool_entry,
    upsert_luogu_problemset,
)
from problem_bank import classify_tag


def auth_headers(student_id: str) -> dict:
    token = create_token(student_id, "student")
    return {"Authorization": f"Bearer {token}"}


class LearningRoutingTests(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(api_server.app)
        self.student_id = f"route_student_{int(time.time() * 1000)}"

    def _create_checkin(self, title: str = "测试题", completion_status: str = "independent", submission_result: str = "not_submitted", bottleneck_text: str = "我知道是并列约束，但还是卡住，不知道该怎么把条件整理成统一关系。") -> int:
        return create_checkin(
            student_id=self.student_id,
            problem_url="https://example.com/problem",
            problem_title=title,
            oj_source="luogu",
            completion_status=completion_status,
            bottleneck_text=bottleneck_text,
            error_types=["模型转化"],
            reflection="这里像是并列约束。",
            problem_context="每个活动都必须同时满足时间窗口和指定地点两个条件。",
            problem_tags=["差分约束"],
            chat_context_summary="",
            submission_result=submission_result,
            student_code="",
        )

    def _create_completed_review(self, checkin_id: int, transfer_signal: str = "当约束能转成不等式链，且目标是判断是否存在矛盾时，要警惕这种图上关系建模。"):
        create_pending_review(checkin_id, self.student_id)
        create_review(
            checkin_id=checkin_id,
            student_id=self.student_id,
            error_tags=[],
            diagnosis="ok",
            next_action="ok",
            suggested_topic="ok",
            error_layer="core_design",
            main_block="你卡在约束关系没有统一。",
            key_bridge="先把不等式约束改写成统一方向的边。",
            next_step="先把每条不等式改写成边。",
            transfer_signal=transfer_signal,
            review_quality_flags=[],
        )

    def _create_main_quiz_passed(self, review_id: int, checkin_id: int):
        quiz_id = create_review_quiz(
            review_id=review_id,
            student_id=self.student_id,
            checkin_id=checkin_id,
            round=1,
            quiz_role=review_engine.QUIZ_ROLE_MAIN,
            quiz_type="choice",
            question_text="main",
            options=[{"value": "A", "label": "A"}],
            correct_answer="A",
            explanation="ok",
            bridge_feedback="ok",
            distractor_feedback={},
            target_bridge="bridge",
            source_error_layer="core_design",
            meta={},
        )
        update_quiz_status(quiz_id, "correct")
        record_quiz_attempt(quiz_id, self.student_id, "A", True, "ok")
        return quiz_id

    def test_help_signal_only_matches_explicit_keywords_or_failure(self):
        route_a = {
            "completion_status": "independent",
            "submission_result": "not_submitted",
            "bottleneck_text": "我还是卡住了，看不懂这些约束该怎么统一。",
            "reflection": "",
        }
        self.assertTrue(api_server.has_explicit_help_signal(route_a))

        route_emotion = {
            "completion_status": "independent",
            "submission_result": "not_submitted",
            "bottleneck_text": "这题真的很难，我有点烦。",
            "reflection": "",
        }
        self.assertFalse(api_server.has_explicit_help_signal(route_emotion))

        route_failed = {
            "completion_status": "independent",
            "submission_result": "wa",
            "bottleneck_text": "我觉得自己差一点。",
            "reflection": "",
        }
        self.assertTrue(api_server.has_explicit_help_signal(route_failed))

        route_failed_but_specific = {
            "completion_status": "independent",
            "submission_result": "wa",
            "bottleneck_text": "我会写二分，但当 a[mid] == x 时，我总不知道应该把右边界收成 mid 还是 mid-1。",
            "reflection": "我总担心把答案漏掉。",
        }
        self.assertFalse(api_server.has_explicit_help_signal(route_failed_but_specific))

    def test_generate_quiz_routes_explicit_help_signal_to_remedy(self):
        checkin_id = self._create_checkin(
            bottleneck_text="我不会做这题，已经卡住了，完全看不懂这些约束怎么统一。",
        )
        self._create_completed_review(checkin_id)
        detail = api_server.get_checkin_detail(checkin_id)
        review_id = detail["review"]["review_id"]

        response = self.client.post(
            f"/api/reviews/{review_id}/quiz/generate",
            headers=auth_headers(self.student_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("remedy_available", response.json()["next_state"])
        self.assertEqual("remedy_available", response.json()["learning_status"])
        self.assertIn("先回到卡住点", response.json()["message"])

    def test_generate_quiz_should_not_skip_specific_failed_boundary_case(self):
        checkin_id = self._create_checkin(
            title="P2249 查找",
            submission_result="wa",
            bottleneck_text="我会写二分，但当 a[mid] == x 时，我总不知道应该把右边界收成 mid 还是 mid-1。",
        )
        create_pending_review(checkin_id, self.student_id)
        create_review(
            checkin_id=checkin_id,
            student_id=self.student_id,
            error_tags=["边界处理"],
            diagnosis="ok",
            next_action="ok",
            suggested_topic="ok",
            error_layer="implementation",
            main_block="a[mid]==x 时右边界应设为 mid 而非 mid-1。",
            key_bridge="找最左位置时要保留 mid 作为候选。",
            next_step="先手推 [1,2,2,3] 这一组边界变化。",
            transfer_signal="看到第一个出现位置时，要警惕 lower_bound 式边界更新。",
            review_quality_flags=[],
        )
        detail = api_server.get_checkin_detail(checkin_id)
        review_id = detail["review"]["review_id"]

        response = self.client.post(
            f"/api/reviews/{review_id}/quiz/generate",
            headers=auth_headers(self.student_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("quiz_in_progress", response.json()["learning_status"])
        self.assertIn("a[mid]", response.json()["quiz"]["question_text"])

    def test_a_route_can_resolve_after_remedy(self):
        checkin_id = self._create_checkin(
            bottleneck_text="我不会做这题，已经卡住了，完全看不懂这些约束怎么统一。",
        )
        self._create_completed_review(checkin_id)
        detail = api_server.get_checkin_detail(checkin_id)
        review_id = detail["review"]["review_id"]

        quiz_response = self.client.post(
            f"/api/reviews/{review_id}/quiz/generate",
            headers=auth_headers(self.student_id),
        )
        self.assertEqual(200, quiz_response.status_code)
        self.assertEqual("remedy_available", quiz_response.json()["next_state"])

        remedy_response = self.client.post(
            f"/api/reviews/{review_id}/remedy",
            json={"action_type": "dynamic_bridge_help"},
            headers=auth_headers(self.student_id),
        )
        self.assertEqual(200, remedy_response.status_code)
        self.assertEqual("remedy_in_progress", remedy_response.json()["learning_status"])

        resolve_response = self.client.post(
            f"/api/reviews/{review_id}/remedy/resolve",
            json={"status": "resolved"},
            headers=auth_headers(self.student_id),
        )
        self.assertEqual(200, resolve_response.status_code)
        self.assertEqual("quiz_in_progress", resolve_response.json()["learning_status"])
        self.assertEqual("final_micro_confirm", resolve_response.json()["next_state"])

        final_quiz = get_quiz_by_id(resolve_response.json()["quiz"]["quiz_id"])
        answer_response = self.client.post(
            f"/api/quizzes/{final_quiz['id']}/answer",
            json={"answer_text": final_quiz["correct_answer"]},
            headers=auth_headers(self.student_id),
        )
        self.assertEqual(200, answer_response.status_code)
        self.assertEqual("resolved", answer_response.json()["learning_status"])

    def test_b_gate_requires_main_followup_optional_and_self_check_clear(self):
        review_context = {
            "completion_status": "independent",
            "submission_result": "not_submitted",
            "bottleneck_text": "我不知道。",
            "reflection": "",
            "understanding_self_check": "clear",
        }
        quizzes = [{"quiz_role": "main", "status": "correct"}]
        self.assertTrue(api_server.passes_explanation_gate(review_context, quizzes))

        quizzes_with_failed_followup = [
            {"quiz_role": "main", "status": "correct"},
            {"quiz_role": "followup", "status": "incorrect"},
        ]
        self.assertFalse(api_server.passes_explanation_gate(review_context, quizzes_with_failed_followup))

    def test_transfer_signal_requires_trigger_and_bridge_relation(self):
        self.assertTrue(
            review_engine.transfer_signal_has_explicit_trigger(
                "当约束能转成不等式链，而且目标是判断是否存在矛盾时，要想到统一建边。",
                "先把不等式约束改写成统一方向的边。",
            )
        )
        self.assertFalse(
            review_engine.transfer_signal_has_explicit_trigger(
                "遇到类似题要想到这个方法。",
                "先把不等式约束改写成统一方向的边。",
            )
        )

    def test_remedy_must_echo_original_bottleneck(self):
        payload = review_engine.generate_remedy_explanation(
            {
                "error_layer": "modeling",
                "bottleneck_text": "我知道这里像并列约束，但卡住了，不知道怎么统一整理成关系。",
                "main_block": "你卡在约束关系没有统一。",
                "next_step": "先把约束逐条改写。",
            },
            review_engine.REMEDY_ACTION_DYNAMIC,
        )

        self.assertIn("并列约束", payload["remedy_text"])
        self.assertIn("卡住", payload["remedy_text"])
        self.assertIn("同一种关系", payload["remedy_text"])

    def test_confirm_pool_skip_marks_needs_backfill_after_four_times(self):
        problem_id = upsert_luogu_problemset(
            {
                "pid": f"P{int(time.time() * 1000)}",
                "title": "差分约束测试题",
                "difficulty": 4,
                "tags": ["差分约束"],
                "description": "desc",
                "inputFormat": "",
                "outputFormat": "",
                "samples": [],
                "limits": {"time": [1000], "memory": [128]},
            },
            classify_tag,
        )
        upsert_confirm_pool_entry(
            problem_id=problem_id,
            problem_url="https://www.luogu.com.cn/problem/PTEST",
            structure_type="difference_constraints",
            difficulty=4,
            bridge_note="不等式约束转有向边，矛盾即正环",
            status="usable",
        )
        for _ in range(4):
            increment_confirm_pool_skip("difference_constraints")

        entry = get_confirm_pool_entry("difference_constraints")
        self.assertEqual(4, entry["skip_count"])
        self.assertEqual("needs_backfill", entry["status"])

    def test_self_check_clear_enters_confirm_when_pool_hit_and_gate_passes(self):
        checkin_id = self._create_checkin()
        self._create_completed_review(checkin_id)
        detail = api_server.get_checkin_detail(checkin_id)
        review_id = detail["review"]["review_id"]
        self._create_main_quiz_passed(review_id, checkin_id)
        update_review_learning_status(review_id, LEARNING_STATUS_SELF_CHECK_REQUIRED)

        problem_id = upsert_luogu_problemset(
            {
                "pid": f"PX{int(time.time() * 1000)}",
                "title": "差分约束 confirm 题",
                "difficulty": 3,
                "tags": ["差分约束"],
                "description": "desc",
                "inputFormat": "",
                "outputFormat": "",
                "samples": [],
                "limits": {"time": [1000], "memory": [128]},
            },
            classify_tag,
        )
        upsert_confirm_pool_entry(
            problem_id=problem_id,
            problem_url="https://www.luogu.com.cn/problem/PX",
            structure_type="difference_constraints",
            difficulty=3,
            bridge_note="不等式约束转有向边，矛盾即正环",
            status="usable",
        )

        response = self.client.post(
            f"/api/reviews/{review_id}/self-check",
            json={"status": "clear"},
            headers=auth_headers(self.student_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("confirm_quiz", response.json()["next_state"])
        self.assertEqual("confirm", response.json()["quiz"]["quiz_role"])
        self.assertEqual("fixed_pool", response.json()["quiz"]["meta"]["confirm_mode"])
        self.assertEqual("difference_constraints", response.json()["quiz"]["meta"]["structure_type"])

    def test_confirm_correct_answer_resolves_review(self):
        checkin_id = self._create_checkin()
        self._create_completed_review(checkin_id)
        detail = api_server.get_checkin_detail(checkin_id)
        review_id = detail["review"]["review_id"]
        self._create_main_quiz_passed(review_id, checkin_id)
        update_review_learning_status(review_id, LEARNING_STATUS_SELF_CHECK_REQUIRED)

        problem_id = upsert_luogu_problemset(
            {
                "pid": f"PY{int(time.time() * 1000)}",
                "title": "差分约束 confirm 题2",
                "difficulty": 3,
                "tags": ["差分约束"],
                "description": "desc",
                "inputFormat": "",
                "outputFormat": "",
                "samples": [],
                "limits": {"time": [1000], "memory": [128]},
            },
            classify_tag,
        )
        upsert_confirm_pool_entry(
            problem_id=problem_id,
            problem_url="https://www.luogu.com.cn/problem/PY",
            structure_type="difference_constraints",
            difficulty=3,
            bridge_note="不等式约束转有向边，矛盾即正环",
            status="usable",
        )

        confirm_response = self.client.post(
            f"/api/reviews/{review_id}/self-check",
            json={"status": "clear"},
            headers=auth_headers(self.student_id),
        )
        self.assertEqual(200, confirm_response.status_code)
        quiz_id = confirm_response.json()["quiz"]["quiz_id"]

        answer_response = self.client.post(
            f"/api/quizzes/{quiz_id}/answer",
            json={"answer_text": "A"},
            headers=auth_headers(self.student_id),
        )
        self.assertEqual(200, answer_response.status_code)
        self.assertTrue(answer_response.json()["is_correct"])
        self.assertEqual("resolved", answer_response.json()["learning_status"])
        self.assertEqual("resolved", answer_response.json()["next_state"])

    def test_self_check_guessed_goes_to_remedy_not_confirm(self):
        checkin_id = self._create_checkin()
        self._create_completed_review(checkin_id)
        detail = api_server.get_checkin_detail(checkin_id)
        review_id = detail["review"]["review_id"]
        self._create_main_quiz_passed(review_id, checkin_id)
        update_review_learning_status(review_id, LEARNING_STATUS_SELF_CHECK_REQUIRED)

        response = self.client.post(
            f"/api/reviews/{review_id}/self-check",
            json={"status": "guessed"},
            headers=auth_headers(self.student_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("remedy_available", response.json()["next_state"])


if __name__ == "__main__":
    unittest.main()
