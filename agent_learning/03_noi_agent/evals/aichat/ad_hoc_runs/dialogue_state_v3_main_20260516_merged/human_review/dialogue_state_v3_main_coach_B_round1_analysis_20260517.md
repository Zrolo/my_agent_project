# Dialogue-State v3 Coach B Round1 Blind Review Analysis (2026-05-17)

This report analyzes the full 350-row Coach B overlap review. It is second-rater evidence, not adjudicated gold.

| condition | overall | show_yes | ready_simple | safe_ready | major+answer | rank1 | rank7 | needs_discussion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only_clean | 3.18 | 17 | 17 | 17 | 4 | 7 | 7 | 7 |
| codehelp_codeaid_clean | 3.1 | 10 | 10 | 10 | 1 | 4 | 10 | 5 |
| dbox_inspired_clean | 3.2 | 15 | 15 | 15 | 3 | 10 | 8 | 5 |
| dbox_inspired_guard | 3.22 | 16 | 16 | 16 | 1 | 10 | 3 | 5 |
| bridge_guided_dbox_style_guard | 3.14 | 12 | 12 | 12 | 2 | 7 | 5 | 5 |
| bridge_contract_compact_guard | 3.1 | 9 | 9 | 9 | 1 | 6 | 11 | 5 |
| bridge_contract_compact_guard_repair | 3.24 | 14 | 14 | 14 | 1 | 6 | 6 | 3 |


## Main Observations

- Under Coach B, the highest-overall condition is `bridge_contract_compact_guard_repair` with mean 3.24.
- Under Coach B, the most ready_simple condition is `enhanced_prompt_only_clean` with 17/50.
- Under Coach B, the lowest major/answer leakage condition is `codehelp_codeaid_clean` with 1/50.
- Coach B is stricter than Coach A overall; adjudication is required before final claims.
