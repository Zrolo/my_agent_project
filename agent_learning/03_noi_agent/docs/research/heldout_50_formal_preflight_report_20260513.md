# 50-case Held-out Formal Preflight Report

Date: 2026-05-13

This report records the preflight result for `bridgebench_cp_heldout_v1_50_draft.jsonl` before the formal 50-case held-out main experiment. It is not an experiment result and not a coach-labeling result. It only determines whether the current dataset is eligible for the formal headline run.

## Conclusion

Current decision: **No-go for formal held-out run; go for coach review / freeze preparation**.

The reason is straightforward:

- The structural checks pass: 50 rows, required fields, category distribution, recent-dialogue distribution, code-excerpt count, and dev-seed overlap are acceptable for the current draft gate.
- The formal frozen-status gate fails: all 50 cases still have `reference_label_status=draft_needs_coach_review`.
- Therefore, the current file is a coach-review draft. It must not be used directly as `bridgebench_cp_heldout_v1_50_frozen.jsonl` for the formal main experiment.

## Command

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_formal_preflight_report.json \
  --require-frozen-status
```

## Structural Summary

| Item | Result |
|---|---:|
| row count | 50 |
| expected count | 50 |
| dev seed overlap | 0 blocking errors |
| no recent dialogue | 10 |
| short recent dialogue | 25 |
| long recent dialogue | 15 |
| code excerpts present | 12 |
| code excerpts none | 38 |

Category distribution:

| category | count |
|---|---:|
| binary_search_boundary | 4 |
| binary_search_predicate | 5 |
| data_structure_semantics | 5 |
| debugging_evidence | 4 |
| dp_state | 5 |
| dp_transition | 5 |
| graph_tree_modeling | 5 |
| greedy_correctness | 5 |
| implementation_boundary | 5 |
| policy_request | 7 |

These results show that the 50-case draft is ready for coach review. It is not structurally broken.

## Formal Gate Failure

With `--require-frozen-status`, the validator requires each case to use a frozen reference status, such as:

```text
adjudicated_reference
coach_reference
adjudicated_gold
single_coach_reference
coach_gold
```

All 50 current rows still use:

```text
draft_needs_coach_review
```

The report therefore contains 50 `frozen_status_required` errors. This is an expected failure. It does not mean the dataset content is invalid; it means the cases have not yet completed coach review, overlap labeling, adjudication, and freeze export.

## Next Steps

Before the formal 50-case main experiment:

1. Coach A reviews / labels all 50 cases.
2. Coach B independently labels at least 20 overlap cases.
3. Low-confidence, multi-bridge, and major-leakage boundary cases are adjudicated.
4. Export `bridgebench_cp_heldout_v1_50_frozen.jsonl`.
5. Rerun formal preflight and require `ok=true`.
6. Only after frozen preflight passes, run the 400-row `--condition-set heldout_main` main experiment.

Use the exporter rather than manually editing JSONL:

```bash
python3 -m evals.aichat.export_heldout_frozen_reference \
  --draft-jsonl docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --coach-a-workbook docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx \
  --output-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --reference-status adjudicated_reference
```

Running this exporter on the currently unfilled workbook returns `missing_labeled_reference`, which is also an expected failure.

## Paper Boundary

The current draft may be used for:

- coach review preparation;
- dataset card / annotation instructions;
- dry runs or tooling checks.

The current draft must not be used for:

- formal held-out headline results;
- uncontaminated test claims after prompt / judge / rubric tuning;
- claims that it is the frozen 50-case test set.

In one sentence: **the 50-case content scaffold is ready, but it is not yet frozen held-out gold/reference.**
