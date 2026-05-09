# Response Ablation Smoke Report 2026-05-09

Status: 3-case smoke only. This is not a paper result.

## Purpose

After the 20-case diagnosis-only smoke, this run checks whether the offline response pipeline can produce student-visible `final_response_text` rows for blind coach review.

The run intentionally uses only 3 cases because the tutor stage is much slower than Bridge Judge diagnosis.

## Inputs

- Seed file: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Cases: `cp_bridge_001`, `cp_bridge_002`, `cp_bridge_003`
- Judge mode: `retrieval_augmented_compact_judge`
- Pipeline mode: `tutor_only`
- Tutor modes:
  - `current_system`
  - `bridge_contract`

## Commands

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/response_ablation_20_20260509/current_system_tutor_only_smoke3.jsonl \
  --limit 3 \
  --pipeline-mode tutor_only \
  --tutor-mode current_system \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --judge-provider deepseek \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json

NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=15 python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/response_ablation_20_20260509/bridge_contract_tutor_only_smoke3.jsonl \
  --limit 3 \
  --pipeline-mode tutor_only \
  --tutor-mode bridge_contract \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --judge-provider deepseek \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json
```

## Results

| Tutor mode | Completed | Errors | p50 total latency ms | p95 total latency ms | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| `current_system` | 2/3 | 1 | 103373.550 | 108224.302 | `cp_bridge_001` had Bridge Judge timeout. Successful tutor stages took 86364.894 ms and 101914.439 ms. |
| `bridge_contract` | 3/3 | 0 | 61411.970 | 95647.067 | Tutor stages took 88372.145 ms, 55490.132 ms, and 20477.675 ms. |

The key observation is latency: response generation is far slower than diagnosis-only runs. The 20-case diagnosis-only smoke had p50 around 3.9 seconds; tutor-enabled runs in this smoke frequently took 60-100 seconds total.

This supports the control-harness policy: full multi-stage pipelines should not be the default online path.

## Rerun With Call Counts

After adding `llm_call_count`, the same 3 cases were rerun with `NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=20`.

Outputs:

```text
evals/aichat/ad_hoc_runs/response_ablation_20_20260509/current_system_tutor_only_smoke3_with_calls.jsonl
evals/aichat/ad_hoc_runs/response_ablation_20_20260509/bridge_contract_tutor_only_smoke3_with_calls.jsonl
evals/aichat/ad_hoc_runs/response_ablation_20_20260509/tutor_only_smoke3_with_calls_summary.md
```

| Tutor mode | Completed | Errors | Avg LLM calls | p50 total latency ms | p95 total latency ms | Stage observation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `current_system` | 3/3 | 0 | 2.000 | 114034.351 | 115716.134 | Bridge Judge: 5896-6741 ms; tutor: 56897-109715 ms. |
| `bridge_contract` | 3/3 | 0 | 2.000 | 112376.305 | 113915.315 | Bridge Judge: 5717-6079 ms; tutor: 56572-108198 ms. |

This rerun shows that the `tutor_only` path uses two LLM stages per case: Bridge Judge plus Tutor. The main bottleneck in this smoke is not extra judge depth; it is tutor generation latency. Bridge Judge stayed around 6 seconds, while the Tutor stage often exceeded 100 seconds.

## Blind Review Export

The two smoke result files were combined into:

```text
evals/aichat/ad_hoc_runs/response_ablation_20_20260509/tutor_only_smoke3_combined.jsonl
```

Blind review workbook:

```text
docs/research/coach_response_review_workbook_tutor_only_smoke3.csv
```

Key file, not for blind review:

```text
docs/research/coach_response_review_workbook_tutor_only_smoke3.key.csv
```

The blind workbook has 5 rows because the timed-out `current_system` case did not produce a `final_response_text`.

The rerun with call counts exported a fresh blind workbook with 6 rows:

```text
docs/research/coach_response_review_workbook_tutor_only_smoke3_with_calls.csv
```

Key file, not for blind review:

```text
docs/research/coach_response_review_workbook_tutor_only_smoke3_with_calls.key.csv
```

## Interpretation

This smoke validates the response-review export path, but it also shows that the current tutor-enabled offline ablation is too slow to scale blindly to 20 or 50 cases without a latency strategy.

Recommended next steps:

1. Use the new 6-row blind workbook to check whether coach response scoring columns are understandable.
2. Run only a small response-quality batch next, such as 5 cases across 2 tutor modes.
3. Before full 20-case response ablation, decide the model/thinking mode and latency budget.
4. Keep full guard/repair runs offline; do not wire them into online AIChat.
