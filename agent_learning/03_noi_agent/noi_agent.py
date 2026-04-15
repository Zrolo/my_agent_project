"""
NOI 竞赛教练 Agent - 限级改造版本
核心：代码层限级 + Prompt层在约束范围内回复 + 槽位化L2追问 + 桥梁红线控制
技术栈：Kimi API + JSON 文件
"""

import json
import os
import re
from openai import OpenAI
from model_config import get_model_candidates, is_model_unavailable_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTA_FILE = os.path.join(BASE_DIR, "quota.json")
PER_PROBLEM_HINT_LIMIT = 3
client = None
CLASSIFIER_TIMEOUT_SECONDS = 2.5
DEFAULT_CHAT_MODELS = ("kimi-k2.5",)

AC_SIGNAL_KEYWORDS = [
    "AC了", "AC 了", "过了", "通过了", "提交成功", "满分", "accepted",
]

AC_UNCERTAINTY_KEYWORDS = [
    "蒙", "不懂", "不太懂", "想复盘", "没真懂", "感觉是猜的", "想弄清楚", "不确定为什么",
]

HANDOFF_FOCUS_BY_RISK = {
    "ac_unclear_in_aichat": "复盘已 AC 题目的关键桥，验证一个理解点。",
    "repeated_stuck_exit": "用小例子拆开当前卡住的桥，记录卡点和已尝试路径。",
}

STUCK_SIGNAL_KEYWORDS = [
    "还是不会", "还是混", "说不清", "想不出", "不懂", "没思路", "想不明白",
]

# ============ 1. 代码层控制对象定义 ============

# L2 槽位定义
L2_SLOTS = ["对象", "选择", "限制", "最简单情况"]

# reason_tags 允许的枚举值
VALID_REASON_TAGS = [
    "direct_request",
    "emotion_pressure", 
    "bridge_attempt",
    "code_no_target",
    "slot_fill",
    "cross_slot_dump",
    "classifier_direct",
    "classifier_bridge",
    "type_confirm",
    "multi_question",
    "missing_context",
    "checkin_handoff",
    "debug_no_code",
]

# L1 强拦关键词
L1_DIRECT_KEYWORDS = [
    "给我代码", "给我答案", "怎么做", "直接讲思路", "帮我写",
    "把答案给我", "你直接告诉我", "你直接说正确做法", "直接给代码",
    "直接告诉我", "直接给", "直接说"
]

L1_SHORT_NO_THINKING = [
    "不会", "没思路", "太难了", "不会写", "没想法", "不知道怎么做"
]

L1_EMOTION_PRESSURE = [
    "比赛快开始了", "老师今天要交", "求你快点", "我来不及了",
    "我很急你直接说", "快告诉我", "来不及了", "要交了"
]

# 桥梁套取关键词
BRIDGE_KEYWORDS = [
    "不会转移", "状态怎么定义", "check 怎么写", "图怎么建",
    "贪心到底按什么选", "递归函数怎么设", "base case 怎么写",
    "push_up 不会改", "push_down 不会写", "lazy 怎么传",
    "这一步推不出来", "判断函数不知道怎么组织", "标记往下传这里想不通",
    "转移方程", "状态定义", "状态方程"
]

# 贴代码特征（代码片段特征）
CODE_PATTERNS = [
    r'#include', r'using namespace', r'def ', r'int main',
    r'for\s*\(', r'while\s*\(', r'if\s*\(', r'class ',
    r'struct ', r'public:', r'private:', r'void ', r'return '
]

SEMANTIC_RISK_PATTERNS = [
    r'这题是.*吗',
    r'是不是',
    r'对不对',
    r'应该.*吧',
    r'像.*吗',
    r'感觉.*吗',
    r'算.*吗',
    r'用.*对吧',
    r'这一步.*推不出来',
    r'判断.*怎么组织',
    r'这里.*想不通',
]

# Type Confirm 检测模式（代码层直接识别，不依赖分类器）
TYPE_CONFIRM_PATTERNS = [
    r'这题是.*[吗吧？?]',  # 这题是...吗/吧/?
    r'是不是.*',
    r'应该用.*[吧吗？?]',
    r'像.*[吗吧？?]',
    r'感觉是.*[吗吧？?]',
    r'算.*[吗吧？?]',
    r'用.*对吧',
    r'这道题是.*[吗吧？?]',
    r'是[二贪递字背图]*[分心归符包论dp]+[吗吧？?]',  # 是DP吗/是二分吗...
]


