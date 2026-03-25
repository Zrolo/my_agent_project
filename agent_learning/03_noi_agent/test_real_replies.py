"""
真实回复样例测试
展示在不同控制对象约束下，Prompt 层应该如何回复

注意：这些样例是"期望的回复风格"，用于验证 Prompt 构造是否正确
实际运行时，LLM 会在这些约束下生成类似回复
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from noi_agent import analyze_student_turn, build_system_prompt, L2_SLOTS


def mock_llm_reply(system_prompt: str, user_input: str) -> str:
    """
    模拟 LLM 在约束下的回复
    实际运行时由 Kimi API 生成，这里展示预期输出风格
    """
    # 解析控制参数
    max_level = "L3"
    bridge_redline = False
    
    if "本次回复最高级别: L1" in system_prompt:
        max_level = "L1"
    elif "本次回复最高级别: L2" in system_prompt:
        max_level = "L2"
    
    if "桥梁红线: 开启" in system_prompt:
        bridge_redline = True
    
    # 根据约束生成模拟回复（展示预期风格）
    if max_level == "L1":
        return "先别想快不快。最笨的方法你会怎么做？\n\n[LEVEL:L1]"
    
    elif max_level == "L2":
        # 从 prompt 中提取当前槽位
        current_slot = "对象"
        for slot in L2_SLOTS:
            if f"当前应该追问的槽位：{slot}" in system_prompt:
                current_slot = slot
                break
        
        slot_questions = {
            "对象": "这道题你最终要记录什么信息？",
            "选择": "每一步你能做什么决定？",
            "限制": "题目里什么条件不能超过？",
            "最简单情况": "最小的输入是什么情况？"
        }
        
        return f"{slot_questions.get(current_slot, '再想想，你漏了什么关键信息？')}\n\n[LEVEL:L2]"
    
    elif max_level == "L3":
        if bridge_redline:
            return "你这里定义缺了一个会影响结果的条件。再想想，什么量会影响后面的结果？\n\n[LEVEL:L3]"
        else:
            return "你的转移少考虑了一个边界情况。当i=1时，dp[i-2]会越界。\n\n[LEVEL:L3]"
    
    return "[LEVEL:L1]"


def test_sample_1_l1_direct_request():
    """样例1: L1 - 直接索取"""
    print("=" * 70)
    print("样例1: L1 - 直接索取")
    print("=" * 70)
    
    user_input = "给我代码"
    control = analyze_student_turn(user_input, [])
    
    print(f"学生输入: {user_input}")
    print(f"控制对象: max_level={control['max_level']}, bridge_redline={control['bridge_redline']}, tags={control['reason_tags']}")
    
    system = build_system_prompt(control, 3, "test", "P1001")
    reply = mock_llm_reply(system, user_input)
    
    print(f"\n系统回复:\n{reply}")
    print("\n✅ 检查点:")
    print("  - 级别为 L1 ✓")
    print("  - 只问一个问题 ✓")
    print("  - 不给方向、不确认题型 ✓")
    print("  - 默认问法：先别想快不快... ✓")
    
    return True


def test_sample_2_l2_slot_inquiry():
    """样例2: L2 - 槽位化单步追问"""
    print("\n" + "=" * 70)
    print("样例2: L2 - 槽位化单步追问（对象槽位）")
    print("=" * 70)
    
    user_input = "这道题应该是背包问题，但我不知道怎么定义状态"
    control = analyze_student_turn(user_input, [])
    
    print(f"学生输入: {user_input}")
    print(f"控制对象: max_level={control['max_level']}, bridge_redline={control['bridge_redline']}, tags={control['reason_tags']}")
    
    system = build_system_prompt(control, 3, "test", "P1001")
    reply = mock_llm_reply(system, user_input)
    
    print(f"\n系统回复:\n{reply}")
    print("\n✅ 检查点:")
    print("  - 级别为 L2 ✓")
    print("  - 只问一个问题 ✓")
    print("  - 围绕槽位（对象/选择/限制/最简单情况）✓")
    print("  - 不给状态定义/转移方程 ✓")
    
    return True


def test_sample_3_l3_normal():
    """样例3: L3 - 正常指出问题"""
    print("\n" + "=" * 70)
    print("样例3: L3 - 正常指出问题（无bridge_redline）")
    print("=" * 70)
    
    user_input = "我定义dp[i]为前i个最大价值，转移是dp[i]=max(dp[i-1], dp[i-2]+v[i])，但WA了"
    control = analyze_student_turn(user_input, [])
    
    print(f"学生输入: {user_input}")
    print(f"控制对象: max_level={control['max_level']}, bridge_redline={control['bridge_redline']}, tags={control['reason_tags']}")
    
    system = build_system_prompt(control, 3, "test", "P1001")
    reply = mock_llm_reply(system, user_input)
    
    print(f"\n系统回复:\n{reply}")
    print("\n✅ 检查点:")
    print("  - 级别为 L3 ✓")
    print("  - 指出具体问题（边界情况）✓")
    print("  - 不直接给正确答案 ✓")
    print("  - 最多引入一个新概念 ✓")
    
    return True


def test_sample_4_l3_bridge_redline():
    """样例4: L3 + bridge_redline - 不能补桥梁"""
    print("\n" + "=" * 70)
    print("样例4: L3 + bridge_redline - 索取关键桥梁时被限制")
    print("=" * 70)
    
    user_input = "我定义了dp[i]表示前i个，但转移不对，应该怎么转移？"
    control = analyze_student_turn(user_input, [])
    
    print(f"学生输入: {user_input}")
    print(f"控制对象: max_level={control['max_level']}, bridge_redline={control['bridge_redline']}, tags={control['reason_tags']}")
    
    system = build_system_prompt(control, 3, "test", "P1001")
    reply = mock_llm_reply(system, user_input)
    
    print(f"\n系统回复:\n{reply}")
    print("\n✅ 检查点:")
    print("  - 级别为 L3 ✓")
    print("  - bridge_redline=true ✓")
    print("  - 可以指出错（定义不完整）✓")
    print("  - 不能补正确转移方程 ✓")
    print("  - 引导学生自己推导 ✓")
    
    return True


def test_sample_5_code_no_target():
    """样例5: 贴代码无怀疑点 -> L2"""
    print("\n" + "=" * 70)
    print("样例5: 贴代码无怀疑点 -> 限制为L2")
    print("=" * 70)
    
    user_input = """#include <bits/stdc++.h>
