# DBox Guard+Repair Fairness Report 20260517

## Scope

This report summarizes the reviewed 20-case DBox-inspired Guard+Repair fairness add-on:

- reviewed workbook: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517_reviewed.xlsx`
- labels: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_labels_20260517.jsonl`
- comparison summary: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_comparison_summary_20260517.json`

The 20 rows are a headline-sensitive targeted set, not a random sample and not a full 50-case DBox+Repair review. The add-on is a single supplemental review. Comparisons to main-experiment conditions use same-case priority60-adjudicated + Coach A/B labels, so reviewer/protocol mismatch remains. Treat this as fairness sensitivity evidence.

## Completeness

- Labeled rows: 20 / 20
- `review_status=labeled`: 20 / 20
- Primary fields filled: overall, would-show, leakage label, reveal justification, sufficiency, burden, confidence, discussion
- Notes: 8 / 20

## Main Results

| condition/view | n | overall | ready | safe-ready | no leakage | minor | major+answer | sufficiency | burden L/M/H | discuss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `dbox_repair_addon_review20` | 20 | 3.550 | 11 | 11 | 14 | 6 | 0 | 1.800 | 8/9/3 | 7 |
| `main_dbox_guard_priority60_plus_coachA_same20` | 20 | 3.400 | 10 | 10 | 15 | 3 | 2 | 1.450 | 7/12/1 | 9 |
| `main_bridge_repair_priority60_plus_coachA_same20` | 20 | 4.050 | 15 | 15 | 17 | 3 | 0 | 1.650 | 3/17/0 | 5 |

Reading: on these 20 sensitive cases, DBox+Repair has overall 3.55, no major/answer leakage, and safe-ready 11/20. Compared with the same-case DBox Guard subset under the priority60+Coach A view, it mainly removes major/answer leakage and slightly improves overall/sufficiency. It does not overturn the Bridge Contract compact + Guard/Repair trend on the same 20 cases.

## Paired Sensitivity

| comparison | n | mean overall delta | W/T/L | safe-ready delta | leakage severity delta | burden delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `dbox_repair_addon_minus_main_dbox_guard_A` | 20 | +0.150 | 6/9/5 | +1 | -0.050 | +0.050 |
| `bridge_repair_A_minus_dbox_repair_addon` | 20 | +0.500 | 12/5/3 | +4 | -0.150 | +0.100 |
| `bridge_repair_A_minus_main_dbox_guard_A` | 20 | +0.650 | 12/5/3 | +5 | -0.200 | +0.150 |

Interpretation: DBox+Repair improves modestly over DBox Guard (+0.15 overall, W/T/L=6/9/5), looking more like risk correction than a large quality gain. Bridge+Repair remains ahead of DBox+Repair under the Coach-A-adjudicated main view (+0.50, W/T/L=12/5/3). Because the add-on and main labels come from different review passes, this is not a strict same-round significance result.

## Coach B Sensitivity

| condition/view | n | overall | ready | safe-ready | no leakage | minor | major+answer | sufficiency | burden L/M/H | discuss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `main_dbox_guard_priority60_plus_coachB_same20` | 20 | 3.150 | 5 | 5 | 18 | 0 | 2 | 0.800 | 10/9/1 | 4 |
| `main_bridge_repair_priority60_plus_coachB_same20` | 20 | 3.250 | 5 | 5 | 19 | 1 | 0 | 0.850 | 10/10/0 | 1 |

Coach B is stricter about student-ready, so ready/safe-ready absolute counts are much lower. This reinforces that ready claims remain rater-sensitive.

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

Can write:

```text
A targeted 20-case DBox-inspired Guard+Repair add-on reduced major/answer leakage on headline-sensitive cases and produced no major/answer leakage in the supplemental review. Its overall quality was modestly above the corresponding DBox Guard subset, but it did not overturn the Bridge Contract compact + Guard/Repair trend under the primary Coach-A-adjudicated view. Because this is a targeted, single supplemental review with reviewer/protocol mismatch, we report it as fairness sensitivity evidence rather than as a new main condition.
```

Do not write:

- DBox+Repair has been validated by a full 50-case double-coach review.
- Bridge+Repair has a confirmed advantage over every repair-enabled baseline.
- Repair improves DBox quality without trade-offs.
- This targeted 20-case set replaces the main experiment.

## Next Steps

1. If time allows, run full 50-case DBox+Repair review, or at least second-review the discussion/risk cases in this 20-case set.
2. Put this result in fairness sensitivity / appendix, not the main headline table.
3. Pair it with the same-candidate Repair stress result: Repair has evidence for leakage reduction, but burden and over-strong hints remain trade-offs.
