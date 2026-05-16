# Answer-slot Guard Patch Self-review (2026-05-12)

This is a development-stage self-review, not a formal held-out result. Its purpose is to check whether `judge_patch_20260512_answer_slot_upstream_observation_split` made Leakage Judge more reliable on answer-slot leakage.

## Run Setup

Input:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/definition_first_regression_cases.jsonl
```

Output:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/bridge_contract_guard_repair_answer_slot_guard_patch_5cases.jsonl
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

Self-review labels:

```text
docs/research/answer_slot_guard_patch_self_review_20260512.jsonl
```

## Automatic Metrics

| metric | value |
| --- | ---: |
| cases | 5 |
| stage errors | 0 |
| automatic leakage rate | 0.400 |
| automatic critical bridge leakage rate | 0.000 |
| rewrite rate | 0.200 |
| repair rate | 0.200 |
| post-repair check rate | 0.200 |
| repair still leaks rate | 0.000 |
| average LLM call count | 3.400 |
| p50 latency ms | 34205.981 |
| p95 latency ms | 45179.932 |

## Self-review Results

| case | auto decision | self leakage | student-ready | quality | interpretation |
| --- | --- | --- | --- | ---: | --- |
| `cp_bridge_001` | level 0 / pass | major bridge leakage | no | 2 | The response directly sets endpoint `+1` marks and asks the student to compute the deviation, turning the contribution/aggregation bridge into an endpoint-marking experiment. |
| `cp_bridge_002` | level 1 / pass | major bridge leakage | no | 2 | The response asks the student to answer what `check(mid)` should return and to fill the feasible/infeasible return mapping, which is the missing predicate-semantics bridge. |
| `cp_bridge_003` | level 1 / rewrite, post pass | no leakage | borderline | 3 | The repaired response is safe but generic; it asks about DP dimensions and key variables without closely targeting the state-semantics gap. |
| `cp_bridge_005` | level 0 / pass | major bridge leakage | no | 2 | The response asks the student to fill the lazy stored value, responsible interval, and "means ____ / later needs to ____"; this is an internal-field-semantics answer slot. |
| `cp_bridge_010` | level 0 / pass | major bridge leakage | no | 2 | The response gives one-dimensional DP semantics and an update formula, then asks the student to simulate forward/reverse order; it effectively demonstrates the rolling-array order bridge. |

## Conclusion

This patch did not solve the root issue. The automatic Judge reports:

```text
critical_bridge_leakage_rate = 0.000
repair_still_leaks_rate = 0.000
```

The self-review finds:

```text
4 / 5 rows still have major bridge leakage.
```

The issue is no longer merely whether the prompt says "answer slots may leak." The deeper problem is:

```text
LLM Leakage Judge recall is still unreliable for answer-slot, filled-table, and fully worked micro-example leakage.
```

## Next Implications

Do not keep stacking more Leakage Judge prompt text in the same way. Next work should shift toward:

1. adding deterministic / rule-based high-risk lint as an offline diagnostic signal, not as coach gold;
2. writing `answer_slot_risk_flag`, `filled_trace_risk_flag`, and `worked_example_risk_flag` into result rows to explain Guard misses;
3. reporting, separately in the 10-20 case dev ablation and 50-case held-out runs:
   - automatic Guard label;
   - deterministic risk lint;
   - coach leakage label;
4. stating clearly in the paper that LLM Guard is an object of calibration, not ground truth.

The safer next step is not another generator prompt patch. It is adding interpretable static risk diagnostics so later blind review and Judge calibration can explain why Guard misses happen.

## Follow-up Implementation Note

After this report, the offline runner now records:

```text
candidate_static_leakage_risk_lint
final_static_leakage_risk_lint
```

These fields are diagnostic-only. They are not automatic gold labels and do not directly modify the final response. The summary script reports candidate/final static risk rates, plus answer-slot, filled-trace, and worked-example sub-risk rates.

Applying the static lint to this 5-case output gives a pattern closer to the self-review:

| case | static risk types |
| --- | --- |
| `cp_bridge_001` | answer_slot; filled_trace; worked_example |
| `cp_bridge_002` | answer_slot; worked_example |
| `cp_bridge_003` | none |
| `cp_bridge_005` | answer_slot; filled_trace |
| `cp_bridge_010` | filled_trace; worked_example |

This is not an adjudicated label, but it helps explain automatic Guard false negatives.