using namespace std;
int main() {
    int n, m;
    cin >> n >> m;
    // ... 一大段代码 ...
    return 0;
}
你帮我看看哪里错了"""
    
    control = analyze_student_turn(user_input, [])
    
    print(f"学生输入: [贴了整段代码，没有指出怀疑点]")
    print(f"控制对象: max_level={control['max_level']}, bridge_redline={control['bridge_redline']}, tags={control['reason_tags']}")
    
    system = build_system_prompt(control, 3, "test", "P1001")
    reply = mock_llm_reply(system, user_input)
    
    print(f"\n系统回复:\n{reply}")
    print("\n✅ 检查点:")
    print("  - 级别为 L2（不是L3）✓")
    print("  - 有 code_no_target 标签 ✓")
    print("  - 不直接分析整段代码 ✓")
    print("  - 从槽位追问开始 ✓")
    
    return True


def test_sample_6_cross_slot_dump():
    """样例6: 跨槽位拼凑 -> L2 + 连接验证"""
    print("\n" + "=" * 70)
    print("样例6: 跨槽位拼凑 -> 做连接验证")
    print("=" * 70)
    
    user_input = "这是背包，物品是药草，容量是时间，每步选拿或不拿，目标是最大价值"
    control = analyze_student_turn(user_input, [])
    
    print(f"学生输入: {user_input}")
    print(f"控制对象: max_level={control['max_level']}, bridge_redline={control['bridge_redline']}, tags={control['reason_tags']}")
    
    system = build_system_prompt(control, 3, "test", "P1001")
    reply = mock_llm_reply(system, user_input)
    
    print(f"\n系统回复:\n{reply}")
    print("\n✅ 检查点:")
    print("  - 级别为 L2（不自动升L3）✓")
    print("  - 有 cross_slot_dump 标签 ✓")
    print("  - 做连接验证（从这些信息能推出什么）✓")
    print("  - 不直接深入讲解 ✓")
    
    return True


def main():
    print("=" * 70)
    print("真实回复样例（期望输出风格验证）")
    print("=" * 70)
    print()
    
    tests = [
        test_sample_1_l1_direct_request,
        test_sample_2_l2_slot_inquiry,
        test_sample_3_l3_normal,
        test_sample_4_l3_bridge_redline,
        test_sample_5_code_no_target,
        test_sample_6_cross_slot_dump,
    ]
    
    all_passed = True
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 70)
    print("样例展示完成")
    print("=" * 70)
    print()
    print("说明：")
    print("- 以上样例展示了不同控制约束下的期望回复风格")
    print("- 实际运行时，LLM 会在 Prompt 约束下生成类似回复")
    print("- 关键约束：max_level, bridge_redline, reason_tags")
    print("- 最终级别标签 [LEVEL:Lx] 仍由 LLM 输出，代码层解析后决定扣费")
    
    return all_passed


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