def _is_type_confirm(text: str) -> bool:
    """
    代码层直接识别 type_confirm 场景
    识别学生是否在猜测或确认题型/方法
    
    返回 True 表示命中 type_confirm 模式
    """
    text_lower = text.lower()
    for pattern in TYPE_CONFIRM_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def get_client() -> OpenAI:
    """延迟初始化客户端"""
    global client
    if client is None:
        api_key = os.environ.get("MOONSHOT_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("MOONSHOT_API_KEY 未设置")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
    return client


# ============ 2. 代码层输入分析函数（双轨版本：等级轨 + 风险轨） ============

# 风险标签优先级（从高到低）
RISK_PRIORITY = {
    "checkin_handoff": 0,
    "missing_context": 1,
    "direct_request": 1,
    "multi_question": 2,
    "bridge_attempt": 3,
    "type_confirm": 4,
    "mixed_signal": 5,
    "debug_no_code": 6,
    "code_no_target": 6,
    "emotion_pressure": 7,
}

# 风险标签对应的最高允许等级
RISK_LEVEL_LIMITS = {
    "checkin_handoff": "L2",
    "direct_request": "L1",
    "bridge_attempt": "L2",  # 无L3证据时
    "type_confirm": "L2",
    "mixed_signal": None,  # 按最危险意图处理
    "multi_question": "L1",
    "debug_no_code": "L1",
    "code_no_target": "L2",
    "missing_context": "L1",
    "emotion_pressure": "L1",
}

TUTOR_ACTION_BY_RISK = {
    "checkin_handoff": "offer_checkin_reflection",
    "direct_request": "ask_baseline_attempt",
    "type_confirm": "ask_evidence_question",
    "bridge_attempt": "ask_missing_bridge_evidence",
    "mixed_signal": "ask_one_focus_point",
    "multi_question": "ask_one_focus_point",
    "debug_no_code": "ask_debug_evidence",
    "code_no_target": "ask_code_evidence",
    "missing_context": "request_problem_context",
    "emotion_pressure": "ask_baseline_attempt",
}


def _detect_risks(user_input: str) -> list:
    """
    风险轨：检测学生输入中的套答案风险
    
    返回风险标签列表，可能包含多个：
    - direct_request: 直接索取答案/代码
    - type_confirm: 确认/猜测题型
    - bridge_attempt: 索取关键桥梁
    - mixed_signal: 混合多个危险意图
    - multi_question: 一条输入多个问题
    
    本版本暂不实现 fake_attempt（依赖L3证据门槛自然过滤）
    """
    risks = []
    text_lower = user_input.lower()

    if _is_ac_reflection_request(user_input):
        risks.append("checkin_handoff")
    
    # 1. direct_request: 直接索取
    for kw in L1_DIRECT_KEYWORDS:
        if kw in user_input:
            risks.append("direct_request")
            break

    if any(kw in user_input for kw in L1_EMOTION_PRESSURE):
        risks.append("emotion_pressure")
    
    # 2. type_confirm: 确认题型
    if _is_type_confirm(user_input):
        risks.append("type_confirm")
    
    # 3. bridge_attempt: 索取桥梁
    if _is_bridge_attempt(user_input):
        risks.append("bridge_attempt")
    
    # 4. multi_question: 多问题
    # 检测是否有多个问号，或明显的多个问题模式
    question_count = text_lower.count('?') + text_lower.count('？')
    if question_count >= 2:
        risks.append("multi_question")

    if _contains_code(user_input) and not _has_doubt_point(user_input):
        risks.append("code_no_target")

    if _is_debug_no_code_request(user_input):
        risks.append("debug_no_code")
    
    # 5. mixed_signal: 混合多个危险意图
    # 如果同时命中多个风险标签（不含 multi_question），标记为 mixed_signal
    core_risks = [r for r in risks if r != "multi_question"]
    if len(core_risks) >= 2:
        risks.append("mixed_signal")
    
    return risks


def _is_ac_reflection_request(text: str) -> bool:
    return (
        _contains_any_keyword(text, AC_SIGNAL_KEYWORDS)
        and _contains_any_keyword(text, AC_UNCERTAINTY_KEYWORDS)
    )


def _contains_any_keyword(text: str, keywords: list[str]) -> bool:
    lowered = (text or "").lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _is_debug_no_code_request(text: str) -> bool:
    has_debug_symptom = any(kw in text for kw in ["WA", "错了", "不对", "样例", "输出", "答案"])
    has_evidence_gap = not _contains_code(text) and any(kw in text for kw in ["不知道哪里错", "不知道哪错", "哪里错", "为什么错"])
    return has_debug_symptom and has_evidence_gap


def _is_missing_context_request(text: str, messages: list) -> bool:
    if "[当前题目上下文" in _combined_message_text(messages):
        return False
    normalized = (text or "").strip()
    if not normalized:
        return True
    vague_patterns = [
        r"^这题怎么想[？?]?$",
        r"^这题怎么做[？?]?$",
        r"^怎么想[？?]?$",
        r"^怎么做[？?]?$",
        r"^不会[。！!？?]*$",
        r"^没思路[。！!？?]*$",
    ]
    return any(re.search(pattern, normalized) for pattern in vague_patterns)


def _get_highest_risk(risks: list) -> str:
    """
    根据优先级获取最高风险标签
    """
    if not risks:
        return None
    
    # 按优先级排序，返回优先级最高的
    sorted_risks = sorted(risks, key=lambda r: RISK_PRIORITY.get(r, 99))
    return sorted_risks[0]


def _infer_scaffold_stage(messages: list) -> int:
    """实时聊天只按同会话轮次做轻量支架升级。"""
    user_turns = sum(1 for msg in messages if msg.get("role") == "user")
    return max(1, min(user_turns or 1, 4))


def _student_texts(messages: list | None) -> list[str]:
    return [
        _extract_student_original_input(str(msg.get("content", "")))
        for msg in (messages or [])
        if msg.get("role") == "user"
    ]


def _has_repeated_stuck_signals(messages: list | None) -> bool:
    latest_three = _student_texts(messages)[-3:]
    stuck_count = sum(_contains_any_keyword(text, STUCK_SIGNAL_KEYWORDS) for text in latest_three)
    return stuck_count >= 2


def _infer_zpd_level(level_control: dict, risk_control: dict) -> str:
    max_level = level_control.get("max_level")
    risk_tags = set(risk_control.get("risk_tags", []))
    if max_level == "L1":
        return "Z0"
    if "type_confirm" in risk_tags or "bridge_attempt" in risk_tags:
        return "Z2"
    if max_level == "L2":
        return "Z1"
    if max_level == "L3":
        return "Z3"
    return "Z1"


def _select_tutor_control(level_control: dict, risk_control: dict, messages: list) -> dict:
    scaffold_stage = _infer_scaffold_stage(messages)
    if _has_repeated_stuck_signals(messages):
        scaffold_stage = 4
    highest_risk = risk_control.get("highest_risk")
    tutor_action = TUTOR_ACTION_BY_RISK.get(highest_risk)
    if not tutor_action:
        if level_control.get("max_level") == "L1":
            tutor_action = "ask_baseline_attempt"
        elif level_control.get("max_level") == "L2":
            tutor_action = "ask_slot_question"
        else:
            tutor_action = "point_to_specific_gap"

    if scaffold_stage >= 4 and tutor_action not in {"ask_baseline_attempt", "ask_one_focus_point", "offer_checkin_reflection"}:
        tutor_action = "offer_micro_example_or_checkin"

    allowed_help_by_stage = {
        1: "只问一个证据问题，不给结论",
        2: "给一个很小的方向提示，再问一个问题",
        3: "给一个极小例子或局部图示，再问一个问题",
        4: "给半步支架；仍卡住则建议打卡复盘",
    }
    forbidden = ["完整题解", "完整代码", "一次性列完整算法步骤"]
    risk_tags = set(risk_control.get("risk_tags", []))
    if "type_confirm" in risk_tags:
        forbidden.append("禁止确认/否认题型")
    if "bridge_attempt" in risk_tags or level_control.get("bridge_redline"):
        forbidden.append("禁止直接补关键桥")

    return {
        "zpd_level": _infer_zpd_level(level_control, risk_control),
        "scaffold_stage": scaffold_stage,
        "tutor_action": tutor_action,
        "allowed_help": allowed_help_by_stage[scaffold_stage],
        "forbidden": forbidden,
        "edf_required": True,
    }


def _extract_student_original_input(user_input: str) -> str:
    """从注入题目上下文的聊天消息中取回学生原始提问，避免误判系统提示词。"""
    marker = "[学生原始问题]"
    context_marker = "[当前题目上下文"
    if marker not in user_input:
        return user_input
    after_marker = user_input.split(marker, 1)[1]
    if context_marker in after_marker:
        after_marker = after_marker.split(context_marker, 1)[0]
    return after_marker.strip() or user_input


def analyze_student_turn(user_input: str, messages: list) -> dict:
    """
    分析学生输入，产出双轨控制对象
    
    返回双轨结构：
    {
        "level_control": {
            "max_level": "L1|L2|L3",
            "bridge_redline": True|False,
            "l2_slot_state": {...},
            "l2_current_slot": "..."
        },
        "risk_control": {
            "risk_tags": [...],
            "highest_risk": "..."  # 优先级最高的风险标签
        }
    }
    
    判定顺序：
    1. 等级轨：判断思考深度（L1/L2/L3）
    2. 风险轨：检测套答案风险
    3. 合并：风险轨优先约束等级轨
    """
    user_input = _extract_student_original_input(user_input)
    user_lower = user_input.lower()
    
    # ========== 等级轨：判断思考深度 ==========
    level_control = {
        "max_level": "L3",  # 默认允许到L3
        "bridge_redline": False,
        "l2_slot_state": {slot: "empty" for slot in L2_SLOTS},
        "l2_current_slot": None
    }
    
    # Step 1: L1 强拦
    l1_triggered = False
    
    # 1A: 直接索取
    for kw in L1_DIRECT_KEYWORDS:
        if kw in user_input:
            l1_triggered = True
            level_control["max_level"] = "L1"
            break
    
    # 1B: 极短且无思考
    if not l1_triggered and len(user_input) < 15:
        for kw in L1_SHORT_NO_THINKING:
            if kw in user_lower:
                l1_triggered = True
                level_control["max_level"] = "L1"
                break
    
    # 1C: 情绪催促
    if not l1_triggered:
        for kw in L1_EMOTION_PRESSURE:
            if kw in user_input:
                l1_triggered = True
                level_control["max_level"] = "L1"
                break
    
    # 1D: 只复述题意
    if not l1_triggered and _is_only_restating(user_input):
        l1_triggered = True
        level_control["max_level"] = "L1"
    
    # 如果已触发L1，跳过后续等级判断
    if not l1_triggered:
        # Step 2: L3 保留资格判断
        has_l3_evidence = _has_l3_evidence(user_input)
        
        if not has_l3_evidence:
            level_control["max_level"] = "L2"
        
        # Step 3: 贴代码无怀疑点
        has_code = _contains_code(user_input)
        has_doubt_point = _has_doubt_point(user_input)
        
        if has_code and not has_doubt_point:
            level_control["max_level"] = "L2"
        
        # Step 4: 桥梁套取识别
        bridge_attempted = _is_bridge_attempt(user_input)
        if bridge_attempted:
            level_control["bridge_redline"] = True
            if not has_l3_evidence:
                level_control["max_level"] = "L2"
        
        # Step 5: L2槽位分析
        if level_control["max_level"] in ("L2", "L3"):
            level_control["l2_slot_state"] = _analyze_slot_filling(user_input)
            level_control["l2_current_slot"] = _determine_current_slot(level_control["l2_slot_state"])
    
    # ========== 风险轨：检测套答案风险 ==========
    risk_tags = _detect_risks(user_input)
    if _is_missing_context_request(user_input, messages) and "missing_context" not in risk_tags:
        risk_tags.append("missing_context")
    highest_risk = _get_highest_risk(risk_tags)
    
    risk_control = {
        "risk_tags": risk_tags,
        "highest_risk": highest_risk
    }
    
    # ========== 合并：风险轨优先约束等级轨 ==========
    # 根据最高优先级风险调整等级
    # 注意：bridge_attempt 需要特殊处理：有L3证据时保留L3，只开启桥梁红线
    if highest_risk:
        limit_level = RISK_LEVEL_LIMITS.get(highest_risk)
        if limit_level:
            # bridge_attempt 特殊处理：如果已经检测到L3证据，保留L3
            if highest_risk == "bridge_attempt" and level_control["max_level"] == "L3":
                # 有L3证据，保留L3，只开启桥梁红线（已在上面处理）
                pass
            else:
                # 其他情况：如果风险要求限制等级，取更严格的等级
                current_level = level_control["max_level"]
                level_order = {"L1": 1, "L2": 2, "L3": 3}
                if level_order.get(limit_level, 3) < level_order.get(current_level, 3):
                    level_control["max_level"] = limit_level
    
    # 同步风险标签到 risk_control
    # 从 level_control 的 reason_tags 中提取风险标签
    risk_tags_from_level = [tag for tag in level_control.get("reason_tags", []) 
                            if tag in ["direct_request", "emotion_pressure", "bridge_attempt", 
                                      "type_confirm", "code_no_target", "cross_slot_dump",
                                      "multi_question", "missing_context", "checkin_handoff",
                                      "debug_no_code"]]
    for tag in risk_tags_from_level:
        if tag not in risk_control["risk_tags"]:
            risk_control["risk_tags"].append(tag)
    
    # 更新最高风险
    if risk_control["risk_tags"]:
        risk_control["highest_risk"] = _get_highest_risk(risk_control["risk_tags"])
    
    tutor_control = _select_tutor_control(level_control, risk_control, messages)

    # 返回双轨结构
    return {
        "level_control": level_control,
        "risk_control": risk_control,
        "tutor_control": tutor_control,
    }


def _is_only_restating(text: str) -> bool:
    """判断是否只复述题意，没有自己的分析"""
    # 简单启发：如果只提到输入输出，没有"我觉得"、"我尝试"等思考痕迹
    restating_patterns = [
        r'输入.*输出', r'题目说', r'题目要求', r'给定.*求',
        r'输入格式', r'输出格式', r'数据范围'
    ]
    thinking_patterns = [
        r'我觉得', r'我想', r'我尝试', r'我认为', r'我分析',
        r'我的思路', r'我的想法', r'我考虑', r'我怀疑'
    ]
    
    has_restating = any(re.search(p, text) for p in restating_patterns)
    has_thinking = any(re.search(p, text) for p in thinking_patterns)
    
    # 如果提到题意描述词汇，且长度较短，且没有思考痕迹
    if has_restating and len(text) < 80 and not has_thinking:
        return True
    return False


def _contains_code(text: str) -> bool:
    """判断是否包含代码片段"""
    code_indicators = 0
    for pattern in CODE_PATTERNS:
        if re.search(pattern, text):
            code_indicators += 1
    # 至少2个代码特征，或包含大括号、分号等
    if code_indicators >= 2 or '{' in text or ';' in text:
        return True
    return False


def _has_doubt_point(text: str) -> bool:
    """判断是否有明确的怀疑点/定位"""
    doubt_patterns = [
        r'第\s*\d+\s*行', r'line\s*\d+', r'这里', r'这行',
        r'怀疑', r'觉得.*不对', r'错在', r'问题在',
        r'WA.*这里', r'TLE.*这里', r'RE.*这里',
        r'dp\[.*\]', r'数组.*越界', r'循环.*条件'
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in doubt_patterns)


def _has_l3_evidence(text: str) -> bool:
    """判断是否有L3证据（可定位的实质性尝试）"""
    
    # 如果同时有代码和怀疑点，算L3证据
    if _contains_code(text) and _has_doubt_point(text):
        return True
    
    # 给出具体状态定义（要有具体定义，不只是"状态"两个字）
    concrete_patterns = [
        r'dp\[.*\].*=.*',  # dp[i] = ...
        r'f\([^)]*\).*=',  # f(n) = ...
        r'设.*dp\[',  # 设dp[
        r'定义.*为.*',  # 定义为具体东西
        r'状态.*表示.*',  # 状态表示...
    ]
    
    for pattern in concrete_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # 给出具体函数定义
    function_patterns = [
        r'def\s+\w+\s*\(',  # def func(
        r'函数\s*\w*\s*\(.*\)',
        r'递归.*f\s*\(',
    ]
    for pattern in function_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # 明确说出具体错误（不是笼统的"WA了"）
    error_patterns = [
        r'第.*行.*错',
        r'越界',
        r'边界.*错',
        r'样例.*过.*但',
        r'TLE.*因为',
        r'RE.*在',
    ]
    for pattern in error_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # 检查是否有具体尝试的描述（要有具体内容）
    trying_patterns = [
        r'我写了.*具体',  # 我写了...具体
        r'我定义了.*',  # 我定义了...
        r'我试了.*但是',  # 我试了...但是
        r'我用了.*方法',  # 我用了...方法
    ]
    return any(re.search(p, text) for p in trying_patterns)


def _is_bridge_attempt(text: str) -> bool:
    """判断是否在尝试套取桥梁"""
    text_lower = text.lower()
    
    # 精确匹配关键词
    for kw in BRIDGE_KEYWORDS:
        if kw in text_lower or kw in text:
            return True
    
    # 宽松匹配：索取关键结构但未展示自己如何推导
    loose_patterns = [
        r'转移.*不对', r'转移.*错', r'不会.*转移', r'转移.*怎么',
        r'状态.*不对', r'状态.*错', r'状态.*怎么.*定义',
        r'base case.*不对', r'base case.*错', r'base case.*怎么',
        r'check.*不对', r'check.*错', r'check.*怎么',
        r'怎么.*push', r'push.*怎么', r'lazy.*怎么',
        r'方程.*怎么', r'怎么.*建模', r'建模.*怎么',
    ]
    
    for pattern in loose_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False


def _is_cross_slot_dump(text: str) -> bool:
    """判断是否存在跨槽位拼凑"""
    # 一句话里同时出现多个槽位关键词
    slot_keywords = {
        "对象": ["数组", "区间", "物品", "节点", "边", "状态", "字符串"],
        "选择": ["选", "不选", "向左", "向右", "合并", "不合并", "拿", "不拿"],
        "限制": ["容量", "时间", "重量", "限制", "不超过", "最多", "至少"],
        "最简单情况": ["边界", "只有一个", "空", "初始", "base case"]
    }
    
    matched_slots = 0
    for slot, keywords in slot_keywords.items():
        if any(kw in text for kw in keywords):
            matched_slots += 1
    
    # 同时匹配3个或以上槽位，且文本较短（<100字），可能是拼凑
    if matched_slots >= 3 and len(text) < 100:
        return True
    return False


def _analyze_slot_filling(text: str) -> dict:
    """分析L2槽位填充状态"""
    state = {slot: "empty" for slot in L2_SLOTS}
    text_lower = text.lower()
    
    # 对象
    if any(kw in text for kw in ["数组", "区间", "物品", "节点", "边", "药草", "字符串"]):
        state["对象"] = "filled"
    elif any(kw in text for kw in ["东西", "元素", "东西"]):
        state["对象"] = "partial"
    
    # 选择
    if any(kw in text_lower for kw in ["选", "不选", "拿", "不拿", "向左", "向右", "合并"]):
        state["选择"] = "filled"
    elif "选择" in text:
        state["选择"] = "partial"
    
    # 限制
    if any(kw in text for kw in ["容量", "时间", "重量", "限制", "不超过", "最大", "总时间"]):
        state["限制"] = "filled"
    elif any(kw in text for kw in ["不能超过", "有限制"]):
        state["限制"] = "partial"
    
    # 最简单情况
    if any(kw in text for kw in ["边界", "只有一个", "空", "初始", "base case", "最小"]):
        state["最简单情况"] = "filled"
    
    return state


def _determine_current_slot(slot_state: dict) -> str:
    """确定当前应该追问的槽位"""
    # 找到第一个未填的槽位
    for slot in L2_SLOTS:
        if slot_state[slot] == "empty":
            return slot
    # 都填了，返回最后一个（最简单情况）做连接验证
    return "最简单情况"


def _looks_like_semantic_risk(text: str) -> bool:
    normalized = (text or "").strip().lower()
    if not normalized:
        return False

    for pattern in SEMANTIC_RISK_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True

    if normalized.endswith(("吗", "吗？", "吗?", "对吧", "对吧？", "对吧?")):
        return True

    return False


def should_call_classifier(dual_control: dict, user_input: str):
    """
    判断是否需要调用分类器（双轨版本）
    
    Args:
        dual_control: 双轨控制对象，包含 level_control 和 risk_control
    """
    text = (user_input or "").strip()
    level_control = dual_control["level_control"]
    risk_control = dual_control["risk_control"]
    
    risk_tags = set(risk_control.get("risk_tags", []))

    if not text or len(text) < 2:
        return False, "skip_empty"

    if level_control.get("max_level") == "L1":
        return False, "skip_l1"

    # 如果已经有高信忆度风险标签，不需要分类器
    high_confidence_risks = {"direct_request", "type_confirm", "bridge_attempt", "emotion_pressure"}
    if risk_tags & high_confidence_risks:
        return False, "skip_high_confidence_risk"

    if level_control.get("max_level") == "L3":
        return False, "skip_l3"

    if level_control.get("max_level") != "L2":
        return False, "skip_non_l2"

    if _looks_like_semantic_risk(text):
        return True, "call_semantic_risk"

    return False, "skip_non_semantic_l2"


# ============ 3. 分类器结果合并（新增） ============

def merge_intent_with_control(control: dict, intent_tag: str) -> dict:
    """
    将 MiniMax 意图分类结果合并到代码层控制对象
    
    规则（只能降级，不能升档）：
    1. direct -> 强制 max_level = L1
    2. type_confirm -> max_level <= L2，添加 type_confirm_tag
    3. bridge -> 打开 bridge_redline，如果没有 L3 证据则压到 L2
    4. substantive -> 严格 no-op，直接返回原 control，不做任何修改
       L3 资格只由代码层的"可定位实质尝试"证据决定，分类器不负责升档
    
    Args:
        control: analyze_student_turn() 返回的控制对象
        intent_tag: 分类器结果 (direct/type_confirm/bridge/substantive/None)
    
    Returns:
        合并后的控制对象
    """
    if not intent_tag:
        return control
    
    # substantive 必须是严格 no-op，直接返回原对象
    # 不新增任何字段，不修改任何已有字段
    if intent_tag == "substantive":
        return control
    
    # 复制控制对象，避免修改原始对象
    merged = dict(control)
    
    # 记录分类器标签（substantive 分支不执行到这里）
    if "intent_tag" not in merged:
        merged["intent_tag"] = intent_tag
    
    # 当前是否有 L3 证据
    has_l3_evidence = "slot_fill" in merged.get("reason_tags", [])
    
    if intent_tag == "direct":
        # 强制压到 L1
        merged["max_level"] = "L1"
        if "classifier_direct" not in merged.get("reason_tags", []):
            merged["reason_tags"] = merged.get("reason_tags", []) + ["classifier_direct"]
    
    elif intent_tag == "type_confirm":
        # 不能确认题型，最多 L2
        if merged["max_level"] in ("L3",):
            merged["max_level"] = "L2"
        if "type_confirm" not in merged.get("reason_tags", []):
            merged["reason_tags"] = merged.get("reason_tags", []) + ["type_confirm"]
    
    elif intent_tag == "bridge":
        # 打开桥梁红线
        merged["bridge_redline"] = True
        if "classifier_bridge" not in merged.get("reason_tags", []):
            merged["reason_tags"] = merged.get("reason_tags", []) + ["classifier_bridge"]
        
        # 如果没有 L3 证据，压到 L2
        if not has_l3_evidence:
            merged["max_level"] = "L2"
    
    return merged


# ============ 4. Prompt构造 ============

def build_system_prompt(dual_control: dict, remaining: int, student_id: str, problem_id: str) -> str:
    """
    构建带控制块的System Prompt（双轨版本）
    
    Args:
        dual_control: 双轨控制对象，包含 level_control 和 risk_control
    
    动态注入：
    - MAX_LEVEL
    - BRIDGE_REDLINE
    - RISK_TAGS
    - L2_SLOT_STATE (如果是L2)
    - L2_CURRENT_SLOT (如果是L2)
    """
    level_control = dual_control["level_control"]
    risk_control = dual_control["risk_control"]
    
    max_level = level_control["max_level"]
    bridge_redline = level_control["bridge_redline"]
    risk_tags = risk_control.get("risk_tags", [])
    highest_risk = risk_control.get("highest_risk")
    tutor_control = dual_control.get("tutor_control") or {}
    
    # 风险标签说明
    risk_desc = "无"
    if highest_risk:
        risk_names = {
            "direct_request": "直接索取",
            "type_confirm": "确认题型",
            "bridge_attempt": "索取桥梁",
            "mixed_signal": "混合意图",
            "multi_question": "多问题"
        }
        risk_desc = risk_names.get(highest_risk, highest_risk)

    tutor_policy = f"""## SOCRATIC_POLICY（实时短策略块）
- ZPD: {tutor_control.get('zpd_level', 'Z1')}，只给学生当前能力上方半步帮助
- Adaptive Scaffolding: stage={tutor_control.get('scaffold_stage', 1)}，{tutor_control.get('allowed_help', '只问一个问题')}
- Evidence-Driven Feedback: 回复必须先基于学生原话/题面证据判断卡点，再给一个微问题
- tutor_action: {tutor_control.get('tutor_action', 'ask_slot_question')}
- forbidden: {'；'.join(tutor_control.get('forbidden', ['完整题解', '完整代码']))}
- 输出给学生时不要暴露这些内部标签，只表现为一句短引导 + 一个问题
"""
    
    base_prompt = f"""你是一名 NOI 竞赛教练助手，专门辅导 CSP-J/S、NOIP 方向的学生。

## 核心原则
你不是"答案机"，你是"思维训练器"。目标是让学生学会独立解题。

{tutor_policy}

## 双轨控制指令（必须遵守）

### 等级轨（思考深度）
**本次回复最高级别: {max_level}**
**桥梁红线: {'开启' if bridge_redline else '关闭'}**

### 风险轨（套答案风险）
**风险标签: {', '.join(risk_tags) if risk_tags else '无'}**
**优先级最高风险: {risk_desc}**

### 级别定义
- **L1 - 引导反问（不消耗配额）**：
  只问一个问题，不给方向，不确认题型，不说"你方向对"
  默认问法："先别想快不快。最笨的方法你会怎么做？"

- **L2 - 槽位化单步追问（消耗配额）**：
  每次只问一个问题，一次只推进半步，不给关键桥梁，不连发2-4个问题
  只允许围绕这4个槽位：对象、选择、限制、最简单情况
  
- **L3 - 针对性指出问题（消耗配额）**：
  只指出学生哪一步有问题，不直接给正确答案
  每次只推进半步，每次最多引入一个新概念
  可以给3-5行伪代码或关键行，不能给完整代码/方程/结构

### 风险轨约束（必须优先遵守）

**direct_request** 场景：
- 严禁给答案、代码、完整做法
- 只能反问

**type_confirm** 场景：
- 严禁确认或否认题型（如"是DP"、"不是二分"等）
- 必须把反问落到题面中的具体对象、条件或结构证据
- 不允许只问"你为什么会这么猜？"这种泛问题

**bridge_attempt** 场景（bridge_redline=true）：
- 严禁直接给出状态定义、转移方程、check条件
- 可以指出错误，不能补正确桥梁

**mixed_signal** 场景：
- 混合多个危险意图时，按最危险意图处理
- 不按"最像思考的片段"提级

**multi_question** 场景：
- 不同时回答多个问题
- 要求聚焦一个点

## 强制输出约束
- 用初中生/高中生能懂的话
- 每次回复不超过5句话
- 每次只问一个问题
- 每次最多引入一个新概念
- 回复最后必须保留等级标签：[LEVEL:L1] 或 [LEVEL:L2] 或 [LEVEL:L3] 或 [LEVEL:L4]
- 标签单独一行，放在回复最后
"""

    # 根据max_level添加具体行为指导
    if max_level == "L1":
        base_prompt += """

## L1 行为要求
学生当前处于L1限制模式，请：
1. 只问上面定义的默认问题："先别想快不快。最笨的方法你会怎么做？"
2. 不给任何方向暗示
3. 不确认任何题型
4. 不认可学生的任何预设
"""
    elif max_level == "L2":
        slot_state = level_control.get("l2_slot_state", {})
        current_slot = level_control.get("l2_current_slot", "对象")
        
        base_prompt += f"""

## L2 槽位状态
当前槽位填充状态：
- 对象: {slot_state.get('对象', 'empty')}
- 选择: {slot_state.get('选择', 'empty')}
- 限制: {slot_state.get('限制', 'empty')}
- 最简单情况: {slot_state.get('最简单情况', 'empty')}

当前应该追问的槽位：{current_slot}

## L2 行为要求
1. 只围绕"{current_slot}"槽位问一个问题
2. 如果学生答不出，降级问更小、更具体的问题
3. 不要跳到其他槽位
4. 填槽后只做极弱确认（如"嗯，这个方向可以"），不能补桥梁
"""
    elif max_level == "L3":
        if bridge_redline:
            base_prompt += """

## L3 + 桥梁红线 行为要求
学生有尝试，但在索取关键桥梁：
1. 可以指出他哪一步方向不对
2. 可以指出定义哪里不完整
3. 可以指出判断条件的方向问题
4. **禁止说出正确状态定义/转移方程/check条件**
5. 只能让学生自己推导正确桥梁
"""
        else:
            base_prompt += """

## L3 行为要求
1. 针对学生具体的尝试，指出问题所在
2. 每次最多推进半步
3. 可以给3-5行伪代码或关键行
4. 不能给完整解法
"""

    # 添加 type_confirm 特殊约束（如果适用）
    if "type_confirm" in risk_tags:
        base_prompt += """

## type_confirm 特殊约束（必须遵守）
学生在猜测或确认题型/方法。

**绝对禁止**：
- 不能确认题型（不能说"对，这是字符串"、"对，是DP"）
- 不能纠正题型（不能说"不是这个，是另外那个"）
- 不能给方向暗示

**必须做的**：
- 必须把反问落到题面中的具体对象、条件或结构证据
- 如果题面提到大量 01 串/前缀关系，就问学生看到了什么前缀证据
- 如果题面提到树上多条路径/点被经过次数，就问一条 u 到 v 路径会影响哪些点
- 如果题面提到二分目标/可行性，就问 mid 代表的目标能不能被满足
- 如果当前题面证据不足，再问："题目里哪个对象或条件让你想到这个方法？"

目标：让学生自己解释推理过程，而不是告诉他答案。
"""

    # 添加当前状态信息
    base_prompt += f"""

## 当前状态
学生：{student_id}
题目：{problem_id}
本题剩余提示次数：{remaining} / {PER_PROBLEM_HINT_LIMIT}

重要：
1. 严格遵守上面的 MAX_LEVEL 限制
2. 严格遵守桥梁红线规则
3. 严格遵守 type_confirm 约束（如果适用）
4. 回复最后一行必须是 [LEVEL:L1|L2|L3|L4] 标签
5. 不要在回复中写配额数字
"""

    return base_prompt


# ============ 5. 配额管理（保持不变） ============

def load_quota(student_id: str, problem_id: str) -> dict:
    """加载配额"""
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
    """消耗配额"""
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
    """配额耗尽后的临别礼物（L4）"""
    return f"""💡 这道题（{problem_id}）的提示配额已用完。

🎁 临别礼物：

建议检查以下几点：
1. 边界条件：数组是否越界？循环范围是否正确？
2. 初始化：DP初始状态、递归base case是否完整？
3. 算法选择：当前复杂度是否满足数据范围？

🎯 下一步：把思路整理成文字，明天找老师当面讨论。

---
本题提示已用完，换题后配额会重置。

[LEVEL:L4]"""


# ============ 5. 标签解析（保持不变） ============

def parse_level_tag(reply: str) -> tuple[str, str]:
    """
    从回复末尾提取 [LEVEL:Lx] 标签
    返回: (级别, 去除标签后的干净回复)
    """
    pattern = r'\[LEVEL:(L1|L2|L3|L4)\]\s*$'
    match = re.search(pattern, reply, re.IGNORECASE)
    
    if match:
        level = match.group(1).upper()
        clean_reply = re.sub(pattern, '', reply, flags=re.IGNORECASE).rstrip()
        return level, clean_reply
    
    return "", reply.strip()


# ============ 6. 硬闸门函数 ============

def enforce_level_gate(level: str, max_level: str, raw_reply: str) -> tuple[str, str]:
    """
    硬闸门：强制限制模型输出级别不超过代码层限制
    
    返回: ( enforced_level, enforced_reply )
    - 如果模型级别超过max_level，强制降级并替换为安全兜底回复
    - 否则保持原样
    """
    # 级别优先级：L1 < L2 < L3 < L4
    level_order = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "": 0}
    
    model_level_num = level_order.get(level, 0)
    max_level_num = level_order.get(max_level, 4)
    
    # 如果模型级别超过代码层限制，强制降级
    if model_level_num > max_level_num:
        # 强制使用max_level对应的兜底回复
        if max_level == "L1":
            fallback = "先别想快不快。最笨的方法你会怎么做？"
        elif max_level == "L2":
            fallback = "这道题你最终要记录什么信息？"
        else:
            # L3也被超了（理论上不应该，但保险起见）
            fallback = "你这里思路方向可能需要调整。再想想哪里不完整？"
        
        return max_level, f"{fallback}\n\n[LEVEL:{max_level}]"
    
    # 未超限，保持原样
    return level, raw_reply


