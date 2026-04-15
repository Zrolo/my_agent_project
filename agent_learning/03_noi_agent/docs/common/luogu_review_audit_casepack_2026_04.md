# 洛谷复盘审查样本包（2026-04-09）

这份文件给后续 AI/老师做两件事：

1. 直接打开已经生成的真实历史复盘，检查学生链路质量。
2. 按知识点继续补测，每个知识点至少取 3 道洛谷题，统一看哪里最该修。

批量生成后的机器可读清单见：

- [luogu_review_generated_batch_2026_04_09.json](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/luogu_review_generated_batch_2026_04_09.json)

---

## 一、当前已经生成好的真实历史样例

这些样例已经进入当前运行中的站点，可以直接在历史页查看。

### 新生成测试样例

| checkin_id | 题目 | 预期桥 | 当前判断 |
| --- | --- | --- | --- |
| 3356 | P2015 二叉苹果树 | `dp.state_design` | 好，已经像“小课” |
| 3357 | P2249 查找 | `implementation / binary_search.left_bound` | 很好，具体、贴题 |
| 3358 | P3372 线段树 1 | `core_design / lazy_semantics` | 可用，但还可以更具体 |

### 新生成测试样例的实际表单填写内容

#### 3356 - P2015 二叉苹果树

```json
{
  "problem_url": "https://www.luogu.com.cn/problem/P2015",
  "problem_title": "P2015 二叉苹果树",
  "oj_source": "luogu",
  "completion_status": "unfinished",
  "submission_result": "not_submitted",
  "bottleneck_text": "我知道题解说这是树形 DP，但我不明白为什么状态只记“当前子树保留几条边”就够了，总觉得还要记左右子树分别留多少。",
  "error_types": ["状态设计", "转移设计"],
  "reflection": "我总想把左右子树都分开记，结果状态越写越大。",
  "problem_tags": ["动态规划 DP", "树形 DP"]
}
```

#### 3357 - P2249 查找

```json
{
  "problem_url": "https://www.luogu.com.cn/problem/P2249",
  "problem_title": "P2249 【深基13.例1】查找",
  "oj_source": "luogu",
  "completion_status": "unfinished",
  "submission_result": "wa",
  "bottleneck_text": "我会写二分，但这里要找第一个等于 x 的位置时，我总把边界更新写乱，不知道 mid 命中后到底该往哪边缩。",
  "error_types": ["边界处理", "二分"],
  "reflection": "我怀疑是 while 里的 l、r 更新方向错了。",
  "problem_tags": ["二分"]
}
```

#### 3358 - P3372 线段树 1

```json
{
  "problem_url": "https://www.luogu.com.cn/problem/P3372",
  "problem_title": "P3372 【模板】线段树 1",
  "oj_source": "luogu",
  "completion_status": "unfinished",
  "submission_result": "not_submitted",
  "bottleneck_text": "我知道要加 lazy 标记，但我不明白这个标记到底表示什么。为什么区间加的时候不立刻把下面所有点都改掉，也还能保证查询是对的？",
  "error_types": ["模型转化", "数据结构"],
  "reflection": "我把 lazy 当成“还没改完的代码流程”，不是“还没下传的信息”。",
  "problem_tags": ["线段树"]
}
```

### 历史对照样例

| checkin_id | 题目 | 主要桥 | 当前判断 |
| --- | --- | --- | --- |
| 3126 | P1434 滑雪 | `dp.state_design` | 很好，梯度清楚 |
| 3127 | P1216 数字三角形 | `dp.transition_design` | 很好，来源关系讲清楚 |
| 1344 | P2922 Secret Message G | `modeling.scale_estimation` | 旧风格问题明显，仍需重点修 |

### 当前站点可直接查看的链接

