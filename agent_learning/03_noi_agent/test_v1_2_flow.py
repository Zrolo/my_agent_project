#!/usr/bin/env python3
"""
v1.2 flow regression script

目标：
1. 用可重复的 deterministic stub 跑通 v1.2 的关键桥梁路径
2. 验证 self-check / confirm / remedy / bridge_path 的状态机
3. 给后续页面联调提供稳定的后端回归基线
"""

import os
import tempfile
from typing import Any

from fastapi.testclient import TestClient

import api_server
import database

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

RESULTS: list[bool] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append(condition)
    status = PASS if condition else FAIL
    suffix = f" [{detail}]" if detail else ""
    print(f"{status} {name}{suffix}")


def _stub_review(**kwargs: Any) -> dict:
    return {
        "ok": True,
        "review": {
            "error_tags": ["状态设计"],
            "error_layer": "core_design",
            "error_layer_confidence": "high",
            "core_design_subtags": ["state_design"],
            "diagnosis": "这道题主要卡在状态含义没有先站稳。",
            "next_action": "先只练状态设计，不要急着写完整转移。",
            "suggested_topic": "状态设计与对象含义",
            "main_block": "你不是不会写，而是还没先把这一步里的对象含义说清楚。",
            "key_bridge": "先确认这一步里每个对象各表示什么，再决定后面的写法。",
            "next_step": "先只写出这一维表示什么，不要急着写完整代码。",
            "transfer_signal": "下次题目一上来就有很多量时，先想谁是对象、谁是限制。",
        },
        "review_quality_flags": [],
    }


def _quiz_payload(role: str, previous_quiz: dict | None = None) -> dict:
    if role == api_server.QUIZ_ROLE_MAIN:
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "这一步最该先确定什么？",
            "options": [
                "先确认当前对象表示什么",
                "先把变量名改短",
                "先把样例答案记下来",
                "先把输出格式写死",
            ],
            "correct_answer": "先确认当前对象表示什么",
            "explanation": "对象含义没站稳，后面每一步都会漂。",
            "target_bridge": "先确认对象表示什么",
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if role == api_server.QUIZ_ROLE_FOLLOWUP:
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果只盯住这一小步，下面哪种说法才真正对？",
            "options": [
                {"value": "A", "label": "先弄清每个对象各表示什么"},
                {"value": "B", "label": "先把代码模板抄下来再回头补对象含义"},
                {"value": "C", "label": "先猜最后答案大概有多大"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这个说法把对象含义和代码模板的顺序弄反了。先把对象表示什么站稳，后面才不会越写越乱。",
                "C": "这个说法把注意力放到了答案大小上，却没有先把对象含义说清楚，所以还没抓住当前桥梁。",
            },
            "explanation": "先把对象含义站稳，才不会后面越写越乱。",
            "target_bridge": "先确认对象表示什么",
            "difficulty_level": "followup",
            "meta": {"difficulty_level": "followup", "micro_hint": "先别写转移，只看对象。"},
        }
    if role == api_server.QUIZ_ROLE_CONFIRM:
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果把这一步换到一个更小的场景里，你现在最该先看什么？",
            "options": [
                "先看每个对象在这个小场景里分别表示什么",
                "先把代码模板抄下来",
                "先猜答案大概会多大",
                "先决定变量名缩写",
            ],
            "correct_answer": "先看每个对象在这个小场景里分别表示什么",
            "explanation": "换个场景后还能先盯对象，说明你真的抓到这一步了。",
            "target_bridge": "先确认对象表示什么",
            "difficulty_level": "confirm",
            "meta": {
                "difficulty_level": "confirm",
                "confirm_focus": "small_scenario_transfer",
            },
        }
    if role == api_server.QUIZ_ROLE_REMEDY:
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果我们把这一步再拆小一点，下面哪种做法更对？",
            "options": [
                {"value": "A", "label": "先看对象含义，再决定后面的写法"},
                {"value": "B", "label": "先把完整代码写完，再回头补对象含义"},
                {"value": "C", "label": "先背样例里的过程，再猜对象关系"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这个做法还是在先写代码。补救阶段更要先把对象含义站稳，不然完整代码只会把错误写得更大。",
                "C": "这个做法把样例过程当成了对象关系的替代品。当前这一步仍然要先看清对象各表示什么。",
            },
            "explanation": "补救阶段更要先站稳对象，不要急着求完整答案。",
            "target_bridge": "先确认对象表示什么",
            "difficulty_level": "easier",
            "meta": {"difficulty_level": "easier"},
        }
    raise AssertionError(f"unexpected role: {role}")


def _stub_generate_bridge_quiz(review_context: dict, previous_quiz: dict | None = None, quiz_role: str = "main") -> dict:
    return _quiz_payload(quiz_role, previous_quiz)


