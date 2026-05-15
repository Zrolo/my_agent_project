# Luogu-grounded Held-out v2 50 Generation Report

本报告记录 `bridgebench_cp_heldout_v2_50_draft.jsonl` 的生成结果。该数据集是 draft，等待教练复核；学生问题为 synthetic-but-grounded，不来自旧线上 AI 回复。

- source_path: `data/local_problem_banks/luogu_latest_20260402.ndjson`
- output_jsonl: `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- review_xlsx: `docs/research/heldout_v2_50_source_and_case_review.zh.xlsx`
- row_count: `50`
- ok: `True`

## 分布

- bridge_bucket_counts: `{'state_representation_semantics': 6, 'transition_recurrence_source': 5, 'predicate_check_semantics': 5, 'boundary_update_order': 5, 'modeling_object_relation': 5, 'aggregation_contribution_summary': 4, 'data_structure_operation_semantics': 5, 'correctness_invariant': 5, 'implementation_boundary': 4, 'debugging_evidence': 3, 'policy_request': 3}`
- student_message_length_distribution: `{'short': 20, 'medium_short': 15, 'medium_long': 10, 'long': 5}`
- recent_dialogue_distribution: `{'none': 10, 'short': 25, 'long': 15}`
- student_code_excerpt_distribution: `{'none': 40, 'present': 10}`

## 使用边界

- 原始洛谷快照不进入 GitHub；本地路径由 snapshot 文档记录。
- JSONL 中包含必要题面摘录，仅供本地教练复核；公开材料优先使用题号、链接和改写摘要。
- 洛谷标签保留为 metadata / workbook 独立列，不写入 `problem_statement`，避免后续生成回复时误把算法标签当作题面泄露给 tutor。
- `heldout_v2_50_source_and_case_review.zh.xlsx` 是题源/case 复核表，不是 AI 回复盲评表；它故意不包含待评分 AI 回复。
- 学生问题为 synthetic-but-grounded，并使用真实线上学生短问风格的多变体模板；后续仍需教练确认是否自然、是否匹配题面。
- 本版本不称为 gold，只能作为 `draft_needs_coach_review`。