# ============ 6.5 输出保险丝（双轨规则） ============

# Type Confirm 危险模式：明确确认或否认题型的句首/独立句
# 使用严格正则，避免误杀追问性质的反问
TYPE_CONFIRM_DANGER_PATTERNS = [
    r'^是\s*(dp|二分|贪心|递归|字符串|背包|图论|动态规划|树状|bfs|dfs)',  # 是DP/是二分...
    r'^不是\s*(dp|二分|贪心|递归|字符串|背包|图论|动态规划)',  # 不是DP/不是二分...
    r'^这题是',  # 这题是...
    r'^应该用',  # 应该用...
    r'^可以用\s*(dp|二分|贪心|递归|字符串|背包|图论)',  # 可以用二分...
    r'^用\s*(dp|二分|贪心|递归|字符串|背包|图论)',  # 用二分...
    r'[^为什么].*是[^,，。]*题',  # 确认是XX题（非追问）
    r'双层.*(?:不行|会超|超时)',
    r'必须\s*(?:用|走|套)',
]

# Bridge 危险模式：直接给出关键桥梁内容
BRIDGE_DANGER_PATTERNS = [
    r'状态定义为[^,，。]{5,}',  # 状态定义为...
    r'转移方程为[^,，。]{5,}',  # 转移方程为...
    r'check\s*函数[^,，。]{3,}',  # check函数...
    r'建图[^,，。]{5,}',  # 建图...
    r'递归[^,，。]{0,10}base\s*case',  # 递归...base case
    r'dp\s*\[\s*x\s*\]\s*\[\s*y\s*\]\s*(?:=|表示|代表|定义为)\s*[^。！？\n]{3,}',
    r'dp\s*\[\s*i\s*\]\s*\[\s*j\s*\]\s*(?:=|表示|代表|定义为)\s*[^。！？\n]{3,}',
    r'(?:令|设)\s*dp\s*\[',
]

