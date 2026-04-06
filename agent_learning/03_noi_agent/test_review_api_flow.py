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


if __name__ == "__main__":
    test_validate_bottleneck_allows_specific_descriptions()
    test_checkin_survives_review_exception()
    test_student_cannot_impersonate_other_student()
    print("review api flow tests passed")
