# Dialogue-State v3 Coach A / Coach B Agreement Report (2026-05-17)

This report compares the fully overlapping 350-row Coach A and Coach B round-1 reviews. It is used for reliability analysis and adjudication triage.

| metric | value |
| --- | --- |
| overlap rows | 350 |
| overall exact | 0.2829 |
| overall within 1 | 0.8429 |
| overall weighted kappa | 0.0242 |
| overall mean delta B-A | -0.5057 |
| show exact | 0.3429 |
| show weighted kappa | -0.0077 |
| leakage exact | 0.6714 |
| leakage weighted kappa | 0.2433 |
| critical binary exact | 0.9029 |
| critical binary kappa | 0.2511 |
| critical precision B vs A | 0.5385 |
| critical recall B vs A | 0.2 |
| rank mean Spearman by case | 0.0264 |
| top-1 agreement cases | 10/50 |
| last-place agreement cases | 10/50 |
| flagged disagreement rows | 244 |


## Interpretation

- High `overall within 1` means overall quality scores are mostly close even if the raters have different strictness levels.
- Low `critical recall B vs A` means Coach B marked fewer critical leakage cases than Coach A; these disagreements require adjudication.
- `rank mean Spearman` reflects case-level rank stability among the seven anonymous responses.
- Severe disagreements are exported to `dialogue_state_v3_main_coach_A_B_disagreements_20260517.csv`.
