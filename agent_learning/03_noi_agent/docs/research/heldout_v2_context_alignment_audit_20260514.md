# Held-out v2 Context Alignment Audit (2026-05-14)

## Conclusion

The previous `bridgebench_cp_heldout_v2_50_draft.jsonl` and derived review workbook should not be used as strict context-aware blind-review evidence. They can only be treated as development-stage rough review over the current student message and target AI response.

## Audit Results

- v2 dataset: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- v2 cases: `50`
- v2 context alignment: `{'no_recent_dialogue': 10, 'recent_dialogue_last_student_mismatch': 40}`
- human review workbook: `/Users/kongyouli/Downloads/coach_response_review_workbook_dev_ablation_zh5_filled.xlsx`
- review rows: `537`
- review workbook context alignment: `{'no_recent_dialogue': 136, 'unparseable_recent_dialogue': 1, 'recent_dialogue_last_student_mismatch': 400}`
- rows with student-visible `[LEVEL:Lx]` tags: `48`

## Root Cause

The old generator appended an extra synthetic current student turn to `recent_dialogue`, while `student_message` was generated independently. As a result, model responses usually answered `student_message`, but reviewers reading the final student turn inside `recent_dialogue` could perceive a context mismatch.

## Fix

1. `recent_dialogue` now represents prior context only; non-N/A contexts end with an AI prompt/question rather than another student current question.
2. The held-out validator now rejects `recent_dialogue_last_student_mismatch`.
3. The offline runner strips internal `[LEVEL:L0-L4]` tags from student-visible responses.
4. A clean v3 dataset has been generated: `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/research/bridgebench_cp_heldout_v3_50_draft.jsonl` with `ok=true`; alignment counts: `{'no_recent_dialogue': 10, 'aligned_prior_context_ends_with_assistant': 40}`.

## Recommendation

- Treat the old zh5 human-review result as development diagnostic only, not as a paper headline result.
- Rerun 50-case generation-only and blind review on the clean v3 dataset.
- If old scores are referenced at all, label them as `current-message-only rough review`, not full context-aware blind review.
