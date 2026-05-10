# Prompt Patch Log

This log records slow-variable changes to prompts, rubrics, registries, routers, or repair policy. Each patch should be tied to failure evidence and regression checks.

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