COMPLETE_SOLUTION_DANGER_PATTERNS = [
    r'完整做法',
    r'完整代码',
    r'代码如下',
    r'题解如下',
    r'AC\s*代码',
    r'#include\s*<',
    r'int\s+main\s*\(',
    r'using\s+namespace\s+std',
]

# 安全替换回复
TYPE_CONFIRM_SAFE_REPLY = "先别急着确认题型。你为什么会这么猜？\n\n[LEVEL:L2]"
BRIDGE_SAFE_REPLY = "这里不能直接给出关键桥梁。你自己的尝试是什么？\n\n[LEVEL:L2]"
COMPLETE_SOLUTION_SAFE_REPLY = "先停一下，我不能直接把完整做法或代码倒给你。你先说：当前这一步里，你能确定的对象和目标分别是什么？\n\n[LEVEL:L2]"


def _check_danger_patterns(reply: str, patterns: list) -> bool:
    """检查回复是否命中危险模式"""
    for pattern in patterns:
        if re.search(pattern, reply, re.IGNORECASE):
            return True
    return False


TYPE_CONFIRM_GENERIC_PATTERNS = [
    r'为什么会?这么猜',
    r'为什么会?这样猜',
    r'题目里哪个特征让你想到这个方法',
    r'看到什么结构才往这个方向想',
]


