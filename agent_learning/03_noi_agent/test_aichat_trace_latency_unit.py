import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from noi_agent import chat


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


class AIChatTraceLatencyTests(unittest.TestCase):
    def test_chat_writes_trace_jsonl_when_enabled(self):
        messages = [{"role": "user", "content": "我知道要 DP，但状态怎么设？"}]

        with tempfile.TemporaryDirectory() as tmpdir:
            trace_file = os.path.join(tmpdir, "aichat_trace.jsonl")
            with patch.dict(
                os.environ,
                {"NOI_AICHAT_TRACE": "1", "NOI_AICHAT_TRACE_FILE": trace_file},
                clear=False,
            ), patch("noi_agent.judge_learning_phase_with_llm", return_value=_fake_learning_phase()), patch(
                "noi_agent.analyze_student_turn", return_value=_dual_control()
            ), patch("noi_agent.should_call_classifier", return_value=(False, "unit_test")), patch(
                "noi_agent.build_system_prompt", return_value="system prompt for trace"
            ), patch(
                "noi_agent._chat_completion_create",
                return_value=_fake_chat_response("你先说说状态里至少要保留哪两个信息。\n\n[LEVEL:L2]"),
            ):
                display_reply, _history_reply, final_level = chat(messages, "student-123", "P1001")

            self.assertEqual("L2", final_level)
            self.assertIn("至少要保留", display_reply)

            with open(trace_file, "r", encoding="utf-8") as f:
                rows = [json.loads(line) for line in f if line.strip()]

        self.assertEqual(1, len(rows))
        trace = rows[0]
        self.assertIn("trace_id", trace)
        self.assertEqual("P1001", trace["problem_id"])
        self.assertNotIn("student-123", json.dumps(trace, ensure_ascii=False))
        self.assertEqual("standard_llm", trace["route_name"])
        self.assertEqual("L2", trace["final_level"])
        self.assertEqual(2, trace["llm_call_count"])
        self.assertIn("main_llm", trace["model_names"])
        self.assertIn("system_prompt", trace["prompt_hashes"])
        for key in (
            "legacy_judge_latency_ms",
            "rules_latency_ms",
            "classifier_latency_ms",
            "main_llm_latency_ms",
            "hard_gate_latency_ms",
            "output_guard_latency_ms",
            "total_latency_ms",
        ):
            self.assertIsInstance(trace[key], int)


if __name__ == "__main__":
    unittest.main()
