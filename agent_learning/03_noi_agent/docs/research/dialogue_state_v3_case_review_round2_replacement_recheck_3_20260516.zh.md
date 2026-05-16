# Dialogue-State v3 Targeted Re-check Workbook（定向复核）

本表用于定向复核前一轮 case/source 审核后仍需处理的样本；它不是正式 50-case 审核结果，也不评价 AI 回复。

- row_count: 3
- source_jsonl: `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- reference_label_status: `targeted_case_source_recheck_only`
- selection_mode: `explicit_case_prefixes`
- case_id_prefix_ok: `True`
- context_coverage_ok: `False`
- context_type_counts: `{'followup_after_code_attempt': 3}`
- followability_counts: `{'F2': 3}`

## Case IDs

- `dialogue_v3_035_data_structure_operation_semantics`
- `dialogue_v3_036_correctness_invariant`
- `dialogue_v3_037_correctness_invariant`
