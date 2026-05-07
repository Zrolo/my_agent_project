import time

from database import (
    get_aichat_learning_issue_stats,
    get_aichat_problem_memory,
    init_db,
    list_aichat_messages,
    list_aichat_messages_for_student,
    list_teacher_aichat_observations,
    record_aichat_message,
    upsert_aichat_problem_memory,
)


def test_record_aichat_message_keeps_teacher_observation_metadata():
    init_db()
    suffix = int(time.time() * 1000)
    student_id = f"aichat_store_student_{suffix}"
    problem_id = "P401::unit"
    session_id = f"session_{suffix}"

    user_message_id = record_aichat_message(
        student_id=student_id,
        problem_id=problem_id,
        session_id=session_id,
        role="user",
        content="这题为什么不能直接枚举？",
        problem_title="测试题",
        problem_url="http://oj.jmfes.com:8888/p/401",
        has_problem_context=True,
        has_student_code=True,
    )
    assistant_message_id = record_aichat_message(
        student_id=student_id,
        problem_id=problem_id,
        session_id=session_id,
        role="assistant",
        content="先估一下枚举次数大概是多少。",
        problem_title="测试题",
        problem_url="http://oj.jmfes.com:8888/p/401",
        has_problem_context=True,
        has_student_code=False,
    )

    assert user_message_id > 0
    assert assistant_message_id > user_message_id

    rows = list_aichat_messages_for_student(student_id, limit=5)
    assert [row["role"] for row in rows[:2]] == ["assistant", "user"]
    assert rows[0]["problem_id"] == problem_id
    assert rows[0]["session_id"] == session_id
    assert rows[0]["problem_title"] == "测试题"
    assert rows[0]["has_problem_context"] == 1
    assert rows[1]["has_student_code"] == 1


def test_list_aichat_messages_can_restore_one_problem_session_in_chat_order():
    init_db()
    suffix = int(time.time() * 1000)
    student_id = f"aichat_restore_student_{suffix}"
    target_problem = "P405::unit"
    other_problem = "P406::unit"
    session_id = f"session_restore_{suffix}"

    record_aichat_message(student_id, target_problem, session_id, "user", "这题为什么要二分？")
    record_aichat_message(student_id, target_problem, session_id, "assistant", "先看直接枚举要试多少次。")
    record_aichat_message(student_id, other_problem, session_id, "user", "别的题记录")

    rows = list_aichat_messages(
        student_id=student_id,
        problem_id=target_problem,
        session_id=session_id,
        limit=10,
        ascending=True,
    )

    assert [row["role"] for row in rows] == ["user", "assistant"]
    assert rows[0]["content"] == "这题为什么要二分？"
    assert rows[1]["content"] == "先看直接枚举要试多少次。"


def test_teacher_aichat_observations_surface_code_debug_bottlenecks():
    init_db()
    suffix = int(time.time() * 1000)
    student_id = f"aichat_observe_student_{suffix}"
    problem_id = "P4047::unit"
    session_id = f"session_observe_{suffix}"

    record_aichat_message(
        student_id=student_id,
        problem_id=problem_id,
        session_id=session_id,
        role="user",
        content="我感觉我的代码思路没有问题，但是输出不对，为什么？",
        problem_title="P4047 部落划分",
        problem_url="https://www.luogu.com.cn/problem/P4047",
        has_problem_context=True,
        has_student_code=True,
    )
    record_aichat_message(
        student_id=student_id,
        problem_id=problem_id,
        session_id=session_id,
        role="assistant",
        content="先看你代码最后输出的边，和题目要求的部落之间距离是不是同一个量。",
        problem_title="P4047 部落划分",
        problem_url="https://www.luogu.com.cn/problem/P4047",
        has_problem_context=True,
        has_student_code=False,
    )

    rows = list_teacher_aichat_observations(limit=10)
    row = next(item for item in rows if item["student_id"] == student_id)

    assert row["problem_id"] == problem_id
    assert row["problem_title"] == "P4047 部落划分"
    assert row["student_message_count"] == 1
    assert row["has_problem_context"] is True
    assert row["has_student_code"] is True
    assert row["issue_type"] == "code_debug"
    assert row["issue_label"] == "代码输出不对"
    assert row["suggested_teacher_action"] == "先看最近 AIChat，再让学生指出代码输出的量对应题目里的哪个量。"
    assert "输出不对" in row["latest_student_message"]


