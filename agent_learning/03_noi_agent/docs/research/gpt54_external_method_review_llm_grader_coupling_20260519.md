# GPT-5.4 External Method Review: LLM Grader Coupling 20260519

## Scope

This memo records a GPT-5.4 subagent method review of the dialogue-state v3 LLM-grader wording. It is a reviewer-facing process audit, not an experimental result, grader calibration run, or model comparison.

## Verdict

```text
needs minor revision
```

The review found that the current evidence package correctly treats DeepSeek-backed LLM grader calibration as auxiliary / limitation evidence rather than a main result. The main results remain based on Coach A / Coach B human review and priority adjudication.

## Main Risk

The reviewer identified one wording risk: same-backend coupling should be stated explicitly. Tutor generation, Bridge Judge / Leakage Guard, and Repair are all implemented within a fixed DeepSeek-family offline stack. Therefore, DeepSeek-backed grader calibration should not be interpreted as cross-backend validation or as an independent replacement for human review.

## Implemented Wording Fixes

- Added a backend-coupling boundary to the DeepSeek LLM grader calibration report.
- Changed `scalable triage` wording to auxiliary low-stakes / auxiliary signal wording.
- Added explicit future-work wording for cross-backend grader calibration, including GPT-5.4-backed grading.
- Clarified that a GPT-5.4 external audit may be cited only as method review / reproducibility audit, not as an experimental result.

## Safe Wording

```text
We report DeepSeek-backed LLM grader calibration as auxiliary evidence only. Because tutor generation, judge/guard, and repair are all implemented within a fixed DeepSeek-family offline stack, this calibration is backend-coupled and should not be interpreted as cross-backend validation. The paper's main findings rely on double human review and priority adjudication rather than automatic grading. Cross-backend grader calibration, including GPT-5.4-backed grading, is left for future work or a revision add-on.
```

## Forbidden Interpretation

Do not write:

- GPT-5.4 subagent review is an experimental LLM-grader calibration.
- GPT-5.4 replaced the DeepSeek calibration.
- DeepSeek calibration is cross-backend validation.
- Any LLM grader replaces Coach A / Coach B human review.
