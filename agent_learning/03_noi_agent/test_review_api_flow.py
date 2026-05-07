import os
import tempfile
import time

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

    my_checkins = []
    last_error = ""
    for _ in range(20):
        my_checkins = client.get("/api/checkins/me").json()["checkins"]
        last_error = my_checkins[0]["review_last_error"] or "" if my_checkins else ""
        if "RuntimeError" in last_error:
            break
        time.sleep(0.05)
    assert len(my_checkins) == 1
    assert my_checkins[0]["problem_context"]
    assert my_checkins[0]["review_status"] in {"pending", "failed"}
    assert "RuntimeError" in last_error


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


def test_jmfes_problem_import_persists_problem_and_ai_tags():
    client = _setup_temp_app()
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )
    original_fetch = api_server.fetch_jmfes_problem
    original_generate_tags = api_server.generate_problem_tags_with_ai

    def fake_fetch(raw_url):
        return {
            "problem_url": "http://oj.jmfes.com:8888/p/401",
            "problem_pid": "401",
            "problem_title": "校内题 401 路径统计",
            "problem_context": "给一棵树和若干路径，统计每个点被路径经过的次数。",
            "problem_tags": [],
            "oj_source": "jmfes",
        }

    def fake_generate_tags(**kwargs):
        assert kwargs["oj_source"] == "jmfes"
        assert "路径" in kwargs["problem_context"]
        return ["树", "路径统计", "差分"]

    api_server.fetch_jmfes_problem = fake_fetch
    api_server.generate_problem_tags_with_ai = fake_generate_tags
    try:
        response = client.post("/api/problem-import", json={"url": "http://172.21.60.30:8888/p/401?tid=x"})
    finally:
        api_server.fetch_jmfes_problem = original_fetch
        api_server.generate_problem_tags_with_ai = original_generate_tags

    assert response.status_code == 200
    payload = response.json()
    assert payload["oj_source"] == "jmfes"
    assert payload["problem_tags"] == ["树", "路径统计", "差分"]

    problem = database.get_problem_by_source_ref("jmfes", "401")
    assert problem is not None
    assert problem["title"] == "校内题 401 路径统计"
    assert database.get_problem_tags(problem["problem_id"], tag_type="ai") == ["差分", "树", "路径统计"]


def test_problem_closure_start_records_bottleneck_event():
    client = _setup_temp_app()
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )
    original_generate = api_server.generate_understanding_check

    def fake_generate_understanding_check(**kwargs):
        return {
            "status": "ok",
            "question": "给一个三点链，写出从最远叶子往回走 1 步到哪里。",
            "target_focus": "二分 check 中从最远叶子回退 D 步",
            "bottleneck_type": "process_tracing",
            "quiz_format": "trace_one_step",
            "evidence": "学生说知道直径但不知道 check 怎么写",
        }

    api_server.generate_understanding_check = fake_generate_understanding_check
    try:
        response = client.post(
            "/api/chat/problem-closure/start",
            json={
                "problem_id": "P9999",
                "session_id": "sess_bottleneck",
                "problem_title": "树上核心城市",
                "problem_context": "选择连通核心城市，使最大距离最小。",
                "chat_model_provider": "deepseek",
            },
        )
    finally:
        api_server.generate_understanding_check = original_generate

    assert response.status_code == 200
    payload = response.json()
    assert payload["bottleneck_type"] == "process_tracing"
    events = database.list_problem_bottleneck_events(problem_ref="P9999")
    assert len(events) == 1
    assert events[0]["student_id"] == "student_a"
    assert events[0]["bottleneck_type"] == "process_tracing"
    assert events[0]["quiz_format"] == "trace_one_step"
    assert events[0]["source_event"] == "closure_quiz"
    assert events[0]["result_status"] == "generated"


if __name__ == "__main__":
    test_validate_bottleneck_allows_specific_descriptions()
    test_checkin_survives_review_exception()
    test_student_cannot_impersonate_other_student()
    test_chat_endpoint_passes_current_problem_context_to_agent()
    test_chat_endpoint_auto_imports_luogu_context_when_only_problem_ref_is_provided()
    test_jmfes_problem_import_persists_problem_and_ai_tags()
    test_problem_closure_start_records_bottleneck_event()
    print("review api flow tests passed")
