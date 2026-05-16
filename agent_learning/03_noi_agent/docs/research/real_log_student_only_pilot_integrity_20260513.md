# Ablation Run Integrity Report

- Manifest: `evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513/manifest.json`
- Expected rows: 48
- Combined rows: 48
- Final response rows: 46
- Review rows: 46
- Analysis ready: False
- Headline ready: False

## Blocking Reasons

[
  "empty_final_response_rows"
]

## Warnings

[
  "stage_errors_present"
]

## Empty Final Response Rows

[
  {
    "case_id": "real_aichat_247",
    "condition_id": "dbox_inspired_guard"
  },
  {
    "case_id": "real_aichat_257",
    "condition_id": "edf_inspired_clean"
  }
]

## Targeted Rerun Pairs

[
  {
    "case_id": "real_aichat_247",
    "condition_id": "dbox_inspired_guard"
  },
  {
    "case_id": "real_aichat_257",
    "condition_id": "edf_inspired_clean"
  }
]

## Targeted Rerun Commands

```bash
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl /Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_ai_prelim_exportable_20260513.jsonl --output-dir evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_targeted_rerun/dbox_inspired_guard --condition-set edf_core --condition-id dbox_inspired_guard --case-id real_aichat_247
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl /Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_ai_prelim_exportable_20260513.jsonl --output-dir evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_targeted_rerun/edf_inspired_clean --condition-set edf_core --condition-id edf_inspired_clean --case-id real_aichat_257
```

## Stage Warning Rows

[
  {
    "case_id": "real_aichat_1293",
    "condition_id": "dbox_inspired_guard",
    "stage_errors": {
      "leakage_judge": "APITimeoutError: Request timed out."
    }
  },
  {
    "case_id": "real_aichat_247",
    "condition_id": "edf_inspired_guard",
    "stage_errors": {
      "leakage_judge": "APITimeoutError: Request timed out."
    }
  },
  {
    "case_id": "real_aichat_249",
    "condition_id": "bridge_contract_guard_repair",
    "stage_errors": {
      "leakage_judge": "APITimeoutError: Request timed out."
    }
  }
]
