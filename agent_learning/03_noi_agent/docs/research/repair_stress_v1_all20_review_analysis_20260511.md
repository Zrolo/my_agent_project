# Repair Before/After Blind Review Analysis

## Data

- Paired cases: 20
- Fully labeled pairs: 20
- Label file: `docs/research/nonexistent_repair_stress_all20_labels.jsonl`

## Summary

| Metric | Value |
|---|---:|
| repaired wins | 14 |
| ties | 3 |
| repaired losses | 3 |
| average quality delta | 1.1 |
| leakage improves | 19 |
| leakage ties | 1 |
| leakage worsens | 0 |
| average leakage severity delta | -1.85 |
| candidate major/answer leakage rate | 100.0% |
| repaired major/answer leakage rate | 5.0% |
| student-ready improves after repair | 14 |
| student-ready ties | 3 |
| student-ready worsens after repair | 3 |

## Case Notes

### repair_stress_001

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 例子本身非常合适，但 AI 已经把 dp[2] 到 dp[4] 的重复使用完整算出来了。正确但泄桥，学生只是在接受结论而不是自己发现。
- Repaired: 5 / no_leakage / 这个例子选得对，容量 5、体积 2 会让正序时 dp[4] 出现重复选同一物品的现象。让学生先写数组，再比较倒序，桥梁很清楚。

### repair_stress_002

- Quality delta: -1
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 转移式和倒序理由都对，但公式、循环方向、覆盖原因一次性给完，正是学生缺的桥。可作为复习总结，不适合作为当前提示。
- Repaired: 2 / no_leakage / 思路是用正序小例子暴露覆盖，但选“重量2、容量3”看不出重复使用，dp[3] 用的是 dp[1]，不会出问题。这个例子会把学生带偏，容量至少要到 4 才能看到 dp[4] 用刚更新的 dp[2]。

### repair_stress_003

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 2 / major_bridge_leakage / 这条不只泄露，还可能把边差分和点差分公式混在一起：说要统计每条边，却用了 cnt[w]--、cnt[parent[w]]-- 这一套更像点路径计数，边计数常见是 lca 减 2。需要先确认目标，否则不建议给学生看。
- Repaired: 4 / no_leakage / 小树 1-2-3 和路径 2-3 让学生在很低成本上试端点/LCA 标记，方向对。稍弱的地方是没有提示为什么 DFS 子树和对应边数，后续可能要再追一问。

### repair_stress_004

- Quality delta: 0
- Critical bridge leakage severity delta: 0
- Candidate: 3 / major_bridge_leakage / 例子是对题的，但端点 +1、LCA -2、DFS 含义都直接讲出来了，学生卡的“在哪里加减”没有自己推。可保留例子，删掉标记结果，让学生先模拟。
- Repaired: 3 / major_bridge_leakage / 比上一条多了让学生模拟，所以下一步更明确；但“4、7 加 +1，2 加 -2”已经把核心标记方案说穿了。微型例子有用，不过应先让学生猜端点和 LCA 的符号。

### repair_stress_005

- Quality delta: 1
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / lazy 语义说得准，但把“父节点已生效、孩子未下传”这座桥直接揭开了。作为讲解可以，作为 L2 引导偏强，最好改成问 sum[x] 和子节点 sum 的状态差异。
- Repaired: 4 / no_leakage / 抓得很准：用当前节点 sum、子节点 sum 的差异逼出 lazy 的语义，没有直接替学生定义。小缺点是没有具体区间例子，弱一点的学生可能还要再追问一次。

### repair_stress_006

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / “父节点欠两个儿子的账”这个类比贴切，但后面把 pushdown 要改的 lazy 和 sum 公式全说完了。学生不用再判断欠给谁、怎么还，提示强度偏过。
- Repaired: 5 / no_leakage / 把“欠账”类比接到具体区间 [1,4] 和两个孩子上，要求学生说出孩子要改哪两个值，正好引出 pushdown。没有直接写公式，强度很合适。

### repair_stress_007

- Quality delta: 1
- Critical bridge leakage severity delta: -1
- Candidate: 3 / major_bridge_leakage / 变形和 j->i 都正确，但这正是学生写反的关键桥，已经直接补完。可以作为答案卡，但不适合作为 L2 过程引导。
- Repaired: 4 / minor_bridge_leakage / 先让学生把不等式化成 d[v]≤d[u]+w，再自己映射边方向，教学上比直接给 j->i 好。它给了松弛标准形，提示略强，但仍保留了变量对应这一步。

### repair_stress_008

- Quality delta: 1
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 规则本身清楚，而且能解决问题；但“这题属于前一种，所以用最短路”直接替学生完成判断。若按 L2，应去掉最后一句，让学生自己判断本题是哪一种。
- Repaired: 4 / no_leakage / 方向是好的：先让学生把不等式类型和最短/最长路对应起来，而不是直接宣布用哪个。下一步稍微宽，最好再让他把本题约束改写成 <= 或 >= 的标准形。

### repair_stress_009

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / first true 的边界更新说对了，但 true 时 r=mid、false 时 l=mid+1 是学生当前要搭的桥，回复直接给完。缺少让他判断“答案在左还是右”的过程。
- Repaired: 5 / no_leakage / 很好地把规则拆成两个判断，还用 000111 的例子让学生先决定动 l 还是 r。没有把最终收缩式直接替他写死，适合作为 L2。

### repair_stress_010

