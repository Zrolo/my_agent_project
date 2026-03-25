"""
NOI 竞赛教练 Agent - 限级改造版本
核心：代码层限级 + Prompt层在约束范围内回复 + 槽位化L2追问 + 桥梁红线控制
技术栈：Kimi API + JSON 文件
"""

import json
import os
import re
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTA_FILE = os.path.join(BASE_DIR, "quota.json")
PER_PROBLEM_HINT_LIMIT = 3
client = None

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
    "cross_slot_dump"
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


# ============ 2. 代码层输入分析函数 ============

def analyze_student_turn(user_input: str, messages: list) -> dict:
    """
    分析学生输入，产出控制对象
    
    判定顺序（固定）：
    1. L1强拦
    2. L3保留资格
    3. 贴代码无怀疑点
    4. 桥梁套取
    5. 跨槽位拼凑
    6. L2槽位分析（只要会到L2就计算）
    
    返回：
    {
        "max_level": "L1|L2|L3",
        "bridge_redline": True|False,
        "reason_tags": [...],
        "l2_slot_state": {"对象": "filled|partial|empty", ...},
        "l2_current_slot": "对象|选择|限制|最简单情况|None"
    }
    """
    user_lower = user_input.lower()
    
    # 初始化控制对象
    control = {
        "max_level": "L3",  # 默认允许到L3
        "bridge_redline": False,
        "reason_tags": [],
        "l2_slot_state": {slot: "empty" for slot in L2_SLOTS},
        "l2_current_slot": None
    }
    
    # ===== Step 1: L1 强拦 =====
    l1_triggered = False
    
    # 1A: 直接索取
    for kw in L1_DIRECT_KEYWORDS:
        if kw in user_input:
            l1_triggered = True
            control["max_level"] = "L1"
            control["reason_tags"].append("direct_request")
            break
    
    # 1B: 极短且无思考
    if not l1_triggered and len(user_input) < 15:
        for kw in L1_SHORT_NO_THINKING:
            if kw in user_lower:
                l1_triggered = True
                control["max_level"] = "L1"
                control["reason_tags"].append("direct_request")
                break
    
    # 1C: 情绪催促
    if not l1_triggered:
        for kw in L1_EMOTION_PRESSURE:
            if kw in user_input:
                l1_triggered = True
                control["max_level"] = "L1"
                control["reason_tags"].append("emotion_pressure")
                break
    
    # 1D: 只复述题意（无自己的分析）
    if not l1_triggered and _is_only_restating(user_input):
        l1_triggered = True
        control["max_level"] = "L1"
        control["reason_tags"].append("direct_request")
    
    if l1_triggered:
        return control
    
    # ===== Step 2: L3 保留资格判断 =====
    has_l3_evidence = _has_l3_evidence(user_input)
    
    if not has_l3_evidence:
        # 没有L3证据，最多到L2
        control["max_level"] = "L2"
    else:
        # 有L3证据，标记slot_fill
        control["reason_tags"].append("slot_fill")
    
    # ===== Step 3: 贴代码无怀疑点 =====
    has_code = _contains_code(user_input)
    has_doubt_point = _has_doubt_point(user_input)
    
    if has_code and not has_doubt_point:
        control["max_level"] = "L2"
        control["reason_tags"].append("code_no_target")
    
    # ===== Step 4: 桥梁套取识别 =====
    bridge_attempted = _is_bridge_attempt(user_input)
    
    if bridge_attempted:
        control["bridge_redline"] = True
        control["reason_tags"].append("bridge_attempt")
        
        if not has_l3_evidence:
            # 无L3证据但索取桥梁，压到L2
            control["max_level"] = "L2"
        # 如果有L3证据，保留L3但开启bridge_redline
    
    # ===== Step 5: 跨槽位拼凑检测 =====
    if _is_cross_slot_dump(user_input):
        control["reason_tags"].append("cross_slot_dump")
        # 不自动升到L3，限制在L2做连接验证
        if control["max_level"] == "L3" and not has_l3_evidence:
            control["max_level"] = "L2"
    
    # ===== Step 6: L2槽位分析（只要会到L2或L3，都计算槽位）=====
    # 修复：只要max_level是L2或L3，就计算槽位状态
    if control["max_level"] in ("L2", "L3"):
        control["l2_slot_state"] = _analyze_slot_filling(user_input)
        control["l2_current_slot"] = _determine_current_slot(control["l2_slot_state"])
    
    return control


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


