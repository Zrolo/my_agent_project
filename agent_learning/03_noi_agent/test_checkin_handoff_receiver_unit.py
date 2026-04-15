"""Unit tests for the checkin handoff receiver (v0 contract).

Tests verify that handoff_payload flows correctly through the review pipeline
and produces the expected system/user prompt content for each risk_type.
"""
import unittest
from unittest.mock import patch


class CheckinHandoffReceiverPromptTests(unittest.TestCase):
    """Tests for prompt building with handoff_payload present."""

    def _ac_unclear_payload(self, problem_ref="P3128"):
        return {
            "handoff_type": "checkin_reflection",
            "source": "aichat",
            "risk_type": "ac_unclear_in_aichat",
            "problem_ref": problem_ref,
            "last_user_message": "我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。",
            "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。",
        }

    def _repeated_stuck_payload(self):
        return {
            "handoff_type": "checkin_reflection",
            "source": "aichat",
            "risk_type": "repeated_stuck_exit",
            "problem_ref": "",
            "last_user_message": "我还是说不清 check(mid) 到底检查什么。",
            "suggested_focus": "用小例子拆开当前卡住的桥，记录卡点和已尝试路径。",
        }

    def _build_system_prompt(self, handoff_payload=None, mode="independent_reflect"):
        from review_engine import _build_review_system_prompt
        return _build_review_system_prompt(mode=mode, handoff_payload=handoff_payload)

    _BOTTLENECK = "我不太清楚为什么这样建图，看了好几遍还是不明白每条边的容量怎么确定"

    def _build_user_prompt(self, handoff_payload=None):
        from review_engine import _build_review_user_prompt
        return _build_review_user_prompt(
            problem_title="P3128 最大流",
            oj_source="luogu",
            status_text="独立完成",
            bottleneck_text=self._BOTTLENECK,
            error_types=["建模理解"],
            handoff_payload=handoff_payload,
        )

    # --- system prompt ---

    def test_system_prompt_without_handoff_has_no_checkin_supplement(self):
        prompt = self._build_system_prompt()
        self.assertNotIn("source=checkin_reflection", prompt)
        self.assertNotIn("移交风险类型", prompt)

    def test_system_prompt_with_ac_unclear_payload_includes_extra_permissions(self):
        prompt = self._build_system_prompt(self._ac_unclear_payload())
        self.assertIn("source=checkin_reflection", prompt)
        self.assertIn("ac_unclear_in_aichat", prompt)
        self.assertIn("复盘已 AC 题目的关键桥", prompt)
        # extra permissions granted
        self.assertIn("3-5 节点", prompt)
        self.assertIn("确认学生已有代码中某一行的局部作用", prompt)

    def test_system_prompt_with_repeated_stuck_payload_includes_risk_type(self):
        prompt = self._build_system_prompt(self._repeated_stuck_payload())
        self.assertIn("repeated_stuck_exit", prompt)
        self.assertIn("用小例子拆开", prompt)

    def test_system_prompt_with_handoff_still_forbids_complete_dp_state(self):
        prompt = self._build_system_prompt(self._ac_unclear_payload())
        self.assertIn("完整 DP 状态定义", prompt)
        self.assertIn("禁止", prompt)

    def test_system_prompt_non_aichat_source_does_not_get_supplement(self):
        payload = {**self._ac_unclear_payload(), "source": "teacher"}
        prompt = self._build_system_prompt(payload)
        self.assertNotIn("source=checkin_reflection", prompt)

    # --- user prompt ---

    def test_user_prompt_without_handoff_has_no_handoff_lines(self):
        prompt = self._build_user_prompt()
        self.assertNotIn("移交背景", prompt)
        self.assertNotIn("移交前最后一条消息", prompt)
        self.assertNotIn("建议复盘焦点", prompt)

    def test_user_prompt_with_ac_unclear_includes_background_and_focus(self):
        prompt = self._build_user_prompt(self._ac_unclear_payload())
        self.assertIn("移交背景", prompt)
        self.assertIn("已 AC 但表示不理解", prompt)
        self.assertIn("移交前最后一条消息", prompt)
        self.assertIn("建议复盘焦点", prompt)
        self.assertIn("复盘已 AC 题目的关键桥", prompt)

    def test_user_prompt_with_repeated_stuck_includes_correct_background(self):
        prompt = self._build_user_prompt(self._repeated_stuck_payload())
        self.assertIn("反复卡住", prompt)
        self.assertIn("用小例子拆开", prompt)

    def test_user_prompt_last_message_is_truncated_to_200_chars(self):
        long_msg = "x" * 300
        payload = {**self._ac_unclear_payload(), "last_user_message": long_msg}
        prompt = self._build_user_prompt(payload)
        # Should appear with at most 200 chars
        self.assertIn("x" * 200, prompt)
        self.assertNotIn("x" * 201, prompt)

    # --- generate_review integration (mocked LLM) ---

    def _make_review_result(self):
        return {
            "ok": True,
            "kind": "success",
            "review": {
                "error_tags": ["建模理解"],
                "error_layer": "modeling",
                "error_layer_confidence": "medium",
                "core_design_subtags": [],
                "diagnosis": "不清楚为什么这样建图",
                "next_action": "回到原题验证建图依据",
                "suggested_topic": "最大流建图",
                "problem_focus": "如何把题目约束映射到容量",
                "main_block": "如何把题目约束映射到容量",
                "key_bridge": "每个约束对应一条有向边和容量",
                "visual_hint": "",
                "guided_walkthrough": "1. 列出约束 2. 找对应边 3. 验证容量",
                "try_now": "列出样例里第一条约束对应哪条边",
                "next_step": "列出样例里第一条约束对应哪条边",
                "transfer_signal": "题目限制能映射到容量时考虑最大流",
            },
            "telemetry": {},
        }

    def test_generate_review_passes_handoff_payload_to_llm_call(self):
        from review_engine import generate_review

        captured_messages = []

        def fake_call_llm(messages, chunk_callback=None):
            captured_messages.extend(messages)
            return True, '{"error_tags":[],"error_layer":"modeling","error_layer_confidence":"medium","core_design_subtags":[],"diagnosis":"x","next_action":"x","suggested_topic":"x","problem_focus":"x","main_block":"x","key_bridge":"x","visual_hint":"","guided_walkthrough":"x","try_now":"x","next_step":"x","transfer_signal":"x"}', {}

        with patch("review_engine._call_llm", side_effect=fake_call_llm):
            generate_review(
                problem_title="P3128 最大流",
                oj_source="luogu",
                completion_status="independent",
                bottleneck_text=self._BOTTLENECK,
                error_types=["建模理解"],
                handoff_payload=self._ac_unclear_payload(),
            )

        system_msg = next(m["content"] for m in captured_messages if m["role"] == "system")
        user_msg = next(m["content"] for m in captured_messages if m["role"] == "user")

        self.assertIn("ac_unclear_in_aichat", system_msg)
        self.assertIn("复盘已 AC 题目的关键桥", user_msg)

    def test_generate_review_without_handoff_has_no_handoff_content_in_prompts(self):
        from review_engine import generate_review

        captured_messages = []

        def fake_call_llm(messages, chunk_callback=None):
            captured_messages.extend(messages)
            return True, '{"error_tags":[],"error_layer":"modeling","error_layer_confidence":"medium","core_design_subtags":[],"diagnosis":"x","next_action":"x","suggested_topic":"x","problem_focus":"x","main_block":"x","key_bridge":"x","visual_hint":"","guided_walkthrough":"x","try_now":"x","next_step":"x","transfer_signal":"x"}', {}

        with patch("review_engine._call_llm", side_effect=fake_call_llm):
            generate_review(
                problem_title="P3128 最大流",
                oj_source="luogu",
                completion_status="independent",
                bottleneck_text=self._BOTTLENECK,
                error_types=["建模理解"],
            )

        system_msg = next(m["content"] for m in captured_messages if m["role"] == "system")
        user_msg = next(m["content"] for m in captured_messages if m["role"] == "user")

        self.assertNotIn("source=checkin_reflection", system_msg)
        self.assertNotIn("移交背景", user_msg)


