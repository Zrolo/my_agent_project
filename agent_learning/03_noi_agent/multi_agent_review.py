"""
多 Agent 代码评审：让两个 AI 互相讨论 noi_agent.py
Agent A：严格的代码评审者，专门找问题
Agent B：实现者，回应问题并提出改进方案
Agent C：督导，最终总结并给出行动清单（存文件供人工审查）
"""

import os
import json
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

# 读取要讨论的代码
with open("noi_agent.py", "r", encoding="utf-8") as f:
    CODE = f.read()

# ============================================================
# 两个 Agent 的身份设定
# ============================================================
REVIEWER_PROMPT = f"""你是一个严格的代码评审者，专注于发现问题。
你正在评审一个 NOI 竞赛教练 AI Agent 的代码。

代码如下：
```python
{CODE}
```

你的任务：
1. 每轮只提出 1-2 个具体问题（不要一次说太多）
2. 问题要具体，指出代码的哪一行或哪个逻辑有问题
3. 重点关注：配额扣减时机、防绕过漏洞、边界情况
4. 语气直接，不废话"""

IMPLEMENTER_PROMPT = f"""你是这段 NOI 竞赛教练 Agent 代码的实现者。
代码如下：
```python
{CODE}
```

你的任务：
1. 认真回应评审者提出的每个问题
2. 如果问题有效，给出具体的修改方案（直接写修改后的代码片段）
3. 如果你不同意，解释原因
4. 每轮回复控制在 150 字以内，简洁"""


SUPERVISOR_PROMPT = """你是一个技术督导，负责总结一场代码评审讨论。
你的任务：
1. 归纳出讨论中发现的所有有效问题（按优先级排序）
2. 列出具体的待办事项（TODO list），每条都要可执行
3. 标出哪些问题已经有了解决方案，哪些还悬而未决
4. 最后给整体代码质量打分（1-10分）并说明理由
格式要清晰，方便人工审查。"""


def call_agent(system_prompt: str, messages: list) -> str:
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "system", "content": system_prompt}] + messages,
        temperature=0.5,
    )
    return response.choices[0].message.content


def save_log(log: list):
    """把讨论记录存到文件，方便拿给人工督导审查"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"review_log_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"\n讨论记录已保存到：{filename}")
    return filename


# ============================================================
# 多轮讨论主循环
# ============================================================
def run_discussion(rounds: int = 3):
    print("=" * 60)
    print("多 Agent 代码评审开始")
    print("=" * 60)

    reviewer_messages = []
    implementer_messages = []
    log = []  # 记录所有对话

    opening = "请开始评审，指出你认为最关键的问题。"
    reviewer_messages.append({"role": "user", "content": opening})

    for i in range(1, rounds + 1):
        print(f"\n--- 第 {i} 轮 ---")

        # Agent A：评审者
        reviewer_reply = call_agent(REVIEWER_PROMPT, reviewer_messages)
        print(f"\n[评审者]：{reviewer_reply}")
        reviewer_messages.append({"role": "assistant", "content": reviewer_reply})
        implementer_messages.append({"role": "user", "content": reviewer_reply})
        log.append({"round": i, "role": "评审者", "content": reviewer_reply})

        # Agent B：实现者
        implementer_reply = call_agent(IMPLEMENTER_PROMPT, implementer_messages)
        print(f"\n[实现者]：{implementer_reply}")
        implementer_messages.append({"role": "assistant", "content": implementer_reply})
        reviewer_messages.append({"role": "user", "content": implementer_reply})
        log.append({"round": i, "role": "实现者", "content": implementer_reply})

    # Agent C：督导总结
    print("\n--- 督导总结 ---")
    full_discussion = "\n\n".join(
        [f"第{e['round']}轮 [{e['role']}]：{e['content']}" for e in log]
    )
    supervisor_reply = call_agent(
        SUPERVISOR_PROMPT,
        [{"role": "user", "content": f"以下是完整的讨论记录：\n\n{full_discussion}\n\n请给出你的总结。"}]
    )
    print(f"\n[督导]：{supervisor_reply}")
    log.append({"round": "总结", "role": "督导", "content": supervisor_reply})

    print("\n" + "=" * 60)
    print("讨论结束")
    print("=" * 60)

    # 保存记录文件
    filename = save_log(log)
    print(f"\n把 {filename} 发给人工督导（Claude）审查，获取最终意见。")


if __name__ == "__main__":
    rounds = int(input("讨论几轮？（建议3轮）：") or "3")
    run_discussion(rounds)