def test_teacher_aichat_observations_classify_complexity_without_checkin():
    init_db()
    suffix = int(time.time() * 1000)
    student_id = f"aichat_complexity_student_{suffix}"
    problem_id = "P405::unit"
    session_id = f"session_complexity_{suffix}"

    record_aichat_message(
        student_id=student_id,
        problem_id=problem_id,
        session_id=session_id,
        role="user",
        content="这道题为什么不能直接枚举？n 是 10^5 会不会超时？",
        problem_title="复杂度测试题",
        has_problem_context=True,
        has_student_code=False,
    )

    rows = list_teacher_aichat_observations(limit=10)
    row = next(item for item in rows if item["student_id"] == student_id)

    assert row["issue_type"] == "complexity"
    assert row["issue_label"] == "复杂度判断不清"
    assert row["suggested_teacher_action"] == "让学生先估算朴素做法次数，再对照数据范围。"


def test_teacher_aichat_observations_classify_learning_issue_categories_for_dashboard():
    init_db()
    suffix = int(time.time() * 1000)
    student_id = f"aichat_issue_student_{suffix}"

    record_aichat_message(
        student_id=student_id,
        problem_id="P1119::issue",
        session_id=f"session_transform_{suffix}",
        role="user",
        content="我知道是 Floyd，但是不理解为什么可以按时间解锁中转点，这样会不会用到没修好的村庄？",
        problem_title="P1119 灾后重建",
        has_problem_context=True,
    )
    record_aichat_message(
        student_id=student_id,
        problem_id="P16354::issue",
        session_id=f"session_method_{suffix}",
        role="user",
        content="这题是不是可以用贪心还是 DP？我不知道为什么选这个方法。",
        problem_title="天际线",
        has_problem_context=True,
    )

    rows = list_teacher_aichat_observations(limit=20)
    transform_row = next(item for item in rows if item["problem_id"] == "P1119::issue")
    method_row = next(item for item in rows if item["problem_id"] == "P16354::issue")

    assert transform_row["learning_issue_type"] == "key_transformation"
    assert transform_row["learning_issue_label"] == "关键转化没接上"
    assert "关键条件" in transform_row["evidence"]
    assert method_row["learning_issue_type"] == "method_selection"
    assert method_row["learning_issue_label"] == "方法选择困难"

    stats = get_aichat_learning_issue_stats(days=7)
    labels = {row["label"]: row for row in stats}
    assert labels["关键转化没接上"]["count"] >= 1
    assert labels["方法选择困难"]["count"] >= 1
    assert labels["关键转化没接上"]["teacher_action"]


def test_aichat_problem_memory_is_shared_by_problem_not_session_and_compacted():
    init_db()
    suffix = int(time.time() * 1000)
    student_id = f"aichat_memory_student_{suffix}"
    problem_id = "P401::memory"

    upsert_aichat_problem_memory(
        student_id=student_id,
        problem_id=problem_id,
        summary="当前卡点：不知道二分 check 在判断什么。\n学生已说清：知道直接枚举会超时。",
        source_session_id="session_a",
    )
    upsert_aichat_problem_memory(
        student_id=student_id,
        problem_id=problem_id,
        summary="学生当前卡点：" + "很长" * 800,
        source_session_id="session_b",
    )

    row = get_aichat_problem_memory(student_id=student_id, problem_id=problem_id)

    assert row is not None
    assert row["student_id"] == student_id
    assert row["problem_id"] == problem_id
    assert row["source_session_id"] == "session_b"
    assert len(row["summary"]) <= 1000
    assert row["summary"].endswith("...")
