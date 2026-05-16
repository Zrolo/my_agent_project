# Definition-first / Worked-example Regression Smoke (2026-05-12)

This is a targeted development smoke, not a final held-out result. It checks whether the previous prompt/rubric patch reduced these failure modes on `cp_bridge_001/002/003/005/010`:

- definition-first leakage;
- fully worked micro-example leakage;
- canonical-template leakage;
- answer-slot questions.

## Run Conditions

Input:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/definition_first_regression_cases.jsonl
```

Conditions:

```text
bridge_contract + guard + repair
dbox_inspired + guard
```

Outputs:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/bridge_contract_guard_repair.jsonl
evals/aichat/ad_hoc_runs/definition_first_regression_20260512/dbox_inspired_guard.jsonl
```

## Automatic Run Status

| condition | cases | stage errors | notes |
| --- | ---: | ---: | --- |
| `bridge_contract_guard_repair` | 5 | 2 | `cp_bridge_001` leakage judge timeout; `cp_bridge_005` bridge judge schema enum invalid. |
| `dbox_inspired_guard` | 5 | 0 | Completed. |

## Self-review Notes

| case | condition | automated guard | self-review | reason |
| --- | --- | --- | --- | --- |
| `cp_bridge_001` | `bridge_contract_guard_repair` | leakage timeout | high risk / likely major | The response asks the student to find the minus mark location and summarize its relation to endpoints/common ancestor. |
| `cp_bridge_002` | `bridge_contract_guard_repair` | pass | acceptable to minor | The tiny example asks true/false semantics without directly stating the answer, but remains close to the check-semantics bridge. |
| `cp_bridge_003` | `bridge_contract_guard_repair` | pass | acceptable | The response asks the student to map knapsack dimensions to time without giving the complete state definition. |
| `cp_bridge_005` | `bridge_contract_guard_repair` | bridge judge error | unknown | No final response to review. |
| `cp_bridge_010` | `bridge_contract_guard_repair` | level 2 / pass | minor risk | The response does not fully compute the table, but gives a strong forward/backward comparison frame. |
| `cp_bridge_001` | `dbox_inspired_guard` | pass | likely major | It directly asks which nodes receive +1 and -1, which is the current answer slot. |
| `cp_bridge_002` | `dbox_inspired_guard` | pass | minor to major | It directly asks whether `true` should move larger or smaller, close to the boundary-action bridge. |
| `cp_bridge_003` | `dbox_inspired_guard` | pass | acceptable to minor | It asks dimensions and index attributes, but does not fully define the state. |
| `cp_bridge_005` | `dbox_inspired_guard` | level 3 / rewrite | major | It explicitly states delayed child update semantics and pushdown trigger conditions. |
| `cp_bridge_010` | `dbox_inspired_guard` | pass | minor | It asks whether the dependency value has already been updated by the current item; close to the overwrite-order bridge. |

## Conclusion

1. The patch reduced some template-like definition-first risks, but prompt-only control is still not stable.
2. `dbox_inspired + guard` is not automatically safer. It can turn the current step into answer-slot questions.
3. `bridge_contract + guard + repair` is better on `cp_bridge_003`, but `cp_bridge_001` and `cp_bridge_010` still need stronger guard/routing policy.
4. `bridge_contract_safe_scaffold` is safe but too low-quality for normal tutoring; it should remain a high-risk fallback.

## Next Implication

Do not keep adding prompt rules indefinitely. Before 50-case held-out evaluation:

1. add `cp_bridge_001/002/005/010` to the prompt-freeze regression set;
2. strengthen Leakage Judge detection for answer-slot questions that ask the student to fill forbidden positions, directions, or follow-up actions;
3. document that high-risk contribution / predicate / representation bridges cannot rely on generator prompt alone.

## Follow-up Targeted Rerun (Same Day)

After adding the Bridge Judge alias `concept_comprehension_gap -> modeling_representation_gap`, we reran `bridge_contract + guard + repair` on `cp_bridge_001` and `cp_bridge_005`:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/bridge_contract_guard_repair_after_alias_and_answer_slot.jsonl
```

Results:

| case | stage errors | automated guard | self-review |
| --- | --- | --- | --- |
| `cp_bridge_001` | none | level 3 / rewrite | Repair still asked answer-bearing mark-location/action slots. |
| `cp_bridge_005` | none | level 3 / rewrite | Repair removed some definition text but copied filled `sum/lazy` table values. |

We then strengthened the Repair prompt against answer-slot rewrites and filled critical tables, and reran `cp_bridge_005`:

```text
evals/aichat/ad_hoc_runs/definition_first_regression_20260512_rerun/cp_bridge_005_after_internal_field_guard_patch.jsonl
```

That run had no stage errors, but the Guard still passed a candidate that directly specified root `sum=20`, `lazy=5`, and child `sum=0` field effects. This is a Guard false-negative risk for internal data-structure field updates.

Therefore, this case should become a Guard calibration regression case rather than another generator-prompt-only patch.
