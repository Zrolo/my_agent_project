# Dev Ablation 20-case Blind Review Analysis

This report analyzes 20 development cases, 1 anonymous system conditions, and 20 blind-reviewed responses. It is development evidence, not a final held-out result.

- Review workbook: `dbox_guard_repair_fairness_review20_workbook_20260517_reviewed.xlsx` (local filled file, not committed)
- Anonymous key: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.key.csv`

- Reviewed responses: 20
- Cases: 20
- Leakage labels: {'minor_bridge_leakage': 6, 'no_leakage': 14}
- Bridge reveal justification labels: {'borderline': 5, 'pedagogically_justified': 4, 'no_reveal': 11}
- Student response burden labels: {'medium': 9, 'high': 3, 'low': 8}
- Show-to-student labels: {'borderline': 9, 'yes': 11}
- Responses with v3 case-specific rubrics: 20 / 20

## Primary Outcomes

`rubric_eval_score_v1` is a development-only triage score and must not be used as the sole paper conclusion.

| condition | n | overall | rubric_score_dev | ready | safe_ready | major+answer | sufficiency | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| enhanced_prompt_only_guard | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| enhanced_prompt_only_guard_repair | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| dbox_inspired_clean | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| dbox_inspired_guard | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| dbox_inspired_guard_repair | 20 | 3.55 | 52.075 | 10 | 10 | 0 | 1.8 | 8/9/3 |
| bridge_contract_compact_clean | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| bridge_contract_compact_guard | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| bridge_contract_compact_guard_repair | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |
| bridge_guided_dbox_style_guard | 0 | 0.0 | 0.0 | 0 | 0 | 0 | 0.0 | 0/0/0 |

## Diagnostic Dimensions

These dimensions support error analysis, prompt revision, and LLM-judge calibration. Micro-example scores are counted only when applicable and filled.

| condition | n | core6 | bridge_id | groundedness | appropriateness | next_step | single_focus | micro mean (scored/applicable) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| enhanced_prompt_only_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| enhanced_prompt_only_guard_repair | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| dbox_inspired_guard_repair | 20 | 1.7083 | 1.85 | 1.7 | 1.5 | 1.7 | 1.8 | 1.5 (10/10) |
| bridge_contract_compact_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| bridge_contract_compact_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| bridge_contract_compact_guard_repair | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |
| bridge_guided_dbox_style_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 (0/0) |

## Key Paired Comparisons

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| enhanced_prompt_only_guard - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| enhanced_prompt_only_guard_repair - enhanced_prompt_only_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| dbox_inspired_guard_repair - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_compact_guard - bridge_contract_compact_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_compact_guard_repair - bridge_contract_compact_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_compact_guard - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_compact_guard_repair - dbox_inspired_guard_repair | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| dbox_inspired_guard - bridge_guided_dbox_style_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |

## Major/Answer Leakage Case Memo Draft

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |

## Development Notes

- The highest `student_ready_pass` condition is `dbox_inspired_guard_repair`: 10 / 20.
- If the case-specific rubric count is 0, this report is a v3 metric reanalysis only; it should not be used as full evidence for case-specific grader calibration.
- This run did not include `bridge_contract_safe_scaffold` as a normal condition; safe scaffold is used only as a block/fallback mechanism and appendix candidate.
- Major/answer leakage cases should be inspected qualitatively because fully worked micro-examples can leak the critical bridge without giving code.
- The new bridge-reveal justification field separates useful instructional information from unjustified early completion of the student's current missing bridge.
- The new scaffold-sufficiency field flags over-withholding: low leakage is not pedagogical success if the response is safe but not useful.
- Student-response burden is an interaction-cost signal, not part of the core score.
- Guard/Repair causal effects still require same-candidate before/after repair stress; between-run averages are not enough.
- Use this run to decide which conditions enter the frozen 50-case held-out study, not as a headline result.
