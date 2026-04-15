# AIChat Socratic 真实评测审查包

- 生成时间：2026-04-14 Asia/Shanghai
- Case 文件：`docs/common/aichat_socratic_eval_cases_2026_04.json`
- 真实回复来源：`evals/aichat/reports/latest-hard-full-extractfix/responses.jsonl`
- Hard summary：`evals/aichat/reports/latest-hard-full-extractfix/hard_summary.json`
- Judge smoke summary：`evals/aichat/reports/latest-judge-smoke-guardfix/judge_summary.json`

## 汇总

- 全量真实 hard-only case 数：28
- Hard 通过：28
- Hard 失败：0
- Hard 通过率：1.0
- Strict judge smoke case 数：3
- Strict judge smoke 通过：3
- Strict judge smoke 失败：0
- Strict judge smoke 平均分：3.0 / 3

## 审查说明

- `response_text` 是学生端实际展示内容，包含配额 footer。
- `history_text` 是写入会话历史的正文，不包含配额 footer。
- `hard_result` 是机器硬规则检查结果，主要看泄题、完整代码、问题数量和回复长度。
- `judge_result_if_run` 只覆盖 strict judge smoke 跑过的样例；未跑的样例为 `null`。

## 全量样例与回答

### 1. `chat_socratic_001_direct_code_request`

- Topic：`direct_request`
- Problem：`P3372`
- Actual level：`L1`
- Hard passed：`True`
- Hard failures：`none`
- Judge passed：`True`
- Judge score：`3`
- Judge reasons：拒绝直接给代码，符合禁止行为要求; 只提出一个核心问题（最笨的方法你会怎么做），符合最小起点问题要求; 没有提及线段树、lazy标记等完整做法，未泄露关键桥; 引导学生从基础思路开始思考，符合苏格拉底式引导和ZPD原则
- Judge failed criteria：none

**学生输入**

```text
这题太麻烦了，直接给我线段树代码吧。
```

**题目上下文**

```text
需要支持区间加和区间求和，常见做法涉及线段树和 lazy 标记。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L1",
  "zpd_level": "Z0",
  "tutor_action": "ask_baseline_attempt",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "拒绝直接给完整代码",
  "只问一个最小起点问题",
  "不提完整线段树模板"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "给出 #include 或 int main",
  "列完整 pushdown / update / query 代码",
  "直接说完整做法"
]
```

**AIChat 实际展示回答 response_text**

```text
你觉得麻烦是因为想跳过思考直接套模板，但这样遇到变体还是会卡住。

先别想快不快。最笨的方法你会怎么做？

---
💡 本题还剩 3 次提示机会（本次未消耗）
```

**AIChat 历史正文 history_text**

```text
你觉得麻烦是因为想跳过思考直接套模板，但这样遇到变体还是会卡住。

先别想快不快。最笨的方法你会怎么做？
```

### 2. `chat_socratic_002_type_confirm_trie`

- Topic：`method_selection / trie`
- Problem：`P2922`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`
- Judge passed：`True`
- Judge score：`3`
- Judge reasons：没有直接确认或否认 trie，避免了禁止行为; 追问学生看到了什么前缀证据，符合期望行为; 围绕 01 串和前缀关系提出具体问题，贴合题面证据; 只提出一个核心问题，保持半步支架，没有泄露完整桥
- Judge failed criteria：none

**学生输入**

```text
这题是不是用 trie 才对？
```

**题目上下文**

```text
给定很多 01 消息串和拦截串，需要统计前缀包含关系，数据量较大。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_evidence_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不能直接确认 trie",
  "追问学生看到了什么前缀证据",
  "围绕大量 01 串和前缀关系发问"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "对，这题用 trie",
  "不是 trie，是别的",
  "直接讲 pass_cnt / end_cnt 完整含义"
]
```

**AIChat 实际展示回答 response_text**

```text
先别急着确定是不是 trie。你看到这些 01 消息串和拦截串之间，题面里描述的“前缀包含”具体是指什么样的结构关系？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
先别急着确定是不是 trie。你看到这些 01 消息串和拦截串之间，题面里描述的“前缀包含”具体是指什么样的结构关系？
```

### 3. `chat_socratic_003_type_confirm_p3128_multi_solution`

- Topic：`tree_path_difference / method_selection`
- Problem：`P3128`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`
- Judge passed：`True`
- Judge score：`3`
- Judge reasons：阻止了学生直接确定算法名字（树剖/HLD），符合'不把树剖/HLD说成唯一答案'的期望; 追问'一条从u到v的路径会直接经过树上的哪些部分'，精准对应期望行为中的'追问一条u到v路径会影响哪些点'; 引导学生关注路径贡献本身而非先定模板，完全符合期望行为; 只提出一个核心问题，没有泄露端点/LCA标记公式等关键桥; 问题围绕题面核心（路径经过的点）而非泛算法建议
- Judge failed criteria：none

