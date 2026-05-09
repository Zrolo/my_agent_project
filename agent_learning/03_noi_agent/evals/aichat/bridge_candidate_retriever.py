from __future__ import annotations

from typing import Iterable


UNKNOWN_FOCUS_CANDIDATE = {
    "focus_id": "unknown",
    "bridge_family": "unknown_or_not_applicable",
    "description": "没有候选 focus 能稳定覆盖当前轮次，或者证据不足。",
    "aliases": [],
    "score": 0,
    "matched_terms": [],
}


TOPIC_RULES = [
    {
        "topic_l1": "binary_search",
        "topic_l2": "binary_search_answer",
        "keywords": ["二分", "binary", "check", "mid", "可行", "单调", "左边界", "右边界"],
    },
    {
        "topic_l1": "dp",
        "topic_l2": "dp_state_transition",
        "keywords": ["dp", "状态", "转移", "背包", "区间dp", "区间 dp", "滚动数组", "递推"],
    },
    {
        "topic_l1": "tree",
        "topic_l2": "tree_path_or_tree_dp",
        "keywords": ["树", "lca", "dfs", "子树", "树上差分", "树形dp", "树形 dp"],
    },
    {
        "topic_l1": "graph",
        "topic_l2": "graph_shortest_path_or_dag",
        "keywords": ["图", "最短路", "dijkstra", "拓扑", "dag", "relax", "边权"],
    },
    {
        "topic_l1": "data_structure",
        "topic_l2": "data_structure_operation",
        "keywords": ["线段树", "lazy", "堆", "优先队列", "并查集", "trie", "单调栈", "栈", "队列"],
    },
    {
        "topic_l1": "string",
        "topic_l2": "string_matching",
        "keywords": ["kmp", "next", "前缀函数", "字符串", "匹配", "前后缀"],
    },
    {
        "topic_l1": "greedy",
        "topic_l2": "greedy_correctness",
        "keywords": ["贪心", "交换", "排序", "局部最优", "反例"],
    },
    {
        "topic_l1": "search",
        "topic_l2": "state_search",
        "keywords": ["bfs", "dfs", "搜索", "钥匙", "状态压缩", "状压", "回溯"],
    },
    {
        "topic_l1": "math",
        "topic_l2": "combinatorics_or_mod",
        "keywords": ["组合", "取模", "模", "乘法溢出", "递推式", "c("],
    },
    {
        "topic_l1": "implementation",
        "topic_l2": "implementation_boundary",
        "keywords": ["下标", "边界", "初始化", "long long", "int", "循环", "if", "输入格式"],
    },
    {
        "topic_l1": "debugging",
        "topic_l2": "debugging_evidence",
        "keywords": ["wa", "tle", "re", "错了", "报错", "样例不过", "调试", "反例"],
    },
]


TOPIC_FOCUS_HINTS = {
    "binary_search": ["check", "binary", "left_bound", "bound", "predicate"],
    "dp": ["state", "transition", "dp", "rolling", "interval", "knapsack"],
    "tree": ["tree", "lca", "dfs", "tree_dp"],
    "graph": ["graph", "dijkstra", "shortest", "relax", "dag", "topological"],
    "data_structure": ["segment", "lazy", "trie", "heap", "union", "monotonic"],
    "string": ["kmp", "prefix", "string"],
    "greedy": ["greedy", "exchange"],
    "search": ["bfs", "dfs", "search", "state"],
    "math": ["modular", "combinatorial", "math"],
    "implementation": ["boundary", "loop", "data_type", "initialization", "io", "condition"],
    "debugging": ["debug", "counterexample", "tle", "wa"],
}

FOCUS_DIRECT_HINTS = {
    "state_design": ["状态", "表示什么", "每一格", "dp[", "数组含义", "维度"],
    "transition_design": ["转移", "转过来", "从哪里", "从哪些", "来源", "情况转", "状态转"],
    "check_condition": ["check", "true", "false", "判定", "可行", "条件"],
    "binary_search_bound_direction": ["左边界", "右边界", "l r", "边界更新", "收左", "收右"],
    "lazy_semantics": ["lazy", "懒标记", "还没做", "pushdown", "下传"],
    "method_selection": ["是不是", "不确定", "方向", "该用", "用什么", "方法", "题型", "算法"],
    "greedy_basis": ["贪心", "结束早", "不会影响", "为什么这样", "交换", "反例"],
    "enumeration_order": ["倒着枚举", "正着枚举", "枚举", "更新顺序", "容量", "顺序"],
    "complexity_fit": ["两层循环", "数据范围", "会不会过", "复杂度", "1e5", "1e6", "n 到"],
    "union_find_operation_mapping": ["并查集", "合并", "集合", "代表元", "union", "unite", "find", "连通"],
    "heap_push_pop_mapping": ["堆", "优先队列", "push", "pop", "取当前最小", "取最小", "合并"],
    "topological_zero_indegree_reason": ["拓扑", "入度为 0", "入度为0", "入度", "前置", "先做", "依赖"],
}