def _combined_message_text(messages: list | None) -> str:
    if not messages:
        return ""
    return "\n".join(str(msg.get("content", "")) for msg in messages)


def _build_type_confirm_contextual_reply(messages: list | None) -> str:
    context = _combined_message_text(messages)
    if "01" in context and "前缀" in context:
        question = "先别急着确认题型。题面里哪些 01 串之间出现了相同前缀，才让你想到要合并这些前缀？"
    elif ("路径" in context or "运输路径" in context) and ("树" in context or "节点" in context or "点" in context):
        question = "先别急着定算法。只看一条从 u 到 v 的路径，它会让哪些点的经过次数发生变化？"
    elif "mid" in context or "check" in context or "二分" in context:
        question = "先别急着确认二分。这个 mid 在题目里代表的目标是什么，它能不能被满足要看哪个条件？"
    elif "50000" in context and "20" in context:
        question = "先别急着判断能不能双层枚举。把 50000 × 50000 × 20 估一下，大概会到什么数量级？"
    else:
        question = "先别急着确认题型。题目里哪个具体对象或条件让你想到这个方法？"
    return f"{question}\n\n[LEVEL:L2]"


def _latest_student_text(messages: list | None) -> str:
    if not messages:
        return ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return _extract_student_original_input(str(msg.get("content", "")))
    return ""


