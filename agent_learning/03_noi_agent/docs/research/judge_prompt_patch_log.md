# Judge Prompt Patch Log

This log records slow-variable changes to prompts used by runtime diagnosers/guards and offline graders. Judge prompts must be governed separately from tutor prompts because changing a grader can change measured results without changing the system under evaluation.

## Scope

This log covers:

- Runtime Bridge Diagnoser prompt;
- Runtime Leakage Guard prompt;
- Offline Bridge Grader prompt;
- Offline Leakage Grader prompt;
- Offline Response Grader prompt;
- Offline Repair Grader / before-after review prompt;
- any rubric or schema text embedded in judge prompts.

It does not cover:

- student-facing tutor prompts, which belong in `prompt_patch_log.md`;
- dataset edits, which should be recorded in dataset cards or experiment reports;
- one-off local manual judgments that are not encoded into prompts.

## Governance Rules

1. Judge prompts are slow variables.
2. A judge prompt patch must be tied to repeated failure evidence or coach-reviewed disagreement.
3. A judge prompt patch must list regression cases.
4. A judge prompt patch must not be tuned on held-out test results and then used to report the same held-out test.
5. Judge prompts should support `UNKNOWN` / `INSUFFICIENT_CONTEXT` where the evidence is inadequate.
6. Runtime judges and offline graders should be versioned separately.

## Freeze Targets

| Prompt family | Current freeze target | Status |
|---|---|---|
| Runtime Bridge Diagnoser | `bridge_diagnoser_prompt_v1.0-dev` | pending freeze |
| Runtime Leakage Guard | `leakage_guard_prompt_v1.0-dev` | pending freeze |
| Offline Bridge Grader | `offline_bridge_grader_prompt_v1.0-dev` | pending definition |
| Offline Leakage Grader | `offline_leakage_grader_prompt_v1.0-dev` | pending definition |
| Offline Response Grader | `offline_response_grader_prompt_v1.0-dev` | pending definition |
| Offline Repair Grader | `offline_repair_grader_prompt_v1.0-dev` | pending definition |

## Patch Entries

### judge_patch_log_initialized_20260511

- Date: 2026-05-11
- Affected layer: judge prompt governance
- Failure cases: N/A
- Evidence:
  - External review identified that runtime judges and offline graders must be separated.
  - Research v1 needs judge prompt freeze before held-out evaluation.
  - LLM Judge outputs need `UNKNOWN` handling and calibration against coach reference.
- Change:
  - Initialized this judge-specific patch log.
  - Declared freeze targets for runtime judges and offline graders.
  - Added governance rule that grader prompts cannot be tuned on held-out test results and then used to report those same test results.
- Regression checks:
  - N/A, documentation-only patch.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260511_leakage_required_elements

- Date: 2026-05-11
- Affected prompt: `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- Runtime or offline: offline Leakage Judge / runtime guard candidate prompt family
- Failure cases:
  - `cp_bridge_001` in `single_llm_structured + guard` smoke.
- Coach evidence:
  - N/A, runner smoke exposed a schema failure before coach review.
- Before metrics:
  - `leakage_judge_result` returned `_failed=true`.
  - `_reason`: `schema_invalid: leaked_elements must be non-empty when leakage_level > 0`.
  - Summary reported `stage_error_counts={"leakage_judge": 2}` for the two single-LLM guard smoke rows.
- Change summary:
  - Added field consistency rules to the Leakage Judge prompt.
  - If `leakage_level > 0`, `leaked_elements` must be non-empty.
  - If the judge cannot identify what leaked, it must not set `leakage_level` to 1-5.
  - If `safe_action` is `rewrite` or `block`, `repair_instruction` must be non-empty.
- Regression cases:
  - `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_requires_leaked_elements_when_level_is_positive`
  - `test_leakage_judge_v1_unit.py`
  - `test_bridge_offline_eval_runner_unit.py`
  - `test_bridge_offline_eval_summary_unit.py`
- After metrics:
  - `single_llm_structured + guard` limit-1 smoke completed with `stage_errors={}` and `safe_action=pass`.
  - `single_llm_structured + guard + repair` limit-1 smoke completed with `stage_errors={}`, `safe_action=rewrite`, and `repair_applied=true`.
- Held-out data affected? no; this was a dev/regression smoke case.
- Human approval:
  - Pending project-owner review.

## Patch Template

```text
### judge_patch_YYYYMMDD_short_name

- Date:
- Affected prompt:
- Runtime or offline:
- Failure cases:
- Coach evidence:
- Before metrics:
- Change summary:
- Regression cases:
- After metrics:
- Held-out data affected? yes/no
- Human approval:
```
