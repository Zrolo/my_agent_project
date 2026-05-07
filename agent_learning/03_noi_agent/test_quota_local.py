"""
配额逻辑纯本地测试（不调用API）
直接测试 detect_quota_consumption 和配额管理函数
"""

import json
import os
import sys

if __name__ != "__main__":
    import pytest
    pytest.skip("旧版配额本地手工演示脚本，不作为 pytest 自动回归测试。", allow_module_level=True)

QUOTA_FILE = "quota.json"
TEST_STUDENT = "测试学生"
TEST_PROBLEM = "P1001"

# 清理旧的测试数据
if os.path.exists(QUOTA_FILE):
    with open(QUOTA_FILE, "r") as f:
        all_quota = json.load(f)
    if TEST_STUDENT in all_quota:
        del all_quota[TEST_STUDENT]
        with open(QUOTA_FILE, "w") as f:
            json.dump(all_quota, f, ensure_ascii=False, indent=2)

# 导入被测函数（这些不依赖API）
from noi_agent import (
    load_quota, 
    save_quota, 
    consume_quota, 
    get_remaining_quota,
    detect_quota_consumption,
    generate_farewell_gift,
    PER_PROBLEM_HINT_LIMIT
)

print("=" * 60)
print("配额逻辑纯本地测试（不调用API）")
print("=" * 60)

# ============ 测试1: 配额初始化 ============
print("\n【测试1】配额初始化")
quota = load_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"quota.json: {quota}")
assert quota['count'] == 0, "count应该初始化为0"
assert quota['max'] == 3, "max应该为3"
print("✅ 测试1通过：配额初始化正确")

# ============ 测试2: 检测L1回复（不应扣配额）============
print("\n【测试2】detect_quota_consumption - L1级别回复")
l1_replies = [
    "请先告诉我：\n1. 你读完题目后的第一个思路是什么？\n2. 你尝试了什么方法？",
    "请先描述你的思考过程。",
    "这道题你需要先自己思考。",
]
for i, reply in enumerate(l1_replies, 1):
    result = detect_quota_consumption(reply)
    print(f"  回复{i} ({len(reply)}字): {'✅ 未扣配额' if not result else '❌ 误判'}")
    assert not result, f"L1回复{i}不应被检测为消耗配额"
print("✅ 测试2通过：L1回复正确识别（不扣配额）")

# ============ 测试3: 检测L2/L3回复（应扣配额）============
print("\n【测试3】detect_quota_consumption - L2/L3级别回复")
l2_l3_replies = [
    ("试试用二分查找，注意边界条件。", "方向提示"),
    ("```python\nfor i in range(n):\n    pass\n```", "代码片段"),
    ("这里可以用前缀和优化，把O(n²)降到O(n)。", "算法建议"),
    ("建议用递归+记忆化的方式，避免重复计算。", "建议+算法"),
    ("考虑一下单调栈的性质，维护一个递增序列。", "算法提示"),
]
for reply, desc in l2_l3_replies:
    result = detect_quota_consumption(reply)
    print(f"  [{desc}]: {'✅ 扣配额' if result else '❌ 漏检'}")
    assert result, f"L2/L3回复'{desc}'应被检测为消耗配额"
print("✅ 测试3通过：L2/L3回复正确识别（扣配额）")

# ============ 测试4: 配额扣减流程 ============
print("\n【测试4】consume_quota 配额扣减")
print(f"  初始: count={load_quota(TEST_STUDENT, TEST_PROBLEM)['count']}")

success, remaining = consume_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"  第1次扣减: success={success}, remaining={remaining}")
assert success and remaining == 2

success, remaining = consume_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"  第2次扣减: success={success}, remaining={remaining}")
assert success and remaining == 1

success, remaining = consume_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"  第3次扣减: success={success}, remaining={remaining}")
assert success and remaining == 0

success, remaining = consume_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"  第4次扣减(超额): success={success}, remaining={remaining}")
assert not success and remaining == 0

print("✅ 测试4通过：配额扣减流程正确")

# ============ 测试5: 配额耗尽后状态 ============
print("\n【测试5】配额耗尽后状态")
quota = load_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"  quota.json: {quota}")
assert quota['count'] == 3
assert quota['max'] == 3
assert get_remaining_quota(TEST_STUDENT, TEST_PROBLEM) == 0
print("✅ 测试5通过：配额耗尽状态正确")

# ============ 测试6: 临别礼物 ============
print("\n【测试6】generate_farewell_gift")
gift = generate_farewell_gift(TEST_PROBLEM)
print(f"  输出预览: {gift[:80]}...")
assert "临别礼物" in gift
assert TEST_PROBLEM in gift
print("✅ 测试6通过：临别礼物生成正确")

# ============ 测试7: 换题后配额重置 ============
print("\n【测试7】换题后配额独立")
TEST_PROBLEM_2 = "P1002"
quota_new = load_quota(TEST_STUDENT, TEST_PROBLEM_2)
print(f"  P1001: {load_quota(TEST_STUDENT, TEST_PROBLEM)}")
print(f"  P1002: {quota_new}")
assert quota_new['count'] == 0, "新题目配额应独立计算"
assert quota_new['max'] == 3
print("✅ 测试7通过：换题后配额独立")

# ============ 最终 quota.json 展示 ============
print("\n" + "=" * 60)
print("【最终 quota.json 内容】")
with open(QUOTA_FILE, "r") as f:
    final_data = json.load(f)
print(json.dumps(final_data, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("✅ 所有本地测试通过！")
print("=" * 60)
