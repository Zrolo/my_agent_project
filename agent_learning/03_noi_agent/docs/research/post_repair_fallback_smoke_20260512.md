# Post-repair Fallback Smoke (2026-05-12)

This is a development-stage smoke report, not a formal held-out result. Its purpose is to verify the new offline runner option `--post-repair-fallback-on-leak` and inspect whether it activates on real model outputs.

## Run Setup

Input:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/definition_first_regression_cases.jsonl
```

Output:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/bridge_contract_guard_repair_post_repair_fallback_5cases.jsonl
```

Run condition:

```text
tutor_mode=bridge_contract
pipeline_mode=tutor_plus_guard_plus_repair
guard_mode=predicted
chat_model_provider=deepseek_flash
judge_provider=deepseek
max_retries=1
post_repair_fallback_on_leak=true
```

## Automatic Metrics

| metric | value |
| --- | ---: |
| cases | 5 |
| stage errors | 0 |
| leakage rate | 0.800 |
| critical bridge leakage rate | 0.000 |
| rewrite rate | 0.600 |
| repair rate | 0.600 |
| post-repair check rate | 0.600 |
| repair still leaks rate | 0.000 |
| post-repair rewrite/block rate | 0.000 |
| average LLM call count | 4.200 |
| p50 latency ms | 28875.869 |
| p95 latency ms | 47958.449 |

## Final Response Source

| case | final source | initial action | post-repair action | repair still leaks | interpretation |
| --- | --- | --- | --- | --- | --- |
| `cp_bridge_001` | repair | rewrite | pass | false | Fallback did not activate; the automatic post-repair judge marked the repair as safe. |
| `cp_bridge_002` | repair | rewrite | pass | false | Fallback did not activate; self-review still sees the check true/false fill-in as close to the missing predicate bridge. |
| `cp_bridge_003` | candidate | pass | n/a | n/a | Repair was not entered. |
| `cp_bridge_005` | repair | rewrite | pass | false | Fallback did not activate; self-review still sees the lazy-semantics task as answer-slot leakage, so the post-repair judge may be a false negative. |
| `cp_bridge_010` | candidate | pass | n/a | n/a | Repair was not entered; self-review still sees a minor forward-loop reuse hint risk. |

## Conclusion

The `--post-repair-fallback-on-leak` path is covered by unit tests: when the post-repair judge still returns rewrite/block, the runner changes `final_response_source` to `safe_fallback_after_repair`. In this 5-case live smoke, however, fallback did not activate because the post-repair judge marked every repaired response as pass.

This means the option solves one failure mode:

```text
Repair still leaks, and the post-repair judge catches it.
```

It does not solve the harder failure mode:

```text
Repair still leaks, but the post-repair judge misses it.
```

Next work should therefore continue calibrating Leakage Judge and Repair around:

1. answer-slot questions: turning the critical bridge into a true/false, table-fill, or candidate-action choice task;
2. internal-field updates: packaging lazy tags, DP cells, boundary updates, or local code slots as student-fill tasks;
3. fully worked micro-examples: examples that do not state a formula but demonstrate the exact relation students were supposed to infer.

Paper wording should stay conservative:

> Post-repair fallback is an offline safety policy that prevents known unsafe repairs from becoming final responses, but it remains limited by post-repair guard recall.
