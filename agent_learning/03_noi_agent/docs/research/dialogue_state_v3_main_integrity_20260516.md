# Ablation Run Integrity Report

- Manifest: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516/manifest.json`
- Expected rows: 350
- Combined rows: 350
- Final response rows: 339
- Review rows: 339
- Analysis ready: False
- Headline ready: False

## Blocking Reasons

[
  "empty_final_response_rows"
]

## Warnings

[]

## Empty Final Response Rows

[
  {
    "case_id": "dialogue_v3_012_predicate_check_semantics",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_013_predicate_check_semantics",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_017_boundary_update_order",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_020_boundary_update_order",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_029_aggregation_contribution_summary",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_011_transition_recurrence_source",
    "condition_id": "bridge_guided_dbox_style_guard"
  },
  {
    "case_id": "dialogue_v3_018_boundary_update_order",
    "condition_id": "bridge_guided_dbox_style_guard"
  },
  {
    "case_id": "dialogue_v3_043_implementation_boundary",
    "condition_id": "bridge_guided_dbox_style_guard"
  },
  {
    "case_id": "dialogue_v3_025_modeling_object_relation",
    "condition_id": "bridge_contract_compact_guard"
  },
  {
    "case_id": "dialogue_v3_032_data_structure_operation_semantics",
    "condition_id": "bridge_contract_compact_guard"
  },
  {
    "case_id": "dialogue_v3_014_predicate_check_semantics",
    "condition_id": "bridge_contract_compact_guard_repair"
  }
]

## Targeted Rerun Pairs

[
  {
    "case_id": "dialogue_v3_012_predicate_check_semantics",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_013_predicate_check_semantics",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_017_boundary_update_order",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_020_boundary_update_order",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_029_aggregation_contribution_summary",
    "condition_id": "codehelp_codeaid_clean"
  },
  {
    "case_id": "dialogue_v3_011_transition_recurrence_source",
    "condition_id": "bridge_guided_dbox_style_guard"
  },
  {
    "case_id": "dialogue_v3_018_boundary_update_order",
    "condition_id": "bridge_guided_dbox_style_guard"
  },
  {
    "case_id": "dialogue_v3_043_implementation_boundary",
    "condition_id": "bridge_guided_dbox_style_guard"
  },
  {
    "case_id": "dialogue_v3_025_modeling_object_relation",
    "condition_id": "bridge_contract_compact_guard"
  },
  {
    "case_id": "dialogue_v3_032_data_structure_operation_semantics",
    "condition_id": "bridge_contract_compact_guard"
  },
  {
    "case_id": "dialogue_v3_014_predicate_check_semantics",
    "condition_id": "bridge_contract_compact_guard_repair"
  }
]

## Targeted Rerun Commands

```bash
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl --output-dir evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_targeted_rerun/bridge_contract_compact_guard --condition-set dialogue_state_v3_main --condition-id bridge_contract_compact_guard --case-id dialogue_v3_025_modeling_object_relation --case-id dialogue_v3_032_data_structure_operation_semantics
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl --output-dir evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_targeted_rerun/bridge_contract_compact_guard_repair --condition-set dialogue_state_v3_main --condition-id bridge_contract_compact_guard_repair --case-id dialogue_v3_014_predicate_check_semantics
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl --output-dir evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_targeted_rerun/bridge_guided_dbox_style_guard --condition-set dialogue_state_v3_main --condition-id bridge_guided_dbox_style_guard --case-id dialogue_v3_011_transition_recurrence_source --case-id dialogue_v3_018_boundary_update_order --case-id dialogue_v3_043_implementation_boundary
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl --output-dir evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_targeted_rerun/codehelp_codeaid_clean --condition-set dialogue_state_v3_main --condition-id codehelp_codeaid_clean --case-id dialogue_v3_012_predicate_check_semantics --case-id dialogue_v3_013_predicate_check_semantics --case-id dialogue_v3_017_boundary_update_order --case-id dialogue_v3_020_boundary_update_order --case-id dialogue_v3_029_aggregation_contribution_summary
```

## Stage Warning Rows

[]
