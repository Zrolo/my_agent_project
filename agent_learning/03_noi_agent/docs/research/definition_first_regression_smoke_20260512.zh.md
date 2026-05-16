# Definition-first / Worked-example Regression Smoke（2026-05-12）

本报告是开发阶段 targeted smoke，不是最终 held-out 结果。它只检查上一轮 prompt/rubric 修复后，`cp_bridge_001/002/003/005/010` 这 5 个高风险 case 是否仍出现：

- 开头定义句泄露；
- 完整推演微型例子泄露；
- 经典模板搬运；
- 把问题问成答案槽位。

## 运行条件

输入：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/definition_first_regression_cases.jsonl
```

运行了两个条件：

```text
bridge_contract + guard + repair
dbox_inspired + guard
```

输出：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/bridge_contract_guard_repair.jsonl
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/dbox_inspired_guard.jsonl
```

## 自动运行结果

| condition | cases | stage errors | notes |
| --- | ---: | ---: | --- |
| `bridge_contract_guard_repair` | 5 | 2 | `cp_bridge_001` leakage judge timeout；`cp_bridge_005` bridge judge schema enum invalid。 |
| `dbox_inspired_guard` | 5 | 0 | 全部跑通。 |

## 自盲评摘录

| case | condition | automated guard | self-review | reason |
| --- | --- | --- | --- | --- |
| `cp_bridge_001` | `bridge_contract_guard_repair` | leakage timeout | high risk / likely major | 回复让学生找“减号标记位置”并总结它和端点、公共祖先关系，仍然接近端点/LCA 标记规则。 |
| `cp_bridge_002` | `bridge_contract_guard_repair` | pass | acceptable to minor | 用极小例子让学生判断 true/false，未直接给答案，但问题仍很贴近 check 语义桥。 |
| `cp_bridge_003` | `bridge_contract_guard_repair` | pass | acceptable | 让学生从背包维度迁移到时间限制，没有直接给完整状态定义。 |
| `cp_bridge_005` | `bridge_contract_guard_repair` | bridge judge error | unknown | 无最终回复，不能评价生成质量。 |
| `cp_bridge_010` | `bridge_contract_guard_repair` | level 2 / pass | minor risk | 没有完整算表，但把正序/倒序对比和错误 `dp[2]` 观察点给得较强。 |
| `cp_bridge_001` | `dbox_inspired_guard` | pass | likely major | 直接问“哪些节点 +1，哪些节点 -1”，这是当前关键桥的答案槽位。 |
| `cp_bridge_002` | `dbox_inspired_guard` | pass | minor to major | 直接问 `true` 后尝试更大还是更小，接近边界动作桥。 |
| `cp_bridge_003` | `dbox_inspired_guard` | pass | acceptable to minor | 问维度和下标对应属性，偏提示但未完整定义状态。 |
| `cp_bridge_005` | `dbox_inspired_guard` | level 3 / rewrite | major | 明确讲出“推迟更新子节点”和下传触发条件，属于 lazy 语义泄露。 |
| `cp_bridge_010` | `dbox_inspired_guard` | pass | minor | 问依赖的值是否已被当前物品更新，接近 overwrite-order 关键桥，但没有直接算完。 |

## 结论

1. 这次 patch 修掉了一部分“模板化开头”的风险，但没有让 prompt-only 控制稳定可靠。
2. `dbox_inspired + guard` 并没有天然更安全。它仍然会把 step-tree 当前子步骤写成答案槽位，例如直接问标记位置、边界动作或 lazy 语义。
3. `bridge_contract + guard + repair` 在 `cp_bridge_003` 上相对更好，但 `cp_bridge_001` 和 `cp_bridge_010` 仍需更强 guard / route 策略。
4. `bridge_contract_safe_scaffold` 虽然安全但质量很低，不适合作为常规回复，只适合作为高风险兜底。

## 对下一步的影响

不建议继续无限追加 prompt 规则。下一步应做三件事：

1. 将 `cp_bridge_001/002/005/010` 加入 prompt freeze 前 regression set；
2. 在 Leakage Judge 中加强“答案槽位问题”检测：如果问题直接要求学生填写 forbidden completion 的关键位置、方向、true/false 后续动作，也应判为泄露或过强提示；
3. 进入 50-case 前明确 route policy：高风险 contribution / predicate / representation 语义桥，不能只靠 generator prompt，必须有 Guard/Repair 或 deterministic fallback。

## 后续 targeted rerun（同日）

在补充 `concept_comprehension_gap -> modeling_representation_gap` 的 Bridge Judge 状态别名后，重新跑了 `cp_bridge_001` 和 `cp_bridge_005` 的 `bridge_contract + guard + repair`：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/bridge_contract_guard_repair_after_alias_and_answer_slot.jsonl
```

结果：

| case | stage errors | automated guard | self-review |
| --- | --- | --- | --- |
| `cp_bridge_001` | none | level 3 / rewrite | Repair 仍让学生填写关键标记位置/动作，属于答案槽位风险。 |
| `cp_bridge_005` | none | level 3 / rewrite | Repair 删除了一部分定义，但仍复制已填 `sum/lazy` 表格，保留关键字段值。 |

随后补充了 Repair prompt 的答案槽位与已填关键表格约束，并单独重跑 `cp_bridge_005`：

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/cp_bridge_005_after_internal_field_guard_patch.jsonl
```

该次 run 没有 stage error，但 Guard 仍把候选判为 pass。候选回复直接给出了根节点 `sum=20`、`lazy=5`、子节点 `sum=0` 等内部字段更新效果。这说明当前 Leakage Judge 对“数据结构内部字段更新动作”仍有 false negative 风险。

因此，这个 case 应升级为 Guard calibration regression，而不是继续只靠生成 prompt 微调。
