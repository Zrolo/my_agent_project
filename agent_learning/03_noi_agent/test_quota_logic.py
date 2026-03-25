"""
配额扣减逻辑回归测试
验证 parse_level_tag 和扣费逻辑的正确性
"""

import sys
import os

# 添加父目录到路径，以便导入 noi_agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from noi_agent import parse_level_tag, load_quota, save_quota, consume_quota, get_remaining_quota
import json


def should_consume(level: str) -> bool:
    """基于 level 决定是否扣费"""
    return level in ("L2", "L3")


def test_parse_level_tag(name: str, reply: str, expected_level: str, expected_consume: bool):
    """测试标签解析"""
    level, clean = parse_level_tag(reply)
    consume = should_consume(level)
    
    status = "✅ PASS" if (level == expected_level and consume == expected_consume) else "❌ FAIL"
    print(f"{status} {name}")
    print(f"   输入: {reply[:60]}...")
    print(f"   解析level: '{level}' (期望: '{expected_level}')")
    print(f"   扣费: {consume} (期望: {expected_consume})")
    print()
    
    return status == "✅ PASS"


def test_quota_consumption_logic():
    """
    测试配额扣减逻辑（不依赖chat()和API）
    直接测试底层配额函数
    """
    print("=" * 70)
    print("测试配额扣减逻辑")
    print("=" * 70)
    print()
    
    test_student = "test_quota_student"
    test_problem = "TEST_P_QUOTA"
    
    # 重置配额
    save_quota(test_student, test_problem, {"count": 0, "max": 3})
    
    # 测试初始状态
    remaining = get_remaining_quota(test_student, test_problem)
    assert remaining == 3, f"初始剩余配额应为3，实际: {remaining}"
    print(f"✅ 初始配额: {remaining}")
    
    # 模拟L2/L3回复 - 扣费
    level = "L2"
    if should_consume(level):
        success, remaining_after = consume_quota(test_student, test_problem)
        assert success, "扣费应该成功"
        assert remaining_after == 2, f"扣费后剩余应为2，实际: {remaining_after}"
        print(f"✅ L2扣费成功，剩余: {remaining_after}")
    
    # 模拟L1回复 - 不扣费
    level = "L1"
    if not should_consume(level):
        remaining = get_remaining_quota(test_student, test_problem)
        assert remaining == 2, f"L1不应扣费，剩余应为2，实际: {remaining}"
        print(f"✅ L1未扣费，剩余: {remaining}")
    
    # 模拟L3回复 - 扣费
    level = "L3"
    if should_consume(level):
        success, remaining_after = consume_quota(test_student, test_problem)
        assert success, "扣费应该成功"
        assert remaining_after == 1, f"扣费后剩余应为1，实际: {remaining_after}"
        print(f"✅ L3扣费成功，剩余: {remaining_after}")
    
    # 模拟L4回复 - 不扣费
    level = "L4"
    if not should_consume(level):
        remaining = get_remaining_quota(test_student, test_problem)
        assert remaining == 1, f"L4不应扣费，剩余应为1，实际: {remaining}"
        print(f"✅ L4未扣费，剩余: {remaining}")
    
    # 再扣一次，到0
    level = "L3"
    if should_consume(level):
        success, remaining_after = consume_quota(test_student, test_problem)
        assert success, "扣费应该成功"
        assert remaining_after == 0, f"扣费后剩余应为0，实际: {remaining_after}"
        print(f"✅ 第三次扣费成功，剩余: {remaining_after}")
    
    # 再扣一次，应该失败
    success, remaining_after = consume_quota(test_student, test_problem)
    assert not success, "配额耗尽后扣费应该失败"
    assert remaining_after == 0, "配额耗尽后剩余应为0"
    print(f"✅ 配额耗尽后扣费失败，剩余: {remaining_after}")
    
    print()
    return True


def test_hard_gate_enforcement():
    """
    测试硬闸门逻辑（不依赖API）
    直接测试 enforce_level_gate 函数
    """
    print("=" * 70)
    print("测试硬闸门逻辑")
    print("=" * 70)
    print()
    
    from noi_agent import enforce_level_gate
    
    # 测试1: 模型返回L1，max_level=L1 - 不拦截
    level, reply = enforce_level_gate("L1", "L1", "内容\n\n[LEVEL:L1]")
    assert level == "L1", "应允许L1"
    assert "内容" in reply, "应保持原内容"
    print("✅ 模型L1 <= 限制L1: 不拦截")
    
    # 测试2: 模型返回L2，max_level=L1 - 强制降级
    level, reply = enforce_level_gate("L2", "L1", "这是L3内容\n\n[LEVEL:L2]")
    assert level == "L1", "应强制降级为L1"
    assert "[LEVEL:L1]" in reply, "应替换为L1标签"
    print("✅ 模型L2 > 限制L1: 强制降级为L1")
    
    # 测试3: 模型返回L3，max_level=L2 - 强制降级
    level, reply = enforce_level_gate("L3", "L2", "这是L3内容\n\n[LEVEL:L3]")
    assert level == "L2", "应强制降级为L2"
    assert "[LEVEL:L2]" in reply, "应替换为L2标签"
    print("✅ 模型L3 > 限制L2: 强制降级为L2")
    
    # 测试4: 模型返回L3，max_level=L3 - 不拦截
    level, reply = enforce_level_gate("L3", "L3", "内容\n\n[LEVEL:L3]")
    assert level == "L3", "应允许L3"
    print("✅ 模型L3 <= 限制L3: 不拦截")
    
    # 测试5: 模型返回空标签，max_level=L2 - 保持（空<任何级别）
    level, reply = enforce_level_gate("", "L2", "内容")
    assert level == "", "空标签应保持"
    print("✅ 模型无标签 <= 限制L2: 不拦截")
    
    print()
    return True


def main():
    print("=" * 70)
    print("配额扣减逻辑与硬闸门回归测试")
    print("=" * 70)
    print()
    
    tests = [
        # 标签解析测试
        ("正文L2末尾L1", "试试这个思路 [LEVEL:L2]\n但你再想想 [LEVEL:L1]", "L1", False),
        ("正文L2末尾L3", "先这样想 [LEVEL:L2]\n然后这样改 [LEVEL:L3]", "L3", True),
        ("小写level:l2", "试试递归 [level:l2]", "L2", True),
        ("小写level:l3", "看这段代码 [level:l3]", "L3", True),
        ("小写level:l1", "请先思考 [level:l1]", "L1", False),
        ("缺标签", "试试递归，但不要直接抄", "", False),
        ("正文有L2字样但无标签", "我觉得是L2级别的难度，需要递归", "", False),
        ("末尾L4", "这道题建议找老师 [LEVEL:L4]", "L4", False),
        ("纯L2标签", "试试二分查找 [LEVEL:L2]", "L2", True),
        ("标签后有空格", "试试递归 [LEVEL:L2]   ", "L2", True),
    ]
    
    passed = 0
    failed = 0
    
    for name, reply, expected_level, expected_consume in tests:
        if test_parse_level_tag(name, reply, expected_level, expected_consume):
            passed += 1
        else:
            failed += 1
    
    # 配额扣减逻辑测试
    try:
        if test_quota_consumption_logic():
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"❌ FAIL 配额扣减测试: {e}")
        import traceback
        traceback.print_exc()
        failed += 1
    
    # 硬闸门测试
    try:
        if test_hard_gate_enforcement():
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"❌ FAIL 硬闸门测试: {e}")
        import traceback
        traceback.print_exc()
        failed += 1
    
    print("=" * 70)
    print(f"结果: {passed} 通过, {failed} 失败")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
