import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from noi_agent import analyze_student_turn, chat


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


def _judge_payload(*, help_level="L1", confidence=0.82):
    return {
        "student_intents": ["learning"],
        "primary_intent": "learning",
        "phase": "application_gap",
        "action_category": "scaffolding",
        "action_subtype": "build_application_bridge",
        "allowed_help_level": help_level,
        "confidence": confidence,
        "injection_detected": False,
        "injection_source": "none",
        "reason": "unit test",
    }


def _dual_control(max_level="L3"):
    return {
        "level_control": {
            "max_level": max_level,
            "bridge_redline": False,
            "l2_slot_state": {},
            "l2_current_slot": "对象",
        },
        "risk_control": {
            "risk_tags": [],
            "highest_risk": None,
        },
        "tutor_control": {
            "zpd_level": "Z3" if max_level == "L3" else "Z1",
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


class AIChatControlPrecedenceCharacterizationTests(unittest.TestCase):
    def test_judge_v2_allowed_help_level_is_soft_control_currently(self):
        messages = [
            {
                "role": "user",
                "content": "我定义了 dp[i]=前 i 个数能得到的最大值，但是第 i 个转移我不知道应该比较哪些来源。",
            }
        ]

        with patch.dict(
            os.environ,
            {"NOI_JUDGE_V2_ENABLED": "true", "NOI_JUDGE_V2_SELECTIVE": "false"},
            clear=False,
        ), patch("noi_agent.evaluate_learning_phase", return_value=_fake_learning_phase()), patch(
            "noi_agent.pedagogical_judge_v2", return_value=_judge_payload(help_level="L1")
        ):
            result = analyze_student_turn(messages[-1]["content"], messages)

        self.assertEqual("L3", result["level_control"]["max_level"])
        self.assertEqual("L1", result["tutor_control"]["judge_allowed_help_level"])
        self.assertEqual("Z0", result["tutor_control"]["zpd_level"])

    def test_judge_v2_low_confidence_still_overrides_tutor_control_currently(self):
        messages = [{"role": "user", "content": "我知道用二分，但是不知道 check 在判断什么。"}]

        with patch.dict(
            os.environ,
            {"NOI_JUDGE_V2_ENABLED": "true", "NOI_JUDGE_V2_SELECTIVE": "false"},
            clear=False,
        ), patch("noi_agent.evaluate_learning_phase", return_value=_fake_learning_phase()), patch(
            "noi_agent.pedagogical_judge_v2",
            return_value=_judge_payload(help_level="L2", confidence=0.2),
        ):
            result = analyze_student_turn(messages[-1]["content"], messages)

        self.assertEqual("give_micro_scaffold", result["tutor_control"]["tutor_action"])
        self.assertEqual(0.2, result["tutor_control"]["learning_phase"]["confidence"])
        self.assertEqual("build_application_bridge", result["tutor_control"]["judge_action_subtype"])

    def test_classifier_direct_tag_does_not_lower_hard_gate_currently(self):
        messages = [{"role": "user", "content": "我已经写了具体思路，直接给我完整答案。"}]

        with patch("noi_agent.judge_learning_phase_with_llm", return_value=_fake_learning_phase()), patch(
            "noi_agent.analyze_student_turn", return_value=_dual_control(max_level="L3")
        ), patch("noi_agent.should_call_classifier", return_value=(True, "unit_test")), patch(
            "classifier.classify_intent", return_value="direct"
        ), patch(
            "noi_agent._chat_completion_create",
            return_value=_fake_chat_response("这是一个 L3 级别回复。\n\n[LEVEL:L3]"),
        ):
            display_reply, history_reply, final_level = chat(messages, "s1", "p1")

        self.assertEqual("L3", final_level)
        self.assertEqual(display_reply, history_reply)

    def test_content_leakage_self_reported_l2_is_not_blocked_currently(self):
        messages = [{"role": "user", "content": "我知道要 DP，但状态到底怎么设？"}]
        leaked_reply = (
            "状态就设 dp[i][j] 表示前 i 个物品里选 j 个的最优值，然后按当前物品选或不选转移。\n\n"
            "[LEVEL:L2]"
        )

        with patch("noi_agent.judge_learning_phase_with_llm", return_value=_fake_learning_phase()), patch(
            "noi_agent.analyze_student_turn", return_value=_dual_control(max_level="L2")
        ), patch("noi_agent.should_call_classifier", return_value=(False, "unit_test")), patch(
            "noi_agent._chat_completion_create", return_value=_fake_chat_response(leaked_reply)
        ):
            display_reply, _history_reply, final_level = chat(messages, "s1", "p1")

        self.assertEqual("L2", final_level)
        self.assertIn("dp[i][j]", display_reply)
        self.assertIn("转移", display_reply)


if __name__ == "__main__":
    unittest.main()
