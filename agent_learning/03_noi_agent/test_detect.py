import json
import os

QUOTA_FILE = 'quota.json'
TEST_STUDENT = '测试学生'
TEST_PROBLEM = 'P1001'
PER_PROBLEM_HINT_LIMIT = 3

# 清理旧的测试数据
if os.path.exists(QUOTA_FILE):
    with open(QUOTA_FILE, 'r') as f:
        all_quota = json.load(f)
    if TEST_STUDENT in all_quota:
        del all_quota[TEST_STUDENT]
        with open(QUOTA_FILE, 'w') as f:
            json.dump(all_quota, f, ensure_ascii=False, indent=2)

def detect_quota_consumption(reply):
    """
    检测LLM回复是否触发了L2（方向提示）或L3（代码片段）
    返回 True 表示需要消耗配额
    """
    reply_stripped = reply.strip()
    
    # 1. 回复很短，大概率是L1引导反问
    if len(reply_stripped) < 30:
        return False
    
    # 2. 检测L3代码片段特征
    code_indicators = [
        "```",
        "`",
        "for ",
        "if ",
        "def ",
        "return",
        "range(",
        "print(",
        "# ",
    ]
    
    for indicator in code_indicators:
        if indicator in reply_stripped:
            return True
    
    # 3. 检测L2方向提示关键词（中文）
    hint_keywords = [
        "试试",
        "可以考虑",
        "建议",
        "尝试",
        "想一下",
        "思考一下",
        "优化",
        "复杂度",
        "时间复杂度",
        "空间复杂度",
        "前缀和",
        "差分",
        "单调",
        "单调栈",
        "单调队列",
        "二分",
        "二分查找",
        "二分搜索",
        "递归",
        "记忆化",
        "状态转移",
        "dp",
        "动态规划",
        "贪心",
        "bfs",
        "dfs",
        "广搜",
        "深搜",
        "搜索",
        "图论",
        "树",
        "链表",
        "栈",
        "队列",
        "哈希",
        "散列表",
        "并查集",
        "最短路",
        "最小生成树",
        "拓扑排序",
        "剪枝",
        "回溯",
        "分治",
        "滑动窗口",
        "双指针",
    ]
    
    reply_lower = reply_stripped.lower()
    for keyword in hint_keywords:
        if keyword in reply_lower:
            return True
    
    # 4. 默认不消耗（保守策略）
    return False

print("=" * 60)
print("修复后测试：detect_quota_consumption")
print("=" * 60)

# 测试L1（不应扣配额）
print("\n【L1回复 - 不应扣配额】")
l1_cases = [
    "请先告诉我：\n1. 你读完题目后的第一个思路是什么？\n2. 你尝试了什么方法？",
    "请先描述你的思考过程。",
    "这道题你需要先自己思考一下。",
]
for i, reply in enumerate(l1_cases, 1):
    result = detect_quota_consumption(reply)
    status = "✅" if not result else "❌ 误判"
    print(f"  回复{i} ({len(reply)}字): {status}")

# 测试L2/L3（应扣配额）
print("\n【L2/L3回复 - 应扣配额】")
l2_l3_cases = [
    ("试试用二分查找，注意边界条件。", "方向提示"),
    ("这里可以用前缀和优化，把O(n²)降到O(n)。", "算法建议"),
    ("建议用递归+记忆化的方式，避免重复计算。", "建议+算法"),
    ("考虑一下单调栈的性质，维护一个递增序列。", "算法提示"),
    ("这个题需要用DFS搜索所有可能的状态。", "算法关键词"),
    ("优化一下时间复杂度，用哈希表可以做到O(n)。", "优化建议"),
]

all_pass = True
for reply, desc in l2_l3_cases:
    result = detect_quota_consumption(reply)
    status = "✅" if result else "❌ 漏检"
    if not result:
        all_pass = False
    print(f"  [{desc}]: {status}")
    if not result:
        print(f"    内容: {reply[:50]}...")

print("\n" + "=" * 60)
if all_pass:
    print("✅ 所有测试通过！修复成功。")
else:
    print("❌ 仍有漏检，需要继续调整。")
print("=" * 60)
