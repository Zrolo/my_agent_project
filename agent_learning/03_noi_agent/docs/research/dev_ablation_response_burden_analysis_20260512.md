# Dev Ablation Response Burden Analysis (2026-05-12)

This report adds a heuristic student-response-burden signal to existing dev ablation blind-review labels. It does not regenerate responses and should not be treated as coach gold.

- Input labels: `docs/research/coach_response_review_labels_dev_ablation_safe_scaffold_20260512.jsonl`
- Rows: 120
- Cases: 10
- Burden counts: {'low': 40, 'medium': 62, 'high': 18}
- Burden source counts: {'heuristic': 120}

## Condition Summary

| condition | n | low/medium/high | high rate | overall | next-step | ready | show yes/border/no | leak no/minor/major+answer |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_clean | 10 | 5/2/3 | 0.3 | 4.0 | 1.9 | 8/10 | 8/2/0 | 2/8/0 |
| bridge_contract_guard | 10 | 4/1/5 | 0.5 | 4.4 | 2.0 | 8/10 | 8/2/0 | 5/3/2 |
| bridge_contract_guard_repair | 10 | 5/1/4 | 0.4 | 4.3 | 2.0 | 9/10 | 9/1/0 | 5/5/0 |
| bridge_contract_safe_scaffold | 10 | 7/3/0 | 0.0 | 1.0 | 1.0 | 0/10 | 0/0/10 | 10/0/0 |
| bridge_inspired_expert_decision_clean | 10 | 1/9/0 | 0.0 | 3.6 | 1.5 | 5/10 | 5/5/0 | 4/5/1 |
| codehelp_codeaid_clean | 10 | 3/5/2 | 0.2 | 3.6 | 1.6 | 5/10 | 5/4/1 | 6/4/0 |
| dbox_inspired_clean | 10 | 4/5/1 | 0.1 | 3.2 | 1.6 | 4/10 | 4/5/1 | 2/6/2 |
| dbox_inspired_guard | 10 | 2/8/0 | 0.0 | 3.5 | 1.8 | 7/10 | 7/2/1 | 3/6/1 |
| enhanced_prompt_only_clean | 10 | 4/3/3 | 0.3 | 3.8 | 2.0 | 6/10 | 6/3/1 | 3/5/2 |
| single_llm_structured_clean | 10 | 1/9/0 | 0.0 | 3.7 | 1.7 | 7/10 | 7/3/0 | 4/6/0 |
| single_llm_structured_guard | 10 | 2/8/0 | 0.0 | 3.6 | 1.7 | 5/10 | 5/5/0 | 6/4/0 |
| socratic_no_answer_clean | 10 | 2/8/0 | 0.0 | 2.3 | 1.3 | 1/10 | 1/8/1 | 9/1/0 |

## High-burden Examples