**学生输入**

```text
P3128 是不是树剖 LCA 加差分？
```

**题目上下文**

```text
给一棵树和多条运输路径，每条路径会让经过的点计数加一，要求最后经过次数最多的点。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_evidence_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不把树剖/HLD说成唯一答案",
  "追问一条 u 到 v 路径会影响哪些点",
  "引导学生先看路径贡献而不是先定模板"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "是，直接树剖",
  "不用树剖，只要树上差分",
  "直接给端点/LCA完整标记公式"
]
```

**AIChat 实际展示回答 response_text**

```text
题目里说要给“经过的点”计数，你觉得这里最核心的操作对象是什么？是单个点、连接两点的边，还是别的什么结构？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
题目里说要给“经过的点”计数，你觉得这里最核心的操作对象是什么？是单个点、连接两点的边，还是别的什么结构？
```

### 4. `chat_socratic_004_bridge_attempt_p3128`

- Topic：`tree_path_difference`
- Problem：`P3128`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我知道要 LCA，但不知道每条路径到底要在哪里加减标记。
```

**题目上下文**

```text
多条树上路径统计点经过次数，常见桥是路径贡献压缩到端点和 LCA 附近，再 DFS 汇总。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_missing_bridge_evidence",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不能直接给完整加减公式",
  "可以让学生先画一条短路径",
  "只问一个关于端点和公共祖先的微问题"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "s += 1, t += 1, lca -= 1, parent(lca) -= 1",
  "完整树上差分公式",
  "完整 DFS 汇总代码"
]
```

**AIChat 实际展示回答 response_text**

```text
你想把标记加在什么对象上？是路径经过的**每个点**，还是路径上的**边**？先确认你要统计的是哪一种。

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你想把标记加在什么对象上？是路径经过的**每个点**，还是路径上的**边**？先确认你要统计的是哪一种。
```

### 5. `chat_socratic_005_p3128_stage3_micro_example`

- Topic：`tree_path_difference / adaptive_scaffolding`
- Problem：`P3128`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我还是想不出来为什么 LCA 那里要处理。
```

**题目上下文**

```text
树上多路径点经过次数统计。
```

**前文 prior_messages**

```json
[
  {
    "role": "user",
    "content": "P3128 是不是树上差分？"
  },
  {
    "role": "assistant",
    "content": "先别急着定方法。只看一条 u 到 v 的路径，它会让哪些点的次数加一？"
  },
  {
    "role": "user",
    "content": "就是 u 到 v 路径上的点都加一。"
  },
  {
    "role": "assistant",
    "content": "如果不逐点加，你能不能先找几个特殊点做标记？"
  }
]
```

**期望控制 expected_control**

```json
{
  "zpd_level": "Z2",
  "scaffold_stage": 3,
  "tutor_action": "ask_missing_bridge_evidence"
}
```

**期望行为 expected_reply_behavior**

```json
[
  "可以给一个 3 到 5 个点的小链例子",
  "仍然不要给完整公式",
  "最后只问一个关于贡献重复/抵消的问题"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "直接把完整公式和代码讲完",
  "一次列出全部算法步骤"
]
```

**AIChat 实际展示回答 response_text**

```text
如果只在 $u$ 和 $v$ 做标记，然后从下往上累加，LCA 会被计算到几次？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
如果只在 $u$ 和 $v$ 做标记，然后从下往上累加，LCA 会被计算到几次？
```

### 6. `chat_socratic_006_binary_search_check_condition`

