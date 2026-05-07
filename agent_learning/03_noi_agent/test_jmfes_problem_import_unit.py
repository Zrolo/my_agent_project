from unittest.mock import patch

from fastapi.testclient import TestClient

import api_server


def test_normalize_jmfes_problem_url_maps_internal_ip_and_strips_tid():
    assert (
        api_server.normalize_jmfes_problem_url(
            "http://172.21.60.30:8888/p/401?tid=67e653847d1c645ed6d42876"
        )
        == "http://oj.jmfes.com:8888/p/401"
    )


def test_fetch_jmfes_problem_marks_oj_source_as_jmfes():
    with patch.object(
        api_server.requests,
        "get",
        return_value=type(
            "Resp",
            (),
            {
                "text": '<div class="problem-content"><h1 class="section__title">和为给定数</h1><div class="section__body typo" data-fragment-id="problem-description"><p>题面正文不少于十个字。</p></div></div><div class="medium-3 columns">',
                "raise_for_status": lambda self: None,
            },
        )(),
    ):
        payload = api_server.fetch_jmfes_problem("http://oj.jmfes.com:8888/p/401")

    assert payload["oj_source"] == "jmfes"


def test_problem_import_accepts_internal_jmfes_problem_url():
    client = TestClient(api_server.app)
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )

    with patch.object(
        api_server,
        "fetch_jmfes_problem",
        return_value={
            "problem_url": "http://oj.jmfes.com:8888/p/401",
            "problem_pid": "401",
            "problem_title": "和为给定数",
            "problem_context": "题面正文",
            "problem_tags": [],
            "oj_source": "other",
        },
    ) as mocked_fetch:
        response = client.post(
            "/api/problem-import",
            json={"url": "http://172.21.60.30:8888/p/401?tid=67e653847d1c645ed6d42876"},
        )

    api_server.app.dependency_overrides.clear()
    assert response.status_code == 200, response.text
    assert response.json()["problem_url"] == "http://oj.jmfes.com:8888/p/401"
    mocked_fetch.assert_called_once_with("http://oj.jmfes.com:8888/p/401")


def test_chat_request_enrichment_supports_internal_jmfes_problem_url():
    request = api_server.ChatRequest(
        student_id="student_a",
        problem_id="http://172.21.60.30:8888/p/401?tid=67e653847d1c645ed6d42876",
        session_id="session-1",
        message="这题怎么做？",
    )

    with patch.object(
        api_server,
        "fetch_jmfes_problem",
        return_value={
            "problem_url": "http://oj.jmfes.com:8888/p/401",
            "problem_pid": "401",
            "problem_title": "和为给定数",
            "problem_context": "题面正文",
            "problem_tags": [],
            "oj_source": "other",
        },
    ) as mocked_fetch:
        enriched = api_server.enrich_chat_request_with_luogu_context(request)

    assert enriched.problem_url == "http://oj.jmfes.com:8888/p/401"
    assert enriched.problem_title == "和为给定数"
    assert enriched.problem_context == "题面正文"
    mocked_fetch.assert_called_once_with("http://oj.jmfes.com:8888/p/401")


def test_create_checkin_accepts_jmfes_source_and_auto_imports_problem():
    client = TestClient(api_server.app)
    api_server.app.dependency_overrides[api_server.require_student] = (
        lambda: {"user_id": "student_a", "role": "student"}
    )

    with patch.object(
        api_server,
        "fetch_jmfes_problem",
        return_value={
            "problem_url": "http://oj.jmfes.com:8888/p/401",
            "problem_pid": "401",
            "problem_title": "和为给定数",
            "problem_context": "题面正文不少于十个字",
            "problem_tags": [],
            "oj_source": "jmfes",
        },
    ), patch.object(api_server, "_start_review_generation_job", return_value=None):
        response = client.post(
            "/api/checkins",
            json={
                "problem_url": "http://172.21.60.30:8888/p/401?tid=abc",
                "problem_title": "",
                "oj_source": "jmfes",
                "completion_status": "unfinished",
                "bottleneck_text": "我不知道应该先排序还是先想怎么在一遍扫描里找两个数凑成目标和。",
                "error_types": ["未说明"],
                "reflection": "我现在只确定可能要用数组处理，但还没站稳方法。",
                "problem_context": "",
                "problem_tags": [],
                "submission_result": "not_submitted",
            },
        )

    api_server.app.dependency_overrides.clear()
    assert response.status_code == 200, response.text
