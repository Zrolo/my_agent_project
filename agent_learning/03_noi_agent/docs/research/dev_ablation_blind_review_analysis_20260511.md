# Dev Ablation 10-case Blind Review Analysis

## Data

- Review rows: 110
- Cases: 10
- System conditions: 11
- All rows are labeled.
- This is a development ablation result, not a final held-out conclusion.

## System Summary

| system | n | overall | core available | micro example | student-ready | safe-pass | show yes | major/answer | minor | no leakage | rank1 | mean rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| enhanced_prompt_only | 10 | 3.4 | 1.533 | 0.889 | 4 | 1 | 4 | 4 | 5 | 1 | 1 | 6.4 |
| socratic_no_answer | 10 | 2.7 | 1.367 | 0.333 | 0 | 0 | 6 | 0 | 0 | 10 | 0 | 8.6 |
| codehelp_codeaid | 10 | 3.3 | 1.55 | 1.0 | 4 | 0 | 8 | 0 | 6 | 4 | 0 | 6.3 |
| dbox_inspired | 10 | 3.4 | 1.567 | 0.5 | 5 | 0 | 6 | 3 | 5 | 2 | 0 | 7.5 |
| dbox_inspired+guard | 10 | 3.7 | 1.567 | 1.25 | 6 | 0 | 7 | 0 | 7 | 3 | 0 | 5.9 |
| bridge_inspired | 10 | 3.7 | 1.65 | 1.0 | 6 | 2 | 9 | 0 | 4 | 6 | 0 | 5.7 |
| single_llm | 10 | 3.6 | 1.667 | 1.333 | 6 | 1 | 9 | 0 | 5 | 5 | 0 | 5.6 |
| single_llm+guard | 10 | 3.4 | 1.533 | 0.8 | 5 | 1 | 6 | 2 | 4 | 4 | 1 | 6.1 |
| bridge_contract | 10 | 4.3 | 1.683 | 1.6 | 6 | 0 | 6 | 3 | 7 | 0 | 4 | 3.7 |
| bridge_contract+guard | 10 | 4.0 | 1.667 | 1.444 | 7 | 1 | 7 | 2 | 7 | 1 | 2 | 4.8 |
| bridge_contract+guard+repair | 10 | 3.5 | 1.533 | 1.667 | 6 | 3 | 7 | 1 | 3 | 6 | 2 | 5.4 |

## Paired Comparisons

| comparison | paired cases | mean diff | W/T/L |
| --- | --- | --- | --- |
| bridge_contract+guard+repair - dbox_inspired+guard | 10 | -0.2 | 3/5/2 |
| bridge_contract+guard - dbox_inspired+guard | 10 | 0.3 | 6/1/3 |
| bridge_contract - dbox_inspired | 10 | 0.9 | 7/2/1 |
| bridge_contract+guard+repair - enhanced_prompt_only | 10 | 0.1 | 5/1/4 |
| dbox_inspired+guard - enhanced_prompt_only | 10 | 0.3 | 5/2/3 |
| bridge_contract+guard+repair - single_llm+guard | 10 | 0.1 | 5/1/4 |

## Notes

- Bridge Contract has the highest quality but also substantial bridge leakage.
- Guard/Repair improves safety but can reduce response quality.
- DBox-inspired + guard is a competitive literature-inspired baseline and should remain in the main study.
- This dev set should guide prompt repair and system selection, not headline claims.
