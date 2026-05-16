# Dev Ablation 50-case Blind Review Analysis

This report analyzes 50 development cases, 10 anonymous system conditions, and 500 blind-reviewed responses. It is development evidence, not a final held-out result.

- Review workbook: `coach_response_review_workbook_dev_ablation_zh7_human_coach_reviewed.xlsx` (local filled file, not committed)
- Anonymous key: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_full_fairness_50_20260514/coach_response_review_workbook_dev_ablation.key.csv`

- Reviewed responses: 500
- Cases: 50
- Leakage labels: {'no_leakage': 419, 'minor_bridge_leakage': 66, 'major_bridge_leakage': 5, 'answer_leakage': 10}
- Bridge reveal justification labels: {'no_reveal': 419, 'borderline': 66, 'unjustified': 15}
- Student response burden labels: {'medium': 354, 'low': 125, 'high': 21}
- Show-to-student labels: {'borderline': 210, 'yes': 248, 'no': 42}
- Responses with v3 case-specific rubrics: 0 / 500

## Primary Outcomes

`rubric_eval_score_v1` is a development-only triage score and must not be used as the sole paper conclusion.

| condition | n | overall | rubric_score_dev | ready | safe_ready | major+answer | sufficiency | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 3.46 | 46.51 | 27 | 27 | 4 | 1.66 | 3/45/2 |
| enhanced_prompt_only_guard | 50 | 3.54 | 46.24 | 25 | 25 | 2 | 1.62 | 4/43/3 |
| enhanced_prompt_only_guard_repair | 50 | 2.98 | 33.42 | 14 | 14 | 3 | 1.4 | 4/40/6 |
| dbox_inspired_clean | 50 | 3.76 | 54.95 | 29 | 29 | 1 | 1.78 | 24/24/2 |
| dbox_inspired_guard | 50 | 3.68 | 49.45 | 23 | 23 | 1 | 1.68 | 19/28/3 |
| dbox_inspired_guard_repair | 50 | 3.56 | 51.31 | 25 | 25 | 2 | 1.8 | 22/26/2 |
| bridge_contract_compact_clean | 50 | 3.62 | 53.36 | 31 | 31 | 1 | 1.78 | 13/37/0 |
| bridge_contract_compact_guard | 50 | 3.54 | 47.76 | 23 | 23 | 1 | 1.7 | 16/33/1 |
| bridge_contract_compact_guard_repair | 50 | 3.48 | 49.37 | 26 | 26 | 0 | 1.86 | 4/45/1 |
| bridge_guided_dbox_style_guard | 50 | 3.68 | 50.2 | 23 | 23 | 0 | 1.76 | 16/33/1 |

## Diagnostic Dimensions

These dimensions support error analysis, prompt revision, and LLM-judge calibration. Micro-example scores are counted only when applicable and filled.

| condition | n | core6 | bridge_id | groundedness | appropriateness | next_step | single_focus | micro mean (scored/applicable) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 1.5467 | 1.76 | 1.78 | 1.66 | 1.04 | 1.34 | 1.16 (50/50) |
| enhanced_prompt_only_guard | 50 | 1.56 | 1.8 | 1.78 | 1.58 | 1.06 | 1.46 | 1.26 (50/50) |
| enhanced_prompt_only_guard_repair | 50 | 1.4367 | 1.66 | 1.58 | 1.24 | 1.02 | 1.44 | 1.28 (50/50) |
| dbox_inspired_clean | 50 | 1.7067 | 1.74 | 1.66 | 1.76 | 1.48 | 1.8 | 1.1667 (48/48) |
| dbox_inspired_guard | 50 | 1.6433 | 1.64 | 1.56 | 1.66 | 1.34 | 1.86 | 1.22 (50/50) |
| dbox_inspired_guard_repair | 50 | 1.68 | 1.64 | 1.64 | 1.66 | 1.4 | 1.86 | 1.1837 (49/49) |
| bridge_contract_compact_clean | 50 | 1.6867 | 1.7 | 1.7 | 1.82 | 1.24 | 1.78 | 1.2449 (49/49) |
| bridge_contract_compact_guard | 50 | 1.6267 | 1.64 | 1.58 | 1.66 | 1.26 | 1.8 | 0.9184 (49/49) |
| bridge_contract_compact_guard_repair | 50 | 1.6467 | 1.76 | 1.7 | 1.64 | 1.06 | 1.8 | 1.1429 (49/49) |
| bridge_guided_dbox_style_guard | 50 | 1.6367 | 1.56 | 1.44 | 1.78 | 1.26 | 1.86 | 1.2 (50/50) |

## Key Paired Comparisons

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 50 | -0.08 | -0.0633 | -0.0495 | 6/33/11 | [-0.28, 0.12] |
| enhanced_prompt_only_guard - enhanced_prompt_only_clean | 50 | 0.08 | 0.0133 | 0.0257 | 10/34/6 | [-0.16, 0.3] |
| enhanced_prompt_only_guard_repair - enhanced_prompt_only_guard | 50 | -0.56 | -0.1233 | -0.1028 | 7/18/25 | [-0.84, -0.28] |
| dbox_inspired_guard_repair - dbox_inspired_guard | 50 | -0.12 | 0.0367 | 0.0286 | 8/31/11 | [-0.4, 0.16] |
| bridge_contract_compact_guard - bridge_contract_compact_clean | 50 | -0.08 | -0.06 | -0.0971 | 8/28/14 | [-0.32, 0.18] |
| bridge_contract_compact_guard_repair - bridge_contract_compact_guard | 50 | -0.06 | 0.02 | 0.0486 | 12/25/13 | [-0.28, 0.16] |
| bridge_contract_compact_guard - dbox_inspired_guard | 50 | -0.14 | -0.0167 | -0.0548 | 12/21/17 | [-0.38, 0.1] |
| bridge_contract_compact_guard_repair - dbox_inspired_guard_repair | 50 | -0.08 | -0.0333 | -0.0348 | 10/24/16 | [-0.36, 0.22] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 50 | 0.0 | -0.0067 | -0.0086 | 11/28/11 | [-0.22, 0.24] |
| dbox_inspired_guard - bridge_guided_dbox_style_guard | 50 | 0.0 | 0.0067 | 0.0086 | 11/28/11 | [-0.24, 0.22] |

## Major/Answer Leakage Case Memo Draft

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| heldout_v2_luogu_011 | enhanced_prompt_only_clean | 2.0 | no | unjustified | 抓到点了，但转移合法性的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_027 | bridge_contract_compact_guard | 2.0 | no | unjustified | 抓到点了，但差分标记位置的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_044 | enhanced_prompt_only_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_033 | dbox_inspired_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是数据结构维护量，不能直接把成品塞过去。 |
| heldout_v2_luogu_044 | bridge_contract_compact_clean | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_037 | enhanced_prompt_only_guard | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是策略背后的不变量，不能直接把成品塞过去。 |
| heldout_v2_luogu_041 | enhanced_prompt_only_clean | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_049 | enhanced_prompt_only_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是拒绝整题答案后的下一步入口，不能直接把成品塞过去。 |
| heldout_v2_luogu_009 | enhanced_prompt_only_clean | 2.0 | no | unjustified | 抓到点了，但DP 转移来源的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_020 | enhanced_prompt_only_guard | 2.0 | no | unjustified | 抓到点了，但二分对象和边界方向的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_041 | dbox_inspired_guard | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_012 | enhanced_prompt_only_clean | 2.0 | no | unjustified | 抓到点了，但check 判定条件的关键结论被说穿了。学生看完基本照做，不需要自己跨那一步。 |
| heldout_v2_luogu_043 | enhanced_prompt_only_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是实现边界和下标，不能直接把成品塞过去。 |
| heldout_v2_luogu_050 | dbox_inspired_clean | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是拒绝整题答案后的下一步入口，不能直接把成品塞过去。 |
| heldout_v2_luogu_021 | dbox_inspired_guard_repair | 1.0 | no | unjustified | 这条越线了，已经在给完整做法/代码。学生要练的是边界更新顺序，不能直接把成品塞过去。 |

## Development Notes

- The highest `student_ready_pass` condition is `bridge_contract_compact_clean`: 31 / 50.
- If the case-specific rubric count is 0, this report is a v3 metric reanalysis only; it should not be used as full evidence for case-specific grader calibration.
- This run did not include `bridge_contract_safe_scaffold` as a normal condition; safe scaffold is used only as a block/fallback mechanism and appendix candidate.
- Major/answer leakage cases should be inspected qualitatively because fully worked micro-examples can leak the critical bridge without giving code.
- The new bridge-reveal justification field separates useful instructional information from unjustified early completion of the student's current missing bridge.
- The new scaffold-sufficiency field flags over-withholding: low leakage is not pedagogical success if the response is safe but not useful.
- Student-response burden is an interaction-cost signal, not part of the core score.
- Guard/Repair causal effects still require same-candidate before/after repair stress; between-run averages are not enough.
- Use this run to decide which conditions enter the frozen 50-case held-out study, not as a headline result.
