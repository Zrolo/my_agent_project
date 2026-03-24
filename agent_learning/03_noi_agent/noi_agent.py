"""
NOI 竞赛教练 Agent - LLM自我标注级别版本
核心：苏格拉底式引导 + 分层响应 + 每题3次配额 + LLM自标注级别
技术栈：Kimi API + JSON 文件
"""

import json
import os
import re
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

QUOTA_FILE = "quota.json"
PER_PROBLEM_HINT_LIMIT = 3

SYSTEM_PROMPT = """你是一名 NOI 竞赛教练助手，专门辅导 CSP-J/S、NOIP 方向的学生。

## 核心原则
你不是"答案机"，你是"思维训练器"。目标是让学生学会独立解题。

## 分层响应规则

**L1 - 引导反问（不消耗配额）**：
- 学生没有展示思考过程
- 你只反问引导学生先思考
- 不给任何答案、方向、代码

**L2 - 方向提示（消耗1次配额）**：
- 学生展示了思考过程
- 你给出方向性提示（如"试试二分""考虑DP"）
- 只给方向，不给具体做法或代码

**L3 - 关键代码片段（消耗1次配额）**：
- 学生在L2后仍卡住
- 你给出关键的几行代码（非完整解法）

**L4 - 转交老师（不消耗配额）**：
- 配额耗尽
- 建议学生找老师当面讨论

## 禁止事项
- 禁止直接给出完整解题代码
- 禁止在学生未展示思考前给任何实质性提示
- 禁止在回复中提及"配额""还剩几次"等字样

## 强制标注规则（必须遵守）
每次回复的最后一行必须是以下标签之一：
[LEVEL:L1]
[LEVEL:L2]
[LEVEL:L3]
[LEVEL:L4]

标签单独一行，放在回复最后，不加任何解释。
这条规则优先级最高，无论回复多长，最后一行必须是标签，不能省略。
"""


def load_quota(student_id: str, problem_id: str) -> dict:
    """加载配额，格式：{count: 0, max: 3}"""
    if os.path.exists(QUOTA_FILE):
        with open(QUOTA_FILE, "r", encoding="utf-8") as f:
            all_quota = json.load(f)
    else:
        all_quota = {}
    
    student_quota = all_quota.get(student_id, {})
    return student_quota.get(problem_id, {"count": 0, "max": PER_PROBLEM_HINT_LIMIT})


def save_quota(student_id: str, problem_id: str, quota: dict):
    """保存配额"""
    if os.path.exists(QUOTA_FILE):
        with open(QUOTA_FILE, "r", encoding="utf-8") as f:
            all_quota = json.load(f)
    else:
        all_quota = {}
    
    if student_id not in all_quota:
        all_quota[student_id] = {}
    
    all_quota[student_id][problem_id] = quota
    
    with open(QUOTA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_quota, f, ensure_ascii=False, indent=2)


def consume_quota(student_id: str, problem_id: str) -> tuple[bool, int]:
    """消耗配额，返回(成功, 剩余次数)"""
    quota = load_quota(student_id, problem_id)
    if quota["count"] >= quota["max"]:
        return False, 0
    
    quota["count"] += 1
    save_quota(student_id, problem_id, quota)
    remaining = quota["max"] - quota["count"]
    return True, remaining


def get_remaining_quota(student_id: str, problem_id: str) -> int:
    """获取剩余配额"""
    quota = load_quota(student_id, problem_id)
    return quota["max"] - quota["count"]


def generate_farewell_gift(problem_id: str) -> str:
    """配额耗尽后的临别礼物"""
    return f"""💡 这道题（{problem_id}）的提示配额已用完。

🎁 临别礼物：

建议检查以下几点：
1. 边界条件：数组是否越界？循环范围是否正确？
2. 初始化：DP初始状态、递归base case是否完整？
3. 算法选择：当前复杂度是否满足数据范围？

🎯 下一步：把思路整理成文字，明天找老师当面讨论。

---
本题提示已用完，换题后配额会重置。"""


