# Held-out 50 Readiness Report

This report summarizes the current status of the 50-case held-out package before the formal main experiment. It is not an experiment result; it is a launch gate.

## Summary

- ready_for_main_experiment: `False`
- blocking_reasons: `coach_a_incomplete`, `coach_b_overlap_incomplete`, `frozen_jsonl_missing`

## Status Table

| Item | Status | Notes |
|---|---|---|
| draft validation | pass | `docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl` |
| Coach A labeled | blocked | 0 / 50 |
| Coach B overlap labeled | blocked | 0 / 20 |
| frozen JSONL exists | blocked | `docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl` |
| frozen formal preflight | blocked | require frozen reference status |

## Next Steps

- Complete Coach A full labeling.
- Complete Coach B overlap labeling.
- Compute agreement and adjudicate disagreements.
- Export the frozen reference JSONL.
- Rerun formal preflight until there are no blockers.