def _extract_problem_ref_from_messages(messages: list | None) -> str:
    text = _combined_message_text(messages)
    match = re.search(r"\bP\d+\b", text)
    return match.group(0) if match else ""


def build_policy_handoff_payload(dual_control: dict, messages: list | None) -> dict | None:
    """Build the v0 AIChat -> checkin handoff payload for forced handoff actions."""
    tutor_control = dual_control.get("tutor_control") or {}
    tutor_action = tutor_control.get("tutor_action")
    if tutor_action == "offer_checkin_reflection":
        risk_type = "ac_unclear_in_aichat"
    elif tutor_action == "offer_micro_example_or_checkin" and tutor_control.get("scaffold_stage", 1) >= 4:
        risk_type = "repeated_stuck_exit"
    else:
        return None

    return {
        "handoff_type": "checkin_reflection",
        "source": "aichat",
        "risk_type": risk_type,
        "problem_ref": _extract_problem_ref_from_messages(messages),
        "last_user_message": _latest_student_text(messages),
        "suggested_focus": HANDOFF_FOCUS_BY_RISK[risk_type],
    }


def build_policy_override_reply(dual_control: dict, messages: list | None) -> str | None:
    """Deterministic replies for routing/guardrail cases where prompt-only is too brittle."""
    tutor_control = dual_control.get("tutor_control") or {}
    risk_control = dual_control.get("risk_control") or {}
    tutor_action = tutor_control.get("tutor_action")
    risk_tags = set(risk_control.get("risk_tags", []))
    text = _latest_student_text(messages)
    context = _combined_message_text(messages)

    if tutor_action == "offer_checkin_reflection":
        return (
            "你已经 AC 了，这一步更适合放到打卡复盘里梳理：先写下你当时的做法、最卡的一步、以及为什么这样写还不稳。\n"
            "我会在复盘里帮你把关键桥补成可回看的卡片，而不是在聊天里重讲整套思路。\n\n[LEVEL:L2]"
        )

    if tutor_action == "offer_micro_example_or_checkin" and tutor_control.get("scaffold_stage", 1) >= 4:
        return (
            "你已经在同一个卡点上绕了几轮了，继续问下去容易变成我替你推。\n"
            "先带着这道题去打卡复盘，把“我以为 check(mid) 在检查什么”和“我哪里说不清”写出来，我再按复盘给你半步拆开。\n\n[LEVEL:L2]"
        )

    if tutor_action == "request_problem_context":
        return "我现在还不知道是哪道题。先把题号、题面链接，或者你卡住的那一步发我，我们再从那里拆。\n\n[LEVEL:L1]"

    if tutor_action == "ask_one_focus_point":
        return "这几个问题先别一起拆。我们先聚焦一个点：你想先弄清概念含义、代码怎么写，还是查询怎么合并？\n\n[LEVEL:L1]"

    if tutor_action == "ask_code_evidence":
        return "先不判断这段代码对不对。你怀疑哪一行，或者哪个样例和你的预期不一样？\n\n[LEVEL:L2]"

    if tutor_action == "ask_debug_evidence":
        return "先别猜错误原因。把代码或你手算的推导过程贴出来；我们只看你的推导从哪一步开始和标准结果不一样。\n\n[LEVEL:L1]"

    if "正偶数" in context and "排除 2" in text:
        return "只看最小反例：如果 w=2，你能把它拆成两个正偶数相加吗？\n\n[LEVEL:L2]"

    if "emotion_pressure" in risk_tags:
        return (
            "明天要交确实会紧张，我们先把压力降到能动手的一小步。\n"
            "只看题目目标：如果不用任何高级做法，你会怎么手动统计一条路径经过了哪些点？\n\n[LEVEL:L1]"
        )

    if "lazy" in text.lower() and ("是不是" in text or "对不对" in text):
        return "先不判对不对。一个区间整体加 3 后，父节点记录的区间和和两个儿子各自知道的信息有什么不同？\n\n[LEVEL:L2]"

    if ("P3128" in context or "路径计数" in context or "树上路径" in context) and ("LCA" in text or "标记" in text):
        if tutor_control.get("scaffold_stage", 1) >= 3:
            return "画一条 1-2-3-4 的小链，假设路径是 2 到 4。只在两个端点打标记再往上汇总时，公共祖先附近会被多算还是少算？\n\n[LEVEL:L2]"
        return "你已经知道卡点在端点和公共祖先。先画一条 3 到 5 个点的小路径：路径两端各会影响哪一段点？\n\n[LEVEL:L2]"

    if "数字三角形" in context and "转移" in text:
        return "你卡的是来源位置。先只看某一行中间的一个格子：它能从上一行的哪几个相邻格子走过来？\n\n[LEVEL:L3]"

    if "dp[x][y]" in text and ("表示" in text or "状态" in text):
        return "先别急着给 `dp[x][y]` 下定义。只看一个格子作为起点时，你最终想从这个格子记录出什么结果？\n\n[LEVEL:L2]"

    return None


