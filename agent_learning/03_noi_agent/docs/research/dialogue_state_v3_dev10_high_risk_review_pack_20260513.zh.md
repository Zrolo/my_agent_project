# Dialogue-State v3 Dev10 高风险样例复核包（2026-05-13）

> 更新：本复核包基于首次 AI 预评生成。后续已修复“拒绝完整代码/完整思路”被误判为 `answer_leakage` 的启发式规则。修复后 dev10 AI 预评中的 `answer_leakage` 从 4 条降为 0 条。见 `dialogue_state_v3_ai_prelim_refusal_fix_20260513.zh.md`。

本复核包来自 `dialogue_state_v3_dev10_20260513_merged` 的 AI 预评结果。它只用于开发阶段排查，不是教练 gold label，也不是论文正式结论。

## 为什么要复核

AI 预评把 4 条回复标成 `answer_leakage`。人工快速查看后，这 4 条不一定是真正的完整答案/代码泄露，其中多条更像启发式规则误伤：模型在拒绝“完整代码/完整思路”时提到了这些词，被规则当成泄露风险。

本轮复核重点不是重新打全量分，而是判断这些红标样例到底属于：

- 真正 answer/code leakage；
- serious/major critical bridge leakage；
- minor/borderline bridge leakage；
- 合理教学透露；
- AI 预评误判。

## 快速总表

| case | condition | AI预评 | Codex初判 | 复核重点 |
| --- | --- | --- | --- | --- |
| `dialogue_v3_048_policy_request` | `enhanced_prompt_only_clean` | answer_leakage | 边界风险：不是完整代码泄露，但选项里可能过早暴露“比较油价/够不够到下一站”的关键贪心判断。 | 检查选项 B/C 是否已经把本题关键桥说穿；如果只是拒绝完整答案，则不是 answer leakage。 |
| `dialogue_v3_033_data_structure_operation_semantics` | `enhanced_prompt_only_clean` | answer_leakage | 疑似 AI 预评误判：回复要求学生说一个变量更新前后的含义，没有直接给完整结构维护规则。 | 检查“更新哪个变量”是否变成答案槽位；如果没有预填变量名，应不算 answer leakage。 |
| `dialogue_v3_036_correctness_invariant` | `bridge_contract_guard` | answer_leakage | 边界风险：让学生写前两个位置记录值，可能是合适 micro-task，也可能过早牵出 DP/贪心记录关系。 | 判断这个小例子是否直接演示了学生应自己发现的不变量/状态记录关系。 |
| `dialogue_v3_048_policy_request` | `codehelp_codeaid_clean` | answer_leakage | 疑似 AI 预评误判：明确拒绝完整代码/完整思路，只要求学生说明卡点并建议小例子。 | 确认“可以拆 3 个站点小例子”是否过强；大概率不是 answer leakage。 |

## 逐条摘录

### 1. `dialogue_v3_048_policy_request` / `enhanced_prompt_only_clean`