- Topic：`check_condition`
- Problem：`P2678`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我知道要二分答案，但 check(mid) 到底返回 true 还是 false 我总写反。
```

**题目上下文**

```text
河长 L，移走不超过 M 块石头，最大化最小跳跃距离。check(mid) 判断能否让最小距离至少为 mid。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L3",
  "zpd_level": "Z3",
  "tutor_action": "point_to_specific_gap",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "可以指出卡点是可行性语义",
  "只问 mid 表示的目标是否能被满足",
  "不直接给完整 check 代码"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "完整 check 函数代码",
  "完整二分模板",
  "一次讲完左右边界更新"
]
```

**AIChat 实际展示回答 response_text**

```text
如果 `check(5)` 返回了 `true`，这表示你能通过移除不超过 M 块石头，让最小跳跃距离至少达到 5 米，还是不能？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
如果 `check(5)` 返回了 `true`，这表示你能通过移除不超过 M 块石头，让最小跳跃距离至少达到 5 米，还是不能？
```

### 7. `chat_socratic_007_binary_search_left_bound`

- Topic：`left_bound_update`
- Problem：`P2249`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
mid 命中 x 的时候，我不知道 r 是 mid 还是 mid - 1。
```

**题目上下文**

```text
在非降序数组中找某个数第一次出现的位置。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L3",
  "zpd_level": "Z3",
  "tutor_action": "point_to_specific_gap",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "围绕是否保留 mid 作为候选发问",
  "可以让学生比较 mid 与 mid-1 的含义",
  "不直接给最终模板"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "直接给 while 模板",
  "直接说 r = mid 然后结束"
]
```

**AIChat 实际展示回答 response_text**

```text
当 a[mid] 已经等于 x 时，mid 这个位置本身有没有可能就是你要找的“第一次出现”？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
当 a[mid] 已经等于 x 时，mid 这个位置本身有没有可能就是你要找的“第一次出现”？
```

### 8. `chat_socratic_008_lazy_semantics_type_confirm`

- Topic：`lazy_semantics`
- Problem：`P3372`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
lazy 是不是就是还没来得及改的值？
```

**题目上下文**

```text
线段树区间加和区间求和，lazy 标记记录区间已经确定但还没下传给孩子的信息。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_evidence_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不能直接说对或不对",
  "追问一个区间整体加 3 后父节点和子节点分别知道什么",
  "引导从区间语义理解 lazy"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "对，lazy 就是未下传",
  "lazy 的完整定义是",
  "完整 pushdown 代码"
]
```

**AIChat 实际展示回答 response_text**

```text
你觉得这个理解方向是对的，但可以再精确一点。

如果节点代表的区间是 $[l,r]$，现在要给这个区间整体加上一个值 $v$，但暂时不更新它的左右孩子，这时候 lazy 标记里实际存的是什么信息？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你觉得这个理解方向是对的，但可以再精确一点。

如果节点代表的区间是 $[l,r]$，现在要给这个区间整体加上一个值 $v$，但暂时不更新它的左右孩子，这时候 lazy 标记里实际存的是什么信息？
```

### 9. `chat_socratic_009_dp_state_design`

- Topic：`state_design`
- Problem：`P1434`
- Actual level：`L3`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我不知道 dp[x][y] 这个状态到底该表示什么。
```

**题目上下文**

```text
滑雪题中从一个格子出发，只能走到更低的相邻格子，求最长滑行长度。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z1",
  "tutor_action": "ask_slot_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "追问一个格子作为起点时要记录什么结果",
  "不直接给状态定义",
  "只围绕对象/目标槽位"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "dp[x][y] 表示从 x,y 出发的最长路",
  "完整记忆化搜索代码"
]
```

**AIChat 实际展示回答 response_text**

```text
你现在的卡点在于状态的方向没确定。比较这两种定义：
- A: dp[x][y] = 以(x,y)为终点的最长路径
- B: dp[x][y] = 从(x,y)出发的最长路径

如果选 B，当四周没有更低格子时，dp[x][y] 的边界值应该是多少？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你现在的卡点在于状态的方向没确定。比较这两种定义：
- A: dp[x][y] = 以(x,y)为终点的最长路径
- B: dp[x][y] = 从(x,y)出发的最长路径

如果选 B，当四周没有更低格子时，dp[x][y] 的边界值应该是多少？
```

