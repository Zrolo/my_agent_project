"""
第二课：工具调用（Function Calling）
目标：让 Agent 能调用外部工具，从"聊天机器人"升级为真正的 Agent

核心概念：
- Agent = LLM + 工具列表 + 执行循环
- LLM 决定"调不调用工具、调哪个、传什么参数"
- 代码决定"真正执行工具并把结果还给 LLM"
"""

import json
import os
import math
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.cn/v1"
)

# ============================================================
# 第一步：定义真实的工具函数
# ============================================================
def count_day_to_noi(year:int) -> str:
    nowday = datetime.now()
    target_day = datetime(year,10,15)
    delta = abs(target_day- nowday)
    return f"还有{delta.days}天"


def get_current_time() -> str:
    """返回当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    """
    计算数学表达式
    支持：+ - * / ** sqrt abs
    """
    try:
        # 安全计算：只允许数学运算
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed["abs"] = abs
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"


def search_knowledge(query: str) -> str:
    """
    模拟知识库搜索（真实项目里接向量数据库）
    """
    knowledge = {
        "python": "Python 是一种高级编程语言，以简洁易读著称。",
        "agent": "AI Agent 是能感知环境、做出决策并执行行动的 AI 系统。",
        "kimi": "Kimi 是月之暗面开发的大语言模型，支持长文本处理。",
        "function calling": "Function Calling 是让 LLM 调用外部函数的机制，是构建 Agent 的核心技术。",
    }
    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return value
    return f"未找到关于 '{query}' 的知识，请换个关键词。"


# ============================================================
# 第二步：用 JSON Schema 描述工具（告诉 LLM 有哪些工具可用）
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "count_day_to_noi",
            "description": "距离noi还有多长时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "noi 举行的年份"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，支持加减乘除、幂运算、sqrt、abs 等",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如：'2 ** 10' 或 'sqrt(144)'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "在知识库中搜索信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# ============================================================
# 第三步：工具分发器（根据 LLM 的选择，执行对应函数）
# ============================================================

TOOL_REGISTRY = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "search_knowledge": search_knowledge,
    "count_day_to_noi": count_day_to_noi,
}

def execute_tool(tool_name: str, tool_args: dict) -> str:
    """执行工具并返回结果字符串"""
    if tool_name not in TOOL_REGISTRY:
        return f"未知工具：{tool_name}"
    func = TOOL_REGISTRY[tool_name]
    return func(**tool_args)


# ============================================================
# 第四步：Agent 主循环（关键！）
#
# 流程：
#   用户输入
#     ↓
#   LLM 判断：直接回复 OR 调用工具
#     ↓（调用工具时）
#   执行工具 → 把结果还给 LLM
#     ↓
#   LLM 根据工具结果生成最终回复
#     ↓
#   输出给用户
# ============================================================

def agent_chat(messages: list, user_input: str) -> str:
    """一次完整的 Agent 对话（含工具调用循环）"""
    messages.append({"role": "user", "content": user_input})

    # 最多允许 5 轮工具调用，防止死循环
    for _ in range(5):
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个能使用工具的 AI 助手。需要时主动调用工具获取信息，不要猜测。"}
            ] + messages,
            tools=TOOLS,
            tool_choice="auto",  # 让 LLM 自己决定是否调用工具
        )

        msg = response.choices[0].message

        # 情况 1：LLM 决定直接回复，不调用工具
        if not msg.tool_calls:
            reply = msg.content
            messages.append({"role": "assistant", "content": reply})
            return reply

        # 情况 2：LLM 要调用工具
        # 先把 LLM 的"我要调用工具"意图加入历史
        messages.append(msg)

        # 执行每个工具调用
        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"  [调用工具] {tool_name}({tool_args})")
            result = execute_tool(tool_name, tool_args)
            print(f"  [工具结果] {result}")

            # 把工具结果追加到历史，LLM 下一轮会看到
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        # 继续循环，让 LLM 根据工具结果生成回复

    return "工具调用次数超限，请重新提问。"


def main():
    print("=== 工具 Agent（第二课）===")
    print("我能使用工具：获取时间、计算数学、搜索知识")
    print("试试问：'现在几点？' '计算 2的10次方' '什么是 Function Calling'")
    print("输入 'quit' 退出\n")

    messages = []

    while True:
        user_input = input("你: ").strip()
        if user_input.lower() == "quit":
            print("再见！")
            break
        if not user_input:
            continue

        reply = agent_chat(messages, user_input)
        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    main()
