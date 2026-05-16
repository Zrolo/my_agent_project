# Dev Ablation 50-case AI Preliminary Review Analysis

This report analyzes 50 development cases, 5 anonymous system conditions, and 250 AI-prelim-reviewed responses. It is development evidence, not a final held-out result.

- Review workbook: `coach_response_review_workbook_dbox_bridge_hybrid_generation_only_50_20260515.ai_prelim.zh.xlsx` (local filled file, not committed)
- Anonymous key: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/coach_response_review_workbook_dev_ablation.key.csv`

- Reviewed responses: 250
- Cases: 50
- Leakage labels: {'no_leakage': 184, 'answer_leakage': 9, 'minor_bridge_leakage': 52, 'major_bridge_leakage': 5}
- Bridge reveal justification labels: {'no_reveal': 184, 'unjustified': 14, 'borderline': 52}
- Student response burden labels: {'low': 230, 'high': 20}
- Show-to-student labels: {'yes': 181, 'no': 14, 'borderline': 55}

## System Summary

| condition | n | overall | core6 | sufficiency | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 50 | 3.5 | 1.9133 | 1.94 | 1.7486 | 12 | 31 | 31 | 31/16/3 | 31/16/3 | 0/16/3 | 43/0/7 |
| dbox_inspired_clean | 50 | 3.66 | 1.9333 | 1.88 | 1.7086 | 11 | 37 | 37 | 37/10/3 | 38/9/3 | 0/9/3 | 49/0/1 |
| dbox_inspired_guard | 50 | 3.66 | 1.9367 | 1.94 | 1.7114 | 7 | 36 | 36 | 36/12/2 | 37/11/2 | 0/11/2 | 43/0/7 |
| bridge_contract_compact_guard | 50 | 3.6 | 1.9167 | 1.88 | 1.7057 | 8 | 36 | 36 | 36/10/4 | 37/9/4 | 0/9/4 | 48/0/2 |
| bridge_guided_dbox_style_guard | 50 | 3.74 | 1.9567 | 1.96 | 1.7771 | 12 | 41 | 41 | 41/7/2 | 41/7/2 | 0/7/2 | 47/0/3 |

## Key Paired Comparisons

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| dbox_inspired_guard - dbox_inspired_clean | 50 | 0.0 | 0.0033 | 0.0029 | 5/40/5 | [-0.22, 0.22] |
| bridge_contract_compact_guard - dbox_inspired_guard | 50 | -0.06 | -0.02 | -0.0057 | 7/35/8 | [-0.26, 0.14] |
| bridge_guided_dbox_style_guard - dbox_inspired_guard | 50 | 0.08 | 0.02 | 0.0657 | 8/39/3 | [-0.1, 0.26] |

## Major Leakage Cases

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| heldout_v4_luogu_042 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_005 | dbox_inspired_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_006 | dbox_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_044 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_041 | dbox_inspired_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_001 | bridge_contract_compact_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_041 | enhanced_prompt_only_clean | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_044 | bridge_guided_dbox_style_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_002 | dbox_inspired_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_044 | dbox_inspired_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_019 | bridge_contract_compact_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_041 | bridge_guided_dbox_style_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_044 | bridge_contract_compact_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| heldout_v4_luogu_042 | bridge_contract_compact_guard | 1.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |

## Development Notes

- The highest `student_ready_pass` condition is `bridge_guided_dbox_style_guard`: 41 / 50.
- This run did not include `bridge_contract_safe_scaffold` as a normal condition; safe scaffold is used only as a block/fallback mechanism and appendix candidate.
- Major/answer leakage cases should be inspected qualitatively because fully worked micro-examples can leak the critical bridge without giving code.
- The new bridge-reveal justification field separates useful instructional information from unjustified early completion of the student's current missing bridge.
- The new scaffold-sufficiency field flags over-withholding: low leakage is not pedagogical success if the response is safe but not useful.
- Guard/Repair causal effects still require same-candidate before/after repair stress; between-run averages are not enough.
- Use this run to decide which conditions enter the frozen 50-case held-out study, not as a headline result.
