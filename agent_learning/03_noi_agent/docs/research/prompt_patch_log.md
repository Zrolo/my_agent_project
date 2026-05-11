# Prompt Patch Log

This log records slow-variable changes to prompts, rubrics, registries, routers, or repair policy. Each patch should be tied to failure evidence and regression checks.

## Governance Rules

- Prompt changes are slow-variable updates. They should not happen automatically during a student conversation.
- Student-facing tutor prompts are tracked here. Judge and grader prompts are tracked separately in `judge_prompt_patch_log.md`.
- Prompt tuning should happen on dev/regression cases, not on held-out test cases used for headline results.
- A prompt patch requires failure evidence, regression checks, and human approval before it is treated as a frozen research version.
- When possible, patch one layer at a time: tutor prompt, repair prompt, rubric, registry, router, or fallback policy.

## Freeze Targets

| Prompt family | Current freeze target | Status |
|---|---|---|
| Main Tutor / current AIChat prompt | `tutor_prompt_v1.0-dev` | pending freeze |
| Bridge Contract Tutor prompt | `bridge_contract_tutor_prompt_v1.0-dev` | pending freeze |
| Repair Generator prompt | `repair_prompt_v1.0-dev` | in dev after micro-task guard patch |
| Deterministic fallback policy text | `fallback_policy_v1.0-dev` | pending freeze |

## patch_20260510_repair_micro_task_guard

- Date: 2026-05-10
- Affected layer: repair prompt / repair user-message contract
- Failure cases: `cp_bridge_010`
- Evidence:
  - `bridge_contract + guard` correctly identified an over-strong 0/1 knapsack micro-example as `safe_action=block`.
  - A later repair run could still solve the replacement micro-task by explaining the same bridge through another fully worked example.
- Change:
  - `docs/common/aichat_repair_response_v1_system_prompt.md` now states that when the repair instruction asks the student to construct, calculate, compare, or observe a replacement micro-example, the repair response must not solve that task for the student.
  - `noi_agent._build_repair_response_v1_user_message()` now repeats this as a per-call hard constraint.
- Regression checks:
  - `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_forbids_solving_replacement_micro_task`
  - `test_aichat_hard_gate_fallback_regression_unit.py`
- Verification:
  - 24 related unit tests passed on 2026-05-10.
- Human approval:
  - Pending project-owner review.
