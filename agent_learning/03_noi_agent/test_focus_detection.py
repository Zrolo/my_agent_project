from review_engine import _detect_quiz_focus


def _ctx(error_layer: str, text: str) -> dict:
    return {
        "problem_title": "",
        "problem_context": text,
        "bottleneck_text": text,
        "main_block": text,
        "key_bridge": text,
        "next_step": text,
        "error_layer": error_layer,
        "core_design_subtags": [],
    }


def test_detect_data_type_focus():
    ctx = _ctx("implementation", "n <= 10^18，我不知道这里是不是必须开 long long，不然会不会溢出。")
    assert _detect_quiz_focus(ctx) == "data_type"


def test_detect_loop_boundary_focus():
    ctx = _ctx("implementation", "这里到底是 0-indexed 还是 1-indexed，我总是在循环起点和终点写错，下标越界。")
    assert _detect_quiz_focus(ctx) == "loop_boundary"


def test_detect_recursion_structure_focus():
    ctx = _ctx("core_design", "我最卡的是递归什么时候停，base case 怎么写，当前这一层到底表示什么。")
    assert _detect_quiz_focus(ctx) == "recursion_structure"


def test_detect_complexity_fit_focus():
    ctx = _ctx("method", "数据范围到 10^6，我这个 O(n^2) 做法会不会 TLE，我不会判断复杂度能不能过。")
    assert _detect_quiz_focus(ctx) == "complexity_fit"


if __name__ == "__main__":
    test_detect_data_type_focus()
    test_detect_loop_boundary_focus()
    test_detect_recursion_structure_focus()
    test_detect_complexity_fit_focus()
    print("focus detection tests passed")
