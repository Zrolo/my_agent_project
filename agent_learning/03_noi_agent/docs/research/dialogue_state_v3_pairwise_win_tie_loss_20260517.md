# Dialogue-State v3 Pairwise Win/Tie/Loss 20260517

## Scope

This file reuses `dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.csv/json` and compares conditions within the same 31 `main_scaffold_eval` cases. `Δ overall` is first condition minus second condition; the confidence interval is a case-level paired bootstrap 95% CI; `paired p` is a random sign-flip permutation test. Negative `Δ major+answer` means fewer critical/answer leaks for the first condition.

## Primary View: priority60 adjudicated + Coach A

| comparison | n | W/T/L | Δ overall | 95% CI | paired p | Δ safe-ready | Δ major+answer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | 31 | 14/10/7 | +0.290 | [-0.097, +0.645] | 0.2016 | -1 | -2 |
| `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | 31 | 7/18/6 | +0.065 | [-0.226, +0.355] | 0.8322 | -1 | +0 |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | 31 | 12/14/5 | +0.290 | [-0.032, +0.613] | 0.1358 | +1 | -2 |
| `dbox_inspired_guard` vs `dbox_inspired_clean` | 31 | 7/15/9 | +0.000 | [-0.355, +0.355] | 1.0000 | +2 | +0 |
| `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | 31 | 18/10/3 | +0.677 | [+0.258, +1.065] | 0.0046 | +12 | -7 |
| `bridge_contract_compact_guard` vs `dbox_inspired_guard` | 31 | 12/12/7 | +0.226 | [-0.065, +0.548] | 0.2360 | +0 | -2 |

## Interpretation

| comparison | paper wording |
| --- | --- |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | Can be described as an overall / leakage trade-off trend; CI crosses 0, so do not claim significant advantage. |
| `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | Does not support a causal Repair claim; W/T/L is close and critical leakage is the same, so use same-candidate stress testing for Repair causality. |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | Can be described as a trend; CI still crosses 0. |
| `dbox_inspired_guard` vs `dbox_inspired_clean` | Guard-only cannot be interpreted as final-response repair; the current path is guard-instrumented. |
| `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | Relatively stable under the primary view; strong prompt-only is not a sufficient upper bound in this dialogue-state CP tutoring setting. |
| `bridge_contract_compact_guard` vs `dbox_inspired_guard` | Can be described as a critical-leakage-control trend; overall CI crosses 0. |

## Sensitivity Summary

- Under Coach A only, `bridge_contract_compact_guard` has slightly higher overall than the repair-enabled version, but `bridge_contract_compact_guard_repair` has lower major+answer leakage.
- Under Coach B only, most overall deltas are near zero, reflecting stricter compressed scoring.
- Under priority60 adjudicated + Coach B, Bridge repair remains slightly ahead in overall, but the gap is small.
- Therefore the paper should report paired uncertainty instead of only mean rankings.

Full machine-readable sensitivity is in `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.csv`.
