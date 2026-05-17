# Dev Ablation 50-case 盲评分析

本报告分析 50 个 dev cases、7 个匿名系统条件、350 条 盲审回复。它用于开发阶段决策和 prompt/regression 修订，不作为最终 held-out test 结论。

- 盲审表：`coach_response_review_workbook_dialogue_state_v3_main_by_case_20260516_coach_A_round1.zh.xlsx`（本地填写文件，未提交仓库）
- 匿名 key：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/coach_response_review_workbook_dev_ablation.key.csv`

- 已标注回复：350 条
- case 数：50 个
- 总体泄露标签：{'major_bridge_leakage': 29, 'no_leakage': 237, 'answer_leakage': 6, 'minor_bridge_leakage': 78}
- 关键桥透露正当性：{'unjustified': 15, 'no_reveal': 237, 'borderline': 98}
- 学生回复负担：{'medium': 264, 'high': 41, 'low': 45}
- 是否愿意给学生看：{'no': 32, 'yes': 208, 'borderline': 110}
- 含 v3 case-specific rubric 的回复：350 / 350

## 主指标

主表只保留少数结果指标；`rubric_eval_score_v1` 仅用于开发阶段筛选，不作为论文唯一结论。

| condition | n | overall | rubric_score_dev | ready | safe_ready | major+answer | sufficiency | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 3.16 | 27.6 | 14 | 14 | 18 | 1.28 | 5/19/26 |
| codehelp_codeaid_clean | 50 | 3.64 | 47.7 | 25 | 25 | 3 | 1.58 | 6/40/4 |
| dbox_inspired_clean | 50 | 3.68 | 50.45 | 29 | 29 | 4 | 1.58 | 7/38/5 |
| dbox_inspired_guard | 50 | 3.7 | 51.3 | 27 | 27 | 2 | 1.62 | 11/37/2 |
| bridge_guided_dbox_style_guard | 50 | 3.68 | 48.05 | 23 | 23 | 3 | 1.58 | 3/44/3 |
| bridge_contract_compact_guard | 50 | 3.9 | 53.9 | 30 | 30 | 4 | 1.66 | 8/41/1 |
| bridge_contract_compact_guard_repair | 50 | 3.96 | 57.91 | 34 | 34 | 1 | 1.7 | 5/45/0 |

## 诊断指标

这些细项用于 error analysis、prompt 修订和 LLM Judge 校准；其中 micro-example 只在适用且已评分时计入。

| condition | n | core6 | bridge_id | groundedness | appropriateness | next_step | single_focus | micro mean (scored/applicable) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 1.39 | 1.84 | 1.5 | 1.28 | 1.26 | 1.52 | 0.75 (48/48) |
| codehelp_codeaid_clean | 50 | 1.5433 | 1.48 | 1.2 | 1.58 | 1.46 | 1.84 | 1.449 (49/49) |
| dbox_inspired_clean | 50 | 1.6367 | 1.66 | 1.32 | 1.58 | 1.68 | 1.92 | 1.4792 (48/48) |
| dbox_inspired_guard | 50 | 1.6133 | 1.56 | 1.16 | 1.62 | 1.7 | 1.92 | 1.4468 (47/47) |
| bridge_guided_dbox_style_guard | 50 | 1.5833 | 1.54 | 1.2 | 1.58 | 1.7 | 1.9 | 1.4694 (49/49) |
| bridge_contract_compact_guard | 50 | 1.6433 | 1.62 | 1.26 | 1.66 | 1.76 | 1.94 | 1.3913 (46/46) |
| bridge_contract_compact_guard_repair | 50 | 1.68 | 1.64 | 1.3 | 1.7 | 1.7 | 1.92 | 1.58 (50/50) |

## 关键配对比较

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 50 | 0.02 | -0.0233 | -0.0262 | 15/19/16 | [-0.26, 0.32] |
| bridge_contract_compact_guard_repair - bridge_contract_compact_guard | 50 | 0.06 | 0.0367 | 0.0538 | 15/25/10 | [-0.2, 0.3] |
| bridge_contract_compact_guard - dbox_inspired_guard | 50 | 0.2 | 0.03 | 0.0248 | 19/18/13 | [-0.04, 0.44] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 50 | -0.02 | -0.03 | -0.019 | 16/18/16 | [-0.3, 0.26] |
| dbox_inspired_guard - bridge_guided_dbox_style_guard | 50 | 0.02 | 0.03 | 0.019 | 16/18/16 | [-0.26, 0.3] |

## Major/Answer Leakage Case Memo 草稿

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| dialogue_v3_012_predicate_check_semantics | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_018_boundary_update_order | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_031_data_structure_operation_semantics | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_038_correctness_invariant | bridge_guided_dbox_style_guard | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_009_transition_recurrence_source | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_013_predicate_check_semantics | codehelp_codeaid_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_009_transition_recurrence_source | bridge_contract_compact_guard | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_038_correctness_invariant | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_040_correctness_invariant | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_044_implementation_boundary | dbox_inspired_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_037_correctness_invariant | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_046_debugging_evidence | codehelp_codeaid_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_001_state_representation_semantics | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_034_data_structure_operation_semantics | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_025_modeling_object_relation | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_016_predicate_check_semantics | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_015_predicate_check_semantics | bridge_contract_compact_guard | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_034_data_structure_operation_semantics | codehelp_codeaid_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_050_policy_request | dbox_inspired_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_048_policy_request | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_004_state_representation_semantics | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_015_predicate_check_semantics | dbox_inspired_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_002_state_representation_semantics | bridge_guided_dbox_style_guard | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_014_predicate_check_semantics | dbox_inspired_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_020_boundary_update_order | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_012_predicate_check_semantics | bridge_contract_compact_guard | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_049_policy_request | bridge_guided_dbox_style_guard | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_018_boundary_update_order | bridge_contract_compact_guard_repair | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_030_aggregation_contribution_summary | bridge_contract_compact_guard | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_021_boundary_update_order | dbox_inspired_guard | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_030_aggregation_contribution_summary | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_042_implementation_boundary | enhanced_prompt_only_clean | 2.0 | no | unjustified | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_032_data_structure_operation_semantics | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_013_predicate_check_semantics | dbox_inspired_guard | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |
| dialogue_v3_014_predicate_check_semantics | enhanced_prompt_only_clean | 3.0 | borderline | borderline | 提示过强，接近或直接补完本轮禁止的关键桥；需改成问题式微任务。 |

## 初步观察

- `student_ready_pass` 最高的是 `bridge_contract_compact_guard_repair`：34 / 50。
- 若 `含 v3 case-specific rubric` 数量为 0，本报告只是 v3 指标重分析；case-specific grader 校准不能把这批旧表当作完整证据。
- 本轮没有包含 `bridge_contract_safe_scaffold` 常规条件；safe scaffold 只作为 block/fallback 机制和 appendix 候选。
- `major_or_answer_leakage_count` 仍然需要按 case 回看，尤其要检查它是否来自过完整 micro-example、直接补完关键桥，还是 reviewer 对局部代码/状态关系的判定。
- 新增 `bridge_reveal_justification` 用于区分“有信息量的合理教学透露”和“过早/过完整的无正当性关键桥泄露”，避免把所有关键知识讲解都惩罚为泄露。
- 新增 `scaffold_sufficiency` 用于识别“低泄露但帮助不足”的过度保留回复；正式比较时应把 leakage 和 sufficiency 放在一起看。
- `学生回复负担` 只作为交互成本指标，不进入 core score；它用于识别学生需要输入过多而导致在线体验变差的回复。
- 出现 major/answer 级泄露的条件：{'enhanced_prompt_only_clean': 18, 'codehelp_codeaid_clean': 3, 'dbox_inspired_clean': 4, 'dbox_inspired_guard': 2, 'bridge_guided_dbox_style_guard': 3, 'bridge_contract_compact_guard': 4, 'bridge_contract_compact_guard_repair': 1}。
- Guard/Repair 的因果效果不能仅凭不同 run 的均值解释；正式判断仍需要 same-candidate before/after repair stress。
- 本轮的作用是筛选 50-case 主实验条件：强 prompt、DBox-inspired、DBox+Guard、Bridge Contract、Safe Scaffold 是否值得保留，要看它们在 paired W/T/L 和 student-ready pass 上是否稳定。

## 解释边界

这批 50-case 是 dev/regression set。可以据此修 prompt、修 rubric、决定主实验条件；但不能据此声称某个系统显著优于强 baseline。正式论文 headline 仍需要冻结 prompt/grader 后的 50-case held-out、部分双教练标注和 judge calibration。
