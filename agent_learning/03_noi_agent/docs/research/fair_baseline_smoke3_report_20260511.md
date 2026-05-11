# Fair Baseline Smoke 3 Report

Date: 2026-05-11

This report records a 3-case dev/regression smoke. The goal is not to make a final quality claim. The goal is to verify that the fair baseline combinations needed for the main experiment can run through the same runner, Guard, Repair, and summary pipeline.

## Why This Smoke

External review raised a key fairness question:

```text
If Guard / Repair helps Bridge Contract, can it also help a strong single-LLM baseline?
Why does the system need Bridge Contract specifically?
```

Therefore Research v1 needs to support:

```text
single_llm_structured
single_llm_structured + guard
single_llm_structured + guard + repair
bridge_contract
bridge_contract + guard
bridge_contract + guard + repair
```

This smoke verifies four Guard-enabled paths.

## Input

- Seed: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Limit: 3
- Cases: `cp_bridge_001`, `cp_bridge_002`, `cp_bridge_003`
- Guard mode: `predicted`
- Judge schema mode: `retrieval_augmented_compact_judge`
- Tutor model provider: `deepseek_flash`
- Chat thinking mode: `disabled`
- Judge provider: `deepseek`
- Max retries: `1`

## Systems

| System | Runner Settings |
|---|---|
| `single_llm_structured + guard` | `--tutor-mode single_llm_structured --pipeline-mode tutor_plus_guard` |
| `single_llm_structured + guard + repair` | `--tutor-mode single_llm_structured --pipeline-mode tutor_plus_guard_plus_repair` |
| `bridge_contract + guard` | `--tutor-mode bridge_contract --pipeline-mode tutor_plus_guard` |
| `bridge_contract + guard + repair` | `--tutor-mode bridge_contract --pipeline-mode tutor_plus_guard_plus_repair` |

## Results

Combined files:

- Results JSONL: `evals/aichat/ad_hoc_runs/fair_baseline_smoke3_20260511/combined_fair_baseline_smoke3.jsonl`
- Summary JSON: `evals/aichat/ad_hoc_runs/fair_baseline_smoke3_20260511/combined_fair_baseline_smoke3_summary.json`
- Chinese summary: `evals/aichat/ad_hoc_runs/fair_baseline_smoke3_20260511/combined_fair_baseline_smoke3_summary.zh.md`
- English summary: `evals/aichat/ad_hoc_runs/fair_baseline_smoke3_20260511/combined_fair_baseline_smoke3_summary.md`

Overall:

| Metric | Value |
|---|---:|
| Rows | 12 |
| Completed | 12 |
| Error count | 0 |
| Stage errors | 0 |
| Bridge family accuracy | 1.000 |
| Known focus accuracy | 1.000 |
| Critical bridge leakage rate | 0.000 |
| Answer/code leakage rate | 0.000 |
| Rewrite rate | 0.083 |
| Repair rate | 0.083 |
| Average LLM calls | 2.750 |
| Total latency p50 | 14.144s |
| Total latency p95 | 34.648s |

By group:

| Group | Cases | Safe Actions | Repair Rate | Avg LLM Calls | p50 Latency | p95 Latency |
|---|---:|---|---:|---:|---:|---:|
| `single_llm_structured + guard` | 3 | pass: 3 | 0.000 | 2.000 | 12.932s | 13.406s |
| `single_llm_structured + guard + repair` | 3 | pass: 3 | 0.000 | 2.000 | 10.844s | 12.472s |
| `bridge_contract + guard` | 3 | pass: 3 | 0.000 | 3.333 | 16.950s | 24.326s |
| `bridge_contract + guard + repair` | 3 | pass: 2, rewrite: 1 | 0.333 | 3.667 | 19.798s | 34.648s |

## Repair Trigger

The only repair occurred in:

```text
case: cp_bridge_001
system: bridge_contract + guard + repair
leakage_level: 2
safe_action: rewrite
leaked_elements: directly gave endpoint/LCA marking rules
final_response_source: repair
```

This proves the Repair path can trigger and emit `final_response_source=repair`. It does not prove Repair is effective. Repair still needs 20-30 high-leakage stress candidates and before/after blind review.

## Interpretation

This smoke supports three narrow conclusions:

1. `single_llm_structured + guard` and `single_llm_structured + guard + repair` can run, enabling fair ablations.
2. Bridge Contract paths require more LLM calls and have higher latency, supporting latency / LLM calls as first-class paper metrics.
3. In these three cases, single-LLM paths did not trigger rewrite, while Bridge Contract full path triggered one rewrite. This is not a quality conclusion; it only motivates larger sample and blind review.

## Limitations

- Only 3 dev/regression cases, not held-out test.
- Model outputs are stochastic; the same case may trigger different Guard actions across runs.
- No coach blind review, so final response quality is unknown.
- No `pass^3` stability experiment yet.

## Next Step

Move to a 20-case dev/regression mini-study with:

```text
current_system
single_llm_structured
single_llm_structured + guard
single_llm_structured + guard + repair
bridge_contract
bridge_contract + guard
bridge_contract + guard + repair
```

Then export a new Chinese blind-review workbook for the coach to score only `final_response_text`.
