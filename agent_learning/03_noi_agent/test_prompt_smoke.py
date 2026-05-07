from noi_agent import (
    analyze_student_turn,
    build_pedagogical_judge_prompt,
    build_system_prompt,
    build_understanding_check_system_prompt,
    parse_level_tag,
)


def test_build_system_prompt_smoke():
    dual_control = analyze_student_turn("你好", [])
    prompt = build_system_prompt(dual_control, remaining=3, student_id="student_a", problem_id="P1001")
    assert "本次回复最高级别" in prompt
    assert "本题提示状态" not in prompt
    assert "本题剩余提示次数" not in prompt
    assert "提示次数" not in prompt
    assert "配额" not in prompt
    assert "先别想快不快" not in prompt
    assert "手算一个很小的样例" not in prompt
    assert "做题陪跑教练" in prompt
    assert "一个极小例子" in prompt
    assert "红线" in prompt


def test_build_system_prompt_type_confirm_block():
    dual_control = analyze_student_turn("这题是DP吗？", [])
    prompt = build_system_prompt(dual_control, remaining=3, student_id="student_a", problem_id="P1001")
    assert "type_confirm 特殊约束" in prompt


def test_build_system_prompt_requires_term_ladder_before_algorithm_terms():
    dual_control = analyze_student_turn("这题为什么要用二分，不能直接枚举吗？", [])
    prompt = build_system_prompt(dual_control, remaining=3, student_id="student_a", problem_id="P1001")
    assert "术语搭台阶" in prompt
    assert "不要突然引入学生尚未建立的中间概念" in prompt
    assert "判定函数" in prompt
    assert "先用题面对象和小例子说明它代表什么" in prompt
    assert "不要直接使用学生原话中没出现过的专业术语" in prompt


def test_build_system_prompt_draws_by_visualization_gap_not_algorithm_name():
    dual_control = analyze_student_turn("这个变化我看不出来", [])
    prompt = build_system_prompt(dual_control, remaining=3, student_id="student_a", problem_id="P1001")
    assert "## 画图协议" in prompt
    assert "可视化缺口" in prompt
    assert "不按算法名" in prompt
    assert "对齐型" in prompt
    assert "变化型" in prompt
    assert "结构型" in prompt
    assert "必须先画" in prompt
    assert "学生明确说先别画图" in prompt
    assert "条件 vs 实际结果" in prompt
    assert "操作前后变化" in prompt
    assert "Markdown 小表格" in prompt
    assert "只有树、图、区间、DP 表、二分流程、栈队列变化" not in prompt


def test_build_system_prompt_should_stop_questioning_after_core_strategy_is_clear():
    dual_control = analyze_student_turn("哦！那我知道了，应该是 floyd 更好", [])
    prompt = build_system_prompt(dual_control, remaining=3, student_id="student_a", problem_id="P1119")
    assert "收束时机" in prompt
    assert "学生已经说出正确算法" in prompt
    assert "核心判断" in prompt
    assert "局部伪代码片段" in prompt
    assert "不要继续让学生模拟更多样例" in prompt


def test_build_system_prompt_must_not_allow_fill_blank_answer_code():
    dual_control = analyze_student_turn("我思路懂了，但是不知道代码怎么写", [])
    prompt = build_system_prompt(dual_control, remaining=3, student_id="student_a", problem_id="P1119")
    assert "函数/循环骨架" not in prompt
    assert "补关键行" not in prompt
    assert "半步代码骨架" not in prompt
    assert "大半份答案代码" in prompt
    assert "再挖一个空" in prompt
    assert "完整函数、完整循环、main、可提交代码骨架" in prompt


def test_pedagogical_judge_prompt_must_not_request_fill_blank_answer_code():
    prompt = build_pedagogical_judge_prompt(
        [{"role": "user", "content": "我思路懂了，但是不知道代码怎么写"}],
        has_problem_context=True,
        has_student_code=False,
    )
    assert "函数/循环骨架" not in prompt
    assert "补关键行" not in prompt
    assert "局部伪代码片段" in prompt
    assert "大半份答案代码" in prompt


def test_parse_level_tag_accepts_common_colon_spacing_variants():
    cases = [
        ("内容\n\n[LEVEL:L2]", "L2"),
        ("内容\n\n[LEVEL: L2]", "L2"),
        ("内容\n\n[LEVEL：L2]", "L2"),
        ("内容\n\n[LEVEL： L2]", "L2"),
        ("内容\n\n[level: l2]", "L2"),
    ]
    for reply, expected in cases:
        level, clean = parse_level_tag(reply)
        assert level == expected
        assert clean == "内容"


def test_understanding_check_prompt_requires_current_bottleneck_transfer_quality():
    prompt = build_understanding_check_system_prompt()
    assert "先诊断学生没想明白的类型" in prompt
    assert "bottleneck_type" in prompt
    assert "quiz_format" in prompt
    assert "evidence" in prompt
    assert "贴合当前这一步" in prompt
    assert "题意翻译" in prompt
    assert "概念边界" in prompt
    assert "表示建模" in prompt
    assert "约束关系" in prompt
    assert "操作过程" in prompt
    assert "策略选择" in prompt
    assert "迁移不稳" in prompt
    assert "代码语义" in prompt
    assert "调试定位" in prompt
    assert "复杂度意识" in prompt
    assert "元认知" in prompt
    assert "情绪负荷" in prompt
    assert "小样例迁移" in prompt
    assert "错误辨析" in prompt
    assert "代码行为核对" in prompt
    assert "30-90 秒" in prompt
    assert "可判分" in prompt
    assert "不要照抄原样例" in prompt
    assert "不要生成通用学习习惯选择题" in prompt


if __name__ == "__main__":
    test_build_system_prompt_smoke()
    test_build_system_prompt_type_confirm_block()
    test_build_system_prompt_requires_term_ladder_before_algorithm_terms()
    test_build_system_prompt_draws_by_visualization_gap_not_algorithm_name()
    test_parse_level_tag_accepts_common_colon_spacing_variants()
    test_understanding_check_prompt_requires_current_bottleneck_transfer_quality()
    print("prompt smoke tests passed")
