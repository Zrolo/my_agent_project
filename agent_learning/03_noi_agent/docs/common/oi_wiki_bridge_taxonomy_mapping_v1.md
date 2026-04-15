# OI Wiki To Bridge Taxonomy Mapping v1

## 目的

这份文档不是要把 OI Wiki 全量搬进 prompt。

它只做一件事：

- 把 OI Wiki 的主目录
- 映射成我们系统后续可用的：
  - `topic_l1`
  - `topic_l2`
  - `bridge`

这样后面不管是：

- 补知识卡
- 接轻量检索
- 做 teacher 统计
- 扩高频桥

都能围绕同一套语言走，不会再一会儿按题型、一会儿按算法名、一会儿按卡点乱跳。

参考来源：

- [OI Wiki GitHub 仓库](https://github.com/OI-wiki/OI-wiki)
- 其 `mkdocs.yml` 当前主导航与 `docs/` 主目录

## 设计边界

这份映射只做三层：

- `topic_l1`
- `topic_l2`
- `bridge`

其中：

- `topic_l1` 对应大的知识域
- `topic_l2` 对应 OI Wiki 里相对稳定的小专题
- `bridge` 对应我们系统真正拿来教学、出 quiz、出 knowledge card 的最小教学桥

这不是百科目录。
这是一份**面向学生复盘系统**的桥级知识索引。

## 当前已在系统中真实落地的 bridge

这些 bridge 已经在 `review_engine.py` 里有真实 focus / quiz / knowledge card / remedy 链路：

| bridge | 当前状态 |
| --- | --- |
| `state_design` | 已落地 |
| `transition_design` | 已落地 |
| `enumeration_order` | 已落地 |
| `check_condition` | 已落地 |
| `left_bound_update` | 已落地 |
| `greedy_basis` | 已落地 |
| `tree_path_difference` | 已落地 |
| `tree_diameter_candidates` | 已落地 |
| `shared_prefix_merging` | 已落地 |
| `lazy_semantics` | 已落地 |
| `complexity_fit` | 已落地 |
| `method_selection` | 已落地 |
| `constraint_modeling` | 已落地 |
| `general_modeling` | 已落地 |

## 主映射

### 1. 动态规划

对应 OI Wiki 主目录：

- `docs/dp/`

建议映射：

| OI Wiki 子域 | topic_l1 | topic_l2 | bridge 候选 |
| --- | --- | --- | --- |
| `dp/basic.md` | `dp` | `dp_basic` | `state_design`, `transition_design`, `answer_extraction` |
| `dp/memo.md` | `dp` | `memoized_search` | `state_design`, `memoization_meaning`, `subproblem_definition` |
| `dp/tree.md` | `dp` | `tree_dp` | `state_design`, `transition_design`, `merge_rule` |
| `dp/knapsack.md` | `dp` | `knapsack` | `state_design`, `transition_design`, `enumeration_order` |
| `dp/interval.md` | `dp` | `interval_dp` | `state_design`, `transition_design`, `boundary_initialization` |
| `dp/state.md` | `dp` | `state_compression_dp` | `state_design`, `state_compression_meaning`, `transition_design` |
| `dp/number.md` | `dp` | `digit_dp` | `state_design`, `boundary_initialization`, `memoization_meaning` |
| `dp/opt/state.md` | `dp` | `dp_optimization` | `state_design`, `transition_design` |

### 2. 数据结构

对应 OI Wiki 主目录：

- `docs/ds/`

建议映射：

| OI Wiki 子域 | topic_l1 | topic_l2 | bridge 候选 |
| --- | --- | --- | --- |
| `ds/seg.md` | `data_structure` | `segment_tree` | `range_info_meaning`, `query_update_split`, `lazy_semantics` |
| `ds/fenwick.md` | `data_structure` | `fenwick` | `range_info_meaning`, `structure_choice` |
| `ds/monotonous-stack.md` | `data_structure` | `monotonic_stack` | `maintenance_invariant`, `structure_choice` |
| `ds/monotonous-queue.md` | `data_structure` | `monotonic_queue` | `maintenance_invariant`, `future_damage_check` |
| `ds/stack.md` | `data_structure` | `stack` | `structure_choice` |
| `ds/queue.md` | `data_structure` | `queue` | `structure_choice` |
| `ds/hash.md` | `data_structure` | `hash_table` | `structure_choice`, `hash_collision_awareness` |
| `ds/dsu.md` | `data_structure` | `disjoint_set` | `union_find_meaning`, `connected_component_linking` |

### 3. 字符串

对应 OI Wiki 主目录：

- `docs/string/`

建议映射：

| OI Wiki 子域 | topic_l1 | topic_l2 | bridge 候选 |
| --- | --- | --- | --- |
| `string/trie.md` | `string` | `trie` | `method_selection`, `shared_prefix_merging`, `prefix_query`, `node_count_meaning` |
| `string/kmp.md` | `string` | `kmp` | `failure_link_meaning`, `pattern_matching_window` |
| `string/hash.md` | `string` | `string_hash` | `method_selection`, `hash_collision_awareness` |
| `string/ac-automaton.md` | `string` | `ac_automaton` | `shared_prefix_merging`, `failure_link_meaning`, `node_count_meaning` |
| `string/basic.md` | `string` | `string_basic` | `string_modeling` |

### 4. 图论

对应 OI Wiki 主目录：

- `docs/graph/`

建议映射：

| OI Wiki 子域 | topic_l1 | topic_l2 | bridge 候选 |
| --- | --- | --- | --- |
| `graph/tree-diameter.md` | `graph` | `tree_diameter` | `tree_diameter_candidates`, `path_candidate_reasoning` |
| `graph/diff-constraints.md` | `graph` | `difference_constraints` | `constraint_modeling`, `graph_modeling` |
| `graph/tree-basic.md` | `graph` | `tree_basics` | `graph_modeling`, `reachability_reasoning` |
| `graph/lca.md` | `graph` | `lca` | `method_selection`, `tree_path_difference`, `state_design` |
| `graph/lca.md` + 树上路径统计题 | `graph` | `tree_path_difference` | `tree_path_difference` |
| 树链剖分 / HLD 相关专题 | `graph` | `heavy_light_decomposition` | `tree_path_difference`, `method_selection` |
| `graph/shortest-path.md` | `graph` | `shortest_path` | `graph_modeling`, `structure_choice`, `constraint_modeling` |
| `graph/dag.md` | `graph` | `dag` | `graph_modeling`, `transition_design` |

### 5. 算法基础

对应 OI Wiki 主目录：

- `docs/basic/`

建议映射：

| OI Wiki 子域 | topic_l1 | topic_l2 | bridge 候选 |
| --- | --- | --- | --- |
| `basic/complexity.md` | `basic` | `complexity` | `complexity_fit` |
| `basic/binary.md` | `basic` | `binary_search` | `check_condition`, `left_bound_update`, `method_selection` |
| `basic/greedy.md` | `basic` | `greedy` | `greedy_basis`, `future_damage_check`, `local_choice_reason` |
| `basic/enumerate.md` | `basic` | `enumeration` | `enumeration_order`, `complexity_fit` |
| `basic/prefix-sum.md` | `basic` | `prefix_sum_difference` | `range_info_meaning`, `general_modeling` |
| `basic/divide-and-conquer.md` | `basic` | `divide_and_conquer` | `recursion_structure` |

### 6. 搜索

对应 OI Wiki 主目录：

- `docs/search/`

建议映射：

| OI Wiki 子域 | topic_l1 | topic_l2 | bridge 候选 |
| --- | --- | --- | --- |
| `search/dfs.md` | `search` | `dfs` | `recursion_structure`, `reachability_reasoning` |
| `search/bfs.md` | `search` | `bfs` | `bfs_layer_meaning`, `reachability_reasoning` |
| `search/backtracking.md` | `search` | `backtracking` | `recursion_structure`, `future_damage_check` |
| `search/heuristic.md` | `search` | `heuristic_search` | `method_selection`, `future_damage_check` |

### 7. 数学

对应 OI Wiki 主目录：

- `docs/math/`

建议映射：

| OI Wiki 子域 | topic_l1 | topic_l2 | bridge 候选 |
| --- | --- | --- | --- |
| `math/bit.md` | `math` | `bit_operation` | `state_compression_meaning`, `general_modeling` |
| `math/binary-exponentiation.md` | `math` | `fast_power` | `method_selection` |
| `math/number-theory/basic.md` | `math` | `number_theory` | `method_selection`, `general_modeling` |
| `math/combinatorics/combination.md` | `math` | `combinatorics` | `general_modeling`, `state_design` |

### 8. 题型 / 杂项

对应 OI Wiki 主目录：

- `docs/topic/`
- `docs/misc/`
- `docs/contest/`

建议映射：

| OI Wiki 子域 | topic_l1 | topic_l2 | bridge 候选 |
| --- | --- | --- | --- |
| `topic/interaction.md` 或交互题相关 | `topic` | `interactive_problem` | `reading_target`, `general_modeling` |
| `misc/discrete.md` | `misc` | `discretization` | `method_selection`, `general_modeling` |
| `contest/common-mistakes.md` | `contest` | `common_mistakes` | `boundary_debug`, `loop_boundary`, `data_type` |

## 当前第一批最值得接通的 OI Wiki -> bridge

不是全部接。
先接最值得的。

| 优先级 | OI Wiki 子域 | 我们的 bridge |
| --- | --- | --- |
| 高 | `basic/complexity.md` | `complexity_fit` |
| 高 | `string/trie.md` | `method_selection`, `shared_prefix_merging` |
| 高 | `ds/seg.md` | `lazy_semantics` |
| 高 | `basic/binary.md` | `check_condition`, `left_bound_update` |
| 高 | `dp/basic.md` | `state_design`, `transition_design` |
| 高 | `graph/tree-diameter.md` | `tree_diameter_candidates` |
| 高 | `graph/lca.md` + 树上路径统计题 | `tree_path_difference` |
| 高 | `graph/diff-constraints.md` | `constraint_modeling` |
| 中 | `basic/greedy.md` | `greedy_basis` |
| 中 | `search/dfs.md` | `recursion_structure` |
| 中 | `basic/prefix-sum.md` | `range_info_meaning` |

## 建议的数据形状

后面如果真正落到代码里，推荐先用这样的最小映射结构：

```json
{
  "oi_wiki_path": "string/trie.md",
  "topic_l1": "string",
  "topic_l2": "trie",
  "bridges": [
    "method_selection",
    "shared_prefix_merging",
    "prefix_query",
    "node_count_meaning"
  ],
  "priority": "high"
}
```

## 当前产品上怎么用

第一阶段不要做大 RAG。

先做这 3 件事：

1. 让每个 `bridge` 都能挂一个 `topic_l1 / topic_l2`
2. 让 teacher 统计能按 `topic_l1 / topic_l2 / bridge` 看分布
3. 让后续知识卡扩充时，知道应该去 OI Wiki 的哪一小块补内容

## 一句话结论

下一阶段不是：

- 每题一份知识库

而是：

- **OI Wiki 章节 -> topic_l1/topic_l2 -> bridge**

这样高频桥继续精修，长尾桥才有可扩展的知识来源。
