"""
AI Review Engine - 生成结构化的学习复盘
"""

import os
import json
import re
from pathlib import Path
from openai import OpenAI
from model_config import get_model_candidates, is_model_unavailable_error

BASE_DIR = Path(__file__).resolve().parent
_client = None
_review_clients = {}
_external_bridge_snippets_cache = None


def load_local_env_if_present(env_path: str | None = None) -> list[str]:
    """Load simple KEY=VALUE lines from .env without overriding real environment."""
    path = Path(env_path) if env_path else BASE_DIR / ".env"
    if not path.exists():
        return []

    loaded: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key or key in os.environ:
            continue
        os.environ[key] = value
        loaded.append(key)
    return loaded


load_local_env_if_present()

DEFAULT_REVIEW_MODELS = ("deepseek-v4-pro",)
LLM_REQUEST_TIMEOUT_SECONDS = int(os.getenv("NOI_LLM_TIMEOUT_SECONDS", "45"))
LLM_MAX_TOKENS = int(os.getenv("NOI_REVIEW_MAX_TOKENS", "32768"))
REVIEW_TAG_LIMIT = int(os.getenv("NOI_REVIEW_TAG_LIMIT", "2"))
REVIEW_CONTEXT_CHAR_LIMIT = int(os.getenv("NOI_REVIEW_CONTEXT_CHAR_LIMIT", "180"))
REVIEW_CARD_CHAR_LIMIT = int(os.getenv("NOI_REVIEW_CARD_CHAR_LIMIT", "220"))
REVIEW_REFLECTION_CHAR_LIMIT = int(os.getenv("NOI_REVIEW_REFLECTION_CHAR_LIMIT", "100"))
REVIEW_CHAT_CONTEXT_CHAR_LIMIT = int(os.getenv("NOI_REVIEW_CHAT_CONTEXT_CHAR_LIMIT", "0"))
REVIEW_CODE_CHAR_LIMIT = int(os.getenv("NOI_REVIEW_CODE_CHAR_LIMIT", "800"))
ANALYSIS_VERSION_V1 = "v1"

# 无效关键词列表
INVALID_KEYWORDS = ["不会", "没思路", "不知道", "不懂", "太难了"]
DETAIL_SIGNAL_KEYWORDS = {
    "题意",
    "条件",
    "样例",
    "状态",
    "转移",
    "边界",
    "特判",
    "数组",
    "越界",
    "溢出",
    "复杂度",
    "代码",
    "报错",
    "提交",
    "check",
    "贪心",
    "背包",
    "二分",
    "dp",
    "图",
    "建模",
    "递归",
    "枚举",
    "排序",
    "最短路",
    "前缀和",
    "并查集",
    "dfs",
    "bfs",
    "wa",
    "tle",
    "re",
}
ERROR_LAYERS = {
    "reading",
    "method",
    "modeling",
    "core_design",
    "implementation",
    "insufficient",
}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
CORE_DESIGN_SUBTAGS = {
    "state_design",
    "transition_design",
    "greedy_basis",
    "check_condition",
    "enumeration_order",
    "tree_path_difference",
    "tree_diameter_candidates",
    "lazy_semantics",
}
GRAPH_HINT_TERMS = ("图", "边", "建图", "最短路", "最长路", "差分约束", "约束", "不等式")
CONSTRAINT_GRAPH_TERMS = ("差分约束", "不等式", "上下界", "先后限制", "大小关系", "约束", "同时满足", "并列约束", "谁限制谁")
DP_HINT_TERMS = ("状态", "转移", "背包", "dp", "容量", "体积", "价值", "物品", "时间")
IMPLEMENTATION_HINT_TERMS = (
    "边界",
    "特判",
    "数组",
    "越界",
    "下标",
    "长度",
    "空区间",
    "n=1",
    "样例",
    "提交",
    "wa",
    "tle",
    "re",
    "调试",
    "运行错误",
    "答案错误",
)
INSUFFICIENT_PATTERNS = (
    r"说不清.*卡在哪",
    r"不知道.*卡在哪",
    r"不知道.*哪里错",
    r"没有形成明确思路",
    r"暂时没有明确思路",
    r"只能描述到这里",
    r"也说不清",
)
GENERIC_TOPIC_TERMS = (
    "图论基础",
    "图论",
    "动态规划",
    "DP",
    "背包问题",
    "背包",
    "模型转化",
    "算法理解",
)
GENERIC_ACTION_TERMS = (
    "加强基础",
    "多做练习",
    "多做这类题",
    "加深理解",
    "重新学习",
    "重新思考",
    "再想一遍",
    "重新阅读题目",
    "系统学习",
    "从简单题开始",
)


def _load_external_bridge_snippets() -> list[dict]:
    global _external_bridge_snippets_cache
    if _external_bridge_snippets_cache is not None:
        return _external_bridge_snippets_cache

    docs_dir = Path(__file__).resolve().parent / "docs" / "common"
    unified_path = docs_dir / "bridge_external_snippets_v1.jsonl"
    if unified_path.exists():
        snippet_files = (unified_path,)
    else:
        snippet_files = (
            docs_dir / "cp_pdf_bridge_snippets_v1.jsonl",
            docs_dir / "oi_wiki_bridge_snippets_v1.jsonl",
        )
    rows: list[dict] = []
    for path in snippet_files:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    _external_bridge_snippets_cache = rows
    return rows


def _pick_external_bridge_snippet(bridge: str, snippet_type: str, source_family: str | None = None) -> dict | None:
    for row in _load_external_bridge_snippets():
        if str(row.get("bridge") or "") != bridge:
            continue
        if str(row.get("snippet_type") or "") != snippet_type:
            continue
        if source_family and str(row.get("source_family") or "") != source_family:
            continue
        return row
    return None


def _bridge_key_from_card_id(card_id: str) -> str | None:
    mapping = {
        "dp.state_design": "state_design",
        "binary_search.check_condition": "check_condition",
        "binary_search.left_bound": "left_bound_update",
        "string.trie.shared_prefix_merging": "shared_prefix_merging",
        "segment_tree.lazy_semantics": "lazy_semantics",
        "modeling.scale_estimation": "complexity_fit",
        "modeling.method_selection": "method_selection",
        "graph.tree_path_difference": "tree_path_difference",
    }
    return mapping.get(card_id)


def _append_sentence(base: str, sentence: str) -> str:
    base = str(base or "").strip()
    sentence = str(sentence or "").strip()
    if not sentence or sentence in base:
        return base
    if not base:
        return sentence
    return f"{base} {sentence}".strip()


def _review_bridge_prompt_constraint(
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
    error_types: list[str],
) -> str:
    focus_text = " ".join(
        filter(
            None,
            [
                problem_title,
                problem_context or "",
                bottleneck_text,
                " ".join(error_types or []),
            ],
        )
    )

    if _contains_any(
        focus_text,
        (
            "a[mid] == x",
            "a[mid]==x",
            "保留 mid",
            "保留mid",
            "最左",
            "左边界",
            "第一个等于",
            "第一个出现",
            "lower_bound",
            "r = mid",
            "右边界 = mid",
        ),
    ):
        return "首轮 bridge 约束：这次必须围着 `a[mid] == x` 时为什么还要保留 mid、继续往左找来讲，不要退回泛泛的二分边界。"

    if _contains_any(
        focus_text,
        (
            "check(mid)",
            "check（mid）",
            "check(",
            "可行",
            "当前 mid",
            "当前mid",
            "二分方向",
            "往哪边缩",
            "判定条件",
        ),
    ):
        return "首轮 bridge 约束：这次必须围着 `check(mid)` 在判断当前 mid 是否可行来讲，不要退回泛化复杂度说明。"

    if _contains_any(
        focus_text,
        (
            "经过次数",
            "结束次数",
            "公共前缀",
            "沿前缀路径",
            "前缀路径",
            "重看所有消息",
            "只沿前缀",
            "只沿当前前缀",
            "沿当前前缀",
            "节点计数",
            "trie 节点",
            "trie节点",
        ),
    ):
        return "首轮 bridge 约束：这次必须围着公共前缀、沿前缀路径、为什么不用重看所有消息来讲；如果是节点计数语境，至少点名经过次数或结束次数。"

    if _contains_any(
        focus_text,
        (
            "方法选择",
            "结构信号",
            "题面信号",
            "支持 trie",
            "支持trie",
            "猜可能要 trie",
            "猜可能要trie",
            "猜一个方法名",
            "为什么该用这个方法",
            "直接枚举",
            "复杂度",
            "规模",
            "范围",
            "前缀关系",
            "相同开头",
            "trie",
        ),
    ):
        return "首轮 bridge 约束：这次必须围着题面信号/结构信号来讲，不要退回“理解这个方法”这类空话；如果是 trie 语境，至少点名“相同开头”或“前缀关系”。"

    return ""


def _apply_external_teaching_bits_to_knowledge_card(bridge: str | None, selected: dict) -> dict:
    if not bridge:
        return selected
    misconception = _pick_external_bridge_snippet(bridge, "misconception")
    mini_example = _pick_external_bridge_snippet(bridge, "mini_example")
    if misconception:
        excerpt = str(misconception.get("excerpt") or "").strip()
        if excerpt:
            selected = {
                **selected,
                "bridge_explanation": _append_sentence(
                    selected.get("bridge_explanation", ""),
                    f"再提醒一个最容易误会的点：{excerpt}",
                ),
            }
    if mini_example:
        excerpt = str(mini_example.get("excerpt") or "").strip()
        if excerpt:
            selected = {
                **selected,
                "algorithm_overview": _append_sentence(
                    selected.get("algorithm_overview", ""),
                    f"再看一个最小例子：{excerpt}",
                ),
            }
    return selected


def _apply_external_teaching_bits_to_remedy(bridge: str | None, selected: dict) -> dict:
    if not bridge:
        return selected
    misconception = _pick_external_bridge_snippet(bridge, "misconception")
    mini_example = _pick_external_bridge_snippet(bridge, "mini_example")
    if misconception:
        excerpt = str(misconception.get("excerpt") or "").strip()
        if excerpt:
            selected = {
                **selected,
                "remedy_text": _append_sentence(
                    selected.get("remedy_text", ""),
                    f"再提醒一个最容易误会的点：{excerpt}",
                ),
            }
    if mini_example:
        excerpt = str(mini_example.get("excerpt") or "").strip()
        if excerpt:
            selected = {
                **selected,
                "remedy_text": _append_sentence(
                    selected.get("remedy_text", ""),
                    f"你可以先抓这个最小例子：{excerpt}",
                ),
            }
    return selected


