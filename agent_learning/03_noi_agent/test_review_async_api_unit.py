import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
from auth import create_token
from database import (
    REVIEW_STATUS_COMPLETED,
    REVIEW_STATUS_PENDING,
    create_checkin,
    create_pending_review,
    create_review,
    get_review_by_checkin,
    get_review_manual_review,
    get_review_events_for_checkin,
    mark_review_failed,
    mark_review_pending,
)


def auth_headers(student_id: str) -> dict:
    token = create_token(student_id, "student")
    return {"Authorization": f"Bearer {token}"}


def teacher_headers(teacher_id: str = "teacher") -> dict:
    token = create_token(teacher_id, "teacher")
    return {"Authorization": f"Bearer {token}"}


class ReviewAsyncApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api_server.app)
        self.owner_id = f"student_owner_{int(time.time() * 1000)}"
        self.other_id = f"student_other_{int(time.time() * 1000)}"

    def _create_checkin(self, student_id: str, title: str = "测试题") -> int:
        return create_checkin(
            student_id=student_id,
            problem_url="https://example.com/problem",
            problem_title=title,
            oj_source="other",
            completion_status="unfinished",
            bottleneck_text="我总把时间条件和地点条件看成主次关系，不知道是不是要同时满足。",
            error_types=["模型转化"],
            reflection="这里像是并列约束，不是主次条件。",
            problem_context="每个活动都必须同时满足时间窗口和指定地点两个条件。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="wa",
            student_code="",
            session_id=f"checkin_test_{int(time.time() * 1000)}",
        )

    def test_student_checkin_detail_requires_owner(self):
        checkin_id = self._create_checkin(self.owner_id, "owner-checkin")
        create_pending_review(checkin_id, self.owner_id)

        response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.other_id),
        )

        self.assertEqual(404, response.status_code)

    def test_retry_only_allowed_when_failed(self):
        checkin_id = self._create_checkin(self.owner_id, "retry-checkin")
        create_pending_review(checkin_id, self.owner_id)

        pending_response = self.client.post(
            f"/api/checkins/{checkin_id}/review/retry",
            headers=auth_headers(self.owner_id),
        )
        self.assertEqual(400, pending_response.status_code)

        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=[],
            diagnosis="ok",
            next_action="ok",
            suggested_topic="ok",
        )
        response = self.client.post(
            f"/api/checkins/{checkin_id}/review/retry",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("无需重试", response.json()["detail"])

        mark_review_failed(checkin_id, "boom")
        with patch.object(api_server, "_start_review_generation_job", return_value=None) as mocked_retry:
            failed_response = self.client.post(
                f"/api/checkins/{checkin_id}/review/retry",
                headers=auth_headers(self.owner_id),
            )
        self.assertEqual(200, failed_response.status_code)
        self.assertEqual(REVIEW_STATUS_PENDING, failed_response.json()["review_status"])
        mocked_retry.assert_called_once()

    def test_student_detail_hides_review_last_error(self):
        checkin_id = self._create_checkin(self.owner_id, "error-hidden")
        create_pending_review(checkin_id, self.owner_id)
        mark_review_pending(checkin_id, "private error")

        response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertIsNone(response.json()["review_last_error"])

    def test_create_checkin_returns_pending_without_waiting(self):
        payload = {
            "problem_url": "https://example.com/new-problem",
            "problem_title": "新建打卡",
            "oj_source": "other",
            "completion_status": "unfinished",
            "problem_context": "每个活动都必须同时满足时间窗口和指定地点两个条件。",
            "submission_result": "wa",
            "bottleneck_text": "我总把时间条件和地点条件当成主次关系，不知道是不是要同时满足。",
            "error_types": ["模型转化"],
            "reflection": "这里应该是并列约束。",
            "problem_tags": [],
            "chat_context_summary": "",
            "student_code": "",
        }

        with patch.object(api_server, "_start_review_generation_job", return_value=None):
            response = self.client.post(
                "/api/checkins",
                json=payload,
                headers=auth_headers(self.owner_id),
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual(REVIEW_STATUS_PENDING, response.json()["review_status"])
        self.assertTrue(response.json()["session_id"].startswith("checkin_"))
        self.assertEqual("failed_verdict", response.json()["review_mode"])
        self.assertEqual("failure_diagnosis", response.json()["review_family"])

    def test_student_detail_returns_review_mode_and_family(self):
        checkin_id = self._create_checkin(self.owner_id, "mode-visible")
        create_pending_review(checkin_id, self.owner_id)

        response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json()["session_id"].startswith("checkin_"))
        self.assertEqual("failed_verdict", response.json()["review_mode"])
        self.assertEqual("failure_diagnosis", response.json()["review_family"])

    def test_student_checkin_list_returns_review_mode_and_family(self):
        checkin_id = self._create_checkin(self.owner_id, "list-mode-visible")
        create_pending_review(checkin_id, self.owner_id)

        response = self.client.get(
            "/api/checkins/me",
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        item = next(row for row in response.json()["checkins"] if row["id"] == checkin_id)
        self.assertTrue(item["session_id"].startswith("checkin_"))
        self.assertEqual("failed_verdict", item["review_mode"])
        self.assertEqual("failure_diagnosis", item["review_family"])

    def test_review_event_endpoint_records_review_feedback(self):
        checkin_id = self._create_checkin(self.owner_id, "event-checkin")
        create_pending_review(checkin_id, self.owner_id)

        detail_response = self.client.get(
            f"/api/checkins/{checkin_id}",
            headers=auth_headers(self.owner_id),
        )
        session_id = detail_response.json()["session_id"]

        response = self.client.post(
            "/api/review-events",
            json={
                "checkin_id": checkin_id,
                "session_id": session_id,
                "event_name": "review_feedback_submitted",
                "student_feedback": "confused",
                "bad_reason": "no_next_step",
                "followup_clicked": True,
                "followup_question_count": 1,
            },
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.json()["status"])
        events = get_review_events_for_checkin(checkin_id)
        self.assertEqual(1, len(events))
        self.assertEqual("review_feedback_submitted", events[0]["event_name"])
        self.assertEqual(session_id, events[0]["session_id"])
        self.assertEqual("failed_verdict", events[0]["review_mode"])
        self.assertEqual("failure_diagnosis", events[0]["review_family"])

    def test_review_event_endpoint_records_review_request_submitted(self):
        payload = {
            "problem_url": "https://example.com/request-problem",
            "problem_title": "请求事件打卡",
            "oj_source": "other",
            "completion_status": "independent",
            "problem_context": "有 n 件纪念品，每组最多放两件且总重量不能超过 w，要求分组数最少。",
            "submission_result": "not_submitted",
            "bottleneck_text": "我会排序后双指针，但说不清为什么最重的尽量和最轻的一组不会吃亏。",
            "error_types": ["知道算法但不知道怎么用"],
            "reflection": "应该是贪心，但我不会解释。",
            "problem_tags": [],
            "chat_context_summary": "",
            "student_code": "",
        }

        with patch.object(api_server, "_start_review_generation_job", return_value=None):
            create_response = self.client.post(
                "/api/checkins",
                json=payload,
                headers=auth_headers(self.owner_id),
            )

        body = create_response.json()
        response = self.client.post(
            "/api/review-events",
            json={
                "checkin_id": body["checkin_id"],
                "session_id": body["session_id"],
                "event_name": "review_request_submitted",
                "problem_id": "P1094",
                "problem_title": "P1094 [NOIP2007 普及组] 纪念品分组",
                "has_code": False,
                "problem_context_length": len(payload["problem_context"]),
                "bottleneck_text_length": len(payload["bottleneck_text"]),
                "latency_ms": 0,
            },
            headers=auth_headers(self.owner_id),
        )

        self.assertEqual(200, response.status_code)
        events = get_review_events_for_checkin(body["checkin_id"])
        self.assertEqual("review_request_submitted", events[-1]["event_name"])
        self.assertEqual("independent_reflect", events[-1]["review_mode"])
        self.assertEqual("success_reflection", events[-1]["review_family"])
        self.assertEqual("P1094", events[-1]["payload"]["problem_id"])
        self.assertEqual(False, events[-1]["payload"]["has_code"])

    def test_teacher_can_list_manual_review_samples(self):
        checkin_id = self._create_checkin(self.owner_id, "manual-sample")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
        )

        response = self.client.get(
            "/api/teacher/review-samples?limit=5",
            headers=teacher_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json()["samples"])
        sample = next(item for item in response.json()["samples"] if item["checkin_id"] == checkin_id)
        self.assertEqual("failed_verdict", sample["review_mode"])
        self.assertEqual("failure_diagnosis", sample["review_family"])
        self.assertIsNone(sample["manual_review"])

    def test_teacher_can_submit_manual_review(self):
        checkin_id = self._create_checkin(self.owner_id, "manual-submit")
        create_review(
            checkin_id=checkin_id,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
        )

        samples_response = self.client.get(
            "/api/teacher/review-samples?limit=50",
            headers=teacher_headers(),
        )
        review_id = next(item for item in samples_response.json()["samples"] if item["checkin_id"] == checkin_id)["review_id"]

        response = self.client.post(
            f"/api/teacher/reviews/{review_id}/manual-review",
            json={
                "mode_correct": "correct",
                "review_grounded": "grounded",
                "student_can_move_next": "yes",
                "notes": "这条可以作为正样本保留",
            },
            headers=teacher_headers(),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.json()["status"])

        manual_review = get_review_manual_review(review_id)
        self.assertIsNotNone(manual_review)
        self.assertEqual("correct", manual_review["mode_correct"])
        self.assertEqual("grounded", manual_review["review_grounded"])
        self.assertEqual("yes", manual_review["student_can_move_next"])

    def test_teacher_stats_include_manual_review_rates(self):
        teacher_id = f"teacher_stats_{int(time.time() * 1000)}"
        first_checkin = self._create_checkin(self.owner_id, "manual-stats-1")
        second_checkin = self._create_checkin(self.owner_id, "manual-stats-2")
        create_review(
            checkin_id=first_checkin,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
        )
        create_review(
            checkin_id=second_checkin,
            student_id=self.owner_id,
            error_tags=["题意理解"],
            diagnosis="诊断",
            next_action="行动",
            suggested_topic="专题",
        )
        first_review = get_review_by_checkin(first_checkin)["id"]
        second_review = get_review_by_checkin(second_checkin)["id"]

        self.client.post(
            f"/api/teacher/reviews/{first_review}/manual-review",
            json={
                "mode_correct": "correct",
                "review_grounded": "grounded",
                "student_can_move_next": "yes",
                "notes": "第一条合格",
            },
            headers=teacher_headers(teacher_id),
        )
        self.client.post(
            f"/api/teacher/reviews/{second_review}/manual-review",
            json={
                "mode_correct": "incorrect",
                "review_grounded": "mixed",
                "student_can_move_next": "no",
                "notes": "第二条需要回看",
            },
            headers=teacher_headers(teacher_id),
        )

        response = self.client.get(
            "/api/teacher/stats?days=30",
            headers=teacher_headers(teacher_id),
        )

        self.assertEqual(200, response.status_code)
        manual_stats = response.json()["manual_review_stats"]
        self.assertEqual(2, manual_stats["reviewed_count"])
        self.assertEqual(0.5, manual_stats["mode_correct_rate"])
        self.assertEqual(0.5, manual_stats["grounded_rate"])
        self.assertEqual(0.5, manual_stats["student_can_move_next_rate"])

    def test_teacher_stats_include_manual_review_breakdown_by_mode_and_family(self):
        teacher_id = f"teacher_breakdown_{int(time.time() * 1000)}"

        failed_checkin = create_checkin(
            student_id=self.owner_id,
            problem_url="https://example.com/failed",
            problem_title="失败题",
            oj_source="other",
            completion_status="unfinished",
            bottleneck_text="我知道是双指针，但窗口更新顺序总写乱。",
            error_types=["实现细节"],
            reflection="我怀疑 while 里的左右端点更新顺序错了。",
            problem_context="给定正整数 m，要求输出所有和等于 m 的连续正整数区间。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="wa",
            student_code="",
            session_id=f"failed_stats_{int(time.time() * 1000)}",
        )
        success_checkin = create_checkin(
            student_id=self.owner_id,
            problem_url="https://example.com/independent",
            problem_title="理解题",
            oj_source="other",
            completion_status="independent",
            bottleneck_text="我会 BFS 求最短步数，但说不清为什么第一次到达就是最短。",
            error_types=["知道算法但不知道怎么用"],
            reflection="应该跟层次扩展有关。",
            problem_context="在 n×m 的棋盘上，马从给定起点出发，要求输出到每个格子的最少步数。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="not_submitted",
            student_code="",
            session_id=f"success_stats_{int(time.time() * 1000)}",
        )
        editorial_checkin = create_checkin(
            student_id=self.owner_id,
            problem_url="https://example.com/editorial",
            problem_title="题解题",
            oj_source="other",
            completion_status="editorial",
            bottleneck_text="题解说这是树形 DP，但我不明白为什么状态只记子树里保留多少条边。",
            error_types=["模型转化"],
            reflection="看懂了代码，但状态定义还是不稳。",
            problem_context="给定一棵有边权的树，要求删去一些边后只保留 q 条边，使留下的苹果总数最大。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="not_submitted",
            student_code="",
            session_id=f"editorial_stats_{int(time.time() * 1000)}",
        )

        create_review(failed_checkin, self.owner_id, ["实现细节"], "诊断", "行动", "专题")
        create_review(success_checkin, self.owner_id, ["知道算法但不知道怎么用"], "诊断", "行动", "专题")
        create_review(editorial_checkin, self.owner_id, ["模型转化"], "诊断", "行动", "专题")

        failed_review = get_review_by_checkin(failed_checkin)["id"]
        success_review = get_review_by_checkin(success_checkin)["id"]
        editorial_review = get_review_by_checkin(editorial_checkin)["id"]

        self.client.post(
            f"/api/teacher/reviews/{failed_review}/manual-review",
            json={
                "mode_correct": "correct",
                "review_grounded": "grounded",
                "student_can_move_next": "yes",
                "notes": "failed ok",
            },
            headers=teacher_headers(teacher_id),
        )
        self.client.post(
            f"/api/teacher/reviews/{success_review}/manual-review",
            json={
                "mode_correct": "correct",
                "review_grounded": "grounded",
                "student_can_move_next": "unsure",
                "notes": "success ok",
            },
            headers=teacher_headers(teacher_id),
        )
        self.client.post(
            f"/api/teacher/reviews/{editorial_review}/manual-review",
            json={
                "mode_correct": "incorrect",
                "review_grounded": "mixed",
                "student_can_move_next": "no",
                "notes": "editorial needs work",
            },
            headers=teacher_headers(teacher_id),
        )

        response = self.client.get("/api/teacher/stats?days=30", headers=teacher_headers(teacher_id))

        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertIn("manual_review_stats_by_mode", body)
        self.assertIn("manual_review_stats_by_family", body)
        self.assertEqual(1, body["manual_review_stats_by_mode"]["failed_verdict"]["reviewed_count"])
        self.assertEqual(1.0, body["manual_review_stats_by_mode"]["failed_verdict"]["mode_correct_rate"])
        self.assertEqual(1, body["manual_review_stats_by_mode"]["independent_reflect"]["reviewed_count"])
        self.assertEqual(1.0, body["manual_review_stats_by_mode"]["independent_reflect"]["grounded_rate"])
        self.assertEqual(2, body["manual_review_stats_by_family"]["failure_diagnosis"]["reviewed_count"])
        self.assertEqual(0.5, body["manual_review_stats_by_family"]["failure_diagnosis"]["mode_correct_rate"])
        self.assertEqual(0.5, body["manual_review_stats_by_family"]["failure_diagnosis"]["grounded_rate"])
        self.assertEqual(1, body["manual_review_stats_by_family"]["success_reflection"]["reviewed_count"])


if __name__ == "__main__":
    unittest.main()
