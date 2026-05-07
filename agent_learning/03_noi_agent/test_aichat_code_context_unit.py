from api_server import ChatRequest, build_chat_message_with_problem_context


def _request(**overrides):
    data = {
        "student_id": "student_a",
        "problem_id": "current",
        "session_id": "session-1",
        "message": "这段代码哪里有问题？",
    }
    data.update(overrides)
    return ChatRequest(**data)


def test_chat_context_without_problem_but_with_code_asks_for_problem_link_first():
    message = build_chat_message_with_problem_context(_request(student_code="int main(){return 0;}"))

    assert "上下文状态：无题目 + 有代码" in message
    assert "请学生先补题目链接或题号" in message
    assert "不要先分析代码" in message
    assert "不知道题目目标" in message


def test_chat_context_with_problem_and_code_requires_problem_code_alignment():
    message = build_chat_message_with_problem_context(
        _request(
            problem_title="跳石头",
            problem_context="给定河道长度、若干石头位置和最多移走数量，求最小跳跃距离的最大值。",
            student_code="bool check(int x){ return true; }",
        )
    )

    assert "上下文状态：有题目 + 有代码" in message
    assert "必须结合题面目标、学生问题和学生代码" in message
    assert "先对齐题目目标与代码实现" in message
    assert "最小可疑位置" in message
    assert "不要直接给最终代码" in message


def test_chat_context_with_problem_without_code_uses_socratic_term_ladder():
    message = build_chat_message_with_problem_context(
        _request(
            message="这题为什么要用二分，不能直接枚举吗？",
            problem_title="跳石头",
            problem_context="给定河道长度、若干石头位置和最多移走数量，求最小跳跃距离的最大值。",
        )
    )

    assert "上下文状态：有题目 + 无代码" in message
    assert "苏格拉底提问为主" in message
    assert "不要突然抛出学生尚未铺垫过的算法术语" in message
    assert "用自己的话复述当前小关系" in message


def test_chat_context_without_problem_or_code_requests_minimal_context():
    message = build_chat_message_with_problem_context(_request(message="这题怎么写？"))

    assert "上下文状态：无题目 + 无代码" in message
    assert "先索取最小上下文" in message
    assert "题号/链接" in message
    assert "不要直接进入算法教学" in message