def _augment_knowledge_card_with_external_snippets(card_id: str, selected: dict) -> dict:
    if card_id == "dp.state_design":
        explanation = _pick_external_bridge_snippet("state_design", "bridge_explanation", "oi-wiki")
        extra_view = _pick_external_bridge_snippet("state_design", "bridge_explanation", "cp-pdf")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("bridge_explanation", ""):
                selected = {
                    **selected,
                    "bridge_explanation": f"{selected['bridge_explanation']} 换个更直白的说法：{excerpt}",
                }
        if extra_view:
            excerpt = str(extra_view.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("algorithm_overview", ""):
                selected = {
                    **selected,
                    "algorithm_overview": f"{selected['algorithm_overview']} 再换个学生更容易抓住的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_knowledge_card("state_design", selected)

    if card_id == "binary_search.check_condition":
        explanation = _pick_external_bridge_snippet("check_condition", "bridge_explanation")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("bridge_explanation", ""):
                selected = {
                    **selected,
                    "bridge_explanation": f"{selected['bridge_explanation']} 换个更直白的说法：{excerpt}",
                }
        if "check(5)=true" not in selected.get("algorithm_overview", ""):
            selected = {
                **selected,
                "algorithm_overview": f"{selected['algorithm_overview']} 比如 `check(5)=true`，只说明“最小跳跃距离至少为 5”这件事当前还能做到，所以答案不小于 5。",
            }
        return _apply_external_teaching_bits_to_knowledge_card("check_condition", selected)

    if card_id == "binary_search.left_bound":
        explanation = _pick_external_bridge_snippet("left_bound_update", "bridge_explanation", "oi-wiki")
        extra_view = _pick_external_bridge_snippet("left_bound_update", "bridge_explanation", "cp-pdf")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("bridge_explanation", ""):
                selected = {
                    **selected,
                    "bridge_explanation": f"{selected['bridge_explanation']} 换个更直白的说法：{excerpt}",
                }
        if extra_view:
            excerpt = str(extra_view.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("algorithm_overview", ""):
                selected = {
                    **selected,
                    "algorithm_overview": f"{selected['algorithm_overview']} 再换个学生更容易抓住的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_knowledge_card("left_bound_update", selected)

    if card_id == "string.trie.shared_prefix_merging":
        explanation = _pick_external_bridge_snippet("shared_prefix_merging", "bridge_explanation", "oi-wiki")
        overview = _pick_external_bridge_snippet("shared_prefix_merging", "algorithm_overview", "cp-pdf")
        extra_view = _pick_external_bridge_snippet("shared_prefix_merging", "bridge_explanation", "cp-pdf")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("bridge_explanation", ""):
                selected = {
                    **selected,
                    "bridge_explanation": f"{selected['bridge_explanation']} 换成更白的话说，就是：{excerpt}",
                }
        if overview:
            excerpt = str(overview.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("algorithm_overview", ""):
                selected = {
                    **selected,
                    "algorithm_overview": f"{selected['algorithm_overview']} 换个更直白的图景：{excerpt}",
                }
        if extra_view:
            excerpt = str(extra_view.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("algorithm_overview", ""):
                selected = {
                    **selected,
                    "algorithm_overview": f"{selected['algorithm_overview']} 再换个学生更容易抓住的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_knowledge_card("shared_prefix_merging", selected)

    if card_id == "segment_tree.lazy_semantics":
        explanation = _pick_external_bridge_snippet("lazy_semantics", "bridge_explanation", "oi-wiki")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("bridge_explanation", ""):
                selected = {
                    **selected,
                    "bridge_explanation": f"{selected['bridge_explanation']} 换个更直白的说法：{excerpt}",
                }
        if "[1,4]" not in selected.get("algorithm_overview", ""):
            selected = {
                **selected,
                "algorithm_overview": f"{selected['algorithm_overview']} 比如一个节点管区间 `[1,4]`，`lazy=3` 就是在说这段区间每个数都还欠着 `+3` 没下传；如果左儿子长度是 `2`，pushdown 时左儿子的 `sum` 会先加 `3×2`。",
            }
        return _apply_external_teaching_bits_to_knowledge_card("lazy_semantics", selected)

    return _apply_external_teaching_bits_to_knowledge_card(_bridge_key_from_card_id(card_id), selected)


def _augment_remedy_with_external_snippets(focus: str, selected: dict) -> dict:
    if focus == "transition_design":
        explanation = _pick_external_bridge_snippet("transition_design", "bridge_explanation", "oi-wiki")
        extra_view = _pick_external_bridge_snippet("transition_design", "bridge_explanation", "cp-pdf")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 换个更直白的说法：{excerpt}",
                }
        if extra_view:
            excerpt = str(extra_view.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 再换个学生更容易抓住的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_remedy("transition_design", selected)

    if focus == "state_design":
        explanation = _pick_external_bridge_snippet("state_design", "bridge_explanation", "oi-wiki")
        extra_view = _pick_external_bridge_snippet("state_design", "bridge_explanation", "cp-pdf")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 换个更直白的说法：{excerpt}",
                }
        if extra_view:
            excerpt = str(extra_view.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 再换个学生更容易抓住的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_remedy("state_design", selected)

    if focus == "check_condition":
        explanation = _pick_external_bridge_snippet("check_condition", "bridge_explanation")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 换个更直白的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_remedy("check_condition", selected)

    if focus == "left_bound_update":
        explanation = _pick_external_bridge_snippet("left_bound_update", "bridge_explanation", "oi-wiki")
        extra_view = _pick_external_bridge_snippet("left_bound_update", "bridge_explanation", "cp-pdf")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 换个更直白的说法：{excerpt}",
                }
        if extra_view:
            excerpt = str(extra_view.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 再换个学生更容易抓住的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_remedy("left_bound_update", selected)

    if focus == "complexity_fit":
        explanation = _pick_external_bridge_snippet("complexity_fit", "bridge_explanation", "oi-wiki")
        extra_view = _pick_external_bridge_snippet("complexity_fit", "bridge_explanation", "cp-pdf")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 换个更直白的说法：{excerpt}",
                }
        if extra_view:
            excerpt = str(extra_view.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 再换个学生更容易抓住的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_remedy("complexity_fit", selected)

    if focus == "method_selection":
        explanation = _pick_external_bridge_snippet("method_selection", "bridge_explanation", "oi-wiki")
        if explanation:
            excerpt = str(explanation.get("excerpt") or "").strip()
            if excerpt and excerpt not in selected.get("remedy_text", ""):
                selected = {
                    **selected,
                    "remedy_text": f"{selected['remedy_text']} 换个更直白的说法：{excerpt}",
                }
        return _apply_external_teaching_bits_to_remedy("method_selection", selected)

    return _apply_external_teaching_bits_to_remedy(focus, selected)
GENERIC_REVIEW_TAG_TERMS = (
    "o2优化",
    "o3优化",
    "省选",
    "普及",
    "提高",
    "noip",
    "noi",
    "ioi",
    "usaco",
    "模板",
)
GENERIC_BRIDGE_TERMS = (
    "理解",
    "掌握",
    "学会",
)
GENERIC_TRANSFER_SIGNALS = (
    "遇到这类题",
    "看到这类题",
    "看到类似题",
    "遇到类似题",
    "下次遇到这种题",
)
TRANSFER_SIGNAL_TRIGGER_TERMS = (
    "规模",
    "结构",
    "约束",
    "目标",
    "状态",
    "范围",
    "上界",
    "下界",
    "不等式",
    "依赖",
    "顺序",
    "连通",
    "冲突",
    "单调",
    "路径",
    "子树",
    "区间",
)
HIGH_RISK_REVIEW_FOCI = {
    "general_modeling",
    "constraint_modeling",
    "greedy_basis",
    "method_selection",
    "tree_path_difference",
    "tree_diameter_candidates",
}
REVIEW_FOCUS_RULES = {
    "general_modeling": {
        "bridge_terms": ("对象", "关系", "点", "边", "谁和谁"),
        "step_terms": ("写", "标", "画", "对象", "关系", "点", "边"),
        "signal_terms": ("对象", "关系", "点", "边", "谁和谁"),
        "main_block": "你不是完全没思路，而是还没先把题目里的对象和关系写清楚，所以方法一直落不到地上。",
        "key_bridge": "关键不是先猜方法，而是先把题目里的对象和关系分开：哪些东西是对象，哪些关系把它们连起来；如果是图，再确认什么当点、什么当边。",
        "next_step": "先写两行：题目里哪些是对象，哪些关系把它们连起来；如果像图，再补一行标出什么当点、什么当边。",
        "transfer_signal": "如果题面一直在描述谁和谁发生关系、什么当点、什么当边，先不要急着猜算法，先把对象和关系写清楚。",
    },
    "constraint_modeling": {
        "bridge_terms": ("限制", "约束", "统一", "同时满足", "并列", "谁限制谁"),
        "step_terms": ("整理", "改写", "标", "限制", "约束", "谁限制谁", "同时满足"),
        "signal_terms": ("限制", "约束", "同时满足", "谁限制谁", "先后限制"),
        "main_block": "你不是不会图论，而是还没先把题目里的限制关系整理成统一形式，导致变量、方向和边权都混在一起。",
        "key_bridge": "关键不是先套方法，而是先把题目里的限制整理成统一形式，再确认这些条件是并列约束，还是谁在限制谁。",
        "next_step": "先把题面限制逐条整理成统一形式，再标出哪些条件要同时满足，或是谁在限制谁。",
        "transfer_signal": "如果题目一直在描述多个量之间的大小关系、上下界、同时满足或先后限制，先想能不能整理成统一约束。",
    },
    "method_selection": {
        "bridge_terms": ("规模", "范围", "信号", "特征", "n<=", "直接枚举", "复杂度"),
        "step_terms": ("圈", "看", "判断", "规模", "范围", "信号", "枚举"),
        "signal_terms": ("规模", "范围", "n<=", "数据范围", "直接枚举"),
        "main_block": "你不是完全不会做，而是还没先用题面里的规模和范围信号判断这题到底支不支持当前做法。",
        "key_bridge": "关键不是先报方法名，而是先看题面给出的规模、范围或结构信号，判断它是不是已经支持这种做法。",
        "next_step": "先圈出题面里的规模或范围信号，再判断它是不是已经支持直接枚举或当前方法，不要先套模板。",
        "transfer_signal": "如果题面先给了很小的规模、范围或明确上界，先别急着报方法名，先判断这些信号是不是已经支持直接枚举或当前做法。",
    },
    "greedy_basis": {
        "bridge_terms": ("优先", "不吃亏", "后续", "空间", "结束时间最早", "兼容"),
        "step_terms": ("画", "比较", "先选", "后续", "空间", "兼容", "最小例子"),
        "signal_terms": ("优先", "不吃亏", "后续", "空间", "兼容"),
        "main_block": "你不是不会背结论，而是还没先说明这个局部选择为什么不吃亏、为什么还能给后续留空间。",
        "key_bridge": "关键不是先记贪心结论，而是先说明为什么当前对象优先选不会吃亏，它给后续留下了什么空间。",
        "next_step": "先画一个最小例子，比较“先选它”和“先不选它”对后续空间或兼容性的影响，再写结论。",
        "transfer_signal": "如果题目在让你做局部优先选择，而且你需要解释为什么不会破坏后续兼容性，就先检查这一步是否在给后面留空间。",
    },
    "tree_diameter_candidates": {
        "bridge_terms": ("直径", "最长路", "候选", "新边", "连起来", "最远点"),
        "step_terms": ("画", "比较", "候选", "左边", "右边", "新边", "最远点"),
        "signal_terms": ("直径", "最长路", "新边", "两边", "连通块"),
        "main_block": "你不是完全不会树的直径，而是还没先把“加上一条新边后，新最长路会从哪些候选里产生”这一步站稳。",
        "key_bridge": "关键不是直接背公式，而是先确认：新最长路只可能来自左边内部、右边内部，或者经过新边把两边最远点接起来。",
        "next_step": "先把这三类候选画出来，再单独想：如果经过新边，两边各该接什么点。",
        "transfer_signal": "如果题目在问两棵树或两个连通块连起来后的最长路，先别急着套答案，先比较最长路会来自哪几类候选。",
    },
    "tree_path_difference": {
        "bridge_terms": ("树上差分", "路径贡献", "经过次数", "LCA", "最近公共祖先", "树剖", "树链剖分", "子树汇总"),
        "step_terms": ("打标记", "差分", "汇总", "DFS", "LCA", "端点", "父亲"),
        "signal_terms": ("多条路径", "树上路径", "经过次数", "路径加一", "LCA", "树剖"),
        "main_block": "你不是不会树剖或 LCA，而是还没先把“一条树上路径的贡献如何变成少数几个点的差分标记”这一步站稳。",
        "key_bridge": "关键不是逐点更新每条路径，而是把路径贡献转成端点、LCA 和 LCA 父亲附近的差分标记，再用 DFS 子树汇总还原每个点经过次数。",
        "next_step": "先只看一条 s 到 t 的路径：为什么可以在 s、t、lca 和 lca 的父亲附近打标记，而不是沿整条路径逐点加。",
        "transfer_signal": "如果题目给很多树上路径，并统计点或边被经过多少次，先想树上差分：端点/LCA 打标记，最后 DFS 汇总。",
    },
}

REVIEW_BRIDGE_GUARD_RULES = {
    "shared_prefix_merging": {
        "focus_terms": ("前缀", "沿前缀路径", "公共前缀", "重看所有消息"),
        "problem_focus": "你不是在做一般字符串处理，而是在分清公共前缀为什么能先合在一起，以及查询时为什么只沿前缀路径走。",
        "key_bridge": "关键是把相同开头先合在一起；这样查询时不用重看所有消息，只沿当前前缀那条路径往下走。",
        "visual_hint": "101\n100\n11\n前缀 10 先合在一起\n查询时只沿前缀路径往下走",
        "guided_walkthrough": "1. 先把 101、100、11 这三个串写出来，看前两条是不是有相同开头。\n2. 再想这些相同开头能不能先共用一段路径。\n3. 最后再说查询时为什么不用把所有消息重新逐个看一遍。",
        "try_now": "先只回答一句：trie 省下来的，为什么是“不用重看所有消息”而不是“把答案背下来”？",
    },
    "check_condition": {
        "focus_terms": ("check(mid)", "可行", "当前 mid", "返回 true"),
        "problem_focus": "你不是在直接算答案，而是在想 `check(mid)` 到底是不是只在判断当前这个 mid 是否可行。",
        "key_bridge": "关键是先站稳：`check(mid)` 的 true 只说明当前 mid 可行，不是已经找到最终答案。",
        "visual_hint": "check(5)=true\n-> 只说明 5 可行\n-> 再决定区间往哪边缩",
        "guided_walkthrough": "1. 先只看 `check(mid)` 这一句，它是不是只在判断当前 mid 能不能成立。\n2. 再把 true/false 分别翻成“当前值可行/不可行”。\n3. 最后再决定二分区间该往哪边缩。",
        "try_now": "先只回答一句：`check(5)=true` 现在说明的是“5 可行”还是“答案就是 5”？",
    },
    "left_bound_update": {
        "focus_terms": ("a[mid]", "保留 mid", "最左", "左边界"),
        "problem_focus": "你不是一般地不会二分，而是卡在 `a[mid] == x` 时，为什么还要把 mid 这一侧保留下来继续往左找。",
        "key_bridge": "关键是如果你要找最左边那个等于 x 的位置，命中后 mid 仍然可能就是答案，所以不能先丢掉。",
        "visual_hint": "[1,2,2,2,3]\na[mid] == 2\n-> mid 先留作候选\n-> r = mid 继续往左缩",
        "guided_walkthrough": "1. 先只盯 `a[mid] == x` 这一格，mid 现在是不是已经可能是答案。\n2. 如果目标是最左边那个位置，mid 这一侧能不能先丢掉。\n3. 最后再决定为什么要保留 mid 继续往左缩。",
        "try_now": "先只回答一句：如果目标是最左边那个 2，`a[mid] == 2` 时为什么不能先丢掉 mid？",
    },
    "method_selection": {
        "focus_terms": ("题面", "结构信号", "相同开头", "前缀关系"),
        "problem_focus": "你不是已经站稳 trie 机制，而是还没从题面里指出哪个结构信号真的在支持这个方法。",
        "key_bridge": "关键不是先报方法名，而是先回到题面，看见“很多消息有相同开头，而且还要反复按前缀查”这个信号。",
        "visual_hint": "题面信号\n-> 很多消息\n-> 反复前缀关系\n-> 相同开头支持 trie",
        "guided_walkthrough": "1. 先只看题面里有哪些对象和操作：消息、拦截串、前缀关系。\n2. 再找哪一个结构信号最直接支持 trie，而不是别的方法。\n3. 最后补一句：为什么“相同开头”会让 trie 变得合理。",
        "try_now": "先只指出一句：题面里哪个结构信号在支持 trie？",
    },
}

QUIZ_ROLE_MAIN = "main"
QUIZ_ROLE_FOLLOWUP = "followup"
QUIZ_ROLE_REMEDY = "remedy"
QUIZ_ROLE_CONFIRM = "confirm"
QUIZ_ROLE_KNOWLEDGE_CONFIRM = "knowledge_confirm"
STRUCTURAL_QUIZ_FOCI = {
    "state_design",
    "transition_design",
    "check_condition",
    "enumeration_order",
    "greedy_basis",
    "general_modeling",
    "constraint_modeling",
    "boundary_debug",
    "left_bound_update",
    "method_selection",
    "shared_prefix_merging",
    "lazy_semantics",
    "tree_path_difference",
    "data_type",
    "loop_boundary",
    "recursion_structure",
    "complexity_fit",
    "tree_diameter_candidates",
}
# Backward-compatible alias while the rest of the module is being migrated.
STRUCTURAL_CONFIRM_FOCI = STRUCTURAL_QUIZ_FOCI
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

REMEDY_ACTION_REPHRASE = "rephrase"
REMEDY_ACTION_SMALLER_EXAMPLE = "smaller_example"
REMEDY_ACTION_DYNAMIC = "dynamic_bridge_help"
REMEDY_ACTION_EASIER_QUIZ = "easier_quiz"

ALGORITHM_NAME_TERMS = (
    "最小生成树",
    "Kruskal",
    "kruskal",
    "Prim",
    "prim",
    "区间DP",
    "区间 dp",
    "树形DP",
    "树形 dp",
    "动态规划",
    "二分答案",
    "差分约束",
    "最短路",
    "Dijkstra",
    "dijkstra",
    "SPFA",
    "spfa",
    "LCA",
    "lca",
    "并查集",
    "Trie",
    "trie",
)


def _default_review_models() -> tuple[str, ...]:
    return (os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro"),)


def _review_provider_for_model(model_name: str | None) -> dict:
    normalized = (model_name or "").strip().lower()
    if normalized.startswith("deepseek"):
        return {
            "provider_id": "deepseek",
            "api_key_envs": ("DEEPSEEK_API_KEY",),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            "token_param": "max_tokens",
            "extra_body": {"thinking": {"type": "enabled"}},
        }
    if normalized.startswith("kimi") or normalized.startswith("moonshot/"):
        return {
            "provider_id": "moonshot",
            "api_key_envs": ("MOONSHOT_API_KEY", "OPENAI_API_KEY"),
            "base_url": os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1"),
            "token_param": "max_completion_tokens",
            "extra_body": None,
        }
    return {
        "provider_id": "openai_compatible",
        "api_key_envs": ("OPENAI_API_KEY",),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "token_param": "max_completion_tokens",
        "extra_body": None,
    }


def _first_env_value(keys: tuple[str, ...]) -> str:
    for key in keys:
        value = os.getenv(key, "").strip()
        if value:
            return value
    return ""


def is_review_llm_configured(model_name: str | None = None) -> bool:
    candidates = get_model_candidates("NOI_REVIEW_MODELS", _default_review_models())
    target_model = model_name or (candidates[0] if candidates else "")
    provider = _review_provider_for_model(target_model)
    return bool(_first_env_value(provider["api_key_envs"]))


def get_client(model_name: str | None = None):
    global _client
    target_model = model_name or _default_review_models()[0]
    provider = _review_provider_for_model(target_model)
    api_key = _first_env_value(provider["api_key_envs"])
    if not api_key:
        env_names = " 或 ".join(provider["api_key_envs"])
        raise RuntimeError(f"{env_names} environment variable not set")

    if provider["provider_id"] == "moonshot" and not model_name:
        if _client is None:
            _client = OpenAI(api_key=api_key, base_url=provider["base_url"])
        return _client

    cache_key = (provider["provider_id"], provider["base_url"], api_key[:8])
    if cache_key not in _review_clients:
        _review_clients[cache_key] = OpenAI(
            api_key=api_key,
            base_url=provider["base_url"],
        )
    return _review_clients[cache_key]


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

    lowered = text.lower()
    has_invalid_keyword = any(kw in text for kw in INVALID_KEYWORDS)
    has_detail_signal = any(keyword in lowered for keyword in DETAIL_SIGNAL_KEYWORDS)

    # 允许出现“不会/不知道”等词，只要学生已经给出了足够具体的算法或调试线索。
    if has_invalid_keyword and len(text) < 35 and not has_detail_signal:
        return False, '描述有点笼统。请补充你尝试过的方法、卡住的步骤，或出现的错误现象。'
    
    return True, ""


def _compact_text(text: str | None, limit: int) -> str:
    compact = re.sub(r"\s+", " ", str(text or "")).strip()
    if not compact or limit <= 0 or len(compact) <= limit:
        return compact
    if limit <= 1:
        return compact[:limit]
    return compact[: limit - 1] + "…"


def _compact_problem_card(problem_card: dict | None) -> str:
    if not problem_card:
        return ""

    preferred_keys = (
        "summary",
        "goal",
        "ask",
        "objects",
        "constraints",
        "key_relations",
        "method_clues",
        "pitfalls",
    )
    compact_card = {}
    for key in preferred_keys:
        if key in problem_card:
            compact_card[key] = problem_card[key]
    for key, value in problem_card.items():
        if key not in compact_card:
            compact_card[key] = value
        if len(compact_card) >= 6:
            break
    return _compact_text(json.dumps(compact_card, ensure_ascii=False), REVIEW_CARD_CHAR_LIMIT)


def _is_generic_review_tag(tag: str) -> bool:
    lowered = tag.lower()
    return any(term in lowered for term in GENERIC_REVIEW_TAG_TERMS)


def _select_review_tags(problem_tags: list | None, focus_text: str) -> list[str]:
    if not problem_tags:
        return []

    seen = set()
    indexed_tags = []
    focus_lower = focus_text.lower()
    for idx, raw_tag in enumerate(problem_tags):
        tag = str(raw_tag).strip()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        indexed_tags.append(
            {
                "tag": tag,
                "index": idx,
                "is_exact_match": tag.lower() in focus_lower,
                "is_generic": _is_generic_review_tag(tag),
            }
        )

    selected = [
        item["tag"]
        for item in indexed_tags
        if item["is_exact_match"] and not item["is_generic"]
    ][:REVIEW_TAG_LIMIT]

    if len(selected) >= REVIEW_TAG_LIMIT:
        return selected

    remaining = [
        item
        for item in indexed_tags
        if item["tag"] not in selected and not item["is_generic"]
    ]
    remaining.sort(key=lambda item: (-len(item["tag"]), item["index"]))
    for item in remaining:
        selected.append(item["tag"])
        if len(selected) >= REVIEW_TAG_LIMIT:
            break
    return selected


def _compact_student_code(student_code: str | None) -> str:
    code = (student_code or "").strip()
    if not code or len(code) <= REVIEW_CODE_CHAR_LIMIT:
        return code

    lines = code.splitlines()
    if len(lines) <= 12:
        head = max(120, int(REVIEW_CODE_CHAR_LIMIT * 0.6))
        tail = max(80, REVIEW_CODE_CHAR_LIMIT - head - 16)
        head_text = code[:head].rstrip()
        tail_text = code[-tail:].lstrip()
        return f"{head_text}\n...\n{tail_text}"

    focus_idx = None
    middle_start = max(0, len(lines) // 4)
    middle_end = min(len(lines), len(lines) * 3 // 4)
    formula_terms = ("return", "ans", "answer", "res", "dp", "mid", "check", "sum")
    for idx in range(middle_start, middle_end):
        line = lines[idx]
        lowered = line.lower()
        if "=" in line and any(term in lowered for term in formula_terms):
            focus_idx = idx
            break
        if any(op in line for op in ("+", "-", "*", "/", "%")) and "=" in line:
            focus_idx = idx
            break

    if focus_idx is None:
        focus_idx = len(lines) // 2

    head_lines = lines[:10]
    focus_start = max(0, focus_idx - 1)
    focus_end = min(len(lines), focus_idx + 2)
    focus_lines = lines[focus_start:focus_end]
    tail_lines = lines[-10:]

    compact_parts = ["\n".join(head_lines)]
    if focus_start > len(head_lines):
        compact_parts.append("...")
    compact_parts.append("\n".join(focus_lines))
    if focus_end < len(lines) - len(tail_lines):
        compact_parts.append("...")
    compact_parts.append("\n".join(tail_lines))
    compact = "\n".join(part for part in compact_parts if part).strip()

    if len(compact) <= REVIEW_CODE_CHAR_LIMIT + 120:
        return compact

    head = max(120, int(REVIEW_CODE_CHAR_LIMIT * 0.45))
    middle_window = max(120, int(REVIEW_CODE_CHAR_LIMIT * 0.25))
    tail = max(80, REVIEW_CODE_CHAR_LIMIT - head - middle_window - 24)
    focus_text = "\n".join(focus_lines).strip()
    compact_focus = focus_text[:middle_window].rstrip()
    head_text = code[:head].rstrip()
    tail_text = code[-tail:].lstrip()
    return f"{head_text}\n...\n{compact_focus}\n...\n{tail_text}"


def _detect_review_mode(completion_status: str, submission_result: str | None) -> str:
    """根据完成状态和提交结果，判断本次 review 属于哪个 mode。

    Family 归属：
        failure_diagnosis（学生尚未建立对当前题的主体性理解）
            failed_verdict     — submission_result in {wa, tle, re, ce}
            stuck_bridge       — completion_status in {unfinished, hinted}
            editorial_transfer — completion_status == editorial

        success_reflection（学生已自己走通，做泛化复盘）
            independent_reflect — fallback
    """
    submission_result = (submission_result or "unknown").strip().lower()
    if submission_result in {"wa", "tle", "re", "ce"}:
        return "failed_verdict"
    if completion_status == "editorial":
        return "editorial_transfer"
    if completion_status in {"unfinished", "hinted"}:
        return "stuck_bridge"
    return "independent_reflect"


def _family_for_review_mode(mode: str) -> str:
    """将四个 review mode 收敛为两大 family。"""
    if mode == "independent_reflect":
        return "success_reflection"
    return "failure_diagnosis"


def _build_normal_review_system_prompt(mode: str = "independent_reflect", handoff_payload: dict | None = None) -> str:
    """第一轮结构化复盘 prompt。"""
    return _build_review_system_prompt(mode=mode, handoff_payload=handoff_payload)


def _build_review_system_prompt(mode: str = "independent_reflect", handoff_payload: dict | None = None) -> str:
    """按 mode 构建 review system prompt。

    Mode → Family 映射（见 _detect_review_mode）：
        failure_diagnosis  — failed_verdict / stuck_bridge / editorial_transfer
        success_reflection — independent_reflect
    """
    base = """你是 NOI 教练，不是答案生成器。

你的主任务不是总结答案，而是基于学生提供的证据，帮助他跨过当前最关键的一步。
如果格式正确但没有帮助学生跨过这一步，这次输出就算失败。

先按 Evidence -> Decision -> Feedback 工作：

Evidence
- 先根据学生提供的题目、卡点、代码、提交现象，判断他当前已经会到哪一步、卡在哪一步。
- 必须使用学生输入里的具体对象、条件、错误现象或步骤作为依据。
- 如果证据不足，禁止直接讲题；默认按更保守、更小步的方式支架，只保留最小可判断范围。

Decision
- 每次只能解决一个当前桥梁，不同时展开多个难点。
- 你只能在学生当前状态基础上推进半步到一步。
- 如果不能确定学生当前已经会到哪一步，默认按更保守、更小步的方式支架。
- 禁止直接给完整答案、完整证明或完整代码。
- 如果你的输出已经让学生不需要自己补最后一步，说明支架过大，必须缩回。

Feedback
- 请根据题目信息、学生卡点和代码片段，输出一次简洁、可执行的复盘。
- 只输出 JSON，不要输出任何额外解释或 Markdown 代码块。

JSON 必须包含这些字段：
error_tags
error_layer
error_layer_confidence
core_design_subtags
diagnosis
next_action
suggested_topic
problem_focus
main_block
key_bridge
visual_hint
guided_walkthrough
try_now
next_step
transfer_signal
topic_commonality
solution_walkthrough
transfer_checklist

字段要求：
1. error_tags：1-3 个中文短词。
2. error_layer：reading|method|modeling|core_design|implementation|insufficient。
3. error_layer_confidence：high|medium|low。
4. core_design_subtags：只有 error_layer=core_design 时可填，值只能是 state_design|transition_design|greedy_basis|check_condition|enumeration_order|tree_path_difference|tree_diameter_candidates|lazy_semantics；否则输出 []。
5. diagnosis：直接指出核心问题，不复述题面。
6. next_action：老师布置的下一步训练。
7. suggested_topic：具体小专题，不要只写大类。
8. problem_focus：学生具体卡住的那一步。
9. main_block：兼容字段，内容与 problem_focus 保持一致。
10. key_bridge：先抓住什么关键事实，解释“为什么这题能这样做”的关键桥梁。
11. visual_hint：可选字段。只在有必要时输出一个文本化小图、小表或小分类框，帮助学生看清当前桥里的对象、关系或候选。禁止输出大段讲义，禁止直接给出最终比较结果、最终结论或完整答案；优先写估算、分类、对比前的半成品提示。
12. guided_walkthrough：跟我走一遍，固定写 2-3 步微引导，每一步都要点名当前题里的对象或条件；每一步只推进一个动作，每一步最好控制在 1-2 句。
13. try_now：现在你来试，只能给一个很小的问题或动作，必须直接检查当前桥有没有真的打通，不能退化成只做表面算数或机械抄写，除非当前桥本身就是规模估算或数量判断。
14. next_step：兼容字段，内容与 try_now 保持一致。
15. transfer_signal：下次看到什么题面信号要想到这类做法。
16. topic_commonality：这类题在考什么。先抽象共性，再映射到当前题，并结合学生卡点解释为什么这道题不是另一个常见做法。允许写成 2-4 段 Markdown，必须有具体题面对象。
17. solution_walkthrough：这道题怎么做通。写成压缩版题解，但不是完整代码；必须讲清核心状态/结构、更新步骤、为什么对、复杂度为什么能过，并对比学生原来的想法差在哪里。
18. transfer_checklist：下次怎么迁移。先说同类题共性，再给 3-5 条可执行检查点；必须包含至少一个反例边界：什么时候这个思路不能直接用；最后给一个小验证问题或同类题练习方向。

通用规则：
1. 面向初中生，说人话，短句。
2. 先讲对象，再讲关系，再讲这一步怎么想。
3. 能对比时，先说最容易误会的一句话，再说正确的一句话。
4. 禁止空话，禁止只报算法名。
5. guided_walkthrough 必须真正带学生走 2-3 步，不能只写画图、手推、再想想；也禁止只写画图、手推、再想想。
6. try_now 必须是 1 步内可回答、可执行的小问题或小动作，必须直接检查当前桥有没有真的打通。
7. 只有完成状态是“看题解”时，problem_focus、main_block、key_bridge、guided_walkthrough、try_now、next_step 才允许有限提算法名；否则只写这题里具体的对象、关系、条件和步骤，不要抽象成方法名或概念名。
8. 除 visual_hint 外，所有字段都要填写；如果 visual_hint 没有帮助，可以留空字符串。
9. 禁止在字段内容里使用半角双引号；不要在字段内容里使用半角双引号；引用题面词语时直接改写，或不用引号。
10. 优先复用题目里的对象名、条件名、公式名。
11. next_action 和 suggested_topic 优先回到当前题，禁止写专项训练、经典题、做3道、变式或拓展；不要写专项训练、经典题、做3道、变式或拓展。
12. 不要对学生使用“卡点”这个内部词；学生可见内容统一改写为“没想明白的地方”“当前这一步”“问题所在”。

长度控制：
- diagnosis / problem_focus / main_block / key_bridge：尽量不超过 60 字
- visual_hint：尽量控制在 6 行以内，只保留当前桥真正需要的对象和关系
- guided_walkthrough：允许明显长一点，但必须保持 2-3 步
- try_now / next_step / transfer_signal：尽量不超过 40 字
- topic_commonality / solution_walkthrough / transfer_checklist：这是学生主要看的三张复盘卡，可以明显长一些；每张卡都要有标题感、对比和当前题例子。"""

    family = _family_for_review_mode(mode)
    family_supplements = {
        "failure_diagnosis": """

本次任务属于 failure_diagnosis。
目标：先定位错误或卡点，再把问题缩小到学生现在能检查的一步。
- problem_focus 必须落到当前错在哪或卡在哪，不能漂成整题总结。
- key_bridge 必须服务当前一步，不要提前展开后面步骤。
- guided_walkthrough 必须围绕当前桥梁做 2-3 步微引导。
- try_now 必须是学生现在就能检查、回答或执行的一步。""",
        "success_reflection": """

本次任务属于 success_reflection。
目标：先帮助学生说清为什么这样做对，再帮助他形成迁移信号。
- 如果学生已经做出题目，problem_focus 优先写“不会解释为什么对”的当前缺口。
- key_bridge 优先解释正确性依据或关键判断。
- guided_walkthrough 必须帮助学生把“为什么对”说顺，而不是重复做法步骤。
- transfer_signal 在本 family 中必须清楚、具体、可迁移。""",
    }

    mode_supplements = {
        "failed_verdict": """

本次任务重点：学生提交有明确错误结果（WA/TLE/RE/CE）。
- diagnosis 必须说清这个错误结果对应的具体出错位置或逻辑。
- problem_focus 必须说清是哪一步代码或判断出了问题，优先点名具体判断条件、连接符、代码位置或输出位置。
- problem_focus 禁止只写“没想清楚”“组合判断语句”“思路有问题”这类模糊说法；不要只写“没想清楚”“组合判断语句”“思路有问题”这类模糊说法。
- problem_focus 禁止只写“组合判断语句”；不要只写“组合判断语句”，要继续落到哪个条件、哪个连接符或哪一处判断。
- try_now 必须是今天可以调试的一个最小动作。
- next_action 优先回到当前题，指出先检查哪一处代码、判断或输出。
- key_bridge 和 transfer_signal 可以简短，但不能为空。
- problem_focus 只说错误类型（如"且关系写错了""条件判断有问题"）不够，必须同时说明是代码里哪一处写错——点名变量名、条件表达式、判断符号或代码位置中至少一个。""",
        "stuck_bridge": """

本次任务重点：学生卡住了，还没完成或需要提示才完成。
- problem_focus 必须说清学生卡在哪个具体步骤，不能只写"不会建模"。
- key_bridge 必须先从题目原文里逐字摘出至少一个名词或条件，不允许改写或概括；再用这个原文词说明为什么这一步是关键。
- try_now 同样：必须点名题目里直接出现过的某个对象或条件，不允许用"某变量""某限制""进度"等自造概念替代。兼容字段 next_step 同样：必须点名题目里直接出现过的某个对象或条件。
- key_bridge 必须点名一个对象、关系、条件或状态含义，说明跨过这一步的关键事实。
- guided_walkthrough 必须先围绕当前对象、关系或条件，把学生从“看不清这一步”带到“知道该先检查什么”，禁止重新讲整题总结。
- try_now 必须是今天立刻可以做的一件小事，优先写手画一次 / 逐条列出 / 手推一轮，并点名当前题里至少一个对象或条件。
- try_now 不能只写列出条件、画表格、挑一维；要点名当前题里的对象、条件或状态。
- transfer_signal 可以简短，但必须提到一个可观察的题目特征，不要给题面特征加引号，不要只写多个限制条件。""",
        "editorial_transfer": """

本次任务重点：学生看了题解，现在要理解和迁移。
- diagnosis 重点说清"为什么这个方法能解决这道题"。
- key_bridge 必须包含具体结构或公式，不能只复述算法名。
- key_bridge 必须说清这道题里的哪个动作对应算法里的哪个操作（如"合并舰队指令 -> union"、"查询间距 -> 路径压缩时累加偏移量"），不能只说算法能做什么。
- guided_walkthrough 必须围绕“题目动作 -> 算法操作”的映射，一步步带学生把这条映射走顺。
- transfer_signal 必须说清下次看到什么特征时联想到这类做法。
- try_now 只写回到原题的一步验证动作，不写练习题或类比；禁止写练习题或类比。""",
        "independent_reflect": """

本次任务重点：学生独立完成，现在做结构性复盘。
- key_bridge 重点说清"这道题为什么这样做是对的"。
- guided_walkthrough 必须帮助学生把“为什么这样做对”讲顺，禁止只重复做法步骤。
- transfer_signal 必须说清触发信号，不能只写"遇到类似题"。
- transfer_signal 必须直接引用题目里出现的具体名词或数量关系，不能写算法类型描述。
- transfer_signal 里不能出现题目名或题目编号，只能写题面里描述的条件、对象和数量关系。
- 错误示范："每个决策点可以选择做多少、后面还有更优选择"、"题目要求最少步数从起点向外扩散"、"每组有上限约束、最小化组数"——这些都是类型模板，不是题面特征。
- 正确示范："题目给出若干油站各有单价、油箱容量有上限、要求总费用最小"、"棋盘上马从指定起点按日字走法到达每个格子"、"n 件物品各有重量、每组最多两件且总重量不超过 w"。
- try_now 只写当前题的一步验证动作，不写变形和拓展；禁止写变形和拓展。
- problem_focus 如果没有明显卡点，必须写清这道题的核心决策流程（如"在当前油站决定加多少油"、"从堆里弹出最小元素后更新相邻节点"），不能为空，也不能只写做出来了。""",
    }
    prompt = base + family_supplements[family] + mode_supplements.get(mode, mode_supplements["independent_reflect"])

    if handoff_payload and handoff_payload.get("source") == "aichat":
        risk_type = handoff_payload.get("risk_type", "")
        suggested_focus = handoff_payload.get("suggested_focus", "")
        checkin_supplement = f"""

本次复盘来自 AIChat 移交（source=checkin_reflection）。
移交风险类型：{risk_type}
建议复盘焦点：{suggested_focus}

在 source=checkin_reflection 模式下，额外允许：
- 确认学生已有代码中某一行的局部作用（不提供修改后的替换代码）。
- 给出一个完整的 3-5 节点或小输入微例子，并逐步走一遍状态变化。
- 说明这道题存在多种合法思路（不展开每种思路的实现步骤）。

source=checkin_reflection 仍然禁止：
- 完整 DP 状态定义。
- 完整转移方程。
- 完整 check(mid) 函数或完整 check 语义。
- 完整树差分 / LCA 加减公式。
- 直接给 AC 代码。
- A/B 选项里有一个是完整正确桥梁。
- 在学生提供充分证据之前直接确认正确性。"""
        prompt += checkin_supplement

    return prompt


def _build_clarify_system_prompt() -> str:
    return """你是 NOI 教练。当前任务不是讲题，而是帮助学生把问题说清楚。

如果当前证据不足，禁止直接讲题，禁止猜方法，禁止展开完整题解。
你只做两件事：
1. 说明为什么现在还不能稳定复盘
2. 给一个最小澄清问题

只输出 JSON：
{
  remedy_text: string,
  micro_action: string
}

要求：
- remedy_text 必须说明当前缺少哪类证据。
- micro_action 只能问一个问题，只能推进一步。
- 优先帮助学生说清：题目要求你求什么、你试到哪一步、你具体卡在哪一层。
- 禁止把 micro_action 写成多个追问，也禁止直接讲整题。""".strip()


def _build_clarify_user_prompt(review_context: dict, remedy_action: str) -> str:
    lines = [
        f"题目：{review_context.get('problem_title', '')}",
        f"题目摘要：{_compact_text(review_context.get('problem_context', ''), 180)}",
        f"学生卡点：{_compact_text(review_context.get('bottleneck_text', ''), 120)}",
        f"当前 error_layer：{review_context.get('error_layer', 'insufficient')}",
        f"补救动作：{remedy_action}",
    ]
    return "\n".join(line for line in lines if line.strip())


def _build_remedy_system_prompt(remedy_action: str) -> str:
    return f"""你是 NOI 教练。当前任务是第一轮没过后的解释型补救。

不重复第一轮复盘；禁止重讲整题，禁止直接给完整答案。
你只能做一件事：只把桥缩小一步，或换一种表示方式，或纠正一个具体误解。
当前补救动作：{remedy_action}

只输出 JSON：
{{
  remedy_text: string,
  visual_hint: string,
  micro_action: string
}}

要求：
- remedy_text 只服务当前这一小步，不展开多个难点。
- visual_hint 可选。只在有必要时输出一个文本化小图、小表或小分类框，帮助学生看清当前桥的对象和关系。禁止直接给出最终比较结果或完整答案，优先写半成品提示。
- micro_action 只能给一个最小动作，必须 1 步内可回答或执行，并且直接检查当前桥有没有真的打通；不能退化成只做表面算数或机械抄写，除非当前桥本身就是规模估算或数量判断。
- 如果能换一种表示方式，就优先用更小样例、对象拆分、条件重写来解释。
- 禁止把 micro_action 写成多步任务。""".strip()


def _build_remedy_user_prompt(review_context: dict, remedy_action: str) -> str:
    lines = [
        f"题目：{review_context.get('problem_title', '')}",
        f"核心卡点：{_compact_text(review_context.get('bottleneck_text', ''), 120)}",
        f"problem_focus：{review_context.get('problem_focus') or review_context.get('main_block', '')}",
        f"key_bridge：{review_context.get('key_bridge', '')}",
        f"try_now：{review_context.get('try_now') or review_context.get('next_step', '')}",
        f"补救动作：{remedy_action}",
    ]
    return "\n".join(line for line in lines if line.strip())


def _build_bottom_out_system_prompt(remedy_action: str) -> str:
    return f"""你是 NOI 教练。当前任务是第三轮最强支架：bottom_out。

这不是新一轮自由讲题，也不是完整题解。你只能围绕当前题、当前桥，给一个更直接的 worked example。
必须面向初中生，说短句，先讲对象，再讲关系，再讲这一步怎么想。
禁止直接给完整答案、完整证明、完整代码。
当前补救动作：{remedy_action}

只输出 JSON：
{{
  remedy_text: string,
  visual_hint: string,
  micro_action: string
}}

要求：
- remedy_text 必须继续围绕当前题，不要切去别的题或前置微课。
- remedy_text 必须像老师把这一步重新讲一遍，但只讲当前桥，不讲完整解法。
- visual_hint 尽量填写，用文本化小图、小表或小分类框做当前题的最小 worked example。
- micro_action 只能问一个最后的最小确认问题，必须 1 步内可回答。
- 如果你已经把整题讲完，说明支架过大，必须缩回。""".strip()


def _build_bottom_out_user_prompt(review_context: dict, remedy_action: str) -> str:
    lines = [
        f"题目：{review_context.get('problem_title', '')}",
        f"题目摘要：{_compact_text(review_context.get('problem_context', ''), 180)}",
        f"学生核心卡点：{_compact_text(review_context.get('bottleneck_text', ''), 120)}",
        f"problem_focus：{review_context.get('problem_focus') or review_context.get('main_block', '')}",
        f"key_bridge：{review_context.get('key_bridge', '')}",
        f"guided_walkthrough：{review_context.get('guided_walkthrough', '')}",
        f"try_now：{review_context.get('try_now') or review_context.get('next_step', '')}",
        f"当前已补救轮次：{review_context.get('remedy_count') or 0}",
        f"补救动作：{remedy_action}",
    ]
    return "\n".join(line for line in lines if line.strip())


def _build_review_user_prompt(
    problem_title: str,
    oj_source: str,
    status_text: str,
    bottleneck_text: str,
    error_types: list,
    reflection: str | None = None,
    problem_context: str | None = None,
    problem_tags: list | None = None,
    chat_context_summary: str | None = None,
    problem_card: dict | None = None,
    submission_text: str | None = None,
    student_code: str | None = None,
    handoff_payload: dict | None = None,
) -> str:
    focus_text = " ".join(
        filter(
            None,
            [
                problem_title,
                problem_context or "",
                bottleneck_text,
                reflection or "",
                " ".join(error_types or []),
            ],
        )
    )
    selected_tags = _select_review_tags(problem_tags, focus_text)

    lines = [
        f"题目：{problem_title}",
        f"来源：{oj_source}",
        f"完成状态：{status_text}",
    ]

    compact_card = _compact_problem_card(problem_card)
    if compact_card:
        lines.append(f"题目结构化卡：{compact_card}")
        compact_context = _compact_text(problem_context, min(REVIEW_CONTEXT_CHAR_LIMIT, 100))
        if compact_context and compact_context not in compact_card:
            lines.append(f"题目补充：{compact_context}")
    elif problem_context:
        lines.append(f"题目摘要：{_compact_text(problem_context, REVIEW_CONTEXT_CHAR_LIMIT)}")

    if selected_tags:
        lines.append(f"相关标签：{'、'.join(selected_tags)}")

    if REVIEW_CHAT_CONTEXT_CHAR_LIMIT > 0 and chat_context_summary:
        lines.append(f"同题摘要：{_compact_text(chat_context_summary, REVIEW_CHAT_CONTEXT_CHAR_LIMIT)}")

    if submission_text:
        lines.append(f"提交现象：{submission_text}")

    lines.append(f"核心卡点：{_compact_text(bottleneck_text, 180)}")
    lines.append(f"错误类型：{', '.join(error_types)}")

    if reflection:
        lines.append(f"学生反思：{_compact_text(reflection, REVIEW_REFLECTION_CHAR_LIMIT)}")

    compact_code = _compact_student_code(student_code)
    if compact_code:
        lines.append(f"代码片段：\n```\n{compact_code}\n```")

    if handoff_payload and handoff_payload.get("source") == "aichat":
        risk_type = handoff_payload.get("risk_type", "")
        suggested_focus = handoff_payload.get("suggested_focus", "")
        last_msg = handoff_payload.get("last_user_message", "")
        if risk_type == "ac_unclear_in_aichat":
            lines.append(f"移交背景：学生已 AC 但表示不理解，AIChat 判断需结构化复盘。")
        elif risk_type == "repeated_stuck_exit":
            lines.append(f"移交背景：学生在 AIChat 反复卡住，AIChat 判断需退出当前抽象路径，进入结构化复盘。")
        if last_msg:
            lines.append(f"移交前最后一条消息：{last_msg[:200]}")
        if suggested_focus:
            lines.append(f"建议复盘焦点：{suggested_focus}")

    bridge_constraint = _review_bridge_prompt_constraint(
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
        error_types=error_types,
    )
    if bridge_constraint:
        lines.append(bridge_constraint)

    return "\n".join(lines)


def _call_llm(messages: list[dict], chunk_callback=None) -> tuple[bool, str, dict]:
    """
    调用 LLM 获取回复
    
    Returns:
        (success, content)
        success: True 表示调用成功，False 表示失败
    """
    last_error = None
    last_telemetry = {
        "model_name": "",
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "finish_reason": "",
    }
    candidates = get_model_candidates("NOI_REVIEW_MODELS", _default_review_models())

    for idx, model_name in enumerate(candidates):
        for attempt in range(2):
            try:
                provider = _review_provider_for_model(model_name)
                request_kwargs = {
                    "model": model_name,
                    "messages": messages,
                    "timeout": LLM_REQUEST_TIMEOUT_SECONDS,
                    "response_format": {"type": "json_object"},
                    "stream": True,
                }
                request_kwargs[provider["token_param"]] = LLM_MAX_TOKENS
                if provider["extra_body"]:
                    request_kwargs["extra_body"] = provider["extra_body"]
                if "kimi-k2.5" not in model_name.lower():
                    request_kwargs["temperature"] = 0.3

                response = get_client(model_name).chat.completions.create(
                    **request_kwargs,
                )
                content_parts: list[str] = []
                last_preview_signature = None
                finish_reason = ""
                prompt_tokens = 0
                completion_tokens = 0

                stream_iter = response if not hasattr(response, "choices") else [response]

                for chunk in stream_iter:
                    usage = getattr(chunk, "usage", None)
                    if usage is not None:
                        prompt_tokens = getattr(usage, "prompt_tokens", 0) or prompt_tokens
                        completion_tokens = getattr(usage, "completion_tokens", 0) or completion_tokens

                    choices = getattr(chunk, "choices", None) or []
                    if not choices:
                        continue

                    choice = choices[0]
                    chunk_finish_reason = getattr(choice, "finish_reason", "") or ""
                    if chunk_finish_reason:
                        finish_reason = chunk_finish_reason

                    delta = getattr(choice, "delta", None)
                    delta_content = getattr(delta, "content", None) if delta is not None else None
                    if delta_content is None:
                        message = getattr(choice, "message", None)
                        delta_content = getattr(message, "content", None) if message is not None else None
                    if not delta_content:
                        continue

                    if isinstance(delta_content, str):
                        content_parts.append(delta_content)
                    elif isinstance(delta_content, list):
                        for item in delta_content:
                            text = getattr(item, "text", None) or ""
                            if text:
                                content_parts.append(text)

                    if chunk_callback:
                        partial_text = "".join(content_parts)
                        draft_preview = _extract_review_draft_preview(partial_text)
                        preview_signature = tuple(
                            draft_preview.get(key, "")
                            for key in (
                                "problem_focus",
                                "main_block",
                                "key_bridge",
                                "guided_walkthrough",
                                "try_now",
                                "next_step",
                                "transfer_signal",
                            )
                        )
                        if preview_signature != last_preview_signature and any(preview_signature):
                            chunk_callback(partial_text, draft_preview)
                            last_preview_signature = preview_signature

                content = "".join(content_parts).strip()
                telemetry = {
                    "model_name": model_name,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "finish_reason": finish_reason,
                }
                last_telemetry = telemetry

                if finish_reason == "length":
                    last_error = RuntimeError(f"review response truncated on model {model_name}")
                    print(f"[review_engine] truncated review response on model {model_name}")
                    if attempt == 0:
                        continue
                    break

                if not content:
                    last_error = RuntimeError(f"empty review response on model {model_name}")
                    print(f"[review_engine] empty review response on model {model_name}")
                    if attempt == 0:
                        continue
                    break

                if idx > 0 or attempt > 0:
                    print(f"[review_engine] fallback/retry model succeeded: {model_name}")
                return True, content, telemetry
            except Exception as exc:
                last_error = exc
                print(f"[review_engine] LLM call failed on model {model_name}: {exc}")
                if attempt == 0 and ("timed out" in str(exc).lower() or "timeout" in str(exc).lower()):
                    continue
                if not is_model_unavailable_error(exc):
                    break
                break

    if last_error:
        print(f"[review_engine] all review model attempts failed: {last_error}")
    return False, "", last_telemetry


def _extract_json_block(text: str) -> str | None:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1).strip()

    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    inline = re.search(r"(\{.*\})", text, re.DOTALL)
    if inline:
        return inline.group(1).strip()
    return None


def _sanitize_json_like_text(text: str) -> str:
    """Make common non-JSON typography safe for json.loads."""
    return (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )


def _normalize_error_tags(raw_tags) -> list[str]:
    if isinstance(raw_tags, list):
        tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
    elif isinstance(raw_tags, str):
        tags = [tag.strip() for tag in re.split(r"[,，、/]", raw_tags) if tag.strip()]
    else:
        tags = []
    return tags[:3]


def _normalize_subtags(raw_subtags, error_layer: str) -> list[str]:
    if error_layer != "core_design":
        return []

    if isinstance(raw_subtags, str):
        items = [item.strip() for item in re.split(r"[,，、/]", raw_subtags) if item.strip()]
    elif isinstance(raw_subtags, list):
        items = [str(item).strip() for item in raw_subtags if str(item).strip()]
    else:
        items = []

    seen = set()
    normalized = []
    for item in items:
        if item in CORE_DESIGN_SUBTAGS and item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _is_trie_node_count_context(text: str) -> bool:
    return _contains_any(
        text or "",
        (
            "经过次数",
            "结束次数",
            "经过当前前缀节点",
            "当前前缀节点",
            "节点该存什么",
            "节点存什么",
            "pass_cnt",
            "end_cnt",
        ),
    )


def _is_tree_path_difference_context(text: str) -> bool:
    candidate = text or ""
    tree_hits = _count_keyword_hits(
        candidate,
        (
            "树上",
            "树",
            "节点",
            "父亲",
            "子树",
            "lca",
            "公共祖先",
            "最近公共祖先",
            "树剖",
            "树链剖分",
            "hld",
        ),
    )
    path_hits = _count_keyword_hits(
        candidate,
        (
            "多条路径",
            "树上路径",
            "树上路线",
            "路线",
            "每段路",
            "一段路",
            "路径贡献",
            "访问贡献",
            "路径加一",
            "经过次数",
            "访问次数",
            "被访问",
            "经过最多",
            "整条路径",
            "沿路",
            "走到下一个",
            "从 s 到 t",
            "从s到t",
        ),
    )
    diff_hits = _count_keyword_hits(
        candidate,
        (
            "树上差分",
            "差分",
            "端点",
            "抵消",
            "打标记",
            "标记",
            "子树汇总",
            "向上汇总",
            "dfs 汇总",
            "dfs汇总",
        ),
    )
    return tree_hits >= 1 and path_hits >= 1 and (diff_hits >= 1 or _contains_any(candidate, ("lca", "公共祖先", "最近公共祖先", "树剖", "树链剖分")))


def _is_shared_prefix_context(text: str) -> bool:
    candidate = text or ""
    if _is_tree_path_difference_context(candidate):
        return False
    return _contains_any(
        candidate,
        (
            "trie",
            "前缀树",
            "公共前缀",
            "前缀关系",
            "相同开头",
            "结束次数",
            "经过当前前缀节点",
            "当前前缀节点",
            "重看所有消息",
            "沿当前前缀",
            "只沿前缀",
            "拦截串",
            "消息",
            "字符串",
            "01 串",
        ),
    )


def _count_keyword_hits(text: str, keywords: tuple[str, ...]) -> int:
    lowered = (text or "").lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered)


def _guard_review_bridge_stability(
    review: dict,
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
    error_types: list[str],
) -> dict:
    review_context = {
        **review,
        "problem_title": problem_title,
        "problem_context": problem_context or "",
        "bottleneck_text": bottleneck_text,
        "error_types": error_types or [],
    }
    source_focus_context = {
        "error_layer": review.get("error_layer", "insufficient"),
        "core_design_subtags": review.get("core_design_subtags") or [],
        "problem_title": problem_title,
        "problem_context": problem_context or "",
        "bottleneck_text": bottleneck_text,
        "error_types": error_types or [],
        "main_block": "",
        "key_bridge": "",
        "next_step": "",
        "transfer_signal": "",
    }
    focus = _detect_quiz_focus(source_focus_context)
    if focus not in HIGH_RISK_REVIEW_FOCI:
        focus = _detect_quiz_focus(review_context)
    if focus == "complexity_fit" and review.get("error_layer") == "method":
        focus = "method_selection"
    if focus not in HIGH_RISK_REVIEW_FOCI:
        return review

    focus_rule = REVIEW_FOCUS_RULES[focus]
    main_block = review.get("main_block", "")
    key_bridge = review.get("key_bridge", "")
    next_step = review.get("next_step", "")
    transfer_signal = review.get("transfer_signal", "")

    if focus == "constraint_modeling" and review.get("error_layer") != "core_design":
        review["error_layer"] = "core_design"

    if (
        _count_keyword_hits(main_block, focus_rule["bridge_terms"]) < 2
        or _contains_any(main_block, GENERIC_TOPIC_TERMS)
    ):
        review["main_block"] = focus_rule["main_block"]

    if (
        _count_keyword_hits(key_bridge, focus_rule["bridge_terms"]) < 2
        or _contains_any(key_bridge, GENERIC_ACTION_TERMS)
        or _contains_any(key_bridge, GENERIC_BRIDGE_TERMS)
    ):
        review["key_bridge"] = focus_rule["key_bridge"]

    if _count_keyword_hits(next_step, focus_rule["step_terms"]) < 2 or _contains_any(next_step, GENERIC_ACTION_TERMS):
        review["next_step"] = focus_rule["next_step"]

    if (
        _count_keyword_hits(transfer_signal, focus_rule["signal_terms"]) < 2
        or _contains_any(transfer_signal, GENERIC_TRANSFER_SIGNALS)
    ):
        review["transfer_signal"] = focus_rule["transfer_signal"]

    return review


def _guard_review_bridge_consistency(
    review: dict,
    focus: str,
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
) -> dict:
    rule = REVIEW_BRIDGE_GUARD_RULES.get(focus)
    if not rule:
        return review

    if focus == "shared_prefix_merging":
        node_count_context = _is_trie_node_count_context(
            " ".join(
                filter(
                    None,
                    [
                        problem_title,
                        problem_context or "",
                        bottleneck_text,
                        review.get("problem_focus", ""),
                        review.get("main_block", ""),
                        review.get("key_bridge", ""),
                        review.get("visual_hint", ""),
                        review.get("guided_walkthrough", ""),
                        review.get("try_now", ""),
                        review.get("next_step", ""),
                        review.get("transfer_signal", ""),
                    ],
                )
            )
        )
        if node_count_context:
            review["problem_focus"] = "你不是在做一般字符串处理，而是在分清 Trie 节点上“经过次数”和“结束次数”各在回答什么。"
            review["main_block"] = review["problem_focus"]
            review["key_bridge"] = "关键是先把经过次数和结束次数分开：经过次数表示有多少消息经过当前前缀节点，结束次数表示有多少消息正好在这里结束。"
            review["visual_hint"] = "101\n100\n11\n前缀 10 这个节点\n-> 经过次数至少是 2\n-> 结束次数另算"
            review["guided_walkthrough"] = "1. 先只盯前缀 10 这个节点，看 101 和 100 会不会都经过它。\n2. 再把“经过次数”和“结束次数”分开说清楚。\n3. 最后再回到查询路径，看为什么只沿前缀节点往下走。"
            review["try_now"] = "先只回答一句：前缀 10 这个节点上的经过次数，正在说明什么？"
            review["next_step"] = review["try_now"]
            return review

    if focus == "method_selection":
        source_text = " ".join(
            filter(
                None,
                [
                    problem_title,
                    problem_context or "",
                    bottleneck_text,
                ],
            )
        )
        trie_signal_terms = ("trie", "前缀", "消息", "拦截串", "相同开头", "前缀关系")
        trie_signal_hits = _count_keyword_hits(source_text, trie_signal_terms)
        if trie_signal_hits < 2:
            return review

    fields = (
        "problem_focus",
        "key_bridge",
        "visual_hint",
        "guided_walkthrough",
        "try_now",
    )
    combined = " ".join(str(review.get(field, "")) for field in fields)
    missing_anchor = _count_keyword_hits(combined, rule["focus_terms"]) < 2
    too_generic = any(
        _contains_any(str(review.get(field, "")), GENERIC_TOPIC_TERMS + GENERIC_ACTION_TERMS + GENERIC_BRIDGE_TERMS)
        for field in fields
    )

    if not missing_anchor and not too_generic:
        return review

    review["problem_focus"] = rule["problem_focus"]
    review["main_block"] = rule["problem_focus"]
    review["key_bridge"] = rule["key_bridge"]
    review["visual_hint"] = rule["visual_hint"]
    review["guided_walkthrough"] = rule["guided_walkthrough"]
    review["try_now"] = rule["try_now"]
    review["next_step"] = rule["try_now"]
    return review


def _guard_review_against_topic_drift(
    review: dict,
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
    error_types: list[str],
) -> dict:
    source_text = " ".join(
        filter(
            None,
            [
                problem_title,
                problem_context or "",
                bottleneck_text,
                " ".join(error_types or []),
            ],
        )
    )
    generated_student_text = " ".join(
        [
            review.get("main_block", ""),
            review.get("key_bridge", ""),
            review.get("next_step", ""),
            review.get("transfer_signal", ""),
        ]
    )
    source_focus_context = {
        "error_layer": review.get("error_layer", "insufficient"),
        "core_design_subtags": review.get("core_design_subtags") or [],
        "problem_title": problem_title,
        "problem_context": problem_context or "",
        "bottleneck_text": bottleneck_text,
        "error_types": error_types or [],
        "main_block": "",
        "key_bridge": "",
        "next_step": "",
        "transfer_signal": "",
    }
    source_focus = _detect_quiz_focus(source_focus_context)
    if _contains_any(source_text, ("n <=", "n<=", "规模上界", "数据范围", "复杂度", "枚举所有子集", "子集")):
        source_focus = "method_selection"

    source_has_graph = _contains_any(source_text, GRAPH_HINT_TERMS)
    source_is_constraint_graph = "x_u - x_v <= c" in source_text or _contains_any(source_text, CONSTRAINT_GRAPH_TERMS)
    source_has_dp = _contains_any(source_text, ("状态", "转移", "背包", "dp", "容量", "体积", "价值", "物品", "不选"))
    source_has_impl = _contains_any(source_text, IMPLEMENTATION_HINT_TERMS)
    generated_has_graph = _contains_any(generated_student_text, GRAPH_HINT_TERMS)
    generated_has_dp = _contains_any(generated_student_text, DP_HINT_TERMS)

    if source_focus == "method_selection":
        source_has_dp = False

    # trie 节点计数语境如果被状态/实现词汇带偏，优先拉回 shared_prefix_merging。
    if source_focus == "shared_prefix_merging" and _is_trie_node_count_context(source_text):
        review["main_block"] = "你不是在想一般的“状态定义”，而是在分清 Trie 节点到底该记录哪两类数量。"
        review["key_bridge"] = "关键是先把经过次数和结束次数分开：经过次数表示有多少消息经过当前前缀节点，结束次数表示有多少消息正好在这里结束。"
        review["next_step"] = "先拿一个当前前缀节点，分别说清它的经过次数和结束次数各回答什么，再往查询路径上套。"
        review["transfer_signal"] = "如果题目在问前缀匹配、节点计数、消息经过哪个节点，就先怀疑是不是 Trie 节点语义没站稳。"
        return review

    # 背包/DP 题却冒出图/不等式/建图词汇时，用更稳的 DP 纠偏文案兜底。
    if source_has_dp and not source_has_graph and generated_has_graph:
        review["key_bridge"] = "关键是先确认每一维状态到底记录什么，再保留“不选当前对象”这一支。"
        review["next_step"] = "先只写状态定义和“不选当前对象”这一支转移，不写完整代码。"
        review["transfer_signal"] = "如果题目是在资源限制下选对象求最优值，先检查是不是背包类建模。"

    # 约束建图题却冒出状态/转移/背包词汇时，用更稳的约束建图文案兜底。
    if source_is_constraint_graph and not source_has_dp and generated_has_dp:
        review["key_bridge"] = "关键是先把变量之间的限制整理成统一约束，再确认变量、边权和方向各表示什么。"
        review["next_step"] = "先把题面条件逐条整理成统一约束，再画出变量和边之间的对应关系。"
        review["transfer_signal"] = "如果题目一直在描述多个变量之间的大小关系、上下界或先后限制，就先怀疑是不是约束建图。"

    # 实现调试题却冒出建图/不等式/状态转移等话术时，拉回到边界与默认前提。
    if source_has_impl and not source_has_graph and not source_has_dp and (generated_has_graph or generated_has_dp):
        review["main_block"] = "你不是方法没想到，而是代码里默认了一些长度、下标或边界前提，提交后这些前提被最小情况打破了。"
        review["key_bridge"] = "关键不是重新建模，而是先找出代码默认了哪些前提，再检查这些前提在最小边界下是否仍然成立。"
        review["next_step"] = "先列出 n=1、最小长度、空区间这几种边界，再逐条检查访问位置会不会越界。"
        review["transfer_signal"] = "如果样例能过但提交 WA/RE，先检查是不是默认长度、下标范围或特判遗漏。"

    if source_has_impl and not source_has_graph and not source_has_dp and (
        "重新检查代码" in generated_student_text or "重新检查" in generated_student_text
    ):
        review["next_step"] = "先列出 n=1、最小长度、空区间这几种边界，再逐条检查访问位置会不会越界。"
        review["transfer_signal"] = "如果样例能过但提交 WA/RE，先检查是不是默认长度、下标范围或特判遗漏。"

    return review


def _guard_review_against_overclaim(
    review: dict,
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
    error_types: list[str],
) -> dict:
    source_text = " ".join(
        filter(
            None,
            [
                problem_title,
                problem_context or "",
                bottleneck_text,
                " ".join(error_types or []),
            ],
        )
    )
    student_text = " ".join(
        [
            review.get("main_block", ""),
            review.get("key_bridge", ""),
            review.get("next_step", ""),
            review.get("transfer_signal", ""),
        ]
    )

    # 差分约束等约束建图题：如果模型擅自写死边方向/边对，优先改成更稳的“先确认谁限制谁”。
    if "x_u - x_v <= c" in source_text and (
        "从 u 指向 v" in student_text
        or "从 v 指向 u" in student_text
        or "(u, v)" in student_text
        or "(v, u)" in student_text
        or "u -> v" in student_text
        or "v -> u" in student_text
        or "边的方向" in student_text
    ):
        review["main_block"] = "你不是不会图论，而是还没有先把每条不等式整理成“谁限制谁”的约束关系。"
        review["key_bridge"] = "关键不是先记最短路模板，而是先把每条限制整理成统一形式，再确认“是谁限制谁”、边权表示什么。"
        review["next_step"] = "把每条限制单独写成统一约束，再逐条标注“谁限制谁”和这条边的权值含义。"
        review["transfer_signal"] = "如果题目一直在描述多个变量之间的大小关系、上下界或先后限制，就先想能不能整理成统一约束。"
        review["diagnosis"] = "你已经意识到题目和图论有关，但真正卡住的是还没有先把每条不等式整理成统一约束，因此没法稳定判断变量、边权和方向各表示什么。"
        review["next_action"] = "先练习把文字限制改写成统一约束，再单独检查“谁限制谁、权值表示什么”这一步。"

    # 背包/DP：如果模型把“时间和价值都转成状态”说得过粗或错误，拉回到“只保留决策相关维度”。
    if _contains_any(source_text, ("背包", "时间", "价值", "采药")) and (
        "时间和价值转化为状态" in student_text
        or "采摘时间和价值转化为状态" in student_text
        or "用已用时间和总价值定义状态" in student_text
        or ("状态" in student_text and "总价值" in student_text)
        or ("dp[i]" in student_text.lower() and ("前i株" in student_text or "前 i 株" in student_text or "不超过i时间" in student_text or "不超过 i 时间" in student_text))
        or "dp[i]=max" in student_text.lower()
        or "dp[i] = max" in student_text.lower()
    ):
        review["main_block"] = "你不是没想到背包，而是还没先确定状态每一维到底记录什么，所以一写转移就把“对象层”和“资源限制”混在一起了。"
        review["key_bridge"] = "关键是只把真正限制决策的量放进状态，比如已用时间或剩余时间；价值是比较结果，不是必须额外开一维状态。"
        review["next_step"] = "先只写状态含义：每一维分别表示什么；然后单独补上“不选当前对象”这一支转移。"
        review["transfer_signal"] = "如果题目是在容量或时间限制下选对象求最优值，先检查是不是背包类建模。"
        review["diagnosis"] = "你已经意识到题目属于背包类，但真正卡住的是还没有先把状态每一维的含义定稳，导致把对象维和资源维混在一起，转移也就跟着变乱了。"
        review["next_action"] = "先只写状态含义，不写公式；确认每一维各表示什么后，再单独补“不选当前对象”这一支。"

    return review


def _guard_review_for_insufficient(
    review: dict,
    problem_context: str | None,
    bottleneck_text: str,
    error_types: list[str],
    reflection: str | None,
    submission_result: str | None,
    student_code: str | None,
) -> dict:
    source_text = " ".join(
        filter(
            None,
            [
                problem_context or "",
                bottleneck_text,
                reflection or "",
                " ".join(error_types or []),
            ],
        )
    )

    strong_unclear = any(re.search(pattern, bottleneck_text or "") for pattern in INSUFFICIENT_PATTERNS)
    weak_signal = (
        not student_code
        and (submission_result in (None, "", "unknown", "not_submitted"))
        and ("其他" in (error_types or []) or len(error_types or []) <= 1)
    )

    if strong_unclear and weak_signal:
        review["error_layer"] = "insufficient"
        review["error_layer_confidence"] = "low"
        review["core_design_subtags"] = []
        review["error_tags"] = ["信息不足"]
        review["main_block"] = "你现在不是已经暴露出某一类固定错误，而是提供的信息还不足以判断真正卡点。"
        review["key_bridge"] = "先把题目要求、你试过什么、你具体在哪一步断掉，这三件事说清楚，系统才能定位关键桥梁。"
        review["next_step"] = "补充题目要求、你的尝试过程，以及你具体是在哪一步卡住，再重新提交一次复盘。"
        review["transfer_signal"] = "如果你自己也只能说“和某类题有关”，那就先把“题目求什么、我试了什么、哪里断掉”写出来。"
        review["diagnosis"] = "当前记录还不足以稳定判断你主要是读题、建模、核心设计还是实现调试出了问题。现在最缺的不是某个算法知识点，而是把题目要求、尝试过程和具体断点描述清楚。"
        review["next_action"] = "先要求学生补充“题目要求 + 已尝试方法 + 具体断点”三项信息，再进行下一次诊断。"
        review["suggested_topic"] = "补充题目信息与解题断点描述"

    return review


def _guard_teacher_guidance(
    review: dict,
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
    error_types: list[str],
) -> dict:
    source_text = " ".join(
        filter(
            None,
            [
                problem_title,
                problem_context or "",
                bottleneck_text,
                " ".join(error_types or []),
            ],
        )
    )
    next_action = review.get("next_action", "")
    suggested_topic = review.get("suggested_topic", "")

    if "x_u - x_v <= c" in source_text:
        if any(term in suggested_topic for term in GENERIC_TOPIC_TERMS):
            review["suggested_topic"] = "差分约束中的统一约束整理与变量-边对应"
        if any(term in next_action for term in GENERIC_ACTION_TERMS):
            review["next_action"] = "先选 3 条限制单独改写成统一约束，再逐条检查“谁限制谁、边权表示什么”这一步。"

    if _contains_any(source_text, ("背包", "采药", "时间", "价值")):
        if any(term in suggested_topic for term in GENERIC_TOPIC_TERMS):
            review["suggested_topic"] = "01背包的状态定义与“不选当前对象”分支"
        if any(term in next_action for term in GENERIC_ACTION_TERMS) or "dp[i]" in next_action.lower() or "总价值" in next_action:
            review["next_action"] = "先只写状态定义和“不选当前对象”这一支转移，再检查哪些量根本不该放进状态。"

    if _contains_any(source_text, IMPLEMENTATION_HINT_TERMS) and not _contains_any(source_text, GRAPH_HINT_TERMS + DP_HINT_TERMS):
        if any(term in suggested_topic for term in GENERIC_TOPIC_TERMS):
            review["suggested_topic"] = "边界条件与默认前提检查"
        if any(term in next_action for term in GENERIC_ACTION_TERMS) or _contains_any(next_action, GRAPH_HINT_TERMS + DP_HINT_TERMS):
            review["next_action"] = "先列出最小边界和容易越界的位置，再逐条检查下标、长度判断和特判是否完整。"

    return review


def _detect_review_quality_flags(review: dict, allow_algorithm_name: bool) -> list[str]:
    if allow_algorithm_name:
        return []

    student_fields = " ".join(
        [
            review.get("main_block", ""),
            review.get("key_bridge", ""),
            review.get("next_step", ""),
        ]
    )
    flags = []
    if _contains_any(student_fields, ALGORITHM_NAME_TERMS):
        flags.append("algorithm_name_leaked")
    return flags


def _apply_text_replacements(text: str, replacements: tuple[tuple[str, str], ...]) -> str:
    result = text or ""
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def _guard_mst_clustering_review(
    review: dict,
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str,
) -> dict:
    source_text = " ".join(filter(None, [problem_title, problem_context or "", bottleneck_text]))
    if not any(keyword in source_text for keyword in ("部落", "最小生成树", "kruskal", "Kruskal", "k条边", "k 个部落", "k个部落")):
        return review

    student_text = " ".join(
        [
            review.get("main_block", ""),
            review.get("key_bridge", ""),
            review.get("next_step", ""),
            review.get("transfer_signal", ""),
        ]
    )

    # 如果串进了约束建图/差分约束话术，强行拉回到更贴题的人话版本。
    if _contains_any(student_text, ("统一约束", "不等式", "边权和方向", "约束建图", "变量")):
        review["main_block"] = "你已经知道这题和先连短边有关，但还没想明白：为什么连到只剩 k 个小团体时，下一条要连的边就是答案。"
        review["key_bridge"] = "这题可以先按从短到长连边。连到只剩 k 个小团体时，下一条本来要把两个小团体连起来的边，长度就是答案。"
        review["next_step"] = "自己画一个只有 5 个点的小图，把边按从短到长排好，连到只剩 3 个小团体，看看下一条边是哪条。"
        review["transfer_signal"] = "如果题目是把很多点分成几组，而且想让组内先尽量靠近，就想想能不能先从短边开始连。"
        review["diagnosis"] = "你已经知道这题和最小生成树有关，但真正卡住的是还没有把“连到只剩 k 个小团体”这一步和“答案取下一条边”连起来。"
        review["next_action"] = "先手动画一个很小的样例图，按边长从小到大连边，停在只剩 k 个小团体时，再观察下一条边。"
        review["suggested_topic"] = "最小生成树里“停在 k 个小团体”这一类题"

    return review


def _simplify_student_language(review: dict) -> dict:
    replacements = (
        ("连通块", "小团体"),
        ("最优划分", "分组结果"),
        ("统一约束", "统一的限制关系"),
        ("约束关系", "限制关系"),
        ("变量", "题目里的量"),
        ("状态转移", "下一步怎么推"),
        ("状态定义", "状态怎么表示"),
        ("判定函数", "检查函数"),
        ("递归过程中的状态", "递归时手里记着的信息"),
        ("子节点指针", "往下走的分支"),
    )

    for key in (
        "problem_focus",
        "main_block",
        "key_bridge",
        "guided_walkthrough",
        "try_now",
        "next_step",
        "transfer_signal",
        "topic_commonality",
        "solution_walkthrough",
        "transfer_checklist",
    ):
        review[key] = _apply_text_replacements(review.get(key, ""), replacements)

    return review


def _extract_json_style_string(text: str, key: str) -> str:
    pattern = rf'"{re.escape(key)}"\s*:\s*"((?:[^"\\]|\\.)*)"'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return ""
    raw = match.group(1)
    try:
        return json.loads(f'"{raw}"')
    except Exception:
        return raw.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t")


def _extract_json_style_array(text: str, key: str):
    pattern = rf'"{re.escape(key)}"\s*:\s*(\[[^\]]*\])'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    raw = match.group(1)
    try:
        return json.loads(raw)
    except Exception:
        return []


def _repair_partial_json_review(text: str) -> dict:
    repaired = {
        "error_tags": _extract_json_style_array(text, "error_tags"),
        "error_layer": _extract_json_style_string(text, "error_layer"),
        "error_layer_confidence": _extract_json_style_string(text, "error_layer_confidence"),
        "core_design_subtags": _extract_json_style_array(text, "core_design_subtags"),
        "diagnosis": _extract_json_style_string(text, "diagnosis"),
        "next_action": _extract_json_style_string(text, "next_action"),
        "suggested_topic": _extract_json_style_string(text, "suggested_topic"),
        "problem_focus": _extract_json_style_string(text, "problem_focus"),
        "main_block": _extract_json_style_string(text, "main_block"),
        "key_bridge": _extract_json_style_string(text, "key_bridge"),
        "visual_hint": _extract_json_style_string(text, "visual_hint"),
        "guided_walkthrough": _extract_json_style_string(text, "guided_walkthrough"),
        "try_now": _extract_json_style_string(text, "try_now"),
        "next_step": _extract_json_style_string(text, "next_step"),
        "transfer_signal": _extract_json_style_string(text, "transfer_signal"),
        "topic_commonality": _extract_json_style_string(text, "topic_commonality"),
        "solution_walkthrough": _extract_json_style_string(text, "solution_walkthrough"),
        "transfer_checklist": _extract_json_style_string(text, "transfer_checklist"),
    }
    return repaired


def _extract_review_draft_preview(text: str) -> dict:
    repaired = _repair_partial_json_review(text)
    preview = {}
    for key in ("problem_focus", "main_block", "key_bridge", "visual_hint", "guided_walkthrough", "try_now", "next_step", "transfer_signal", "topic_commonality", "solution_walkthrough", "transfer_checklist"):
        value = str(repaired.get(key, "") or "").strip()
        if value:
            preview[key] = value
    return preview


def _backfill_student_guidance(review: dict) -> dict:
    if all(
        review.get(key)
        for key in ("problem_focus", "key_bridge", "guided_walkthrough", "try_now", "transfer_signal")
    ):
        return review

    error_layer = review.get("error_layer", "insufficient")
    subtags = review.get("core_design_subtags") or []
    focus = subtags[0] if subtags else error_layer

    guidance_map = {
        "state_design": {
            "problem_focus": "你不是没想到动态规划，而是还没有先把状态里每一维到底记录什么定稳，所以一写转移就开始混。",
            "main_block": "你不是没想到动态规划，而是还没有先把状态里每一维到底记录什么定稳，所以一写转移就开始混。",
            "key_bridge": "关键是先只保留真正限制决策的量，明确每一维表示什么，再决定哪些信息根本不该进状态。",
        "guided_walkthrough": "1. 先只看这题真正限制决策的量。\n2. 再用一句完整的话写清每一维记录什么。\n3. 最后删掉那些只是拿来比较结果、却不该进状态的信息。",
        "visual_hint": "真正要进状态的量 | 只是比较结果的量\n先保留左边，再删右边",
        "try_now": "先用一句完整的话写清 `dp[...]` 到底表示什么。",
        "next_step": "先别急着写公式，只写一句完整的话：`dp[...]` 到底表示什么，再检查有没有多余维度。",
        "transfer_signal": "如果你发现自己一写 DP 就想开很多维，先停下来问：每一维到底在记录什么，哪些量只是比较结果。",
    },
        "transition_design": {
            "problem_focus": "你不是不会写 DP，而是还没把“选”和“不选”或“从哪几种情况转来”整理完整，所以转移总会漏分支。",
            "main_block": "你不是不会写 DP，而是还没把“选”和“不选”或“从哪几种情况转来”整理完整，所以转移总会漏分支。",
            "key_bridge": "关键不是先背公式，而是先把当前状态可能从哪些上一状态来列全，再写成统一转移。",
        "guided_walkthrough": "1. 先盯住当前状态到底代表什么。\n2. 再把它可能来自的上一状态逐条列全。\n3. 最后再把这些来源改写成统一的转移式。",
        "visual_hint": "当前状态 <- 来源1\n当前状态 <- 来源2\n当前状态 <- 来源3",
        "try_now": "先把当前状态所有可能来源先列成中文。",
        "next_step": "拿一个最小样例，把当前状态的所有来源先列成中文，再对应写成转移式。",
        "transfer_signal": "如果你写出的转移只有一支，先检查是不是漏掉了“不选当前对象”或其他来源情况。",
    },
        "check_condition": {
            "problem_focus": "你不是不会二分或判定，而是还没有先把 `check` 到底在验证什么条件说清楚。",
            "main_block": "你不是不会二分或判定，而是还没有先把 `check` 到底在验证什么条件说清楚。",
            "key_bridge": "关键是先把“答案成立”翻成一句可检验的话，再决定 `check` 里需要维护哪些量。",
        "guided_walkthrough": "1. 先把 `check(mid)` 返回 true 翻成一句完整中文。\n2. 再找出为了验证这句话必须维护哪些量。\n3. 最后回到代码里检查这些量有没有被真正维护到。",
        "visual_hint": "check(mid)=true\n=> 说明某句话成立\n=> 为了验证它，需要维护哪些量？",
        "try_now": "先写一句完整中文：`check(mid)` 返回 true 到底表示什么？",
        "next_step": "先写一句完整中文：`check(mid)` 返回 true 到底表示什么，再对照代码看有没有偏掉。",
        "transfer_signal": "如果题目在问“这个值行不行”，先把“行”的定义写成一句完整判断条件。",
    },
        "enumeration_order": {
            "problem_focus": "你不是不会写循环，而是还没想清楚为什么这一维必须先枚举，所以顺序一换就把旧状态覆盖掉了。",
            "main_block": "你不是不会写循环，而是还没想清楚为什么这一维必须先枚举，所以顺序一换就把旧状态覆盖掉了。",
            "key_bridge": "关键是先判断当前转移依赖的是“上一层旧值”还是“本层新值”，再决定枚举顺序。",
        "guided_walkthrough": "1. 先找出当前转移依赖的是旧值还是刚更新的新值。\n2. 再顺着依赖方向判断这一维应该正着枚举还是倒着枚举。\n3. 最后用一个最小样例检查顺序一变时哪一步被覆盖了。",
        "visual_hint": "先看依赖：旧值 / 新值\n旧值 -> 常常倒着枚举\n新值 -> 常常正着枚举",
        "try_now": "先判断当前转移依赖的是旧值还是刚更新的新值。",
        "next_step": "先在纸上标出当前状态依赖哪些旧状态，再反推这一维应该正着枚举还是倒着枚举。",
        "transfer_signal": "如果你一改循环顺序答案就变，先检查转移依赖的是旧值还是刚更新的新值。",
    },
        "constraint_modeling": {
            "problem_focus": "你不是不会图论，而是还没先把题目里的限制关系整理成统一形式，导致变量、方向和边权都混在一起。",
            "main_block": "你不是不会图论，而是还没先把题目里的限制关系整理成统一形式，导致变量、方向和边权都混在一起。",
            "key_bridge": "关键是先把每条限制改写成统一约束，再确认“谁限制谁”和这条边表示什么。",
        "guided_walkthrough": "1. 先把题面条件逐条改写成统一约束。\n2. 再标出每条约束里谁限制谁。\n3. 最后再决定这条边的方向和边权应该表示什么。",
        "visual_hint": "条件1 -> 统一约束 -> 谁限制谁\n条件2 -> 统一约束 -> 谁限制谁",
        "try_now": "先把题面条件逐条改写成统一约束。",
        "next_step": "把题面条件逐条改写成统一约束，再标出每条约束里谁是被限制的量。",
        "transfer_signal": "如果题目一直在描述多个量之间的大小关系或先后限制，先想能不能整理成统一约束。",
    },
        "general_modeling": {
            "problem_focus": "你不是完全没思路，而是还没先把题目里的对象和关系写清楚，所以方法一直落不到地上。",
            "main_block": "你不是完全没思路，而是还没先把题目里的对象和关系写清楚，所以方法一直落不到地上。",
            "key_bridge": "关键是先确定“什么是点、什么是边、什么是状态/对象”，再考虑方法。",
        "guided_walkthrough": "1. 先写出题目里真正的对象有哪些。\n2. 再写这些对象之间有什么关系。\n3. 最后再判断这些对象更像点、边、状态还是别的结构。",
        "visual_hint": "对象A <-> 对象B\n对象A 做什么\n对象B 和谁有关",
        "try_now": "先只写一行：题目里的对象有哪些，它们之间有什么关系？",
        "next_step": "先只写一行：题目里的对象有哪些，它们之间有什么关系。",
        "transfer_signal": "如果题目表面信息很多，先不要猜算法，先把对象和关系写清楚。",
    },
        "method_selection": {
            "problem_focus": "你不是完全不会，而是还没先从题面里找出真正支持这个方法的结构信号，所以一上来就容易凭题感猜方法。",
            "main_block": "你不是完全不会，而是还没先从题面里找出真正支持这个方法的结构信号，所以一上来就容易凭题感猜方法。",
            "key_bridge": "关键不是先报方法名，而是先回到题面，看清到底是哪一个结构信号在支持这个方法。",
            "guided_walkthrough": "1. 先圈出题面里最像线索的对象、操作或限制。\n2. 再问：这些线索为什么更像在支持当前方法。\n3. 最后再回到方法名，检查它是不是和这些题面信号对得上。",
            "visual_hint": "题面对象/操作/限制\n-> 哪一个是真线索\n-> 这条线索支持什么方法",
            "try_now": "先指出题面里一个真正支持当前方法的结构信号。",
            "next_step": "先别报方法名，先指出题面里一个真正支持当前方法的结构信号。",
            "transfer_signal": "如果你一看到题就想套熟方法，先停下来问：题面里到底哪一个结构信号真的在支持它。",
        },
        "complexity_fit": {
            "problem_focus": "你不是完全不会，而是还没先把数据范围和总量级放在一起判断，所以会把“能不能过”这一步留到最后碰运气。",
            "main_block": "你不是完全不会，而是还没先把数据范围和总量级放在一起判断，所以会把“能不能过”这一步留到最后碰运气。",
            "key_bridge": "关键不是先报一个更高级的方法名，而是先估总量级，看当前做法会不会先超时。",
            "guided_walkthrough": "1. 先圈出题面里真正会一起变大的量。\n2. 再把这些量乘起来，估总量级会不会先炸。\n3. 最后才判断当前做法是不是还撑得住。",
            "visual_hint": "数据范围\n-> 哪些量一起变大\n-> 总量级会不会先炸",
            "try_now": "先只回答一句：这题更该先判断规模能不能过，还是先背方法名？",
            "next_step": "先把会一起变大的量圈出来，再估总量级会不会先炸。",
            "transfer_signal": "如果题面里有两个以上会一起变大的量，先别急着报方法名，先估总量级。",
        },
        "shared_prefix_merging": {
            "problem_focus": "你不是完全不会 trie，而是还没先把“为什么查询时不用重看所有消息”这一步站稳。",
            "main_block": "你不是完全不会 trie，而是还没先把“为什么查询时不用重看所有消息”这一步站稳。",
            "key_bridge": "关键不是 trie 名字高级，而是公共前缀先合在一起后，查询时就只沿当前前缀路径走。",
            "guided_walkthrough": "1. 先挑两三条有相同开头的串。\n2. 再看这些相同开头为什么可以先合在一起。\n3. 最后回到查询，确认为什么不用把所有消息重新拿出来比。",
            "visual_hint": "101\n100\n11\n相同开头先并在一起\n查询时只沿前缀路径走",
            "try_now": "先只回答一句：trie 为什么能省掉重看所有消息这件事？",
            "next_step": "先画两三条有相同开头的串，再看查询时为什么只沿当前前缀往下走。",
            "transfer_signal": "如果题目反复按前缀查很多字符串，先想公共前缀能不能先合在一起。",
        },
        "left_bound_update": {
            "problem_focus": "你不是不会二分，而是还没先把“找到一个等于 x 的位置后，为什么还要保留它继续往左找”这一步站稳。",
            "main_block": "你不是不会二分，而是还没先把“找到一个等于 x 的位置后，为什么还要保留它继续往左找”这一步站稳。",
            "key_bridge": "关键不是看到相等就立刻停，而是先保留 mid 这个候选，再继续往左缩，才能找到最左位置。",
            "guided_walkthrough": "1. 先盯住当前目标是不是“最左那个位置”。\n2. 再看 `a[mid] == x` 时，mid 为什么还可能就是答案。\n3. 最后才决定边界怎么缩，保证 mid 不会被直接丢掉。",
            "visual_hint": "目标：最左位置\n看到相等\n-> 先保留 mid\n-> 再继续往左缩",
            "try_now": "先只回答一句：如果 `a[mid] == x`，为什么还不能马上把 mid 丢掉？",
            "next_step": "先说清目标是不是最左位置，再判断 `a[mid] == x` 时 mid 为什么还要保留。",
            "transfer_signal": "如果题目要你找第一个/最左一个满足条件的位置，看到相等时先别急着停，先想 mid 要不要保留。",
        },
        "lazy_semantics": {
            "problem_focus": "你不是不会线段树，而是还没先把 lazy 标记到底记录什么站稳，所以一看到下传就开始混。",
            "main_block": "你不是不会线段树，而是还没先把 lazy 标记到底记录什么站稳，所以一看到下传就开始混。",
            "key_bridge": "关键不是把 lazy 当成“代码还没执行完”，而是把它看成“这段区间还有一份已经确定、但还没下传给孩子的信息”。",
            "guided_walkthrough": "1. 先只盯住一个节点和它代表的区间。\n2. 再看 lazy 记录的是这段区间还有哪份信息没下传。\n3. 最后才回到 pushdown，确认为什么孩子还没收到这份信息。",
            "visual_hint": "父节点区间\nsum 已更新\nlazy 还挂着\n-> 孩子还没收到这份信息",
            "try_now": "先只回答一句：lazy 标记到底记录的是哪一类信息？",
            "next_step": "先盯住一个节点，说明 lazy 记录的到底是什么，不要先讲代码执行顺序。",
            "transfer_signal": "如果你总把 lazy 看成“代码没跑完”，先回到区间含义，看它到底在记录哪份还没下传的信息。",
        },
    }

    explicit_focus = str(review.get("focus") or "").strip()
    if explicit_focus:
        focus = explicit_focus

    guidance = guidance_map.get(focus)
    if not guidance and error_layer == "modeling":
        guidance = guidance_map["general_modeling"]
    if not guidance and error_layer == "core_design":
        guidance = guidance_map["state_design"]

    if not guidance:
        return review

    for key, value in guidance.items():
        if not review.get(key):
            review[key] = value
    _sync_guided_review_aliases(review)
    return review


def _sync_guided_review_aliases(review: dict) -> dict:
    """Keep new guided fields canonical while preserving legacy aliases."""
    if not review.get("problem_focus"):
        review["problem_focus"] = review.get("main_block", "")
    if not review.get("main_block"):
        review["main_block"] = review.get("problem_focus", "")
    if not review.get("try_now"):
        review["try_now"] = review.get("next_step", "")
    if not review.get("next_step"):
        review["next_step"] = review.get("try_now", "")
    if not review.get("visual_hint"):
        review["visual_hint"] = ""
    if not review.get("topic_commonality"):
        transfer = review.get("transfer_signal", "")
        bridge = review.get("key_bridge", "")
        review["topic_commonality"] = "\n\n".join(part for part in (
            f"这类题的共性：{transfer}" if transfer else "",
            f"回到这道题：{bridge}" if bridge else "",
        ) if part)
    if not review.get("solution_walkthrough"):
        walkthrough = review.get("guided_walkthrough", "")
        bridge = review.get("key_bridge", "")
        review["solution_walkthrough"] = "\n\n".join(part for part in (
            bridge,
            walkthrough,
        ) if part)
    if not review.get("transfer_checklist"):
        try_now = review.get("try_now") or review.get("next_step", "")
        transfer = review.get("transfer_signal", "")
        review["transfer_checklist"] = "\n".join(part for part in (
            f"- 下次先看：{transfer}" if transfer else "",
            f"- 现在验证：{try_now}" if try_now else "",
        ) if part)
    return review


REVIEW_META_KNOWLEDGE_TERMS = (
    "当前对象",
    "后续空间",
    "不吃亏",
    "留空间",
    "局部优先",
    "先记贪心结论",
    "先报方法名",
)


def _guard_review_against_meta_knowledge(
    review: dict,
    problem_title: str,
    problem_context: str | None,
    bottleneck_text: str | None,
) -> dict:
    context_text = "\n".join(
        part.strip()
        for part in (problem_title or "", problem_context or "", bottleneck_text or "")
        if str(part or "").strip()
    )
    context_hits = set(re.findall(r"[A-Za-z0-9_()+\\-]{2,}|[\u4e00-\u9fff]{2,}", context_text))

    def looks_meta(value: str) -> bool:
        return any(term in value for term in REVIEW_META_KNOWLEDGE_TERMS)

    def has_context_anchor(value: str) -> bool:
        value_hits = set(re.findall(r"[A-Za-z0-9_()+\\-]{2,}|[\u4e00-\u9fff]{2,}", value or ""))
        return len(value_hits & context_hits) >= 2

    main_block = (review.get("main_block") or "").strip()
    if main_block and looks_meta(main_block) and not has_context_anchor(main_block) and bottleneck_text:
        review["main_block"] = _compact_text(bottleneck_text, 60)

    key_bridge = (review.get("key_bridge") or "").strip()
    diagnosis = (review.get("diagnosis") or "").strip()
    if key_bridge and looks_meta(key_bridge) and not has_context_anchor(key_bridge):
        if diagnosis and not looks_meta(diagnosis):
            review["key_bridge"] = _compact_text(diagnosis, 60)
        elif bottleneck_text:
            review["key_bridge"] = "关键不是直接套结论，而是先把你卡住的这一步为什么成立说清楚。"
    return review


def _normalize_review(parsed: dict, fallback_text: str = "") -> dict:
    review = {
        "error_tags": _normalize_error_tags(parsed.get("error_tags", [])),
        "error_layer": str(parsed.get("error_layer", "insufficient")).strip(),
        "error_layer_confidence": str(
            parsed.get("error_layer_confidence", parsed.get("confidence", "low"))
        ).strip(),
        "core_design_subtags": [],
        "diagnosis": str(parsed.get("diagnosis", "")).strip(),
        "next_action": str(parsed.get("next_action", "")).strip(),
        "suggested_topic": str(parsed.get("suggested_topic", "")).strip(),
        # v2.1 学生纠偏层
        "problem_focus": str(parsed.get("problem_focus", parsed.get("main_block", ""))).strip(),
        "main_block": str(parsed.get("main_block", "")).strip(),
        "key_bridge": str(parsed.get("key_bridge", "")).strip(),
        "visual_hint": str(parsed.get("visual_hint", "")).strip(),
        "guided_walkthrough": str(parsed.get("guided_walkthrough", "")).strip(),
        "try_now": str(parsed.get("try_now", parsed.get("next_step", ""))).strip(),
        "next_step": str(parsed.get("next_step", "")).strip(),
        "transfer_signal": str(parsed.get("transfer_signal", "")).strip(),
        "topic_commonality": str(parsed.get("topic_commonality", "")).strip(),
        "solution_walkthrough": str(parsed.get("solution_walkthrough", "")).strip(),
        "transfer_checklist": str(parsed.get("transfer_checklist", "")).strip(),
    }
    _sync_guided_review_aliases(review)

    if review["error_layer"] not in ERROR_LAYERS:
        review["error_layer"] = "insufficient"

    if review["error_layer_confidence"] not in CONFIDENCE_LEVELS:
        review["error_layer_confidence"] = "low"

    review["core_design_subtags"] = _normalize_subtags(
        parsed.get("core_design_subtags", []),
        review["error_layer"],
    )
    if review["error_layer"] == "core_design":
        inferred_focus = _detect_quiz_focus(review)
        if inferred_focus in CORE_DESIGN_SUBTAGS:
            review["core_design_subtags"] = [inferred_focus]

    if not review["diagnosis"] and fallback_text:
        review["diagnosis"] = fallback_text[:200].strip()
    if not review["next_action"]:
        review["next_action"] = "先补充更具体的卡点过程，再根据当前错误层做针对性训练。"
    if not review["suggested_topic"]:
        review["suggested_topic"] = "先补当前题型对应的基础训练。"

    review = _backfill_student_guidance(review)

    if review["error_layer"] == "insufficient":
        if not review["problem_focus"]:
            review["problem_focus"] = "你当前主要卡点还不够清晰，需要补充更多题目信息和尝试过程。"
        if not review["key_bridge"]:
            review["key_bridge"] = "先把题目要求、限制条件和你的思路过程写清楚，系统才能定位关键桥梁。"
        if not review["guided_walkthrough"]:
            review["guided_walkthrough"] = "1. 先写清题目求什么。\n2. 再写你试了哪一步。\n3. 最后指出卡住的具体位置。"
        if not review["visual_hint"]:
            review["visual_hint"] = "题目求什么\n-> 你试到哪一步\n-> 你具体卡在哪"
        if not review["try_now"]:
            review["try_now"] = "先补充题意、思路和具体卡住的位置。"
        if not review["transfer_signal"]:
            review["transfer_signal"] = '如果你自己也说不清卡点，先写清楚“题目求什么、我试了什么、哪里出错”。'
        _sync_guided_review_aliases(review)

    return review


def _parse_review(text: str) -> dict:
    """解析 LLM 返回的复盘内容"""
    json_block = _extract_json_block(text)
    if json_block:
        try:
            parsed = json.loads(_sanitize_json_like_text(json_block))
            if isinstance(parsed, dict):
                return _normalize_review(parsed, fallback_text=text)
        except Exception:
            repaired = _repair_partial_json_review(json_block)
            if any(repaired.values()):
                return _normalize_review(repaired, fallback_text=text)

    parsed = {
        "error_tags": [],
        "error_layer": "insufficient",
        "error_layer_confidence": "low",
        "core_design_subtags": [],
        "diagnosis": "",
        "next_action": "",
        "suggested_topic": "",
        "problem_focus": "",
        "main_block": "",
        "key_bridge": "",
        "visual_hint": "",
        "guided_walkthrough": "",
        "try_now": "",
        "next_step": "",
        "transfer_signal": "",
    }

    error_match = re.search(r'错误标签[:：]\s*(.+?)(?=\n|$)', text)
    if error_match:
        parsed["error_tags"] = error_match.group(1).strip()

    layer_match = re.search(r'(?:错误层级|错误大类|error_layer)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if layer_match:
        parsed["error_layer"] = layer_match.group(1).strip()

    confidence_match = re.search(r'(?:置信度|error_layer_confidence|confidence)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if confidence_match:
        parsed["error_layer_confidence"] = confidence_match.group(1).strip()

    subtags_match = re.search(r'(?:核心设计子标签|core_design_subtags)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if subtags_match:
        parsed["core_design_subtags"] = subtags_match.group(1).strip()

    diagnosis_match = re.search(r'问题诊断[:：]\s*(.+?)(?=下一步行动|推荐专题|$)', text, re.DOTALL)
    if diagnosis_match:
        parsed["diagnosis"] = diagnosis_match.group(1).strip()

    next_match = re.search(r'下一步行动[:：]\s*(.+?)(?=推荐专题|$)', text, re.DOTALL)
    if next_match:
        parsed["next_action"] = next_match.group(1).strip()

    topic_match = re.search(r'推荐专题[:：]\s*(.+)$', text, re.DOTALL)
    if topic_match:
        parsed["suggested_topic"] = topic_match.group(1).strip()

    problem_focus_match = re.search(r'(?:你卡在哪|你主要卡在哪|problem_focus|main_block)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if problem_focus_match:
        parsed["problem_focus"] = problem_focus_match.group(1).strip()

    main_block_match = re.search(r'(?:你主要卡在哪|main_block)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if main_block_match:
        parsed["main_block"] = main_block_match.group(1).strip()

    key_bridge_match = re.search(r'(?:先抓住什么|这题的关键桥梁|key_bridge)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if key_bridge_match:
        parsed["key_bridge"] = key_bridge_match.group(1).strip()

    visual_hint_match = re.search(r'(?:看图想一想|visual_hint)[:：]\s*(.+?)(?=跟我走一遍|guided_walkthrough|现在你来试|try_now|你现在立刻该做什么|next_step|下次遇到什么信号要想到它|下次怎么认出来|transfer_signal|$)', text, re.IGNORECASE | re.DOTALL)
    if visual_hint_match:
        parsed["visual_hint"] = visual_hint_match.group(1).strip()

    guided_walkthrough_match = re.search(r'(?:跟我走一遍|guided_walkthrough)[:：]\s*(.+?)(?=现在你来试|try_now|你现在立刻该做什么|next_step|下次遇到什么信号要想到它|下次怎么认出来|transfer_signal|$)', text, re.IGNORECASE | re.DOTALL)
    if guided_walkthrough_match:
        parsed["guided_walkthrough"] = guided_walkthrough_match.group(1).strip()

    try_now_match = re.search(r'(?:现在你来试|try_now|你现在立刻该做什么|next_step)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if try_now_match:
        parsed["try_now"] = try_now_match.group(1).strip()

    next_step_match = re.search(r'(?:你现在立刻该做什么|next_step)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if next_step_match:
        parsed["next_step"] = next_step_match.group(1).strip()

    transfer_signal_match = re.search(r'(?:下次遇到什么信号要想到它|下次怎么认出来|transfer_signal)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if transfer_signal_match:
        parsed["transfer_signal"] = transfer_signal_match.group(1).strip()

    return _normalize_review(_backfill_student_guidance(parsed), fallback_text=text)


def _quiz_text_context(review_context: dict) -> str:
    return " ".join(
        str(part or "")
        for part in (
            review_context.get("problem_title"),
            review_context.get("problem_context"),
            review_context.get("bottleneck_text"),
            review_context.get("main_block"),
            review_context.get("key_bridge"),
            review_context.get("next_step"),
        )
    )


def _detect_quiz_focus(review_context: dict) -> str:
    explicit_focus = str(review_context.get("focus") or "").strip()
    if explicit_focus in STRUCTURAL_QUIZ_FOCI or explicit_focus in {"reading_target", "implementation_debug"}:
        return explicit_focus

    error_layer = review_context.get("error_layer", "insufficient")
    subtags = review_context.get("core_design_subtags") or []
    text = _quiz_text_context(review_context)

    if error_layer == "core_design":
        if _contains_any(
            text,
            (
                "最左",
                "左边界",
                "第一个等于",
                "第一个出现",
                "lower_bound",
                "保留 mid",
                "保留mid",
                "r = mid",
                "右边界 = mid",
                "a[mid] == x",
                "a[mid]==x",
            ),
        ):
            return "left_bound_update"
        if _is_tree_path_difference_context(text):
            return "tree_path_difference"
        if _contains_any(text, ("lazy", "下传", "pushdown", "标记", "懒标记")):
            return "lazy_semantics"
        if _is_shared_prefix_context(text):
            return "shared_prefix_merging"
        if _contains_any(text, ("递归", "base case", "结束条件", "停下来", "递归返回", "回溯", "分治", "叶子")):
            return "recursion_structure"
        for subtag in subtags:
            if subtag == "greedy_basis" and not _contains_any(text, ("贪心", "排序", "优先选", "依据")):
                continue
            if subtag in HIGH_RISK_REVIEW_FOCI:
                return subtag
            if subtag in CORE_DESIGN_SUBTAGS:
                return subtag
        if _contains_any(text, ("直径", "最长路", "新边", "连通块", "最远点", "候选")):
            return "tree_diameter_candidates"
        if _contains_any(text, CONSTRAINT_GRAPH_TERMS + ("同时满足", "并列约束", "谁限制谁")):
            return "constraint_modeling"
        if _contains_any(text, ("对象", "关系", "点", "边", "谁和谁")):
            return "general_modeling"
        if _contains_any(text, ("状态", "dp", "维", "记录", "表示")):
            return "state_design"
        if _contains_any(text, ("转移", "递推", "不选", "选当前")):
            return "transition_design"
        if _contains_any(text, ("check", "可行", "判定", "二分")):
            return "check_condition"
        if _contains_any(text, ("贪心", "排序", "优先选", "依据")):
            return "greedy_basis"
        if _contains_any(text, ("枚举", "顺序", "先枚举")):
            return "enumeration_order"

    if error_layer == "modeling":
        if _contains_any(text, CONSTRAINT_GRAPH_TERMS + ("同时满足", "并列约束", "谁限制谁")):
            return "constraint_modeling"
        if _contains_any(text, ("对象", "关系", "点", "边", "谁和谁")):
            return "general_modeling"
        return "general_modeling"

    if error_layer == "implementation":
        if _contains_any(
            text,
            (
                "最左",
                "左边界",
                "第一个等于",
                "第一个出现",
                "lower_bound",
                "保留 mid",
                "保留mid",
                "r = mid",
                "右边界 = mid",
                "a[mid] == x",
                "a[mid]==x",
            ),
        ):
            return "left_bound_update"
        if _contains_any(text, ("long long", "int", "溢出", "精度", "范围太大", "1e18", "10^18", "double", "取模", "mod")):
            return "data_type"
        if _contains_any(text, ("循环范围", "起点", "终点", "下标", "越界", "1-indexed", "0-indexed", "i <= n", "i < n", "枚举到哪里", "边界错了")):
            return "loop_boundary"
        if _contains_any(text, ("边界", "最小", "n=1", "空区间", "特判")):
            return "boundary_debug"
        return "implementation_debug"

    if error_layer == "method":
        if _is_tree_path_difference_context(text):
            return "tree_path_difference"
        if _contains_any(
            text,
            (
                "check(mid)",
                "check（mid）",
                "返回 true",
                "返回true",
                "返回 false",
                "返回false",
                "当前 mid 可行",
                "当前mid可行",
                "二分方向",
                "往哪边缩",
                "判定条件",
                "可行还是太大",
            ),
        ):
            return "check_condition"
        if _is_shared_prefix_context(text) and _contains_any(text, ("公共前缀", "前缀路径", "重看所有消息", "沿当前前缀", "只沿前缀", "查询时不用重看")):
            return "shared_prefix_merging"
        if _contains_any(
            text,
            (
                "结构信号",
                "题面信号",
                "支持这个方法",
                "支持 trie",
                "支持trie",
                "先猜可能要 trie",
                "先猜可能要trie",
                "背模板",
                "凭题感猜",
                "猜一个方法名",
                "为什么该用这个方法",
            ),
        ):
            return "method_selection"
        if _contains_any(
            text,
            (
                "复杂度",
                "O(",
                "数据范围",
                "数据量",
                "规模",
                "量级",
                "乘积",
                "总量",
                "字符比较次数",
                "n <=",
                "n<=",
                "会不会超时",
                "TLE",
                "超时",
                "能不能过",
            ),
        ):
            return "complexity_fit"
        return "method_selection"
    if error_layer == "reading":
        return "reading_target"
    return "unknown"


def _default_target_bridge(review_context: dict, focus: str) -> str:
    existing = (review_context.get("key_bridge") or "").strip()
    if existing:
        return existing
    mapping = {
        "reading_target": "先看清题目到底要求什么和限制什么",
        "method_selection": "先找出题面里支持这个方法的信号",
        "shared_prefix_merging": "先说清公共前缀为什么能先合在一起",
        "constraint_modeling": "先把题目里的限制关系写成统一形式",
        "general_modeling": "先把题目里的对象和关系写清楚",
        "state_design": "先确定状态里每一维到底表示什么",
        "transition_design": "先确认转移漏没漏掉一种情况",
        "tree_path_difference": "先把一条树上路径贡献转成端点/LCA 标记，再用 DFS 汇总还原经过次数",
        "tree_diameter_candidates": "先比较新最长路会来自哪几类候选",
        "check_condition": "先想清楚 check 在验证什么",
        "left_bound_update": "先说清 `a[mid] == x` 时为什么还要保留 mid 继续往左找",
        "greedy_basis": "先说清楚为什么这个对象要优先选",
        "enumeration_order": "先确定为什么这一维必须先枚举",
        "lazy_semantics": "先说清 lazy 标记记录的是哪份还没下传的信息",
        "data_type": "先根据数据范围确认该开什么类型",
        "loop_boundary": "先确定这个循环到底应该从哪里开始、到哪里结束",
        "recursion_structure": "先写清递归什么时候停、每一层在表示什么",
        "complexity_fit": "先根据数据范围判断当前复杂度能不能过",
        "boundary_debug": "先检查最小边界和默认前提",
        "implementation_debug": "先找出哪类默认前提最可能先出错",
        "unknown": "先把你卡住的这一小步说清楚",
    }
    return mapping.get(focus, mapping["unknown"])


def _bridge_first_step_phrase(review_context: dict, focus: str, fallback: str) -> str:
    text = " ".join(
        part.strip()
        for part in (
            review_context.get("key_bridge") or "",
            review_context.get("next_step") or "",
            review_context.get("main_block") or "",
            review_context.get("problem_context") or "",
        )
        if part and part.strip()
    )

    if focus == "general_modeling":
        if _contains_any(text, ("谁和谁", "关系")):
            return "先写清题目里“谁和谁有关系”"
        if _contains_any(text, ("点", "边")):
            return "先确定什么当点、什么表示关系"
        if _contains_any(text, ("对象",)):
            return "先把题目里的对象和关系写清楚"
    if focus == "constraint_modeling":
        if _contains_any(text, ("不等式", "统一形式", "关系式")):
            return "先把限制关系写成统一形式"
    if focus == "state_design":
        if _contains_any(text, ("时间",)):
            return "先说清状态里“时间”这一维表示什么"
        if _contains_any(text, ("容量", "体积")):
            return "先说清状态里“容量”这一维表示什么"
        if _contains_any(text, ("位置", "阶段", "前 i", "前i")):
            return "先说清状态里“位置/阶段”这一维表示什么"
        if _contains_any(text, ("哪一维", "这一维", "状态")):
            return "先说清这一维状态到底表示什么"
    if focus == "method_selection":
        if _contains_any(text, ("信号", "特征")):
            return "先找出题面里支持这个方法的那个信号"
        if _contains_any(text, ("trie", "前缀", "拦截串", "消息")):
            return "先找出题面里哪一个信号在支持 trie"
    if focus == "shared_prefix_merging":
        if _contains_any(text, ("公共前缀", "相同开头")):
            return "先说清公共前缀为什么能先合在一起"
        if _contains_any(text, ("重看所有消息", "沿当前前缀")):
            return "先说清查询时为什么不用重看所有消息"
    if focus == "left_bound_update":
        if _contains_any(text, ("a[mid] == x", "a[mid]==x", "相等")):
            return "先说清 `a[mid] == x` 时为什么还要保留 mid"
        if _contains_any(text, ("最左", "左边界", "第一个")):
            return "先说清为什么要保留 mid 继续往左找"
    if focus == "lazy_semantics":
        if _contains_any(text, ("下传", "pushdown")):
            return "先说清 lazy 里哪份信息还没下传"
        if _contains_any(text, ("标记", "懒标记", "lazy")):
            return "先说清 lazy 标记到底记录什么"
    if focus == "tree_path_difference":
        if _contains_any(text, ("lca", "最近公共祖先", "树剖", "树链剖分")):
            return "先说清一条路径为什么能在端点和 LCA 附近打标记"
        if _contains_any(text, ("经过次数", "多条路径", "路径贡献")):
            return "先说清路径贡献为什么能先差分、最后 DFS 汇总"
    if focus == "tree_diameter_candidates":
        if _contains_any(text, ("新边", "连起来")):
            return "先比较加上新边后最长路会来自哪几类候选"
        if _contains_any(text, ("直径", "最长路")):
            return "先说清新最长路会不会经过新边"
    if focus == "data_type":
        if _contains_any(text, ("1e18", "10^18", "很大", "范围")):
            return "先看数据范围会不会超过 int"
        if _contains_any(text, ("溢出", "long long")):
            return "先确认这里是不是必须开 long long"
    if focus == "loop_boundary":
        if _contains_any(text, ("1-indexed", "下标")):
            return "先说清这个循环到底是按 0 下标还是 1 下标写"
        if _contains_any(text, ("起点", "终点", "范围")):
            return "先定清这个循环应该从哪到哪"
    if focus == "recursion_structure":
        if _contains_any(text, ("base case", "结束条件", "停下来")):
            return "先写清递归什么时候停下来"
        if _contains_any(text, ("这一层", "当前层", "递归函数")):
            return "先说清当前这一层递归到底表示什么"
    if focus == "complexity_fit":
        if _contains_any(text, ("TLE", "超时")):
            return "先用数据范围判断这个复杂度会不会超时"
        if _contains_any(text, ("O(", "复杂度")):
            return "先判断题目的数据范围能不能支持这个复杂度"
    if focus == "check_condition":
        if _contains_any(text, ("check", "判定", "验证")):
            return "先想清 check 到底在验证什么"
    return fallback


def _default_bridge_feedback(correct_answer: str, review_context: dict) -> str:
    answer = (correct_answer or "").strip()
    target_bridge = (review_context.get("key_bridge") or review_context.get("next_step") or "").strip()
    if answer:
        if target_bridge:
            return f"你已经知道：这一步最关键的是“{answer}”。这正是你原题里“{target_bridge}”这一步要站稳的地方。"
        return f"你已经知道：这一步最关键的是“{answer}”。这正是你原题里卡住的那一小步。"
    if target_bridge:
        return f"你已经知道：这一步真正要站稳的是“{target_bridge}”。"
    return "你已经知道：这一步真正要站稳的，是把当前桥梁里最关键的结构说清楚。"


def _infer_algorithm_category(review_context: dict, focus: str) -> str:
    text = _quiz_text_context(review_context)
    fallback = {
        "state_design": "动态规划",
        "transition_design": "动态规划",
        "enumeration_order": "动态规划",
        "check_condition": "判定/二分",
        "left_bound_update": "二分边界",
        "greedy_basis": "贪心/排序",
        "tree_path_difference": "树上差分/LCA",
        "tree_diameter_candidates": "树的直径",
        "general_modeling": "图论建模",
        "constraint_modeling": "差分约束",
        "boundary_debug": "边界/调试",
        "method_selection": "方法判断",
        "shared_prefix_merging": "Trie/前缀树",
        "lazy_semantics": "线段树",
        "data_type": "数据类型/范围",
        "loop_boundary": "循环/边界",
        "recursion_structure": "递归/搜索",
        "complexity_fit": "复杂度判断",
    }
    if focus in fallback:
        return fallback[focus]
    if _contains_any(text, ("背包", "容量", "体积", "价值", "物品")):
        return "背包类"
    if _contains_any(text, ("树", "子树", "根", "节点", "树上")):
        return "树形DP"
    if _contains_any(text, ("区间", "括号", "合并区间")):
        return "区间DP"
    if _contains_any(text, ("二分", "check", "可行")):
        return "二分答案"
    if _contains_any(text, ("差分约束", "不等式", "约束")):
        return "差分约束"
    if _contains_any(text, ("最小生成树", "Kruskal", "Prim", "贪心", "排序", "哈夫曼", "Huffman", "活动选择")):
        return "贪心/排序"
    if _contains_any(text, ("建图", "拓扑", "强连通", "SCC", "有向图", "无向图", "点", "边")):
        return "图论建模"
    if _contains_any(text, ("边界", "越界", "特判", "n=1", "空区间", "下标")):
        return "边界/调试"
    if _contains_any(text, ("方法", "题型", "信号", "特征", "模板")):
        return "方法判断"
    if _contains_any(text, ("最长上升子序列", "LIS", "子序列")):
        return "序列DP"
    if _contains_any(text, ("long long", "int", "溢出", "精度")):
        return "数据类型/范围"
    if _contains_any(text, ("递归", "回溯", "base case", "分治")):
        return "递归/搜索"
    if _contains_any(text, ("复杂度", "TLE", "数据范围")):
        return "复杂度判断"
    return fallback.get(focus, "通用结构题")


def _bridge_signal_hits(text: str, keywords: tuple[str, ...]) -> list[str]:
    lowered = (text or "").lower()
    hits = []
    for keyword in keywords:
        if keyword.lower() in lowered and keyword not in hits:
            hits.append(keyword)
    return hits


def _resolve_bridge_decision(review_context: dict) -> dict:
    """Return observation-only bridge routing metadata without changing execution focus."""
    text = _quiz_text_context(review_context)
    stable_focus = _detect_quiz_focus(review_context)
    focus_source = "explicit" if str(review_context.get("focus") or "").strip() else "source_rule"
    matched_signals: list[str] = []
    conflict_signals: list[str] = []
    suppressed_candidates: list[str] = []

    signal_map = {
        "tree_path_difference": (
            "树上路径",
            "树上路线",
            "多条路径",
            "经过次数",
            "访问次数",
            "LCA",
            "公共祖先",
            "树剖",
            "差分",
            "DFS 汇总",
            "边",
        ),
        "shared_prefix_merging": (
            "trie",
            "前缀",
            "消息",
            "拦截串",
            "经过次数",
            "结束次数",
        ),
        "lazy_semantics": (
            "lazy",
            "懒标记",
            "标记",
            "pushdown",
            "下传",
            "区间",
        ),
        "method_selection": (
            "方法",
            "题面信号",
            "结构信号",
            "KMP",
            "next 数组",
            "失配",
            "前后缀",
        ),
    }
    matched_signals.extend(_bridge_signal_hits(text, signal_map.get(stable_focus, ())))

    tree_context = _is_tree_path_difference_context(text)
    trie_context = _is_shared_prefix_context(text) or _is_trie_node_count_context(text)
    lazy_context = _contains_any(text, ("lazy", "懒标记", "pushdown", "下传", "标记"))
    if tree_context and trie_context:
        conflict_signals.append("经过次数 also matches shared_prefix_merging")
        suppressed_candidates.append("shared_prefix_merging")
    if tree_context and lazy_context:
        conflict_signals.append("标记 also matches lazy_semantics")
        suppressed_candidates.append("lazy_semantics")
    if stable_focus != "tree_path_difference" and _is_tree_path_difference_context(text):
        suppressed_candidates.append("tree_path_difference")

    candidate_bridge_id = ""
    candidate_parent_focus = ""
    candidate_confidence = ""
    open_bridge_label = ""
    open_bridge_reason = ""
    status = "known_bridge" if stable_focus not in {"unknown", "implementation_debug"} else "open_bridge"
    route_confidence = "high" if status == "known_bridge" else "low"

    if stable_focus == "tree_path_difference" and _contains_any(text, ("边经过", "哪条边", "道路", "每条边", "边被经过", "对边的贡献")):
        status = "candidate_bridge"
        candidate_bridge_id = "tree_path_difference.edge_variant"
        candidate_parent_focus = "tree_path_difference"
        candidate_confidence = "medium"
        open_bridge_label = "树上边贡献差分"
        open_bridge_reason = "当前题在问边经过次数，稳定桥仍先按树上路径差分父桥执行。"
        route_confidence = "medium"

    if _contains_any(text, ("KMP", "kmp", "next 数组", "失配", "前后缀")):
        status = "open_bridge"
        stable_focus = stable_focus if stable_focus != "unknown" else "method_selection"
        candidate_bridge_id = "kmp_failure_link"
        candidate_parent_focus = "method_selection"
        candidate_confidence = "low"
        open_bridge_label = "KMP 失配跳转 / failure link"
        open_bridge_reason = "当前系统还没有稳定 KMP 机制桥，先记录为开放候选，不驱动确定性链路。"
        matched_signals.extend(_bridge_signal_hits(text, signal_map["method_selection"]))
        route_confidence = "low"

    card_id = _knowledge_card_id(review_context, stable_focus)
    return {
        "status": status,
        "stable_focus": stable_focus,
        "card_id": card_id,
        "route_confidence": route_confidence,
        "focus_source": focus_source,
        "matched_signals": list(dict.fromkeys(matched_signals)),
        "conflict_signals": list(dict.fromkeys(conflict_signals)),
        "suppressed_candidates": list(dict.fromkeys(suppressed_candidates)),
        "candidate_bridge_id": candidate_bridge_id,
        "candidate_parent_focus": candidate_parent_focus,
        "candidate_confidence": candidate_confidence,
        "open_bridge_label": open_bridge_label,
        "open_bridge_reason": open_bridge_reason,
    }


def _load_prompt_file(relative_path: str) -> str:
    path = PROMPTS_DIR / relative_path
    return path.read_text(encoding="utf-8").strip()


def _expand_prompt_snippets(text: str) -> str:
    pattern = re.compile(r"{{\s*snippet:([a-zA-Z0-9_\-]+)\s*}}")

    def repl(match: re.Match[str]) -> str:
        snippet_name = match.group(1)
        return _load_prompt_file(f"snippets/{snippet_name}.md")

    return pattern.sub(repl, text)


def _render_prompt_template(relative_path: str, variables: dict[str, str]) -> str:
    text = _expand_prompt_snippets(_load_prompt_file(relative_path))
    pattern = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
    return pattern.sub(lambda match: str(variables.get(match.group(1), "")), text)


def _confirm_focus_instruction(focus: str) -> str:
    mapping = {
        "state_design": "优先生成“状态定义/状态含义结构题”。题目应让学生在几个具体状态定义里判断哪一个更稳，不能要求计算具体状态值。",
        "transition_design": "优先生成“转移关系结构题”。题目应让学生在几个具体转移写法里判断哪个更完整，不能要求代入具体数字算出结果。",
        "check_condition": "优先生成“check 条件结构题”。题目应让学生在几个具体说法里判断 check 到底在验证什么，不能要求给定具体 mid 去算返回值。",
        "enumeration_order": "优先生成“枚举顺序结构题”。题目应让学生在几个具体顺序描述里判断哪种顺序正确或为什么不能反过来，不能要求模拟循环后的具体数组结果。",
    }
    return mapping.get(focus, "优先生成结构型小题，不要生成计算题。")


def _state_axis_label(review_context: dict) -> tuple[str, str]:
    text = _quiz_text_context(review_context)
    if _contains_any(text, ("时间", "时刻", "节课", "天数", "轮次", "回合")):
        return "时间", "已经到了第几个时间点或第几次决策"
    if _contains_any(text, ("容量", "体积", "背包")):
        return "容量", "当前已经用了多少容量"
    if _contains_any(text, ("位置", "下标", "阶段", "前 i", "第 i")):
        return "位置/阶段", "已经处理到第几个位置或第几个阶段"
    if _contains_any(text, ("个数", "数量", "选了", "选择了", "次数")):
        return "数量", "已经选了多少个对象"
    return "这一维", "当前推进到哪一个阶段或资源进度"


def _state_slot_label(review_context: dict) -> str:
    text = _quiz_text_context(review_context)
    match = re.search(r"([A-Za-z_][A-Za-z0-9_]*(?:\[[^\]\n]{1,24}\]){1,3})", text)
    if match:
        return match.group(1)
    if _contains_any(text, ("这一格", "这格")):
        return "这一格"
    return "这个状态格"


def _deterministic_tree_path_difference_quiz(
    review_context: dict,
    target_bridge: str,
    *,
    level: str,
    previous_quiz: dict | None = None,
) -> dict:
    focus = "tree_path_difference"
    if level == "main":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "P3128 里有很多条树上路径都要给经过的点加一，为什么更该先想“端点/LCA 打标记 + DFS 汇总”，而不是每条路径逐点走一遍？",
            "options": [
                {"value": "A", "label": "一条路径的贡献可以先压成 s、t、LCA 和 LCA 父亲附近的差分标记，最后 DFS 汇总出每个点的经过次数"},
                {"value": "B", "label": "因为树剖这个名字更高级，所以不需要解释路径贡献怎么被记录"},
                {"value": "C", "label": "每条路径都沿着边逐点加一也一样稳，只是代码稍微长一点"},
                {"value": "D", "label": "只要先求出 LCA，所有点的经过次数就会自动出现"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "树剖或 LCA 只是帮你定位路径结构，不能替代“路径贡献怎么被差分记录”这一步。",
                "C": "逐点走每条路径会把很多重复路径段反复更新，K 和 N 大时容易炸。树上差分正是为了省掉这件事。",
                "D": "LCA 只告诉你路径在哪里分叉，不会自动算出每个点被经过多少次，还需要差分标记和 DFS 汇总。",
            },
            "explanation": "这座桥的关键是：多条树上路径不要逐点更新。先把每条路径的贡献压到端点和 LCA 附近的差分标记上，最后一次 DFS 子树汇总，还原每个点的经过次数。",
            "bridge_feedback": "你这一步真正答对的是：树剖/LCA 只是定位路径，真正省事的是端点/LCA 差分标记，再 DFS 汇总。",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                **({"confirm_mode": "structure"} if level == "confirm" else {}),
            },
        }
    if level == "followup":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "只看一条从 s 到 t 的树上路径，差分这一步最该先记住哪句话？",
            "options": [
                {"value": "A", "label": "先在 s、t 加贡献，再在 LCA 和 LCA 的父亲附近抵消，之后靠 DFS 汇总还原路径上点的贡献"},
                {"value": "B", "label": "先把 s 到 t 路径上的每个点都立刻更新一遍，后面就不用汇总了"},
                {"value": "C", "label": "先只给 LCA 加一，因为整条路径的信息都存在 LCA 上"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这又回到逐点更新了。树上差分想省掉的就是每条路径都沿路走一遍。",
                "C": "LCA 是路径的分叉点，不是整条路径贡献的唯一承载点。端点和 LCA 附近都要配合标记。",
            },
            "explanation": "第二轮只缩到一条路径：端点先加，LCA 附近抵消，最后 DFS 汇总。这样路径贡献才会在汇总时刚好落回路径上的点。",
            "bridge_feedback": f"你这一步真正要站稳的是：{target_bridge or '一条路径先端点/LCA 标记，最后 DFS 汇总还原经过次数。'}",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            },
        }
    if level == "final_micro_confirm":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "多条树上路径统计经过次数时，是不是先把每条路径压成端点/LCA 附近的差分标记，再 DFS 汇总？",
            "options": [
                {"value": "A", "label": "是"},
                {"value": "B", "label": "不是"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "最后这题只确认一个最小事实：树上差分不是逐点走路径，而是先少数点打标记，最后 DFS 汇总还原贡献。",
            },
            "explanation": "最后这题只确认一个小事实：端点/LCA 附近打标记，DFS 汇总还原经过次数。",
            "bridge_feedback": "你最后要站稳的就是：路径贡献先差分标记，最后 DFS 汇总。",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
            },
        }
    return {
        "mode": "quiz",
        "quiz_type": "choice",
        "question_text": "如果只盯住树上差分这一小步，下面哪种理解更稳？",
        "options": [
            {"value": "A", "label": "路径贡献先变成端点/LCA 附近的差分标记，最后 DFS 汇总"},
            {"value": "B", "label": "先逐点走完每条路径，差分只是最后装饰一下"},
            {"value": "C", "label": "只求 LCA 就够了，不需要端点标记和汇总"},
        ],
        "correct_answer": "A",
        "distractor_feedback": {
            "B": "这把树上差分的核心省事点丢掉了。它不是逐点更新后的装饰，而是替代逐点更新的记录方式。",
            "C": "LCA 只负责定位路径分叉点，贡献还要靠端点/LCA 标记和 DFS 汇总还原。",
        },
        "explanation": "树上差分这一步要站稳：先少数点打标记，最后一次汇总还原路径贡献。",
        "bridge_feedback": "你这一步真正答对的是：先差分标记，再 DFS 汇总。",
        "target_bridge": target_bridge,
        "difficulty_level": level,
        "meta": {
            "difficulty_level": level,
            "focus": focus,
            "algorithm_category": _infer_algorithm_category(review_context, focus),
            **({"confirm_mode": "structure"} if level == "confirm" else {}),
        },
    }


def _looks_like_process_advice_quiz(payload: dict | None, focus: str) -> bool:
    if not payload or payload.get("mode") != "quiz":
        return False
    if focus not in STRUCTURAL_QUIZ_FOCI:
        return False
    if _payload_answer_type(payload) == "learning_advice":
        return True
    question_text = str(payload.get("question_text", "")).strip()
    process_patterns = (
        "更该先",
        "是不是先要",
        "先做什么",
        "先确定什么",
        "先看清哪件事",
        "先补哪一小步",
    )
    if any(pattern in question_text for pattern in process_patterns):
        return True
    options = payload.get("options") or []
    labels = []
    for option in options:
        if isinstance(option, dict):
            labels.append(str(option.get("label", "")).strip())
        else:
            labels.append(str(option).strip())
    if not labels:
        return False
    starts_with_process = sum(1 for label in labels if label.startswith("先"))
    structural_markers = (
        "dp[",
        "check(",
        "状态",
        "转移",
        "定义",
        "顺序",
        "条件",
        "表示",
    )
    has_structural_marker = any(any(marker in label for marker in structural_markers) for label in labels)
    return starts_with_process >= 2 and not has_structural_marker


def _is_learning_advice_text(text: str) -> bool:
    candidate = (text or "").strip()
    if not candidate:
        return False

    advice_prefixes = (
        "先",
        "应该先",
        "更该先",
        "是不是先",
    )
    advice_phrases = (
        "先分析再动手",
        "先确定状态含义",
        "先写清对象关系",
        "先统一约束再建图",
        "先猜像哪类题",
        "先把实现顺序定下来",
        "更像正确的第一步",
        "哪种理由更合理",
        "最能支持该先考虑这个方法",
        "先把题目里的限制关系统一写成同一种形式",
        "最值得先查",
        "最值得先检查",
    )
    structural_markers = (
        "dp[",
        "check(",
        "d[",
        "fa[",
        "size[",
        "从短区间到长区间",
        "倒序枚举",
        "表示",
        "定义",
        "条件",
        "顺序",
        "维护",
        "距离",
        "代价",
        "价值",
        "边权",
        "点表示",
        "边表示",
    )
    if any(marker in candidate for marker in structural_markers):
        return False
    if any(phrase in candidate for phrase in advice_phrases):
        return True
    return any(candidate.startswith(prefix) for prefix in advice_prefixes)


def _payload_answer_type(payload: dict) -> str:
    answer_type = str(payload.get("answer_type", "")).strip()
    if answer_type in {"structural_fact", "learning_advice"}:
        return answer_type
    return "learning_advice" if _is_learning_advice_text(str(payload.get("correct_answer", ""))) else "structural_fact"


def _deterministic_structural_quiz(
    review_context: dict,
    focus: str,
    target_bridge: str,
    *,
    level: str,
    previous_quiz: dict | None = None,
) -> dict | None:
    if focus == "tree_path_difference":
        return _deterministic_tree_path_difference_quiz(
            review_context,
            target_bridge,
            level=level,
            previous_quiz=previous_quiz,
        )

    if focus == "state_design":
        axis, meaning = _state_axis_label(review_context)
        if level == "main":
            slot_label = _state_slot_label(review_context)
            if axis == "这一维" and slot_label not in {"这一格", "这格", "这个状态格"}:
                slot_phrase = f"{slot_label} 这一格"
                return {
                    "mode": "quiz",
                    "quiz_type": "choice",
                    "question_text": f"如果先把{slot_phrase}的含义定清楚，下面哪种解释更合理？",
                    "options": [
                        {"value": "A", "label": "它表示这个状态本身对应的子问题结果"},
                        {"value": "B", "label": "它表示整道题最后答案应该直接写在哪"},
                        {"value": "C", "label": "它表示转移时顺手算出来的临时中间值"},
                        {"value": "D", "label": "它表示代码外层循环已经写到第几轮"},
                    ],
                    "correct_answer": "A",
                    "distractor_feedback": {
                        "B": f"这个理解把{slot_phrase}当成了整题答案位置，但状态格先要站稳的是：这个状态自己对应的结果是什么。",
                        "C": f"这个理解把{slot_phrase}当成了临时草稿位。状态格里先存的是要被反复复用的子问题结果，不是顺手算出来的临时值。",
                        "D": f"这个理解把{slot_phrase}当成了代码书写顺序。状态格描述的是题目结构里的一个状态，不是程序写到第几轮。",
                    },
                    "explanation": f"这里先要站稳的是：{slot_phrase}到底记录什么。只有先把这格的含义定清楚，后面的转移才不会乱。",
                    "bridge_feedback": f"你这一步真正答对的是：先把{slot_phrase}的状态含义定清楚，而不是先去猜答案位置、临时值或代码顺序。",
                    "target_bridge": target_bridge,
                    "difficulty_level": level,
                    "meta": {
                        "difficulty_level": level,
                        "focus": focus,
                        "algorithm_category": _infer_algorithm_category(review_context, focus),
                    },
                }
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": f"如果状态里要放“{axis}”这一维，下面哪种解释更合理？",
                "options": [
                    {"value": "A", "label": f"它表示{meaning}"},
                    {"value": "B", "label": "它表示最后答案应该写在哪一格"},
                    {"value": "C", "label": "它表示转移时临时算出来的中间值"},
                    {"value": "D", "label": "它表示代码外层循环写到第几轮"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": f"这个理解把“{axis}”这一维当成了答案位置，而不是状态里真正要记录的阶段信息，后面的状态和转移都会跟着跑偏。",
                    "C": f"这个理解把“{axis}”这一维当成了临时计算量，但状态维度记录的应该是长期要保留的含义，不是顺手算出来的中间值。",
                    "D": f"这个理解把“{axis}”这一维误当成代码写法顺序，维度描述的是题目结构里的阶段信息，不是程序写到第几层循环。",
                },
                "explanation": f"这里先要站稳的是：状态里“{axis}”这一维到底记录什么。只有先把这一维定义清楚，后面的转移才不会乱。",
                "bridge_feedback": f"你这一步真正答对的是：先把状态里“{axis}”这一维的含义定清楚，而不是先去猜转移或代码写法。这正是你原题当前卡住的地方。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                    **({"confirm_mode": "structure"} if level == "confirm" else {}),
                },
            }
        if level == "followup":
            slot_label = _state_slot_label(review_context)
            slot_phrase = f"{slot_label} 这一格" if slot_label not in {"这一格", "这格", "这个状态格"} else "这一格状态"
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": f"如果只看{slot_phrase}，它更像在记录下面哪一件事？",
                "options": [
                    {"value": "A", "label": "这个状态本身对应的子问题结果"},
                    {"value": "B", "label": "整道题最后答案应该写在哪"},
                    {"value": "C", "label": "下一步该往哪个方向转移"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": f"这个理解把{slot_phrase}当成了最终答案格，但状态格先存的是“站在这个状态上能得到什么结果”，不是整题答案直接写哪。",
                    "C": f"这个理解把{slot_phrase}当成了动作提示卡。转移方向是后面根据状态去决定的，不是这格本身记录的内容。",
                },
                "explanation": f"先把{slot_phrase}看成“这个状态自己的结果格”，不要把它和整题答案位置、下一步转移方向混在一起。",
                "bridge_feedback": f"你这一步真正要站稳的是：{slot_phrase}先记录这个状态本身对应的子问题结果。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "final_micro_confirm":
            slot_label = _state_slot_label(review_context)
            slot_phrase = f"{slot_label} 这一格" if slot_label not in {"这一格", "这格", "这个状态格"} else "这一格状态"
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": f"如果只看{slot_phrase}，它是不是在记录这个状态本身对应的子问题结果？",
                "options": [
                    {"value": "A", "label": "是"},
                    {"value": "B", "label": "不是"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": f"{slot_phrase}先存的是“这个状态自己能得到什么结果”。如果连这一点都没站稳，后面就会把状态格、整题答案和转移动作混在一起。",
                },
                "explanation": f"最后这题只确认一个最小事实：{slot_phrase}存的是这个状态本身对应的子问题结果，不是最终答案位置，也不是转移模板。",
                "bridge_feedback": f"你最后要站稳的就是：{target_bridge or f'先说清 {slot_phrase} 到底记录什么。'}",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": f"如果只盯住状态里“{axis}”这一维，下面哪种说法才真正把它讲清了？",
            "options": [
                {"value": "A", "label": f"它表示{meaning}"},
                {"value": "B", "label": "它表示当前要写哪一条转移式"},
                {"value": "C", "label": "它表示外层循环已经写到第几轮"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": f"这个说法把“{axis}”这一维和后面的转移写法混在了一起。状态维度先要记录题目结构里的阶段信息，不是先去代替转移式。",
                "C": f"这个说法把“{axis}”这一维误当成代码循环顺序。状态维度描述的是题目里的阶段含义，不是程序写到第几轮。",
            },
            "explanation": f"这一步的关键是先把“{axis}”这一维到底记录什么说清楚，不要把状态含义和转移或代码顺序混在一起。",
            "bridge_feedback": f"你这一步真正答对的是：先把状态里“{axis}”这一维的意思说清楚。这正是你原题里需要先站稳的地方。",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                **({"confirm_mode": "structure"} if level == "confirm" else {}),
            },
        }

    if focus == "left_bound_update":
        if level == "main":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果目标是找最左边那个等于 x 的位置，`a[mid] == x` 时下面哪种处理更稳？",
                "options": [
                    {"value": "A", "label": "先保留 mid 这个候选，再继续往左缩"},
                    {"value": "B", "label": "直接把 mid 丢掉，只看它右边"},
                    {"value": "C", "label": "一相等就立刻停，不用再看前面"},
                    {"value": "D", "label": "先把左边界跳到 mid+1，答案后面再修"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "目标是找最左位置时，mid 可能就是答案，不能一相等就先把它丢掉。",
                    "C": "一相等就停，只能保证找到一个等于 x 的位置，不能保证它已经是最左那个。",
                    "D": "这会把 mid 直接越过去。既然要找最左位置，看到相等时就更不能先把 mid 丢掉。",
                },
                "explanation": "这里先要站稳的是：目标既然是最左位置，`a[mid] == x` 时 mid 仍然可能就是答案，所以要先保留它，再继续往左缩。",
                "bridge_feedback": "你这一步真正答对的是：看到相等时先保留 mid，再继续往左找。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "followup":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果 `a[mid] == x`，当前这一步更该先做什么？",
                "options": [
                    {"value": "A", "label": "先保留 mid，再继续往左找更早的位置"},
                    {"value": "B", "label": "先把 mid 丢掉，只看右半边"},
                    {"value": "C", "label": "直接返回 mid，不用再确认前面"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "你现在找的是最左位置，mid 可能就是答案，不能先把它丢掉。",
                    "C": "直接返回只能保证找到了一个位置，不能保证它已经是最左那个。",
                },
                "explanation": "先把这一小步站稳：`a[mid] == x` 时 mid 还是候选，所以要先保留 mid，再继续往左找。",
                "bridge_feedback": "你这一步真正要站稳的是：相等时先保留 mid，再继续往左缩。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "final_micro_confirm":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果 `a[mid] == x`，是不是还要保留 mid，再继续往左找更早的位置？",
                "options": [{"value": "A", "label": "是"}, {"value": "B", "label": "不是"}],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "最后这题只确认一个最小事实：找最左位置时，mid 一相等也不能先丢。",
                },
                "explanation": "最后这题只确认一个最小事实：目标是最左位置时，看到相等要先保留 mid。",
                "bridge_feedback": "你最后要站稳的就是：相等时先保留 mid，再继续往左找。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        return None

    if focus == "lazy_semantics":
        if level == "main":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果一个线段树节点上挂着 lazy 标记，下面哪种理解更合理？",
                "options": [
                    {"value": "A", "label": "这段区间还有一份已经确定、但还没下传给孩子的信息"},
                    {"value": "B", "label": "这段代码还没执行完，先记个名字提醒自己"},
                    {"value": "C", "label": "这个节点以后不用再维护 sum 了"},
                    {"value": "D", "label": "这个节点已经把所有孩子都更新好了"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "lazy 不是代码执行进度条，它记录的是区间信息还没下传到孩子。",
                    "C": "sum 仍然要维护。lazy 只是把“还没下传的信息”先挂在当前节点上。",
                    "D": "如果都已经下传好了，就不需要继续挂着 lazy 了。",
                },
                "explanation": "这里先要站稳的是：lazy 记录的是“这段区间还有一份已经确定、但还没下传给孩子的信息”，不是代码还没执行完。",
                "bridge_feedback": "你这一步真正答对的是：lazy 记录的是还没下传的信息，不是执行进度。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "followup":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果只盯住 lazy 这一小步，它更像在记录下面哪类东西？",
                "options": [
                    {"value": "A", "label": "当前区间已经确定、但还没下传给孩子的信息"},
                    {"value": "B", "label": "当前函数还没跑完的代码步骤"},
                    {"value": "C", "label": "整棵树最后的最终答案"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "lazy 不是代码流程提示，它对应的是区间信息暂时还挂在父节点上。",
                    "C": "最终答案不会直接塞进 lazy。lazy 只负责记录还没下传的信息。",
                },
                "explanation": "先把这一小步站稳：lazy 记录的是“区间信息还没下传给孩子”，不是代码执行状态。",
                "bridge_feedback": "你这一步真正要站稳的是：lazy 存的是还没下传的信息。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "final_micro_confirm":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "lazy 标记是不是在记录还没下传的信息，不是还没执行完的代码？",
                "options": [{"value": "A", "label": "是"}, {"value": "B", "label": "不是"}],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "最后这题只确认一个最小事实：lazy 记录的是信息还没下传，不是代码没跑完。",
                },
                "explanation": "最后这题只确认一个最小事实：lazy 先表示“信息还没下传给孩子”。",
                "bridge_feedback": "你最后要站稳的就是：lazy 记录的是还没下传的信息。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        return None

    if focus == "check_condition":
        if level == "main":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果这题要写 check(mid)，下面哪种理解更合理？",
                "options": [
                    {"value": "A", "label": "check(mid) 用来判断答案取到 mid 时条件是否仍然成立"},
                    {"value": "B", "label": "check(mid) 用来直接算出最终最优答案"},
                    {"value": "C", "label": "check(mid) 主要是把二分模板补完整，不用单独想"},
                    {"value": "D", "label": "check(mid) 用来顺手更新答案，判不判都无所谓"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "这个理解把 check 当成了“直接求答案”的函数，但 check 真正做的是可行性判断：当前 mid 行不行，而不是直接把最优值算出来。",
                    "C": "这个理解把 check 当成模板附属品了。实际上 check 是整道题的核心判断器，必须先说清它在验证什么，二分才不会空转。",
                    "D": "这个理解把“判是否可行”和“更新最终答案”混在了一起。check 负责判断 mid 是否成立，不是顺手去改最终答案。",
                },
                "explanation": "这一步最关键的是把 check 的职责说清楚：它判断的是“当前 mid 是否可行”，不是直接去算最终答案。",
                "bridge_feedback": "你这一步真正答对的是：先把 check 在验证什么说清楚，而不是先背二分模板。这正是原题当前卡住的桥。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                    **({"confirm_mode": "structure"} if level == "confirm" else {}),
                },
            }
        if level == "followup":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果只盯住 `check(mid)` 这一小步，`check(mid)` 返回 true 时更贴近下面哪种说法？",
                "options": [
                    {"value": "A", "label": "说明当前 mid 可行"},
                    {"value": "B", "label": "说明最终最优答案已经直接被算出来了"},
                    {"value": "C", "label": "说明二分一定该往更大的方向走，不用再看条件"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "返回 true 只是在说“这个 mid 行得通”，不是已经把最终最优答案直接算出来了。",
                    "C": "返回 true 先说明的是“当前 mid 可行”。至于区间怎么缩，还要看你这题是在找最大可行、最小可行还是别的边界。",
                },
                "explanation": "先把这一小步站稳：`check(mid)` 返回 true，表示当前这个 mid 满足条件、是可行的，不是已经把最终答案直接算出来。",
                "bridge_feedback": "你这一步真正要站稳的是：返回 true 先表示“当前 mid 可行”，别把它和最终答案、二分方向直接绑死。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "final_micro_confirm":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果 `check(mid)` 返回 true，它是不是只说明当前这个 mid 可行？",
                "options": [
                    {"value": "A", "label": "是"},
                    {"value": "B", "label": "不是"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "这一步最后只确认一个最小事实：返回 true 先说明“当前这个 mid 可行”。它还没有直接替你把最终答案或二分方向全部定死。",
                },
                "explanation": "最后这题只确认一个最小事实：`check(mid)` 返回 true，先表示当前这个 mid 可行。",
                "bridge_feedback": "你最后要站稳的就是：返回 true 先表示“当前 mid 可行”。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果只盯住 `check(mid)` 这一小步，下面哪种说法才是对的？",
            "options": [
                {"value": "A", "label": "`check(mid)` 用来判断当前 `mid` 是否可行"},
                {"value": "B", "label": "`check(mid)` 用来直接算出最终最优答案"},
                {"value": "C", "label": "`check(mid)` 只是模板里补齐代码的步骤，不需要单独想"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这个说法把 `check` 当成了直接求最优值的函数。可 `check(mid)` 真正负责的是判断“这个 mid 行不行”，不是直接把答案算出来。",
                "C": "这个说法把 `check` 当成了模板附属品。实际上它是整道题的判断核心，必须先说清它在验证什么，二分才不会空转。",
            },
            "explanation": "先把 `check(mid)` 的职责说清楚：它判断的是当前 `mid` 是否可行，而不是直接去求最终答案。",
            "bridge_feedback": "你这一步真正答对的是：`check` 先判“可不可行”，不是先去求答案。这正是你原题里需要先站稳的桥。",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                **({"confirm_mode": "structure"} if level == "confirm" else {}),
            },
        }

    if focus == "enumeration_order":
        if level == "main":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果当前状态要用到前面已经算好的状态，下面哪种顺序理解更合理？",
                "options": [
                    {"value": "A", "label": "先让被依赖的状态准备好，再去算当前状态"},
                    {"value": "B", "label": "先按代码最好写的顺序枚举，不对再改"},
                    {"value": "C", "label": "先把答案变量定下来，顺序后面再说"},
                    {"value": "D", "label": "先让样例大致能跑，再回头改顺序"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "这个理解把“代码顺手”放在了“依赖先后”前面。枚举顺序首先要服从状态依赖，不是先按手感写代码。",
                    "C": "这个理解把注意力放到了答案变量上，但当前这一步真正影响对错的是：被依赖的状态有没有先准备好。",
                    "D": "这个理解把顺序问题当成了后面再调的小事。可一旦依赖方向反了，样例能过也只是碰巧，不代表逻辑是对的。",
                },
                "explanation": "枚举顺序首先要服从状态依赖。谁被依赖，谁就要先准备好，不能先按代码顺手去写。",
                "bridge_feedback": "你这一步真正答对的是：先按依赖顺序安排谁在前谁在后，而不是先按手感写循环。这正是原题里最容易反的地方。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                    **({"confirm_mode": "structure"} if level == "confirm" else {}),
                },
            }
        if level == "followup":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果当前这一格要用到前一个已经算好的状态，下面哪种顺序更稳？",
                "options": [
                    {"value": "A", "label": "先把前一个状态算好，再来更新当前这一格"},
                    {"value": "B", "label": "先算当前这一格，不够再回头补前一个状态"},
                    {"value": "C", "label": "先按代码顺手的方向写循环，顺序后面再调"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "如果当前这一格要用前一个状态的结果，那前一个状态就不能晚到。顺序一反，当前这一格拿到的就不是已经准备好的依赖。",
                    "C": "这里先服从的是依赖先后，不是代码顺不顺手。先把前一个状态准备好，当前这一格才有东西可用。",
                },
                "explanation": "先把这一小步站稳：如果当前这一格要用前一个已经算好的状态，就要先把前一个状态准备好，再来更新当前这一格。",
                "bridge_feedback": "你这一步真正要站稳的是：谁被依赖，谁就要先算好。别把依赖顺序让给代码书写顺序。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "final_micro_confirm":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果当前这一格要用前一个状态的结果，是不是要先把前一个状态算好？",
                "options": [
                    {"value": "A", "label": "是"},
                    {"value": "B", "label": "不是"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "最后这题只确认一个最小事实：既然当前这一格要用前一个状态的结果，那前一个状态就得先准备好，不能等到后面再补。",
                },
                "explanation": "最后这题只确认一个最小事实：依赖谁，就先把谁算好，再来更新当前这一格。",
                "bridge_feedback": "你最后要站稳的就是：先把被依赖的前一个状态算好。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果当前状态要依赖前面的状态，下面哪种顺序理解才是对的？",
            "options": [
                {"value": "A", "label": "先把被依赖的状态算好，再去更新当前状态"},
                {"value": "B", "label": "先按代码顺手的顺序写循环，不对再改"},
                {"value": "C", "label": "先让样例大致能跑，顺序后面再调"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这个说法把“代码顺手”放在了“依赖先后”前面。枚举顺序首先要服从状态依赖，不是先按手感写代码。",
                "C": "这个说法把顺序问题当成后面再调的小事。可一旦依赖方向反了，样例能过也只是碰巧，不代表逻辑真的对。",
            },
            "explanation": "顺序问题本质上是依赖问题。先把被依赖的状态准备好，当前状态才有东西可用。",
            "bridge_feedback": "你这一步真正答对的是：枚举顺序要跟着依赖关系走，而不是跟着写代码的习惯走。",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                **({"confirm_mode": "structure"} if level == "confirm" else {}),
            },
        }

    if focus == "transition_design":
        if level == "main":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果在想“当前状态怎么转过来”，下面哪种理解更完整？",
                "options": [
                    {"value": "A", "label": "要从所有合法的前一状态去想，不能只盯一种最显眼的来源"},
                    {"value": "B", "label": "先写一种最顺手的转移，其他情况后面再补"},
                    {"value": "C", "label": "先把循环顺序写完，转移自然就会对"},
                    {"value": "D", "label": "当前状态直接等于当前这一项，不用再看前面"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "这个理解最容易漏掉一类合法来源。转移设计最怕的不是不会写，而是只盯着一种最显眼的情况，其他分支被漏掉了。",
                    "C": "这个理解把“顺序”当成了“转移”的替代品。循环顺序当然重要，但它不能替你补齐转移里漏掉的情况。",
                    "D": "这个理解把状态之间的连接关系切断了。当前状态如果完全不看前面，就不是在做转移，而是在凭当前这一项硬定答案。",
                },
                "explanation": "转移设计最关键的是先把“有哪些合法来源”想全。只要漏掉一种情况，后面的式子和代码都会跟着错。",
                "bridge_feedback": "你这一步真正答对的是：转移要先看来源是否想全，而不是先凭感觉写一条最顺手的式子。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                    **({"confirm_mode": "structure"} if level == "confirm" else {}),
                },
            }
        if level == "followup":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果当前状态可能有两类合法来源，下面哪种做法更稳？",
                "options": [
                    {"value": "A", "label": "先把这两类合法来源想全，再决定怎么转过来"},
                    {"value": "B", "label": "先写最顺手的那一类来源，另一类后面再补"},
                    {"value": "C", "label": "先把循环顺序定死，来源是否想全后面再说"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "这还是在凭手感只抓最显眼的一支来源。只要另一类合法来源没站稳，转移就会天然缺一块。",
                    "C": "循环顺序当然重要，但它不能代替你把合法来源想全。来源没站稳时，顺序再整齐也只是带着漏项往前跑。",
                },
                "explanation": "先把这一小步站稳：如果当前状态可能有两类合法来源，就先把这两类来源想全，再写具体怎么转过来。",
                "bridge_feedback": "你这一步真正要站稳的是：先把合法来源想全，再谈具体转移。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "final_micro_confirm":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果当前状态可能有两类合法来源，是不是要先把这两类合法来源想全？",
                "options": [
                    {"value": "A", "label": "是"},
                    {"value": "B", "label": "不是"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "最后这题只确认一个最小事实：只要当前状态可能有多类合法来源，就要先把这些来源想全，不能只抓最顺手的一支。",
                },
                "explanation": "最后这题只确认一个最小事实：先把合法来源想全，再写具体转移。",
                "bridge_feedback": "你最后要站稳的就是：先把当前状态的合法来源想全。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果只盯住转移这一小步，下面哪种理解才是对的？",
            "options": [
                {"value": "A", "label": "先检查所有合法来源有没有想全，再写具体转移"},
                {"value": "B", "label": "先写一条最顺手的转移，漏掉的情况后面再补"},
                {"value": "C", "label": "先把循环顺序写完，转移自然会对"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这个说法最容易漏掉一类合法来源。转移设计最怕的不是不会写，而是只盯着一种最显眼的情况，其他分支被漏掉了。",
                "C": "这个说法把“顺序”当成了“转移”的替代品。循环顺序当然重要，但它不能替你补齐转移里漏掉的情况。",
            },
            "explanation": "很多转移错误不是方向反了，而是少想了一支情况。先检查来源是否想全，转移才站得住。",
            "bridge_feedback": "你这一步真正答对的是：先补齐所有合法来源，再去写具体转移。",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                **({"confirm_mode": "structure"} if level == "confirm" else {}),
            },
        }

    if focus == "tree_diameter_candidates":
        if level == "main":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果加上一条新边后，新的最长路更该先从下面哪几类候选里去想？",
                "options": [
                    {"value": "A", "label": "左边内部、右边内部、经过新边这三类候选"},
                    {"value": "B", "label": "只要看新边两端的两个点就够了，原来的最长路不用再管"},
                    {"value": "C", "label": "只要重新从任意点随便跑一遍，候选种类不用区分"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "原来左右两边内部的最长路并不会因为加了一条新边就自动消失，所以不能只盯着新边两端。",
                    "C": "这会跳过“候选从哪里来”这一步。先把候选分清楚，后面才知道该比较哪几种情况。",
                },
                "explanation": "这一步最关键的是先把候选想全：新最长路不只可能经过新边，也可能仍然留在左边内部或右边内部。",
                "bridge_feedback": "你这一步真正答对的是：先把新最长路的候选来源想全，再去比较哪一个最大。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                    **({"confirm_mode": "structure"} if level == "confirm" else {}),
                },
            }
        if level == "followup":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果最长路经过新边，两端更该接到什么样的点？",
                "options": [
                    {"value": "A", "label": "连接点两侧各自离连接点最远的点"},
                    {"value": "B", "label": "连接点两侧随便挑一个点就行"},
                    {"value": "C", "label": "只看左边最远点，右边接哪个点无所谓"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "如果想让经过新边的路径尽量长，两边都要往远点接，不能随便挑一个点。",
                    "C": "经过新边的这类候选要把左右两边都想全，不是只把一边拉长。",
                },
                "explanation": "先把这一小步站稳：如果最长路经过新边，两边都该尽量往各自离连接点最远的点去接。",
                "bridge_feedback": "你这一步真正要站稳的是：经过新边时，两边都要接各自最远的点。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "final_micro_confirm":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果最长路经过新边，是不是要让两端都尽量接到各自最远的点？",
                "options": [
                    {"value": "A", "label": "是"},
                    {"value": "B", "label": "不是"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "最后这题只确认一个最小事实：经过新边的候选如果想尽量长，两边都要往各自更远的点去接。",
                },
                "explanation": "最后这题只确认一个最小事实：经过新边时，两边都该往各自最远的点接，才能形成这类候选里的最长路径。",
                "bridge_feedback": "你最后要站稳的就是：经过新边时，两边都要接各自最远的点。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果只盯住新边这一小步，下面哪种说法才是对的？",
            "options": [
                {"value": "A", "label": "经过新边时，两边都要往各自最远的点去接"},
                {"value": "B", "label": "经过新边时，只看其中一边最远就够了"},
                {"value": "C", "label": "经过新边时，接到哪个点都差不多"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这会漏掉另一边对路径长度的贡献。经过新边的候选要把左右两边一起想。",
                "C": "这还是把“最长路”当成随便接点。要让路径最长，两边都要尽量往远点接。",
            },
            "explanation": "如果最长路经过新边，关键不是随便接，而是让左右两边都尽量拉长。",
            "bridge_feedback": "你这一步真正答对的是：经过新边时，两边都要接各自更远的点。",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                **({"confirm_mode": "structure"} if level == "confirm" else {}),
            },
        }

    if focus == "greedy_basis":
        if level == "main":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果当前要先选一个对象，下面哪种理由更能支撑这一步？",
                "options": [
                    {"value": "A", "label": "先选它，是因为这样更不容易破坏后面的结构或可选空间"},
                    {"value": "B", "label": "先选它，是因为它看起来最大、最顺手、最好写"},
                    {"value": "C", "label": "先选它，是因为贪心题通常都先处理当前这个对象"},
                    {"value": "D", "label": "先选它，后面如果不对再回头改顺序"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "这还是在靠手感挑对象，不是在回答“为什么先选它不会把后面的结构破坏掉”。",
                    "C": "贪心不是靠题感口号成立的。先选当前对象，必须有当前题里的局部理由支撑。",
                    "D": "贪心依据不是后面再调的装饰。如果当前这一步的优先理由没站稳，后面的选择链就会一直漂。",
                },
                "explanation": "贪心依据最关键的不是“看起来顺手”，而是这一步先选它，为什么不会破坏后面的结构或可选空间。",
                "bridge_feedback": "你这一步真正答对的是：先讲清当前对象为什么可以优先，而不是只靠题感或手感。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                    **({"confirm_mode": "structure"} if level == "confirm" else {}),
                },
            }
        if level == "followup":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果当前这个对象更优先，下面哪种理由更稳？",
                "options": [
                    {"value": "A", "label": "先选它，能给后面留下更稳的空间或结构"},
                    {"value": "B", "label": "先选它，只是因为它当前数值更大、更顺手"},
                    {"value": "C", "label": "先选它，因为贪心题一般都会这么做"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "局部更大或更顺手，不等于局部决策更安全。这里先要站稳的是：它能不能保住后面的空间或结构。",
                    "C": "这还是在背方法口号，不是在回答“为什么当前这个对象现在就该优先”。",
                },
                "explanation": "先把这一小步站稳：当前对象之所以优先，不是因为顺手，而是因为它能给后面留下更稳的空间或结构。",
                "bridge_feedback": "你这一步真正要站稳的是：当前这个对象优先，是因为它保住了后面的空间或结构。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        if level == "final_micro_confirm":
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果优先选当前这个对象，是不是要先说明它不会破坏后面的结构？",
                "options": [
                    {"value": "A", "label": "是"},
                    {"value": "B", "label": "不是"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "最后这题只确认一个最小事实：当前对象之所以能先选，得先说清它不会把后面的结构或可选空间破坏掉。",
                },
                "explanation": "最后这题只确认一个最小事实：先选当前对象，要先有“不会破坏后面的结构”这个理由。",
                "bridge_feedback": "你最后要站稳的就是：当前对象优先，先要说明它不会破坏后面的结构。",
                "target_bridge": target_bridge,
                "difficulty_level": level,
                "meta": {
                    "difficulty_level": level,
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                },
            }
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果只盯住“先选谁”这一小步，下面哪种说法才是对的？",
            "options": [
                {"value": "A", "label": "先选它，要先说清为什么这样不会破坏后面的结构"},
                {"value": "B", "label": "先选它，只要看起来最大最顺手就行"},
                {"value": "C", "label": "先选它，因为贪心题通常都这么做"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这个说法还是只看当前手感，没有回答“为什么这一步先选它是安全的”。",
                "C": "这个说法是在背模板口号，不是在给出当前题里的局部理由。",
            },
            "explanation": "先选谁这一步，最重要的不是熟悉感，而是要先说清：为什么先选它不会把后面的结构弄坏。",
            "bridge_feedback": "你这一步真正答对的是：先给出局部优先的理由，再决定当前对象能不能先选。",
            "target_bridge": target_bridge,
            "difficulty_level": level,
            "meta": {
                "difficulty_level": level,
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                **({"confirm_mode": "structure"} if level == "confirm" else {}),
            },
        }

    return None


def _deterministic_local_followup_quiz(
    review_context: dict,
    focus: str,
    target_bridge: str,
    previous_quiz: dict | None = None,
) -> dict | None:
    text = " ".join(
        str(part or "")
        for part in (
            review_context.get("problem_title"),
            review_context.get("problem_context"),
            review_context.get("bottleneck_text"),
            review_context.get("key_bridge"),
            review_context.get("next_step"),
            (previous_quiz or {}).get("question_text", ""),
        )
    )
    if focus == "complexity_fit":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果 M 和 N 都可能很大，当前这一步更该先确认哪件事？",
            "options": [
                {"value": "A", "label": "先估 M×N 这类总量级会不会先炸，再判断当前做法能不能过"},
                {"value": "B", "label": "先假设机器跑得够快，写完再看会不会超时"},
                {"value": "C", "label": "先背一个更高级的方法名，规模能不能过以后再说"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这会把最关键的总量级判断留到最后碰运气。先估 M×N 这类总量级会不会炸，才知道当前做法要不要继续。",
                "C": "方法名不能替代规模判断。你先得知道 M×N 这类总量级会不会先炸，才能决定是否真的需要换方法。",
            },
            "explanation": "第二轮不再问整题该用什么方法，而是只盯住一个更小的局部动作：先把 M×N 这类总量级估出来，再看当前做法能不能过。",
            "bridge_feedback": f"你这一步真正要站稳的是：{target_bridge or '先把总量级估出来，再判断当前复杂度能不能过。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "followup",
            "meta": {
                "difficulty_level": "followup",
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "followup_mode": "local_scale_check",
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            },
        }

    if focus == "shared_prefix_merging":
        explanation = "第二轮不再重复整题复杂度，而是只盯住一个局部机制：查询时到底还会不会把所有消息重新看一遍。只要这一步站稳，为什么 trie 能更快就会清楚很多。"
        bridge_feedback = (
            f"你这一步真正要站稳的是：{target_bridge or 'trie 查询时并不会把所有消息重新逐条拿出来比，而是沿当前前缀往下走。'}"
        )
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果把所有消息先放进 trie，查询一条拦截串时，是重新看所有消息，还是只沿着当前前缀往下走？",
            "options": [
                {"value": "A", "label": "不用，只要沿着这条查询自己的前缀往下走"},
                {"value": "B", "label": "要，还是得把所有消息重新逐条拿出来比"},
                {"value": "C", "label": "只要把长度一样的消息重新看一遍就够了"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这还是把 trie 当成“换个容器后继续逐条比对”。可 trie 真正省下来的，就是不用把所有消息重新拿出来比，而是直接沿当前前缀往下走。",
                "C": "查询时要看的不是“长度一样的消息”，而是当前前缀在树上对应的那条路径。长度相同不等于共享前缀。",
            },
            "explanation": explanation,
            "bridge_feedback": bridge_feedback,
            "target_bridge": target_bridge,
            "difficulty_level": "followup",
            "meta": {
                "difficulty_level": "followup",
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "followup_mode": "local_mechanism",
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            },
        }

    if focus != "method_selection":
        return None

    if _contains_any(text, ("trie", "前缀", "拦截串", "消息")):
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果很多消息有相同开头，这一步更该先圈出哪一个更直接支持 trie 的小信号？",
            "options": [
                {"value": "A", "label": "很多消息有相同开头，说明共享前缀值得先合在一起看"},
                {"value": "B", "label": "只要串长不超过 20，就一定该直接上 trie"},
                {"value": "C", "label": "只是因为以前做过类似题，感觉这题像 trie"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "串长小只是辅助信息，不是这一步最直接的小信号。现在先盯住的是：相同开头值不值得先合起来看。",
                "C": "熟题感觉可以帮你起念头，但它不能替代题面里的这个局部信号：很多消息真的在共享前缀。",
            },
            "explanation": "第二轮把题面信号再缩小半步，不再问整句“为什么该用 trie”，只先确认你有没有看见“很多消息相同开头”这个局部信号。",
            "bridge_feedback": f"你这一步真正要站稳的是：{target_bridge or '先抓题面里真正支持 trie 的结构信号。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "followup",
            "meta": {
                "difficulty_level": "followup",
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "followup_mode": "local_shared_prefix_signal",
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            },
        }

    return {
        "mode": "quiz",
        "quiz_type": "choice",
        "question_text": "如果这一步先不急着报方法名，更该先盯住题面里的哪一类信息？",
        "options": [
            {"value": "A", "label": "题面里真正支持这个方法的结构信号"},
            {"value": "B", "label": "这题像不像以前做过的熟题"},
            {"value": "C", "label": "先把方法步骤背出来，题面信号后面再补"},
        ],
        "correct_answer": "A",
        "distractor_feedback": {
            "B": "熟题联想可以帮你起感觉，但它不能替代当前题面的真实结构信号。方法选对，先要靠题面支持。",
            "C": "先背步骤会让方法和题面脱节。你得先说清题面里哪一个信号在支持当前做法。",
        },
        "explanation": "第二轮不再问整桥“为什么该用这个方法”，而是只缩到一个更小的局部动作：先抓题面里真正支持这个方法的结构信号。",
        "bridge_feedback": f"你这一步真正要站稳的是：{target_bridge or '先抓题面里支持这个方法的结构信号。'}",
        "target_bridge": target_bridge,
        "difficulty_level": "followup",
        "meta": {
            "difficulty_level": "followup",
            "focus": focus,
            "algorithm_category": _infer_algorithm_category(review_context, focus),
            "followup_mode": "local_signal",
            "previous_question": (previous_quiz or {}).get("question_text", ""),
        },
    }


def _parse_quiz_payload(text: str, *, expected_level: str) -> dict | None:
    json_block = _extract_json_block(text)
    if not json_block:
        return None
    try:
        parsed = json.loads(_sanitize_json_like_text(json_block))
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None

    mode = parsed.get("mode", "quiz")
    if mode == "fallback_explain":
        fallback_explain = str(
            parsed.get("fallback_explain", "") or parsed.get("explanation", "")
        ).strip() or "当前这一步更适合先换一种方式讲清楚，而不是继续出确认题。"
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": fallback_explain,
            "explanation": fallback_explain,
            "bridge_feedback": "",
            "distractor_feedback": {},
            "target_bridge": str(parsed.get("target_bridge", "")).strip(),
            "difficulty_level": expected_level,
            "meta": {"difficulty_level": expected_level},
        }

    quiz_type = str(parsed.get("quiz_type", "")).strip()
    if quiz_type not in {"choice", "short_fill"}:
        return None
    question_text = str(parsed.get("question_text", "")).strip()
    correct_answer = str(parsed.get("correct_answer", "")).strip()
    answer_type = str(parsed.get("answer_type", "")).strip()
    explanation = str(parsed.get("explanation", "")).strip()
    bridge_feedback = str(parsed.get("bridge_feedback", "")).strip()
    distractor_feedback = parsed.get("distractor_feedback") if isinstance(parsed.get("distractor_feedback"), dict) else {}
    target_bridge = str(parsed.get("target_bridge", "")).strip()
    meta = parsed.get("meta") if isinstance(parsed.get("meta"), dict) else {}
    options = parsed.get("options")
    if not isinstance(options, list):
        return None
    normalized_options = []
    for idx, option in enumerate(options):
        if isinstance(option, dict):
            value = str(option.get("value", "")).strip()
            label = str(option.get("label", "")).strip()
        else:
            value = chr(ord("A") + idx)
            label = str(option).strip()
        if not value or not label:
            continue
        normalized_options.append({"value": value, "label": label})
    options = normalized_options

    if quiz_type == "choice":
        if len(options) < 2 or len(options) > 4:
            return None
        option_values = {option["value"] for option in options}
        if correct_answer not in option_values:
            matched = next((option["value"] for option in options if option["label"] == correct_answer), "")
            if not matched:
                return None
            correct_answer = matched
    else:
        options = []
        if not correct_answer:
            return None

    if not question_text or not explanation:
        return None
    resolved_answer_type = answer_type if answer_type in {"structural_fact", "learning_advice"} else (
        "learning_advice" if _is_learning_advice_text(correct_answer) else "structural_fact"
    )
    if resolved_answer_type == "learning_advice":
        return None

    valid_option_values = {option["value"] for option in options}
    normalized_feedback = {}
    for option_value, feedback in distractor_feedback.items():
        option_key = str(option_value).strip()
        feedback_text = str(feedback).strip()
        if option_key == correct_answer or option_key not in valid_option_values:
            continue
        if len(feedback_text) < 20:
            return None
        normalized_feedback[option_key] = feedback_text
    distractor_feedback = normalized_feedback

    meta = {
        **meta,
        "difficulty_level": expected_level,
    }

    return {
        "mode": "quiz",
        "quiz_type": quiz_type,
        "question_text": question_text,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "bridge_feedback": bridge_feedback,
        "distractor_feedback": distractor_feedback,
        "target_bridge": target_bridge,
        "difficulty_level": expected_level,
        "meta": {
            **meta,
            "answer_type": resolved_answer_type,
        },
    }


def _generic_distractor_feedback(option_label: str, focus: str, review_context: dict) -> str:
    target_bridge = (review_context.get("key_bridge") or review_context.get("next_step") or "").strip()
    if focus == "state_design":
        return f"这个说法没有真正把状态含义说清，容易把“这一维到底表示什么”和后面的转移写法混在一起。{target_bridge or '先把状态定义站稳，再往后走。'}"
    if focus == "transition_design":
        return f"这个写法更像是在凭感觉补式子，没有先确认转移是不是漏掉了一种情况。{target_bridge or '这一步要先检查转移是否完整。'}"
    if focus == "check_condition":
        return f"这个说法没有抓住 check 真正在判什么，容易把“验证是否可行”和“更新最终答案”混在一起。{target_bridge or '先说清 check 在验证什么。'}"
    if focus == "enumeration_order":
        return f"这个说法没有抓住依赖顺序，容易按代码顺手去写，而不是按状态依赖来定谁先谁后。{target_bridge or '先确定哪一维必须在前。'}"
    if focus == "constraint_modeling":
        return f"这个选项没有先把限制关系写整齐，容易在建边前就把谁限制谁搞反。{target_bridge or '先统一关系，再往下建模。'}"
    if focus == "general_modeling":
        return f"这个选项更像是在先猜题型，没有先把题目里的对象和关系分清楚。{target_bridge or '先把对象和关系写清楚。'}"
    if focus == "greedy_basis":
        return f"这个说法没有真正回答“为什么要先选它”，所以还不够支撑贪心依据。{target_bridge or '先讲清为什么当前对象应该优先。'}"
    if focus == "method_selection":
        return f"这个选项没有抓住题面里的方法信号，还是在凭熟悉感猜方法。{target_bridge or '先找出支持这个方法的题面特征。'}"
    if focus == "boundary_debug":
        return f"这个说法没有先盯最容易破的边界或默认前提，所以还抓不到这类实现 bug 的核心。{target_bridge or '先检查最小边界和默认前提。'}"
    if focus == "data_type":
        return f"这个判断没有真正对照数据范围去看类型是否会溢出，所以还不够稳。{target_bridge or '先按范围判断该开什么类型。'}"
    if focus == "loop_boundary":
        return f"这个写法没有先把循环起点、终点或下标体系说清楚，容易少一位或多一位。{target_bridge or '先定清循环到底从哪到哪。'}"
    if focus == "recursion_structure":
        return f"这个说法没有抓住递归什么时候停、当前这一层表示什么，所以还没把递归结构站稳。{target_bridge or '先写清递归什么时候停和这一层表示什么。'}"
    if focus == "complexity_fit":
        return f"这个判断没有把数据范围和复杂度放在一起看，容易在能不能过这件事上想当然。{target_bridge or '先根据范围判断复杂度能不能过。'}"
    return f"这个选项没有真正抓住当前桥梁里最关键的结构。{target_bridge or '先把这一步最关键的那层结构说清楚。'}"


def _normalize_quiz_contract(payload: dict | None, review_context: dict, focus: str, quiz_role: str) -> dict | None:
    if not payload or payload.get("mode") != "quiz":
        return payload

    options = payload.get("options") or []
    normalized_options = []
    for idx, option in enumerate(options):
        if isinstance(option, dict):
            value = str(option.get("value", "")).strip()
            label = str(option.get("label", "")).strip()
        else:
            value = chr(ord("A") + idx)
            label = str(option).strip()
        if not value or not label:
            continue
        normalized_options.append({"value": value, "label": label})
    payload["options"] = normalized_options

    if payload.get("quiz_type") == "choice":
        option_values = {option["value"] for option in payload["options"]}
        if payload.get("correct_answer") not in option_values:
            matched = next(
                (option["value"] for option in payload["options"] if option["label"] == payload.get("correct_answer")),
                "",
            )
            if matched:
                payload["correct_answer"] = matched

    distractor_feedback = payload.get("distractor_feedback") or {}
    if not isinstance(distractor_feedback, dict):
        distractor_feedback = {}
    normalized_feedback = {}
    for option in payload["options"]:
        option_value = option["value"]
        if option_value == payload.get("correct_answer"):
            continue
        feedback = str(distractor_feedback.get(option_value, "")).strip()
        if len(feedback) < 20:
            feedback = _generic_distractor_feedback(option.get("label", ""), focus, review_context)
        normalized_feedback[option_value] = feedback
    payload["distractor_feedback"] = normalized_feedback

    payload["meta"] = {
        **(payload.get("meta") or {}),
        "difficulty_level": payload.get("difficulty_level", payload.get("meta", {}).get("difficulty_level", "main")),
        "focus": (payload.get("meta") or {}).get("focus") or focus,
        "algorithm_category": (payload.get("meta") or {}).get("algorithm_category") or _infer_algorithm_category(review_context, focus),
    }
    if quiz_role == QUIZ_ROLE_CONFIRM:
        payload["meta"]["confirm_mode"] = payload["meta"].get("confirm_mode", "abstract")
    return payload


def _structural_stage_instruction(level: str) -> str:
    if level == "main":
        return (
            "这是一道 main quiz。优先使用学生原题里的对象、状态名、关系名或变量语境出题，"
            "帮助学生在“自己这道题”的语境里认出正确结构。优先使用 4 选 1 的 choice 题。"
            "不能把原题完整解法、后续问法或超出当前桥梁的内容一起带进选项。"
        )
    if level == "followup":
        return (
            "这是一道 follow-up quiz。仍然优先使用学生原题里的对象和语境，不换成新题型。"
            "它必须比 main 更小、更单步，但不能生成 judgement（对/错）题。"
            "优先生成 2 选 1 或 3 选 1 的结构型 choice 题。"
        )
    return (
        "这是一道 confirm quiz。它的目标不是更简单，而是换一个角度验证学生是否真正理解了同一座桥。"
        "在可行时，优先用一个更小的新情境来验证迁移；如果不适合迁移，再退回原题语境中的结构判断。"
    )


def _generate_structural_quiz(
    review_context: dict,
    focus: str,
    target_bridge: str,
    *,
    level: str,
    previous_quiz: dict | None = None,
) -> dict | None:
    previous_question = (previous_quiz or {}).get("question_text", "")
    previous_correct_answer = (previous_quiz or {}).get("correct_answer", "")
    role_rules = _load_prompt_file(f"snippets/role-{level}.md")
    focus_rules = _load_prompt_file(f"snippets/focus-{focus}.md")
    algorithm_category = _infer_algorithm_category(review_context, focus)
    core_design_subtags = ", ".join(review_context.get("core_design_subtags") or [])
    system_prompt = _render_prompt_template(
        "quiz-content/system.md",
        {
            "role_rules": role_rules,
            "focus_rules": focus_rules,
        },
    )
    user_prompt = _render_prompt_template(
        "quiz-content/user.md",
        {
            "problem_title": review_context.get("problem_title", ""),
            "problem_context": review_context.get("problem_context", ""),
            "bottleneck_text": review_context.get("bottleneck_text", ""),
            "error_layer": review_context.get("error_layer", ""),
            "key_bridge": review_context.get("key_bridge", ""),
            "next_step": review_context.get("next_step", ""),
            "core_design_subtags": core_design_subtags,
            "focus": focus,
            "algorithm_category": algorithm_category,
            "target_bridge": target_bridge,
            "previous_question": previous_question,
            "previous_correct_answer": previous_correct_answer,
            "difficulty_level": level,
        },
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    ok, content, _ = _call_llm(messages)
    if not ok:
        return _deterministic_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level=level,
            previous_quiz=previous_quiz,
        )
    payload = _parse_quiz_payload(content, expected_level=level)
    if not payload:
        return _deterministic_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level=level,
            previous_quiz=previous_quiz,
        )
    if payload["mode"] != "quiz":
        return _deterministic_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level=level,
            previous_quiz=previous_quiz,
        ) or payload
    if _looks_like_process_advice_quiz(payload, focus):
        return _deterministic_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level=level,
            previous_quiz=previous_quiz,
        ) or {
            "mode": "fallback_explain",
            "fallback_explain": "当前这一步更适合先换一种方式讲清楚，而不是继续出流程口号题。",
            "explanation": "当前这一步更适合先换一种方式讲清楚，而不是继续出流程口号题。",
            "difficulty_level": level,
            "meta": {"difficulty_level": level},
        }
    payload["target_bridge"] = payload.get("target_bridge") or target_bridge
    payload["bridge_feedback"] = payload.get("bridge_feedback") or _default_bridge_feedback(payload.get("correct_answer", ""), review_context)
    meta = {
        **payload.get("meta", {}),
        "difficulty_level": level,
        "focus": focus,
        "algorithm_category": payload.get("meta", {}).get("algorithm_category") or algorithm_category,
    }
    if level == "confirm":
        meta["confirm_mode"] = "structure"
    payload["meta"] = meta
    payload["difficulty_level"] = level
    return payload


def _generate_structural_confirm_quiz(review_context: dict, focus: str, target_bridge: str, previous_quiz: dict | None = None) -> dict | None:
    return _generate_structural_quiz(
        review_context,
        focus,
        target_bridge,
        level="confirm",
        previous_quiz=previous_quiz,
    )


def _main_quiz_payload(review_context: dict, focus: str, target_bridge: str) -> dict:
    if focus in {"left_bound_update", "lazy_semantics"}:
        payload = _deterministic_structural_quiz(review_context, focus, target_bridge, level="main")
        if payload:
            return payload

    if focus == "complexity_fit":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果题面里两层规模都可能很大，当前这一步更该先确认双层枚举会不会超时？",
            "options": [
                {"value": "A", "label": "先把双层枚举的总量级和时间限制放在一起判断会不会超时"},
                {"value": "B", "label": "先假设机器跑得够快，写完再看会不会超时"},
                {"value": "C", "label": "先背一个更高级的方法名，规模能不能过以后再说"},
                {"value": "D", "label": "先只看单次操作顺不顺手，不用先估总量级"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这会把最关键的规模判断留到最后碰运气。先知道当前做法会不会超时，才知道要不要换方法。",
                "C": "方法名不能替代规模判断。你先得知道总量级会不会炸，才能决定是否真的需要换方法。",
                "D": "这里最容易漏掉的不是单次操作，而是总量级。两层数量一起变大时，先估总量级才知道当前复杂度能不能过。",
            },
            "explanation": "第一轮先不急着报方法名，而是先站稳一个更基础的判断：两层规模一起变大时，双层枚举的总量级会不会已经明显超出时间限制。",
            "bridge_feedback": f"你这一步真正要站稳的是：{target_bridge or '先根据数据范围判断双层枚举会不会超时。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {
                "difficulty_level": "main",
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "main_mode": "local_scale_check",
            },
        }

    if focus == "shared_prefix_merging":
        text = " ".join(
            str(part or "")
            for part in (
                review_context.get("problem_title"),
                review_context.get("problem_context"),
                review_context.get("bottleneck_text"),
                review_context.get("key_bridge"),
                review_context.get("try_now"),
                review_context.get("next_step"),
            )
        )
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果把很多消息先放进 trie，查询一条拦截串时，为什么不用重看所有消息，而是沿当前前缀往下走？",
            "options": [
                {"value": "A", "label": "查询时不用把所有消息重新逐条拿出来比，只要沿当前前缀往下走"},
                {"value": "B", "label": "查询时还是要把所有消息都重新看一遍，只是代码写法更短"},
                {"value": "C", "label": "trie 会直接把整条答案背出来，所以前缀过程可以完全跳过"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这还是把 trie 当成“换个容器继续逐条比对”。它真正省下来的，是不用把所有消息重新拿出来比，而是直接沿当前前缀走。",
                "C": "trie 不是魔法答案表。查询时还是要沿当前前缀路径往下走，只是不用重看所有消息。",
            },
            "explanation": "第一轮先不问整题复杂度，只盯住一个核心机制：trie 为什么能把“重看所有消息”变成“沿当前前缀往下走”。",
            "bridge_feedback": f"你这一步真正要先站稳的是：{target_bridge or '查询时不重看所有消息，而是沿当前前缀往下走。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {
                "difficulty_level": "main",
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "main_mode": "local_mechanism",
            },
        }

    if focus == "method_selection":
        text = " ".join(
            str(part or "")
            for part in (
                review_context.get("problem_title"),
                review_context.get("problem_context"),
                review_context.get("bottleneck_text"),
                review_context.get("key_bridge"),
                review_context.get("try_now"),
                review_context.get("next_step"),
            )
        )
        if _contains_any(text, ("trie", "前缀", "拦截串", "消息")):
            return {
                "mode": "quiz",
                "quiz_type": "choice",
                "question_text": "如果这题有很多字符串，而且反复在问前缀关系，下面哪一条更像支持 trie 的题面信号？",
                "options": [
                    {"value": "A", "label": "很多字符串有相同开头，而且还要反复按前缀查询或统计"},
                    {"value": "B", "label": "只要串长不超过 20，就一定该直接上 trie"},
                    {"value": "C", "label": "只要数据范围大，就一定先上 trie"},
                    {"value": "D", "label": "只是因为以前做过类似题，所以这题大概率也该用 trie"},
                ],
                "correct_answer": "A",
                "distractor_feedback": {
                    "B": "串长小只是辅助信息，不是决定性信号。更关键的是：很多字符串共享前缀，还要反复按前缀查。",
                    "C": "数据范围大只能提示你先换思路，不会自动说明“就一定是 trie”。还得看是不是在反复做前缀关系。",
                    "D": "熟题感觉可以帮你起念头，但不能替代这题里真正支持 trie 的结构信号。",
                },
                "explanation": "第一轮先不直接讲 trie 的内部机制，而是先站稳一个更前面的判断：题面里到底哪一个结构信号在支持 trie。",
                "bridge_feedback": f"你这一步真正要先站稳的是：{target_bridge or '先找出题面里真正支持 trie 的结构信号。'}",
                "target_bridge": target_bridge,
                "difficulty_level": "main",
                "meta": {
                    "difficulty_level": "main",
                    "focus": focus,
                    "algorithm_category": _infer_algorithm_category(review_context, focus),
                    "main_mode": "local_signal",
                },
            }
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": "当前这一步更适合先把“题面里到底有哪些结构信号指向这种方法”讲清楚，而不是出一题容易变成方法口号的小测。",
            "explanation": "当前这一步更适合先把“题面里到底有哪些结构信号指向这种方法”讲清楚，而不是出一题容易变成方法口号的小测。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }

    if focus in STRUCTURAL_QUIZ_FOCI:
        structural_payload = _deterministic_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level="main",
        )
        if structural_payload:
            return structural_payload

    if focus == "reading_target":
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": "当前这一步更适合先把题目要求和限制讲清楚，而不是出一题容易滑成读题口号的小测。",
            "explanation": "当前这一步更适合先把题目要求和限制讲清楚，而不是出一题容易滑成读题口号的小测。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "constraint_modeling":
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": "当前这一步更适合先把限制关系怎么统一表示讲清楚，而不是出一题容易退回流程建议的小测。",
            "explanation": "当前这一步更适合先把限制关系怎么统一表示讲清楚，而不是出一题容易退回流程建议的小测。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "general_modeling":
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": "当前这一步更适合先把对象、关系或维护量具体讲清楚，而不是出一题容易滑成“第一步该怎么想”的建模型小测。",
            "explanation": "当前这一步更适合先把对象、关系或维护量具体讲清楚，而不是出一题容易滑成“第一步该怎么想”的建模型小测。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "state_design":
        return _deterministic_structural_quiz(review_context, focus, target_bridge, level="main") or {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "这一步更适合先换一种方式讲清楚，而不是继续出流程口号题。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "transition_design":
        return _deterministic_structural_quiz(review_context, focus, target_bridge, level="main") or {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "这一步更适合先换一种方式讲清楚，而不是继续出流程口号题。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "check_condition":
        return _deterministic_structural_quiz(review_context, focus, target_bridge, level="main") or {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "这一步更适合先换一种方式讲清楚，而不是继续出流程口号题。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "greedy_basis":
        return _deterministic_structural_quiz(review_context, focus, target_bridge, level="main") or {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "这一步更适合先换一种方式讲清楚，而不是继续出流程口号题。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "tree_diameter_candidates":
        return _deterministic_structural_quiz(review_context, focus, target_bridge, level="main") or {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "correct_answer": "",
            "explanation": "这一步更适合先换一种方式讲清楚，而不是继续出流程口号题。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "enumeration_order":
        return _deterministic_structural_quiz(review_context, focus, target_bridge, level="main") or {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "这一步更适合先换一种方式讲清楚，而不是继续出流程口号题。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "boundary_debug":
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": "当前这一步更适合先把具体是哪种边界会打破默认前提讲清楚，而不是出一题容易变成调试流程建议的小测。",
            "explanation": "当前这一步更适合先把具体是哪种边界会打破默认前提讲清楚，而不是出一题容易变成调试流程建议的小测。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    if focus == "implementation_debug":
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": "当前这一步更适合先把具体哪种实现前提被打破讲清楚，而不是出一题容易变成调试口号的小测。",
            "explanation": "当前这一步更适合先把具体哪种实现前提被打破讲清楚，而不是出一题容易变成调试口号的小测。",
            "target_bridge": target_bridge,
            "difficulty_level": "main",
            "meta": {"difficulty_level": "main"},
        }
    return {
        "mode": "fallback_explain",
        "quiz_type": "",
        "question_text": "",
        "options": [],
        "correct_answer": "",
        "explanation": "当前这一步还不适合继续出题，应该先换一种方式把卡点说清楚。",
        "target_bridge": "",
        "difficulty_level": "main",
        "meta": {"difficulty_level": "main"},
    }


def _followup_quiz_payload(review_context: dict, focus: str, target_bridge: str, previous_quiz: dict | None = None) -> dict:
    if focus == "unknown":
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "当前这一步还不适合继续出题，应该先换一种方式把卡点说清楚。",
            "target_bridge": "",
            "difficulty_level": "followup",
            "meta": {"difficulty_level": "followup"},
        }

    local_payload = _deterministic_local_followup_quiz(
        review_context,
        focus,
        target_bridge,
        previous_quiz=previous_quiz,
    )
    if local_payload:
        local_payload["meta"] = {
            **(local_payload.get("meta") or {}),
            "difficulty_level": "followup",
            "micro_hint": review_context.get("main_block")
            or "这一步还差一点，我们先只盯住最关键的那一小步。",
            "previous_quiz_type": (previous_quiz or {}).get("quiz_type", ""),
            "previous_question": (previous_quiz or {}).get("question_text", ""),
        }
        return local_payload

    if focus in STRUCTURAL_QUIZ_FOCI:
        if focus in {
            "state_design",
            "check_condition",
            "enumeration_order",
            "transition_design",
            "greedy_basis",
            "tree_path_difference",
            "tree_diameter_candidates",
            "left_bound_update",
            "lazy_semantics",
        }:
            structural_payload = _deterministic_structural_quiz(
                review_context,
                focus,
                target_bridge,
                level="followup",
                previous_quiz=previous_quiz,
            )
        else:
            structural_payload = _generate_structural_quiz(
                review_context,
                focus,
                target_bridge,
                level="followup",
                previous_quiz=previous_quiz,
            )
        if structural_payload and structural_payload.get("mode") == "quiz":
            structural_payload["meta"] = {
                **structural_payload.get("meta", {}),
                "difficulty_level": "followup",
                "micro_hint": review_context.get("main_block")
                or "这一步还差一点，我们先只盯住最关键的那一小步。",
                "previous_quiz_type": (previous_quiz or {}).get("quiz_type", ""),
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            }
            structural_payload["difficulty_level"] = "followup"
        if structural_payload:
            return structural_payload

    return {
        "mode": "fallback_explain",
        "quiz_type": "",
        "question_text": "",
        "options": [],
        "correct_answer": "",
        "fallback_explain": "这一步还不适合继续出 follow-up 小题，我们先换一种方式把卡点讲清楚。",
        "explanation": "这一步还不适合继续出 follow-up 小题，我们先换一种方式把卡点讲清楚。",
        "target_bridge": target_bridge,
        "difficulty_level": "followup",
        "meta": {
            "difficulty_level": "followup",
            "micro_hint": review_context.get("main_block")
            or "这一步还差一点，我们先只盯住最关键的那一小步。",
            "previous_quiz_type": (previous_quiz or {}).get("quiz_type", ""),
            "previous_question": (previous_quiz or {}).get("question_text", ""),
        },
    }


def _easier_quiz_payload(review_context: dict, focus: str, target_bridge: str, previous_quiz: dict | None = None) -> dict:
    if focus in {"unknown"}:
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "当前这一步还不适合继续出题，应该先换一种方式把卡点说清楚。",
            "target_bridge": "",
            "difficulty_level": "easier",
            "meta": {"difficulty_level": "easier"},
        }

    if focus == "tree_path_difference":
        structural_payload = _deterministic_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level="followup",
            previous_quiz=previous_quiz,
        )
        if structural_payload:
            structural_payload["difficulty_level"] = "easier"
            structural_payload["meta"] = {
                **structural_payload.get("meta", {}),
                "difficulty_level": "easier",
                "previous_quiz_type": (previous_quiz or {}).get("quiz_type", ""),
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            }
            return structural_payload

    if focus in STRUCTURAL_QUIZ_FOCI:
        structural_payload = _generate_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level="followup",
            previous_quiz=previous_quiz,
        )
        if structural_payload and structural_payload.get("mode") == "quiz":
            structural_payload["difficulty_level"] = "easier"
            structural_payload["meta"] = {
                **structural_payload.get("meta", {}),
                "difficulty_level": "easier",
                "previous_quiz_type": (previous_quiz or {}).get("quiz_type", ""),
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            }
            return structural_payload
        if structural_payload:
            return structural_payload

    return {
        "mode": "fallback_explain",
        "quiz_type": "",
        "question_text": "",
        "options": [],
        "correct_answer": "",
        "fallback_explain": "这一步更适合先换一种方式讲清楚，而不是继续出更小的小题。",
        "explanation": "这一步更适合先换一种方式讲清楚，而不是继续出更小的小题。",
        "target_bridge": target_bridge,
        "difficulty_level": "easier",
        "meta": {
            "difficulty_level": "easier",
            "previous_quiz_type": (previous_quiz or {}).get("quiz_type", ""),
            "previous_question": (previous_quiz or {}).get("question_text", ""),
        },
    }


def _generic_final_micro_confirm_payload(review_context: dict, focus: str, target_bridge: str) -> dict | None:
    algorithm_category = _infer_algorithm_category(review_context, focus)
    shared_meta = {
        "difficulty_level": "final_micro_confirm",
        "focus": focus,
        "algorithm_category": algorithm_category,
        "confirm_mode": "final_micro_confirm",
    }

    if focus == "constraint_modeling":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果这一步只是先把限制关系站稳，下面哪种做法才对？",
            "options": [
                {"value": "A", "label": "先把限制关系统一成同一种方向或表示，再往下建模"},
                {"value": "B", "label": "先凭印象挑一个熟悉算法，把关系细节留到后面再补"},
                {"value": "C", "label": "先把所有点对关系都枚举出来，关系方向反了再调"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这会把真正的限制关系留空，后面的建模只是在往熟悉方法上硬套，学生还是会在“谁限制谁”这一步继续混乱。",
                "C": "这会跳过“先把关系写整齐”这一步，学生会在对象和方向还没站稳时就进入大规模枚举，错误只会被放大。",
            },
            "explanation": "这一步最小的确认就是：先把限制关系统一成一种表示，再继续往下建模。方向和关系没站稳，后面的边、状态或判断都会跟着歪。",
            "bridge_feedback": f"你最后需要站稳的就是：{target_bridge or '先把限制关系统一成同一种表示。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "final_micro_confirm",
            "meta": shared_meta,
        }

    if focus == "general_modeling":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果这一步只是确认模型有没有站稳，下面哪句更对？",
            "options": [
                {"value": "A", "label": "先把题目里的对象和关系说清楚，再决定怎么表示"},
                {"value": "B", "label": "先猜最像哪类经典题，再把题目往模板上套"},
                {"value": "C", "label": "先写代码框架，具体对象含义可以边写边猜"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这会让学生绕开题目里的真实对象和关系，只靠题感猜模板，模型本身仍然是空的。",
                "C": "对象和关系没说清楚时直接写代码，只会把模糊理解变成更难排查的实现错误。",
            },
            "explanation": "模型类卡点最后要确认的不是模板名，而是对象和关系有没有被说清楚。只有先站稳这件事，后续表示和算法才有依托。",
            "bridge_feedback": f"这一步最后要站稳的是：{target_bridge or '先把对象和关系写清楚。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "final_micro_confirm",
            "meta": shared_meta,
        }

    if focus == "method_selection":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果这一步只确认“为什么该用这个方法”，下面哪句更对？",
            "options": [
                {"value": "A", "label": "先找题面里真正支持这个方法的结构信号"},
                {"value": "B", "label": "先看这题像不像以前做过的题，像就直接套方法"},
                {"value": "C", "label": "先背方法步骤，题面信号可以做完后再补"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这仍然是在靠熟悉感猜方法，不是在回答“题面里到底哪一处结构支持这个方法”。",
                "C": "先背步骤会让方法和题面脱节，学生还是说不清为什么这道题能这样做。",
            },
            "explanation": "方法选择类的最终最小确认，就是看学生能不能指出题面里真正支持这个方法的结构信号，而不是靠熟悉感或背模板。",
            "bridge_feedback": f"这一步最后要确认的是：{target_bridge or '先找出支持这个方法的题面信号。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "final_micro_confirm",
            "meta": shared_meta,
        }

    if focus == "reading_target":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果这一步只确认你有没有读清题目目标，下面哪句更对？",
            "options": [
                {"value": "A", "label": "先说清题目最后要求求什么或输出什么"},
                {"value": "B", "label": "先猜算法类型，目标细节可以到写代码时再看"},
                {"value": "C", "label": "先抄样例，等答案不对时再回头看目标"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "题目目标没读清时先猜方法，后面所有判断都会建立在错目标上。",
                "C": "样例只能帮你感受题目，不会自动替你定义最终要求求什么。",
            },
            "explanation": "读题目标类的最后确认，就是先把“题目到底要求你求什么”说清楚。目标不稳，后面方法和实现都会一起漂。",
            "bridge_feedback": f"这一步最后要确认的是：{target_bridge or '先把题目最后要求求什么说清楚。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "final_micro_confirm",
            "meta": shared_meta,
        }

    return None


def _deterministic_local_final_micro_confirm_payload(
    review_context: dict,
    focus: str,
    target_bridge: str,
    previous_quiz: dict | None = None,
) -> dict | None:
    text = " ".join(
        str(part or "")
        for part in (
            review_context.get("problem_title"),
            review_context.get("problem_context"),
            review_context.get("bottleneck_text"),
            review_context.get("key_bridge"),
            review_context.get("try_now"),
            review_context.get("next_step"),
            (previous_quiz or {}).get("question_text", ""),
        )
    )
    if focus == "complexity_fit":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果两层规模都很大，是不是应该先判断双层枚举会不会超时？",
            "options": [
                {"value": "A", "label": "是"},
                {"value": "B", "label": "不是"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "这会把最关键的规模判断跳过去。先知道当前做法会不会炸，后面才知道要不要换方法。",
            },
            "explanation": "最后这题只确认一个最小事实：规模大时，先判断双层枚举能不能过。",
            "bridge_feedback": f"你最后要站稳的就是：{target_bridge or '先根据数据范围判断双层枚举会不会超时。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "final_micro_confirm",
            "meta": {
                "difficulty_level": "final_micro_confirm",
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "confirm_mode": "final_micro_confirm",
                "final_mode": "local_scale_check",
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            },
        }

    if focus == "shared_prefix_merging":
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "把很多消息先放进 trie 后，查一条拦截串时，真正省下来的，是不是不用重看所有消息、只沿当前前缀往下走？",
            "options": [
                {"value": "A", "label": "不用把所有消息重新逐条拿出来比，只要沿着当前前缀往下走"},
                {"value": "B", "label": "不用再看前缀，系统会直接把答案完整背出来"},
                {"value": "C", "label": "还是要把所有消息再看一遍，只是 trie 的名字更高级"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "trie 不是魔法答案表，查询时还是要看当前这条拦截串的前缀路径，只是不用重看所有消息。",
                "C": "这还是把 trie 当成“换个容器继续逐条比对”。真正省下来的，是不必把所有消息重新拿出来看一遍。",
            },
            "explanation": "最后这题不再问抽象方法判断，只确认一个最小局部事实：trie 之所以更快，是因为查询时不用把所有消息重新逐条拿出来比，而是只沿当前前缀往下走。",
            "bridge_feedback": f"你最后要站稳的就是：{target_bridge or '查询时不重看所有消息，只沿当前前缀往下走。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "final_micro_confirm",
            "meta": {
                "difficulty_level": "final_micro_confirm",
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "confirm_mode": "final_micro_confirm",
                "final_mode": "local_mechanism",
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            },
        }

    if focus != "method_selection":
        return None

    if _contains_any(text, ("trie", "前缀", "拦截串", "消息")):
        return {
            "mode": "quiz",
            "quiz_type": "choice",
            "question_text": "如果这题反复按前缀查询很多字符串，是不是应该先把这个信号当成支持 trie 的线索？",
            "options": [
                {"value": "A", "label": "是"},
                {"value": "B", "label": "不是"},
            ],
            "correct_answer": "A",
            "distractor_feedback": {
                "B": "最后这题只确认一个最小事实：很多字符串共享前缀、还要反复按前缀查，这正是支持 trie 的题面线索。",
            },
            "explanation": "最后这题只确认一个最小事实：方法选择要先回到题面信号，而不是先跳进机制细节。",
            "bridge_feedback": f"你最后要站稳的就是：{target_bridge or '先找题面里真正支持 trie 的结构信号。'}",
            "target_bridge": target_bridge,
            "difficulty_level": "final_micro_confirm",
            "meta": {
                "difficulty_level": "final_micro_confirm",
                "focus": focus,
                "algorithm_category": _infer_algorithm_category(review_context, focus),
                "confirm_mode": "final_micro_confirm",
                "final_mode": "local_signal",
                "previous_question": (previous_quiz or {}).get("question_text", ""),
            },
        }

    return {
        "mode": "quiz",
        "quiz_type": "choice",
        "question_text": "如果这一步只确认方法依据，是不是应该先找题面里真正支持这个方法的结构信号？",
        "options": [
            {"value": "A", "label": "是"},
            {"value": "B", "label": "不是"},
        ],
        "correct_answer": "A",
        "distractor_feedback": {
            "B": "方法选择这一步最小的确认，不是看你会不会背步骤，而是看你会不会先找题面里支持它的结构信号。",
        },
        "explanation": "最后这题只确认一个最小事实：方法依据要先回到题面信号，而不是靠熟题感觉或背模板。",
        "bridge_feedback": f"你最后要站稳的就是：{target_bridge or '先找题面里真正支持这个方法的结构信号。'}",
        "target_bridge": target_bridge,
        "difficulty_level": "final_micro_confirm",
        "meta": {
            "difficulty_level": "final_micro_confirm",
            "focus": focus,
            "algorithm_category": _infer_algorithm_category(review_context, focus),
            "confirm_mode": "final_micro_confirm",
            "final_mode": "local_signal",
            "previous_question": (previous_quiz or {}).get("question_text", ""),
        },
    }


def generate_final_micro_confirm_quiz(review_context: dict, previous_quiz: dict | None = None) -> dict:
    """生成第三轮补救后的最后一小题确认，优先本地确定性产出，避免再次放大模型负担。"""
    focus = _detect_quiz_focus(review_context)
    target_bridge = _default_target_bridge(review_context, focus)

    payload = None
    if focus in STRUCTURAL_QUIZ_FOCI:
        payload = _deterministic_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level="final_micro_confirm",
            previous_quiz=previous_quiz,
        )
    if not payload:
        payload = _deterministic_local_final_micro_confirm_payload(
            review_context,
            focus,
            target_bridge,
            previous_quiz=previous_quiz,
        )
    if not payload:
        payload = _generic_final_micro_confirm_payload(review_context, focus, target_bridge)
    if not payload:
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": "这一步暂时不适合继续加确认题，我们先停在这里，避免越讲越散。",
            "explanation": "这一步暂时不适合继续加确认题，我们先停在这里，避免越讲越散。",
            "target_bridge": target_bridge,
            "difficulty_level": "final_micro_confirm",
            "meta": {"difficulty_level": "final_micro_confirm", "focus": focus},
        }

    payload = _normalize_quiz_contract(payload, review_context, focus, QUIZ_ROLE_REMEDY)
    if payload and payload.get("mode") == "quiz":
        payload["difficulty_level"] = "final_micro_confirm"
        payload["meta"] = {
            **(payload.get("meta") or {}),
            "difficulty_level": "final_micro_confirm",
            "focus": focus,
            "algorithm_category": (payload.get("meta") or {}).get("algorithm_category") or _infer_algorithm_category(review_context, focus),
            "confirm_mode": "final_micro_confirm",
            "previous_quiz_type": (previous_quiz or {}).get("quiz_type", ""),
            "previous_question": (previous_quiz or {}).get("question_text", ""),
        }
    return payload


def _knowledge_card_id(review_context: dict, focus: str, previous_quiz: dict | None = None) -> str:
    text = " ".join(
        str(part or "")
        for part in (
            review_context.get("problem_title"),
            review_context.get("problem_context"),
            review_context.get("bottleneck_text"),
            review_context.get("key_bridge"),
            (previous_quiz or {}).get("question_text", ""),
        )
    )
    if focus == "left_bound_update":
        return "binary_search.left_bound"
    if focus == "lazy_semantics":
        return "segment_tree.lazy_semantics"
    if focus == "shared_prefix_merging":
        return "string.trie.shared_prefix_merging"
    if focus == "state_design":
        return "dp.state_design"
    if focus == "transition_design":
        return "dp.transition_design"
    if focus == "check_condition":
        return "binary_search.check_condition"
    if focus == "greedy_basis":
        return "greedy.greedy_basis"
    if focus == "tree_path_difference":
        return "graph.tree_path_difference"
    if focus == "tree_diameter_candidates":
        return "graph.tree_diameter.tree_diameter_candidates"
    if focus == "complexity_fit":
        return "modeling.scale_estimation"
    if focus in {"method_selection", "complexity_fit"}:
        return "modeling.method_selection"
    if focus == "general_modeling":
        return "modeling.method_selection"
    return f"bridge.{focus or 'generic'}"


def generate_knowledge_bailout_card(review_context: dict, previous_quiz: dict | None = None) -> dict:
    focus = _detect_quiz_focus(review_context)
    target_bridge = _default_target_bridge(review_context, focus)
    card_id = _knowledge_card_id(review_context, focus, previous_quiz)
    opening = "你刚才已经试了几种方式，这不是白费。现在我们把这一步单独讲清楚，再回来确认。"

    cards = {
        "dp.state_design": {
            "bridge_explanation": "这里最容易误会的是：dp[x][y] 这一格不是“整题答案放哪”。真正要站稳的是：它表示“站在格子 (x,y) 这个状态上，能得到的子问题结果”。先把这一格存什么说清楚，转移才不会乱。",
            "visual_hint": "状态格 dp[x][y]\n-> 先问：它存的是什么结果\n-> 再问：这个结果从哪几格转来",
            "algorithm_overview": "这一步在整套记忆化搜索/DP 里负责先把“状态格里存什么”站稳，也就是先把子问题结果说清楚。后面再让这些状态格彼此转移。",
            "micro_action": "你先只回答一句：dp[x][y] 这一格是在记录哪一个子问题的结果？",
        },
        "dp.transition_design": {
            "bridge_explanation": "这里最容易误会的是：先凭手感写一个最顺手的转移。真正要站稳的是：当前状态可能从哪几类前一个状态过来。先别急着写式子，先把来源想全。",
            "visual_hint": "当前格 (i,j)\n<- 上一层 (i-1,j-1)\n<- 上一层 (i-1,j)\n先把来源想全，再写 max/min/加法",
            "algorithm_overview": "这一步在整套 DP 里负责先把“当前状态依赖哪些前态”列出来，再决定怎么合并这些来源。",
            "micro_action": "先只列两行：当前状态可能从哪几类前态来？",
        },
        "binary_search.check_condition": {
            "bridge_explanation": "这里最容易误会的是：check(mid) 要直接算出答案。真正要站稳的是：它只回答一个小问题，现在这个 mid 行不行。先把这件事站稳，二分方向才不会乱。",
            "visual_hint": "check(5)=true\n-> 只说明 5 还可行\n-> 再决定区间往哪边缩",
            "algorithm_overview": "这一步在整套二分答案里负责判断“当前这个 mid 是否可行”。二分本身只负责缩区间。比如 `check(5)=true`，只说明“答案至少还能达到 5”这句话当前成立，不是已经把最终答案直接算出来了。",
            "micro_action": "你先只说一句：check(mid) 返回 true，到底说明了什么？",
        },
        "binary_search.left_bound": {
            "bridge_explanation": "这里最容易误会的是：一看到 `a[mid] == x` 就能立刻停。真正要站稳的是：如果目标是最左位置，mid 还可能就是答案，所以要先保留 mid，再继续往左找。",
            "visual_hint": "[1,2,2,2,3]\na[mid] == 2\n-> mid 先留作候选\n-> r = mid 继续往左缩",
            "algorithm_overview": "这一步在整套二分边界题里负责先站稳“相等时要不要保留 mid”。只有这步对了，左边界才不会被你自己丢掉。",
            "micro_action": "先只回答一句：为什么 `a[mid] == x` 时还不能马上把 mid 丢掉？",
        },
        "greedy.greedy_basis": {
            "bridge_explanation": "这里最容易误会的是：先背一个贪心结论就行。真正要站稳的是：为什么当前这个对象先选不会吃亏，还能给后面留空间。",
            "visual_hint": "[1,3] 先选\n[3,5] 还能接上\n-> 后面还有空间\n-> 这一步才不吃亏",
            "algorithm_overview": "这一步在整套贪心里负责解释“为什么先选它不会吃亏”。后面才谈局部最优怎样连成整体。",
            "micro_action": "你先只回答：先选当前这个对象，为什么不会把后面堵死？",
        },
        "graph.tree_diameter.tree_diameter_candidates": {
            "bridge_explanation": "这里最容易误会的是：加上一条新边后，只要盯着新边本身看。真正要站稳的是：新的最长路只可能来自左边内部、右边内部，或者经过新边把两边最远点接起来。",
            "visual_hint": "左边最远点\n右边最远点\n经过新边接起来\n先比较这三类候选，再判断谁最长",
            "algorithm_overview": "这一步在整套树直径思路里负责先把三类候选想全。后面才去比较哪一类真的最长。",
            "micro_action": "先只回答一句：如果最长路经过新边，两边各该接到什么样的点？",
        },
        "graph.tree_path_difference": {
            "bridge_explanation": "这里最容易误会的是：树剖或 LCA 本身会把答案算出来。真正要站稳的是：LCA 只是帮你定位一条树上路径在哪里分叉；路径贡献要先变成端点、LCA 和 LCA 父亲附近的差分标记，最后用 DFS 子树汇总还原每个点的经过次数。",
            "visual_hint": "一条路径 s -> t\ns += 1, t += 1\nlca -= 1, parent(lca) -= 1\nDFS 向上汇总 -> 路径上的点得到贡献",
            "algorithm_overview": "这一步在整套树上差分里负责把“很多路径逐点加一”改成“每条路径只改少数几个点”。树剖可以帮你求 LCA 或维护路径，但 P3128 这座桥的核心仍然是：端点/LCA 打标记，最后 DFS 汇总出每个点被经过多少次。",
            "micro_action": "先只回答一句：一条 s 到 t 的路径，为什么不是沿路逐点加，而是先在端点和 LCA 附近打标记？",
        },
        "string.trie.shared_prefix_merging": {
            "bridge_explanation": "这里最容易误会的是：trie 像在神奇地把答案背出来。真正要站稳的是：它先把公共前缀合在一起，所以查询时不用重看所有消息，只沿当前前缀往下走。",
            "visual_hint": "101\n100\n11\n前缀 10 先合在一起\n查询时只沿前缀路径往下走",
            "algorithm_overview": "这一步在整套 trie 里负责先把相同开头合并起来。后面查询时就只需要沿这条前缀路径走。比如消息有 `101`、`100`、`11`，前两条前面两位一样，就值得先把这段相同开头合在一起看。",
            "micro_action": "先只回答一句：trie 为什么能省掉重看所有消息这件事？",
        },
        "modeling.method_selection": {
            "bridge_explanation": "这里最容易误会的是：先凭题感猜一个方法名。真正要站稳的是：先看题面里有没有真正支持这个方法的结构信号。方法选对，先靠题面信号，不靠题感。",
            "visual_hint": "题面信号\n-> 规模 / 结构 / 约束\n-> 这些信号支持哪种做法",
            "algorithm_overview": "这一步在整套方法选择里负责先读题面信号，先抓住题面里真正的结构信号。后面才判断这些结构信号支持哪种做法。",
            "micro_action": "先指出题面里一个真正支持当前方法的信号。",
        },
        "modeling.scale_estimation": {
            "bridge_explanation": "这里最容易误会的是：先报一个更高级的方法名就行。真正要站稳的是：先估规模，如果两层数量一起变大，双层枚举很可能先炸。先把“当前做法能不能过”站稳，再判断要不要换方法。",
            "visual_hint": "先看数据范围\n-> 再看有没有两层一起变大\n-> 最后判断双层枚举能不能撑住",
            "algorithm_overview": "这一步在整套方法判断里负责先看规模能不能撑住当前做法，先判断双层枚举会不会先炸。后面才决定要不要换方法。",
            "micro_action": "先只回答一句：这题更该先判断哪件事，方法名还是规模能不能过？",
        },
        "segment_tree.lazy_semantics": {
            "bridge_explanation": "这里最容易误会的是：lazy 像“代码还没执行完”。真正要站稳的是：lazy 记录的是这段区间已经确定、但还没下传给孩子的信息。",
            "visual_hint": "[1,4]\nlazy=3\n左儿长度=2\n-> pushdown: 左儿 sum += 3×2",
            "algorithm_overview": "这一步在线段树里负责先把 lazy 的语义站稳：它记录的是区间信息暂时还挂在父节点上，后面再下传给孩子。比如节点管 `[1,4]`，`lazy=3` 表示这段区间每个数都还欠着 `+3` 没下传；如果左儿子长度是 `2`，pushdown 时左儿子的 `sum` 会先加 `3×2`。",
            "micro_action": "先只回答一句：lazy 标记到底记录的是哪一类信息？",
        },
    }
    selected = cards.get(card_id) or {
        "bridge_explanation": f"你现在卡住的这一步，其实可以先缩成一句更白的话：{target_bridge or '先把当前桥站稳。'}",
        "visual_hint": "先只盯这一小步\n-> 说清它在做什么\n-> 再回到整题",
        "algorithm_overview": "先把当前桥讲清楚，再把它放回整种方法里看，理解会更稳。",
        "micro_action": "先只用一句话，说清你现在卡住的这一步到底在确认什么。",
    }
    focus_text = " ".join(
        str(part or "")
        for part in (
            review_context.get("problem_title"),
            review_context.get("problem_context"),
            review_context.get("bottleneck_text"),
            review_context.get("key_bridge"),
            target_bridge,
        )
    )
    if card_id == "modeling.method_selection" and _contains_any(focus_text, ("trie", "前缀", "拦截串", "消息")):
        selected = {
            **selected,
            "visual_hint": "101\n100\n11\n前两条前面两位一样\n-> 这就是“相同开头”的题面信号\n-> 这是支持 trie 的题面信号",
            "algorithm_overview": "这一步在整套方法选择里负责先读题面信号：很多消息有相同开头，而且要反复按前缀查。比如消息有 `101`、`100`、`11`，前两条前面两位一样，这就是一个很直接的信号。先把这个信号抓住，下一步才会自然过渡到“这些相同开头值不值得先合在一起看”。",
            "micro_action": "先指出题面里一个支持 trie 的信号，再补一句：为什么很多消息相同开头值得先合在一起看？",
        }
    if card_id == "string.trie.shared_prefix_merging" and _is_trie_node_count_context(focus_text):
        selected = {
            **selected,
            "bridge_explanation": "这里最容易误会的是：trie 节点像随便存个数字就行。真正要站稳的是：经过次数记录了有多少消息经过当前前缀节点，结束次数记录了有多少消息正好在这里结束。把这两个数分清，前缀查询时才知道该沿路径累加什么。",
            "visual_hint": "101\n100\n11\n前缀 10 这个节点\n-> 经过次数至少是 2\n-> 结束次数另算",
            "algorithm_overview": "这一步在整套 trie 里负责先把“节点到底存什么”站稳。比如消息有 `101`、`100`、`11`，前两条都会经过前缀 `10` 这个节点，所以它的经过次数至少是 `2`；如果一条消息正好在某个节点结束，还要单独记结束次数。查询时，你才知道为什么能沿路径看经过次数和结束次数，而不是把所有消息重新翻一遍。",
            "micro_action": "先只回答一句：经过次数表示的到底是哪一类信息？",
        }
    selected = _augment_knowledge_card_with_external_snippets(card_id, selected)
    return {
        "mode": "knowledge_card",
        "card_id": card_id,
        "knowledge_card_id": card_id,
        "opening": opening,
        "bridge_explanation": selected["bridge_explanation"],
        "visual_hint": selected.get("visual_hint", ""),
        "algorithm_overview": selected["algorithm_overview"],
        "micro_action": selected["micro_action"],
        "target_bridge": target_bridge,
        "focus": focus,
    }


def generate_knowledge_confirm_quiz(
    review_context: dict,
    knowledge_card: dict,
    previous_quiz: dict | None = None,
) -> dict:
    del previous_quiz
    card_id = str((knowledge_card or {}).get("card_id") or "")
    target_bridge = str((knowledge_card or {}).get("target_bridge") or "").strip()
    focus = str((knowledge_card or {}).get("focus") or _detect_quiz_focus(review_context))
    algorithm_category = _infer_algorithm_category(review_context, focus)
    payload_map = {
        "dp.state_design": {
            "question_text": "知识卡后确认：如果只看 dp[x][y] 这一格，它更像在记录什么？",
            "options": [
                {"value": "A", "label": "这个状态本身对应的子问题结果"},
                {"value": "B", "label": "整道题最后答案应该直接写在哪"},
                {"value": "C", "label": "外层循环当前写到第几轮"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把“状态格存什么”站稳。",
            "bridge_feedback": "先把状态格记录的子问题结果站稳。",
            "distractor_feedback": {
                "B": "这仍然把状态格当成整题答案位置了。状态格先存的是当前状态自己的结果。",
                "C": "循环写到第几轮是代码过程，不是状态格本身记录的内容。",
            },
        },
        "dp.transition_design": {
            "question_text": "知识卡后确认：如果当前状态可能有两类合法来源，先要做的更像下面哪件事？",
            "options": [
                {"value": "A", "label": "先把两类合法来源想全"},
                {"value": "B", "label": "先随便挑一种来源写上去"},
                {"value": "C", "label": "先把最终答案位置定好"},
            ],
            "correct_answer": "A",
            "explanation": "这题只确认一个最小事实：转移前先把合法来源想全。",
            "bridge_feedback": "先把当前状态的来源想全。",
            "distractor_feedback": {
                "B": "少想一类来源，后面的转移再工整也会漏情况。",
                "C": "这里先要站稳的是来源完整性，不是最终答案位置。",
            },
        },
        "binary_search.check_condition": {
            "question_text": "知识卡后确认：如果 `check(mid)` 返回 true，它先说明的更像下面哪句话？",
            "options": [
                {"value": "A", "label": "当前这个 mid 可行"},
                {"value": "B", "label": "最终最优答案已经直接算出来了"},
                {"value": "C", "label": "二分方向一定只能往更大的一边走"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把 check 的职责站稳。",
            "bridge_feedback": "先把“当前这个 mid 可行”这句话站稳。",
            "distractor_feedback": {
                "B": "true 只是在说当前 mid 行得通，不是直接把最终答案算出来。",
                "C": "区间往哪边缩，还要结合题目是在找最大可行还是最小可行。",
            },
        },
        "binary_search.left_bound": {
            "question_text": "知识卡后确认：如果目标是找最左那个位置，`a[mid] == x` 时更该先做什么？",
            "options": [
                {"value": "A", "label": "先保留 mid，再继续往左找更早的位置"},
                {"value": "B", "label": "先把 mid 丢掉，只看右边"},
                {"value": "C", "label": "直接返回 mid，不用再看前面"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把“相等时先保留 mid”站稳。",
            "bridge_feedback": "先把“相等时保留 mid”这一步站稳。",
            "distractor_feedback": {
                "B": "目标是最左位置时，mid 可能就是答案，不能先丢。",
                "C": "直接返回只能保证找到一个位置，不能保证它已经是最左那个。",
            },
        },
        "greedy.greedy_basis": {
            "question_text": "知识卡后确认：如果先选当前这个对象，更该先确认哪句话？",
            "options": [
                {"value": "A", "label": "它不会把后面的选择空间堵死"},
                {"value": "B", "label": "它看起来最熟悉，所以先选它"},
                {"value": "C", "label": "先选它只是为了让代码更好写"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把“为什么先选它不吃亏”站稳。",
            "bridge_feedback": "先说明当前对象为什么不吃亏。",
            "distractor_feedback": {
                "B": "贪心依据不是熟悉感，而是这一步不会破坏后面的结构。",
                "C": "代码好写不是贪心成立的理由。",
            },
        },
        "graph.tree_diameter.tree_diameter_candidates": {
            "question_text": "知识卡后确认：如果最长路经过新边，两边更该接到哪类点？",
            "options": [
                {"value": "A", "label": "连接点两侧各自离连接点最远的点"},
                {"value": "B", "label": "连接点两侧随便找两个点接上就行"},
                {"value": "C", "label": "只看左边最远点，右边接谁都差不多"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把“经过新边时两边都要接最远点”站稳。",
            "bridge_feedback": "先把“经过新边时，两边都接各自最远点”这句话站稳。",
            "distractor_feedback": {
                "B": "随便接点不会得到这类候选里的最长路径，两边都要往更远的点去接。",
                "C": "经过新边的候选要同时考虑左右两边，不是只拉长其中一边。",
            },
        },
        "graph.tree_path_difference": {
            "question_text": "知识卡后确认：P3128 这类多条树上路径统计经过次数时，更该先站稳哪句话？",
            "options": [
                {"value": "A", "label": "每条路径先在端点和 LCA 附近做差分标记，最后 DFS 汇总"},
                {"value": "B", "label": "树剖或 LCA 求出来后，每个点的经过次数会自动出现"},
                {"value": "C", "label": "每条路径都逐点加一最稳，差分只是可有可无的优化"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把“端点/LCA 标记 + DFS 汇总”这座桥站稳。",
            "bridge_feedback": "先把“路径贡献差分标记，最后 DFS 汇总还原经过次数”站稳。",
            "distractor_feedback": {
                "B": "LCA 只定位路径分叉点，不会自动给出所有点的经过次数。",
                "C": "逐点加一正是要避免的重复更新。树上差分不是装饰，而是核心记录方式。",
            },
        },
        "string.trie.shared_prefix_merging": {
            "question_text": "知识卡后确认：查询一条串时，trie 更像是在沿当前前缀做下面哪件事？",
            "options": [
                {"value": "A", "label": "沿着这条串的当前前缀一路往下走"},
                {"value": "B", "label": "把所有消息重新逐条拿出来比一遍"},
                {"value": "C", "label": "直接跳过前缀，系统自动背出答案"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把“沿前缀往下走”站稳。",
            "bridge_feedback": "先把“只沿当前前缀往下走，不用重看所有消息”这件事站稳。",
            "distractor_feedback": {
                "B": "这仍然是在重看所有消息，正是 trie 想省掉的重复工作。",
                "C": "trie 不是自动背答案，它只是把公共前缀提前合并。",
            },
        },
        "modeling.method_selection": {
            "question_text": "知识卡后确认：如果你要说明“为什么该用这个方法”，更该先说题面里的哪件事？",
            "options": [
                {"value": "A", "label": "题面里真正支持这个方法的结构信号"},
                {"value": "B", "label": "这题像以前哪道熟题"},
                {"value": "C", "label": "先把方法步骤背出来"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你会不会先抓题面信号。",
            "bridge_feedback": "先说题面里支持这个方法的结构信号。",
            "distractor_feedback": {
                "B": "像不像熟题，不等于这题真的支持这个方法。",
                "C": "背步骤不能代替题面信号判断。",
            },
        },
        "modeling.scale_estimation": {
            "question_text": "知识卡后确认：如果两层规模都可能很大，当前更该先确认哪件事？",
            "options": [
                {"value": "A", "label": "先判断双层枚举会不会明显超时"},
                {"value": "B", "label": "先背一个更高级的方法名，规模以后再看"},
                {"value": "C", "label": "先假设机器跑得够快，写完再试"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把“先做规模判断”站稳。",
            "bridge_feedback": "先把“双层枚举会不会先炸，规模能不能撑住当前做法”这句话站稳。",
            "distractor_feedback": {
                "B": "方法名不能替代规模判断。先要知道当前做法会不会在这个规模下炸掉。",
                "C": "把超时风险留到最后再碰，会让你在错误方向上走很久。",
            },
        },
        "segment_tree.lazy_semantics": {
            "question_text": "知识卡后确认：lazy 标记更像在记录下面哪类东西？",
            "options": [
                {"value": "A", "label": "当前区间已经确定、但还没下传给孩子的信息"},
                {"value": "B", "label": "当前函数还没执行完的代码步骤"},
                {"value": "C", "label": "整棵树最后的最终答案"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把 lazy 的语义站稳。",
            "bridge_feedback": "先把 lazy 记录的是“还没下传的信息”站稳。",
            "distractor_feedback": {
                "B": "lazy 不是代码执行进度条，而是区间信息还挂在父节点上。",
                "C": "最终答案不会直接塞进 lazy。lazy 只负责记录还没下传的信息。",
            },
        },
    }
    selected = payload_map.get(card_id) or {
        "question_text": "知识卡后确认：现在你最该先说清楚下面哪件事？",
        "options": [
            {"value": "A", "label": target_bridge or "当前这一步到底在确认什么"},
            {"value": "B", "label": "先猜它像哪类熟题"},
            {"value": "C", "label": "先跳到完整解法"},
        ],
        "correct_answer": "A",
        "explanation": "知识卡后的最后确认，只看你有没有把当前桥说清楚。",
        "bridge_feedback": target_bridge or "先把当前桥说清楚。",
        "distractor_feedback": {
            "B": "这里先要站稳的是当前桥，不是熟题联想。",
            "C": "直接跳完整解法，会把刚刚补的桥又冲散。",
        },
    }
    focus_text = " ".join(
        str(part or "")
        for part in (
            review_context.get("problem_title"),
            review_context.get("problem_context"),
            review_context.get("bottleneck_text"),
            review_context.get("key_bridge"),
            target_bridge,
        )
    )
    if card_id == "string.trie.shared_prefix_merging" and _is_trie_node_count_context(focus_text):
        selected = {
            "question_text": "知识卡后确认：如果一个 trie 节点记录经过次数，它更像在说明下面哪句话？",
            "options": [
                {"value": "A", "label": "有多少消息经过当前前缀节点"},
                {"value": "B", "label": "当前代码已经执行到了第几步"},
                {"value": "C", "label": "整棵 trie 的最终答案已经放在这里"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，只看你有没有把“经过次数记录的是经过当前前缀节点的消息数”站稳。",
            "bridge_feedback": "先把“经过次数表示有多少消息经过当前前缀节点”这句话站稳。",
            "distractor_feedback": {
                "B": "经过次数不是代码执行进度，它是在记这条前缀路径上有多少消息走到这里。",
                "C": "节点里的经过次数不是整题答案，只是当前前缀节点的局部统计。",
            },
        }
    if card_id == "modeling.method_selection" and _contains_any(focus_text, ("trie", "前缀", "拦截串", "消息")):
        selected = {
            "question_text": "知识卡后确认：如果很多消息有相同开头，而且还要反复按前缀查，下面哪句更像真正支持 trie 的说明？",
            "options": [
                {"value": "A", "label": "很多消息有相同开头，值得先合在一起看，再按前缀一路往下查"},
                {"value": "B", "label": "只要看到字符串题，就可以先默认套 trie"},
                {"value": "C", "label": "先把 trie 的代码步骤背下来，题面信号以后再补"},
            ],
            "correct_answer": "A",
            "explanation": "知识卡后的最后确认，不只看你会不会说“支持 trie”，还看你能不能把这个支持理由说得更贴题：很多消息有相同开头，而且要反复按前缀查，所以这些相同开头值得先合在一起看。",
            "bridge_feedback": "先把“题面里有很多相同开头，而且这些相同开头值得先合在一起看，所以支持 trie”这句话站稳。",
            "distractor_feedback": {
                "B": "字符串题很多，但不是所有字符串题都该默认上 trie。还是要回到题面里看有没有共享前缀和反复前缀查询这类信号。",
                "C": "背代码步骤不能代替方法判断。学生还是要先说清楚这题为什么支持 trie。",
            },
        }
    return {
        "mode": "quiz",
        "quiz_type": "choice",
        "question_text": selected["question_text"],
        "options": selected["options"],
        "correct_answer": selected["correct_answer"],
        "explanation": selected["explanation"],
        "bridge_feedback": selected["bridge_feedback"],
        "distractor_feedback": selected["distractor_feedback"],
        "target_bridge": target_bridge,
        "difficulty_level": "knowledge_confirm",
        "meta": {
            "difficulty_level": "knowledge_confirm",
            "knowledge_bailout": True,
            "knowledge_card_id": card_id,
            "knowledge_card": knowledge_card,
            "focus": focus,
            "algorithm_category": algorithm_category,
        },
    }


def _confirm_quiz_payload(review_context: dict, focus: str, target_bridge: str, previous_quiz: dict | None = None) -> dict:
    if focus in {"unknown"}:
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "当前这一步更适合先换一种方式讲清楚，而不是继续出确认题。",
            "target_bridge": "",
            "difficulty_level": "confirm",
            "meta": {
                "difficulty_level": "confirm",
                "confirm_focus": "fallback_explain",
            },
        }

    if focus == "tree_path_difference":
        structural_payload = _deterministic_structural_quiz(
            review_context,
            focus,
            target_bridge,
            level="confirm",
            previous_quiz=previous_quiz,
        )
        if structural_payload:
            return structural_payload

    if focus in STRUCTURAL_QUIZ_FOCI:
        structural_payload = _generate_structural_confirm_quiz(
            review_context,
            focus,
            target_bridge,
            previous_quiz,
        )
        if structural_payload:
            return structural_payload

    mapping = {
        "reading_target": (
            "如果把这一步换个说法，你最先还是要看清哪件事？",
            [
                "题目到底要你求什么、限制了什么",
                "先抓一个熟悉方法往上套，再边做边改",
                "先把样例里的过程当成通用流程",
                "先按自己猜的目标去理解条件",
            ],
            "题目到底要你求什么、限制了什么",
            "就算换个说法，这一步最先也还是要看清题目要求和限制。",
            "small_scenario_transfer",
        ),
        "method_selection": (
            "如果题目换了个小场景，这一步最先还是要找什么？",
            [
                "题面里支持这个方法的那个信号",
                "最熟悉的模板长什么样",
                "样例里最大的那个数",
                "代码里先写哪一层循环",
            ],
            "题面里支持这个方法的那个信号",
            "确认方法时，最关键的仍然是先看题面给了什么信号，而不是先背模板。",
            "small_scenario_transfer",
        ),
        "constraint_modeling": (
            "就算不写原题里的符号，这一步最先还是要整理什么？",
            [
                "限制关系先怎么统一写出来",
                "先把图画出来，再慢慢猜关系",
                "先想最短路模板怎么背",
                "先把最终答案格式定下来",
            ],
            "限制关系先怎么统一写出来",
            "确认这类桥梁时，关键仍然是先把限制关系写整齐，而不是先套图论模板。",
            "object_recognition",
        ),
        "general_modeling": (
            "如果把原题缩成只有几个对象，这一步最先还是要做什么？",
            [
                _bridge_first_step_phrase(review_context, focus, "先写清这些对象分别是什么、谁和谁有关系"),
                "先猜它像哪类做过的题，再往上套方法",
                "先把后面实现流程定下来，再回头补模型",
                "先看样例最后输出了什么，再猜中间结构",
            ],
            _bridge_first_step_phrase(review_context, focus, "先写清这些对象分别是什么、谁和谁有关系"),
            "换个小场景后，这一步还是要先站稳“谁”和“谁之间发生了什么”，而不是先猜方法。",
            "small_scenario_transfer",
        ),
        "state_design": (
            "如果换个更小的例子，这一步最先还是要说清什么？",
            [
                _bridge_first_step_phrase(review_context, focus, "先说清这一维状态到底表示什么"),
                "先把转移式大致写出来，再边写边补状态",
                "先把循环顺序定下来，再反推状态含义",
                "先把边界和数组大小定死，再看状态够不够",
            ],
            _bridge_first_step_phrase(review_context, focus, "先说清这一维状态到底表示什么"),
            "确认状态设计时，最重要的证据不是会不会写式子，而是能不能说清这一维表示什么。",
            "small_scenario_transfer",
        ),
        "transition_design": (
            "如果你把这一步讲给别人听，最该先提醒哪件事？",
            [
                "转移有没有漏掉一种情况",
                "先把状态再加一维试试看",
                "先把循环顺序写死再说",
                "先把答案输出格式定好",
            ],
            "转移有没有漏掉一种情况",
            "换个角度看，转移设计最常见的问题仍然是少了一支情况。",
            "incorrect_reason_check",
        ),
        "check_condition": (
            "如果把 mid 固定住，这一步真正要确认的还是哪件事？",
            [
                "check 到底在验证什么",
                "二分模板先怎么写出来",
                "答案最后怎么更新更顺手",
                "先猜答案会落在哪个区间",
            ],
            "check 到底在验证什么",
            "确认这类桥梁时，关键仍然是先说清“给定答案后要判什么”。",
            "next_step_structure",
        ),
        "greedy_basis": (
            "如果把题目换个小场景，这一步最需要保持不变的是什么？",
            [
                "为什么这个对象要优先选",
                "先按一个顺手的顺序排排看",
                "先把代码写出来试样例",
                "先套一个常见贪心模板",
            ],
            "为什么这个对象要优先选",
            "确认贪心依据时，最关键的是能不能说清“为什么先选它”。",
            "small_scenario_transfer",
        ),
        "enumeration_order": (
            "如果换个问法，这一步最先还是要确定什么？",
            [
                "哪一维必须排在前面",
                "先按代码最好写的顺序枚举",
                "先把答案变量和更新位置准备好",
                "先让样例能跑，再回头改顺序",
            ],
            "哪一维必须排在前面",
            "确认枚举顺序时，最关键的证据仍然是能不能说清谁必须在前。",
            "next_step_structure",
        ),
        "boundary_debug": (
            "如果换成另一个小样例，你最先还是要查哪件事？",
            ["最小边界会不会先出错", "先把整个算法重写一遍", "先把数组全都开大", "先忽略最小情况"],
            "最小边界会不会先出错",
            "确认调试这一步时，最有价值的证据仍然是你会不会先看最小边界。",
            "small_scenario_transfer",
        ),
        "implementation_debug": (
            "如果把这一步换个说法，你最先还是要查什么？",
            ["默认前提在最小情况还成不成立", "先换一种算法重写", "先把循环和数组都放大试试", "先调大常量再看"],
            "默认前提在最小情况还成不成立",
            "确认实现调试这一步时，关键仍然是先检查默认前提会不会先被打破。",
            "incorrect_reason_check",
        ),
    }

    question_text, options, correct_answer, explanation, confirm_focus = mapping.get(
        focus,
        (
            "如果换个问法，这一步你最先还是要说清什么？",
            ["你具体卡住的是哪一步", "先跳到完整做法", "先猜它像哪类题", "先只看答案格式"],
            "你具体卡住的是哪一步",
            "确认这类桥梁时，关键还是先把真正卡住的那一小步说清楚。",
            "object_recognition",
        ),
    )
    return {
        "mode": "quiz",
        "quiz_type": "choice",
        "question_text": question_text,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "bridge_feedback": _default_bridge_feedback(correct_answer, review_context),
        "target_bridge": target_bridge,
        "difficulty_level": "confirm",
        "meta": {
            "difficulty_level": "confirm",
            "confirm_mode": "abstract",
            "confirm_focus": confirm_focus,
            "previous_quiz_type": (previous_quiz or {}).get("quiz_type", ""),
            "previous_question": (previous_quiz or {}).get("question_text", ""),
            "soft_priority": "prefer_small_scenario_transfer_when_feasible",
        },
    }


def generate_bridge_quiz(review_context: dict, previous_quiz: dict | None = None, quiz_role: str = QUIZ_ROLE_MAIN) -> dict:
    """根据当前 review 生成主 quiz / follow-up / confirm / 更简单 quiz。"""
    error_layer = review_context.get("error_layer", "insufficient")
    if error_layer == "insufficient":
        level = (
            "main"
            if quiz_role == QUIZ_ROLE_MAIN
            else ("followup" if quiz_role == QUIZ_ROLE_FOLLOWUP else ("confirm" if quiz_role == QUIZ_ROLE_CONFIRM else "easier"))
        )
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": "当前这一步还不适合继续出题，应该先换一种方式把卡点说清楚。",
            "target_bridge": "",
            "difficulty_level": level,
            "meta": {"difficulty_level": level},
        }

    focus = _detect_quiz_focus(review_context)
    target_bridge = _default_target_bridge(review_context, focus)

    if quiz_role == QUIZ_ROLE_MAIN:
        payload = _main_quiz_payload(review_context, focus, target_bridge)
    elif quiz_role == QUIZ_ROLE_FOLLOWUP:
        payload = _followup_quiz_payload(review_context, focus, target_bridge, previous_quiz)
    elif quiz_role == QUIZ_ROLE_CONFIRM:
        payload = _confirm_quiz_payload(review_context, focus, target_bridge, previous_quiz)
    else:
        payload = _easier_quiz_payload(review_context, focus, target_bridge, previous_quiz)

    if payload.get("mode") == "quiz":
        payload["bridge_feedback"] = payload.get("bridge_feedback") or _default_bridge_feedback(
            payload.get("correct_answer", ""),
            review_context,
        )
        payload = _normalize_quiz_contract(payload, review_context, focus, quiz_role)
    return payload


def transfer_signal_has_explicit_trigger(signal_text: str, key_bridge: str) -> bool:
    signal = (signal_text or "").strip()
    bridge = (key_bridge or "").strip()
    if not signal:
        return False
    if any(term in signal for term in GENERIC_TRANSFER_SIGNALS):
        return False
    has_trigger = any(term in signal for term in TRANSFER_SIGNAL_TRIGGER_TERMS)
    if not has_trigger:
        return False

    bridge_tokens = [
        token
        for token in re.split(r"[，。；、：\s]+", bridge)
        if len(token) >= 2
    ]
    relation_markers = ("因为", "所以", "说明", "对应", "先", "要", "意味着")
    if any(token in signal for token in bridge_tokens[:4]):
        return True
    return any(marker in signal for marker in relation_markers)


def generate_confirm_quiz_from_pool(
    review_context: dict,
    structure_type: str,
    bridge_note: str,
    problem_url: str,
) -> dict:
    target_bridge = (review_context.get("key_bridge") or review_context.get("next_step") or "").strip()
    bridge_hint = (bridge_note or target_bridge or "先确认这道题的核心结构桥").strip()
    return {
        "mode": "quiz",
        "quiz_type": "choice",
        "question_text": f"这道迁移确认题已经换了题面，但核心桥不变。面对 `{structure_type}` 这类结构时，你最该先确认哪一步？",
        "options": [
            {"value": "A", "label": bridge_hint},
            {"value": "B", "label": "先背这类题的固定代码模板，再把题面往上套"},
            {"value": "C", "label": "先忽略结构，只看题面像不像你刚做过的原题"},
        ],
        "correct_answer": "A",
        "explanation": "confirm 的目标不是再背一道同类题，而是先认出“虽然题面换了，但核心桥还在”。",
        "bridge_feedback": f"这一步真正要确认的是：{bridge_hint}",
        "distractor_feedback": {
            "B": "这会把迁移题退化成背模板，学生可能会做表面题，但没有真的认出结构桥。",
            "C": "confirm 要验证的是“表面不同、结构相同”，不能只靠题面熟悉感。",
        },
        "target_bridge": target_bridge,
        "difficulty_level": "confirm",
        "meta": {
            "difficulty_level": "confirm",
            "confirm_mode": "fixed_pool",
            "structure_type": structure_type,
            "problem_url": problem_url,
        },
    }


def generate_remedy_explanation(review_context: dict, remedy_action: str) -> dict:
    """生成解释类补救内容，优先走 clarify/remedy prompt，失败时回退到 deterministic 文案。"""
    error_layer = review_context.get("error_layer", "insufficient")
    if error_layer == "insufficient":
        messages = [
            {"role": "system", "content": _build_clarify_system_prompt()},
            {"role": "user", "content": _build_clarify_user_prompt(review_context, remedy_action)},
        ]
    else:
        deterministic = _generate_bridge_specific_remedy_explanation(review_context, remedy_action)
        if deterministic:
            return deterministic

    if error_layer == "insufficient":
        pass
    elif (review_context.get("remedy_count") or 0) >= 1:
        messages = [
            {"role": "system", "content": _build_bottom_out_system_prompt(remedy_action)},
            {"role": "user", "content": _build_bottom_out_user_prompt(review_context, remedy_action)},
        ]
    else:
        messages = [
            {"role": "system", "content": _build_remedy_system_prompt(remedy_action)},
            {"role": "user", "content": _build_remedy_user_prompt(review_context, remedy_action)},
        ]

    llm_success, content, _telemetry = _call_llm(messages)
    if llm_success:
        parsed = _parse_remedy_explanation_payload(content)
        if parsed:
            return {
                "remedy_type": "explain",
                "remedy_action": remedy_action,
                **parsed,
            }

    return _generate_remedy_explanation_fallback(review_context, remedy_action)


def _parse_remedy_explanation_payload(content: str) -> dict | None:
    try:
        parsed = json.loads(content)
    except Exception:
        return None

    remedy_text = str(parsed.get("remedy_text", "")).strip()
    micro_action = str(parsed.get("micro_action", "")).strip()
    if not remedy_text or not micro_action:
        return None

    return {
        "remedy_text": remedy_text[:400],
        "visual_hint": str(parsed.get("visual_hint", "")).strip()[:240],
        "micro_action": micro_action[:160],
    }


def _generate_bridge_specific_remedy_explanation(review_context: dict, remedy_action: str) -> dict | None:
    focus = _detect_quiz_focus(review_context)
    if focus not in {
        "transition_design",
        "state_design",
        "check_condition",
        "complexity_fit",
        "method_selection",
        "shared_prefix_merging",
        "lazy_semantics",
        "left_bound_update",
        "constraint_modeling",
        "tree_path_difference",
    }:
        return None

    bottleneck_text = (review_context.get("bottleneck_text") or "").strip()
    main_block = (review_context.get("main_block") or "").strip()
    anchor = bottleneck_text[:60] if bottleneck_text else (main_block[:60] if main_block else "")
    opening = f"你刚才卡住的是：{anchor}。" if anchor else ""
    if (review_context.get("remedy_count") or 0) >= 1:
        opening += " 这次我们不再绕整题，只盯住这一个最小事实。"

    payload_map = {
        "transition_design": {
            "remedy_text": "这里最容易误会的是：转移式像凭感觉试出来的。真正要站稳的是：先把当前状态可能从哪些更小状态转来想全，再由这些来源写出转移。",
            "visual_hint": "当前格 (i,j)\n<- 上一层 (i-1,j-1)\n<- 上一层 (i-1,j)\n再写转移式",
            "micro_action": "你现在先只回答一句：当前状态可能从哪几个更小状态转来？",
        },
        "state_design": {
            "remedy_text": "这里最容易误会的是：状态格只是代码里随便起的一个变量。真正要站稳的是：这一格在回答哪一个更小的子问题，它记录的是这个子问题的结果。",
            "visual_hint": "先看这一格在回答什么小问题\n-> 再说这一格存什么\n-> 后面才知道怎么转移",
            "micro_action": "你现在先只回答一句：dp[x][y] 这一格到底在记录哪一个子问题的结果？",
        },
        "check_condition": {
            "remedy_text": "这里最容易误会的是：check(mid) 要直接把答案算出来。真正要站稳的是：它只负责回答一个小问题，当前这个 mid 到底可不可行。比如 `check(5)=true`，只说明“最小跳跃距离至少为 5”这件事当前还能做到。",
            "visual_hint": "check(5)=true\n-> 只说明 5 可行\n-> 二分再决定往哪边缩",
            "micro_action": "你现在先只说一句：check(mid) 返回 true，到底说明了什么？",
        },
        "complexity_fit": {
            "remedy_text": "这里最容易误会的是：先报一个更高级的方法名就行。真正要站稳的是：先把会一起变大的量圈出来，估一眼总量级，再判断双层枚举会不会先炸。",
            "visual_hint": "先看数据范围\n-> 哪些量一起变大\n-> 总量级会不会先炸",
            "micro_action": "你现在先只回答一句：这题更该先判断规模能不能过，还是先报方法名？",
        },
        "method_selection": {
            "remedy_text": "这里最容易误会的是：先凭题感猜一个方法名。真正要站稳的是：先回到题面，指出哪一个结构信号真的在支持这个方法。",
            "visual_hint": "题面对象/操作/限制\n-> 哪个是真线索\n-> 这条线索支持什么方法",
            "micro_action": "你现在先指出题面里一个真正支持当前方法的结构信号。",
        },
        "shared_prefix_merging": {
            "remedy_text": "这里最容易误会的是：trie 像在神奇地把答案背出来。真正要站稳的是：公共前缀先合在一起以后，查询时就不用重看所有消息，只沿当前前缀路径往下走。比如消息有 `101`、`100`、`11`，前两条前面两位一样，就值得先把这段相同开头合在一起看。",
            "visual_hint": "101\n100\n11\n前缀 10 先合在一起\n查询时只沿前缀路径走",
            "micro_action": "你现在先只回答一句：为什么查询时只沿当前前缀路径走，就能省掉重看所有消息？",
        },
        "lazy_semantics": {
            "remedy_text": "这里最容易误会的是：lazy 像“代码还没执行完”。真正要站稳的是：lazy 记录的是这段区间已经确定、但还没下传给孩子的信息。比如节点管 `[1,4]`，`lazy=3` 表示这段区间每个数都还欠着 `+3`；如果左儿子长度是 `2`，pushdown 时左儿子的 `sum` 会先加 `3×2`。",
            "visual_hint": "[1,4]\nlazy=3\n左儿长度=2\n-> pushdown: 左儿 sum += 3×2",
            "micro_action": "你现在先只回答一句：lazy 标记到底记录的是哪一类信息？",
        },
        "left_bound_update": {
            "remedy_text": "这里最容易误会的是：一看到 `a[mid] == x` 就能立刻停。真正要站稳的是：如果目标是最左位置，mid 还可能就是答案，所以要先保留 mid，再继续往左找。",
            "visual_hint": "[1,2,2,2,3]\na[mid] == 2\n-> mid 先留作候选\n-> r = mid 继续往左缩",
            "micro_action": "你现在先只回答一句：为什么 `a[mid] == x` 时还不能马上把 mid 丢掉？",
        },
        "constraint_modeling": {
            "remedy_text": "这里最容易误会的是：先凭感觉把条件一条条硬拼在一起。真正要站稳的是：先把每条限制都翻译成同一种关系，再看这些关系是谁限制谁、能不能放进同一张图里。",
            "visual_hint": "A <= B + c\nB <= C + d\n先统一成同一种关系\n-> 再看谁限制谁",
            "micro_action": "你现在先只指出一句：这题里的限制该先统一翻成哪一类关系？",
        },
        "tree_path_difference": {
            "remedy_text": "这里最容易误会的是：树剖/LCA 这个方法名本身会把 P3128 做完。真正要站稳的是：LCA 只是帮你找到路径分叉点；每条 s 到 t 的路径贡献要先压成 s、t、LCA 和 LCA 父亲附近的差分标记，最后 DFS 子树汇总，才还原出每个点被经过了多少次。",
            "visual_hint": "s -> t 路径\ns += 1, t += 1\nlca -= 1, parent(lca) -= 1\nDFS 汇总 -> 点经过次数",
            "micro_action": "你现在先只回答一句：为什么这题不是每条路径逐点加，而是先端点/LCA 打标记？",
        },
    }
    selected = payload_map[focus]
    if focus == "method_selection":
        focus_text = " ".join(
            str(part or "")
            for part in (
                review_context.get("problem_title"),
                review_context.get("problem_context"),
                review_context.get("bottleneck_text"),
                review_context.get("key_bridge"),
            )
        )
        if _contains_any(focus_text, ("trie", "前缀", "拦截串", "消息")):
            selected = {
                **selected,
                "remedy_text": "这里最容易误会的是：先凭题感猜一个方法名。真正要站稳的是：先回到题面，看见“很多消息有相同开头，而且还要反复按前缀查”这个信号。比如消息有 `101`、`100`、`11`，前两条前面两位一样，这就是一个能看见的局部结构。先抓住这个信号，下一步你才会自然想到：这些相同开头值不值得先合在一起看。",
                "visual_hint": "101\n100\n11\n前两条前面两位一样\n-> 这就是“相同开头”的题面信号\n-> 这是支持 trie 的题面信号",
                "micro_action": "你现在先指出一句：题面里哪个“相同开头”信号在支持 trie？",
            }
    if focus == "shared_prefix_merging":
        focus_text = " ".join(
            str(part or "")
            for part in (
                review_context.get("problem_title"),
                review_context.get("problem_context"),
                review_context.get("bottleneck_text"),
                review_context.get("main_block"),
                review_context.get("key_bridge"),
                review_context.get("next_step"),
            )
        )
        if _is_trie_node_count_context(focus_text):
            selected = {
                **selected,
                "remedy_text": "这里最容易误会的是：节点上随便记一个数字就够了。真正要站稳的是：经过次数表示有多少消息经过当前前缀节点，结束次数表示有多少消息正好在这里结束。比如消息有 `101`、`100`、`11`，前两条都会经过前缀 `10` 这个节点，所以它的经过次数至少是 `2`。这样查询时，你才知道为什么可以沿路径看经过次数和结束次数，而不是把所有消息重新翻一遍。",
                "visual_hint": "101\n100\n11\n前缀 10 这个节点\n-> 经过次数至少是 2\n-> 结束次数另算",
                "micro_action": "你现在先只回答一句：经过次数表示的到底是哪一类信息？",
            }
    selected = _augment_remedy_with_external_snippets(focus, selected)
    return {
        "remedy_type": "explain",
        "remedy_action": remedy_action,
        "remedy_text": f"{opening} {selected['remedy_text']}".strip(),
        "visual_hint": selected["visual_hint"],
        "micro_action": selected["micro_action"],
    }


def _generate_remedy_explanation_fallback(review_context: dict, remedy_action: str) -> dict:
    """当前补救链路的 deterministic 兜底，确保 prompt split 失败时学习流不崩。"""
    error_layer = review_context.get("error_layer", "insufficient")
    key_bridge = review_context.get("key_bridge") or ""
    main_block = review_context.get("main_block") or ""
    bottleneck_text = (review_context.get("bottleneck_text") or "").strip()
    bottleneck_anchor = bottleneck_text[:60] if bottleneck_text else (main_block[:60] if main_block else "")

    if error_layer == "insufficient":
        return {
            "remedy_type": "explain",
            "remedy_action": remedy_action,
            "remedy_text": f"你刚才真正卡住的是：{bottleneck_anchor or '还没把断点说清楚'}。你现在最需要的不是继续猜方法，而是先把这题到底求什么、你试过什么、你具体断在了哪一步说清楚。",
            "visual_hint": "题目求什么\n-> 你试到哪一步\n-> 你具体卡在哪",
            "micro_action": "你现在先用一句话写：题目要我求什么；再写一句：我试到哪一步停住了。",
        }

    if remedy_action == REMEDY_ACTION_SMALLER_EXAMPLE:
        smaller_examples = {
            "reading": "先拿题目里的最小样例，只看输入和输出，别急着想算法，先说清楚题目到底要你求什么。",
            "method": "先别想整题，你只看一个最小样例，想一想：如果用这个方法，第一步到底在处理什么。",
            "modeling": "先别想整题，把题目里最核心的两个对象单独写出来，再看它们之间到底是什么关系。",
            "core_design": "先拿一个很小的样例，只盯住这一小步，看这里的每个量分别表示什么。",
            "implementation": "先拿最小边界样例，只检查这一处访问或判断在最小情况下会不会出错。",
        }
        text = smaller_examples.get(error_layer, "先拿一个最小样例，只盯住这一小步，不要一下看整题。")
    elif remedy_action == REMEDY_ACTION_DYNAMIC:
        dynamic_examples = {
            "reading": "你现在更像是还没把题目要求和限制分开。先别想算法，先把“求什么”和“限制什么”分成两行写出来。",
            "method": "你现在不是完全不会，而是还没看清这题为什么该用这个方法。先问自己：这个方法到底解决了题目的哪一个核心条件。",
            "modeling": "你现在卡的不是代码，而是还没把题目里的对象和关系说清楚。先找出“谁”和“谁之间发生了什么”。",
            "core_design": "你现在已经知道大方向了，但这一步里每个量到底表示什么还没定稳。先把这一步每个量的意思单独写出来。",
            "implementation": "你现在更像是思路差不多了，但这一步代码还没落稳。先只检查这一处默认前提在最小情况还成不成立。",
        }
        text = dynamic_examples.get(error_layer, "我们先别扩展整题，只盯住你现在最卡的这一小步。")
    else:
        rephrase_examples = {
            "reading": "先别想算法，你现在更需要先把题目到底要你算什么看清楚。",
            "method": "先别背模板，你现在更需要搞清楚为什么这题该用这个方法。",
            "modeling": "先别急着写公式或代码，你现在更需要先把题目里的对象和关系说清楚。",
            "core_design": "先别一下把整题都推完，你现在更需要先看清这一步里每个量到底表示什么。",
            "implementation": "先别急着重写整题，你现在更需要先检查这一步在最小情况会不会出问题。",
        }
        text = rephrase_examples.get(error_layer, main_block or "我们先只讲这一小步。")

    visual_hint = ""
    if remedy_action == REMEDY_ACTION_SMALLER_EXAMPLE:
        visual_hint = "先只盯这一小块\n-> 把对象写出来\n-> 再看它们的关系"
    elif remedy_action == REMEDY_ACTION_DYNAMIC:
        visual_hint = "先看对象\n再看关系\n最后只做这一小步"
    if (review_context.get("remedy_count") or 0) >= 1:
        visual_hint = "当前题最小例子\n左边这一端 -> 接谁更远\n右边这一端 -> 接谁更远"

    remedy_prefix = f"你刚才卡住的是：{bottleneck_anchor}。" if bottleneck_anchor else ""
    return {
        "remedy_type": "explain",
        "remedy_action": remedy_action,
        "remedy_text": f"{remedy_prefix}{text}".strip(),
        "visual_hint": visual_hint,
        "micro_action": (review_context.get("next_step") or "你现在先只盯住这一小步，不要一下看完整题。")[:120],
    }


def generate_review(
    problem_title: str,
    oj_source: str,
    completion_status: str,
    bottleneck_text: str,
    error_types: list,
    reflection: str = None,
    problem_context: str = None,
    problem_tags: list | None = None,
    chat_context_summary: str | None = None,
    problem_card: dict | None = None,
    submission_result: str = None,
    student_code: str = None,
    draft_callback=None,
    handoff_payload: dict | None = None,
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

    submission_result = (submission_result or "unknown").strip().lower()

    # 完成状态中文映射
    status_map = {
        "independent": "独立完成",
        "hinted": "需要提示",
        "editorial": "看题解",
        "unfinished": "未完成",
    }
    status_text = status_map.get(completion_status, completion_status)

    # 提交结果中文映射
    result_map = {
        "not_submitted": "尚未提交",
        "wa": "WA（答案错误）",
        "tle": "TLE（超时）",
        "re": "RE（运行错误）",
        "ce": "CE（编译错误）",
        "unknown": "不确定",
    }
    submission_text = result_map.get(submission_result, "")
    allow_algorithm_name = completion_status == "editorial"

    mode = _detect_review_mode(completion_status, submission_result)
    system_prompt = _build_normal_review_system_prompt(mode=mode, handoff_payload=handoff_payload)
    user_prompt = _build_review_user_prompt(
        problem_title=problem_title,
        oj_source=oj_source,
        status_text=status_text,
        bottleneck_text=bottleneck_text,
        error_types=error_types,
        reflection=reflection,
        problem_context=problem_context,
        problem_tags=problem_tags,
        chat_context_summary=chat_context_summary,
        problem_card=problem_card,
        submission_text=submission_text,
        student_code=student_code,
        handoff_payload=handoff_payload,
    )

    # 调用 LLM
    llm_success, content, telemetry = _call_llm(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        chunk_callback=draft_callback,
    )

    if not llm_success:
        return {
            "ok": False,
            "kind": "llm_unavailable",
            "message": "AI 复盘服务暂时不可用，你的打卡已保存，请稍后查看或联系老师",
            "telemetry": telemetry,
        }

    # 解析结果
    review = _parse_review(content)
    review = _guard_review_against_topic_drift(
        review,
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
        error_types=error_types,
    )
    review = _guard_review_against_overclaim(
        review,
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
        error_types=error_types,
    )
    review = _guard_teacher_guidance(
        review,
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
        error_types=error_types,
    )
    review = _guard_review_bridge_stability(
        review,
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
        error_types=error_types,
    )
    bridge_consistency_focus = _detect_quiz_focus(
        {
            "error_layer": review.get("error_layer", "insufficient"),
            "core_design_subtags": review.get("core_design_subtags") or [],
            "problem_title": problem_title,
            "problem_context": problem_context or "",
            "bottleneck_text": bottleneck_text,
            "error_types": error_types or [],
            "main_block": review.get("main_block", ""),
            "key_bridge": review.get("key_bridge", ""),
            "next_step": review.get("next_step", ""),
            "transfer_signal": review.get("transfer_signal", ""),
        }
    )
    review = _guard_review_bridge_consistency(
        review,
        focus=bridge_consistency_focus,
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
    )
    review = _guard_mst_clustering_review(
        review,
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
    )
    review = _guard_review_for_insufficient(
        review,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
        error_types=error_types,
        reflection=reflection,
        submission_result=submission_result,
        student_code=student_code,
    )
    review = _guard_review_against_meta_knowledge(
        review,
        problem_title=problem_title,
        problem_context=problem_context,
        bottleneck_text=bottleneck_text,
    )
    review = _simplify_student_language(review)
    bridge_route_meta = _resolve_bridge_decision(
        {
            "problem_title": problem_title,
            "problem_context": problem_context or "",
            "bottleneck_text": bottleneck_text,
            "error_types": error_types or [],
            "problem_tags": problem_tags or [],
            "error_layer": review.get("error_layer", "insufficient"),
            "error_layer_confidence": review.get("error_layer_confidence", "low"),
            "core_design_subtags": review.get("core_design_subtags") or [],
            "problem_focus": review.get("problem_focus", ""),
            "main_block": review.get("main_block", ""),
            "key_bridge": review.get("key_bridge", ""),
            "visual_hint": review.get("visual_hint", ""),
            "guided_walkthrough": review.get("guided_walkthrough", ""),
            "try_now": review.get("try_now", ""),
            "next_step": review.get("next_step", ""),
            "transfer_signal": review.get("transfer_signal", ""),
        }
    )
    review_quality_flags = _detect_review_quality_flags(review, allow_algorithm_name=allow_algorithm_name)

    return {
        "ok": True,
        "kind": "success",
        "review": review,
        "review_quality_flags": review_quality_flags,
        "bridge_route_meta": bridge_route_meta,
        "telemetry": telemetry,
        "message": "复盘生成成功"
    }


def generate_problem_analysis(
    problem_title: str,
    compact_card: dict,
    difficulty: int | None = None,
) -> dict:
    system_prompt = """你是一位经验丰富的 NOI 信息学竞赛教练。请根据题目的压缩题目卡，生成一张结构化教学分析卡。

请输出一个且仅一个 JSON 对象，不要输出 Markdown 代码块，不要输出解释前缀。

JSON 格式：
{{
  "summary": "一句话概括题目核心，<=60字",
  "strategy_types": ["必须从受控词表中选，最多2个"],
  "knowledge_points": ["2-4个更细粒度知识点"],
  "common_mistakes": ["3-5个真实易错点"]
}}

strategy_types 只能从以下词表中选择，不能自造新词：
["simulation","greedy","binary_search","two_pointer","prefix_diff","sort","divide_conquer","monotone_structure","stack_queue","heap","dsu","bit","segment_tree","hash","trie","linked_list","dp_linear","dp_knapsack","dp_interval","dp_tree","dp_bitmask","dp_digit","graph_traversal","graph_shortest","graph_mst","graph_toposort","graph_constraint","graph_bipartite","graph_scc","tree_lca","tree_hld","math_number","math_combinatorics","math_fast_power","math_game","string_kmp","string_hash","composite","other"]

要求：
1. summary 只写题目最核心的任务和关键观察，不要写题解。
2. strategy_types 只写主策略，不要把实现小技巧也放进去。
3. knowledge_points 比 algo_tags 更细，但不要过细到代码技巧。
4. common_mistakes 必须是学生真实会犯的错，不能写空话。
5. 如果某个技巧只是实现细节（例如倒序扫描、滚动数组），优先放进 knowledge_points，不放进 strategy_types。
"""

    user_prompt = f"""题目标题：{problem_title}
题目难度：{difficulty if difficulty is not None else '未知'}
压缩题目卡：{json.dumps(compact_card, ensure_ascii=False, sort_keys=True)}
"""

    ok, content, telemetry = _call_llm([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ])
    if not ok:
        return {
            "ok": False,
            "message": "problem_analysis LLM unavailable",
            "telemetry": telemetry,
        }

    json_block = _extract_json_block(content) or content
    try:
        payload = json.loads(_sanitize_json_like_text(json_block))
    except Exception:
        return {
            "ok": False,
            "message": "problem_analysis JSON parse failed",
            "telemetry": telemetry,
        }

    summary = str(payload.get("summary") or "").strip()
    strategy_types = payload.get("strategy_types") or []
    knowledge_points = payload.get("knowledge_points") or []
    common_mistakes = payload.get("common_mistakes") or []

    if not summary:
        return {
            "ok": False,
            "message": "problem_analysis summary missing",
            "telemetry": telemetry,
        }

    allowed_strategy_types = {
        "simulation", "greedy", "binary_search", "two_pointer", "prefix_diff", "sort",
        "divide_conquer", "monotone_structure", "stack_queue", "heap", "dsu", "bit",
        "segment_tree", "hash", "trie", "linked_list", "dp_linear", "dp_knapsack",
        "dp_interval", "dp_tree", "dp_bitmask", "dp_digit", "graph_traversal",
        "graph_shortest", "graph_mst", "graph_toposort", "graph_constraint",
        "graph_bipartite", "graph_scc", "tree_lca", "tree_hld", "math_number",
        "math_combinatorics", "math_fast_power", "math_game", "string_kmp",
        "string_hash", "composite", "other",
    }
    normalized_strategy_types = []
    for item in strategy_types:
        text = str(item).strip()
        if text in allowed_strategy_types and text not in normalized_strategy_types:
            normalized_strategy_types.append(text)

    return {
        "ok": True,
        "analysis": {
            "summary": summary[:120],
            "strategy_types": normalized_strategy_types[:2],
            "knowledge_points": [str(item).strip() for item in knowledge_points if str(item).strip()][:4],
            "common_mistakes": [str(item).strip() for item in common_mistakes if str(item).strip()][:5],
        },
        "telemetry": telemetry,
    }


if __name__ == "__main__":
    # 测试校验函数
    print("=== 测试校验函数 ===")
    print(validate_bottleneck("不会"))  # 应该失败
    print(validate_bottleneck("我不知道怎么做这道题"))  # 应该失败（<30字且含无效词）
    print(validate_bottleneck("我知道是背包问题，但不确定状态转移方程怎么写"))  # 应该通过