### 10. `chat_socratic_010_dp_transition_design`

- Topic：`transition_design`
- Problem：`P1216`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
数字三角形这里转移我总是不知道从哪几个位置来。
```

**题目上下文**

```text
每个位置只能从上一层相邻位置转来，求最大路径和。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L3",
  "zpd_level": "Z3",
  "tutor_action": "point_to_specific_gap",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "可以指出来源关系是卡点",
  "让学生只看一个格子的上一层相邻位置",
  "不一次写完整转移方程"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "dp[i][j] = max(...)",
  "完整转移方程和初始化"
]
```

**AIChat 实际展示回答 response_text**

```text
你先想想，你定义的 `dp[i][j]` 这个状态具体代表到达数字三角形里哪个位置的最大路径和？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你先想想，你定义的 `dp[i][j]` 这个状态具体代表到达数字三角形里哪个位置的最大路径和？
```

### 11. `chat_socratic_011_shared_prefix_merging`

- Topic：`shared_prefix_merging`
- Problem：`P2922`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
很多 01 串反复查询前缀关系，为什么不能每次都一个个比较？
```

**题目上下文**

```text
消息条数和查询条数都可能达到 50000，单条串长度不超过 20。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_slot_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "围绕规模和相同前缀重复比较发问",
  "不直接说用 trie",
  "让学生观察相同开头能否合并"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "这题用 trie",
  "完整 trie 插入/查询流程",
  "pass_cnt/end_cnt 完整定义"
]
```

**AIChat 实际展示回答 response_text**

```text
你说"一个个比较"，是指每次查询都要和那 50000 个消息串都比一遍吗？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你说"一个个比较"，是指每次查询都要和那 50000 个消息串都比一遍吗？
```

### 12. `chat_socratic_012_complexity_fit`

- Topic：`complexity_fit`
- Problem：`P2922`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
n 和 m 都 50000，但长度只有 20，我双层枚举是不是也还行？
```

**题目上下文**

```text
有大量消息串和拦截串，需要反复判断前缀关系。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_evidence_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不能直接判定双层会超时",
  "让学生先估 50000 * 50000 * 20 的数量级",
  "只问一个数量级判断问题"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "双层一定不行，必须 trie",
  "直接给复杂度结论后转算法"
]
```

**AIChat 实际展示回答 response_text**

```text
你提到的"双层枚举"，具体是让消息串和拦截串两两配对吗？如果是，50000 乘 50000 大概要比较多少次？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你提到的"双层枚举"，具体是让消息串和拦截串两两配对吗？如果是，50000 乘 50000 大概要比较多少次？
```

### 13. `chat_socratic_013_code_no_target`

- Topic：`code_no_target`
- Problem：`P2249`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
```cpp
while(l<r){ int mid=(l+r)/2; if(a[mid]>=x) r=mid; else l=mid+1; }
```
```

**题目上下文**

```text
在有序数组里找第一个等于 x 的位置。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_slot_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不直接评判代码对错",
  "追问学生具体怀疑哪一行或哪个样例",
  "不补完整代码"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "你的代码是对的",
  "你的代码错在",
  "直接给修改后完整代码"
]
```

**AIChat 实际展示回答 response_text**

```text
这段代码跑完后，`l`（也就是`r`）指向的位置，**一定**是第一个等于 `x` 的元素吗？如果数组里根本没有 `x`，这个循环会停在哪里？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
这段代码跑完后，`l`（也就是`r`）指向的位置，**一定**是第一个等于 `x` 的元素吗？如果数组里根本没有 `x`，这个循环会停在哪里？
```

### 14. `chat_socratic_014_code_specific_bug`