class CheckinRequestHandoffFieldTests(unittest.TestCase):
    """Verify CheckinRequest model accepts handoff_payload."""

    def test_checkin_request_accepts_handoff_payload(self):
        # Just test the Pydantic model directly
        try:
            from api_server import CheckinRequest
        except Exception:
            self.skipTest("api_server import requires full environment")

        req = CheckinRequest(
            oj_source="luogu",
            completion_status="independent",
            bottleneck_text="我不太清楚为什么这样建图，超过15字",
            error_types=["建模理解"],
            handoff_payload={
                "handoff_type": "checkin_reflection",
                "source": "aichat",
                "risk_type": "ac_unclear_in_aichat",
                "problem_ref": "P3128",
                "last_user_message": "AC了但蒙的",
                "suggested_focus": "复盘已 AC 题目的关键桥，验证一个理解点。",
            },
        )
        self.assertIsNotNone(req.handoff_payload)
        self.assertEqual("ac_unclear_in_aichat", req.handoff_payload["risk_type"])

    def test_checkin_request_handoff_payload_defaults_to_none(self):
        try:
            from api_server import CheckinRequest
        except Exception:
            self.skipTest("api_server import requires full environment")

        req = CheckinRequest(
            oj_source="luogu",
            completion_status="independent",
            bottleneck_text="我不太清楚为什么这样建图，超过15字",
            error_types=["建模理解"],
        )
        self.assertIsNone(req.handoff_payload)


if __name__ == "__main__":
    unittest.main()
