# Definition-first / Post-repair Self-review (2026-05-12)

This report is a development-stage self-review, not a formal held-out result. Its purpose is to check whether the new `post_repair_leakage_judge_result` and `repair_still_leaks` fields expose failed repairs instead of hiding them behind a repaired final response.

## Inputs And Outputs

Input:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/definition_first_regression_cases.jsonl
```

Run condition:

```text
tutor_mode=bridge_contract
pipeline_mode=tutor_plus_guard_plus_repair
guard_mode=predicted
chat_model_provider=deepseek_flash
judge_provider=deepseek
max_retries=1
```

Output:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/bridge_contract_guard_repair_with_post_repair_check_5cases.jsonl
```

Self-review labels:

```text
docs/research/definition_first_post_repair_self_review_20260512.jsonl
```

## Automatic Metrics

| metric | value |
| --- | ---: |
| cases | 5 |
| stage errors | 0 |
| leakage rate | 0.600 |
| critical bridge leakage rate | 0.400 |
| rewrite rate | 0.600 |
| repair rate | 0.600 |
| post-repair check rate | 0.600 |
| repair still leaks rate | 0.333 |
| post-repair rewrite/block rate | 0.333 |
| avg LLM call count | 4.400 |
| p50 latency ms | 42308.399 |
| p95 latency ms | 45699.191 |

## Self-review Results

| case | auto guard | post repair | self leakage | student-ready | quality | interpretation |
| --- | --- | --- | --- | --- | ---: | --- |
| `cp_bridge_001` | level 3 / rewrite | pass | minor bridge leakage | yes | 4 | The repair removes the full endpoint/LCA formula and keeps only endpoint-observation plus a blank table. It still exposes the endpoint `+1` half-step, so the hint risk is minor rather than zero. |
| `cp_bridge_002` | pass | n/a | major bridge leakage | borderline | 3 | The response asks the student to decide whether `check(4)` returns true/false and to summarize what true means. That is the current missing predicate-semantics bridge, so this is an answer-slot Guard false negative. |
| `cp_bridge_003` | pass | n/a | no leakage | yes | 5 | The response only asks the student to explain the meaning of one DP-table cell. It does not directly give the full DP definition or recurrence. |
| `cp_bridge_005` | level 3 / rewrite | level 3 / rewrite | major bridge leakage | no | 2 | The repair still asks for the lazy semantics and keeps a strongly constrained table involving `sum/lazy/current value/target value`. The post-repair judge also marks it as still needing rewrite. |
| `cp_bridge_010` | level 1 / rewrite | pass | minor bridge leakage | yes | 4 | The repair asks the student to choose a tiny example and simulate forward update behavior, without giving the reverse-loop template. It still nudges the student to observe repeated use of the same item. |

## Key Findings

1. `post_repair_leakage_judge_result` is useful: it clearly catches the Repair failure in `cp_bridge_005`.
2. Guard still has false negatives: `cp_bridge_002` packages the missing check true/false semantics as a student fill-in task, and the automatic Guard passes it.
3. Repair is not a safety endpoint: among the 3 repaired cases, 1 still leaks after repair, giving a development-set `repair_still_leaks_rate=0.333`.
4. Quality and safety still trade off: the repaired `cp_bridge_001` and `cp_bridge_010` responses are usable, but both retain small bridge-hint risk.

## Next Implications

Do not keep adding generator prompt rules alone. Next steps should be:

1. Add `cp_bridge_002` to the Guard false-negative regression set, focused on answer-slot and predicate-semantics detection.
2. Add `cp_bridge_005` to the Repair failure regression set, focused on internal-field-update and filled-table leakage.
3. The offline runner now has an optional `--post-repair-fallback-on-leak` condition: if the post-repair judge still returns rewrite/block, the final response switches to deterministic safe fallback instead of the repaired text. See [post_repair_fallback_smoke_20260512.md](post_repair_fallback_smoke_20260512.md).
4. Report `repair_still_leaks_rate` in formal summaries; do not report only `repair_rate`.
