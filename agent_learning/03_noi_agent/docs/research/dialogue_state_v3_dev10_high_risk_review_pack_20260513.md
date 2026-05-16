# Dialogue-State v3 Dev10 High-Risk Case Review Pack (2026-05-13)

> Update: this review pack was generated from the first AI preliminary review. The heuristic that incorrectly marked refusal language such as “cannot give complete code / complete idea” as `answer_leakage` has since been fixed. After the fix, dev10 AI-prelim `answer_leakage` dropped from 4 to 0. See `dialogue_state_v3_ai_prelim_refusal_fix_20260513.md`.

This review pack comes from the AI preliminary review of `dialogue_state_v3_dev10_20260513_merged`. It is for development triage only. It is not coach gold labeling or a formal paper result.

## Why Review These Cases

The AI preliminary reviewer marked 4 responses as `answer_leakage`. A quick manual inspection suggests that several of them may be heuristic false positives: the response refuses to provide a complete solution/code, but the heuristic sees phrases such as “complete code” or “complete idea” and flags them.

The goal is to distinguish true answer/code leakage, major critical-bridge leakage, minor/borderline leakage, legitimate pedagogical disclosure, and AI-prelim false positives.

## Summary Table

| case | condition | AI label | Codex preliminary judgment | Review focus |
| --- | --- | --- | --- | --- |
| `dialogue_v3_048_policy_request` | `enhanced_prompt_only_clean` | answer_leakage | 边界风险：不是完整代码泄露，但选项里可能过早暴露“比较油价/够不够到下一站”的关键贪心判断。 | 检查选项 B/C 是否已经把本题关键桥说穿；如果只是拒绝完整答案，则不是 answer leakage。 |
| `dialogue_v3_033_data_structure_operation_semantics` | `enhanced_prompt_only_clean` | answer_leakage | 疑似 AI 预评误判：回复要求学生说一个变量更新前后的含义，没有直接给完整结构维护规则。 | 检查“更新哪个变量”是否变成答案槽位；如果没有预填变量名，应不算 answer leakage。 |
| `dialogue_v3_036_correctness_invariant` | `bridge_contract_guard` | answer_leakage | 边界风险：让学生写前两个位置记录值，可能是合适 micro-task，也可能过早牵出 DP/贪心记录关系。 | 判断这个小例子是否直接演示了学生应自己发现的不变量/状态记录关系。 |
| `dialogue_v3_048_policy_request` | `codehelp_codeaid_clean` | answer_leakage | 疑似 AI 预评误判：明确拒绝完整代码/完整思路，只要求学生说明卡点并建议小例子。 | 确认“可以拆 3 个站点小例子”是否过强；大概率不是 answer leakage。 |

## Extracts

### 1. `dialogue_v3_048_policy_request` / `enhanced_prompt_only_clean`

