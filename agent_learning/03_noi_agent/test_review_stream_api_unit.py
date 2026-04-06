import time
import unittest

from fastapi.testclient import TestClient

import api_server
from auth import create_token
from database import create_checkin, create_pending_review, mark_review_failed


def auth_headers(student_id: str) -> dict:
    token = create_token(student_id, "student")
    return {"Authorization": f"Bearer {token}"}


class ReviewStreamApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api_server.app)
        self.owner_id = f"stream_owner_{int(time.time() * 1000)}"
        self.other_id = f"stream_other_{int(time.time() * 1000)}"
        if hasattr(api_server, "_checkin_runtime_status"):
            api_server._checkin_runtime_status.clear()

    def _create_checkin(self, student_id: str, title: str = "流式测试题") -> int:
        return create_checkin(
            student_id=student_id,
            problem_url="https://example.com/problem",
            problem_title=title,
            oj_source="other",
            completion_status="unfinished",
            bottleneck_text="我知道大方向，但不知道关键一步为什么成立。",
            error_types=["模型转化"],
            reflection="这里像关键一步没证明出来。",
            problem_context="题目要求在一个结构里找到最优策略，并解释关键一步为什么可行。",
            problem_tags=[],
            chat_context_summary="",
            submission_result="wa",
            student_code="",
        )

    def _stream_once(self, checkin_id: int, student_id: str) -> str:
        with self.client.stream(
            "GET",
            f"/api/checkins/{checkin_id}/stream?once=1",
            headers=auth_headers(student_id),
        ) as response:
            self.assertEqual(200, response.status_code)
            chunks = []
            for line in response.iter_lines():
                if not line:
                    continue
                chunks.append(line)
        return "\n".join(chunks)

    def test_stream_requires_owner(self):
        checkin_id = self._create_checkin(self.owner_id)
        create_pending_review(checkin_id, self.owner_id)

        response = self.client.get(
            f"/api/checkins/{checkin_id}/stream",
            headers=auth_headers(self.other_id),
        )

        self.assertEqual(404, response.status_code)

    def test_stream_emits_pending_status_event(self):
        checkin_id = self._create_checkin(self.owner_id)
        create_pending_review(checkin_id, self.owner_id)
        api_server.update_checkin_runtime_status(
            checkin_id,
            "llm_start",
            "pending",
            "正在调用模型",
        )

        payload = self._stream_once(checkin_id, self.owner_id)

        self.assertIn("event: status", payload)
        self.assertIn('"phase":"llm_start"', payload)
        self.assertIn('"review_status":"pending"', payload)

    def test_stream_emits_error_event_when_failed(self):
        checkin_id = self._create_checkin(self.owner_id)
        create_pending_review(checkin_id, self.owner_id)
        mark_review_failed(checkin_id, "boom")
        api_server.update_checkin_runtime_status(
            checkin_id,
            "failed",
            "failed",
            "复盘生成失败，可稍后重试",
        )

        payload = self._stream_once(checkin_id, self.owner_id)

        self.assertIn("event: error", payload)
        self.assertIn('"phase":"failed"', payload)
        self.assertIn('"review_status":"failed"', payload)

    def test_stream_falls_back_to_queued_when_runtime_state_missing(self):
        checkin_id = self._create_checkin(self.owner_id)
        create_pending_review(checkin_id, self.owner_id)

        payload = self._stream_once(checkin_id, self.owner_id)

        self.assertIn("event: status", payload)
        self.assertIn('"phase":"queued"', payload)
        self.assertIn('"review_status":"pending"', payload)

    def test_stream_emits_review_chunk_event_when_draft_exists(self):
        checkin_id = self._create_checkin(self.owner_id)
        create_pending_review(checkin_id, self.owner_id)
        api_server.update_checkin_runtime_status(
            checkin_id,
            "llm_start",
            "pending",
            "正在调用模型",
            draft_review={
                "main_block": "你已经知道和树的直径有关，但还没说明公式为什么成立。",
                "key_bridge": "关键是先说明核心城市覆盖直径中段后，最远距离为什么只由两端剩余长度决定。",
            },
        )

        payload = self._stream_once(checkin_id, self.owner_id)

        self.assertIn("event: review_chunk", payload)
        self.assertIn('"draft_review"', payload)
        self.assertIn('"main_block"', payload)


if __name__ == "__main__":
    unittest.main()
