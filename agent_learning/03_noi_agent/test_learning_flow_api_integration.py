import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
import review_engine
from auth import create_token
from database import (
    LEARNING_STATUS_SELF_CHECK_REQUIRED,
    create_pending_review,
    create_review,
    create_review_quiz,
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


class LearningFlowApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(api_server.app)
        self.student_id = f"flow_api_{int(time.time() * 1000)}"
        self.headers = auth_headers(self.student_id)

    def _create_checkin_via_api(self, bottleneck_text: str, submission_result: str = "not_submitted") -> int:
        payload = {
            "problem_url": "https://example.com/problem",
            "problem_title": "链路联调题",
            "oj_source": "luogu",
            "completion_status": "independent",
            "problem_context": "每个活动都必须同时满足时间窗口和指定地点两个条件。",
            "submission_result": submission_result,
            "bottleneck_text": bottleneck_text,
            "error_types": ["模型转化"],
            "reflection": "这里像并列约束。",
            "problem_tags": ["差分约束"],
            "chat_context_summary": "",
            "student_code": "",
        }
        with patch.object(api_server, "_start_review_generation_job", return_value=None):
            response = self.client.post("/api/checkins", json=payload, headers=self.headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual("pending", response.json()["review_status"])
        return response.json()["checkin_id"]

    def _complete_review(self, checkin_id: int, transfer_signal: str) -> int:
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
        detail = self.client.get(f"/api/checkins/{checkin_id}", headers=self.headers)
        self.assertEqual(200, detail.status_code)
        self.assertTrue(detail.json()["review"])
        return detail.json()["review"]["review_id"]

    def _create_passed_main_quiz(self, review_id: int, checkin_id: int):
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

    def test_a_route_from_checkin_to_remedy_resolve(self):
        checkin_id = self._create_checkin_via_api(
            bottleneck_text="我不会做这题，已经卡住了。我试着把条件改成不等式，但不知道每条边该怎么统一方向。",
        )
        review_id = self._complete_review(
            checkin_id,
            transfer_signal="当约束能转成不等式链，且目标是判断是否存在矛盾时，要警惕这种图上关系建模。",
        )

        quiz_response = self.client.post(
            f"/api/reviews/{review_id}/quiz/generate",
            headers=self.headers,
        )
        self.assertEqual(200, quiz_response.status_code)
        self.assertEqual("remedy_available", quiz_response.json()["next_state"])

        remedy_response = self.client.post(
            f"/api/reviews/{review_id}/remedy",
            json={"action_type": "dynamic_bridge_help"},
            headers=self.headers,
        )
        self.assertEqual(200, remedy_response.status_code)
        self.assertEqual("remedy_in_progress", remedy_response.json()["learning_status"])

        resolve_response = self.client.post(
            f"/api/reviews/{review_id}/remedy/resolve",
            json={"status": "resolved"},
            headers=self.headers,
        )
        self.assertEqual(200, resolve_response.status_code)
        self.assertEqual("resolved", resolve_response.json()["learning_status"])

    def test_c_route_from_checkin_to_confirm_answer_resolved(self):
        checkin_id = self._create_checkin_via_api(
            bottleneck_text="我知道这里像并列约束，但还是卡住，不知道该怎么把条件整理成统一关系。",
        )
        review_id = self._complete_review(
            checkin_id,
            transfer_signal="当约束能转成不等式链，且目标是判断是否存在矛盾时，要警惕这种图上关系建模。",
        )
        self._create_passed_main_quiz(review_id, checkin_id)
        update_review_learning_status(review_id, LEARNING_STATUS_SELF_CHECK_REQUIRED)

        problem_id = upsert_luogu_problemset(
            {
                "pid": f"PZ{int(time.time() * 1000)}",
                "title": "差分约束 confirm 集成题",
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
            problem_url="https://www.luogu.com.cn/problem/PZ",
            structure_type="difference_constraints",
            difficulty=3,
            bridge_note="不等式约束转有向边，矛盾即正环",
            status="usable",
        )

        confirm_response = self.client.post(
            f"/api/reviews/{review_id}/self-check",
            json={"status": "clear"},
            headers=self.headers,
        )
        self.assertEqual(200, confirm_response.status_code)
        self.assertEqual("confirm_quiz", confirm_response.json()["next_state"])
        self.assertEqual("fixed_pool", confirm_response.json()["quiz"]["meta"]["confirm_mode"])

        quiz_id = confirm_response.json()["quiz"]["quiz_id"]
        answer_response = self.client.post(
            f"/api/quizzes/{quiz_id}/answer",
            json={"answer_text": "A"},
            headers=self.headers,
        )
        self.assertEqual(200, answer_response.status_code)
        self.assertTrue(answer_response.json()["is_correct"])
        self.assertEqual("resolved", answer_response.json()["next_state"])


if __name__ == "__main__":
    unittest.main()
