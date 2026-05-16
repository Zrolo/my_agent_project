# Ablation Run Integrity Report

- Manifest: `evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_merged/manifest.json`
- Expected rows: 48
- Combined rows: 48
- Final response rows: 48
- Review rows: 48
- Analysis ready: True
- Headline ready: False

## Blocking Reasons

[]

## Warnings

[
  "stage_errors_present"
]

## Empty Final Response Rows

[]

## Targeted Rerun Pairs

[]

## Targeted Rerun Commands

```bash

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
