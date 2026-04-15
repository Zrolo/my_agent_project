"""
AI Review Engine - 生成结构化的学习复盘
"""

import os
import json
import re
from pathlib import Path
from openai import OpenAI
from model_config import get_model_candidates, is_model_unavailable_error

_client = None
DEFAULT_REVIEW_MODELS = ("kimi-k2.5",)
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
}
QUIZ_ROLE_MAIN = "main"
QUIZ_ROLE_FOLLOWUP = "followup"
QUIZ_ROLE_REMEDY = "remedy"
QUIZ_ROLE_CONFIRM = "confirm"
STRUCTURAL_QUIZ_FOCI = {
    "state_design",
    "transition_design",
    "check_condition",
    "enumeration_order",
    "greedy_basis",
    "general_modeling",
    "constraint_modeling",
    "boundary_debug",
    "method_selection",
    "data_type",
    "loop_boundary",
    "recursion_structure",
    "complexity_fit",
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


def _build_review_system_prompt(mode: str = "independent_reflect", handoff_payload: dict | None = None) -> str:
    """按 mode 构建 review system prompt。

    Mode → Family 映射（见 _detect_review_mode）：
        failure_diagnosis  — failed_verdict / stuck_bridge / editorial_transfer
        success_reflection — independent_reflect
    """
    base = """你是 NOI 教练。

请根据题目信息、学生卡点和代码片段，输出一次简洁、可执行的复盘。
只输出 JSON，不要输出任何额外解释或 Markdown 代码块。

JSON 必须包含这些字段：
error_tags
error_layer
error_layer_confidence
core_design_subtags
diagnosis
next_action
suggested_topic
main_block
key_bridge
next_step
transfer_signal

字段要求：
1. error_tags：1-3 个中文短词。
2. error_layer：reading|method|modeling|core_design|implementation|insufficient。
3. error_layer_confidence：high|medium|low。
4. core_design_subtags：只有 error_layer=core_design 时可填，值只能是 state_design|transition_design|greedy_basis|check_condition|enumeration_order；否则输出 []。
5. diagnosis：直接指出核心问题，不复述题面。
6. next_action：老师布置的下一步训练。
7. suggested_topic：具体小专题，不要只写大类。
8. main_block：学生具体卡住的那一步。
9. key_bridge：解释“为什么这题能这样做”的关键桥梁。
10. next_step：今天立刻能做的小动作。
11. transfer_signal：下次看到什么题面信号要想到这类做法。

规则：
1. 面向初中生，说人话，短句。
2. 不要空话，不要只报算法名。
3. next_step 必须是 1-2 步内可执行的小动作。
4. 信息不够时用 insufficient + low，不要编造细节。
5. 只有完成状态是“看题解”时，main_block、key_bridge、next_step 才允许有限提算法名；否则只写这题里具体的对象、关系、条件和步骤，不要抽象成方法名或概念名。
6. 所有字段都要填写。
7. 不要在字段内容里使用半角双引号；引用题面词语时直接改写，或不用引号。
8. 优先复用题目里的对象名、条件名、公式名。
9. next_action 和 suggested_topic 优先回到当前题，不要写专项训练、经典题、做3道、变式或拓展。

长度控制：
- diagnosis / main_block / key_bridge：尽量不超过 60 字
- 其他文本字段：尽量不超过 30 字"""

    # family 归属（不发进 prompt，仅供代码阅读定位）：
    #   failure_diagnosis  — failed_verdict / stuck_bridge / editorial_transfer
    #   success_reflection — independent_reflect
    supplements = {
        "failed_verdict": """

本次任务重点：学生提交有明确错误结果（WA/TLE/RE/CE）。
- diagnosis 必须说清这个错误结果对应的具体出错位置或逻辑
- main_block 必须说清是哪一步代码或判断出了问题，优先点名具体判断条件、连接符、代码位置或输出位置
- main_block 不要只写“没想清楚”“组合判断语句”“思路有问题”这类模糊说法
- main_block 不要只写“组合判断语句”，要继续落到哪个条件、哪个连接符或哪一处判断
- next_step 必须是今天可以调试的一个最小动作
- next_action 优先回到当前题，指出先检查哪一处代码、判断或输出
- key_bridge 和 transfer_signal 可以简短，但不能为空
- main_block 只说错误类型（如"且关系写错了""条件判断有问题"）不够，必须同时说明是代码里哪一处写错——点名变量名、条件表达式、判断符号或代码位置中至少一个""",
        "stuck_bridge": """

本次任务重点：学生卡住了，还没完成或需要提示才完成。
- main_block 必须说清学生卡在哪个具体步骤，不能只写"不会建模"
- key_bridge 必须先从题目原文里逐字摘出至少一个名词或条件，不允许改写或概括；再用这个原文词说明为什么这一步是关键
- next_step 同样：必须点名题目里直接出现过的某个对象或条件，不允许用"某变量""某限制""进度"等自造概念替代
- key_bridge 必须点名一个对象、关系、条件或状态含义，说明跨过这一步的关键事实
- next_step 必须是今天立刻可以做的一件小事，优先写手画一次 / 逐条列出 / 手推一轮，并点名当前题里至少一个对象或条件
- next_step 不能只写列出条件、画表格、挑一维；要点名当前题里的对象、条件或状态
- transfer_signal 可以简短，但必须提到一个可观察的题目特征，不要给题面特征加引号，不要只写多个限制条件""",
        "editorial_transfer": """

本次任务重点：学生看了题解，现在要理解和迁移。
- diagnosis 重点说清"为什么这个方法能解决这道题"
- key_bridge 必须包含具体结构或公式，不能只复述算法名
- key_bridge 必须说清这道题里的哪个动作对应算法里的哪个操作（如"合并舰队指令 -> union"、"查询间距 -> 路径压缩时累加偏移量"），不能只说算法能做什么
- transfer_signal 必须说清下次看到什么特征时联想到这类做法
- next_step 只写回到原题的一步验证动作，不写练习题或类比""",
        "independent_reflect": """

本次任务重点：学生独立完成，现在做结构性复盘。
- key_bridge 重点说清"这道题为什么这样做是对的"
- transfer_signal 必须说清触发信号，不能只写"遇到类似题"
- transfer_signal 必须直接引用题目里出现的具体名词或数量关系，不能写算法类型描述
- transfer_signal 里不能出现题目名或题目编号，只能写题面里描述的条件、对象和数量关系
- 错误示范："每个决策点可以选择做多少、后面还有更优选择"、"题目要求最少步数从起点向外扩散"、"每组有上限约束、最小化组数"——这些都是类型模板，不是题面特征
- 正确示范："题目给出若干油站各有单价、油箱容量有上限、要求总费用最小"、"棋盘上马从指定起点按日字走法到达每个格子"、"n 件物品各有重量、每组最多两件且总重量不超过 w"
- next_step 只写当前题的一步验证动作，不写变形和拓展
- main_block 如果没有明显卡点，必须写清这道题的核心决策流程（如"在当前油站决定加多少油"、"从堆里弹出最小元素后更新相邻节点"），不能为空，也不能只写做出来了""",
    }
    prompt = base + supplements.get(mode, supplements["independent_reflect"])
    if handoff_payload and handoff_payload.get("source") == "aichat":
        risk_type = handoff_payload.get("risk_type", "")
        suggested_focus = handoff_payload.get("suggested_focus", "")
        prompt += f"""

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
- 直接给 AC 代码或修改后的整段代码。
"""
    return prompt


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
            lines.append("移交背景：学生已 AC 但表示不理解，AIChat 判断需结构化复盘。")
        elif risk_type == "repeated_stuck_exit":
            lines.append("移交背景：学生在 AIChat 反复卡住，AIChat 判断需退出当前抽象路径，进入结构化复盘。")
        if last_msg:
            lines.append(f"移交前最后一条消息：{last_msg[:200]}")
        if suggested_focus:
            lines.append(f"建议复盘焦点：{suggested_focus}")

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
    candidates = get_model_candidates("NOI_REVIEW_MODELS", DEFAULT_REVIEW_MODELS)

    for idx, model_name in enumerate(candidates):
        for attempt in range(2):
            try:
                request_kwargs = {
                    "model": model_name,
                    "messages": messages,
                    "timeout": LLM_REQUEST_TIMEOUT_SECONDS,
                    "max_completion_tokens": LLM_MAX_TOKENS,
                    "response_format": {"type": "json_object"},
                    "stream": True,
                }
                if "kimi-k2.5" not in model_name.lower():
                    request_kwargs["temperature"] = 0.3

                response = get_client().chat.completions.create(
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
                            for key in ("main_block", "key_bridge", "next_step", "transfer_signal")
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

    for key in ("main_block", "key_bridge", "next_step", "transfer_signal"):
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
        "main_block": _extract_json_style_string(text, "main_block"),
        "key_bridge": _extract_json_style_string(text, "key_bridge"),
        "next_step": _extract_json_style_string(text, "next_step"),
        "transfer_signal": _extract_json_style_string(text, "transfer_signal"),
    }
    return repaired


def _extract_review_draft_preview(text: str) -> dict:
    repaired = _repair_partial_json_review(text)
    preview = {}
    for key in ("main_block", "key_bridge", "next_step", "transfer_signal"):
        value = str(repaired.get(key, "") or "").strip()
        if value:
            preview[key] = value
    return preview


def _backfill_student_guidance(review: dict) -> dict:
    if all(review.get(key) for key in ("main_block", "key_bridge", "next_step", "transfer_signal")):
        return review

    error_layer = review.get("error_layer", "insufficient")
    subtags = review.get("core_design_subtags") or []
    focus = subtags[0] if subtags else error_layer

    guidance_map = {
        "state_design": {
            "main_block": "你不是没想到动态规划，而是还没有先把状态里每一维到底记录什么定稳，所以一写转移就开始混。",
            "key_bridge": "关键是先只保留真正限制决策的量，明确每一维表示什么，再决定哪些信息根本不该进状态。",
            "next_step": "先别急着写公式，只写一句完整的话：`dp[...]` 到底表示什么，再检查有没有多余维度。",
            "transfer_signal": "如果你发现自己一写 DP 就想开很多维，先停下来问：每一维到底在记录什么，哪些量只是比较结果。",
        },
        "transition_design": {
            "main_block": "你不是不会写 DP，而是还没把“选”和“不选”或“从哪几种情况转来”整理完整，所以转移总会漏分支。",
            "key_bridge": "关键不是先背公式，而是先把当前状态可能从哪些上一状态来列全，再写成统一转移。",
            "next_step": "拿一个最小样例，把当前状态的所有来源先列成中文，再对应写成转移式。",
            "transfer_signal": "如果你写出的转移只有一支，先检查是不是漏掉了“不选当前对象”或其他来源情况。",
        },
        "check_condition": {
            "main_block": "你不是不会二分或判定，而是还没有先把 `check` 到底在验证什么条件说清楚。",
            "key_bridge": "关键是先把“答案成立”翻成一句可检验的话，再决定 `check` 里需要维护哪些量。",
            "next_step": "先写一句完整中文：`check(mid)` 返回 true 到底表示什么，再对照代码看有没有偏掉。",
            "transfer_signal": "如果题目在问“这个值行不行”，先把“行”的定义写成一句完整判断条件。",
        },
        "enumeration_order": {
            "main_block": "你不是不会写循环，而是还没想清楚为什么这一维必须先枚举，所以顺序一换就把旧状态覆盖掉了。",
            "key_bridge": "关键是先判断当前转移依赖的是“上一层旧值”还是“本层新值”，再决定枚举顺序。",
            "next_step": "先在纸上标出当前状态依赖哪些旧状态，再反推这一维应该正着枚举还是倒着枚举。",
            "transfer_signal": "如果你一改循环顺序答案就变，先检查转移依赖的是旧值还是刚更新的新值。",
        },
        "constraint_modeling": {
            "main_block": "你不是不会图论，而是还没先把题目里的限制关系整理成统一形式，导致变量、方向和边权都混在一起。",
            "key_bridge": "关键是先把每条限制改写成统一约束，再确认“谁限制谁”和这条边表示什么。",
            "next_step": "把题面条件逐条改写成统一约束，再标出每条约束里谁是被限制的量。",
            "transfer_signal": "如果题目一直在描述多个量之间的大小关系或先后限制，先想能不能整理成统一约束。",
        },
        "general_modeling": {
            "main_block": "你不是完全没思路，而是还没先把题目里的对象和关系写清楚，所以方法一直落不到地上。",
            "key_bridge": "关键是先确定“什么是点、什么是边、什么是状态/对象”，再考虑方法。",
            "next_step": "先只写一行：题目里的对象有哪些，它们之间有什么关系。",
            "transfer_signal": "如果题目表面信息很多，先不要猜算法，先把对象和关系写清楚。",
        },
    }

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
        "main_block": str(parsed.get("main_block", "")).strip(),
        "key_bridge": str(parsed.get("key_bridge", "")).strip(),
        "next_step": str(parsed.get("next_step", "")).strip(),
        "transfer_signal": str(parsed.get("transfer_signal", "")).strip(),
    }

    if review["error_layer"] not in ERROR_LAYERS:
        review["error_layer"] = "insufficient"

    if review["error_layer_confidence"] not in CONFIDENCE_LEVELS:
        review["error_layer_confidence"] = "low"

    review["core_design_subtags"] = _normalize_subtags(
        parsed.get("core_design_subtags", []),
        review["error_layer"],
    )

    if not review["diagnosis"] and fallback_text:
        review["diagnosis"] = fallback_text[:200].strip()
    if not review["next_action"]:
        review["next_action"] = "先补充更具体的卡点过程，再根据当前错误层做针对性训练。"
    if not review["suggested_topic"]:
        review["suggested_topic"] = "先补当前题型对应的基础训练。"

    review = _backfill_student_guidance(review)

    if review["error_layer"] == "insufficient":
        if not review["main_block"]:
            review["main_block"] = "你当前主要卡点还不够清晰，需要补充更多题目信息和尝试过程。"
        if not review["key_bridge"]:
            review["key_bridge"] = "先把题目要求、限制条件和你的思路过程写清楚，系统才能定位关键桥梁。"
        if not review["next_step"]:
            review["next_step"] = "补充题意、思路和具体卡住的位置后，再重新提交复盘。"
        if not review["transfer_signal"]:
            review["transfer_signal"] = '如果你自己也说不清卡点，先写清楚“题目求什么、我试了什么、哪里出错”。'

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
        "main_block": "",
        "key_bridge": "",
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

    main_block_match = re.search(r'(?:你主要卡在哪|main_block)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if main_block_match:
        parsed["main_block"] = main_block_match.group(1).strip()

    key_bridge_match = re.search(r'(?:这题的关键桥梁|key_bridge)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if key_bridge_match:
        parsed["key_bridge"] = key_bridge_match.group(1).strip()

    next_step_match = re.search(r'(?:你现在立刻该做什么|next_step)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
    if next_step_match:
        parsed["next_step"] = next_step_match.group(1).strip()

    transfer_signal_match = re.search(r'(?:下次遇到什么信号要想到它|transfer_signal)[:：]\s*(.+?)(?=\n|$)', text, re.IGNORECASE)
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
    error_layer = review_context.get("error_layer", "insufficient")
    subtags = review_context.get("core_design_subtags") or []
    text = _quiz_text_context(review_context)

    if error_layer == "core_design":
        if _contains_any(text, ("递归", "base case", "结束条件", "停下来", "递归返回", "回溯", "分治", "叶子")):
            return "recursion_structure"
        for subtag in subtags:
            if subtag == "greedy_basis" and not _contains_any(text, ("贪心", "排序", "优先选", "依据")):
                continue
            if subtag in HIGH_RISK_REVIEW_FOCI:
                return subtag
            if subtag in CORE_DESIGN_SUBTAGS:
                return subtag
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
        if _contains_any(text, ("long long", "int", "溢出", "精度", "范围太大", "1e18", "10^18", "double", "取模", "mod")):
            return "data_type"
        if _contains_any(text, ("循环范围", "起点", "终点", "下标", "越界", "1-indexed", "0-indexed", "i <= n", "i < n", "枚举到哪里", "边界错了")):
            return "loop_boundary"
        if _contains_any(text, ("边界", "最小", "n=1", "空区间", "特判")):
            return "boundary_debug"
        return "implementation_debug"

    if error_layer == "method":
        if _contains_any(text, ("复杂度", "O(", "数据范围", "n <=", "n<=", "会不会超时", "TLE", "超时", "能不能过")):
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
        "constraint_modeling": "先把题目里的限制关系写成统一形式",
        "general_modeling": "先把题目里的对象和关系写清楚",
        "state_design": "先确定状态里每一维到底表示什么",
        "transition_design": "先确认转移漏没漏掉一种情况",
        "check_condition": "先想清楚 check 在验证什么",
        "greedy_basis": "先说清楚为什么这个对象要优先选",
        "enumeration_order": "先确定为什么这一维必须先枚举",
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
    fallback = {
        "state_design": "动态规划",
        "transition_design": "动态规划",
        "enumeration_order": "动态规划",
        "check_condition": "判定/二分",
        "greedy_basis": "贪心/排序",
        "general_modeling": "图论建模",
        "constraint_modeling": "差分约束",
        "boundary_debug": "边界/调试",
        "method_selection": "方法判断",
        "data_type": "数据类型/范围",
        "loop_boundary": "循环/边界",
        "recursion_structure": "递归/搜索",
        "complexity_fit": "复杂度判断",
    }
    return fallback.get(focus, "通用结构题")


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
    if focus == "state_design":
        axis, meaning = _state_axis_label(review_context)
        if level == "main":
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

    return None


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
    if focus in STRUCTURAL_QUIZ_FOCI:
        structural_payload = _generate_structural_quiz(
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
    if focus == "method_selection":
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
        return {
            "mode": "fallback_explain",
            "quiz_type": "",
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "fallback_explain": "当前这一步更适合先把“局部决策为什么不破坏后面的结构”讲清楚，而不是出一题容易变成贪心口号的小测。",
            "explanation": "当前这一步更适合先把“局部决策为什么不破坏后面的结构”讲清楚，而不是出一题容易变成贪心口号的小测。",
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

    if focus in STRUCTURAL_QUIZ_FOCI:
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
    """生成解释类补救内容，保持可控而不开放到整题题解。"""
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

    remedy_prefix = f"你刚才卡住的是：{bottleneck_anchor}。" if bottleneck_anchor else ""
    return {
        "remedy_type": "explain",
        "remedy_action": remedy_action,
        "remedy_text": f"{remedy_prefix}{text}".strip(),
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
    system_prompt = _build_review_system_prompt(mode=mode, handoff_payload=handoff_payload)
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
    review_quality_flags = _detect_review_quality_flags(review, allow_algorithm_name=allow_algorithm_name)

    return {
        "ok": True,
        "kind": "success",
        "review": review,
        "review_quality_flags": review_quality_flags,
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
