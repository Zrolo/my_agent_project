# Dialogue-State v3 50-Case Refresh 20260515

中文版本：`dialogue_state_v3_50_refresh_20260515.zh.md`

## Conclusion

After this refresh, `bridgebench_cp_dialogue_state_v3_50_draft.jsonl` is the preferred candidate for the next follow-up scaffolding experiment. It is still `draft_needs_coach_review`; it is not gold data and should not be used as a headline paper result yet.

Compared with the previous v4 generation-only draft, this version is not only a fix for short questions without context. It explicitly separates initial help-seeking turns from follow-up tutoring turns:

- initial questions: 10 cases;
- follow-up turns: 40 cases;
- F1 follows well: 7 cases;
- F2 partially follows: 18 cases;
- F3 struggles to follow: 10 cases;
- F4 prerequisite gap: 5 cases.

## What Changed

The earlier `dialogue_state_v3` draft had F1-F4 labels and follow-up types, but its current student replies were too short in practice, and some `recent_dialogue_bucket` labels were not matched by the actual dialogue content. This refresh fixes two issues:

1. Current student replies now satisfy the target text-length distribution: `short=20`, `medium_short=15`, `medium_long=10`, `long=5`.
2. Cases marked as long context now contain multi-turn recent dialogue in the actual text, not just in metadata.

## Validation

Generated files:

- dataset: `bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- Chinese coach review workbook: `dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- English coach review workbook: `dialogue_state_v3_50_source_and_case_review.en.xlsx`
- dialogue-state validation: `dialogue_state_v3_validation_report_20260515.json`
- held-out-style validation: `dialogue_state_v3_heldout_style_validation_report_20260515.json`
- context audit: `dialogue_state_v3_50_context_readiness_audit_20260515.md`

Passed gates:

- `row_count=50`
- `problem_source_platform_counts={"luogu": 50}`
- bridge-bucket quotas match the planned distribution
- current student-message length distribution is `20/15/10/5`
- recent-dialogue distribution is `none=10`, `short=25`, `long=15`
- 17 cases include student code snippets, satisfying the minimum of 10 code/error-code cases
- `turn_position_counts={"initial": 10, "followup": 40}`
- `reference_label_status=draft_needs_coach_review`

## Relationship To Heldout v4

`bridgebench_cp_heldout_v4_50_draft.jsonl` remains as a historical draft. It is useful for documenting the short-question context fix, but only 10 cases have explicit follow-up metadata. If the next experiment is meant to test whether AIChat can continue from a student's response to a prior scaffold, use `dialogue_state_v3` instead.

## Next Steps

1. Have a coach or researcher review `dialogue_state_v3_50_source_and_case_review.zh.xlsx`; use `dialogue_state_v3_50_source_and_case_review.en.xlsx` for external English review. Focus on problem statement, current student reply, recent dialogue, F1-F4 label, missing bridge, and forbidden content consistency.
2. After review, export the formal generation-only input.
3. Run the fixed condition matrix without mixing old v4 workbooks.
4. After model generation, export the response review workbook with problem statement, recent dialogue, context AI reply, current student reply, target AI response, and case-specific rubric.
5. Treat all current results as development and data-preparation evidence, not formal paper conclusions.
