# Dialogue-State v3 Priority60 Adjudicated + Coach A Provisional Analysis (2026-05-17)

This report replaces 60 high-priority A/B disagreement rows with adjudicated labels and keeps Coach A round-1 labels for the remaining 290 rows. It is provisional, not final gold.

## Adjudication Summary

- Adjudicated rows: 60, covered cases: 39.
- Adjudication decisions: {'use_A': 29, 'new_label': 22, 'use_B': 9}.
- Adjudicated leakage labels: {'no_leakage': 37, 'major_bridge_leakage': 16, 'minor_bridge_leakage': 7}.
- Adjudicated student-ready labels: {'yes': 27, 'no': 16, 'unclear': 17}.

## Provisional System Summary

| condition | overall | show_yes | ready_simple | safe_ready | major+answer | minor | adjudicated_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 3.12 | 14 | 14 | 14 | 13 | 19 | 21 |
| codehelp_codeaid_clean | 3.6 | 30 | 30 | 30 | 2 | 9 | 7 |
| dbox_inspired_clean | 3.74 | 33 | 33 | 33 | 3 | 10 | 10 |
| dbox_inspired_guard | 3.72 | 34 | 34 | 34 | 2 | 8 | 5 |
| bridge_guided_dbox_style_guard | 3.66 | 29 | 29 | 29 | 3 | 15 | 4 |
| bridge_contract_compact_guard | 3.86 | 33 | 33 | 32 | 0 | 14 | 9 |
| bridge_contract_compact_guard_repair | 4.02 | 39 | 39 | 39 | 0 | 7 | 4 |

## Interpretation

- This step adjudicates the highest-risk disagreements around critical leakage, show yes/no flips, large overall deltas, and large rank deltas.
- Because the remaining 290 rows still use Coach A labels, this table should be treated as trend evidence rather than final paper results.
