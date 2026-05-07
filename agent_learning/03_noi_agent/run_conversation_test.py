import json
import os

if __name__ != "__main__":
    import pytest
    pytest.skip("旧版真实 LLM 手工演示脚本，不作为 pytest 自动回归测试。", allow_module_level=True)

from noi_agent import chat, load_quota, QUOTA_FILE

# 清理旧的测试数据
if os.path.exists(QUOTA_FILE):
    with open(QUOTA_FILE, "r") as f:
        all_quota = json.load(f)
    if "测试" in all_quota:
        del all_quota["测试"]
        with open(QUOTA_FILE, "w") as f:
            json.dump(all_quota, f, ensure_ascii=False, indent=2)

STUDENT = "测试"
PROBLEM = "P1001"

print("=" * 60)
print("真实对话测试 - 记录配额扣减情况")
print("=" * 60)
print(f"\n学生: {STUDENT}, 题目: {PROBLEM}")

# 显示初始配额
quota = load_quota(STUDENT, PROBLEM)
print(f"初始配额: count={quota['count']}, max={quota['max']}")
print(f"\n{'='*60}\n")

messages = []

# 第1轮
print("【第1轮】")
print("学生输入: 这道题我不会做")
print("-" * 40)

messages.append({"role": "user", "content": "这道题我不会做"})
reply1 = chat(messages, STUDENT, PROBLEM)
messages.append({"role": "assistant", "content": reply1})

print(f"Agent回复:\n{reply1}")

quota1 = load_quota(STUDENT, PROBLEM)
print(f"\n[第1轮后 quota.json]")
print(json.dumps({STUDENT: {PROBLEM: quota1}}, ensure_ascii=False, indent=2))
print(f"\n{'='*60}\n")

# 第2轮
print("【第2轮】")
print("学生输入: 我觉得可能要用递归，但不知道怎么写")
print("-" * 40)

messages.append({"role": "user", "content": "我觉得可能要用递归，但不知道怎么写"})
reply2 = chat(messages, STUDENT, PROBLEM)
messages.append({"role": "assistant", "content": reply2})

print(f"Agent回复:\n{reply2}")

quota2 = load_quota(STUDENT, PROBLEM)
print(f"\n[第2轮后 quota.json]")
print(json.dumps({STUDENT: {PROBLEM: quota2}}, ensure_ascii=False, indent=2))
print(f"\n{'='*60}\n")

# 第3轮
print("【第3轮】")
print("学生输入: 可以给我看一下代码吗")
print("-" * 40)

messages.append({"role": "user", "content": "可以给我看一下代码吗"})
reply3 = chat(messages, STUDENT, PROBLEM)
messages.append({"role": "assistant", "content": reply3})

print(f"Agent回复:\n{reply3}")

quota3 = load_quota(STUDENT, PROBLEM)
print(f"\n[第3轮后 quota.json]")
print(json.dumps({STUDENT: {PROBLEM: quota3}}, ensure_ascii=False, indent=2))
print(f"\n{'='*60}\n")

# 最终总结
print("【测试完成】")
print(f"最终 count: {quota3['count']} / {quota3['max']}")
