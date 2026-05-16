# Ablation Run Integrity Report

- Manifest: `evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513/manifest.json`
- Expected rows: 400
- Combined rows: 400
- Final response rows: 399
- Review rows: 400
- Analysis ready: False
- Headline ready: False

## Blocking Reasons

[
  "empty_final_response_rows",
  "review_row_count_mismatch"
]

## Warnings

[]

## Empty Final Response Rows

[
  {
    "case_id": "heldout_cp_015",
    "condition_id": "bridge_contract_guard"
  }
]

## Targeted Rerun Pairs

[
  {
    "case_id": "heldout_cp_015",
    "condition_id": "bridge_contract_guard"
  }
]

## Targeted Rerun Commands

```bash
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_ai_reference_draft_20260513.jsonl --output-dir evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_targeted_rerun/bridge_contract_guard --condition-set heldout_main --condition-id bridge_contract_guard --case-id heldout_cp_015
```

## Stage Warning Rows

[]
