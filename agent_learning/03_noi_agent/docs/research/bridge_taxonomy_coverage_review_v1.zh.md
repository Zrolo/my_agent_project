# Bridge Taxonomy Coverage Review v1

本文档用于回答一个标注设计问题：

> 当前 bridge subtype / forbidden content 是否应该继续按具体算法扩展，还是抽象成能覆盖大部分算法竞赛场景的桥梁形状？

结论：**不应按具体算法穷举。应保留少量抽象桥梁形状，用 `algorithm_topic`、`registered_focus_id` 和备注记录具体算法语境。**

## 外部资料对照

CP-Algorithms 的目录覆盖 Algebra、Data Structures、Dynamic Programming、String Processing、Combinatorics、Numerical Methods、Geometry、Graphs 等大类，并在图论下继续细分遍历、连通性、最短路、最小生成树、环、LCA、网络流、匹配等主题。OI Wiki 也按算法基础、搜索、动态规划、字符串、数学、数据结构、图论、计算几何、杂项、专题组织知识。USACO Guide 的 Gold 目录同样按 Math、Dynamic Programming、Graphs、Data Structures、Trees、Additional Topics 分层，并特别提醒 topic 列表不是穷尽的，比赛题可能包含未列出或跨分区的主题。

这些资料说明：算法竞赛知识体系天然是开放的。如果 bridge subtype 直接写成 `Dijkstra 旧项判断`、`Floyd 中转点枚举`、`SPFA 入队条件` 这类算法名，标签体系会无限膨胀，也会让教练误以为没列出的算法就没有对应标签。

资料来源：

- CP-Algorithms main page: https://cp-algorithms.com/
- OI Wiki main page: https://oiwiki.com/
- USACO Guide Gold topics: https://usaco.guide/gold

## 建议的三层结构

| 层级 | 用途 | 例子 |
| --- | --- | --- |
| `algorithm_topic` | 记录算法领域或知识点 | `graph.shortest_path.dijkstra`, `dp.interval`, `string.kmp`, `geometry.convex_hull` |
| `bridge_subtype` | 记录学生缺少的可迁移推理形状 | `predicate.obsolete_candidate_guard`, `ordering.dependency_satisfaction_order` |
| `forbidden_content` | 记录本轮不能直接补完的泄露形状 | `no_exact_guard_condition`, `no_full_invariant_proof` |

教练标注时先看学生缺的是哪种推理桥，再把具体算法写进 topic / focus / note，而不是新增算法专属 subtype。

## 推荐覆盖的大类桥梁形状

下面的表不是要求一次性全部进入下拉框，而是作为后续扩展的覆盖地图。已经在当前 schema 中覆盖的用“已有”标记；建议观察后再加的用“候选”标记。

