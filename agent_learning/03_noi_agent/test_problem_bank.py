from problem_bank import (
    build_compact_card,
    classify_tag,
    extract_data_range,
    normalize_luogu_problem_ref,
    retry_problem_analysis_by_pid,
)


def test_classify_tag():
    assert classify_tag("2011") == "year"
    assert classify_tag("NOIP 提高组") == "contest"
    assert classify_tag("模拟") == "algo"


def test_normalize_luogu_problem_ref():
    assert normalize_luogu_problem_ref("P1001") == (
        "P1001",
        "https://www.luogu.com.cn/problem/P1001",
    )
    assert normalize_luogu_problem_ref("https://www.luogu.com.cn/problem/P1001") == (
        "P1001",
        "https://www.luogu.com.cn/problem/P1001",
    )


def test_extract_data_range():
    hint = "【数据范围】\n对于 100% 的数据，n <= 1e4, a <= 1e5。\n![](img)"
    assert "n <= 1e4" in extract_data_range(hint)


def test_build_compact_card_uses_algo_tags_and_limits():
    problem = {
        "problem_id": 1,
        "title": "P1003 铺地毯",
        "time_limit_ms": 1000,
        "statement_json": '{"description":"题目描述。第二句。","inputFormat":"输入格式。","outputFormat":"输出格式。","hint":"【数据范围】 n <= 1e4"}',
    }

    import problem_bank

    original = problem_bank.get_problem_tags
    problem_bank.get_problem_tags = lambda problem_id, tag_type=None: ["模拟", "枚举"] if tag_type == "algo" else []
    try:
        card = build_compact_card(problem)
    finally:
        problem_bank.get_problem_tags = original

    assert card["algo_tags"] == ["模拟", "枚举"]
    assert card["time_limit_ms"] == 1000
    assert "题目描述" in card["description_compact"]


def test_retry_problem_analysis_runs_generator_after_reset():
    import problem_bank

    original_get_problem = problem_bank.get_problem_by_luogu_pid
    original_reset = problem_bank.reset_problem_analysis_for_retry
    original_generate = problem_bank.generate_problem_analysis
    original_upsert = problem_bank.upsert_luogu_problem_analysis
    original_fail = problem_bank.mark_problem_analysis_failed

    calls = {"reset": 0, "generate": 0, "upsert": 0, "failed": 0}

    problem_bank.get_problem_by_luogu_pid = lambda pid: {
        "problem_id": 7,
        "title": "P1003 铺地毯",
        "difficulty": 2,
        "time_limit_ms": 1000,
        "statement_json": '{"description":"题目描述。","inputFormat":"输入格式。","outputFormat":"输出格式。","hint":"【数据范围】 n <= 1e4"}',
    }
    problem_bank.reset_problem_analysis_for_retry = lambda problem_id, version: calls.__setitem__("reset", calls["reset"] + 1)
    problem_bank.generate_problem_analysis = lambda **kwargs: (
        calls.__setitem__("generate", calls["generate"] + 1) or {
            "ok": True,
            "analysis": {
                "summary": "摘要",
                "strategy_types": ["simulation"],
                "knowledge_points": ["倒序枚举"],
                "common_mistakes": ["正序扫描"],
            },
        }
    )
    problem_bank.upsert_luogu_problem_analysis = lambda **kwargs: calls.__setitem__("upsert", calls["upsert"] + 1)
    problem_bank.mark_problem_analysis_failed = lambda *args, **kwargs: calls.__setitem__("failed", calls["failed"] + 1)

    original_tags = problem_bank.get_problem_tags
    problem_bank.get_problem_tags = lambda problem_id, tag_type=None: ["模拟"] if tag_type == "algo" else []
    try:
        ok, status = retry_problem_analysis_by_pid("P1003")
    finally:
        problem_bank.get_problem_by_luogu_pid = original_get_problem
        problem_bank.reset_problem_analysis_for_retry = original_reset
        problem_bank.generate_problem_analysis = original_generate
        problem_bank.upsert_luogu_problem_analysis = original_upsert
        problem_bank.mark_problem_analysis_failed = original_fail
        problem_bank.get_problem_tags = original_tags

    assert ok is True
    assert status == "completed"
    assert calls["reset"] == 1
    assert calls["generate"] == 1
    assert calls["upsert"] == 1
    assert calls["failed"] == 0
