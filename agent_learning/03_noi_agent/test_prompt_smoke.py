from noi_agent import analyze_student_turn, build_system_prompt


def test_build_system_prompt_smoke():
    dual_control = analyze_student_turn("你好", [])
    prompt = build_system_prompt(dual_control, remaining=3, student_id="student_a", problem_id="P1001")
    assert "本次回复最高级别" in prompt


def test_build_system_prompt_type_confirm_block():
    dual_control = analyze_student_turn("这题是DP吗？", [])
    prompt = build_system_prompt(dual_control, remaining=3, student_id="student_a", problem_id="P1001")
    assert "type_confirm 特殊约束" in prompt


if __name__ == "__main__":
    test_build_system_prompt_smoke()
    test_build_system_prompt_type_confirm_block()
    print("prompt smoke tests passed")