- Quality delta: 0
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / check 的含义和边界方向都讲对了，但这就是学生卡住的 true/false 语义桥。可以作为最后总结，不宜在这一轮直接给。
- Repaired: 3 / no_leakage / 守住了不直接给 check 的边界，但问题有点抽象，学生可能只是把“可行”两个字重复一遍。最好接一个具体 mid，让他判断 true 后目标值该放大还是缩小。

### repair_stress_011

- Quality delta: -1
- Critical bridge leakage severity delta: -1
- Candidate: 3 / major_bridge_leakage / 堆操作流程是对的，但“小的重量尽量少被重复累加”只是结论，不是学生能验证的桥。最好补一个对比例子或交换论证问题，而不是直接报哈夫曼核心。
- Repaired: 2 / minor_bridge_leakage / 1,2,3,4 这个例子不太好：顺序合并和每次取最小会走出同样代价，学生算完也看不出为什么顺序合并不行。建议换成能产生明显差异的反例，再引导比较总成本。

### repair_stress_012

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 复杂度结论是对的，但把学生该自己算出的 n²≈4e10 直接说完了。后面前缀和/树状数组/单调结构三选一偏散，缺少针对原循环里哪一步可维护的引导。
- Repaired: 5 / no_leakage / 很对准 TLE 的桥：先让学生把 n² 算出来，再引到“内层能不能维护/预处理”。没有直接报 4e10，也没有乱塞数据结构，下一步比较清楚。

### repair_stress_013

- Quality delta: -1
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / next 的定义和跳转理由都准确，但把 prefix/suffix 语义和失配跳转桥一次性讲完了。KMP 这种抽象点最好配一个短模式串让学生自己对齐，不然容易只背定义。
- Repaired: 2 / no_leakage / 问题方向对，但太空了：只问“next 可能记录什么”基本等于把学生原问题重问一遍。至少要给一个已匹配前缀/后缀的小例子，否则学生很难迈出下一步。

### repair_stress_014

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 证明是标准且正确的，但整段交换论证直接给完了。学生的问题是“为什么对”，这条会让他记住结论，却少了自己判断替换安全性的过程。
- Repaired: 5 / no_leakage / 很好的交换论证引导：先假设最优解第一个不是最早结束，再让学生判断替换后后续活动是否还能选。关键桥保留给学生完成。

### repair_stress_015

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 这段把“值不小且位置更靠右→更晚过期→永远支配”完整讲完了，正确但直接说穿了队尾弹出的证明桥。学生读完基本不用自己推。
- Repaired: 5 / no_leakage / 小例子能让学生看到“右侧且更大的元素会压掉队尾”，最后追问未来还能不能成为最大值，正好把支配关系引出来。后续最好让学生自己补上“更晚过期”这句话。

### repair_stress_016

- Quality delta: 1
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 结论是对的，但 dp[0]=0、其他位置 INF、只从非 INF 转移这些关键点都直接替学生填好了。学生卡的是 base case 和不可达语义，这条更像总结答案。
- Repaired: 4 / no_leakage / 抓住了 base case 的语义问题，让学生先说 dp[0] 和其他状态各代表什么。略可惜的是没有给一个“还没到达的位置”小提示，基础弱的学生可能会停在抽象层。

### repair_stress_017

- Quality delta: 3
- Critical bridge leakage severity delta: -3
- Candidate: 2 / answer_leakage / 这就是学生要的完整 if 和赋值，能直接抄进代码。虽然含义解释对，但完全跳过了 relax 条件的推理，教学上不该直接给。
- Repaired: 5 / no_leakage / 面对学生要你补 if，这条守住了边界：只问比较哪两个距离、更新谁。下一步很具体，学生还得自己写出条件。

### repair_stress_018

- Quality delta: 0
- Critical bridge leakage severity delta: -2
- Candidate: 3 / answer_leakage / 反例本身很清楚，也贴着“每次选价值最大”的错误贪心；但容量、物品和最优解全给了，学生没有练到怎么构造反例。更像直接交答案，不像教他找最小反例。
- Repaired: 3 / minor_bridge_leakage / 方向比直接给反例好，能引导学生比较“一个大物品”和“多个小物品”。但填空设计不完整：说了还需要别的物品，却只给 A/B 两个栏位，学生可能不知道要补 C；建议明确留出第三个物品格子。

### repair_stress_019

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 公式解释正确，但直接把 pre[R] 和 pre[L-1] 的抵消关系说完了。学生卡在下标时，更适合先用 [3,5] 这类小区间让他自己看剩下哪些项。
- Repaired: 5 / no_leakage / 这个提问很稳：pre[5]、pre[2] 到 [3,5] 的递进能让学生自己看出“减掉左边界前一段”。下一步具体，不容易继续下标混乱。

### repair_stress_020

- Quality delta: 2
- Critical bridge leakage severity delta: -2
- Candidate: 3 / major_bridge_leakage / 方向和复杂度都正确，但直接确认 Dijkstra+堆并给出松弛流程，基本替学生完成了算法选择。若按教练式 L1，应保留“非负边权为什么支持 Dijkstra”这一问。
- Repaired: 5 / no_leakage / 很适合这轮：没有直接盖章 Dijkstra，而是追问非负边权为什么关键。学生下一步就是说明算法条件，强度刚好。

## Interpretation

- Quality delta subtracts candidate quality from repaired quality; new review workbooks use `1-5` scores, while old label files remain compatible with `good=2, okay=1, bad=0`.
- Leakage severity delta maps `no=0, minor=1, major=2, answer=3` and subtracts candidate from repaired; negative means reduced leakage.
- This is a single-coach blind-review analysis, not an absolute gold label.