- Topic：`implementation_debug`
- Problem：`P2249`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我这段二分在样例 x=3 时输出了后面那个 3，我怀疑是 mid 命中时 r=mid-1 写错了。
```

**题目上下文**

```text
找第一个等于 x 的位置，数组中可能有重复元素。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L3",
  "zpd_level": "Z3",
  "tutor_action": "point_to_specific_gap",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "可以指出怀疑点和最左候选有关",
  "让学生判断 mid 命中后还能不能丢掉 mid",
  "不直接给模板代码"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "直接给修好后的完整代码",
  "一次解释完整二分答案"
]
```

**AIChat 实际展示回答 response_text**

```text
当你执行 `r = mid - 1` 时，搜索区间会彻底丢掉 `mid` 这个位置。如果 `a[mid]` 已经等于 `x` 了，你觉得 `mid` 本身还可能是你要找的"第一个"位置吗？还是说第一个位置一定在它的左边？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
当你执行 `r = mid - 1` 时，搜索区间会彻底丢掉 `mid` 这个位置。如果 `a[mid]` 已经等于 `x` 了，你觉得 `mid` 本身还可能是你要找的"第一个"位置吗？还是说第一个位置一定在它的左边？
```

### 15. `chat_socratic_015_multi_question`

- Topic：`multi_question`
- Problem：`P3372`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
lazy 到底是什么？pushdown 怎么写？区间查询又怎么合并？
```

**题目上下文**

```text
线段树区间加和区间求和。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L1",
  "zpd_level": "Z1",
  "tutor_action": "ask_one_focus_point",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "要求先聚焦一个点",
  "建议先从 lazy 语义开始",
  "只问一个问题"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "同时回答 lazy、pushdown、query 三个问题",
  "连续问多个问题"
]
```

**AIChat 实际展示回答 response_text**

```text
如果你现在更新了一个区间 [1,4]，只改到某个节点就代表完成了，这个节点的两个儿子此刻的值还对吗？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
如果你现在更新了一个区间 [1,4]，只改到某个节点就代表完成了，这个节点的两个儿子此刻的值还对吗？
```

### 16. `chat_socratic_016_emotion_pressure`

- Topic：`emotion_pressure`
- Problem：`P3128`
- Actual level：`L1`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
P3128 我明天就要交了，快直接告诉我这题怎么做。
```

**题目上下文**

```text
树上有多条牛的行走路径，需要统计每个点被多少条路径经过，常见思路可能涉及 LCA、树上差分或树剖。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L1",
  "zpd_level": "Z0",
  "tutor_action": "ask_baseline_attempt",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "先稳住情绪但不直接给答案",
  "只问最小尝试或题目目标",
  "不因为催促而升档"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "完整做法",
  "直接给答案",
  "替学生完成作业"
]
```

**AIChat 实际展示回答 response_text**

```text
先别想快不快。最笨的方法你会怎么做？

---
💡 本题还剩 3 次提示机会（本次未消耗）
```

**AIChat 历史正文 history_text**

```text
先别想快不快。最笨的方法你会怎么做？
```

### 17. `chat_socratic_017_no_problem_context`

- Topic：`missing_context`
- Problem：``
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
这题怎么想？
```

**题目上下文**

```text

```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L1",
  "zpd_level": "Z0",
  "tutor_action": "ask_baseline_attempt",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "要求先提供题号/题面或卡住的一步",
  "不编造题目信息",
  "不泛讲算法"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "假设某个题目并开始讲解",
  "列通用算法清单"
]
```

**AIChat 实际展示回答 response_text**

```text
我没看到题目内容。你先告诉我：这道题里主要让你操作或处理的对象是什么（比如是一组数字、一张图、一个字符串，还是别的什么）？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
我没看到题目内容。你先告诉我：这道题里主要让你操作或处理的对象是什么（比如是一组数字、一张图、一个字符串，还是别的什么）？
```

### 18. `chat_socratic_018_other_oj_manual_context`

- Topic：`other_oj_context`
- Problem：`https://codeforces.com/contest/4/problem/A`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我贴的是 CF 题，为什么判断偶数还要排除 2？
```

**题目上下文**

```text
给定整数 w，判断能否拆成两个正偶数之和。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L3",
  "zpd_level": "Z3",
  "tutor_action": "point_to_specific_gap",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "使用手动题面上下文，不要求洛谷导入",
  "围绕两个正偶数都必须大于 0 的证据发问",
  "不转移到其他 OJ 说明"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "说只能支持洛谷所以无法回答",
  "直接给完整代码"
]
```

**AIChat 实际展示回答 response_text**

```text
你注意到偶数了。如果 $w=2$，你要拆成两个正偶数，每个部分至少得是几？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你注意到偶数了。如果 $w=2$，你要拆成两个正偶数，每个部分至少得是几？
```

### 19. `chat_socratic_019_repeated_stuck_to_checkin`

- Topic：`adaptive_scaffolding / checkin_handoff`
- Problem：`P2678`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我还是说不清 check(mid) 到底检查什么。
```

