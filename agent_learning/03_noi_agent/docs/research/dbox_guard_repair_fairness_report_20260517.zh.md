# DBox Guard+Repair Fairness Report 20260517

## 范围

本报告汇总教练回填的 20-case DBox-inspired Guard+Repair fairness add-on：

- reviewed workbook: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517_reviewed.xlsx`
- labels: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_labels_20260517.jsonl`
- comparison summary: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_comparison_summary_20260517.json`

这 20 条是 headline-sensitive targeted set，不是随机抽样，也不是完整 50-case DBox+Repair 人审。DBox+Repair add-on 是单次补评；与主实验条件的比较使用同 case 的 priority60 adjudicated + Coach A/B 主实验标签，因此存在 reviewer/protocol mismatch。结论只能作为 fairness sensitivity evidence。

## 完整性

- 标注行数：20 / 20
- `review_status=labeled`：20 / 20
- 主指标均已填写：overall、would-show、leakage label、reveal justification、sufficiency、burden、confidence、discussion
- 备注：8 / 20

## 主结果

| condition/view | n | overall | ready | safe-ready | no leakage | minor | major+answer | sufficiency | burden L/M/H | discuss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `dbox_repair_addon_review20` | 20 | 3.550 | 11 | 11 | 14 | 6 | 0 | 1.800 | 8/9/3 | 7 |
| `main_dbox_guard_priority60_plus_coachA_same20` | 20 | 3.400 | 10 | 10 | 15 | 3 | 2 | 1.450 | 7/12/1 | 9 |
| `main_bridge_repair_priority60_plus_coachA_same20` | 20 | 4.050 | 15 | 15 | 17 | 3 | 0 | 1.650 | 3/17/0 | 5 |

读法：在这 20 个敏感样本上，DBox+Repair add-on 的 overall 为 3.55，major+answer leakage 为 0，safe-ready 为 11/20。相比主实验 DBox Guard 的 priority60+Coach A 口径，它主要减少了 major+answer leakage（2 -> 0）并小幅提高 overall / sufficiency；但 Bridge Contract compact + Guard/Repair 在同一 20 cases 上仍有更高 overall 和 safe-ready。

## Paired Sensitivity

| comparison | n | mean overall delta | W/T/L | safe-ready delta | leakage severity delta | burden delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `dbox_repair_addon_minus_main_dbox_guard_A` | 20 | +0.150 | 6/9/5 | +1 | -0.050 | +0.050 |
| `bridge_repair_A_minus_dbox_repair_addon` | 20 | +0.500 | 12/5/3 | +4 | -0.150 | +0.100 |
| `bridge_repair_A_minus_main_dbox_guard_A` | 20 | +0.650 | 12/5/3 | +5 | -0.200 | +0.150 |

解释：DBox+Repair 相对 DBox Guard 的均值提升较小（+0.15，W/T/L=6/9/5），更像风险修正而不是质量大幅提升。Bridge+Repair 相对 DBox+Repair 的差距在 Coach A 主口径下仍为 +0.50（W/T/L=12/5/3）。不过由于 DBox+Repair 是补评、主表条件来自原 A/B 流程，不能把这个 paired table 写成严格同轮显著性证明。

## Coach B Sensitivity

| condition/view | n | overall | ready | safe-ready | no leakage | minor | major+answer | sufficiency | burden L/M/H | discuss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `main_dbox_guard_priority60_plus_coachB_same20` | 20 | 3.150 | 5 | 5 | 18 | 0 | 2 | 0.800 | 10/9/1 | 4 |
| `main_bridge_repair_priority60_plus_coachB_same20` | 20 | 3.250 | 5 | 5 | 19 | 1 | 0 | 0.850 | 10/10/0 | 1 |

Coach B 对 student-ready 更严格，因此 ready/safe-ready 绝对值低。DBox+Repair 补评与 Coach B 不是同一完整评分流程，不能直接做强结论；只能说明主实验中的 rater strictness 仍然影响 ready 解读。

## Risk Cases

| case_id | overall | show | leakage | burden | discuss | note |
| --- | ---: | --- | --- | --- | --- | --- |
| `dialogue_v3_012_predicate_check_semantics` | 3 | borderline | minor_bridge_leakage | medium | yes | 优点：例子能推进 true/false 方向。问题：可行/不可行和搜索侧选择已给得偏强，学生可能填空而非自构造。建议：改成先让学生自己判断两个候选是否可行。 |
| `dialogue_v3_020_boundary_update_order` | 2 | borderline | no_leakage | medium | yes | 问题：小例子的递推式和原题/边界覆盖问题贴合弱，学生可能在无关数组更新上耗力。安全但教学指向不够清楚。 |
| `dialogue_v3_030_aggregation_contribution_summary` | 3 | borderline | minor_bridge_leakage | high | yes | 优点：路径前缀例子有桥梁导向。问题：pre[u]+pre[v] 的提示接近 LCA 修正核心，且模拟负担偏高。 |
| `dialogue_v3_032_data_structure_operation_semantics` | 3 | borderline | minor_bridge_leakage | low | yes | 问题：把 a+b 与最大值对比，几乎把节点摘要方向摆到学生面前；仍需学生回答，但偏强。 |
| `dialogue_v3_005_state_representation_semantics` | 3 | borderline | minor_bridge_leakage | medium | yes | 优点：抓到状态表示。问题：先给出“节点 u 对应原图哪个点”这个维度，接近状态核心；且要求列两个维度负担略高。 |
| `dialogue_v3_022_modeling_object_relation` | 3 | borderline | no_leakage | high | no | 问题：要求列三种关系及条件，学生回复负担偏高；可改成只选一个对象对和一种关系。 |
| `dialogue_v3_031_data_structure_operation_semantics` | 3 | borderline | minor_bridge_leakage | low | yes | 问题：直接点出逆序对需要查“之前出现且比它大”的数量，接近数据结构摘要语义核心；仍需学生补 leaf sum 含义。 |
| `dialogue_v3_042_implementation_boundary` | 4 | yes | no_leakage | high | no |  |
| `dialogue_v3_001_state_representation_semantics` | 3 | borderline | minor_bridge_leakage | low | yes | 问题：直接提示用起始和结束两个参数，接近区间状态下标核心；还未完整给状态值含义，故判轻微泄露。 |

## Paper-Ready Interpretation

可以写：

```text
A targeted 20-case DBox-inspired Guard+Repair add-on reduced major/answer leakage on headline-sensitive cases and produced no major/answer leakage in the supplemental review. Its overall quality was modestly above the corresponding DBox Guard subset, but it did not overturn the Bridge Contract compact + Guard/Repair trend under the primary Coach-A-adjudicated view. Because this is a targeted, single supplemental review with reviewer/protocol mismatch, we report it as fairness sensitivity evidence rather than as a new main condition.
```

中文：

```text
在 20 条 headline-sensitive DBox+Repair 补评中，DBox+Repair 没有出现 major/answer leakage，并相对同 case 的 DBox Guard 子集小幅提高 overall 和 sufficiency；但在 Coach A 主口径下，它没有推翻 Bridge Contract compact + Guard/Repair 的 overall / safe-ready 趋势。由于这是 targeted single supplemental review，且与主实验条件存在 reviewer/protocol mismatch，应作为 fairness sensitivity evidence 报告，而不是新的主实验 condition。
```

不能写：

- DBox+Repair 已经被完整 50-case 双教练人审验证。
- Bridge+Repair 对所有 repair-enabled baseline 有确定优势。
- Repair 在 DBox 上无代价地提升质量。
- 这 20-case targeted set 可以替代主实验结果。

## 下一步

1. 若时间允许，补做 50-case 全量 DBox+Repair review，或至少让第二位教练复评这 20 条中的 discussion/risk cases。
2. 在论文 Discussion 中把本结果放在 fairness sensitivity / appendix，而不是 main headline table。
3. 与 same-candidate Repair stress result 一起写：Repair 减少泄露更有证据，但可能带来 burden 或提示过强的 trade-off。