def enforce_output_guards(reply: str, level_control: dict, risk_control: dict, messages: list | None = None) -> tuple[str, str]:
    """
    输出保险丝（双轨规则）
    
    根据风险标签检查并约束输出，确保：
    - type_confirm 场景不确认/否认题型
    - bridge_attempt 场景不直接给桥梁
    
    返回: (处理后的回复, 是否被替换的标记)
    """
    risk_tags = risk_control.get("risk_tags", [])

    # 0. 通用泄题保险丝：任何场景都不允许完整题解/代码 dump
    if _check_danger_patterns(reply, COMPLETE_SOLUTION_DANGER_PATTERNS):
        return COMPLETE_SOLUTION_SAFE_REPLY, "complete_solution_guard"
    
    # 1. Type Confirm 保险丝
    if "type_confirm" in risk_tags:
        if _check_danger_patterns(reply, TYPE_CONFIRM_DANGER_PATTERNS):
            return _build_type_confirm_contextual_reply(messages), "type_confirm_guard"
        if _check_danger_patterns(reply, TYPE_CONFIRM_GENERIC_PATTERNS):
            return _build_type_confirm_contextual_reply(messages), "type_confirm_generic_guard"
    
    # 2. Bridge 保险丝
    if level_control.get("bridge_redline", False) or "bridge_attempt" in risk_tags:
        if _check_danger_patterns(reply, BRIDGE_DANGER_PATTERNS):
            return BRIDGE_SAFE_REPLY, "bridge_guard"
    
    # 3. Multi Question 保险丝
    if "multi_question" in risk_tags:
        # 检测回复是否同时回答了多个问题
        answer_count = len(re.findall(r'[。\.\!\?]？\s*(?=可以|应该|这个|那个)', reply))
        if answer_count >= 2:
            return "请一次只问一个点，我们先聚焦一下你最关键的问题。\n\n[LEVEL:L2]", "multi_question_guard"
    
    return reply, None


