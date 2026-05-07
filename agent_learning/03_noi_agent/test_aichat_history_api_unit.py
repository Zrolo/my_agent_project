import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
from auth import create_token
from database import init_db, record_aichat_message, upsert_aichat_problem_memory


def auth_headers(student_id: str) -> dict:
    token = create_token(student_id, "student")
    return {"Authorization": f"Bearer {token}"}


class AIChatHistoryApiTests(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(api_server.app)
        suffix = int(time.time() * 1000)
        self.student_id = f"history_student_{suffix}"
        self.problem_id = "P405::history"
        self.session_id = f"history_session_{suffix}"
        api_server.session_histories.clear()

    def test_history_endpoint_returns_current_problem_session_messages_in_chat_order(self):
        record_aichat_message(self.student_id, self.problem_id, self.session_id, "user", "这题为什么要二分？")
        record_aichat_message(self.student_id, self.problem_id, self.session_id, "assistant", "先看直接枚举要试多少次。")
        record_aichat_message(self.student_id, "P406::other", self.session_id, "user", "别的题")

        response = self.client.get(
            f"/api/chat/history?problem_id={self.problem_id}&session_id={self.session_id}",
            headers=auth_headers(self.student_id),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [
                {"role": "user", "content": "这题为什么要二分？"},
                {"role": "assistant", "content": "先看直接枚举要试多少次。"},
            ],
            response.json()["messages"],
        )

    def test_chat_endpoint_restores_database_history_before_next_turn(self):
        record_aichat_message(self.student_id, self.problem_id, self.session_id, "user", "我觉得可以直接枚举。")
        record_aichat_message(self.student_id, self.problem_id, self.session_id, "assistant", "先估一下枚举次数。")
        captured_messages = []

        def fake_chat(messages, student_id, problem_id):
            captured_messages.extend(messages)
            return "我们继续看这一轮。", "我们继续看这一轮。", "L2"

        with patch.object(api_server, "chat", side_effect=fake_chat):
            response = self.client.post(
                "/chat",
                headers=auth_headers(self.student_id),
                json={
                    "student_id": self.student_id,
                    "problem_id": self.problem_id,
                    "session_id": self.session_id,
                    "message": "那我现在该看哪里？",
                    "problem_title": "测试题",
                    "problem_context": "给定很多数据，需要找最小不满意度。",
                },
            )

        self.assertEqual(200, response.status_code)
        contents = [item["content"] for item in captured_messages]
        self.assertIn("我觉得可以直接枚举。", contents)
        self.assertIn("先估一下枚举次数。", contents)
        self.assertTrue(any("那我现在该看哪里？" in content for content in contents))

    def test_chat_endpoint_injects_same_problem_memory_without_full_other_session_history(self):
        upsert_aichat_problem_memory(
            student_id=self.student_id,
            problem_id=self.problem_id,
            summary="当前卡点：知道要二分，但没有说清 check 在维护什么。\n下一步建议：用一个 3 个对象的小例子对齐判断关系。",
            source_session_id="old_session",
        )
        record_aichat_message(
            self.student_id,
            self.problem_id,
            "old_session",
            "user",
            "旧会话里很长的原始对话不应该被整段塞进新 session。",
        )
        captured_messages = []

        def fake_chat(messages, student_id, problem_id):
            captured_messages.extend(messages)
            return "我们接着摘要里的卡点走。", "我们接着摘要里的卡点走。", "L2"

        new_session_id = f"new_session_{int(time.time() * 1000)}"
        with patch.object(api_server, "chat", side_effect=fake_chat):
            response = self.client.post(
                "/chat",
                headers=auth_headers(self.student_id),
                json={
                    "student_id": self.student_id,
                    "problem_id": self.problem_id,
                    "session_id": new_session_id,
                    "message": "我还是不知道 check 怎么写。",
                    "problem_title": "测试题",
                    "problem_context": "给定很多数据，需要找最小不满意度。",
                },
            )

        self.assertEqual(200, response.status_code)
        joined = "\n".join(item["content"] for item in captured_messages)
        self.assertIn("同题短摘要记忆", joined)
        self.assertIn("知道要二分", joined)
        self.assertNotIn("旧会话里很长的原始对话", joined)
