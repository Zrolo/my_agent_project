"""
AI Review Engine - 生成结构化的学习复盘
"""

import os
import json
import re
from openai import OpenAI

_client = None

# 无效关键词列表
INVALID_KEYWORDS = ["不会", "没思路", "不知道", "不懂", "太难了"]


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("MOONSHOT_API_KEY")
        if not api_key:
            raise RuntimeError("MOONSHOT_API_KEY environment variable not set")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
    return _client


def validate_bottleneck(bottleneck_text: str) -> tuple[bool, str]:
    """
    校验卡点描述是否合格
    
    Returns:
        (is_valid, error_message)
        is_valid: True 表示通过校验，False 表示被拒绝
        error_message: 如果 is_valid=False，返回错误提示；否则返回空字符串
    """
    if not bottleneck_text:
        return False, "卡点描述不能为空"
    
    text = bottleneck_text.strip()
    
    if len(text) < 15:
        return False, "卡点描述太短（至少15字）。请具体描述：卡在哪一步、用了什么方法、遇到什么错误"
    
    # 屏蔽无效描述（够长但包含无效关键词且长度不足30）
    if any(kw in text for kw in INVALID_KEYWORDS) and len(text) < 30:
        return False, '描述有点笼统。请参考示例："知道是背包问题，但不确定状态是 dp[i][j] 还是 dp[i][j][k]，看了题解才知道只需要二维"'
    
    return True, ""


def _call_llm(prompt: str) -> tuple[bool, str]:
    """
    调用 LLM 获取回复
    
    Returns:
        (success, content)
        success: True 表示调用成功，False 表示失败
    """
    try:
        response = get_client().chat.completions.create(
            model="kimi-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return True, response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[review_engine] LLM call failed: {e}")
        return False, ""


def _parse_review(text: str) -> dict:
    """解析 LLM 返回的复盘内容"""
    result = {
        "error_tags": [],
        "diagnosis": "",
        "next_action": "",
        "suggested_topic": ""
    }
    
    # 解析错误标签
    error_match = re.search(r'错误标签[:：]\s*(.+?)(?=\n|$)', text)
    if error_match:
        tags_text = error_match.group(1).strip()
        # 支持逗号或顿号分隔
        result["error_tags"] = [t.strip() for t in re.split(r'[,，、]', tags_text) if t.strip()]
    
    # 解析问题诊断
    diagnosis_match = re.search(r'问题诊断[:：]\s*(.+?)(?=下一步行动|$)', text, re.DOTALL)
    if diagnosis_match:
        result["diagnosis"] = diagnosis_match.group(1).strip()
    
    # 解析下一步行动
    next_match = re.search(r'下一步行动[:：]\s*(.+?)(?=推荐专题|$)', text, re.DOTALL)
    if next_match:
        result["next_action"] = next_match.group(1).strip()
    
    # 解析推荐专题
    topic_match = re.search(r'推荐专题[:：]\s*(.+)$', text, re.DOTALL)
    if topic_match:
        result["suggested_topic"] = topic_match.group(1).strip()
    
    return result


def generate_review(
    problem_title: str,
    oj_source: str,
    completion_status: str,
    bottleneck_text: str,
    error_types: list,
    reflection: str = None,
) -> dict:
    """
    根据打卡信息生成 AI 复盘
    
    Returns:
        {
            "ok": True/False,
            "kind": "success" | "validation_error" | "llm_unavailable",
            "review": {...},  # kind="success" 时有
            "message": "..."  # 错误提示或成功消息
        }
    """
    # 前置业务校验
    is_valid, error_msg = validate_bottleneck(bottleneck_text)
    if not is_valid:
        return {
            "ok": False,
            "kind": "validation_error",
            "message": error_msg
        }
    
    # 构建提示
    prompt = f"""你是一位经验丰富的 NOI 信息学竞赛教练。请根据学生的打卡信息，生成一份结构化的复盘报告。

【题目信息】
- 题目：{problem_title}
- 来源：{oj_source}
- 完成状态：{"独立完成" if completion_status == "independent" else "需要提示" if completion_status == "hinted" else "看题解" if completion_status == "editorial" else "未完成"}

【学生反馈】
- 卡点描述：{bottleneck_text}
- 错误类型：{', '.join(error_types)}
{f"- 反思总结：{reflection}" if reflection else ""}

请按以下格式输出复盘报告（注意：不要输出任何标题或格式标记，只输出内容）：

错误标签：<1-3个关键词，如"DP优化, 状态设计, 单调栈">
问题诊断：<具体问题分析，50-100字>
下一步行动：<具体可执行的建议，30-50字>
推荐专题：<建议刷的相关题目或知识点>
"""
    
    # 调用 LLM
    llm_success, content = _call_llm(prompt)
    
    if not llm_success:
        return {
            "ok": False,
            "kind": "llm_unavailable",
            "message": "AI 复盘服务暂时不可用，你的打卡已保存，请稍后查看或联系老师"
        }
    
    # 解析结果
    review = _parse_review(content)
    
    # 如果解析失败，使用原始内容
    if not review["diagnosis"]:
        review["diagnosis"] = content[:200] if len(content) > 200 else content
    
    # 清理内容
    review["diagnosis"] = review["diagnosis"].strip()
    review["next_action"] = review["next_action"].strip()
    review["suggested_topic"] = review["suggested_topic"].strip()
    
    return {
        "ok": True,
        "kind": "success",
        "review": review,
        "message": "复盘生成成功"
    }


if __name__ == "__main__":
    # 测试校验函数
    print("=== 测试校验函数 ===")
    print(validate_bottleneck("不会"))  # 应该失败
    print(validate_bottleneck("我不知道怎么做这道题"))  # 应该失败（<30字且含无效词）
    print(validate_bottleneck("我知道是背包问题，但不确定状态转移方程怎么写"))  # 应该通过
