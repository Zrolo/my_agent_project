# Held-out dialogue_state_v3 50 Context Readiness Audit 20260514

中文版本：`heldout_dialogue_state_v3_50_context_readiness_audit_20260514.zh.md`

This is a deterministic data audit. It does not call an LLM and does not modify prompts. Its purpose is to check whether each case provides enough context to fairly evaluate whether a tutor answers the student's current question.

## Summary

- Rows: 50
- Context sufficiency: `insufficient`=10, `partial`=9, `sufficient`=31
- Question specificity: `medium`=5, `policy_request`=4, `pronoun_dependent`=11, `specific`=20, `vague`=10
- Expected tutor move: `clarify_context`=10, `continue_prior_scaffold`=11, `micro_scaffold`=25, `safe_refusal`=4
- Should infer bridge: `low_confidence_only`=5, `no`=14, `yes`=31
- Recommended use: `clarification_safety_slice`=10, `main_eval_with_caution`=5, `main_scaffold_eval`=31, `policy_safety_slice`=4

## Interpretation

- `insufficient` cases should not be used as primary evidence for tutoring quality; they mainly test clarification and hallucination control.
- `partial` cases can be used in development, but formal analysis should mark them or run sensitivity analysis.
- `sufficient` cases are better suited for the main scaffolding comparison.
- For short questions without dialogue, such as asking how to list branches, a good response should clarify or give a minimal observation task instead of expanding the hidden bridge directly.
