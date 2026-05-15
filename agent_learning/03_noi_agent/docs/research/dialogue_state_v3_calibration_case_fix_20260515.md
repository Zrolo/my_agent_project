# Dialogue-State v3 Calibration Case Fix Log (2026-05-15)

This note records the dataset-generation fixes made after the 6-case calibration review. It is part of the case/source review stage and is not a formal experiment result.

## Calibration Findings

Among the six calibration cases, `dialogue_v3_001` and `dialogue_v3_048` were acceptable; `dialogue_v3_011`, `dialogue_v3_018`, `dialogue_v3_026`, and `dialogue_v3_043` required revision. The main issue was not source usability, but inconsistent chains across `recent_dialogue -> student_message -> missing_bridge -> success_criteria`.

## Fixes Applied

- `dialogue_v3_018`: Boundary/order follow-up replies no longer use generic branching language. They now focus on old values, overwriting, and update order.
- `dialogue_v3_026`: Modeling/object-relation follow-up replies no longer use binary-search `true/false` or boundary-direction wording. They now focus on objects, relations, coverage, and dependencies.
- `dialogue_v3_043`: Implementation-boundary prerequisite-gap replies no longer use generic feasibility/state-semantics wording. They now focus on characters, input parsing, indices, initialization, and ranges.
- `dialogue_v3_011`: Transition-source follow-up replies now explicitly include source cues. This reduces the overly generic F1 reply issue, but the case should still be reviewed for whether `F1/advance` remains too optimistic.

## Generator Changes

- Follow-up student replies are now selected based on bridge bucket rather than only context type.
- Short-reply fallbacks are also bucket-aware, avoiding compressed generic phrases that mismatch the target bridge.
- Implementation-boundary cases are matched before generic boundary cases, preventing `implementation_boundary` from being treated as boundary-update/order cases.

## Verification

- Added and passed the regression test `test_followup_replies_match_bridge_bucket`.
- Dialogue-state generation, review workbook, validation, and bilingual-document tests passed: 43 tests total.
- Regenerated the dialogue-state v3 JSONL, Chinese/English 50-case review workbooks, and 6-case calibration workbooks.

## Recommended Next Step

Run a short 5-6 case calibration re-check before the full 50-case case/source review. `dialogue_v3_011` should remain a focus item to decide whether it should stay `F1/advance` or be revised to `F2/clarify`.
