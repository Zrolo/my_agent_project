# Single LLM Structured Smoke Report (2026-05-10)

Status: 3-case structural smoke test, not a final paper result.

## Goal

This run checks whether the newly added `single_llm_structured` baseline can be compared with the existing `current_system` and `bridge_contract` tutor modes using the same offline output format.

The key research question is:

```text
Can one LLM diagnose a compact bridge contract, generate the student reply,
and self-check leakage in one call?
```

## Setup

- Seed: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Limit: 3 cases
- Tutor model provider: `deepseek_flash`
- Chat thinking mode: `disabled`
- Pipeline mode: `tutor_only`
- Guard / repair: not run
- Output directory: `evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/`

Commands run:

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/single_llm_structured_tutor_only_smoke3.jsonl \
  --limit 3 \
  --tutor-mode single_llm_structured \
  --pipeline-mode tutor_only \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --judge-schema-mode retrieval_augmented_compact_judge

python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/current_system_tutor_only_smoke3.jsonl \
  --limit 3 \
  --tutor-mode current_system \
  --pipeline-mode tutor_only \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --judge-schema-mode retrieval_augmented_compact_judge

python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/bridge_contract_tutor_only_smoke3.jsonl \
  --limit 3 \
  --tutor-mode bridge_contract \
  --pipeline-mode tutor_only \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --judge-schema-mode retrieval_augmented_compact_judge
```

## Summary

| Tutor mode | Cases | Errors | LLM calls / turn | p50 latency | p95 latency | Bridge family agreement | Focus agreement | Help level agreement | Invalid label rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `current_system` | 3 | 0 | 2.0 | 11666.521 ms | 14098.017 ms | 1.0 | 1.0 | 1.0 | 0.0 |
| `bridge_contract` | 3 | 0 | 2.0 | 12114.546 ms | 12832.904 ms | 1.0 | 1.0 | 1.0 | 0.0 |
| `single_llm_structured` | 3 | 0 | 1.0 | 5828.631 ms | 5908.953 ms | 0.0 | 0.0 | 0.333 | 1.0 |

## Findings

1. `single_llm_structured` is much faster in this smoke run because it uses one LLM call instead of Bridge Judge plus tutor.
2. The one-call baseline produced valid JSON and student-visible replies for all 3 cases.
3. Its contract labels drifted badly: `invalid_label_rate=1.0`. For example, it wrote free-text labels such as `树上差分标记位置` instead of the schema enum `aggregation_contribution_bridge`.
4. The current summary pipeline now counts runtime-contract predictions when calculating single-LLM agreement and flags out-of-schema enum values as invalid labels.
5. This supports keeping `single_llm_structured` as an important baseline, but not assuming it is a reliable runtime controller without stronger constrained decoding or stricter prompt/schema enforcement.

## Interpretation

This is useful evidence for the paper design:

- Single LLM is faster and cheaper.
- Single LLM may be less stable as a structured diagnostic controller.
- Bridge Judge / Bridge Contract costs more latency but produced schema-aligned labels in this 3-case smoke.

Do not over-interpret the quality of the student replies from only 3 cases. The next step is a 20-case mini-study with blind response review.

## Artifacts

- Combined JSONL: `evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/combined_tutor_only_smoke3.jsonl`
- Summary JSON: `evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/combined_tutor_only_smoke3_summary.json`
- English summary MD: `evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/combined_tutor_only_smoke3_summary.md`
- Chinese summary MD: `evals/aichat/ad_hoc_runs/single_llm_structured_smoke_20260510/combined_tutor_only_smoke3_summary.zh.md`
