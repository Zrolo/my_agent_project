# Dev Ablation 10-case + Safe Scaffold Report 20260512

Chinese version: [dev_ablation_safe_scaffold_limit10_report_20260512.zh.md](dev_ablation_safe_scaffold_limit10_report_20260512.zh.md).

## Status

This report is a Research v1 **P1 development ablation**, not a final held-out paper result.

This run extends the 2026-05-11 10-case dev ablation with one explicit appendix / stress condition:

```text
bridge_contract_safe_scaffold
```

It corresponds to:

```text
tutor_mode=bridge_contract
pipeline_mode=deterministic_safe_scaffold
```

This condition is only for offline research comparison. It is not connected to online student AIChat, is not part of the default dev suite, and should not be treated as a main-table conclusion.

## Why This Condition Was Added

The earlier prompt-abstraction smoke exposed an important failure mode:

```text
The clean offline Bridge Contract Tutor removed online prompt contamination,
but on high-risk contribution / aggregation bridges,
prompt-only Bridge Contract can still reveal the critical bridge through micro-examples.
```

The purpose of `deterministic_safe_scaffold` is not to prove that it is the best tutor. It tests:

1. whether a conservative safe scaffold can sharply reduce invocation cost in high-risk turns;
2. whether it can serve as a safe lower-bound route;
3. whether coach blind review finds that the safety gain comes with unacceptable pedagogical quality loss.

## Command

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10 \
  --limit 10 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1 \
  --include-safe-scaffold
```

## Outputs

- Manifest: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/manifest.json`
- Combined JSONL: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation.jsonl`
- Summary JSON: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_summary.json`
- English summary: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_summary.md`
- Chinese summary: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/combined_dev_ablation_summary.zh.md`
- Blind review CSV: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.csv`
- Blind review XLSX: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.zh.xlsx`
- Key CSV, not for blind review: `evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.key.csv`

## Conditions

This run produced 10 seed cases × 12 conditions = 120 system responses:

| Condition | Role |
| --- | --- |
| `enhanced_prompt_only_clean` | strong prompt-only baseline |
| `socratic_no_answer_clean` | Socratic/no-answer literature-inspired baseline |
| `codehelp_codeaid_clean` | no-direct-solution programming-education baseline |
| `dbox_inspired_clean` | DBox-inspired decomposition baseline |
| `dbox_inspired_guard` | DBox-inspired + same Leakage Guard |
| `bridge_inspired_expert_decision_clean` | Bridge-inspired expert-decision baseline |
| `single_llm_structured_clean` | one-call structured LLM baseline |
| `single_llm_structured_guard` | single LLM + same Leakage Guard |
| `bridge_contract_clean` | Bridge Contract tutor |
| `bridge_contract_guard` | Bridge Contract + Leakage Guard |
| `bridge_contract_guard_repair` | Bridge Contract + Leakage Guard + Repair |
| `bridge_contract_safe_scaffold` | Bridge Judge + deterministic safe scaffold appendix condition |

## Automatic Run Summary

| Metric | Value |
| --- | ---: |
| case count | 10 |
| condition count | 12 |
| combined rows | 120 |
| completed rows | 120 |
| error count | 0 |
| blind review rows | 120 |
| answer/code leakage rate, auto Leakage Judge | 0.000 |
| critical bridge leakage rate, auto Leakage Judge | 0.075 |
| rewrite rate, auto Leakage Judge | 0.100 |
| block rate, auto Leakage Judge | 0.025 |
| repair rate | 0.008 |
| average LLM call count | 1.742 |
| total latency p50 | 17881.903 ms |
| total latency p95 | 47912.565 ms |
| stage error count | 1 leakage_judge |

The automatic leakage metrics come from the runtime/offline Leakage Judge, not from coach labels. They are risk-tracing signals, not headline paper-quality judgments.

## Per-condition Operational Summary

