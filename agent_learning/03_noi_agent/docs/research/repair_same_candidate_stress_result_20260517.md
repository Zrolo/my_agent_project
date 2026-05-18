# Repair Same-Candidate Stress Result 20260517

## Scope

This report summarizes the completed `repair_same_candidate_stress_blind_review_workbook_20260517_filled.xlsx`. The review fixed the same original candidate and repaired output, randomized them as Response A / Response B, and used a separate key to recover before/after labels.

This is **same-candidate stress evidence**. It supports a causal estimate of Repair under fixed candidates, but it does not replace the condition-level main experiment and does not show that Repair fully solves leakage.

## Overall Results

| metric | value |
| --- | ---: |
| labeled pairs | 30 / 30 |
| before overall mean | 3.367 |
| after overall mean | 3.633 |
| mean overall delta | +0.267 |
| quality win / tie / loss | 12 / 11 / 7 |
| repair preferred / original preferred / tie | 15 / 11 / 4 |
| leakage improved / same / worse | 16 / 14 / 0 |
| burden improved / same / worse | 2 / 16 / 12 |
| still-leaks rate | 0.000 |
| too-vague-after-repair rate | 0.067 |

## Leakage Distribution

| label | before | after |
| --- | ---: | ---: |
| no_leakage | 10 | 22 |
| minor_bridge_leakage | 13 | 8 |
| major_bridge_leakage | 7 | 0 |
| answer_leakage | 0 | 0 |

Repair reduced major leakage from 7 to 0 and did not worsen leakage in any pair. Leakage severity improved in 16/30 pairs, stayed the same in 14/30 pairs, and worsened in 0/30 pairs.

## Quality And Burden Trade-Off

| dimension | before | after |
| --- | ---: | ---: |
| would_show yes | 12 | 18 |
| would_show borderline | 11 | 11 |
| would_show no | 7 | 1 |
| burden low | 18 | 8 |
| burden medium | 11 | 19 |
| burden high | 1 | 3 |

Repair increased mean overall by +0.267, with pair-level quality W/T/L of 12/11/7. However, student burden worsened in 12/30 pairs and improved in only 2/30. Repair often reduces leakage by making the response more conservative, open-ended, or requiring more student judgment.

## Source Condition Split

| source condition | n | mean overall delta | quality W/T/L | leakage improved/same/worse | burden improved/same/worse | repair preferred/original/tie |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `bridge_contract_compact_guard_repair` | 13 | -0.077 | 3/6/4 | 5/8/0 | 1/9/3 | 4/6/3 |
| `dbox_inspired_guard_repair` | 17 | +0.529 | 9/5/3 | 11/6/0 | 1/7/9 | 11/5/1 |

Repair benefits are clearer on DBox-inspired repair candidates, likely because those before candidates more often had direct bridge leakage or over-complete hints. Bridge Contract repair candidates were already closer to the safety boundary, so quality effects are more mixed.

## Bridge Family Coverage

| bridge bucket | leakage improved | leakage same | quality win | quality tie | quality loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| `state_representation_semantics` | 3 | 1 | 3 | 1 | 0 |
| `transition_recurrence_source` | 1 | 2 | 1 | 1 | 1 |
| `predicate_check_semantics` | 3 | 1 | 1 | 2 | 1 |
| `boundary_update_order` | 0 | 2 | 0 | 1 | 1 |
| `modeling_object_relation` | 2 | 1 | 1 | 1 | 1 |
| `aggregation_contribution_summary` | 3 | 2 | 2 | 2 | 1 |
| `data_structure_operation_semantics` | 3 | 2 | 3 | 1 | 1 |
| `correctness_invariant` | 0 | 2 | 1 | 1 | 0 |
| `implementation_boundary` | 1 | 0 | 0 | 1 | 0 |
| `policy_request` | 0 | 1 | 0 | 0 | 1 |

This is natural repair-set coverage, not full taxonomy-stratified coverage. Do not present it as sufficient coverage for all bridge families.

## Paper-Ready Interpretation

Can write:

```text
In a 30-pair same-candidate stress test, Repair reduced or preserved leakage severity in all pairs, improved leakage in 16/30 pairs, and reduced major leakage from 7/30 to 0/30. Overall quality increased modestly on average (+0.27), but student burden worsened in 12/30 pairs, indicating a quality-safety-burden trade-off.
```

Do not write:

- Repair fully solves all leakage.
- Repair's causal effect is proven by the main experiment.
- Repair always improves quality.
- Repair has no student-burden cost.

## Impact On The Main Paper

This result fills the same-candidate evidence gap. The main experiment shows that the repair-enabled condition performs well; this stress test shows directional evidence that Repair reduces leakage under fixed-candidate before/after comparison. It should be reported as stress-test evidence, not as a reinterpretation of main-experiment means as the sole causal proof.