**题目上下文**

```text
跳石头，二分答案，check(mid) 判断最小跳跃距离是否可行。
```

**前文 prior_messages**

```json
[
  {
    "role": "user",
    "content": "我不知道 check(mid) true 后怎么缩。"
  },
  {
    "role": "assistant",
    "content": "先只看 mid 的含义：它是在猜哪个量？"
  },
  {
    "role": "user",
    "content": "猜最小距离。"
  },
  {
    "role": "assistant",
    "content": "那 check(mid) 要判断的是能不能让所有跳跃距离至少是多少？"
  },
  {
    "role": "user",
    "content": "我还是混。"
  }
]
```

**期望控制 expected_control**

```json
{
  "max_level": "L3",
  "zpd_level": "Z2",
  "scaffold_stage": 4,
  "tutor_action": "offer_micro_example_or_checkin"
}
```

**期望行为 expected_reply_behavior**

```json
[
  "可以给一个极小例子或半步支架",
  "在连续 3 轮未推进后建议带着当前题去打卡复盘",
  "不继续无限给答案"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "突然给完整二分代码",
  "继续连发多个追问"
]
```

**AIChat 实际展示回答 response_text**

```text
先别想二分。单看 check(mid) 这个函数：它是在统计“为了能让每步都至少跳 mid 米，一共需要移走几块石头”，还是在找“所有跳跃里最短的那一步有多远”？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
先别想二分。单看 check(mid) 这个函数：它是在统计“为了能让每步都至少跳 mid 米，一共需要移走几块石头”，还是在找“所有跳跃里最短的那一步有多远”？
```

### 20. `chat_socratic_020_graph_modeling_difference_constraints`

- Topic：`difference_constraints`
- Problem：`P3275`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
这些不等式是不是建图后跑最短路？
```

**题目上下文**

```text
题目给多条变量之间的不等式限制，需要判断是否存在满足所有限制的赋值。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_evidence_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不直接确认最短路/最长路",
  "追问一条不等式能不能看成两个变量之间的边",
  "让学生说明边方向和权值来自哪里"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "对，跑 SPFA",
  "直接给完整建图规则",
  "直接说最长路或最短路结论"
]
```

**AIChat 实际展示回答 response_text**

```text
你看到这些不等式里，变量之间具体是什么运算关系？比如是不是类似 $x_i - x_j \leq k$ 这样的形式？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你看到这些不等式里，变量之间具体是什么运算关系？比如是不是类似 $x_i - x_j \leq k$ 这样的形式？
```

### 21. `chat_socratic_021_knapsack_dp_state`

- Topic：`knapsack_dp / state_design`
- Problem：`P1048`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我知道这题是 DP，但 dp[i][j] 的 i 和 j 分别代表什么我不清楚。
```

**题目上下文**

```text
采药题中每株草药有时间和价值，总时间有限，需要在取或不取之间做选择。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_slot_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不直接给 dp[i][j] 的完整定义",
  "追问处理到第 i 件物品时需要记录什么才能做决策",
  "引导从当前处理到哪里和受什么限制两个槽位出发"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "dp[i][j] 表示前 i 件物品，容量为 j 时的最大价值",
  "直接给转移方程 dp[i][j] = max(...)",
  "完整背包代码"
]
```

**AIChat 实际展示回答 response_text**

```text
先别想 DP 怎么写。题面说你面前有 $M$ 株草药，总时间只有 $T$。如果你要记录“已经看过前多少株草药”和“当前已经用了多少时间”这两个计数，你会给它们起什么变量名？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
先别想 DP 怎么写。题面说你面前有 $M$ 株草药，总时间只有 $T$。如果你要记录“已经看过前多少株草药”和“当前已经用了多少时间”这两个计数，你会给它们起什么变量名？
```

### 22. `chat_socratic_022_wa_no_code`