def _stub_generate_remedy_explanation(review_context: dict, action_type: str) -> dict:
    return {
        "remedy_type": "explain",
        "remedy_action": action_type,
        "remedy_text": "先别急着整题往后推，我们只盯这一小步，把对象和关系重新站稳。",
        "micro_action": "现在先只写一句：这一步里每个对象各表示什么。",
    }


def _setup_temp_app() -> TestClient:
    fd, path = tempfile.mkstemp(prefix="noi_v12_flow_", suffix=".db")
    os.close(fd)
    database.DB_PATH = path
    api_server.init_db()
    api_server.app.dependency_overrides.clear()
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )
    api_server.app.dependency_overrides[api_server.require_teacher] = (
        lambda: {"user_id": "teacher", "role": "teacher"}
    )
    api_server.generate_review = _stub_review
    api_server.generate_bridge_quiz = _stub_generate_bridge_quiz
    api_server.generate_remedy_explanation = _stub_generate_remedy_explanation
    return TestClient(api_server.app)


def _create_checkin_and_review(client: TestClient, title: str) -> tuple[int, int]:
    response = client.post(
        "/api/checkins",
        json={
            "problem_url": "https://www.luogu.com.cn/problem/P1001",
            "problem_title": title,
            "oj_source": "luogu",
            "completion_status": "independent",
            "problem_context": "题目给出若干对象之间的关系，要求判断每一步先看什么。",
            "submission_result": "wa",
            "bottleneck_text": "我知道大概方向，但这一步为什么要先看对象含义，我还说不太清楚，所以总是写着写着就乱了。",
            "error_types": ["状态设计"],
            "reflection": "测试流程",
            "student_code": "int main(){return 0;}",
        },
    )
    assert response.status_code == 200, response.text
    checkin_id = response.json()["checkin_id"]
    history = client.get("/api/checkins/me?limit=50").json()["checkins"]
    item = next(row for row in history if row["id"] == checkin_id)
    return checkin_id, item["review_id"]


def _start_main_quiz(client: TestClient, review_id: int) -> dict:
    response = client.post(f"/api/reviews/{review_id}/quiz/generate")
    assert response.status_code == 200, response.text
    return response.json()["quiz"]


def _answer_quiz(client: TestClient, quiz_id: int, answer: str) -> dict:
    response = client.post(f"/api/quizzes/{quiz_id}/answer", json={"answer_text": answer})
    assert response.status_code == 200, response.text
    return response.json()


def _quiz_correct_answer(quiz_id: int) -> str:
    quiz = database.get_quiz_by_id(quiz_id)
    assert quiz is not None
    return quiz["correct_answer"]


def _self_check(client: TestClient, review_id: int, status: str) -> dict:
    response = client.post(f"/api/reviews/{review_id}/self-check", json={"status": status})
    assert response.status_code == 200, response.text
    return response.json()


def _trigger_remedy_and_resolve(client: TestClient, review_id: int, status: str) -> None:
    response = client.post(
        f"/api/reviews/{review_id}/remedy",
        json={"action_type": "rephrase"},
    )
    assert response.status_code == 200, response.text
    resolve = client.post(
        f"/api/reviews/{review_id}/remedy/resolve",
        json={"status": status},
    )
    assert resolve.status_code == 200, resolve.text


def _latest_checkin_item(client: TestClient, checkin_id: int) -> dict:
    history = client.get("/api/checkins/me?limit=50").json()["checkins"]
    return next(row for row in history if row["id"] == checkin_id)


def test_main_clear(client: TestClient) -> None:
    checkin_id, review_id = _create_checkin_and_review(client, "main_clear")
    quiz = _start_main_quiz(client, review_id)
    result = _answer_quiz(client, quiz["quiz_id"], _quiz_correct_answer(quiz["quiz_id"]))
    check("main_clear enters self_check_required", result["next_state"] == "self_check_required")
    _self_check(client, review_id, "clear")
    item = _latest_checkin_item(client, checkin_id)
    check("main_clear resolved", item["review_learning_status"] == "resolved")
    check("main_clear bridge_path", item["review_bridge_path"] == "main_clear", item.get("review_bridge_path"))
    check("main_clear self-check stored", item["review_understanding_self_check"] == "clear")


def test_main_guessed_confirm(client: TestClient) -> None:
    checkin_id, review_id = _create_checkin_and_review(client, "main_guessed_confirm")
    quiz = _start_main_quiz(client, review_id)
    _answer_quiz(client, quiz["quiz_id"], _quiz_correct_answer(quiz["quiz_id"]))
    guessed = _self_check(client, review_id, "guessed")
    check("guessed creates confirm quiz", guessed["next_state"] == "confirm_quiz")
    confirm_quiz = guessed["quiz"]
    check("confirm difficulty level", confirm_quiz["meta"].get("difficulty_level") == "confirm")
    check("confirm focus present", bool(confirm_quiz["meta"].get("confirm_focus")))
    _answer_quiz(client, confirm_quiz["quiz_id"], _quiz_correct_answer(confirm_quiz["quiz_id"]))
    item = _latest_checkin_item(client, checkin_id)
    check("main_guessed_confirm resolved", item["review_learning_status"] == "resolved")
    check("main_guessed_confirm path", item["review_bridge_path"] == "main_guessed_confirm", item.get("review_bridge_path"))