# ============ 3. Prompt构造 ============

def build_system_prompt(control: dict, remaining: int, student_id: str, problem_id: str) -> str:
    """
    构建带控制块的System Prompt
    
    动态注入：
    - MAX_LEVEL
    - BRIDGE_REDLINE
    - REASON_TAGS
    - L2_SLOT_STATE (如果是L2)
    - L2_CURRENT_SLOT (如果是L2)
    """
    max_level = control["max_level"]
    bridge_redline = control["bridge_redline"]
    reason_tags = control["reason_tags"]
    
    base_prompt = f"""你是一名 NOI 竞赛教练助手，专门辅导 CSP-J/S、NOIP 方向的学生。

## 核心原则
你不是"答案机"，你是"思维训练器"。目标是让学生学会独立解题。

## 代码层控制指令（必须遵守）

**本次回复最高级别: {max_level}**
**桥梁红线: {'开启' if bridge_redline else '关闭'}**
**触发原因: {', '.join(reason_tags) if reason_tags else '无'}**

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

### 桥梁红线规则（bridge_redline=true时必须遵守）

**允许做的事**：
- 指出方向有问题
- 指出哪一类错误存在
- 指出哪里不完整

**禁止做的事**：
- 说出正确内容
- 补正确桥梁
- 把关键结构说出来

**一句话总结**：可以指出错，不能补正确答案。

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
        slot_state = control.get("l2_slot_state", {})
        current_slot = control.get("l2_current_slot", "对象")
        
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

    # 添加当前状态信息
    base_prompt += f"""

## 当前状态
学生：{student_id}
题目：{problem_id}
本题剩余提示次数：{remaining} / {PER_PROBLEM_HINT_LIMIT}

重要：
1. 严格遵守上面的 MAX_LEVEL 限制
2. 严格遵守桥梁红线规则
3. 回复最后一行必须是 [LEVEL:L1|L2|L3|L4] 标签
4. 不要在回复中写配额数字
"""

    return base_prompt


# ============ 4. 配额管理（保持不变） ============

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


# ============ 7. 主对话逻辑 ============

def chat(messages: list, student_id: str, problem_id: str) -> tuple[str, str]:
    """
    主对话逻辑：
    1. 检查配额
    2. 代码层分析学生输入，产出控制对象（含max_level硬限制）
    3. 构建带控制块的Prompt
    4. 调用LLM
    5. **硬闸门**：检查模型输出是否超过max_level，超限则强制降级
    6. 提取（可能被强制修改后的）标签，决定扣配额
    7. 返回 (display_reply, history_reply)
    
    返回: (reply_for_display, reply_for_history)
    """
    remaining = get_remaining_quota(student_id, problem_id)
    
    if remaining <= 0:
        farewell = generate_farewell_gift(problem_id)
        return farewell, farewell
    
    # 获取最后一条用户输入
    last_user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_msg = msg.get("content", "")
            break
    
    # 代码层分析：产出控制对象（关键：max_level是硬上限）
    control = analyze_student_turn(last_user_msg, messages)
    max_level = control["max_level"]  # 硬闸门上限
    
    # 构建带控制块的System Prompt
    system_prompt = build_system_prompt(control, remaining, student_id, problem_id)
    
    # 调用LLM
    response = get_client().chat.completions.create(
        model="moonshot-v1-8k",
        messages=[{"role": "system", "content": system_prompt}] + messages,
        temperature=0.3,
    )
    
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
    
    # 基于**强制限制后的最终级别**决定扣费和展示
    if final_level in ("L2", "L3"):
        success, remaining_after = consume_quota(student_id, problem_id)
        if success:
            reply_for_display = clean_reply + f"\n\n---\n💡 本题还剩 {remaining_after} 次提示机会"
        else:
            reply_for_display = clean_reply + "\n\n---\n⚠️ 提示配额已用完"
    else:
        reply_for_display = clean_reply + f"\n\n---\n💡 本题还剩 {remaining} 次提示机会（本次未消耗）"
    
    reply_for_history = clean_reply
    
    return reply_for_display, reply_for_history


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
        reply_for_display, reply_for_history = chat(messages, student_id, problem_id)
        messages.append({"role": "assistant", "content": reply_for_history})

        print(f"\nAgent：{reply_for_display}\n")


if __name__ == "__main__":
    main()
