# Repair Same-Candidate Stress Result 20260517

## 范围

本报告汇总教练已填完的 `repair_same_candidate_stress_blind_review_workbook_20260517_filled.xlsx`。评审设计固定同一条 candidate 的 before/after repair 输出，并随机盲化为 Response A / Response B。汇总时使用单独 key 还原 before/after。

本结果是 **same-candidate stress evidence**。它可以支持 Repair 在固定 candidate 上的因果效果估计，但不能反过来替代主实验 condition-level 结果，也不能说明 Repair 已完全解决泄露。

## 总体结果

| metric | value |
| --- | ---: |
| labeled pairs | 30 / 30 |
| before overall mean | 3.367 |
| after overall mean | 3.633 |
| mean overall delta | +0.267 |
| quality win / tie / loss | 12 / 11 / 7 |
| repair preferred / original preferred / tie | 15 / 11 / 4 |
| leakage improved / same / worse | 16 / 14 / 0 |
| burden improved / same / worse | 2 / 16 / 12 |
| still-leaks rate | 0.000 |
| too-vague-after-repair rate | 0.067 |

## Leakage Distribution

| label | before | after |
| --- | ---: | ---: |
| no_leakage | 10 | 22 |
| minor_bridge_leakage | 13 | 8 |
| major_bridge_leakage | 7 | 0 |
| answer_leakage | 0 | 0 |

读法：Repair 将 7 条 major leakage 降到 0，且没有新增更严重的泄露。16/30 pair 的 leakage severity 改善，14/30 持平，0/30 变差。这是当前最强的 same-candidate evidence。

## Quality And Burden Trade-Off

| dimension | before | after |
| --- | ---: | ---: |
| would_show yes | 12 | 18 |
| would_show borderline | 11 | 11 |
| would_show no | 7 | 1 |
| burden low | 18 | 8 |
| burden medium | 11 | 19 |
| burden high | 1 | 3 |

Repair 后 overall 均值上升 +0.267，pair-level quality win/tie/loss 为 12/11/7；但 student burden 有明显 trade-off：12/30 变重，只有 2/30 变轻。说明 Repair 往往通过更保守、更开放或更要求学生补判断的方式降低泄露，因此论文必须同时报告 burden delta。

## Source Condition Split

| source condition | n | mean overall delta | quality W/T/L | leakage improved/same/worse | burden improved/same/worse | repair preferred/original/tie |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `bridge_contract_compact_guard_repair` | 13 | -0.077 | 3/6/4 | 5/8/0 | 1/9/3 | 4/6/3 |
| `dbox_inspired_guard_repair` | 17 | +0.529 | 9/5/3 | 11/6/0 | 1/7/9 | 11/5/1 |

解释：Repair 在 DBox-inspired repair candidates 上收益更明显，因为这些 before candidates 更常带有直接桥梁泄露或过完整提示。Bridge Contract repair candidates 的 before 版本本来更接近安全边界，因此 Repair 的质量效果更混合。

## Bridge Family Coverage

| bridge bucket | leakage improved | leakage same | quality win | quality tie | quality loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| `state_representation_semantics` | 3 | 1 | 3 | 1 | 0 |
| `transition_recurrence_source` | 1 | 2 | 1 | 1 | 1 |
| `predicate_check_semantics` | 3 | 1 | 1 | 2 | 1 |
| `boundary_update_order` | 0 | 2 | 0 | 1 | 1 |
| `modeling_object_relation` | 2 | 1 | 1 | 1 | 1 |
| `aggregation_contribution_summary` | 3 | 2 | 2 | 2 | 1 |
| `data_structure_operation_semantics` | 3 | 2 | 3 | 1 | 1 |
| `correctness_invariant` | 0 | 2 | 1 | 1 | 0 |
| `implementation_boundary` | 1 | 0 | 0 | 1 | 0 |
| `policy_request` | 0 | 1 | 0 | 0 | 1 |

这是 natural repair set 的覆盖，不是 taxonomy-stratified full coverage。不要把它写成所有 bridge families 上均已充分验证。

## Paper-Ready Interpretation

可以写：

```text
In a 30-pair same-candidate stress test, Repair reduced or preserved leakage severity in all pairs, improved leakage in 16/30 pairs, and reduced major leakage from 7/30 to 0/30. Overall quality increased modestly on average (+0.27), but student burden worsened in 12/30 pairs, indicating a quality-safety-burden trade-off.
```

中文：

```text
在 30-pair same-candidate stress test 中，Repair 没有使任何样本的泄露更严重，并使 16/30 个 pair 的 leakage severity 改善；major leakage 从 7/30 降为 0/30。整体质量均值小幅上升（+0.27），但 12/30 个 pair 的学生回复负担变重，说明 Repair 的收益伴随 burden trade-off。
```

不能写：

- Repair 已完全解决所有泄露。
- Repair 在主实验中已被因果证明。
- Repair 总是提升质量。
- Repair 没有学生负担代价。

## 对主论文的影响

本结果补上了主实验缺失的 same-candidate evidence：主实验只说明 `bridge_contract_compact_guard_repair` condition 表现好；本 stress test 则显示，在固定 candidate 的 before/after 比较中，Repair 对 leakage reduction 有明确方向性证据。但论文仍应把它写成 stress-test evidence，而不是把主实验均值重新解释为 Repair 的唯一因果证明。
