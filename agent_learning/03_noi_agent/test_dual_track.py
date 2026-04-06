#!/usr/bin/env python3
"""
NOI Agent 双轨规则 v1 全量回归测试

测试覆盖：
1. 等级轨（L1/L2/L3/L4）
2. 风险轨（6个风险标签）
3. 组合场景
4. 输出保险丝
5. 模板模式
"""

import sys
sys.path.insert(0, '/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent')

from noi_agent import (
    analyze_student_turn,
    _is_type_confirm,
    _is_bridge_attempt,
    _detect_risks,
    _get_highest_risk,
    enforce_output_guards,
    RISK_PRIORITY,
)


def test_level_track():
    """测试等级轨"""
    print("=" * 60)
    print("测试组 1: 等级轨")
    print("=" * 60)
    
    tests = [
        # (input, expected_level, description)
        ("给我代码", "L1", "直接索取"),
        ("不会", "L1", "极短无思考"),
        ("比赛快开始了你直接说", "L1", "情绪催促"),
        ("输入一个数组，输出最大值", "L1", "只复述题意"),
        ("这题是DP吗？", "L2", "type_confirm 最多L2"),
        ("状态怎么定义", "L2", "bridge_attempt 无L3证据"),
        ("我定义了dp[i]但转移不对，第3行错了", "L3", "有代码+怀疑点"),
    ]
    
    passed = 0
    for inp, expected, desc in tests:
        result = analyze_student_turn(inp, [])
        level = result["level_control"]["max_level"]
        ok = level == expected
        status = "✅" if ok else "❌"
        print(f"{status} {desc}: 输入='{inp[:20]}...' 预期={expected} 实际={level}")
        if ok:
            passed += 1
    
    print(f"\n等级轨测试: {passed}/{len(tests)} 通过")
    return passed == len(tests)


def test_risk_track():
    """测试风险轨"""
    print("\n" + "=" * 60)
    print("测试组 2: 风险轨")
    print("=" * 60)
    
    tests = [
        # (input, expected_risks, description)
        ("给我代码", ["direct_request"], "direct_request"),
        ("这题是DP吗？", ["type_confirm"], "type_confirm"),
        ("状态怎么定义", ["bridge_attempt"], "bridge_attempt"),
        ("这题是DP吗？状态怎么定义？", ["type_confirm", "bridge_attempt", "multi_question", "mixed_signal"], "多风险混合"),
        ("给我代码怎么写？是DP吗？", ["direct_request", "type_confirm", "mixed_signal"], "direct + type_confirm"),
    ]
    
    passed = 0
    for inp, expected, desc in tests:
        risks = _detect_risks(inp)
        # 检查期望的风险标签都是否存在
        ok = all(r in risks for r in expected)
        status = "✅" if ok else "❌"
        print(f"{status} {desc}: 输入='{inp[:25]}...'")
        print(f"   预期: {expected}")
        print(f"   实际: {risks}")
        if ok:
            passed += 1
    
    print(f"\n风险轨测试: {passed}/{len(tests)} 通过")
    return passed == len(tests)


def test_risk_priority():
    """测试危险优先级"""
    print("\n" + "=" * 60)
    print("测试组 3: 危险优先级")
    print("=" * 60)
    
    tests = [
        (["direct_request", "type_confirm"], "direct_request"),
        (["type_confirm", "bridge_attempt"], "bridge_attempt"),
        (["bridge_attempt", "type_confirm"], "bridge_attempt"),
        (["type_confirm", "multi_question"], "type_confirm"),
        (["multi_question"], "multi_question"),
    ]
    
    passed = 0
    for risks, expected in tests:
        highest = _get_highest_risk(risks)
        ok = highest == expected
        status = "✅" if ok else "❌"
        print(f"{status} 风险{risks} -> 最高优先级={highest} (预期={expected})")
        if ok:
            passed += 1
    
    print(f"\n优先级测试: {passed}/{len(tests)} 通过")
    return passed == len(tests)


def test_output_guards():
    """测试输出保险丝"""
    print("\n" + "=" * 60)
    print("测试组 4: 输出保险丝")
    print("=" * 60)
    
    tests = [
        # type_confirm 场景
        {
            "reply": "是DP。你先排序。",
            "risk_tags": ["type_confirm"],
            "bridge_redline": False,
            "should_trigger": True,
            "desc": "type_confirm 确认题型"
        },
        {
            "reply": "不是二分，是贪心。",
            "risk_tags": ["type_confirm"],
            "bridge_redline": False,
            "should_trigger": True,
            "desc": "type_confirm 否认题型"
        },
        {
            "reply": "这题是字符串处理。",
            "risk_tags": ["type_confirm"],
            "bridge_redline": False,
            "should_trigger": True,
            "desc": "type_confirm '这题是' 模式"
        },
        # 正常场景不应触发
        {
            "reply": "你为什么觉得这里可以用遍历？",
            "risk_tags": [],
            "bridge_redline": False,
            "should_trigger": False,
            "desc": "无风险标签不触发"
        },
    ]
    
    passed = 0
    for test in tests:
        level_control = {"bridge_redline": test["bridge_redline"]}
        risk_control = {"risk_tags": test["risk_tags"]}
        
        result, triggered = enforce_output_guards(test["reply"], level_control, risk_control)
        
        # 检查是否触发保险丝
        was_triggered = triggered is not None
        ok = was_triggered == test["should_trigger"]
        
        status = "✅" if ok else "❌"
        print(f"{status} {test['desc']}: 触发={was_triggered} (预期={test['should_trigger']})")
        if triggered:
            print(f"   保险丝: {triggered}")
            print(f"   输出: {result[:50]}...")
        
        if ok:
            passed += 1
    
    print(f"\n输出保险丝测试: {passed}/{len(tests)} 通过")
    return passed == len(tests)


def test_combined_scenarios():
    """测试组合场景"""
    print("\n" + "=" * 60)
    print("测试组 5: 组合场景")
    print("=" * 60)
    
    tests = [
        # L2 + type_confirm
        ("这题是DP吧？", "L2", ["type_confirm"], "L2 + type_confirm"),
        # L2 + bridge_attempt
        ("状态怎么定义", "L2", ["bridge_attempt"], "L2 + bridge_attempt"),
        # L3 + bridge_attempt（有证据）
        ("我定义了dp[i]表示前i个，但转移不对", "L3", ["bridge_attempt"], "L3 + bridge_attempt"),
    ]
    
    passed = 0
    for inp, exp_level, exp_risks, desc in tests:
        result = analyze_student_turn(inp, [])
        level = result["level_control"]["max_level"]
        risks = result["risk_control"]["risk_tags"]
        
        level_ok = level == exp_level
        risks_ok = all(r in risks for r in exp_risks)
        ok = level_ok and risks_ok
        
        status = "✅" if ok else "❌"
        print(f"{status} {desc}")
        print(f"   等级: 预期={exp_level} 实际={level}")
        print(f"   风险: 预期={exp_risks} 实际={risks}")
        
        if ok:
            passed += 1
    
    print(f"\n组合场景测试: {passed}/{len(tests)} 通过")
    return passed == len(tests)


def main():
    print("=" * 60)
    print("NOI Agent 双轨规则 v1 全量回归测试")
    print("=" * 60)
    
    results = []
    results.append(("等级轨", test_level_track()))
    results.append(("风险轨", test_risk_track()))
    results.append(("危险优先级", test_risk_priority()))
    results.append(("输出保险丝", test_output_guards()))
    results.append(("组合场景", test_combined_scenarios()))
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, ok in results:
        status = "✅ 通过" if ok else "❌ 失败"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