- [P2015 二叉苹果树 - 3356](http://127.0.0.1:8000/app/history/3356)
- [P2249 查找 - 3357](http://127.0.0.1:8000/app/history/3357)
- [P3372 线段树 1 - 3358](http://127.0.0.1:8000/app/history/3358)
- [P1434 滑雪 - 3126](http://127.0.0.1:8000/app/history/3126)
- [P1216 数字三角形 - 3127](http://127.0.0.1:8000/app/history/3127)
- [P2922 Secret Message G - 1344](http://127.0.0.1:8000/app/history/1344)

---

## 二、当前产品判断：最该先修哪些知识点

### 第一优先级

#### `modeling.scale_estimation`

代表题：
- `P2922 Secret Message G`
- 这类题现在仍然容易：
  - 直接给大数结论
  - 把“估规模”讲成答案总结
  - `try_now` 偏算数，不够像“判断策略”

#### `modeling.method_selection`

代表题：
- `P2922 Secret Message G`
- 这类题现在还容易和 `scale_estimation` 混在一起。
- 需要继续收成：
  - 先看题面结构信号
  - 再解释为什么这个方法匹配
  - 少一点“先报方法名”

### 第二优先级

#### `core_design / lazy_semantics`

代表题：
- `P3372 线段树 1`
- 当前已经比以前清楚，但还可以更像老师板书：
  - 更完整的区间加例子
  - 更明确的“sum/lazy 各记录什么”

### 当前相对稳定

- `dp.state_design`
- `dp.transition_design`
- `binary_search.check_condition`
- `greedy.greedy_basis`
- `graph.tree_diameter.tree_diameter_candidates`

这些桥已经更接近：
- 定桥
- 拆桥
- 最小确认
- 知识兜底卡

---

## 三、知识点覆盖池：每个知识点 3 道洛谷题

说明：
- 这些题都已在本地 `problems` 表中存在。
- 下面同时给出：
  - 预期知识点
  - 建议卡点描述
  - 建议表单填写模板
  - 预期命中 focus / knowledge card
- 可以供别的 AI 直接拿去创建 checkin 测试数据。

### 1. `dp.state_design`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P1434 滑雪 | 典型“状态语义”桥 | 我总分不清 `dp[x][y]` 是“从这里出发能滑多远”还是“滑到这里为止有多长”。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["状态设计","记忆化搜索"]` | `focus=state_design` -> `dp.state_design` |
| P2015 二叉苹果树 | 树形 DP 状态容易写大 | 我总觉得状态里要分别记左右子树留几条边，不知道为什么只记“当前子树总共留几条边”就够了。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["状态设计","转移设计"]` | `focus=state_design` -> `dp.state_design` |
| P1115 最大子段和 | 线性 DP 容易把“当前结尾”写错成“全局答案” | 我分不清 `f[i]` 是“前 i 个数的答案”，还是“必须以第 i 个数结尾的最好值”。 | `completion_status=unfinished; submission_result=wa; error_types=["状态设计","线性DP"]` | `focus=state_design` -> `dp.state_design` |

### 2. `dp.transition_design`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P1216 数字三角形 | 最经典的“来源没想全” | 我知道是 DP，但我老漏掉当前格子能从上一行哪两个位置转移过来。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["转移设计","动态规划 DP"]` | `focus=transition_design` -> `dp.transition_design` |
| P1880 石子合并 | 区间 DP 典型转移枚举 | 我知道要按区间长度枚举，但区间 `[l,r]` 为什么要枚举最后一次合并点 `k`，这个来源我总想不全。 | `completion_status=unfinished; submission_result=wa; error_types=["转移设计","区间DP"]` | `focus=transition_design` -> `dp.transition_design` |
| P2782 友好城市 | LIS/排序后转移易漏条件 | 我知道先排序，但后面 DP 转移时，为什么只有一类前态能转过来，我总写不全。 | `completion_status=unfinished; submission_result=wa; error_types=["转移设计","排序"]` | `focus=transition_design` -> `dp.transition_design` |

### 3. `binary_search.check_condition`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P2678 跳石头 | 最典型 `check(mid)` 桥 | 我知道要二分答案，但 `check(mid)` 到底是在验证“至少能不能做到 mid”还是别的，我总说不清。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["二分","判定条件"]` | `focus=check_condition` -> `binary_search.check_condition` |
| P2249 查找 | 左端点/边界更新桥 | 我会写二分，但当 `a[mid] == x` 时，我总不知道应该把右边界收成 `mid` 还是 `mid-1`。 | `completion_status=unfinished; submission_result=wa; error_types=["边界处理","二分"]` | `focus=check_condition` 或实现边界桥 |
| P1168 中位数 | 有序结构+二分直觉容易混 | 我总觉得可以靠二分位置直接判断，但不清楚到底在“检查什么条件”。 | `completion_status=unfinished; submission_result=wa; error_types=["二分","模型转化"]` | `focus=check_condition` -> `binary_search.check_condition` |

### 4. `greedy.greedy_basis`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P1803 线段覆盖 | 活动选择经典贪心依据 | 我知道答案是先选结束早的区间，但我讲不清为什么这样不会把后面的选择堵死。 | `completion_status=unfinished; submission_result=wa; error_types=["贪心","方法依据"]` | `focus=greedy_basis` -> `greedy.greedy_basis` |
| P1090 合并果子 | Huffman 型贪心依据 | 我知道每次取最小两堆，但说不清为什么先合并大的会更吃亏。 | `completion_status=unfinished; submission_result=wa; error_types=["贪心","堆"]` | `focus=greedy_basis` -> `greedy.greedy_basis` |
| P5536 核心城市 | 题感式贪心容易说不清 | 我知道题解是贪心，但我讲不清当前这一步为什么优先处理这个点不会破坏后面。 | `completion_status=unfinished; submission_result=wa; error_types=["贪心","树的直径"]` | `focus=greedy_basis` -> `greedy.greedy_basis` |

### 5. `graph.tree_diameter.tree_diameter_candidates`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P2195 HXY造公园 | 当前系统已有代表题 | 我知道要比较新直径，但不明白“经过新边”的候选为什么要接两边最远点。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["树的直径","候选比较"]` | `focus=tree_diameter_candidates` -> `graph.tree_diameter.tree_diameter_candidates` |
| P5536 核心城市 | 同样涉及树的直径结构 | 我知道要先找直径，但不明白为什么关键点一定跟直径路径有关。 | `completion_status=unfinished; submission_result=wa; error_types=["树的直径","候选结构"]` | `focus=tree_diameter_candidates` -> `graph.tree_diameter.tree_diameter_candidates` |
| P1195 口袋的天空 | 可转成图结构候选思路审查 | 我会想到连通块，但总说不清“最后最关键的候选结构”为什么是这些。 | `completion_status=unfinished; submission_result=wa; error_types=["图论","候选结构"]` | `focus=tree_diameter_candidates` 或图结构候选桥 |

### 6. `string.trie.shared_prefix_merging`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P2922 Secret Message G | 当前主代表题 | 我不明白为什么把很多消息先放进 trie 后，查询时就不用再把所有消息重看一遍。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["字典树 Trie","方法理解"]` | `focus=method_selection` + `card=string.trie.shared_prefix_merging` |
| 题库中任一 `字典树 Trie` 标签题 A | 本地题库里优先再找字典树题 | 我知道 trie 能做前缀统计，但“公共前缀合在一起”这件事我没真正看懂。 | `completion_status=unfinished; submission_result=wa; error_types=["字典树 Trie","前缀匹配"]` | `card=string.trie.shared_prefix_merging` |
| 题库中任一 `字典树 Trie` 标签题 B | 用来验证卡片泛化性 | 我总把 trie 想成“把所有串存起来”，没看懂它真正省的是重复前缀。 | `completion_status=unfinished; submission_result=wa; error_types=["字典树 Trie","模型转化"]` | `card=string.trie.shared_prefix_merging` |

注：目前本地已确认的强代表题是 `P2922`。后续别的 AI 可继续在 `problem_tags` 中按 `字典树 Trie` 扩 2 道。

### 7. `graph.tree_path_difference`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P3128 Max Flow P | 点经过次数版树上差分代表题 | 我只想到树剖 LCA，但不知道为什么要把每条路径贡献变成端点和 LCA 附近的差分标记，最后再 DFS 汇总。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["树上差分","LCA","树剖"]` | `focus=tree_path_difference` -> `graph.tree_path_difference` |
| P3258 松鼠的新家 | 路线访问次数的自然语言代表题 | 我知道松鼠每段路都要贡献一次，但不知道为什么可以在起点、终点、公共祖先附近打标记，最后向上汇总。 | `completion_status=unfinished; submission_result=wa; error_types=["树上差分","LCA"]` | `focus=tree_path_difference` -> `graph.tree_path_difference` |
| 树上边经过次数统计题 | 用来审查点差分和边差分边界 | 我总想沿路把每条边加一，但题解说要用 LCA 和树上差分，在端点打标记后 DFS 汇总。 | `completion_status=unfinished; submission_result=wa; error_types=["树上差分","边经过次数"]` | `focus=tree_path_difference`，后续可拆边差分 variant |

注：当前 `graph.tree_path_difference` 已覆盖点经过次数和路线访问次数；边差分仍是边界样例，后续需要决定是否拆成单独 variant。

### 8. `modeling.scale_estimation`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P2922 Secret Message G | 当前最典型规模判断桥 | 我没先算 `M×N` 的量级，就觉得逐条比对应该能过。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["复杂度分析","数据规模"]` | `focus=complexity_fit` -> `modeling.scale_estimation` |
| P1196 银河英雄传说 | 大量操作时易误判暴力 | 我总想每次操作都把整列重新算一遍，但没先估总复杂度。 | `completion_status=unfinished; submission_result=wa; error_types=["复杂度分析","并查集"]` | `focus=complexity_fit` -> `modeling.scale_estimation` |
| P3958 奶酪 | 搜索/并查集前易误判复杂度 | 我第一反应是暴力判断球和球之间是否可达，但没先估边数规模。 | `completion_status=unfinished; submission_result=wa; error_types=["复杂度分析","图论"]` | `focus=complexity_fit` -> `modeling.scale_estimation` |

### 9. `modeling.method_selection`

| 题目 | 为什么适合 | 建议卡点描述 | 建议表单填写模板 | 预期命中 |
| --- | --- | --- | --- |
| P2922 Secret Message G | 方法选择桥主代表题 | 我总是先猜“可能要 trie”，但说不清题面里到底有什么结构信号支持它。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["方法选择","字典树 Trie"]` | `focus=method_selection` -> `modeling.method_selection` 或 `string.trie.shared_prefix_merging` |
| P3372 线段树 1 | 区间修改/区间查询典型方法判断 | 我知道题解用线段树，但我讲不清为什么树状数组/暴力不够。 | `completion_status=unfinished; submission_result=not_submitted; error_types=["方法选择","线段树"]` | `focus=method_selection` -> `modeling.method_selection` |
| P1196 银河英雄传说 | 并查集建模选择 | 我知道题解是并查集，但我说不清为什么这里不是普通数组模拟，而要维护集合关系。 | `completion_status=unfinished; submission_result=wa; error_types=["方法选择","并查集"]` | `focus=method_selection` -> `modeling.method_selection` |

---

## 四、建议给其他 AI 的检验方式

如果让别的 AI 继续审查，建议它按这个顺序：

1. 先打开“当前已生成好的真实历史样例”。
2. 对每条样例都看：
   - 第一轮复盘是否像小课
   - `visual_hint` 是否像提示而不是答案卡
   - `try_now` 是否真的在考当前桥
3. 再按上面的“知识点覆盖池”补新 checkin。
4. 对每个知识点至少看 3 道题，最后输出：
   - 哪个知识点最稳
   - 哪个知识点最抽象
   - 哪个知识点最值得先修

---

## 五、当前我的产品判断

### 已经比较稳

- `dp.state_design`
- `dp.transition_design`
- `binary_search.check_condition`
- `greedy.greedy_basis`

### 还要继续修

- `modeling.scale_estimation`
- `modeling.method_selection`
- `string.trie.shared_prefix_merging`
- `core_design / lazy_semantics`

最主要的原因是：
- 方法桥比结构桥更容易漂
- 仍然容易从“引导学生判断”滑向“直接给策略结论”
- `P2922` 一类题还会在 `scale_estimation` 和 `trie 机制桥` 之间摇摆
