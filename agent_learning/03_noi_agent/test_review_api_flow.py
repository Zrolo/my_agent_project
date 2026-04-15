import os
import tempfile

from fastapi.testclient import TestClient

import api_server
import database
from review_engine import validate_bottleneck


def _setup_temp_app():
    fd, path = tempfile.mkstemp(prefix="noi_review_flow_", suffix=".db")
    os.close(fd)
    database.DB_PATH = path
    api_server.init_db()
    api_server.app.dependency_overrides.clear()
    return TestClient(api_server.app)


def test_validate_bottleneck_allows_specific_descriptions():
    ok, _ = validate_bottleneck("我知道是DP，但是不知道该把什么作为状态来表示。")
    assert ok

    ok, _ = validate_bottleneck("我知道是背包，但状态设计一直不稳定，不知道该记录什么。")
    assert ok


def test_checkin_survives_review_exception():
    client = _setup_temp_app()
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )
    api_server.generate_review = lambda **kwargs: (_ for _ in ()).throw(RuntimeError("boom"))

    response = client.post(
        "/api/checkins",
        json={
            "problem_url": "https://example.com/problem/P1001",
            "problem_title": "P1001",
            "oj_source": "luogu",
            "completion_status": "unfinished",
            "problem_context": "给定若干状态转移关系，要求求出最终最优值，并注意边界情况。",
            "submission_result": "unknown",
            "bottleneck_text": "我尝试了几种转移方式，但总是漏情况，自己也没定位出来具体是哪一步。",
            "error_types": ["状态转移"],
            "reflection": None,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["review_status"] == "pending"
    assert payload["review"] is None

    my_checkins = client.get("/api/checkins/me").json()["checkins"]
    assert len(my_checkins) == 1
    assert my_checkins[0]["problem_context"]
    assert my_checkins[0]["review_status"] == "pending"
    assert "RuntimeError" in (my_checkins[0]["review_last_error"] or "")


def test_student_cannot_impersonate_other_student():
    client = _setup_temp_app()
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )
    api_server.app.dependency_overrides[api_server.get_current_user] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )

    chat_response = client.post(
        "/chat",
        json={
            "student_id": "student_b",
            "problem_id": "P1001",
            "message": "这题怎么做",
            "session_id": "sess_test",
        },
    )
    assert chat_response.status_code == 403

    quota_response = client.get("/quota/student_b/P1001")
    assert quota_response.status_code == 403


def test_chat_endpoint_passes_current_problem_context_to_agent():
    client = _setup_temp_app()
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )
    captured = {}
    original_chat = api_server.chat

    def fake_chat(messages, student_id, problem_id):
        captured["messages"] = [dict(message) for message in messages]
        captured["student_id"] = student_id
        captured["problem_id"] = problem_id
        return "先看路径上的点怎么被计数。", "先看路径上的点怎么被计数。", "L1"

    api_server.chat = fake_chat
    try:
        response = client.post(
            "/chat",
            json={
                "student_id": "student_a",
                "problem_id": "P3128",
                "message": "我不知道这里为什么要用树上差分。",
                "session_id": "sess_context",
                "problem_title": "P3128 [USACO15DEC] Max Flow P",
                "problem_url": "https://www.luogu.com.cn/problem/P3128",
                "problem_context": "给一棵树和多条运输路径，要求统计经过次数最多的点。",
                "student_code": "diff[u]++; diff[v]++; diff[lca]-=2;",
            },
        )
    finally:
        api_server.chat = original_chat

    assert response.status_code == 200
    assert captured["student_id"] == "student_a"
    assert captured["problem_id"] == "P3128"
    last_user_message = [message for message in captured["messages"] if message["role"] == "user"][-1]["content"]
    assert "当前题目上下文" in last_user_message
    assert "P3128 [USACO15DEC] Max Flow P" in last_user_message
    assert "多条运输路径" in last_user_message
    assert "diff[u]++" in last_user_message
    assert "我不知道这里为什么要用树上差分。" in last_user_message


def test_chat_endpoint_auto_imports_luogu_context_when_only_problem_ref_is_provided():
    client = _setup_temp_app()
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )
    captured = {}
    original_chat = api_server.chat
    original_fetch = api_server.fetch_luogu_problem

    def fake_fetch(raw_url):
        captured["fetch_ref"] = raw_url
        return {
            "problem_url": "https://www.luogu.com.cn/problem/P3128",
            "problem_title": "P3128 [USACO15DEC] Max Flow P",
            "problem_context": "给一棵树和多条运输路径，要求统计经过次数最多的点。",
            "problem_tags": ["树上差分", "LCA"],
            "oj_source": "luogu",
        }

    def fake_chat(messages, student_id, problem_id):
        captured["messages"] = [dict(message) for message in messages]
        captured["student_id"] = student_id
        captured["problem_id"] = problem_id
        return "先把一条路径对端点和 LCA 的贡献写出来。", "先把一条路径对端点和 LCA 的贡献写出来。", "L1"

    api_server.fetch_luogu_problem = fake_fetch
    api_server.chat = fake_chat
    try:
        response = client.post(
            "/chat",
            json={
                "student_id": "student_a",
                "problem_id": "P3128",
                "message": "这题我只知道是 LCA，但不知道怎么统计。",
                "session_id": "sess_auto_import",
            },
        )
    finally:
        api_server.chat = original_chat
        api_server.fetch_luogu_problem = original_fetch

    assert response.status_code == 200
    assert captured["fetch_ref"] == "https://www.luogu.com.cn/problem/P3128"
    last_user_message = [message for message in captured["messages"] if message["role"] == "user"][-1]["content"]
    assert "P3128 [USACO15DEC] Max Flow P" in last_user_message
    assert "多条运输路径" in last_user_message
    assert "这题我只知道是 LCA" in last_user_message


if __name__ == "__main__":
    test_validate_bottleneck_allows_specific_descriptions()
    test_checkin_survives_review_exception()
    test_student_cannot_impersonate_other_student()
    test_chat_endpoint_passes_current_problem_context_to_agent()
    test_chat_endpoint_auto_imports_luogu_context_when_only_problem_ref_is_provided()
    print("review api flow tests passed")
