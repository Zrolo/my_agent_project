# Tutor Thinking Ablation Smoke Report 2026-05-09

Status: 3-case smoke only. This is not a paper result.

Chinese version: `docs/research/tutor_thinking_ablation_smoke_report_20260509.zh.md`

## Purpose

This smoke isolates Tutor generation latency under the same offline research pipeline:

- `pipeline_mode=tutor_only`
- `tutor_mode=bridge_contract`
- `judge_schema_mode=retrieval_augmented_compact_judge`
- `judge_provider=deepseek`
- `chat_model_provider=deepseek_flash`

The only experimental variable is Tutor thinking mode:

- `--chat-thinking-mode enabled`
- `--chat-thinking-mode disabled`

## Inputs

- Seed file: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Cases: `cp_bridge_001`, `cp_bridge_002`, `cp_bridge_003`
- Focus registry: `docs/research/focus_registry_v1.json`

## Commands

```bash
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=20 python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_enabled_smoke3.jsonl \
  --limit 3 \
  --pipeline-mode tutor_only \
  --tutor-mode bridge_contract \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --judge-provider deepseek \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode enabled \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json

NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=20 python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_disabled_smoke3.jsonl \
  --limit 3 \
  --pipeline-mode tutor_only \
  --tutor-mode bridge_contract \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --judge-provider deepseek \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json
```

## Results

| Tutor model | Thinking mode | Completed | Errors | Avg LLM calls | p50 total latency ms | p95 total latency ms | Tutor latency range ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `deepseek_flash` | `enabled` | 3/3 | 0 | 2.000 | 40918.400 | 41220.855 | 21923.205-35726.892 |
| `deepseek_flash` | `disabled` | 3/3 | 0 | 2.000 | 14081.960 | 16963.281 | 6145.421-10444.663 |

Per-case stage latency:

| Case | Thinking | Total ms | Bridge Judge ms | Tutor ms |
| --- | --- | ---: | ---: | ---: |
| `cp_bridge_001` | enabled | 40918.400 | 6342.989 | 34574.247 |
| `cp_bridge_002` | enabled | 28052.861 | 6127.711 | 21923.205 |
| `cp_bridge_003` | enabled | 41220.855 | 5492.550 | 35726.892 |
| `cp_bridge_001` | disabled | 14081.960 | 5644.357 | 8436.996 |
| `cp_bridge_002` | disabled | 16963.281 | 6517.299 | 10444.663 |
| `cp_bridge_003` | disabled | 11663.749 | 5517.083 | 6145.421 |

## Blind Review Export

Combined result JSONL:

```text
evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_enabled_vs_disabled_smoke3.jsonl
```

Summary:

```text
evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_enabled_vs_disabled_smoke3_summary.md
```

Blind review workbook:

```text
docs/research/coach_response_review_workbook_deepseek_flash_thinking_smoke3.csv
```

Key file, not for blind review:

```text
docs/research/coach_response_review_workbook_deepseek_flash_thinking_smoke3.key.csv
```

## Interpretation

This smoke suggests that Tutor thinking mode can dominate latency even when the number of LLM stages is unchanged. Both conditions used two LLM stages per case: Bridge Judge plus Tutor. Bridge Judge latency stayed near 5.5-6.5 seconds, while Tutor latency changed substantially.

The latency result alone is not enough to choose a default mode. `thinking=disabled` is much faster in this smoke, but the next decision must use blind coach scoring to check whether it weakens scaffold quality or increases critical bridge leakage.

## Next Step

Use the blind workbook to score response quality before changing any online AIChat default. Suggested comparison dimensions:

- bridge fit;
- scaffold appropriateness;
- leakage control;
- next-step clarity;
- single-focus coherence;
- overall coach preference.

Do not promote `thinking=disabled` to the online default based on latency alone.
