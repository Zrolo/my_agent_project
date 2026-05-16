# 50-case AI Preliminary High-risk Coach Review Pack

This note documents the high-risk review pack derived from `heldout_50_ai_reference_dev_20260513_merged`. The source run contains 50 held-out draft cases × 8 system conditions, for 400 generated tutor responses. This pack is for development-stage quality control and coach review prioritization only. It is not coach gold and should not be used as a headline paper result.

## Purpose

Reviewing all 400 responses is costly. To first inspect the failures most likely to affect claims about safety and instructional quality, we created two smaller review packs from the AI preliminary review:

1. `high_risk_rows`: 25 responses flagged as high risk by the AI preliminary review. This is the fastest pack for validating major / answer leakage.
2. `high_risk_case_pack`: all 8 system responses for the 11 cases that contain at least one high-risk response, for 88 rows total. This supports paired within-case comparison across conditions.

## Inputs And Outputs

- Source run: `evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged`
- Full AI preliminary workbook: `coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx`
- High-risk rows CSV: `coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_rows.csv`
- High-risk rows review workbook: `coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_rows.zh.xlsx`
- High-risk rows key: `coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_rows.key.csv`
- High-risk case pack CSV: `coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_case_pack.csv`
- High-risk case pack review workbook: `coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_case_pack.zh.xlsx`
- High-risk case pack key: `coach_response_review_workbook_dev_ablation.ai_prelim.high_risk_case_pack.key.csv`

The `*.key.csv` files are for researchers only and should not be sent to blind reviewers. Coaches should receive only the `.zh.xlsx` files.

## Selection Criteria

A response is included in `high_risk_rows` if it satisfies any of the following:

- AI preliminary leakage label is `major_bridge_leakage` or `answer_leakage`;
- AI preliminary `would_show_to_student=no`;
- AI preliminary `needs_discussion=yes`;
- AI preliminary overall quality is 1 or 2.

We then expanded the cases containing those high-risk rows into `high_risk_case_pack`, which includes all 8 system responses for each selected case.

## Size

| Pack | Rows | Cases | Use |
| --- | ---: | ---: | --- |
| `high_risk_rows` | 25 | 11 | Fast validation of AI-flagged high-risk rows |
| `high_risk_case_pack` | 88 | 11 | Within-case comparison across the 8 system conditions |

AI preliminary leakage distribution among high-risk rows:

| Label | Count |
| --- | ---: |
| `answer_leakage` | 16 |
| `major_bridge_leakage` | 9 |

Case distribution among high-risk rows:

| case_id | High-risk rows |
| --- | ---: |
| `heldout_cp_044` | 7 |
| `heldout_cp_017` | 5 |
| `heldout_cp_039` | 3 |
| `heldout_cp_014` | 2 |
| `heldout_cp_019` | 2 |
| `heldout_cp_003` | 1 |
| `heldout_cp_024` | 1 |
| `heldout_cp_035` | 1 |
| `heldout_cp_036` | 1 |
| `heldout_cp_045` | 1 |
| `heldout_cp_048` | 1 |

Condition distribution among high-risk rows is listed below. This table is for researchers only and should not be shown to blind reviewers.

| Condition | High-risk rows |
| --- | ---: |
| `current_system` + `tutor_only_no_diagnosis` | 6 |
| `bridge_contract` + `tutor_plus_guard` | 6 |
| `codehelp_codeaid_no_direct_solution_tutor` + `tutor_only_no_diagnosis` | 4 |
| `enhanced_prompt_only` + `tutor_only_no_diagnosis` | 4 |
| `bridge_contract` + `tutor_plus_guard_plus_repair` | 2 |
| `bridge_inspired_expert_decision_tutor` + `tutor_only_no_diagnosis` | 1 |
| `dbox_inspired_decomposition_tutor` + `tutor_plus_guard` | 1 |
| `single_llm_structured` + `tutor_plus_guard` | 1 |

## Suggested Coach Workflow

Use this as a two-step targeted review instead of immediately asking coaches to review all 400 rows:

1. Review `high_risk_rows.zh.xlsx` first. The goal is to confirm whether the 25 AI-flagged responses truly contain `major_bridge_leakage` / `answer_leakage`, and to identify false positives.
2. If the 25-row review confirms concentrated failures, review `high_risk_case_pack.zh.xlsx`. The goal is to compare all 8 anonymous system responses within the same case and decide whether the problem is condition-specific, case-specific, or rubric-boundary-specific.

Coach review should focus on:

- whether the response directly completes the current critical bridge for the student;
- whether the response only provides justified background rather than leakage;
- whether a direct code / full-answer request was safely refused;
- whether the micro-example guides observation or fully works through the answer-bearing relation;
- whether Guard / Repair conditions are merely conservative or still preserve instructional progress.

## How To Use The Findings

If coaches find many AI false positives:

- do not directly patch the tutor prompt;
- calibrate the AI preliminary review, static lint, and leakage rubric first;
- add false-positive examples to the Judge calibration set.

If coaches confirm that failures cluster in specific conditions:

- add the corresponding cases to prompt regression;
- inspect whether the condition still uses answer-slot, filled-trace, or worked-example leakage patterns;
- patch only on the development set and freeze before formal held-out evaluation.

If coaches confirm that failures cluster in specific cases:

- inspect whether `missing_bridge`, `forbidden_content`, and `success_criteria` are too strict or underspecified;
- route the case to adjudication before treating it as a system failure.

## Current Takeaway

The 50-case × 8-condition development run is ready for targeted coach review. The next step is not to add more baselines, but to have coaches review the 25 high-risk rows first, confirm whether the AI preliminary review is reliable, and then decide whether full 400-row review or stratified review is necessary.