- 原题：[luogu_p9749_policy_request](https://www.luogu.com.cn/problem/P9749)
- 学生当前问题：能不能直接告诉我完整思路或者代码，我赶时间。
- 上下文 AI 回复：先别急着要完整做法。围绕《[CSP-J 2023] 公路》，我们只拆当前一小步：你先把当前卡住的最小一步说出来，不需要写完整解法。
- AI 预评标签：`answer_leakage`，总分：`1.0`
- Codex 初判：边界风险：不是完整代码泄露，但选项里可能过早暴露“比较油价/够不够到下一站”的关键贪心判断。
- 复核重点：检查选项 B/C 是否已经把本题关键桥说穿；如果只是拒绝完整答案，则不是 answer leakage。

AI 回复（要复核）：

```text
我理解你赶时间，但直接给完整代码反而会让你在考场上遇到变体题时无从下手。这道题的核心其实只需要想清楚一个关键判断，我帮你用最省时间的方式推进：

**先看一个极小的例子（3个站点）：**
- 距离：站点1→2是10公里，站点2→3是10公里
- 油价：站点1每升8元，站点2每升10元，站点3每升6元
- 车每升油能跑5公里

**问题：** 如果你在站点1加满油（假设油箱无限大），开到站点2时，你是应该：
A) 在站点2加油，因为油不够到终点  
B) 不在站点2加油，因为站点2的油比站点1贵，继续用站点1的油往前开  
C) 先判断油够不够到站点3，如果够就不加，如果不够就只加够到站点3的量

**请选一个，并说一句为什么。** 这个判断想通后，整道题的代码框架就出来了。
```

### 2. `dialogue_v3_033_data_structure_operation_semantics` / `enhanced_prompt_only_clean`

- 原题：[luogu_p12247_data_structure_operation_semantics](https://www.luogu.com.cn/problem/P12247)
- 学生当前问题：我按这个想法写了一点，但样例第二个过不去，感觉边界或者更新顺序有问题。
- 上下文 AI 回复：先别急着要完整做法。围绕《跳舞机》，我们只拆当前一小步：你先说一次 update/query 之后，结构里应该保持什么摘要信息。
- AI 预评标签：`answer_leakage`，总分：`1.0`
- Codex 初判：疑似 AI 预评误判：回复要求学生说一个变量更新前后的含义，没有直接给完整结构维护规则。
- 复核重点：检查“更新哪个变量”是否变成答案槽位；如果没有预填变量名，应不算 answer leakage。

AI 回复（要复核）：

```text
你说得对，边界和更新顺序确实是这类问题的关键。

我们先不看完整代码，而是聚焦在一个**具体的操作上**。假设当前时间是 `t`，你正在处理第 `i` 个玩家（他到达时间是 `a[i]`，游玩时长是 `k`）。

**请你用一句话或一个表达式告诉我：** 当你在代码里决定“让第 `i` 个玩家开始玩”的时候，你**更新了哪个变量**？这个变量在更新前和更新后分别代表什么含义？

不用解释整个算法，只说这一个赋值动作。
```

### 3. `dialogue_v3_036_correctness_invariant` / `bridge_contract_guard`

- 原题：[luogu_p10709_correctness_invariant](https://www.luogu.com.cn/problem/P10709)
- 学生当前问题：我按这个想法写了一点，但样例第二个过不去，感觉边界或者更新顺序有问题。
- 上下文 AI 回复：先别急着要完整做法。围绕《[NOISG 2024 Prelim] Part》，我们只拆当前一小步：你先比较两个相邻选择互换以后，目标值会不会变差。
- AI 预评标签：`answer_leakage`，总分：`1.0`
- Codex 初判：边界风险：让学生写前两个位置记录值，可能是合适 micro-task，也可能过早牵出 DP/贪心记录关系。
- 复核重点：判断这个小例子是否直接演示了学生应自己发现的不变量/状态记录关系。

AI 回复（要复核）：

```text
我看到你第二个样例过不去，而且怀疑是边界或更新顺序的问题。我们先不急着改完整代码，而是用一个很小的例子来观察一下你当前思路中可能出问题的地方。

假设我们有 4 个朋友，快乐值分别是：`[5, -3, 4, -2]`。  
按照你现在的想法，如果我们要用某种方式记录“选到第 i 个位置时的最优值”，请你只写出**前两个位置**（i=1 和 i=2）时，你当前代码会分别记录什么值？  
（这里位置从 1 开始编号，i=1 对应第一个朋友快乐值 5，i=2 对应第二个朋友快乐值 -3）
```

### 4. `dialogue_v3_048_policy_request` / `codehelp_codeaid_clean`

- 原题：[luogu_p9749_policy_request](https://www.luogu.com.cn/problem/P9749)
- 学生当前问题：能不能直接告诉我完整思路或者代码，我赶时间。
- 上下文 AI 回复：先别急着要完整做法。围绕《[CSP-J 2023] 公路》，我们只拆当前一小步：你先把当前卡住的最小一步说出来，不需要写完整解法。
- AI 预评标签：`answer_leakage`，总分：`1.0`
- Codex 初判：疑似 AI 预评误判：明确拒绝完整代码/完整思路，只要求学生说明卡点并建议小例子。
- 复核重点：确认“可以拆 3 个站点小例子”是否过强；大概率不是 answer leakage。

AI 回复（要复核）：

```text
我理解你赶时间，但直接给完整代码或思路反而会让你失去练习的机会。不如这样：你先告诉我你目前卡在哪一步？是不知道如何计算最少加油费用，还是对站点顺序和距离的关系有疑问？我可以帮你拆解一个小例子，比如只有3个站点，你试着算一下，然后我们一起看哪里需要调整。
```

## 建议

如果人工复核确认其中多数是误判，下一步应修 `auto_fill_response_review.py` 的启发式规则：拒绝“完整代码/完整思路”的文字不应自动触发 answer leakage；同时把 answer leakage 和 critical bridge leakage 分开判断。

- CSV：`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/risk_case_review_pack_dev10_20260513.csv`
- Excel：`evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/risk_case_review_pack_dev10_20260513.zh.xlsx`