| 抽象桥梁形状 | 状态 | 学生常见话法 | 覆盖的算法例子 | 教练解释 |
| --- | --- | --- | --- | --- |
| 目标/限制拆解 | 已有 | “题目到底要我求什么？” | 所有题型 | 把输入、输出、最大/最小/计数/可行性目标拆清楚。 |
| 对象关系建模 | 已有 | “什么当点？什么当边？” | 图建模、区间建模、状态建模 | 把题面对象、关系、操作变成可计算结构。 |
| 方法选择信号 | 已有 | “这题是不是二分/DP/图？” | DP、二分、贪心、图、数据结构 | 让学生用题面特征验证算法方向，而不是直接盖章。 |
| 状态/表示语义 | 已有 | “dp[j] / dist / mask 到底表示什么？” | DP、BFS 状压、最短路、字符串自动机 | 定义数组格子、节点字段、mask、辅助数组里的信息含义。 |
| 前缀/回退/失败链接语义 | 已有 | “next 数组里的数是什么？” | KMP、AC 自动机、后缀自动机、Trie 回退 | 理解失配、回退、共享前缀或历史压缩信息。 |
| 转移/递推来源 | 已有 | “这一格从哪里转移来？” | DP、树形 DP、组合递推、图 DP | 找出当前状态由哪些前态、决策或子问题组成。 |
| 判定条件语义 | 已有 | “check 到底判断什么？” | 二分答案、if 条件、relax、合法性判断 | 明确 true/false、更新/不更新、合法/非法的含义。 |
| 过期/失效候选守卫 | 已有 | “队列里旧的要不要跳过？” | Dijkstra 堆、A*、多次入队 BFS、懒删除堆 | 判断当前取出的候选是否仍然有效。 |
| 依赖顺序/更新顺序 | 已有 | “为什么要倒序/拓扑序/先长度？” | 背包压维、区间 DP、DAG DP、Floyd 中转点 | 保证用到的依赖已经准备好，或避免本轮污染旧状态。 |
| 单次使用更新顺序 | 已有 | “正着更新为什么会重复用？” | 0/1 背包、滚动数组、原地 DP | 防止本轮刚写出的状态被再次读取。 |
| 贡献汇总/差分标记 | 已有 | “为什么只在端点加减？” | 前缀和、差分、树上差分、BIT 区间技巧 | 把多次影响压缩记录，再通过前缀/DFS/查询还原。 |
| 数据结构操作映射 | 已有 | “题目动作对应 push 还是 pop？” | 堆、并查集、线段树、Fenwick、单调栈 | 把题面动作映射到查询、更新、合并、弹出等操作。 |
| 维护字段/聚合语义 | 候选 | “线段树节点要维护什么？” | Segment tree、Fenwick、Sparse Table、Treap | 明确节点/块/表格中保存什么摘要，以及如何由子结构维护。 |
| 单调/支配淘汰 | 已有 | “为什么弹掉以后不会再有用？” | 单调栈、单调队列、凸包优化、贪心淘汰 | 理解被淘汰候选被另一个候选支配。 |
| 已确定候选不变量 | 已有 | “为什么弹出后就确定？” | Dijkstra、BFS 层序、拓扑处理、Prim/Kruskal 部分选择 | 解释为什么当前确认的结果不会被后来推翻。 |
| 交换/替换论证 | 已有 | “为什么这个贪心不会亏？” | 活动选择、排序贪心、MST cut/cycle argument | 用交换、替换或 cut/cycle 说明局部选择安全。 |
| 数学性质/同余不变量 | 候选 | “为什么取模/奇偶/整除能判断？” | 数论、模运算、奇偶性、gcd、CRT | 把运算限制转成保持不变的数学关系。 |
| 计数分解/容斥 | 候选 | “为什么要加这个减那个？” | 组合计数、容斥、Catalan、生成函数初步 | 把全集拆成互斥/重叠类别，并防止漏算或重算。 |
| 几何谓词/方向关系 | 候选 | “叉积正负表示什么？” | 凸包、线段相交、点在多边形、扫描线几何 | 把几何位置关系转成方向、面积、排序或交点判定。 |
| 搜索状态去重/剪枝 | 候选 | “visited 该怎么设？为什么能剪？” | DFS/BFS、回溯、IDA*、meet-in-the-middle | 判断哪些搜索分支等价、重复、必不优或不可行。 |
| 复杂度瓶颈定位 | 已有 | “两层循环会不会过？” | 暴力优化、预处理、数据结构替代内层循环 | 找到真正慢的层或操作，再选择优化方向。 |
| 实现边界/初始化 | 已有 | “i 到 n 还是 n-1？初值怎么设？” | 所有代码实现 | 下标、开闭区间、base case、哨兵、类型、输入输出。 |
| 调试证据/最小反例 | 已有 | “WA 但不知道哪里错。” | 所有调试场景 | 先收集最小失败样例、实际输出、可疑位置，而不是猜修法。 |
| 迁移总结/题型信号 | 已有 | “下次怎么识别这种题？” | 复盘与迁移 | 总结触发条件、典型结构和下次可复用的判断问题。 |

## 建议暂不扩大的部分

目前不建议为以下算法单独新增 subtype：

- SPFA；
- Floyd；
- Tarjan；
- Dinic；
- Kruskal；
- KMP；
- 线段树懒标记；
- 数位 DP；
- 树上差分；
- 具体背包变体。

这些应通过 `algorithm_topic` 或 `registered_focus_id` 区分，bridge subtype 只记录抽象桥梁。例如：

| 具体算法问题 | 推荐 subtype | 推荐 forbidden_content |
| --- | --- | --- |
| SPFA 是否重复入队 | `predicate.obsolete_candidate_guard` 或 `predicate.feasibility_truth_direction` | `no_exact_guard_condition` |
| Floyd 为什么枚举 k | `ordering.subproblem_size_dependency_order` 或 `ordering.topological_dependency` 近似 | `no_exact_iteration_template` |
| KMP next 数组含义 | `state.failure_link_or_prefix_semantics` | `no_exact_state_definition` |
| Dinic 分层图为什么这样推进 | `representation_state_bridge` + `predicate_condition_bridge` 组合 | `no_exact_modeling_plan` / `no_exact_check_condition` |
| Kruskal 为什么按边权选 | `correctness.settled_candidate_invariant` 或 `correctness.local_choice_exchange_argument` | `no_full_invariant_proof` |

## 对当前 schema 的建议

当前 Research v1 已经覆盖了大多数常见辅导场景。短期不建议大幅增加下拉项，否则标注负担会反弹。

建议只观察下面 5 个候选是否在 50-case 标注中频繁出现：

1. `math.property_invariant_bridge`：数论/同余/奇偶/gcd 等数学性质桥。
2. `counting.partition_inclusion_bridge`：计数拆分、容斥、避免重算漏算。
3. `geometry.predicate_relation_bridge`：叉积、方向、相交、凸性等几何谓词。
4. `search.pruning_dedup_bridge`：搜索去重、剪枝、visited 状态设计。
5. `ds.maintained_summary_semantics`：数据结构节点/块/表格维护字段语义。

如果某个候选在 50-case 或真实日志中出现多次，再加入 v3 schema；否则先用 `primary_bridge_subtype_note` 记录即可。

## 给教练的简短判定口诀

```text
先问：学生缺的是哪种推理关系？
再问：这关系能不能迁移到别的算法？
能迁移，就选抽象 subtype。
具体算法名，只写在 topic / focus / note。
禁止内容，只写不能泄露哪种关键关系，不写某算法专属规则。
```