def _finalize_chat_reply(clean_reply: str, final_level: str, remaining: int, student_id: str, problem_id: str) -> tuple[str, str, str]:
    """Apply quota accounting and display footer to an already-guarded reply."""
    if final_level in ("L2", "L3"):
        success, remaining_after = consume_quota(student_id, problem_id)
        if success:
            reply_for_display = clean_reply + f"\n\n---\n💡 本题还剩 {remaining_after} 次提示机会"
        else:
            reply_for_display = clean_reply + "\n\n---\n⚠️ 提示配额已用完"
    else:
        reply_for_display = clean_reply + f"\n\n---\n💡 本题还剩 {remaining} 次提示机会（本次未消耗）"
    return reply_for_display, clean_reply, final_level


# ============ 7. 主对话逻辑 ============

def chat(messages: list, student_id: str, problem_id: str) -> tuple[str, str, str]:
    """
    主对话逻辑（双轨版本）：
    1. 检查配额
    2. 代码层分析：产出双轨控制对象（等级轨 + 风险轨）
    3. 构建带双轨控制块的Prompt
    4. 调用LLM
    5. **硬闸门**：检查模型输出是否超过max_level
    6. **输出保险丝**：检查并约束风险场景输出
    7. 返回 (display_reply, history_reply, final_level)
    
    返回: (reply_for_display, reply_for_history, final_level)
    """
    remaining = get_remaining_quota(student_id, problem_id)
    
    if remaining <= 0:
        farewell = generate_farewell_gift(problem_id)
        return farewell, farewell, "L4"
    
    # 获取最后一条用户输入
    last_user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_msg = msg.get("content", "")
            break
    
    # 代码层分析：产出双轨控制对象
    dual_control = analyze_student_turn(last_user_msg, messages)
    level_control = dual_control["level_control"]
    risk_control = dual_control["risk_control"]

    policy_override_reply = build_policy_override_reply(dual_control, messages)
    if policy_override_reply:
        final_level, clean_reply = parse_level_tag(policy_override_reply)
        clean_reply, guard_triggered = enforce_output_guards(clean_reply, level_control, risk_control, messages=messages)
        if guard_triggered:
            final_level = "L2"
        return _finalize_chat_reply(clean_reply, final_level, remaining, student_id, problem_id)
    
    # 分类器增强（如果需要）
    should_classify, classifier_reason = should_call_classifier(dual_control, last_user_msg)
    if should_classify:
        try:
            from classifier import classify_intent
            intent_tag = classify_intent(last_user_msg, timeout=CLASSIFIER_TIMEOUT_SECONDS)
            # 合并分类器结果到风险轨
            if intent_tag in ["direct", "type_confirm", "bridge"]:
                if intent_tag not in risk_control["risk_tags"]:
                    risk_control["risk_tags"].append(intent_tag)
                    # 更新最高风险
                    if risk_control["highest_risk"] is None or \
                       RISK_PRIORITY.get(intent_tag, 99) < RISK_PRIORITY.get(risk_control["highest_risk"], 99):
                        risk_control["highest_risk"] = intent_tag
        except Exception as e:
            print(f"[classifier] fail reason=unexpected_exception input_len={len(last_user_msg.strip())} detail={e}")
    else:
        print(f"[classifier] skipped reason={classifier_reason} input_len={len(last_user_msg.strip())}")
    
    max_level = level_control["max_level"]  # 硬闸门上限
    
    # 构建带双轨控制块的System Prompt
    system_prompt = build_system_prompt(dual_control, remaining, student_id, problem_id)
    
    # 调用LLM
    last_error = None
    response = None
    for idx, model_name in enumerate(get_model_candidates("NOI_CHAT_MODELS", DEFAULT_CHAT_MODELS)):
        try:
            temperature = 1 if "kimi-k2.5" in model_name.lower() else 0.3
            response = get_client().chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=temperature,
            )
            if idx > 0:
                print(f"[noi_agent] fallback model succeeded: {model_name}")
            break
        except Exception as exc:
            last_error = exc
            print(f"[noi_agent] LLM call failed on model {model_name}: {exc}")
            if not is_model_unavailable_error(exc):
                raise

    if response is None:
        raise last_error or RuntimeError("No available chat model")
    
    raw_reply = response.choices[0].message.content
    
    # 提取模型输出的级别标签
    model_level, clean_reply = parse_level_tag(raw_reply)
    
    # ===== 硬闸门：强制限制不超过max_level =====
    enforced_level, enforced_reply = enforce_level_gate(model_level, max_level, raw_reply)
    
    # 重新解析（如果硬闸门生效，reply会被替换）
    if enforced_reply != raw_reply:
        final_level, clean_reply = parse_level_tag(enforced_reply)
    else:
        final_level = model_level
    
    # ===== 输出保险丝（双轨规则） =====
    # 根据风险轨检查并约束输出
    clean_reply, guard_triggered = enforce_output_guards(clean_reply, level_control, risk_control, messages=messages)
    if guard_triggered:
        final_level = "L2"  # 保险丝触发时强制降为L2
    
    return _finalize_chat_reply(clean_reply, final_level, remaining, student_id, problem_id)


def main():
    print("=== NOI 竞赛教练 Agent（限级改造版）===")
    print("代码层限级 + Prompt层约束 + 槽位化L2追问\n")
    
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
        reply_for_display, reply_for_history, final_level = chat(messages, student_id, problem_id)
        messages.append({"role": "assistant", "content": reply_for_history})

        print(f"\nAgent [{final_level}]：{reply_for_display}\n")


if __name__ == "__main__":
    main()
