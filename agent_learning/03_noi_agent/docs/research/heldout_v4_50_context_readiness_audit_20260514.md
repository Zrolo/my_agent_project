# Held-out v4 50 Context Readiness Audit 20260514

中文版本：`heldout_v4_50_context_readiness_audit_20260514.zh.md`

This is a deterministic data audit. It does not call an LLM and does not modify prompts. Its purpose is to check whether each case provides enough context to fairly evaluate whether a tutor answers the student's current question.

## Summary

- Rows: 50
- Context sufficiency: `partial`=5, `sufficient`=45
- Question specificity: `medium`=4, `policy_request`=2, `pronoun_dependent`=27, `specific`=17
- Expected tutor move: `continue_prior_scaffold`=27, `micro_scaffold`=21, `safe_refusal`=2
- Should infer bridge: `low_confidence_only`=3, `no`=2, `yes`=45
- Recommended use: `main_eval_with_caution`=3, `main_scaffold_eval`=45, `policy_safety_slice`=2

## Interpretation

- `insufficient` cases should not be used as primary evidence for tutoring quality; they mainly test clarification and hallucination control.
- `partial` cases can be used in development, but formal analysis should mark them or run sensitivity analysis.
- `sufficient` cases are better suited for the main scaffolding comparison.
- For short questions without dialogue, such as asking how to list branches, a good response should clarify or give a minimal observation task instead of expanding the hidden bridge directly.
