# 10-case Dev Ablation Static Lint Reanalysis (2026-05-12)

This is a development-stage reanalysis, not a formal held-out result. Its purpose is to backfill static leakage-risk lint on the existing `dev_ablation_20260512_safe_scaffold_limit10` outputs and compare automatic Guard labels with interpretable static risk signals.

## Inputs And Outputs

Input:

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation.jsonl
```

Reanalysis outputs:

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_static_lint_summary.json
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_static_lint_summary.md
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_static_lint_summary.zh.md
```

The JSONL was generated before static lint fields were added. The summary script now backfills the following diagnostics from `candidate_response_text` / `final_response_text`:

```text
candidate_static_leakage_risk_lint
final_static_leakage_risk_lint
```

These fields are diagnostic signals only. They are not coach gold labels and do not modify final responses.

## Overall Results

| metric | value |
| --- | ---: |
| rows | 120 |
| automatic leakage rate | 0.150 |
| automatic critical bridge leakage rate | 0.075 |
| final static risk rate | 0.521 |
| final answer-slot risk rate | 0.118 |
| final filled-trace risk rate | 0.378 |
| final worked-example risk rate | 0.176 |

Core signal:

```text
Automatic Guard catches few critical bridge leaks,
but more than half of final responses contain static high-risk patterns.
```

This does not mean more than half are major leakage. Static lint is a high-recall, low-precision diagnostic. It marks positions that deserve coach review and Judge calibration attention.

## Group Results

| condition | final static risk | answer-slot | filled-trace | worked-example | automatic critical leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| `bridge_contract_safe_scaffold` | 0.100 | 0.000 | 0.100 | 0.000 | n/a |
| `socratic_no_answer_clean` | 0.400 | 0.100 | 0.300 | 0.100 | n/a |
| `dbox_inspired_guard` | 0.444 | 0.111 | 0.222 | 0.111 | 0.100 |
| `dbox_inspired_clean` | 0.500 | 0.100 | 0.400 | 0.100 | n/a |
| `single_llm_structured_clean` | 0.500 | 0.100 | 0.400 | 0.100 | n/a |
| `single_llm_structured_guard` | 0.500 | 0.100 | 0.400 | 0.100 | 0.000 |
| `bridge_contract_clean` | 0.600 | 0.200 | 0.400 | 0.300 | n/a |
| `bridge_contract_guard` | 0.600 | 0.100 | 0.400 | 0.400 | 0.100 |
| `enhanced_prompt_only_clean` | 0.600 | 0.200 | 0.500 | 0.100 | n/a |
| `codehelp_codeaid_clean` | 0.600 | 0.000 | 0.400 | 0.400 | n/a |
| `bridge_inspired_expert_decision_clean` | 0.700 | 0.100 | 0.500 | 0.200 | n/a |
| `bridge_contract_guard_repair` | 0.700 | 0.300 | 0.500 | 0.200 | 0.100 |

## Interpretation

1. `bridge_contract_safe_scaffold` has the lowest static risk. This is expected because it is a deterministic L1 safe scaffold, not the main method; it belongs in appendix / fallback comparisons.
2. `bridge_contract_guard_repair` has one of the highest static risk rates, suggesting that Repair does not reliably reduce answer-slot, filled-trace, or worked-example risk.
3. `single_llm_structured_guard` has automatic critical leakage of 0, but static risk remains 0.5, suggesting possible Guard false negatives.
4. `dbox_inspired_guard` has lower static risk than `dbox_inspired_clean`, but it remains 0.444; Guard helps but is incomplete.

## Implications

This reanalysis supports a more robust evaluation framing:

```text
coach label = reference / adjudicated label
LLM Guard = runtime detector under calibration
static lint = interpretable risk signal
```

The formal 50-case held-out should not report only the LLM Guard leakage rate. It should report:

1. coach leakage label;
2. automatic Guard label;
3. static risk lint;
4. Guard false negative / false positive;
5. overlap between static lint and coach-labeled major leakage.

## Next Steps

1. Keep static lint fields in all dev/held-out result rows.
2. Add static-lint versus coach-label cross tabs to the blind-review analysis script.
3. Stop endlessly stacking Guard prompt text; focus on calibrating Guard recall and explaining false negatives.
4. Freeze prompts/rubric before the 50-case held-out, while keeping static lint as diagnostic rather than adjudication.
