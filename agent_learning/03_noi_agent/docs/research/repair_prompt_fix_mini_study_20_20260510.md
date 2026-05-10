# Repair Prompt Fix 20-Case Rerun Report (2026-05-10)

## Background

The previous targeted rerun showed that `repair_response_v1` could remove a leaked worked example and then solve a replacement micro-task for the student. That preserves the surface form of repair but can still reveal the missing bridge.

This rerun evaluates only the offline `bridge_contract + guard + repair` pipeline after tightening the repair prompt. It does not mean the online student AIChat has adopted this pipeline.

## Run Settings

- Input: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Output: `evals/aichat/ad_hoc_runs/mini_study_20_20260510/bridge_contract_guard_repair_20_repairpromptfix_clean.jsonl`
- Summary:
  - `evals/aichat/ad_hoc_runs/mini_study_20_20260510/bridge_contract_guard_repair_20_repairpromptfix_clean_summary.json`
  - `evals/aichat/ad_hoc_runs/mini_study_20_20260510/bridge_contract_guard_repair_20_repairpromptfix_clean_summary.md`
- Tutor: `deepseek_flash`
- Thinking: disabled
- Judge schema: `retrieval_augmented_compact_judge`
- Guard: predicted
- Pipeline: `tutor_plus_guard_plus_repair`

## Main Results

| Metric | Value |
| --- | ---: |
| Case count | 20 |
| Completed count | 20 |
| Error count | 0 |
| Bridge family agreement | 0.900 |
| Known focus agreement | 0.800 |
| Help level agreement | 0.950 |
| Candidate leakage rate | 0.300 |
| Candidate critical bridge leakage rate | 0.050 |
| Answer/code leakage rate | 0.000 |
| Rewrite / repair rate | 0.200 |
| Final blocked rate | 0.000 |
| Average LLM calls | 3.600 |
| Total latency p50 | 18.17s |
| Total latency p95 | 29.04s |

The leakage metrics here are Leakage Judge decisions over candidate responses, not proof that the repaired `final_response_text` still leaks.

## Repaired Cases

Four cases triggered rewrite/repair:

- `cp_bridge_003`: DP state semantics. The repaired response asks the student to infer `dp[t]` from `dp[0] / dp[3] / dp[5]`.
- `cp_bridge_006`: Trie shared prefixes. The repaired response asks the student to draw a Trie and observe shared-prefix nodes.
- `cp_bridge_008`: binary-search left boundary. The repaired response asks the student to simulate a duplicate-value array and observe why returning `mid` is not enough.
- `cp_bridge_010`: 0/1 knapsack reverse iteration. The repaired response no longer solves the full contrast example. It asks the student to construct a one-item example and observe whether `dp[c-w]` has already been updated by the current item.

## Key Observations

1. `cp_bridge_010` moved from a fully worked contrast example toward an observation-oriented micro-example. This matches the new bridge-oriented micro-example policy.
2. `repair_response_v1` should be treated as a current-response repair generator, not a second tutor. It should remove leakage, preserve intent, and provide only a half-step scaffold.
3. Latency remains high: p50 is about 18s and p95 is about 29s. This supports the paper claim that the full multi-stage pipeline is suitable for offline evaluation and high-risk turns, not as the default online path.
4. Because LLM generations are stochastic, this rerun should not be interpreted as a strict causal comparison with the previous 20-case run. It is a clean rerun after the repair-prompt fix.

## Research Value

This rerun supports two Research v1 claims:

1. Critical bridge leakage is not limited to complete code or complete solutions. A fully worked micro-example can also leak the current missing bridge.
2. Repair cannot merely rephrase the answer. A high-quality repair should transform an over-strong response into a bridge-oriented micro-example: an observation object, a concrete question, and a transferable abstraction goal.

## Next Step

Recommended next steps:

1. Add the four repaired cases to the response-quality regression set.
2. Export a small Chinese blind-review workbook comparing candidate vs repaired responses.
3. Finalize the rubric for `bridge_oriented_micro_example_score` before expanding to 50 seed cases.
