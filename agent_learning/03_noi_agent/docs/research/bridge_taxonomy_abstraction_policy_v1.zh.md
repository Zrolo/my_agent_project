# Bridge Taxonomy Abstraction Policy v1

本文档说明 Research v1 中 `bridge_subtype`、`registered_focus_id` 和 `forbidden_content` 的粒度边界。

## 核心原则

不要把 bridge subtype 做成算法清单。

算法信息应放在：

- `algorithm_topic_l1`
- `algorithm_topic_l2`
- `registered_focus_id` 的候选检索上下文
- `primary_bridge_subtype_note` / `missing_bridge_instance` 的自然语言说明

桥梁标签应放在：

- 学生缺少哪一类可迁移推理关系；
- 这个关系属于状态语义、转移来源、判定条件、依赖顺序、贡献汇总、不变量、实现边界、调试证据等哪一类；
- AI 本轮不能直接补完哪类关键关系。

## 为什么要抽象

如果 subtype 中出现 `Dijkstra 旧项判断`，就会自然产生问题：

- 为什么没有 SPFA？
- 为什么没有 Floyd？
- 为什么没有 Tarjan、Dinic、Kruskal？

这说明标签层级已经混入了算法实例。正确做法不是继续补齐所有算法，而是把该标签抽象成更通用的桥梁：

```text
predicate.obsolete_candidate_guard
```

它覆盖“多候选结构中当前弹出的候选是否仍有效”的判断。Dijkstra 优先队列旧距离只是其中一个例子。

## 当前抽象替换

| 旧标签 | 新标签 | 说明 |
| --- | --- | --- |
| `predicate.dijkstra_stale_entry_guard` | `predicate.obsolete_candidate_guard` | 多候选/队列/堆中候选是否过期或失效 |
| `state.kmp_prefix_function_semantics` | `state.failure_link_or_prefix_semantics` | 回退、前缀、共享历史信息的状态语义 |
| `ordering.reverse_capacity_loop` | `ordering.single_use_update_order` | 防止同一轮刚更新状态被重复使用 |
| `aggregation.tree_path_difference_marking` | `aggregation.path_contribution_marking` | 路径/区间贡献压缩到边界或节点再汇总 |
| `implementation.dfs_parent_guard` | `implementation.traversal_back_edge_guard` | 遍历中防回走、防重复访问、防环 |
| `correctness.shortest_path_invariant` | `correctness.settled_candidate_invariant` | 当前候选被确认后不再被推翻的不变量 |

旧标签保留在 `bridge_subtype_registry_v2.json` 中作为 `deprecated` 兼容项，以免历史标注无法校验。新的教练标注 workbook 不应优先展示旧标签。

## 禁止内容写法

`bridge_specific_forbidden_content` 不应写成具体算法规则。

推荐写成抽象泄露形状：

- `no_exact_state_definition`
- `no_exact_recurrence`
- `no_exact_check_condition`
- `no_exact_boundary_update_rule`
- `no_exact_guard_condition`
- `no_exact_modeling_plan`
- `no_full_invariant_proof`
- `no_exact_contribution_formula`
- `no_exact_iteration_template`
- `no_exact_data_structure_template`
- `no_complete_local_condition`
- `no_fully_worked_micro_trace`

例如：

```text
不要写：不能直接给 Dijkstra 旧距离判断。
推荐写：no_exact_guard_condition，并在 missing_bridge_instance 里说明这是“判断弹出的候选是否仍与当前 dist 一致”。
```

## 标注建议

教练标注时按以下顺序判断：

1. 先选 `primary_bridge_family`。
2. 再选抽象 `primary_bridge_subtype_id`。
3. 用 `algorithm_topic_l1/l2` 或 `registered_focus_id` 记录算法背景。
4. 在 `primary_bridge_subtype_note` 中写当前 case 的具体算法语境。
5. 用 `bridge_specific_forbidden_content` 记录不能直接泄露的抽象内容类型。

这样可以避免标签体系为了覆盖某个算法不断膨胀，同时保留论文需要的 CP-specific 分析能力。
