# Dev Ablation 50-case Blind Review Analysis

This report analyzes 50 development cases, 7 anonymous system conditions, and 350 blind-reviewed responses. It is development evidence, not a final held-out result.

- Review workbook: `coach_response_review_workbook_dialogue_state_v3_main_by_case_20260516_coach_A_round1.zh.xlsx` (local filled file, not committed)
- Anonymous key: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/coach_response_review_workbook_dev_ablation.key.csv`

- Reviewed responses: 350
- Cases: 50
- Leakage labels: {'major_bridge_leakage': 29, 'no_leakage': 237, 'answer_leakage': 6, 'minor_bridge_leakage': 78}
- Bridge reveal justification labels: {'unjustified': 15, 'no_reveal': 237, 'borderline': 98}
- Student response burden labels: {'medium': 264, 'high': 41, 'low': 45}
- Show-to-student labels: {'no': 32, 'yes': 208, 'borderline': 110}
- Responses with v3 case-specific rubrics: 350 / 350

## Primary Outcomes

`rubric_eval_score_v1` is a development-only triage score and must not be used as the sole paper conclusion.

| condition | n | overall | rubric_score_dev | ready | safe_ready | major+answer | sufficiency | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 3.16 | 27.6 | 14 | 14 | 18 | 1.28 | 5/19/26 |
| codehelp_codeaid_clean | 50 | 3.64 | 47.7 | 25 | 25 | 3 | 1.58 | 6/40/4 |
| dbox_inspired_clean | 50 | 3.68 | 50.45 | 29 | 29 | 4 | 1.58 | 7/38/5 |
| dbox_inspired_guard | 50 | 3.7 | 51.3 | 27 | 27 | 2 | 1.62 | 11/37/2 |
| bridge_guided_dbox_style_guard | 50 | 3.68 | 48.05 | 23 | 23 | 3 | 1.58 | 3/44/3 |
| bridge_contract_compact_guard | 50 | 3.9 | 53.9 | 30 | 30 | 4 | 1.66 | 8/41/1 |
| bridge_contract_compact_guard_repair | 50 | 3.96 | 57.91 | 34 | 34 | 1 | 1.7 | 5/45/0 |

## Diagnostic Dimensions

These dimensions support error analysis, prompt revision, and LLM-judge calibration. Micro-example scores are counted only when applicable and filled.

| condition | n | core6 | bridge_id | groundedness | appropriateness | next_step | single_focus | micro mean (scored/applicable) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 1.39 | 1.84 | 1.5 | 1.28 | 1.26 | 1.52 | 0.75 (48/48) |
| codehelp_codeaid_clean | 50 | 1.5433 | 1.48 | 1.2 | 1.58 | 1.46 | 1.84 | 1.449 (49/49) |
| dbox_inspired_clean | 50 | 1.6367 | 1.66 | 1.32 | 1.58 | 1.68 | 1.92 | 1.4792 (48/48) |
| dbox_inspired_guard | 50 | 1.6133 | 1.56 | 1.16 | 1.62 | 1.7 | 1.92 | 1.4468 (47/47) |
| bridge_guided_dbox_style_guard | 50 | 1.5833 | 1.54 | 1.2 | 1.58 | 1.7 | 1.9 | 1.4694 (49/49) |
| bridge_contract_compact_guard | 50 | 1.6433 | 1.62 | 1.26 | 1.66 | 1.76 | 1.94 | 1.3913 (46/46) |
| bridge_contract_compact_guard_repair | 50 | 1.68 | 1.64 | 1.3 | 1.7 | 1.7 | 1.92 | 1.58 (50/50) |

## Key Paired Comparisons

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 50 | 0.02 | -0.0233 | -0.0262 | 15/19/16 | [-0.26, 0.32] |
| bridge_contract_compact_guard_repair - bridge_contract_compact_guard | 50 | 0.06 | 0.0367 | 0.0538 | 15/25/10 | [-0.2, 0.3] |
| bridge_contract_compact_guard - dbox_inspired_guard | 50 | 0.2 | 0.03 | 0.0248 | 19/18/13 | [-0.04, 0.44] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 50 | -0.02 | -0.03 | -0.019 | 16/18/16 | [-0.3, 0.26] |
| dbox_inspired_guard - bridge_guided_dbox_style_guard | 50 | 0.02 | 0.03 | 0.019 | 16/18/16 | [-0.26, 0.3] |

## Major/Answer Leakage Case Memo Draft

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

## Development Notes

- The highest `student_ready_pass` condition is `bridge_contract_compact_guard_repair`: 34 / 50.
- If the case-specific rubric count is 0, this report is a v3 metric reanalysis only; it should not be used as full evidence for case-specific grader calibration.
- This run did not include `bridge_contract_safe_scaffold` as a normal condition; safe scaffold is used only as a block/fallback mechanism and appendix candidate.
- Major/answer leakage cases should be inspected qualitatively because fully worked micro-examples can leak the critical bridge without giving code.
- The new bridge-reveal justification field separates useful instructional information from unjustified early completion of the student's current missing bridge.
- The new scaffold-sufficiency field flags over-withholding: low leakage is not pedagogical success if the response is safe but not useful.
- Student-response burden is an interaction-cost signal, not part of the core score.
- Guard/Repair causal effects still require same-candidate before/after repair stress; between-run averages are not enough.
- Use this run to decide which conditions enter the frozen 50-case held-out study, not as a headline result.
