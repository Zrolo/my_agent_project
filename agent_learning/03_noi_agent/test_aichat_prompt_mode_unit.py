import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
from auth import create_token
from database import init_db
from noi_agent import chat


def auth_headers(student_id: str) -> dict:
    token = create_token(student_id, "student")
    return {"Authorization": f"Bearer {token}"}


def _fake_chat_response(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def _fake_learning_phase():
    return {
        "student_state": "forming_strategy",
        "phase": "forming_strategy",
        "recommended_action": "summarize_and_scaffold",
        "question_budget": 0,
        "can_show_verification": False,
        "code_help_level": "none",
        "confidence": 0.8,
        "evidence": "unit test",
    }


def _dual_control(max_level="L2"):
    return {
        "level_control": {
            "max_level": max_level,
            "bridge_redline": False,
            "l2_slot_state": {},
            "l2_current_slot": "对象",
            "reason_tags": ["bridge_attempt"],
        },
        "risk_control": {
            "risk_tags": ["bridge_attempt"],
            "highest_risk": "bridge_attempt",
        },
        "tutor_control": {
            "zpd_level": "Z2",
            "scaffold_stage": 2,
            "tutor_action": "point_to_specific_gap",
            "allowed_help": "unit test",
            "forbidden": ["完整题解", "完整代码"],
            "edf_required": True,
            "question_streak": 0,
            "latest_made_progress": False,
            "learning_phase": _fake_learning_phase(),
        },
    }


class AIChatPromptModeUnitTests(unittest.TestCase):
    def setUp(self):
        init_db()
        api_server.app.dependency_overrides.clear()
        api_server.session_histories.clear()
        self.client = TestClient(api_server.app)
        suffix = int(time.time() * 1000)
        self.student_id = f"prompt_mode_student_{suffix}"

    def test_chat_endpoint_passes_prompt_mode_to_agent_and_response(self):
        captured = {}

        def fake_chat(
            messages,
            student_id,
            problem_id,
            chat_model_provider=None,
            aichat_prompt_mode=None,
        ):
            captured["chat_model_provider"] = chat_model_provider
            captured["aichat_prompt_mode"] = aichat_prompt_mode
            return "我们用一个小例子先拆这一步。", "我们用一个小例子先拆这一步。", "L2"

        with patch.object(api_server, "chat", side_effect=fake_chat):
            response = self.client.post(
                "/chat",
                headers=auth_headers(self.student_id),
                json={
                    "student_id": self.student_id,
                    "problem_id": "P405",
                    "session_id": "sess_prompt_mode",
                    "message": "lazy 到底表示还没做什么？",
                    "problem_title": "测试题",
                    "chat_model_provider": "deepseek_flash",
                    "aichat_prompt_mode": "dbox_inspired_clean",
                },
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual("deepseek_flash", captured["chat_model_provider"])
        self.assertEqual("dbox_inspired_clean", captured["aichat_prompt_mode"])
        self.assertEqual("dbox_inspired_clean", response.json()["aichat_prompt_mode"])
        self.assertEqual("教练引导", response.json()["aichat_prompt_mode_label"])

    def test_dbox_prompt_mode_uses_direct_decomposition_prompt(self):
        messages = [{"role": "user", "content": "我知道要 DP，但状态怎么设？"}]
        captured = {}

        def fake_chat_completion_create(system_prompt, messages, provider_id=None):
            captured["system_prompt"] = system_prompt
            return _fake_chat_response("你先说说状态里至少要保留哪两个信息。\n\n[LEVEL:L2]")

        with patch("noi_agent.judge_learning_phase_with_llm", return_value=_fake_learning_phase()) as phase_judge, patch(
            "noi_agent.analyze_student_turn", return_value=_dual_control()
        ), patch("noi_agent.should_call_classifier", return_value=(False, "unit_test")), patch(
            "noi_agent._chat_completion_create", side_effect=fake_chat_completion_create
        ):
            display_reply, _history_reply, final_level = chat(
                messages,
                "student-123",
                "P1001",
                chat_model_provider="deepseek_flash",
                aichat_prompt_mode="dbox_inspired_clean",
            )

        self.assertEqual("L2", final_level)
        self.assertIn("至少要保留", display_reply)
        phase_judge.assert_not_called()
        self.assertIn("分解式教练", captured["system_prompt"])
        self.assertIn("step-tree-style decomposition", captured["system_prompt"])
        self.assertIn("不要直接补完整关键桥", captured["system_prompt"])
        self.assertIn("学生可见回复不要写出内部模式名", captured["system_prompt"])


if __name__ == "__main__":
    unittest.main()
