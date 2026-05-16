# EDF-inspired 10-case AI Self-review Analysis (2026-05-12)

This report analyzes 10 development cases, 6 anonymous system conditions, and 60 AI-prelim-reviewed responses. It is EDF-inspired baseline development evidence, not coach gold labels or a final held-out result.

- Review workbook: `coach_response_review_workbook_dev_ablation.ai_prelim.zh.xlsx` (local filled file, not committed)
- Anonymous key: `evals/aichat/ad_hoc_runs/edf_core_ablation_20260512/coach_response_review_workbook_dev_ablation.key.csv`

- Reviewed responses: 60
- Cases: 10
- Leakage labels: {'no_leakage': 33, 'minor_bridge_leakage': 19, 'major_bridge_leakage': 8}
- Bridge reveal justification labels: {'no_reveal': 33, 'borderline': 19, 'unjustified': 8}
- Student response burden labels: {'low': 59, 'high': 1}
- Show-to-student labels: {'yes': 25, 'borderline': 27, 'no': 8}

## System Summary

| condition | n | overall | core6 | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 10 | 3.4 | 1.8833 | 1.7286 | 0 | 5 | 5 | 5/4/1 | 5/4/1 | 0/4/1 | 10/0/0 |
| dbox_inspired_guard | 10 | 3.4 | 1.8833 | 1.6857 | 0 | 5 | 5 | 5/4/1 | 5/4/1 | 0/4/1 | 10/0/0 |
| edf_inspired_clean | 10 | 3.1 | 1.7333 | 1.5 | 0 | 3 | 3 | 3/5/2 | 6/2/2 | 0/2/2 | 10/0/0 |
| edf_inspired_guard | 10 | 2.9 | 1.65 | 1.4286 | 0 | 2 | 2 | 2/5/3 | 6/1/3 | 0/1/3 | 10/0/0 |
| bridge_contract_guard | 10 | 3.4 | 1.8833 | 1.7429 | 0 | 4 | 4 | 4/6/0 | 5/5/0 | 0/5/0 | 9/0/1 |
| bridge_contract_guard_repair | 10 | 3.5 | 1.9 | 1.7428 | 0 | 6 | 6 | 6/3/1 | 6/3/1 | 0/3/1 | 10/0/0 |

## Key Paired Comparisons

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_guard - dbox_inspired_guard | 10 | 0.0 | 0.0 | 0.0571 | 1/8/1 | [-0.3, 0.3] |
| edf_inspired_guard - edf_inspired_clean | 10 | -0.2 | -0.0833 | -0.0714 | 1/6/3 | [-0.6, 0.2] |
| edf_inspired_guard - dbox_inspired_guard | 10 | -0.5 | -0.2333 | -0.2571 | 0/5/5 | [-0.8, -0.2] |
| bridge_contract_guard - edf_inspired_guard | 10 | 0.5 | 0.2333 | 0.3143 | 6/3/1 | [0.1, 0.9] |
| bridge_contract_guard_repair - edf_inspired_guard | 10 | 0.6 | 0.25 | 0.3143 | 5/5/0 | [0.2, 1.0] |
| bridge_contract_guard_repair - bridge_contract_guard | 10 | 0.1 | 0.0167 | -0.0 | 2/7/1 | [-0.2, 0.4] |

## Major Leakage Cases

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |
| cp_bridge_010 | bridge_contract_guard_repair | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_001 | edf_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_010 | edf_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_001 | edf_inspired_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_005 | edf_inspired_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_002 | enhanced_prompt_only_clean | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_005 | edf_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |
| cp_bridge_010 | dbox_inspired_guard | 2.0 | no | unjustified | AI self-review, not coach gold: heuristic preliminary label for dev triage; 请教练复核关键桥泄露、... |

## Development Notes

- The highest `student_ready_pass` condition is `bridge_contract_guard_repair`: 6 / 10.
- This is the EDF core condition set: use it to compare EDF against enhanced prompt / DBox+Guard and to check whether Guard improves EDF.
- Major/answer leakage cases should be inspected qualitatively because fully worked micro-examples can leak the critical bridge without giving code.
- The new bridge-reveal justification field separates useful instructional information from unjustified early completion of the student's current missing bridge.
- Guard/Repair causal effects still require same-candidate before/after repair stress; between-run averages are not enough.
- Use this run to decide whether EDF-inspired should remain an appendix/dev baseline; in this AI-prelim review it trails DBox+Guard and Bridge Contract+Guard+Repair.
