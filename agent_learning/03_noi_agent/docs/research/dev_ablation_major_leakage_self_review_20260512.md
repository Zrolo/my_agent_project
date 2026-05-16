# Dev Ablation Major Leakage Self-Review and Patch Record (2026-05-12)

This note is based on `dev_ablation_safe_scaffold_blind_review_analysis_20260512.zh.md`. It is a development-stage self-review and prompt/rubric patch record, not a final held-out paper result.

## Observed Failure Pattern

Across 10 development cases, 12 system conditions, and 120 blind-reviewed responses, 8 rows were labeled as `major_bridge_leakage`. These were not full-code or full-solution leaks. They were critical-bridge leaks:

1. **Definition-first leakage**: the response opens by defining the exact concept the student is trying to infer, then asks a question.
2. **Fully worked micro-example leakage**: the example is relevant but computes or demonstrates the missing relation completely.
3. **Canonical-template leakage**: the response copies a standard state meaning, marking rule, or update-order template into the answer.
4. **Sequential bridge completion**: the response gives a local judgment and then asks for the next action, boundary direction, or operation location in the same turn.

## Patch Principle

This patch does not add algorithm-specific recipes. It patches abstract leakage shapes:

- Bridge Contract Tutor must not use an opening definition sentence to name or explain the current missing bridge.
- Bridge Contract Tutor must not both judge a local result and ask for the next action/boundary/location in one turn.
- DBox-inspired baseline must not copy canonical templates or standard definitions; `current_substep` must be a task, not an answer sentence.
- Leakage Judge now explicitly treats definition-first responses as possible critical bridge leakage.
- Repair now explicitly removes definition-first leaks and converts them into observation tasks, comparison tasks, or blank slots.

## Modified Files

- `evals/aichat/run_bridge_offline_eval.py`
- `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- `docs/common/aichat_repair_response_v1_system_prompt.md`
- `docs/research/prompt_patch_log.md`
- `docs/research/judge_prompt_patch_log.md`

## Regression Tests

Added or updated:

- `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_prompt_blocks_definition_first_and_followup_action_leaks`
- `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_dbox_prompt_blocks_canonical_template_and_definition_leaks`
- `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_flags_definition_first_bridge_leaks`
- `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_removes_definition_first_leaks`

## What This Does Not Prove

This patch only means that the prompts/rubrics now cover a recurring development-set failure pattern. It does not prove:

- Bridge Contract significantly outperforms strong baselines;
- Guard/Repair fully solves critical bridge leakage;
- DBox-inspired baselines are formally beaten;
- The patch will improve held-out results.

The next step remains targeted smoke before prompt freeze, followed by 50-case held-out evaluation, partial double annotation, and judge calibration.
