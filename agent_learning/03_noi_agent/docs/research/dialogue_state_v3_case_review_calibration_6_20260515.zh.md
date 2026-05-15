# Dialogue-State v3 Case Review Calibration Workbook（6 条校准）

本表用于让教练先试填 case/source 审核字段。它不是正式 50-case 审核结果，也不评价 AI 回复。

- row_count: 6
- source_jsonl: `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- reference_label_status: `calibration_case_source_review_only`
- context_type_counts: `{'initial_question': 1, 'followup_after_partial_answer': 2, 'followup_after_wrong_answer': 1, 'followup_after_prerequisite_gap': 1, 'policy_direct_answer_special': 1}`
- followability_counts: `{'NA': 1, 'F2': 2, 'F3': 2, 'F4': 1}`

## Case IDs

- `dialogue_v3_001_state_representation_semantics`
- `dialogue_v3_011_transition_recurrence_source`
- `dialogue_v3_018_boundary_update_order`
- `dialogue_v3_026_modeling_object_relation`
- `dialogue_v3_043_implementation_boundary`
- `dialogue_v3_048_policy_request`