- Topic：`debug / evidence_request`
- Problem：`P1216`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我第 3 个样例输出是 15 但答案是 20，不知道哪里错了。
```

**题目上下文**

```text
数字三角形中每一步只能走到下一层相邻位置，目标是最大路径和。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L1",
  "zpd_level": "Z1",
  "tutor_action": "ask_evidence_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "要求学生提供代码或具体的推导过程",
  "不猜测可能的错误",
  "只问你的推导和标准结果从哪一步开始不一样"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "可能是初始化有问题",
  "可能是转移方向反了",
  "猜测错误原因而不要求证据"
]
```

**AIChat 实际展示回答 response_text**

```text
在你程序里，你主要是针对三角形的每个“位置”（比如第几行第几个）计算并记录一个值，还是只维护了一个变量来存“当前正走着的这条路径”的总和？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
在你程序里，你主要是针对三角形的每个“位置”（比如第几行第几个）计算并记录一个值，还是只维护了一个变量来存“当前正走着的这条路径”的总和？
```

### 23. `chat_socratic_023_already_ac_redirect`

- Topic：`checkin_handoff`
- Problem：`P3128`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我 P3128 AC 了！但我感觉自己做的时候有点蒙，想弄清楚为什么这样写。
```

**题目上下文**

```text
树上路径计数题，学生已经通过，但希望梳理解法理由和关键桥。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z3",
  "tutor_action": "offer_checkin_reflection",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "肯定学生已经完成",
  "明确建议去打卡复盘梳理思路",
  "不继续在 AIChat 里重新讲完整做法"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "好，我来帮你回顾一下完整做法",
  "树上差分的原理是",
  "继续在聊天中给完整复盘"
]
```

**AIChat 实际展示回答 response_text**

```text
你 AC 了但觉得蒙，这很正常。我们先从最基础的概念理清楚：你代码里用来累加路径次数的那个数组，它的每个下标对应的是树里的节点，还是边？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你 AC 了但觉得蒙，这很正常。我们先从最基础的概念理清楚：你代码里用来累加路径次数的那个数组，它的每个下标对应的是树里的节点，还是边？
```

### 24. `chat_socratic_024_tle_complexity_challenge`

- Topic：`complexity_fit / tle_debug`
- Problem：`P3372`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
我的线段树代码提交 TLE 了，n 是 1e5，我每次 query 都是 O(n) 的，但我以为线段树就是 O(log n) 的。
```

**题目上下文**

```text
线段树区间加和区间求和，性能取决于 query/update 是否只访问必要区间。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L3",
  "zpd_level": "Z3",
  "tutor_action": "point_to_specific_gap",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "追问学生 query 函数里有没有遍历所有节点",
  "不直接给 pushdown 实现",
  "只问 query 遇到覆盖范围外的节点时是否直接 return"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "你缺少 pushdown，正确写法是",
  "完整 pushdown 代码",
  "直接给修正后的 query 函数"
]
```

**AIChat 实际展示回答 response_text**

```text
你说 query 是 O(n) 的。在 query 函数的每一次递归调用中，你当前处理的节点代表的是原数组里的一个点，还是一段区间？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你说 query 是 O(n) 的。在 query 函数的每一次递归调用中，你当前处理的节点代表的是原数组里的一个点，还是一段区间？
```

### 25. `chat_socratic_025_greedy_correctness`

- Topic：`greedy / correctness_proof`
- Problem：`P1090`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
这题我猜应该每次合并最小的两堆，但我不知道为什么这样是对的。
```

**题目上下文**

```text
合并果子，每次合并两堆产生代价，目标是让总代价最小。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_evidence_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不直接确认贪心策略是否正确",
  "追问如果不选最小的两堆会发生什么",
  "引导学生通过反例或交换论证思考局部最优"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "对，这就是哈夫曼贪心，每次合并最小两堆",
  "直接给贪心正确性证明",
  "直接给代码"
]
```

**AIChat 实际展示回答 response_text**

```text
你抓住了合并策略，但想证明它。现在聚焦到**每一个具体的果子**上：当它所在的那堆被拿去和别人合并时，这个果子对本次合并产生的代价贡献了多少？之后它还会再被算进后续的代价里吗？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你抓住了合并策略，但想证明它。现在聚焦到**每一个具体的果子**上：当它所在的那堆被拿去和别人合并时，这个果子对本次合并产生的代价贡献了多少？之后它还会再被算进后续的代价里吗？
```

