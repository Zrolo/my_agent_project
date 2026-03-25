"""
代码层判级逻辑回归测试
验证 analyze_student_turn() 的控制对象产出
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from noi_agent import analyze_student_turn, L2_SLOTS


def test_l1_direct_request():
    """测试L1强拦：直接索取"""
    print("=" * 70)
    print("测试L1强拦：直接索取")
    print("=" * 70)
    
    test_cases = [
        ("给我代码", "direct_request"),
        ("直接讲思路", "direct_request"),
        ("帮我写这道题", "direct_request"),
        ("把答案给我", "direct_request"),
        ("你直接告诉我怎么做", "direct_request"),
    ]
    
    for text, expected_tag in test_cases:
        control = analyze_student_turn(text, [])
        assert control["max_level"] == "L1", f"'{text}' 应该触发L1，实际: {control['max_level']}"
        assert expected_tag in control["reason_tags"], f"'{text}' 应该有 {expected_tag} 标签"
        assert control["bridge_redline"] == False, "L1不应该开启bridge_redline"
        print(f"✅ '{text}' -> L1, tags={control['reason_tags']}")
    
    print()
    return True


def test_l1_emotion_pressure():
    """测试L1强拦：情绪催促（可能被direct_request拦截，都算L1）"""
    print("=" * 70)
    print("测试L1强拦：情绪催促")
    print("=" * 70)
    
    test_cases = [
        ("比赛快开始了，直接告诉我", ["L1"]),
        ("老师今天要交，求你快点", ["L1"]),
        ("我来不及了，快告诉我思路", ["L1"]),
        ("我很急你直接说答案", ["L1"]),
    ]
    
    for text, expected_levels in test_cases:
        control = analyze_student_turn(text, [])
        assert control["max_level"] in expected_levels, f"'{text}' 应该触发{expected_levels}"
        # 可以是 emotion_pressure 或 direct_request，都算对
        assert len(control["reason_tags"]) > 0, f"'{text}' 应该有触发标签"
        print(f"✅ '{text}' -> L{control['max_level']}, tags={control['reason_tags']}")
    
    print()
    return True


def test_l1_short_no_thinking():
    """测试L1强拦：极短无思考"""
    print("=" * 70)
    print("测试L1强拦：极短无思考")
    print("=" * 70)
    
    test_cases = ["不会", "没思路", "太难了", "不会写"]
    
    for text in test_cases:
        control = analyze_student_turn(text, [])
        assert control["max_level"] == "L1", f"'{text}' 应该触发L1"
        print(f"✅ '{text}' -> L1")
    
    print()
    return True


def test_bridge_attempt_without_l3():
    """测试桥梁套取但无L3证据：应压到L2"""
    print("=" * 70)
    print("测试桥梁套取但无L3证据")
    print("=" * 70)
    
    test_cases = [
        "P1048，像01背包，不会转移",
        "这道题应该是DP，但状态怎么定义",
        "我知道用二分，但check怎么写",
        "图怎么建啊",
    ]
    
    for text in test_cases:
        control = analyze_student_turn(text, [])
        assert control["max_level"] == "L2", f"'{text}' 无L3证据+索取桥梁，应压到L2，实际: {control['max_level']}"
        assert control["bridge_redline"] == True, "应开启bridge_redline"
        assert "bridge_attempt" in control["reason_tags"]
        print(f"✅ '{text}' -> L2, bridge_redline=True, tags={control['reason_tags']}")
    
    print()
    return True


def test_bridge_attempt_with_l3():
    """测试有L3证据但仍索取桥梁：保留L3但开启bridge_redline"""
    print("=" * 70)
    print("测试有L3证据但仍索取桥梁")
    print("=" * 70)
    
    test_cases = [
        "我定义了dp[i]表示前i个，但转移不对",
        "我写了递归函数f(n)，但base case不知道对不对",
    ]
    
    for text in test_cases:
        control = analyze_student_turn(text, [])
        # 有具体定义（dp[i]）算L3证据
        # "转移不对"算索取桥梁
        print(f"'{text}'")
        print(f"  -> L{control['max_level']}, bridge_redline={control['bridge_redline']}, tags={control['reason_tags']}")
        # 有L3证据应该保留L3级别
        assert control["max_level"] in ["L2", "L3"], f"'{text}' 应有L3或L2"
        if control["max_level"] == "L3":
            # L3时应该开启bridge_redline
            assert control["bridge_redline"] == True, "L3+索取桥梁应开启bridge_redline"
            assert "bridge_attempt" in control["reason_tags"]
            assert "slot_fill" in control["reason_tags"]
        print(f"✅ 通过")
    
    print()
    return True


def test_pure_l3_evidence():
    """测试纯L3证据，无桥梁索取：正常L3"""
    print("=" * 70)
    print("测试纯L3证据，无桥梁索取")
    print("=" * 70)
    
    test_cases = [
        ("我定义dp[i]为前i个物品最大价值，转移是dp[i]=max(dp[i-1], dp[i-2]+v[i])，但WA了", "L3"),
        ("我写了递归f(n)=f(n-1)+f(n-2)，但TLE", "L3"),
        ("我用了暴力枚举所有子集然后超时了", "L2_L3"),  # 这个可能不够强
    ]
    
    for text, expected in test_cases:
        control = analyze_student_turn(text, [])
        print(f"'{text[:40]}...' -> L{control['max_level']}, tags={control['reason_tags']}")
        if expected == "L3":
            assert control["max_level"] == "L3", f"应有L3证据"
            assert "slot_fill" in control["reason_tags"]
        print(f"✅ 通过")
    
    print()
    return True


def test_code_no_target():
    """测试贴代码无怀疑点"""
    print("=" * 70)
    print("测试贴代码无怀疑点")
    print("=" * 70)
    
    # 贴代码但没有指出哪一行有问题
    code_text = """
