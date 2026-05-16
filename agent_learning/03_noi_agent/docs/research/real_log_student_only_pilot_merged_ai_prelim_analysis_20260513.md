# Real AIChat Student-only 8-case Merged Pilot AI Self-review Analysis (2026-05-13)

This report analyzes 8 real online student-question-only pilot cases, 6 anonymous system conditions, and 48 AI-prelim-reviewed responses. It is a real-log development realism check and EDF-core condition screen, not coach gold labels or a final held-out result.

- Review workbook: `coach_response_review_workbook_real_log_pilot_merged_20260513.ai_prelim.zh.xlsx` (local filled file, not committed)
- Anonymous key: `evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_merged/coach_response_review_workbook_dev_ablation.key.csv`

- Reviewed responses: 48
- Cases: 8
- Leakage labels: {'no_leakage': 38, 'minor_bridge_leakage': 10}
- Bridge reveal justification labels: {'no_reveal': 38, 'borderline': 10}
- Student response burden labels: {'low': 47, 'high': 1}
- Show-to-student labels: {'yes': 31, 'borderline': 17}

## System Summary

| condition | n | overall | core6 | micro7 | rank1 | ready | safe_ready | show yes/border/no | leak no/minor/major+answer | reveal justified/border/unjustified | burden low/medium/high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 8 | 3.75 | 1.9375 | 1.7143 | 0 | 6 | 6 | 6/2/0 | 7/1/0 | 0/1/0 | 8/0/0 |
| dbox_inspired_guard | 8 | 3.75 | 1.9583 | 1.7321 | 0 | 6 | 6 | 6/2/0 | 6/2/0 | 0/2/0 | 8/0/0 |
| edf_inspired_clean | 8 | 3.5 | 1.875 | 1.625 | 0 | 4 | 4 | 4/4/0 | 6/2/0 | 0/2/0 | 7/0/1 |
| edf_inspired_guard | 8 | 3.375 | 1.7917 | 1.5357 | 0 | 3 | 3 | 3/5/0 | 6/2/0 | 0/2/0 | 8/0/0 |
| bridge_contract_guard | 8 | 3.625 | 1.9375 | 1.8035 | 0 | 5 | 5 | 5/3/0 | 5/3/0 | 0/3/0 | 8/0/0 |
| bridge_contract_guard_repair | 8 | 3.875 | 1.9583 | 1.7857 | 0 | 7 | 7 | 7/1/0 | 8/0/0 | 0/0/0 | 8/0/0 |

## Key Paired Comparisons

| comparison | cases | Δ overall | Δ core6 | Δ micro7 | W/T/L | CI95 |
| --- | --- | --- | --- | --- | --- | --- |
| bridge_contract_guard - dbox_inspired_guard | 8 | -0.125 | -0.0208 | 0.0714 | 0/7/1 | [-0.375, 0.0] |
| edf_inspired_guard - edf_inspired_clean | 8 | -0.125 | -0.0833 | -0.0893 | 1/5/2 | [-0.5, 0.375] |
| edf_inspired_guard - dbox_inspired_guard | 8 | -0.375 | -0.1666 | -0.1964 | 0/5/3 | [-0.75, -0.125] |
| bridge_contract_guard - edf_inspired_guard | 8 | 0.25 | 0.1458 | 0.2678 | 3/4/1 | [-0.25, 0.625] |
| bridge_contract_guard_repair - edf_inspired_guard | 8 | 0.5 | 0.1667 | 0.25 | 4/4/0 | [0.125, 0.875] |
| bridge_contract_guard_repair - bridge_contract_guard | 8 | 0.25 | 0.0208 | -0.0179 | 2/6/0 | [0.0, 0.625] |

## Major Leakage Cases

| case | condition | overall | show | reveal justification | coach note |
| --- | --- | --- | --- | --- | --- |

## Development Notes

- The highest `student_ready_pass` condition is `bridge_contract_guard_repair`: 7 / 8.
- This is the EDF core condition set: use it to compare EDF against enhanced prompt / DBox+Guard and to check whether Guard improves EDF.
- Major/answer leakage cases should be inspected qualitatively because fully worked micro-examples can leak the critical bridge without giving code.
- The new bridge-reveal justification field separates useful instructional information from unjustified early completion of the student's current missing bridge.
- Guard/Repair causal effects still require same-candidate before/after repair stress; between-run averages are not enough.
- Use this run to decide whether EDF-inspired should remain an appendix/dev baseline; in this AI-prelim review it trails DBox+Guard and Bridge Contract+Guard+Repair.