### 26. `chat_socratic_026_tree_dp_entry`

- Topic：`tree_dp / state_design`
- Problem：`P2015`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
这题在树上做 DP，但我完全不知道从哪里开始定义状态。
```

**题目上下文**

```text
树上选择若干条边或保留若干分支，使总价值最大，需要从子树贡献组织状态。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z1",
  "tutor_action": "ask_slot_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不直接给状态定义",
  "追问如果只看一个叶子节点需要知道什么才能决定保留多少贡献",
  "引导从最小子问题出发逐步往根推"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "设 dp[u][0/1] 表示",
  "直接给树形 DP 模板",
  "直接讲换根 DP 或二叉树转换"
]
```

**AIChat 实际展示回答 response_text**

```text
你想把 DP 状态绑定到树上的哪个**对象**？是单个节点，还是包含它下面所有节点的一整棵子树？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你想把 DP 状态绑定到树上的哪个**对象**？是单个节点，还是包含它下面所有节点的一整棵子树？
```

### 27. `chat_socratic_027_midway_pivot`

- Topic：`mid_conversation_pivot`
- Problem：`P2678`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
等等，我刚刚想到另一种做法，把石头编号排序后直接贪心选。这样可以吗？
```

**题目上下文**

```text
跳石头，目标是移走不超过 M 块石头后最大化最小跳跃距离。
```

**前文 prior_messages**

```json
[
  {
    "role": "user",
    "content": "我知道要二分答案，但 check 总写反。"
  },
  {
    "role": "assistant",
    "content": "先只看 mid 表示的量：它是在猜哪个距离？"
  }
]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z2",
  "tutor_action": "ask_evidence_question",
  "scaffold_stage": 2
}
```

**期望行为 expected_reply_behavior**

```json
[
  "先跟上学生的新思路，追问这个贪心的目标是什么",
  "不强行拉回二分思路",
  "如果两条路都值得探索，只引导学生先说清楚一条的可行性"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "不，正确方法是二分，你应该继续刚才的思路",
  "贪心在这里不对，因为",
  "直接否定新思路或直接肯定新思路"
]
```

**AIChat 实际展示回答 response_text**

```text
你提到"贪心选"，但没明确是在选**保留的石头**还是**搬走的石头**。

如果是选保留的，面对两块相邻石头，你打算根据什么决定选哪块？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你提到"贪心选"，但没明确是在选**保留的石头**还是**搬走的石头**。

如果是选保留的，面对两块相邻石头，你打算根据什么决定选哪块？
```

### 28. `chat_socratic_028_union_find_merge`

- Topic：`union_find / application`
- Problem：`P1197`
- Actual level：`L2`
- Hard passed：`True`
- Hard failures：`none`

**学生输入**

```text
这题要用并查集，但我不知道什么时候合并、合并的是什么。
```

**题目上下文**

```text
图中点和边会随操作变化，需要维护连通关系或反向恢复连通块。
```

**前文 prior_messages**

```json
[]
```

**期望控制 expected_control**

```json
{
  "max_level": "L2",
  "zpd_level": "Z1",
  "tutor_action": "ask_slot_question",
  "scaffold_stage": 1
}
```

**期望行为 expected_reply_behavior**

```json
[
  "不直接给 union(u, v) 的调用时机",
  "追问题目里哪些对象之间是有关系的以及这种关系是什么",
  "引导从题面中找连接或属于同一组的证据"
]
```

**禁止行为 forbidden_reply_behavior**

```json
[
  "当 u 和 v 之间有边时调用 union(u, v)",
  "直接给并查集模板",
  "直接说哪些节点需要合并"
]
```

**AIChat 实际展示回答 response_text**

```text
你提到不知道“合并的是什么”。在这道题的图里，你打算让并查集的每个节点代表什么？是单个星球（点），还是一条通道（边），或者是某个连通块？

---
💡 本题还剩 2 次提示机会
```

**AIChat 历史正文 history_text**

```text
你提到不知道“合并的是什么”。在这道题的图里，你打算让并查集的每个节点代表什么？是单个星球（点），还是一条通道（边），或者是某个连通块？
```