def parse_level_tag(reply: str) -> tuple[str, str]:
    """
    从回复末尾提取 [LEVEL:Lx] 标签
    返回: (级别, 去除标签后的干净回复)
    级别: "L1", "L2", "L3", "L4", 或 ""（未找到）
    """
    # 匹配回复末尾的标签（支持可选空白）
    pattern = r'\[LEVEL:(L1|L2|L3|L4)\]\s*$'
    match = re.search(pattern, reply, re.IGNORECASE)
    
    if match:
        level = match.group(1).upper()
        # 移除标签，保留干净回复
        clean_reply = re.sub(pattern, '', reply, flags=re.IGNORECASE).rstrip()
        return level, clean_reply
    
    return "", reply.strip()


def detect_quota_consumption(reply: str) -> bool:
    """
    检测回复是否应消耗配额
    优先用标签，标签不存在时用备用检测
    """
    # 第一优先：找标签
    match = re.search(r'\[LEVEL:(L\d)\]', reply)
    if match:
        level = match.group(1)
        return level in ("L2", "L3")
    
    # 备用：只检测最可靠的特征
    # L3：有代码块（``` 出现）→ 几乎100%是L3
    if "```" in reply:
        return True
    
    # 其他情况一律不扣（保守策略，宁可少扣不误扣）
    return False


def chat(messages: list, student_id: str, problem_id: str) -> tuple[str, str]:
    """
    主对话逻辑：
    1. 检查配额
    2. 调用LLM获取回复（LLM自标注级别）
    3. 提取标签，决定是否扣配额
    4. 返回 (带配额信息的回复, 干净回复用于存历史)
    
    返回: (reply_for_display, reply_for_history)
    - reply_for_display: 带配额提示，给学生看
    - reply_for_history: 干净内容（去标签，无配额提示），存messages
    """
    remaining = get_remaining_quota(student_id, problem_id)
    
    if remaining <= 0:
        farewell = generate_farewell_gift(problem_id)
        # 配额耗尽时，显示内容和存历史内容相同
        return farewell, farewell
    
    # 构建带配额状态的system prompt
    system_with_quota = SYSTEM_PROMPT + f"""

## 当前状态
学生：{student_id}
题目：{problem_id}
本题剩余提示次数：{remaining} / {PER_PROBLEM_HINT_LIMIT}

重要：
1. 根据学生输入判断给L1/L2/L3/L4哪个级别回复
2. 回复最后一行必须是 [LEVEL:Lx] 标签
3. 不要在回复中写配额数字
"""
    
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "system", "content": system_with_quota}] + messages,
        temperature=0.3,
    )
    
    raw_reply = response.choices[0].message.content
    
    # 提取级别标签，获取干净回复（无标签，无配额提示）
    level, clean_reply = parse_level_tag(raw_reply)
    
    # 使用 detect_quota_consumption 决定是否扣配额（优先标签，备用代码块检测）
    if detect_quota_consumption(raw_reply):
        # 消耗配额
        success, remaining_after = consume_quota(student_id, problem_id)
        if success:
            reply_for_display = clean_reply + f"\n\n---\n💡 本题还剩 {remaining_after} 次提示机会"
        else:
            reply_for_display = clean_reply + "\n\n---\n⚠️ 提示配额已用完"
    else:
        # 不消耗配额
        reply_for_display = clean_reply + f"\n\n---\n💡 本题还剩 {remaining} 次提示机会（本次未消耗）"
    
    # 存历史用：干净回复（去标签，无配额提示）
    reply_for_history = clean_reply
    
    return reply_for_display, reply_for_history


def main():
    print("=== NOI 竞赛教练 Agent ===")
    print("LLM自标注级别 + 代码读取标签扣配额\n")
    
    student_id = input("学生名字：").strip()
    problem_id = input("题目编号（如 P1001）：").strip()
    
    quota = load_quota(student_id, problem_id)
    remaining = quota["max"] - quota["count"]
    print(f"\n开始辅导 {student_id} 的 {problem_id}")
    print(f"当前配额：{remaining}/{quota['max']} 次提示\n")
    print("输入 'quit' 退出，输入 'reset' 重置配额\n")

    messages = []

    while True:
        user_input = input("学生：").strip()
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "reset":
            save_quota(student_id, problem_id, {"count": 0, "max": PER_PROBLEM_HINT_LIMIT})
            print(f"✅ 已重置 {problem_id} 的配额\n")
            continue
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        reply_for_display, reply_for_history = chat(messages, student_id, problem_id)
        messages.append({"role": "assistant", "content": reply_for_history})

        print(f"\nAgent：{reply_for_display}\n")


if __name__ == "__main__":
    main()
