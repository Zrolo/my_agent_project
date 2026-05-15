# Luogu-grounded Held-out v2 50 Generation Report

This report records the generation of `bridgebench_cp_heldout_v2_50_draft.jsonl`. The dataset is a draft pending coach review; student messages are synthetic-but-grounded and do not use prior online AI replies.

- source_path: `data/local_problem_banks/luogu_latest_20260402.ndjson`
- output_jsonl: `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- review_xlsx: `docs/research/heldout_v2_50_source_and_case_review.zh.xlsx`
- row_count: `50`
- ok: `True`

## Distributions

- bridge_bucket_counts: `{'state_representation_semantics': 6, 'transition_recurrence_source': 5, 'predicate_check_semantics': 5, 'boundary_update_order': 5, 'modeling_object_relation': 5, 'aggregation_contribution_summary': 4, 'data_structure_operation_semantics': 5, 'correctness_invariant': 5, 'implementation_boundary': 4, 'debugging_evidence': 3, 'policy_request': 3}`
- student_message_length_distribution: `{'short': 20, 'medium_short': 15, 'medium_long': 10, 'long': 5}`
- recent_dialogue_distribution: `{'none': 10, 'short': 25, 'long': 15}`
- student_code_excerpt_distribution: `{'none': 40, 'present': 10}`

## Boundaries

- The raw Luogu snapshot is not committed to GitHub; the local path is recorded in the snapshot document.
- The JSONL contains necessary statement excerpts for local coach review; public materials should prefer problem IDs, links, and rewritten summaries.
- Luogu tags are kept as metadata / workbook columns and are not embedded in `problem_statement`, so response-generation prompts can avoid leaking algorithm labels as statement text.
- `heldout_v2_50_source_and_case_review.zh.xlsx` is a source/case review workbook, not an AI response blind-review workbook; it intentionally has no target AI response.
- Student messages are synthetic-but-grounded and use varied templates inspired by real online short student questions; coaches still need to confirm naturalness and statement fit.
- This version is not gold; every row remains `draft_needs_coach_review`.
