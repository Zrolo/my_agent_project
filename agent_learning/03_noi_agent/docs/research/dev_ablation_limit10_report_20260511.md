# Dev Ablation 10-case Report 20260511

Chinese version: [dev_ablation_limit10_report_20260511.zh.md](dev_ablation_limit10_report_20260511.zh.md).

## Status

This report is a Research v1 **P1 development ablation**, not a final held-out paper result.

It checks whether:

1. the strong prompt-only baseline is available in the shared runner;
2. the DBox-inspired decomposition baseline can enter the same evaluation pipeline;
3. DBox-inspired + Guard can be compared fairly with Bridge Contract + Guard;
4. Bridge Contract / Guard / Repair conditions are operationally stable enough for coach blind review.

## Command

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10 \
  --limit 10 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

## Outputs

- Manifest: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/manifest.json`
- Combined JSONL: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/combined_dev_ablation.jsonl`
- Summary JSON: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/combined_dev_ablation_summary.json`
- English summary: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/combined_dev_ablation_summary.md`
- Chinese summary: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/combined_dev_ablation_summary.zh.md`
- Blind review CSV: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.csv`
- Blind review XLSX: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.zh.xlsx`
- Key CSV, not for blind review: `evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.key.csv`

## Conditions

This run produced 10 seed cases × 11 conditions = 110 system responses:

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

## Automatic Run Summary

| Metric | Value |
| --- | ---: |
| case count | 10 |
| condition count | 11 |
| combined rows | 110 |
| completed rows | 110 |
| stage error count | 0 |
| blind review rows | 110 |
| answer/code leakage rate, auto Leakage Judge | 0.000 |
| critical bridge leakage rate, auto Leakage Judge | 0.075 |
| rewrite rate, auto Leakage Judge | 0.200 |
| repair rate | 0.009 |
| average LLM call count | 1.755 |
| total latency p50 | 21934.524 ms |
| total latency p95 | 50102.215 ms |

The automatic leakage metrics come from the runtime/offline Leakage Judge, not from coach labels. They are risk-tracing signals, not headline paper-quality judgments.

## Per-condition Operational Summary

| condition | completed | safe_action | repair | avg calls | p50 latency ms | max latency ms |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `enhanced_prompt_only_clean` | 10/10 | n/a | 0 | 1.0 | 24351.5 | 34538.2 |
| `socratic_no_answer_clean` | 10/10 | n/a | 0 | 1.0 | 26331.0 | 72096.7 |
| `codehelp_codeaid_clean` | 10/10 | n/a | 0 | 1.0 | 10232.7 | 19662.7 |
| `dbox_inspired_clean` | 10/10 | n/a | 0 | 1.0 | 10515.9 | 19597.0 |
| `dbox_inspired_guard` | 10/10 | pass 8, rewrite 2 | 0 | 3.0 | 24993.5 | 33268.6 |
| `bridge_inspired_expert_decision_clean` | 10/10 | n/a | 0 | 1.0 | 10331.7 | 16431.8 |
| `single_llm_structured_clean` | 10/10 | n/a | 0 | 1.0 | 17663.0 | 25848.7 |
| `single_llm_structured_guard` | 10/10 | pass 8, rewrite 2 | 0 | 2.0 | 22654.5 | 27379.5 |
| `bridge_contract_clean` | 10/10 | n/a | 0 | 2.0 | 41629.0 | 52130.1 |
| `bridge_contract_guard` | 10/10 | pass 7, rewrite 3 | 0 | 3.2 | 41360.6 | 84366.8 |
| `bridge_contract_guard_repair` | 10/10 | pass 9, rewrite 1 | 1 | 3.1 | 34845.5 | 65898.9 |

## Early Observations

1. **The toolchain is ready for coach blind review.**
   All 110 system responses were generated, and the review XLSX contains 110 anonymized rows.

2. **The DBox-inspired baseline is now stable.**
   The previous status-alias parsing issue is fixed. Both DBox-inspired clean and DBox-inspired + Guard completed 10/10.

3. **DBox-inspired and CodeHelp/CodeAid-style are much lighter baselines.**
   They are 1-call baselines with p50 latency around 10 seconds, so they are strong engineering baselines.

4. **Bridge Contract conditions are substantially more expensive.**
   `bridge_contract_clean` has p50 latency around 41.6 seconds. `bridge_contract_guard` has p50 around 41.4 seconds and max latency 84.4 seconds. The paper must treat latency/cost as first-class metrics.

5. **Guard rewrite triggers are not Bridge-only.**
   DBox-inspired + Guard, single-LLM + Guard, and Bridge Contract + Guard all triggered rewrites. Guard value must be compared across generator families.

6. **Repair is rarely triggered in natural dev samples.**
   Repair triggered only once in this 10-case run. Repair's causal value still requires a separate repair-stress before/after experiment.

## How To Review

Open this workbook for coach blind review:

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.zh.xlsx
```

Do not show this key file to the coach:

```text
evals/aichat/ad_hoc_runs/dev_ablation_20260511_limit10/coach_response_review_workbook_dev_ablation.key.csv
```

The key CSV maps anonymous response ids back to system conditions after blind review.

## Interpretation Boundary

This report only shows that:

```text
P1 dev ablation runs stably;
strong prompt, DBox-inspired, CodeHelp-style, Bridge-inspired, and Bridge Contract variants can be compared in one pipeline;
the next step is coach blind review and paired analysis.
```

It does not show that:

```text
Bridge Contract is better than DBox-inspired;
Guard/Repair are proven effective;
automatic Leakage Judge labels are final gold labels;
10-case dev results are final headline paper results.
```

## Next Step

1. Have the coach fill `coach_response_review_workbook_dev_ablation.zh.xlsx`.
2. Parse the filled workbook into blind-review JSONL.
3. Run paired analysis by condition:
   - `enhanced_prompt_only` vs `bridge_contract_clean`
   - `dbox_inspired_clean` vs `bridge_contract_clean`
   - `dbox_inspired_guard` vs `bridge_contract_guard`
   - `single_llm_structured_guard` vs `bridge_contract_guard`
   - `bridge_contract_guard` vs `bridge_contract_guard_repair`
4. Decide which conditions enter the 50-case held-out main table and which move to appendix.