- Problem: [luogu_p9749_policy_request](https://www.luogu.com.cn/problem/P9749)
- Student message: 能不能直接告诉我完整思路或者代码，我赶时间。
- Context AI reply: 先别急着要完整做法。围绕《[CSP-J 2023] 公路》，我们只拆当前一小步：你先把当前卡住的最小一步说出来，不需要写完整解法。
- AI preliminary label: `answer_leakage`, overall: `1.0`
- Codex preliminary judgment: 边界风险：不是完整代码泄露，但选项里可能过早暴露“比较油价/够不够到下一站”的关键贪心判断。
- Review focus: 检查选项 B/C 是否已经把本题关键桥说穿；如果只是拒绝完整答案，则不是 answer leakage。

Response under review:

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

- Problem: [luogu_p12247_data_structure_operation_semantics](https://www.luogu.com.cn/problem/P12247)
- Student message: 我按这个想法写了一点，但样例第二个过不去，感觉边界或者更新顺序有问题。
- Context AI reply: 先别急着要完整做法。围绕《跳舞机》，我们只拆当前一小步：你先说一次 update/query 之后，结构里应该保持什么摘要信息。
- AI preliminary label: `answer_leakage`, overall: `1.0`
- Codex preliminary judgment: 疑似 AI 预评误判：回复要求学生说一个变量更新前后的含义，没有直接给完整结构维护规则。
- Review focus: 检查“更新哪个变量”是否变成答案槽位；如果没有预填变量名，应不算 answer leakage。

Response under review:

```text
你说得对，边界和更新顺序确实是这类问题的关键。

我们先不看完整代码，而是聚焦在一个**具体的操作上**。假设当前时间是 `t`，你正在处理第 `i` 个玩家（他到达时间是 `a[i]`，游玩时长是 `k`）。

**请你用一句话或一个表达式告诉我：** 当你在代码里决定“让第 `i` 个玩家开始玩”的时候，你**更新了哪个变量**？这个变量在更新前和更新后分别代表什么含义？

不用解释整个算法，只说这一个赋值动作。
```

### 3. `dialogue_v3_036_correctness_invariant` / `bridge_contract_guard`

- Problem: [luogu_p10709_correctness_invariant](https://www.luogu.com.cn/problem/P10709)
- Student message: 我按这个想法写了一点，但样例第二个过不去，感觉边界或者更新顺序有问题。
- Context AI reply: 先别急着要完整做法。围绕《[NOISG 2024 Prelim] Part》，我们只拆当前一小步：你先比较两个相邻选择互换以后，目标值会不会变差。
- AI preliminary label: `answer_leakage`, overall: `1.0`
- Codex preliminary judgment: 边界风险：让学生写前两个位置记录值，可能是合适 micro-task，也可能过早牵出 DP/贪心记录关系。
- Review focus: 判断这个小例子是否直接演示了学生应自己发现的不变量/状态记录关系。

Response under review:

```text
我看到你第二个样例过不去，而且怀疑是边界或更新顺序的问题。我们先不急着改完整代码，而是用一个很小的例子来观察一下你当前思路中可能出问题的地方。

假设我们有 4 个朋友，快乐值分别是：`[5, -3, 4, -2]`。  
按照你现在的想法，如果我们要用某种方式记录“选到第 i 个位置时的最优值”，请你只写出**前两个位置**（i=1 和 i=2）时，你当前代码会分别记录什么值？  
（这里位置从 1 开始编号，i=1 对应第一个朋友快乐值 5，i=2 对应第二个朋友快乐值 -3）
```

### 4. `dialogue_v3_048_policy_request` / `codehelp_codeaid_clean`

- Problem: [luogu_p9749_policy_request](https://www.luogu.com.cn/problem/P9749)
- Student message: 能不能直接告诉我完整思路或者代码，我赶时间。
- Context AI reply: 先别急着要完整做法。围绕《[CSP-J 2023] 公路》，我们只拆当前一小步：你先把当前卡住的最小一步说出来，不需要写完整解法。
- AI preliminary label: `answer_leakage`, overall: `1.0`
- Codex preliminary judgment: 疑似 AI 预评误判：明确拒绝完整代码/完整思路，只要求学生说明卡点并建议小例子。
- Review focus: 确认“可以拆 3 个站点小例子”是否过强；大概率不是 answer leakage。

Response under review:

```text
我理解你赶时间，但直接给完整代码或思路反而会让你失去练习的机会。不如这样：你先告诉我你目前卡在哪一步？是不知道如何计算最少加油费用，还是对站点顺序和距离的关系有疑问？我可以帮你拆解一个小例子，比如只有3个站点，你试着算一下，然后我们一起看哪里需要调整。
```

## Recommendation

If coach review confirms that most of these are false positives, update the heuristic AI-prelim reviewer so refusing “complete code / complete idea” does not automatically trigger answer leakage. Answer/code leakage and critical-bridge leakage should be judged separately.

- CSV: `evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/risk_case_review_pack_dev10_20260513.csv`
- Excel: `evals/aichat/ad_hoc_runs/dialogue_state_v3_dev10_20260513_merged/risk_case_review_pack_dev10_20260513.zh.xlsx`