| condition | completed | safe_action/source | repair | avg calls | p50 latency ms | max latency ms |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 10/10 | n/a | 0 | 1.0 | 23317.5 | 47912.6 |
| `socratic_no_answer_clean` | 10/10 | n/a | 0 | 1.1 | 29341.0 | 58060.1 |
| `codehelp_codeaid_clean` | 10/10 | n/a | 0 | 1.0 | 10016.4 | 17475.8 |
| `dbox_inspired_clean` | 10/10 | n/a | 0 | 1.0 | 11060.8 | 16623.9 |
| `dbox_inspired_guard` | 10/10 | block 1, pass 8, unknown 1 | 0 | 3.2 | 23417.9 | 30500.2 |
| `bridge_inspired_expert_decision_clean` | 10/10 | n/a | 0 | 1.0 | 8700.0 | 9672.1 |
| `single_llm_structured_clean` | 10/10 | n/a | 0 | 1.0 | 16201.8 | 25572.6 |
| `single_llm_structured_guard` | 10/10 | pass 10 | 0 | 2.2 | 23936.8 | 41411.3 |
| `bridge_contract_clean` | 10/10 | n/a | 0 | 2.0 | 20841.2 | 47071.1 |
| `bridge_contract_guard` | 10/10 | pass 7, rewrite 3 | 0 | 3.2 | 31865.5 | 53539.6 |
| `bridge_contract_guard_repair` | 10/10 | pass 9, rewrite 1 | 1 | 3.2 | 31949.0 | 60161.4 |
| `bridge_contract_safe_scaffold` | 10/10 | safe_fallback 10 | 0 | 1.0 | 3739.1 | 4899.1 |

## Early Observations

1. **The toolchain produced 120 reviewable responses.**
   The manifest reports `combined_row_count=120`, and the review key has 120 rows. Safe scaffold was not dropped from the review export.

2. **Safe scaffold is substantially faster.**
   `bridge_contract_safe_scaffold` uses 1 LLM call on average and has p50 latency around 3.7 seconds. It runs Bridge Judge and then returns a deterministic safe observation task.

3. **Safe scaffold quality cannot be judged from the automatic summary.**
   It does not run Leakage Judge, so automatic critical bridge leakage is n/a. Whether it is safe but too vague must be judged by coach blind review.

4. **Bridge Contract + Guard / Repair remains expensive.**
   `bridge_contract_guard` and `bridge_contract_guard_repair` average around 3.2 LLM calls with p50 latency around 31.9 seconds. This reinforces that online deployment should not default to full multi-stage execution on every turn.

5. **Guard behavior varies across generators.**
   `dbox_inspired_guard` produced block / unknown decisions, `single_llm_structured_guard` passed all ten, and `bridge_contract_guard` triggered rewrites. Guard must be evaluated across generator families rather than treated as Bridge-only.

6. **Repair is still rarely triggered in natural dev samples.**
   Only one row used `repair` as the final response source. Repair's causal value should mainly be evaluated through repair-stress before/after experiments.

## How To Review

Open this workbook for coach blind review:

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.zh.xlsx
```

Do not show this key file to the coach:

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_limit10/coach_response_review_workbook_dev_ablation.key.csv
```

The key CSV maps anonymous response ids back to system conditions after blind review.

## Key Blind-review Comparisons

The most important paired comparisons in this run are:

- `bridge_contract_safe_scaffold` vs `bridge_contract_clean`
- `bridge_contract_safe_scaffold` vs `bridge_contract_guard`
- `bridge_contract_safe_scaffold` vs `enhanced_prompt_only_clean`
- `bridge_contract_safe_scaffold` vs `dbox_inspired_guard`

Review questions:

```text
Does safety clearly improve?
Does the response become too conservative or pedagogically weak?
Does the student still know what to do next?
Is this suitable as a high-risk fallback rather than a default tutor?
```

## Interpretation Boundary

This report only shows that:

```text
the safe scaffold appendix condition now runs in the same dev ablation workflow;
it has substantially lower cost;
it produces student-visible responses for blind review;
the next step is coach review of the quality-safety trade-off.
```

It does not show that:

```text
safe scaffold is better than Bridge Contract;
safe scaffold should enter the main table;
automatic Leakage Judge labels are final gold labels;
10-case dev results are final headline paper results.
```

## Next Step

1. Have the coach fill `coach_response_review_workbook_dev_ablation.zh.xlsx`.
2. Parse the filled workbook into blind-review JSONL.
3. Run paired analysis by condition, especially comparing safe scaffold against Bridge Contract variants.
4. Decide from coach review:
   - whether safe scaffold belongs only in appendix;
   - whether it should become a high-risk routing candidate;
   - which conditions should enter the 50-case held-out main table.
