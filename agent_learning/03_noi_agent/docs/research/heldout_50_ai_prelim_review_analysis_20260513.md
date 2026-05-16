# Dev Ablation 50-case AI Preliminary Review Analysis

This report analyzes 50 development cases, 8 anonymous system conditions, and 400 AI-prelim-reviewed responses. It is development evidence, not a final held-out result.

- Review workbook: `coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx` (local filled file, not committed)
- Anonymous key: `evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged/coach_response_review_workbook_dev_ablation.key.csv`

- Reviewed responses: 400
- Cases: 50
- Leakage labels: {'no_leakage': 300, 'minor_bridge_leakage': 75, 'major_bridge_leakage': 9, 'answer_leakage': 16}
- Bridge reveal justification labels: {'no_reveal': 300, 'borderline': 75, 'unjustified': 25}
- Student response burden labels: {'low': 386, 'high': 14}
- Show-to-student labels: {'yes': 282, 'borderline': 93, 'no': 25}

## System Summary

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_system_deployment | 50 | 3.5 | 1.9067 | 1.88 | 1.7371 | 0 | 36 | 36 | 36/8/6 | 36/8/6 | 0/8/6 | 45/0/5 |
| enhanced_prompt_only_clean | 50 | 3.44 | 1.9 | 1.9 | 1.7314 | 0 | 30 | 30 | 30/16/4 | 31/15/4 | 0/15/4 | 49/0/1 |
| socratic_no_answer_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| codehelp_codeaid_clean | 50 | 3.62 | 1.92 | 1.88 | 1.7543 | 0 | 36 | 36 | 36/10/4 | 38/8/4 | 0/8/4 | 50/0/0 |
| dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| dbox_inspired_guard | 50 | 3.7 | 1.94 | 1.94 | 1.74 | 0 | 37 | 37 | 37/12/1 | 38/11/1 | 0/11/1 | 46/0/4 |
| edf_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| bridge_inspired_expert_decision_clean | 50 | 3.68 | 1.9067 | 1.78 | 1.68 | 0 | 36 | 36 | 36/13/1 | 44/5/1 | 0/5/1 | 50/0/0 |
| single_llm_structured_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| single_llm_structured_guard | 50 | 3.68 | 1.9267 | 1.88 | 1.7086 | 0 | 35 | 35 | 35/14/1 | 40/9/1 | 0/9/1 | 49/0/1 |
| bridge_contract_clean | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| bridge_contract_guard | 50 | 3.5 | 1.9067 | 1.84 | 1.7314 | 0 | 34 | 34 | 34/10/6 | 34/10/6 | 0/10/6 | 49/0/1 |
| bridge_contract_guard_repair | 50 | 3.7 | 1.9433 | 1.94 | 1.7628 | 0 | 38 | 38 | 38/10/2 | 39/9/2 | 0/9/2 | 48/0/2 |
| bridge_contract_safe_scaffold | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |

## Key Paired Comparisons

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_safe_scaffold - bridge_contract_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - bridge_contract_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_safe_scaffold - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard - dbox_inspired_guard | 50 | -0.2 | -0.0333 | -0.0086 | 3/38/9 | [-0.4, -0.02] |
| edf_inspired_guard - edf_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| edf_inspired_guard - dbox_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard - edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard_repair - edf_inspired_guard | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| bridge_contract_guard_repair - bridge_contract_guard | 50 | 0.2 | 0.0367 | 0.0314 | 8/39/3 | [0.0, 0.42] |
| bridge_contract_clean - enhanced_prompt_only_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| dbox_inspired_guard - dbox_inspired_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |
| single_llm_structured_guard - single_llm_structured_clean | 0 | 0.0 | 0.0 | 0.0 | 0/0/0 | [0.0, 0.0] |

## Major Leakage Cases

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| heldout_cp_035 | current_system_deployment | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | codehelp_codeaid_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_014 | bridge_contract_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_048 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_019 | bridge_contract_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | bridge_inspired_expert_decision_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | bridge_contract_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_019 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_045 | codehelp_codeaid_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_039 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | bridge_contract_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | codehelp_codeaid_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_003 | bridge_contract_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | dbox_inspired_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | single_llm_structured_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_017 | bridge_contract_guard_repair | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_024 | codehelp_codeaid_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_039 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_036 | current_system_deployment | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_014 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_044 | bridge_contract_guard_repair | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_cp_039 | bridge_contract_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |

## Development Notes

- The highest `student_ready_pass` condition is `bridge_contract_guard_repair`: 38 / 50.
- This run did not include `bridge_contract_safe_scaffold` as a normal condition; safe scaffold is used only as a block/fallback mechanism and appendix candidate.
- Major/answer leakage cases should be inspected qualitatively because fully worked micro-examples can leak the critical bridge without giving code.
- The new bridge-reveal justification field separates useful instructional information from unjustified early completion of the student's current missing bridge.
- The new scaffold-sufficiency field flags over-withholding: low leakage is not pedagogical success if the response is safe but not useful.
- Guard/Repair causal effects still require same-candidate before/after repair stress; between-run averages are not enough.
- Use this run to decide which conditions enter the frozen 50-case held-out study, not as a headline result.