| case | condition | overall | show | leakage | reason | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| cp_bridge_003 | bridge_contract_guard_repair | 4.0 | yes | minor_bridge_leakage | many_questions | 我们先来聚焦一个问题：DP 数组每一格的两个下标分别代表什么？ 举一个非常小的例子——只有 2 株药草，总时间限制 T=5： - 药草1：用时3，价值2 - 药草2：用时2，价值3 请只看下面这一格： `dp[1][5]` - 第一个下标“1”在这里指的是什么范围？（提示：... |
| cp_bridge_010 | enhanced_prompt_only_clean | 3.0 | borderline | major_bridge_leakage | many_questions | 你说得对，正序枚举在某些时候确实也能更新成功，而且第一次看到这个结论时感到困惑是很正常的。关键是：**正序更新会允许同一个物品被多次使用，而01背包要求每个物品只能用一次**。 我拿一个极小的例子走一遍，你马上就能看到区别： **只有 1 个物品**，重量 = 1，价值 =... |
| cp_bridge_005 | bridge_contract_guard | 3.0 | borderline | major_bridge_leakage | many_questions | 你卡在了对 lazy 标记含义的理解上——它不是一个已经完成的操作结果，而是**一个承诺**。 下面用一个极小的例子，让你看清这个“承诺”到底代表什么。 --- **1. 这个例子要观察的桥梁问题** lazy 标记（例如在区间加中）记录的是 **“本该对这一段每个数都做的... |
| cp_bridge_002 | enhanced_prompt_only_clean | 3.0 | borderline | minor_bridge_leakage | many_questions | 你知道二分答案是对的，你卡在 “check(mid) 返回 true/false 到底对应什么移动方向” 上 —— 这是二分答案里最容易写反的点，但也是用一个极小例子就能理清的。 我们先抛开题目里的移石头个数限制，只看一个最简单的情况： 假设石头位置是 0, 3, 7, 1... |
| cp_bridge_009 | bridge_contract_guard_repair | 5.0 | yes | no_leakage | many_questions | 好问题。你卡住的地方正是“贪心选择为什么安全”的核心——我们得先看一个具体例子，再从中提炼出规律。 --- **1. 这个例子要观察的桥梁问题** 为什么选结束最早的活动，不会让后面可选的活动变少？即它能否替代其他解中的第一个活动，且不破坏可行性。 **2. 给一个足够小、... |
| cp_bridge_009 | bridge_contract_clean | 4.0 | yes | no_leakage | many_questions | 我们来观察一个具体现象。你相信“选结束最早的活动”是好的，但不确定它会不会排挤掉后面更好的组合。 下面是一个很小的例子，请只看这一件事： 活动：A(1,3), B(2,4), C(3,5)。（时间区间） 假设你第一步有两个可行的选择：选A（结束最早）或者选B（稍晚开始但结束... |
| cp_bridge_006 | bridge_contract_guard_repair | 3.0 | borderline | no_leakage | all_items | 好的，我们来聚焦一个很小的例子，看看 Trie 插入时发生了什么。 下面是一个小例子：字符串 `101` 和 `100` 插入一棵空 Trie。 请你依次观察： 1. 插入第一条 `101` 后，Trie 中创建了哪些节点？请列出每个节点对应的字符和路径： - 根节点 → ... |
| cp_bridge_003 | bridge_contract_clean | 5.0 | yes | minor_bridge_leakage | full_table | 你说“只知道像背包”，那我们先从一个极小的例子入手，观察背包类题目中“表格”每个格子到底在记录什么。 **例子**： 只有1株草药，需要时间5，价值10。总时间限制为10。 想象我们有一个表格 `dp`，行代表“考虑了前几株”（从0到1），列代表“当前花费的总时间”（从0到... |
| cp_bridge_010 | bridge_contract_guard | 5.0 | yes | no_leakage | full_table, many_questions | 为了观察01背包容量枚举顺序的影响，我们用一个极小的例子： - 背包容量4，只有1个物品，重量2价值3。 - 初始dp数组全为0。 请你看两个表格（表头：容量j，0-4），并尝试回答后面的问题。 **正序枚举（j=0,1,2,3,4）：** 初始dp： 0,0,0,0,0 ... |
| cp_bridge_010 | dbox_inspired_clean | 1.0 | no | no_leakage | multi_step_trace | 让我们先聚焦在一个小例子上：假设只有一件物品（重量2，价值3），背包总容量为3。请分别用正序（容量从0到3）和倒序（容量从3到0）更新dp数组。写下每一步后dp[3]的值，看看正序时为什么会出现6（多用了物品）？这个观察应该能回答你的问题。 |
| cp_bridge_009 | enhanced_prompt_only_clean | 4.0 | borderline | minor_bridge_leakage | many_questions | 你已经有“选结束最早的活动”这个策略了，只是对“这样不会影响后面的选择”有疑问。我们可以用一个很小的例子来观察。 考虑三个活动： | 活动 | 开始 | 结束 | |------|------|------| | A | 1 | 4 | | B | 2 | 5 | | C ... |
| cp_bridge_008 | bridge_contract_guard | 5.0 | yes | no_leakage | many_questions | 你说得对，a[mid] == x 时看起来像是找到了。但问题是：题目要求的是**第一次出现的位置**，数组中可能有多个相同的 x。比如这样一个微型例子： 数组 [1, 2, 3, 3, 3, 4, 5]，目标 x = 3。 假设二分过程中 mid 指向了索引 3（即中间那个... |
| cp_bridge_010 | bridge_contract_guard_repair | 4.0 | yes | minor_bridge_leakage | many_questions, multi_step_trace | 让我们用一个极小的例子来观察“覆盖顺序”到底是怎么影响结果的。 **1. 为什么会出现覆盖问题？** 当你只用一维数组滚动更新时，如果容量从小到大循环，本层刚更新的状态可能被当作上一层状态再次使用，导致一个物品被错误地多次选取。下面这个例子会让你亲眼看到这种覆盖是怎么发生的... |
| cp_bridge_006 | codehelp_codeaid_clean | 4.0 | yes | minor_bridge_leakage | multi_step_trace | 好问题！Trie 的优势在于建树时已经把消息的组织结构存下来了。想象一下，如果我们在纸上画一棵简单的 Trie，只包含几个短消息。现在要查一个前缀，你只需要按照前缀的每一步在树上走，看看能不能走通。走通时，计数器或其他标记会告诉你经过了多少条消息。你不需要重新翻看原始消息列... |
| cp_bridge_008 | bridge_contract_clean | 5.0 | yes | no_leakage | many_questions | 我们来观察一个关键判断问题：当二分查找遇到 `a[mid] == x` 时，为什么不能立即认为 mid 就是答案。 考虑这个小例子： 数组 `[1, 3, 3, 3, 5]`，目标值 `x = 3`。 假设当前搜索区间是 `[0, 4]`，计算出中间位置 `mid = 2`... |
| cp_bridge_001 | bridge_contract_guard | 4.0 | yes | minor_bridge_leakage | many_questions | 你想知道路径上的贡献怎么用端点标记来表示。我们先看一个最小例子，观察只在端点标记会有什么效果。 **例子**：一棵链状树 1-2-3，根为 1。考虑路径 1→3（经过点 1,2,3）。假如我们在点 1 和点 3 各放一个 **+1 标记**。然后从叶子 3 开始向上汇总：每... |
| cp_bridge_009 | bridge_contract_guard | 5.0 | yes | no_leakage | many_questions | 你说得很清楚：你已经知道“选结束时间最早的活动”这个策略，但还不放心它会不会影响后面选更多的机会。这里的桥梁问题其实就是——**为什么局部选最早结束的活动，反而不会减少后续可选活动的总数？** 我们拿一个很小的例子来观察： **例子**：四个活动（只关注开始、结束时间） 活... |
| cp_bridge_003 | codehelp_codeaid_clean | 2.0 | borderline | no_leakage | full_table | 你提到了背包，方向是对的。试着想象一个非常小的例子：只有1株药草，耗时3，价值5，总时间限制是5。如果用一个表格来记录‘在不同剩余时间下能得到的最大价值’，表格的行和列分别会表示什么？从这个表格你能看出dp数组每格的含义吗？ |

## Interpretation Boundary

- `low`: the student can usually answer with A/B, yes/no, a word, or one short sentence.
- `medium`: the student needs one or two short reasons, a local judgment, or a small calculation.
- `high`: the response asks for a full table, multi-step derivation, complete rule, full trace, code, or pseudocode.
- New review workbooks prefer the coach-filled `coach_student_response_burden`; the heuristic is only a fallback for older labels.
- Heuristic labels should be calibrated by coach review before being used as a headline metric.
