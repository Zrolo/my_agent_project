# Bridge Contract Prompt Compression Smoke3 Result (2026-05-13)

## Purpose

This smoke run used three dialogue-state v3 development cases to verify that the prompt-compression conditions run end to end, and to get an initial signal on whether compression improves naturalness and student readiness. The result is AI self-review for development triage only. It is not coach gold labeling or a formal paper result.

## Conditions

```text
dbox_inspired_guard
bridge_contract_guard
bridge_contract_compact_guard
bridge_contract_minimal_guard
```

Run output:

```text
evals/aichat/ad_hoc_runs/prompt_compression_smoke3_20260513/
```

## Integrity Check

```text
case_count = 3
condition_count = 4
combined_row_count = 12
final_response_row_count = 12
review_row_count = 12
empty_final_response_rows = 0
stage_warning_rows = 0
headline_ready = true
analysis_ready = true
```

## AI Self-Review Summary

| condition | overall | core6 | student_ready_pass | minor leakage | major/answer leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| bridge_contract_guard | 4.00 | 2.00 | 3/3 | 0 | 0 |
| bridge_contract_compact_guard | 3.67 | 1.94 | 2/3 | 1 | 0 |
| bridge_contract_minimal_guard | 3.67 | 1.94 | 2/3 | 1 | 0 |
| dbox_inspired_guard | 3.33 | 1.89 | 1/3 | 2 | 0 |

## Initial Interpretation

The compressed prompts generated complete, reviewable responses and the run structure was clean. However, on these three representation/state cases, compact/minimal did not outperform the long `bridge_contract_guard`; the AI self-review suggested that the long version remained stronger on student readiness and leakage control.

Therefore, compact/minimal should not replace the default Bridge Contract prompt yet. The next step is:

1. Keep the long prompt as the current development baseline.
2. Expand the `prompt_compression` condition set to a 10-case dev ablation.
3. Check whether compact/minimal improves naturalness on non-state cases.
4. Exclude compact/minimal from the formal held-out main table if their minor/major leakage increases.

## Boundary

This result does not prove that the long prompt is optimal, nor that compact prompts are ineffective. It only says that in this small representation/state smoke run, prompt compression did not immediately improve quality and may weaken leakage control.
