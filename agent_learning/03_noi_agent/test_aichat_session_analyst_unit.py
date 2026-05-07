import os
import tempfile
from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server
import database


class TempDatabase:
    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_dir.name, "session_analyst.db")
        database.init_db()
        api_server.app.dependency_overrides.clear()
        api_server.app.dependency_overrides[api_server.require_teacher] = (
            lambda: {"user_id": "teacher_session_analyst", "role": "teacher"}
        )
        self.client = TestClient(api_server.app)
        return self

    def __exit__(self, exc_type, exc, tb):
        api_server.app.dependency_overrides.clear()
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()


def _seed_session(session_id="session_ana", student_id="stu_ana", problem_id="P16414"):
    database.record_aichat_conversation_message(
        student_id=student_id,
        student_username="student_ana",
        student_real_name="王五",
        problem_id=problem_id,
        session_id=session_id,
        role="student",
        content="我看懂异或条件了，但不知道怎么构造排列。",
    )
    database.record_aichat_conversation_message(
        student_id=student_id,
        student_username="student_ana",
        student_real_name="王五",
        problem_id=problem_id,
        session_id=session_id,
        role="ai_coach",
        content="先只看两个相邻数什么时候满足条件。",
    )
    database.record_aichat_turn_tag(
        student_id=student_id,
        student_username="student_ana",
        student_real_name="王五",
        problem_id=problem_id,
        session_id=session_id,
        turn_id="turn_1",
        role="student",
        primary_intent="learning",
        learning_issue="知道算法但不会落题",
        understanding_evidence=["表达题目目标"],
        missing_evidence=["核心构造关系"],
        risk_flags=["prompt_injection"],
        injection_detected=True,
        injection_source="problem",
        same_point_loop_signal=False,
        suggested_level="L2",
        confidence=0.88,
        short_reason="题面含AI指令",
    )
    database.upsert_aichat_session_summary(
        session_id=session_id,
        student_id=student_id,
        student_username="student_ana",
        student_real_name="王五",
        problem_id=problem_id,
        message_count=2,
        student_turn_count=1,
        ai_turn_count=1,
        has_understanding_evidence=True,
        understanding_evidence_types=["problem_goal"],
        same_gap_loop=False,
        latest_tutor_action="give_micro_scaffold",
        latest_rule_max_level="L2",
        last_student_message="我看懂异或条件了，但不知道怎么构造排列。",
    )


def test_record_and_get_aichat_session_analysis():
    with TempDatabase():
        analysis_id = database.upsert_aichat_session_analysis(
            session_id="session_ana",
            student_id="stu_ana",
            problem_id="P16414",
            status="completed",
            analysis_json={"main_issue": "知道算法但不会构造"},
            main_issue="知道算法但不会构造",
            teacher_next_action="让学生枚举合法相邻对。",
            needs_followup=True,
            model="deepseek-v4-pro",
            prompt_version="session_analyst_v1.0.0",
        )

        row = database.get_aichat_session_analysis("session_ana")

    assert analysis_id > 0
    assert row["status"] == "completed"
    assert row["main_issue"] == "知道算法但不会构造"
    assert row["analysis_json"]["main_issue"] == "知道算法但不会构造"
    assert row["needs_followup"] == 1


def test_teacher_session_analysis_endpoint_returns_processing_then_completed():
    with TempDatabase() as ctx:
        _seed_session()
        fake_analysis = {
            "main_issue": "知道算法但不会构造",
            "issue_detail": "学生能理解条件，但没有形成排列构造策略。",
            "understanding_evidence": ["表达题目目标"],
            "missing_evidence": ["核心构造关系"],
            "teacher_next_action": "让学生枚举合法相邻对。",
            "recommended_practice_type": "低难度构造题",
            "needs_followup": True,
            "confidence": 0.86,
        }
        with patch("api_server.analyze_aichat_session", return_value=fake_analysis):
            first = ctx.client.get("/api/teacher/aichat_session_analysis?session_id=session_ana")
            second = ctx.client.get("/api/teacher/aichat_session_analysis?session_id=session_ana")

        assert first.status_code == 200
        assert first.json()["status"] in {"processing", "completed"}
        assert second.status_code == 200
        assert second.json()["status"] == "completed"
        assert second.json()["analysis"]["main_issue"] == "知道算法但不会构造"


def test_teacher_session_analysis_retry_regenerates_existing_analysis():
    with TempDatabase() as ctx:
        _seed_session()
        database.upsert_aichat_session_analysis(
            session_id="session_ana",
            student_id="stu_ana",
            problem_id="P16414",
            status="completed",
            analysis_json={"main_issue": "旧判断"},
            main_issue="旧判断",
            teacher_next_action="旧建议",
            needs_followup=False,
            model="deepseek-v4-pro",
            prompt_version="session_analyst_v1.0.0",
        )
        fake_analysis = {
            "main_issue": "重新判断后发现卡在构造策略",
            "issue_detail": "学生能理解条件，但没有形成排列构造策略。",
            "understanding_evidence": ["表达题目目标"],
            "missing_evidence": ["核心构造关系"],
            "teacher_next_action": "让学生枚举合法相邻对。",
            "recommended_practice_type": "低难度构造题",
            "needs_followup": True,
            "confidence": 0.9,
        }

        with patch.dict(api_server.os.environ, {"NOI_SESSION_ANALYST_SYNC": "true"}, clear=False), \
             patch("api_server.analyze_aichat_session", return_value=fake_analysis):
            response = ctx.client.post(
                "/api/teacher/aichat_session_analysis/retry",
                json={"session_id": "session_ana"},
            )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "completed"
        assert payload["analysis"]["main_issue"] == "重新判断后发现卡在构造策略"


def test_teacher_session_analysis_health_counts_statuses():
    with TempDatabase() as ctx:
        for index, status in enumerate(["completed", "processing", "failed"], start=1):
            database.upsert_aichat_session_analysis(
                session_id=f"session_health_{index}",
                student_id=f"stu_{index}",
                problem_id="P16414",
                status=status,
                analysis_json={"main_issue": status},
                main_issue=status,
                teacher_next_action="",
                needs_followup=False,
                model="deepseek-v4-pro",
                prompt_version="session_analyst_v1.0.0",
                failure_reason="provider_timeout" if status == "failed" else "",
            )

        response = ctx.client.get("/api/teacher/aichat_session_analysis/health?days=7")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 3
    assert payload["status_counts"]["completed"] == 1
    assert payload["status_counts"]["processing"] == 1
    assert payload["status_counts"]["failed"] == 1
    assert payload["failure_rate"] == 1 / 3