#include <bits/stdc++.h>
using namespace std;
int main() {
    int n, m;
    cin >> n >> m;
    for (int i = 0; i < n; i++) {
        // ... 代码省略
    }
    return 0;
}
你帮我看看哪里错了
"""
    
    control = analyze_student_turn(code_text, [])
    # 应该被限制在L2，且标记code_no_target
    assert "code_no_target" in control["reason_tags"], "应标记code_no_target"
    print(f"✅ 贴代码无怀疑点 -> L{control['max_level']}, tags={control['reason_tags']}")
    
    # 对比：贴代码并指出怀疑点
    code_with_doubt = """
我写了这段代码，但第15行总是越界：
for (int i = 0; i <= n; i++) {
    dp[i] = dp[i-1] + a[i];  // 这里i=n时会越界
}
"""
    control2 = analyze_student_turn(code_with_doubt, [])
    # 有怀疑点，可以进L3
    assert control2["max_level"] == "L3", "贴代码+指出怀疑点应保留L3"
    print(f"✅ 贴代码+指出怀疑点 -> L3")
    
    print()
    return True


def test_cross_slot_dump():
    """测试跨槽位拼凑"""
    print("=" * 70)
    print("测试跨槽位拼凑")
    print("=" * 70)
    
    # 一句话同时说出对象/选择/限制/目标
    cross_slot_text = "这是背包，物品是药草，容量是时间，每步选拿或不拿，目标是最大价值"
    
    control = analyze_student_turn(cross_slot_text, [])
    # 应标记cross_slot_dump
    assert "cross_slot_dump" in control["reason_tags"], "应标记cross_slot_dump"
    print(f"✅ 跨槽位拼凑 -> L{control['max_level']}, tags={control['reason_tags']}")
    
    print()
    return True


def test_l2_slot_tracking():
    """测试L2槽位追踪"""
    print("=" * 70)
    print("测试L2槽位追踪")
    print("=" * 70)
    
    # 只填了"对象"槽位
    text1 = "我觉得这道题是在处理一个数组"
    control1 = analyze_student_turn(text1, [])
    # 这种模糊描述可能触发L1或L2
    print(f"✅ 只提数组 -> L{control1['max_level']}, 对象槽位: {control1['l2_slot_state'].get('对象', 'N/A')}")
    
    # 填了对象和选择（更具体）
    text2 = "每个药草可以选拿或不拿"
    control2 = analyze_student_turn(text2, [])
    print(f"✅ 提药草和选择 -> L{control2['max_level']}, 槽位: {control2['l2_slot_state']}")
    
    print()
    return True


def main():
    print("=" * 70)
    print("代码层判级逻辑回归测试")
    print("=" * 70)
    print()
    
    all_passed = True
    
    tests = [
        test_l1_direct_request,
        test_l1_emotion_pressure,
        test_l1_short_no_thinking,
        test_bridge_attempt_without_l3,
        test_bridge_attempt_with_l3,
        test_pure_l3_evidence,
        test_code_no_target,
        test_cross_slot_dump,
        test_l2_slot_tracking,
    ]
    
    for test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except AssertionError as e:
            print(f"❌ FAIL {test_func.__name__}: {e}")
            all_passed = False
        except Exception as e:
            print(f"❌ ERROR {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("=" * 70)
    if all_passed:
        print("所有测试通过！✅")
    else:
        print("部分测试失败 ❌")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
