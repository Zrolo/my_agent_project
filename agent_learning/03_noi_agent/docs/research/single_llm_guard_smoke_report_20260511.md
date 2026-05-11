# Single-LLM Guard Smoke Report

Date: 2026-05-11

This report records the minimal live smoke for `single_llm_structured + guard` and `single_llm_structured + guard + repair`. The goal is not to make a quality claim. The goal is to verify that the strong single-LLM baseline can use the same Guard / Repair path as Bridge Contract systems, enabling fair ablations.

## Goal

This smoke checks three engineering questions:

1. Can `single_llm_structured` run with `tutor_plus_guard`?
2. Can `single_llm_structured` run with `tutor_plus_guard_plus_repair`?
3. Do the outputs preserve the common fields: `candidate_response_text`, `final_response_text`, `final_response_source`, `repair_applied`, `blocked`, `latency_ms`, and `llm_call_count`?

## Input

- Seed: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Limit: 1
- Case: `cp_bridge_001`
- Tutor mode: `single_llm_structured`
- Guard mode: `predicted`
- Judge schema mode: `retrieval_augmented_compact_judge`
- Tutor model provider: `deepseek_flash`
- Chat thinking mode: `disabled`
- Judge provider: `deepseek`
- Max retries: `1`

## Fixes

The smoke exposed two issues:

1. Leakage Judge sometimes returned `leakage_level > 0` with `leaked_elements=[]`, causing schema invalidation.
2. `single_llm_structured` tutor JSON parsing could fail transiently, but the runner did not retry the tutor stage.

This update:

- adds hard field-consistency rules to `docs/common/aichat_leakage_judge_v1_system_prompt.md`;
- applies `max_retries` to the tutor stage in `evals/aichat/run_bridge_offline_eval.py`;
- adds unit coverage for the prompt rule and tutor-stage transient exception retry.

## Results

Combined summary:

- Cases: 2 rows, same seed case under two pipeline modes.
- Completed: 2/2.
- Error count: 0.
- Stage errors: `{}`.
- Average LLM calls: 2.5.
- Total latency p50: 17.945s.
- Total latency p95: 21.671s.
- `single_llm_structured + guard`: `safe_action=pass`, `repair_applied=false`.
- `single_llm_structured + guard + repair`: `safe_action=rewrite`, `repair_applied=true`.

Summary files:

- `evals/aichat/ad_hoc_runs/single_llm_guard_smoke_20260511/combined_single_llm_guard_limit1_after_retry_fix_summary.json`
- `evals/aichat/ad_hoc_runs/single_llm_guard_smoke_20260511/combined_single_llm_guard_limit1_after_retry_fix_summary.zh.md`
- `evals/aichat/ad_hoc_runs/single_llm_guard_smoke_20260511/combined_single_llm_guard_limit1_after_retry_fix_summary.md`

## Interpretation

This smoke only proves that the path runs. It does not prove that `single_llm + guard/repair` is better.

Important observations:

1. The same case produced different guard actions across two stochastic runs: one pass and one rewrite. The main experiment should therefore use `pass^3` or at least repeated trials for stability.
2. `single_llm + guard + repair` can trigger repair and emit `final_response_source=repair`.
3. Guard/Repair can now be attached to the strong single-LLM baseline, which supports a fair ablation rather than giving Guard/Repair only to Bridge Contract.

## Next Step

Run a 3-case smoke over:

```text
single_llm_structured + guard
single_llm_structured + guard + repair
bridge_contract + guard
bridge_contract + guard + repair
```

If that smoke has no stage errors, expand to the 20-case dev/regression mini-study.
