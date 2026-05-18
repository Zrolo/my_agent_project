# Dialogue-State v3 Main-Scaffold Paired Uncertainty (20260517)

## Scope

This report uses only the `main_scaffold_eval` slice (31 cases), so clarification and policy-safety cases do not enter the headline tutoring-quality comparison. The primary view is `priority60_adjudicated_plus_coachA`, with Coach A only, Coach B only, and `priority60_adjudicated_plus_coachB` retained as sensitivity views.

Method: paired within-case comparisons. `Δ overall` is first condition minus second condition. The CI is a case-level paired bootstrap 95% interval. The p value is a random sign-flip paired permutation test (20,000 Monte Carlo trials). W/T/L counts per-case overall wins, ties, and losses. `Δ critical leaks` is first minus second for critical/answer leakage counts, so negative is better for the first condition.

## Primary View: priority60 adjudicated + Coach A

| comparison | n | Δ overall | 95% bootstrap CI | paired p | W/T/L | Δ ready | Δ safe-ready | Δ critical leaks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | 31 | +0.2903 | [-0.0968, +0.6452] | 0.2016 | 14/10/7 | -1 | -1 | -2 |
| `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | 31 | +0.0645 | [-0.2258, +0.3548] | 0.8322 | 7/18/6 | -1 | -1 | +0 |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | 31 | +0.2903 | [-0.0323, +0.6129] | 0.1358 | 12/14/5 | +1 | +1 | -2 |
| `dbox_inspired_guard` vs `dbox_inspired_clean` | 31 | +0.0000 | [-0.3548, +0.3548] | 1.0000 | 7/15/9 | +2 | +2 | +0 |
| `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | 31 | +0.6774 | [+0.2581, +1.0645] | 0.0046 | 18/10/3 | +12 | +12 | -7 |
| `bridge_contract_compact_guard` vs `dbox_inspired_guard` | 31 | +0.2258 | [-0.0645, +0.5484] | 0.2360 | 12/12/7 | +0 | +0 | -2 |

## Interpretation

- `bridge_contract_compact_guard_repair` is higher than `dbox_inspired_guard` on overall score (+0.2903) and has 2 fewer critical/answer leaks, but the CI crosses 0 and paired p≈0.2016. This supports a trend/trade-off claim, not a significant-win claim.
- `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` is small (+0.0645, W/T/L=7/18/6) with no critical-leakage advantage, so the main experiment does not establish a causal Repair gain.
- `dbox_inspired_guard` vs `dbox_inspired_clean` has Δ overall=0, reinforcing that guard-only should not be interpreted as final-response repair.
- `codehelp_codeaid_clean` is stronger than `enhanced_prompt_only_clean` in the primary view (+0.6774 with a CI above 0), suggesting strong prompt-only is not a sufficient safety/quality ceiling for this slice.

## Sensitivity

| scenario | comparison | Δ overall | 95% bootstrap CI | paired p | W/T/L |
| --- | --- | --- | --- | --- | --- |
| coach_A_only | `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | +0.2581 | [-0.1613, +0.6774] | 0.3063 | 14/9/8 |
| coach_A_only | `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | -0.0645 | [-0.4194, +0.2903] | 0.8557 | 7/16/8 |
| coach_A_only | `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | +0.1935 | [-0.1613, +0.5161] | 0.3637 | 12/13/6 |
| coach_A_only | `dbox_inspired_guard` vs `dbox_inspired_clean` | -0.0645 | [-0.4194, +0.2903] | 0.8585 | 7/14/10 |
| coach_A_only | `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | +0.4839 | [+0.0968, +0.8710] | 0.0372 | 16/10/5 |
| coach_A_only | `bridge_contract_compact_guard` vs `dbox_inspired_guard` | +0.3226 | [+0.0000, +0.6452] | 0.0866 | 13/12/6 |
| coach_B_only | `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | +0.0323 | [-0.1935, +0.2581] | 1.0000 | 7/18/6 |
| coach_B_only | `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | +0.0968 | [-0.1613, +0.3548] | 0.6359 | 8/17/6 |
| coach_B_only | `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | +0.0645 | [-0.1935, +0.3226] | 0.8089 | 7/18/6 |
| coach_B_only | `dbox_inspired_guard` vs `dbox_inspired_clean` | +0.0323 | [-0.2581, +0.3226] | 1.0000 | 9/14/8 |
| coach_B_only | `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | +0.0323 | [-0.2903, +0.3548] | 1.0000 | 7/15/9 |
| coach_B_only | `bridge_contract_compact_guard` vs `dbox_inspired_guard` | -0.0645 | [-0.3548, +0.2258] | 0.8377 | 5/18/8 |
| priority60_adjudicated_plus_coachA | `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | +0.2903 | [-0.0968, +0.6452] | 0.2016 | 14/10/7 |
| priority60_adjudicated_plus_coachA | `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | +0.0645 | [-0.2258, +0.3548] | 0.8322 | 7/18/6 |
| priority60_adjudicated_plus_coachA | `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | +0.2903 | [-0.0323, +0.6129] | 0.1358 | 12/14/5 |
| priority60_adjudicated_plus_coachA | `dbox_inspired_guard` vs `dbox_inspired_clean` | +0.0000 | [-0.3548, +0.3548] | 1.0000 | 7/15/9 |
| priority60_adjudicated_plus_coachA | `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | +0.6774 | [+0.2581, +1.0645] | 0.0046 | 18/10/3 |
| priority60_adjudicated_plus_coachA | `bridge_contract_compact_guard` vs `dbox_inspired_guard` | +0.2258 | [-0.0645, +0.5484] | 0.2360 | 12/12/7 |
| priority60_adjudicated_plus_coachB | `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | +0.0323 | [-0.2258, +0.2903] | 1.0000 | 7/17/7 |
| priority60_adjudicated_plus_coachB | `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | +0.0323 | [-0.2258, +0.2903] | 1.0000 | 7/17/7 |
| priority60_adjudicated_plus_coachB | `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | +0.0968 | [-0.1290, +0.3226] | 0.5848 | 8/18/5 |
| priority60_adjudicated_plus_coachB | `dbox_inspired_guard` vs `dbox_inspired_clean` | +0.0645 | [-0.1935, +0.3226] | 0.8177 | 9/16/6 |
| priority60_adjudicated_plus_coachB | `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | +0.2581 | [-0.0645, +0.6129] | 0.2208 | 10/16/5 |
| priority60_adjudicated_plus_coachB | `bridge_contract_compact_guard` vs `dbox_inspired_guard` | +0.0000 | [-0.2581, +0.2581] | 1.0000 | 7/16/8 |

## Paper Wording

Safe wording: Bridge Contract compact + Guard/Repair shows a stronger overall/leakage trade-off on the main scaffold slice, but most headline comparisons have uncertainty intervals crossing zero and should be reported with paired uncertainty rather than as single-mean wins. Student-ready and rank preference are sensitive to rater strictness and should be reported as limitations.

Do not claim that guard-only reduced final-response leakage, that Repair causality is proven by the main experiment, or that Bridge Contract significantly dominates all baselines.

Machine-readable outputs: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.csv` and `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.json`.
