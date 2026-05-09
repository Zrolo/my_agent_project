# Single LLM Strict Schema Smoke Report (2026-05-10)

Status: 3-case prompt ablation smoke test, not a final paper result.

## Goal

The previous `single_llm_structured` smoke showed that one LLM call was fast, but it produced out-of-schema free-text labels such as `树上差分标记位置`.

This run tests a stricter one-call prompt:

- exact enum lists for `turn_type`, `algorithm_topic_l1`, `primary_bridge_family`, `max_scaffold_level`, and `leakage_risk`;
- explicit instruction not to output Chinese free-form schema labels;
- top-k `algorithm_topic` and `registered_focus` candidates injected as a non-LLM retrieval signal;
- `selected_focus_id` restricted to top-k candidates or `unknown`.

## Setup

- Seed: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Limit: 3 cases
- Tutor model provider: `deepseek_flash`
- Chat thinking mode: `disabled`
- Pipeline mode: `tutor_only`
- Guard / repair: not run
- Output directory: `evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/`

## Result

| Single-LLM variant | Cases | Errors | LLM calls / turn | p50 latency | p95 latency | Bridge family agreement | Focus agreement | Help level agreement | Invalid label rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| loose schema prompt | 3 | 0 | 1.0 | 5828.631 ms | 5908.953 ms | 0.0 | 0.0 | 0.333 | 1.0 |
| strict schema + top-k candidates | 3 | 0 | 1.0 | 6413.114 ms | 7712.401 ms | 1.0 | 1.0 | 0.0 | 0.0 |

## Interpretation

The strict prompt fixed the most important structural problem in this 3-case smoke:

- invalid label rate dropped from `1.0` to `0.0`;
- bridge family agreement rose from `0.0` to `1.0`;
- focus agreement rose from `0.0` to `1.0`.

The trade-off is that latency increased modestly because the prompt is longer and includes top-k candidates. The one-call baseline is still faster than the two-call Bridge Judge + Tutor variants from the previous smoke.

The strict prompt did not match the coach reference scaffold level in these 3 cases: it selected `L1` for all three, while the reference labels use `L2`. This is useful error evidence. The next prompt iteration should focus on help-level calibration rather than schema validity.

## Paper Value

This supports a clean ablation:

```text
single_llm_loose_schema:
  fast, but label drift is high.

single_llm_strict_schema_topk:
  still one LLM call, label drift drops, but help-strength calibration may remain weak.
```

This is exactly the kind of baseline needed before claiming that multi-stage Bridge Judge control is necessary.

## Artifacts

- Strict JSONL: `evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/single_llm_structured_strict_tutor_only_smoke3.jsonl`
- Strict summary JSON: `evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/single_llm_structured_strict_tutor_only_smoke3_summary.json`
- Strict English summary: `evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/single_llm_structured_strict_tutor_only_smoke3_summary.md`
- Strict Chinese summary: `evals/aichat/ad_hoc_runs/single_llm_structured_strict_smoke_20260510/single_llm_structured_strict_tutor_only_smoke3_summary.zh.md`
