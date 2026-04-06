"""
Moonshot kimi-k2.5 意图预分类器 (禁思考版本)
职责：对学生原始输入做意图分类，补充关键词匹配的盲区

输出只能是：direct / type_confirm / bridge / substantive / None(失败)

规则：只降级，不升档
- direct → 压到 L1
- type_confirm → 最多 L2
- bridge → bridge_redline=True
- substantive → 严格 no-op

失败时不影响主链路，走代码层兜底
"""

import os
import re
import time
from threading import Lock
from typing import Optional
from model_config import get_model_candidates, is_model_unavailable_error

# 有效的分类标签
VALID_LABELS = ["direct", "type_confirm", "bridge", "substantive"]

# Moonshot API 配置
MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"
CACHE_TTL_SECONDS = 600.0
DEFAULT_CLASSIFIER_MODELS = ("kimi-k2.5",)

_client = None
_client_lock = Lock()
_cache_lock = Lock()
_intent_cache = {}

# 分类器系统提示词 - 轻量级，只输出标签
CLASSIFIER_SYSTEM_PROMPT = """你是一个意图分类器。

请把学生输入分类到以下4个标签之一：
direct
type_confirm
bridge
substantive

判定规则：
- direct：直接索取答案、代码、完整做法
- type_confirm：猜测或确认题型/方法，例如"这题是DP吗""应该用二分吧"
- bridge：索取关键桥梁，例如"状态怎么定义""转移怎么写""check怎么写"
- substantive：给出了具体尝试、具体定义、具体错误、具体 case

输出规则：
- 只能输出一个标签
- 不要解释
- 不要输出多余文字
- 不要输出标点
- 如果不确定，也必须在这4个标签中选一个最接近的"""


def _log_classifier(status: str, **kwargs) -> None:
    parts = [f"{key}={value}" for key, value in kwargs.items()]
    suffix = " " + " ".join(parts) if parts else ""
    print(f"[classifier] {status}{suffix}")


def _normalize_cache_key(user_input: str) -> str:
    text = re.sub(r"\s+", " ", (user_input or "").strip().lower())
    return text


def _get_client():
    global _client
    if _client is not None:
        return _client

    with _client_lock:
        if _client is not None:
            return _client

        api_key = os.environ.get("MOONSHOT_API_KEY", "")
        if not api_key:
            return None

        from openai import OpenAI

        _client = OpenAI(
            api_key=api_key,
            base_url=MOONSHOT_BASE_URL,
            max_retries=0,  # 禁用重试，实现快失败
        )
        return _client


def _get_cached_result(cache_key: str):
    now = time.time()
    with _cache_lock:
        cached = _intent_cache.get(cache_key)
        if not cached:
            return False, None

        expires_at, cached_result = cached
        if expires_at <= now:
            _intent_cache.pop(cache_key, None)
            return False, None

        return True, cached_result


def _set_cached_result(cache_key: str, result: Optional[str]) -> None:
    expires_at = time.time() + CACHE_TTL_SECONDS
    with _cache_lock:
        _intent_cache[cache_key] = (expires_at, result)


def classify_intent(user_input: str, timeout: float = 5.0) -> Optional[str]:
    """
    使用 Moonshot kimi-k2.5 (禁思考) 对学生输入进行意图分类
    
    Args:
        user_input: 学生原始输入
        timeout: 超时时间（秒），默认 5 秒
    
    Returns:
        分类标签: direct / type_confirm / bridge / substantive
        失败或超时时返回 None
    """
    cache_key = _normalize_cache_key(user_input)
    input_len = len((user_input or "").strip())
    started_at = time.perf_counter()

    cache_hit, cached_result = _get_cached_result(cache_key)
    if cache_hit:
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        _log_classifier(
            "ok",
            input_len=input_len,
            cache="hit",
            elapsed_ms=elapsed_ms,
            result=cached_result if cached_result is not None else "none",
        )
        return cached_result

    client = _get_client()
    if client is None:
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        _set_cached_result(cache_key, None)
        _log_classifier(
            "fail",
            input_len=input_len,
            cache="miss",
            elapsed_ms=elapsed_ms,
            reason="no_api_key",
        )
        return None

    last_error = None
    candidates = get_model_candidates("NOI_CLASSIFIER_MODELS", DEFAULT_CLASSIFIER_MODELS)

    for model_name in candidates:
        try:
            request_kwargs = {
                "model": model_name,
                "max_completion_tokens": 16,
                "messages": [
                    {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                "timeout": timeout,
            }
            if "k2" in model_name.lower():
                request_kwargs["extra_body"] = {
                    "thinking": {"type": "disabled"}
                }

            response = client.chat.completions.create(**request_kwargs)

            content = response.choices[0].message.content
            if not content:
                continue

            cleaned = content.strip().lower()
            cleaned = cleaned.replace("\n", " ").replace("\r", "")
            cleaned = cleaned.rstrip(".!?。！？")

            for label in VALID_LABELS:
                if cleaned == label:
                    _set_cached_result(cache_key, label)
                    elapsed_ms = int((time.perf_counter() - started_at) * 1000)
                    _log_classifier(
                        "ok",
                        input_len=input_len,
                        cache="miss",
                        elapsed_ms=elapsed_ms,
                        result=label,
                        model=model_name,
                    )
                    return label

            last_error = ValueError("invalid_output")
        except Exception as exc:
            last_error = exc
            if not is_model_unavailable_error(exc):
                break

    _set_cached_result(cache_key, None)
    elapsed_ms = int((time.perf_counter() - started_at) * 1000)
    if last_error and "timed out" in str(last_error).lower():
        reason = "timeout"
    elif last_error and str(last_error) == "invalid_output":
        reason = "invalid_output"
    else:
        reason = "api_error"
    _log_classifier(
        "fail",
        input_len=input_len,
        cache="miss",
        elapsed_ms=elapsed_ms,
        reason=reason,
    )
    return None


# 简单的本地 fallback 分类（关键词匹配，用于测试或分类器失败时）
def classify_intent_fallback(user_input: str) -> Optional[str]:
    """
    本地关键词 fallback 分类
    当 Moonshot 分类器失败时使用
    """
    text = user_input.lower()
    
    # direct
    direct_keywords = ["给我代码", "给我答案", "直接告诉我", "帮我写", "怎么做"]
    for kw in direct_keywords:
        if kw in text:
            return "direct"
    
    # type_confirm
    type_confirm_patterns = [
        "是", "吗？", "对不对", "应该", "吧？",
        "字符串", "dp", "二分", "图论", "贪心", "递归"
    ]
    if any(p in text for p in type_confirm_patterns[:4]):
        if any(p in text for p in type_confirm_patterns[4:]):
            return "type_confirm"
    
    # bridge
    bridge_keywords = [
        "状态怎么", "转移怎么", "check怎么", "怎么定义",
        "push_up", "push_down", "lazy怎么", "base case"
    ]
    for kw in bridge_keywords:
        if kw in text:
            return "bridge"
    
    return None


if __name__ == "__main__":
    # 测试
    test_cases = [
        ("给我代码", "direct"),
        ("这题是DP吗？", "type_confirm"),
        ("状态怎么定义", "bridge"),
        ("我写了dp[i]=dp[i-1]但WA了", "substantive"),
    ]
    
    print("=== Moonshot kimi-k2.5 分类器测试 ===")
    all_passed = True
    for text, expected in test_cases:
        result = classify_intent(text)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} 输入: {text!r:<30} -> 结果: {result} (期望: {expected})")
    
    print()
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试未通过，检查输出是否严格匹配")