def test_main_guessed_remedy(client: TestClient) -> None:
    checkin_id, review_id = _create_checkin_and_review(client, "main_guessed_remedy")
    quiz = _start_main_quiz(client, review_id)
    _answer_quiz(client, quiz["quiz_id"], _quiz_correct_answer(quiz["quiz_id"]))
    guessed = _self_check(client, review_id, "guessed")
    confirm_quiz = guessed["quiz"]
    wrong_answer = "__wrong__"
    response = _answer_quiz(client, confirm_quiz["quiz_id"], wrong_answer)
    check("confirm wrong enters remedy", response["next_state"] == "remedy_available")
    _trigger_remedy_and_resolve(client, review_id, "resolved")
    item = _latest_checkin_item(client, checkin_id)
    check("main_guessed_remedy resolved", item["review_learning_status"] == "resolved")
    check("main_guessed_remedy path", item["review_bridge_path"] == "main_guessed_remedy", item.get("review_bridge_path"))


def test_main_confused_remedy(client: TestClient) -> None:
    checkin_id, review_id = _create_checkin_and_review(client, "main_confused_remedy")
    quiz = _start_main_quiz(client, review_id)
    _answer_quiz(client, quiz["quiz_id"], _quiz_correct_answer(quiz["quiz_id"]))
    response = _self_check(client, review_id, "confused")
    check("confused enters remedy", response["next_state"] == "remedy_available")
    _trigger_remedy_and_resolve(client, review_id, "resolved")
    item = _latest_checkin_item(client, checkin_id)
    check("main_confused_remedy resolved", item["review_learning_status"] == "resolved")
    check("main_confused_remedy path", item["review_bridge_path"] == "main_confused_remedy", item.get("review_bridge_path"))


def test_followup_correct(client: TestClient) -> None:
    checkin_id, review_id = _create_checkin_and_review(client, "followup_correct")
    quiz = _start_main_quiz(client, review_id)
    response = _answer_quiz(client, quiz["quiz_id"], "__wrong__")
    check("main wrong creates followup", response["next_state"] == "followup_quiz")
    followup_quiz = response["quiz"]
    _answer_quiz(client, followup_quiz["quiz_id"], _quiz_correct_answer(followup_quiz["quiz_id"]))
    item = _latest_checkin_item(client, checkin_id)
    check("followup_correct resolved", item["review_learning_status"] == "resolved")
    check("followup_correct path", item["review_bridge_path"] == "followup_correct", item.get("review_bridge_path"))
    check("followup_correct has no self-check", item["review_understanding_self_check"] is None)


def test_followup_remedy(client: TestClient) -> None:
    checkin_id, review_id = _create_checkin_and_review(client, "followup_remedy")
    quiz = _start_main_quiz(client, review_id)
    response = _answer_quiz(client, quiz["quiz_id"], "__wrong__")
    followup_quiz = response["quiz"]
    _answer_quiz(client, followup_quiz["quiz_id"], "__wrong__")
    _trigger_remedy_and_resolve(client, review_id, "resolved")
    item = _latest_checkin_item(client, checkin_id)
    check("followup_remedy resolved", item["review_learning_status"] == "resolved")
    check("followup_remedy path", item["review_bridge_path"] == "followup_remedy", item.get("review_bridge_path"))


def test_teacher_view_fields(client: TestClient) -> None:
    response = client.get("/api/teacher/checkins?limit=100&offset=0")
    assert response.status_code == 200, response.text
    items = response.json()["checkins"]
    found = [item for item in items if item["problem_title"] in {
        "main_clear",
        "main_guessed_confirm",
        "main_guessed_remedy",
        "main_confused_remedy",
        "followup_correct",
        "followup_remedy",
    }]
    check("teacher sees all regression cases", len(found) == 6, str(len(found)))
    sample = next(item for item in found if item["problem_title"] == "main_guessed_confirm")
    check("teacher payload includes self-check", sample["review_understanding_self_check"] == "guessed")
    check("teacher payload includes bridge_path", sample["review_bridge_path"] == "main_guessed_confirm")


def main() -> None:
    client = _setup_temp_app()

    test_main_clear(client)
    test_main_guessed_confirm(client)
    test_main_guessed_remedy(client)
    test_main_confused_remedy(client)
    test_followup_correct(client)
    test_followup_remedy(client)
    test_teacher_view_fields(client)

    print("-" * 40)
    passed = sum(1 for ok in RESULTS if ok)
    total = len(RESULTS)
    print(f"v1.2 flow regression: {passed}/{total} passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
