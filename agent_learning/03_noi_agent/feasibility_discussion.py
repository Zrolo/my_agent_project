"""
多 Agent 方案可行性讨论
Agent A：质疑者，专门找方案的漏洞和风险
Agent B：支持者，为方案辩护并提出改进
Agent C：督导，给出最终可行性结论
"""

import os
import json
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

# 读取方案文档
PROPOSAL_PATH = "../../noi_teaching_agent_proposal.md"
with open(PROPOSAL_PATH, "r", encoding="utf-8") as f:
    PROPOSAL = f.read()

# ============================================================
# 三个 Agent 的角色设定
# ============================================================
SKEPTIC_PROMPT = f"""你是一个经验丰富的产品经理，专门质疑方案的可行性。
你正在评审一个 NOI 竞赛教练 AI Agent 的项目方案。

方案内容：
{PROPOSAL}

你的任务：
1. 每轮只提出 1-2 个最致命的质疑
2. 质疑要具体，说明为什么这个假设可能不成立
3. 重点关注：技术复杂度是否低估、用户接受度假设是否合理、时间线是否可行
4. 语气犀利，不客气"""

ADVOCATE_PROMPT = f"""你是这个 NOI 竞赛教练 AI Agent 方案的负责人。
方案内容：
{PROPOSAL}

你的任务：
1. 认真回应质疑者的每个问题
2. 如果质疑有道理，承认并提出修正方案
3. 如果质疑过于悲观，用数据或逻辑反驳
4. 每轮回复控制在 200 字以内"""

SUPERVISOR_PROMPT = """你是一个资深的技术顾问，负责对这场可行性讨论给出最终结论。
你的任务：
1. 列出方案中已被确认的核心风险（按严重程度排序）
2. 列出方案的真实优势（不要客套话）
3. 给出最终可行性评级：
   - 🟢 可行（建议直接推进）
   - 🟡 有条件可行（需要先解决XX问题）
   - 🔴 风险过高（建议大幅修改后再推进）
4. 给出最关键的3条行动建议
格式清晰，方便人工决策。"""


def call_agent(system_prompt: str, messages: list) -> str:
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "system", "content": system_prompt}] + messages,
        temperature=0.6,
    )
    return response.choices[0].message.content


def save_log(log: list):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"feasibility_log_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"\n讨论记录已保存：{filename}")
    return filename


def run_discussion(rounds: int = 3):
    print("=" * 60)
    print("NOI Agent 方案可行性讨论")
    print("=" * 60)

    skeptic_messages = []
    advocate_messages = []
    log = []

    skeptic_messages.append({"role": "user", "content": "请开始质疑，说出你认为最致命的问题。"})

    for i in range(1, rounds + 1):
        print(f"\n--- 第 {i} 轮 ---")

        # Agent A：质疑
        skeptic_reply = call_agent(SKEPTIC_PROMPT, skeptic_messages)
        print(f"\n[质疑者]：{skeptic_reply}")
        skeptic_messages.append({"role": "assistant", "content": skeptic_reply})
        advocate_messages.append({"role": "user", "content": skeptic_reply})
        log.append({"round": i, "role": "质疑者", "content": skeptic_reply})

        # Agent B：辩护
        advocate_reply = call_agent(ADVOCATE_PROMPT, advocate_messages)
        print(f"\n[支持者]：{advocate_reply}")
        advocate_messages.append({"role": "assistant", "content": advocate_reply})
        skeptic_messages.append({"role": "user", "content": advocate_reply})
        log.append({"round": i, "role": "支持者", "content": advocate_reply})

    # Agent C：督导总结
    print("\n--- 督导最终结论 ---")
    full_discussion = "\n\n".join(
        [f"第{e['round']}轮 [{e['role']}]：{e['content']}" for e in log]
    )
    supervisor_reply = call_agent(
        SUPERVISOR_PROMPT,
        [{"role": "user", "content": f"讨论记录：\n\n{full_discussion}\n\n请给出最终可行性结论。"}]
    )
    print(f"\n[督导]：{supervisor_reply}")
    log.append({"round": "总结", "role": "督导", "content": supervisor_reply})

    print("\n" + "=" * 60)
    filename = save_log(log)
    print(f"把 {filename} 发给人工督导审查。")


if __name__ == "__main__":
    rounds = int(input("讨论几轮？（建议3轮）：") or "3")
    run_discussion(rounds)
