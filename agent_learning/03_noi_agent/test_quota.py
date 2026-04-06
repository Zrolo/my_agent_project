"""
配额逻辑手工测试脚本（遗留）
===========================

⚠️  重要说明：
本脚本为旧版手工演示脚本，仅用于手动验证配额扣减流程。
不代表当前真实接口契约，不作为回归测试依据。

当前 chat() 返回契约：
    (display_reply: str, history_reply: str, final_level: str)

如需自动化测试，请使用 test_control_logic.py 或等待新版测试套件。

模拟用户输入，测试配额扣减逻辑
"""

import json
import os
import sys

# 检查 API key
if not os.environ.get("MOONSHOT_API_KEY"):
    print("❌ 错误：MOONSHOT_API_KEY 未设置")
    print("请先运行：export MOONSHOT_API_KEY=你的API密钥")
    sys.exit(1)

print("✅ MOONSHOT_API_KEY 已设置")
print("=" * 60)

# 清理旧的测试数据
QUOTA_FILE = "quota.json"
TEST_STUDENT = "测试学生"
TEST_PROBLEM = "P1001"

if os.path.exists(QUOTA_FILE):
    with open(QUOTA_FILE, "r") as f:
        all_quota = json.load(f)
    # 清理测试学生的数据
    if TEST_STUDENT in all_quota:
        del all_quota[TEST_STUDENT]
        with open(QUOTA_FILE, "w") as f:
            json.dump(all_quota, f, ensure_ascii=False, indent=2)
    print(f"🧹 已清理测试数据")

print(f"\n开始测试：学生={TEST_STUDENT}, 题目={TEST_PROBLEM}")
print("=" * 60)

# 导入被测函数
from noi_agent import (
    load_quota, 
    save_quota, 
    consume_quota, 
    get_remaining_quota,
    detect_quota_consumption,
    generate_farewell_gift,
    chat,
    PER_PROBLEM_HINT_LIMIT
)

# 检查初始配额
quota = load_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"\n【初始状态】")
print(f"quota.json 内容: {quota}")
print(f"剩余配额: {get_remaining_quota(TEST_STUDENT, TEST_PROBLEM)} / {PER_PROBLEM_HINT_LIMIT}")

# ============ 测试1: L1 级别（反问，不应扣配额）============
print("\n" + "=" * 60)
print("【测试1】L1级别：输入'这道题我不会，帮我看看'")
print("预期：触发L1反问，不消耗配额")
print("-" * 60)

messages = [{"role": "user", "content": "这道题我不会，帮我看看"}]
reply1 = chat(messages, TEST_STUDENT, TEST_PROBLEM)

print(f"\nAgent回复：\n{reply1}")

quota_after_1 = load_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"\n【测试1后配额状态】")
print(f"quota.json: {quota_after_1}")
print(f"count值: {quota_after_1['count']}")
print(f"剩余配额: {get_remaining_quota(TEST_STUDENT, TEST_PROBLEM)}")

if quota_after_1['count'] == 0:
    print("✅ 测试1通过：L1未扣配额")
else:
    print(f"❌ 测试1失败：L1被误扣了配额")

# ============ 测试2: L2/L3 级别（有实质提示，应扣配额）============
print("\n" + "=" * 60)
print("【测试2】L2/L3级别：输入'我觉得可以用二分，但不知道边界怎么写'")
print("预期：触发L2方向提示，消耗1次配额")
print("-" * 60)

messages.append({"role": "assistant", "content": reply1})
messages.append({"role": "user", "content": "我觉得可以用二分，但不知道边界怎么写"})
reply2 = chat(messages, TEST_STUDENT, TEST_PROBLEM)

print(f"\nAgent回复：\n{reply2}")

quota_after_2 = load_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"\n【测试2后配额状态】")
print(f"quota.json: {quota_after_2}")
print(f"count值: {quota_after_2['count']}")
print(f"剩余配额: {get_remaining_quota(TEST_STUDENT, TEST_PROBLEM)}")

if quota_after_2['count'] == 1:
    print("✅ 测试2通过：L2/L3正确扣减1次配额")
else:
    print(f"❌ 测试2失败：预期count=1，实际count={quota_after_2['count']}")

# ============ 测试3: 继续测试直到配额耗尽 ============
print("\n" + "=" * 60)
print("【测试3】继续提问，直到配额耗尽")
print("-" * 60)

round_num = 3
while get_remaining_quota(TEST_STUDENT, TEST_PROBLEM) > 0:
    messages.append({"role": "assistant", "content": reply2})
    messages.append({"role": "user", "content": "我还是不太懂，能给个代码示例吗"})
    reply = chat(messages, TEST_STUDENT, TEST_PROBLEM)
    
    quota = load_quota(TEST_STUDENT, TEST_PROBLEM)
    print(f"\n第{round_num}轮：count={quota['count']}, 剩余={get_remaining_quota(TEST_STUDENT, TEST_PROBLEM)}")
    print(f"回复预览：{reply[:100]}...")
    
    round_num += 1
    if round_num > 10:  # 防止无限循环
        break

# ============ 测试4: 配额耗尽后 ============
print("\n" + "=" * 60)
print("【测试4】配额耗尽后再次提问")
print("预期：返回'临别礼物'，不调用LLM")
print("-" * 60)

messages.append({"role": "user", "content": "再给我点提示吧"})
reply_final = chat(messages, TEST_STUDENT, TEST_PROBLEM)

print(f"\nAgent回复：\n{reply_final}")

quota_final = load_quota(TEST_STUDENT, TEST_PROBLEM)
print(f"\n【最终配额状态】")
print(f"quota.json: {quota_final}")
print(f"count值: {quota_final['count']} (应等于max={quota_final['max']})")

if "临别礼物" in reply_final or "配额" in reply_final:
    print("✅ 测试4通过：配额耗尽后正确返回临别礼物")
else:
    print("❌ 测试4失败：配额耗尽后未返回临别礼物")

# ============ 测试总结 ============
print("\n" + "=" * 60)
print("【测试总结】")
print("=" * 60)

# 读取最终的 quota.json 显示完整结构
if os.path.exists(QUOTA_FILE):
    with open(QUOTA_FILE, "r") as f:
        final_data = json.load(f)
    print(f"\nquota.json 完整内容：")
    print(json.dumps(final_data, ensure_ascii=False, indent=2))

print("\n测试完成！")
