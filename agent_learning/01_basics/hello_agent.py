"""
第一个 AI Agent
目标：理解 Agent 最核心的概念——对话循环
"""

from openai import OpenAI
import os

# 初始化客户端（Kimi API 兼容 OpenAI 格式）
client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.cn/v1"
)

def chat(messages: list, user_input: str) -> str:
    """发送消息给 Kimi，返回回复"""
    messages.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "system", "content": "你是一个友好的 AI 助手，帮助用户学习 AI Agent 开发。"}] + messages,
        max_tokens=1024,
    )

    reply = response.choices[0].message.content

    # 把 AI 的回复也加入历史记录（这就是"记忆"的最基础形式）
    messages.append({
        "role": "assistant",
        "content": reply
    })

    return reply


def main():
    print("=== 你的第一个 AI Agent ===")
    print("输入 'quit' 退出\n")

    messages = []  # 对话历史

    while True:
        user_input = input("你: ").strip()

        if user_input.lower() == "quit":
            print("再见！")
            break

        if not user_input:
            continue

        reply = chat(messages, user_input)
        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    main()
