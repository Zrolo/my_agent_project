import tempfile
from types import SimpleNamespace
from unittest.mock import patch

import database
import noi_agent
from database import (
    get_aichat_session_summary,
    init_db,
    list_aichat_conversation_messages,
    list_aichat_judge_shadow_events,
)
from noi_agent import analyze_student_turn, chat


class TempDatabase:
    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = f"{self.temp_dir.name}/noi_agent_test.db"
        init_db()
        return self

    def __exit__(self, exc_type, exc, tb):
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()


def _fake_chat_response(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_chat_writes_conversation_message():
    with TempDatabase():
        with patch("noi_agent.judge_learning_phase_with_llm", return_value=None), \
             patch(
                 "noi_agent._chat_completion_create",
                 return_value=_fake_chat_response("先看题目让你求的量是什么。\n\n[LEVEL:L2]"),
             ):
            chat(
                [{"role": "user", "content": "P1119 这题我不知道怎么做"}],
                student_id="student_a",
                problem_id="P1119",
                chat_model_provider="deepseek_flash",
            )

        rows = list_aichat_conversation_messages(
            student_id="student_a",
            problem_id="P1119",
            limit=10,
            ascending=True,
        )

        assert rows[0]["role"] == "student"
        assert rows[0]["content"] == "P1119 这题我不知道怎么做"
        assert rows[0]["student_username"] == "student_a"
        assert rows[0]["student_real_name"] == "student_a"
        assert rows[0]["consent_for_research"] == 1


def test_ai_reply_writes_conversation_message():
    with TempDatabase():
        with patch("noi_agent.judge_learning_phase_with_llm", return_value=None), \
             patch(
                 "noi_agent._chat_completion_create",
                 return_value=_fake_chat_response("先把村庄当点、道路当边。\n\n[LEVEL:L2]"),
             ):
            chat(
                [{"role": "user", "content": "P1119 样例我会，后面不会"}],
                student_id="student_b",
                problem_id="P1119",
                chat_model_provider="deepseek_flash",
            )

        rows = list_aichat_conversation_messages(
            student_id="student_b",
            problem_id="P1119",
            limit=10,
            ascending=True,
        )

        assert [row["role"] for row in rows] == ["student", "ai_coach"]
        assert "村庄当点" in rows[1]["content"]
        assert rows[1]["model_provider"] == "deepseek_flash"


def test_judge_shadow_event_includes_agreement_fields():
    fake_judge = {
        "student_intents": ["learning"],
        "primary_intent": "learning",
        "phase": "application_gap",
        "action_category": "scaffolding",
        "action_subtype": "build_application_bridge",
        "allowed_help_level": "L2",
        "confidence": 0.9,
        "injection_detected": False,
        "injection_source": "none",
        "reason": "mock",
    }

    with TempDatabase():
        with patch.dict(
            noi_agent.os.environ,
            {"NOI_JUDGE_V2_SHADOW": "true", "NOI_JUDGE_V2_SELECTIVE": "false"},
            clear=False,
        ), patch("noi_agent.pedagogical_judge_v2", return_value=fake_judge):
            analyze_student_turn(
                "我知道用 Floyd 但不会用。",
                [{"role": "user", "content": "我知道用 Floyd 但不会用。"}],
                student_id="student_c",
                problem_id="P1119",
                session_id="session_c",
            )

        events = list_aichat_judge_shadow_events(student_id="student_c", limit=5)
        assert len(events) == 1
        event = events[0]
        assert event["judge_action_subtype"] == "build_application_bridge"
        assert "agreement_action_exact" in event
        assert "agreement_action_family" in event
        assert "agreement_help_level" in event
        assert "agreement_would_override" in event
        assert event["consent_for_research"] == 1


def test_session_summary_updates_on_progress():
    with TempDatabase():
        messages = [
            {"role": "user", "content": "P1119 题目要求按时间查询最短路"},
            {"role": "assistant", "content": "你觉得时间会影响哪些点能用？"},
            {"role": "user", "content": "村庄当点，道路当边，修好后才能作为中转点，用 Floyd 更新距离"},
        ]
        analyze_student_turn(
            messages[-1]["content"],
            messages,
            student_id="student_d",
            problem_id="P1119",
            session_id="session_progress",
        )

        summary = get_aichat_session_summary("session_progress")
        assert summary is not None
        assert summary["student_id"] == "student_d"
        assert summary["has_understanding_evidence"] == 1
        assert summary["same_gap_loop"] == 0
        assert summary["student_turn_count"] == 2


def test_session_summary_detects_loop():
    with TempDatabase():
        messages = [
            {"role": "user", "content": "我不会"},
            {"role": "assistant", "content": "你怀疑是哪一行错？"},
            {"role": "user", "content": "全都有问题"},
            {"role": "assistant", "content": "哪个样例没过？"},
            {"role": "user", "content": "都过不了"},
        ]
        analyze_student_turn(
            messages[-1]["content"],
            messages,
            student_id="student_e",
            problem_id="P0001",
            session_id="session_loop",
        )

        summary = get_aichat_session_summary("session_loop")
        assert summary is not None
        assert summary["same_gap_loop"] == 1
        assert summary["same_gap_loop_type"] in {
            "stuck_loop",
            "evidence_seeking_loop",
            "frustration_loop",
        }