def _normalize_text(*parts: object) -> str:
    return " ".join(str(part or "").lower() for part in parts)


def _matched_keywords(text: str, keywords: Iterable[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword.lower() in text]


def retrieve_algorithm_topic_candidates(
    *,
    student_message: str,
    problem_context: str | dict | None = None,
    limit: int = 5,
) -> list[dict]:
    text = _normalize_text(student_message, problem_context)
    candidates = []
    for rule in TOPIC_RULES:
        matched = _matched_keywords(text, rule["keywords"])
        if not matched:
            continue
        score = len(matched)
        if rule["topic_l1"] in {"binary_search", "dp"}:
            score += 0.25
        candidates.append(
            {
                "topic_l1": rule["topic_l1"],
                "topic_l2": rule["topic_l2"],
                "score": round(score, 3),
                "matched_terms": matched[:8],
            }
        )
    candidates.sort(key=lambda item: (-item["score"], item["topic_l1"], item["topic_l2"]))
    if not candidates:
        candidates.append(
            {
                "topic_l1": "unknown",
                "topic_l2": "unknown",
                "score": 0,
                "matched_terms": [],
            }
        )
    return candidates[: max(1, limit)]


def _focus_text(item: dict) -> str:
    aliases = item.get("aliases") or []
    if not isinstance(aliases, list):
        aliases = []
    return _normalize_text(
        item.get("focus_id", ""),
        item.get("bridge_family", ""),
        item.get("description", ""),
        " ".join(str(alias) for alias in aliases),
    )


def _topic_focus_boost(item: dict, topic_l1_values: set[str]) -> tuple[float, list[str]]:
    focus_text = _focus_text(item)
    matched_hints = []
    for topic_l1 in topic_l1_values:
        for hint in TOPIC_FOCUS_HINTS.get(topic_l1, []):
            if hint in focus_text:
                matched_hints.append(hint)
    return (0.35 * len(set(matched_hints)), sorted(set(matched_hints)))


def _direct_focus_boost(item: dict, text: str) -> tuple[float, list[str]]:
    focus_id = str(item.get("focus_id") or "")
    direct_hints = FOCUS_DIRECT_HINTS.get(focus_id, [])
    matched = _matched_keywords(text, direct_hints)
    return (1.2 * len(set(matched)), sorted(set(matched)))


def retrieve_focus_candidates(
    *,
    student_message: str,
    problem_context: str | dict | None,
    algorithm_topic_candidates: list[dict],
    focus_registry: list[dict] | None,
    limit: int = 5,
) -> list[dict]:
    text = _normalize_text(student_message, problem_context)
    topic_l1_values = {
        str(candidate.get("topic_l1"))
        for candidate in algorithm_topic_candidates or []
        if candidate.get("topic_l1")
    }
    candidates = []
    for item in focus_registry or []:
        if not isinstance(item, dict) or not item.get("focus_id"):
            continue
        focus_terms = [
            str(item.get("focus_id", "")).replace("_", " "),
            str(item.get("focus_id", "")),
            str(item.get("bridge_family", "")),
        ]
        aliases = item.get("aliases") or []
        if isinstance(aliases, list):
            focus_terms.extend(str(alias) for alias in aliases)
        description_words = [
            token
            for token in _focus_text(item).replace("/", " ").replace("-", " ").split()
            if len(token) >= 2
        ]
        focus_terms.extend(description_words[:24])
        matched = _matched_keywords(text, dict.fromkeys(term for term in focus_terms if term))
        topic_boost, topic_hints = _topic_focus_boost(item, topic_l1_values)
        direct_boost, direct_hints = _direct_focus_boost(item, text)
        score = len(matched) + topic_boost + direct_boost
        if score <= 0:
            continue
        candidates.append(
            {
                "focus_id": item["focus_id"],
                "bridge_family": item.get("bridge_family", ""),
                "description": item.get("description", ""),
                "aliases": item.get("aliases") or [],
                "score": round(score, 3),
                "matched_terms": (matched + topic_hints + direct_hints)[:10],
            }
        )
    candidates.sort(key=lambda item: (-item["score"], item["focus_id"]))
    unknown = dict(UNKNOWN_FOCUS_CANDIDATE)
    capped_limit = max(1, limit)
    candidates = candidates[: capped_limit]
    if not any(candidate.get("focus_id") == "unknown" for candidate in candidates):
        if len(candidates) >= capped_limit:
            candidates[-1] = unknown
        else:
            candidates.append(unknown)
    return candidates
