# Judge Schema Smoke Report 2026-05-09

本报告记录 20 条 `diagnosis_only` 离线 smoke。目标是比较三种 Bridge Judge schema 负担：

- `full_schema_judge`
- `compact_contract_judge`
- `retrieval_augmented_compact_judge`

本次实验只调用 Bridge Judge，不调用 tutor、Leakage Judge 或 Repair，因此结果只用于观察诊断稳定性、focus 选择和延迟，不代表最终学生可见回复质量。

## Commands

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/compact_contract_smoke_20260509/full_schema_diagnosis_20.jsonl \
  --limit 20 \
  --pipeline-mode diagnosis_only \
  --judge-schema-mode full_schema_judge \
  --judge-provider deepseek \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json

python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/compact_contract_smoke_20260509/compact_contract_diagnosis_20.jsonl \
  --limit 20 \
  --pipeline-mode diagnosis_only \
  --judge-schema-mode compact_contract_judge \
  --judge-provider deepseek \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json

python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/compact_contract_smoke_20260509/retrieval_compact_diagnosis_20_v2.jsonl \
  --limit 20 \
  --pipeline-mode diagnosis_only \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --judge-provider deepseek \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json
```

## Results

| Mode | Completed | Errors | Student State Acc | Bridge Family Acc | Known Focus Acc | Registered Focus Acc | Unknown Focus Recall | Invalid Contract | Focus OOB | p50 Latency ms | p95 Latency ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `full_schema_judge` | 19/20 | 1 | 0.632 | 0.842 | 0.474 | 0.600 | 0.250 | n/a | n/a | 4365.483 | 8427.964 |
| `compact_contract_judge` | 20/20 | 0 | 0.600 | 0.800 | 0.600 | 0.750 | 0.000 | 0.000 | n/a | 4365.124 | 8055.573 |
| `retrieval_augmented_compact_judge` v1 | 20/20 | 0 | 0.650 | 0.750 | 0.550 | 0.562 | 0.500 | 0.000 | 0.000 | 4456.885 | 10862.205 |
| `retrieval_augmented_compact_judge` v2 | 20/20 | 0 | 0.700 | 0.800 | 0.700 | 0.750 | 0.500 | 0.000 | 0.000 | 4052.669 | 4442.795 |

## V2 Coach Gold Rerun

After the coach-filled workbook was exported to
`docs/research/coach_seed_labeling_v2_gold_20.jsonl`, the first 20 seed rows
were rebuilt as `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`. This
refreshes the gold labels from the old v1 taxonomy to the coach-facing v2
taxonomy.

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/v2_gold_20_20260509/retrieval_compact_diagnosis_20_v2gold_v2prompt_retriever.jsonl \
  --limit 20 \
  --pipeline-mode diagnosis_only \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --judge-provider deepseek \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json
```

| Gold Source | Mode | Completed | Errors | Student State Acc | Bridge Family Acc | Known Focus Acc | Registered Focus Acc | Help Type Acc | Help Level Acc | Invalid Contract | Focus OOB | p50 Latency ms | p95 Latency ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| coach v2 gold 20 | `retrieval_augmented_compact_judge` | 20/20 | 0 | 0.550 | 0.900 | 0.850 | 0.850 | 0.550 | 0.950 | 0.000 | 0.000 | 3923.054 | 4968.610 |

The v2 rerun confirms that the earlier low bridge-family score was mostly a
taxonomy-version mismatch: the old Bridge Judge prompt still used v1 labels
such as `strategy_application_gap` and `aggregation_bridge`, while the workbook
now uses v2 labels such as `method_application_gap` and
`aggregation_contribution_bridge`. After updating the prompt/validator to accept
v2 labels and improving the top-k retriever for new focuses
(`union_find_operation_mapping`, `heap_push_pop_mapping`,
`topological_zero_indegree_reason`), the diagnosis layer reaches high
bridge-family and registered-focus agreement on this 20-case smoke.

## Main Findings

1. `full_schema_judge` had one provider timeout on `cp_bridge_001`; compact and retrieval compact completed all 20 cases.
2. Compact runtime contracts stayed structurally valid: `invalid_label_rate=0.0`.
3. Retrieval-augmented compact v2 had `focus_out_of_registry_rate=0.0`, meaning the Judge did not choose focus IDs outside the top-k candidate set.
4. Initial retrieval v1 missed several common OI phrases. After adding direct hints for method selection, greedy proof, enumeration order, and complexity fit, retrieval compact improved:
   - known focus accuracy: 0.55 -> 0.70
   - student state accuracy: 0.65 -> 0.70
   - p95 latency: 10862.205 ms -> 4442.795 ms
5. The v2 coach-gold rerun removes most taxonomy-version noise and should be
   used as the reference for the next offline diagnosis experiments.

## Remaining Mismatch Themes

- `lazy_semantics`: Judge labels the bridge as aggregation, while old gold labels it as representation. This is a real taxonomy boundary issue.
- `left_bound_update`: retrieval includes the right focus but the Judge sometimes chooses broader `check_condition`.
- `recursion_structure`: candidate retrieval contains the right focus, but Judge chooses `state_design`; prompt or registry descriptions may need sharper boundaries.
- `unknown` gold focus: old seed rows mark several cases unknown even though the expanded registry now has matching focus IDs.

## Interpretation

For the current research direction, `retrieval_augmented_compact_judge` is the best next candidate. It is not yet clearly more accurate than compact on all metrics, but it provides stronger runtime guarantees:

- no focus hallucination outside top-k;
- compact contract stays valid;
- stable latency in this smoke;
- better fit with the proposed risk-triggered routing design.

Before treating the numbers as paper evidence, the remaining 30 seed rows should
be labeled or adjudicated under the v2 human annotation schema. The current
coach-v2 result is a 20-case smoke, not a final benchmark.

## Next Step

Use `retrieval_augmented_compact_judge` as the default diagnosis mode for the
next offline experiment. Then expand/adjudicate the remaining seed rows and rerun:

```text
retrieval_augmented_compact_judge + diagnosis_only
current_system vs bridge_contract + tutor_only
bridge_contract + tutor_plus_guard
bridge_contract + tutor_plus_guard_plus_repair
```
