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

Status labels:

- `freeze-candidate`: can enter held-out only after project-owner approval and version stamping.
- `dev-signal-only`: may be logged for analysis, but cannot be treated as final gold.
- `pending-definition`: not ready for held-out headline metrics.
- `blocked`: should not enter held-out until the listed blocker is resolved.

| Prompt family | Current freeze target | Freeze readiness status | Held-out role |
|---|---|---|---|
| Runtime Bridge Diagnoser | `bridge_diagnoser_prompt_v1.0-dev` | `freeze-candidate` | diagnosis/control signal; needs coach agreement reporting |
| Runtime Leakage Guard | `leakage_guard_prompt_v1.0-dev` | `dev-signal-only` | log alongside coach leakage labels and static lint; do not use as sole safety judgment |
| Offline Bridge Grader | `offline_bridge_grader_prompt_v1.0-dev` | `pending-definition` | not ready for headline automated grading |
| Offline Leakage Grader | `offline_leakage_grader_prompt_v1.0-dev` | `pending-definition` | not ready for headline automated grading |
| Offline Response Grader | `offline_response_grader_prompt_v1.0-dev` | `pending-definition` | not ready for headline automated grading |
| Offline Repair Grader | `offline_repair_grader_prompt_v1.0-dev` | `pending-definition` | use coach before/after review instead |

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

### judge_patch_20260511_fully_worked_micro_example_leakage

- Date: 2026-05-11
- Affected prompt: `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- Runtime or offline: offline Leakage Judge / runtime guard candidate prompt family
- Failure cases:
  - Dev ablation Bridge Contract cases such as `cp_bridge_001`, `cp_bridge_008`, and `cp_bridge_010`.
  - Repair stress cases where a fully worked small example directly demonstrated the current missing bridge.
- Coach evidence:
  - Coach notes repeatedly marked outputs as pedagogically strong but leaking because the micro-example completed the current bridge, such as endpoint/LCA marking, binary-search boundary movement, or 0/1 knapsack overwrite order.
- Before metrics:
  - In the 10-case dev ablation, `bridge_contract` had 10/10 minor or major bridge leakage despite the highest mean quality.
  - `bridge_contract+guard` still had 9/10 minor or major bridge leakage, indicating that guard detection undercounted fully worked micro-example leakage.
- Change summary:
  - Added an explicit rule that a fully worked micro-example can be critical bridge leakage.
  - If a candidate response completely demonstrates the relation the student was supposed to infer, it should usually be `leakage_level=3` even without complete code or a complete solution.
- Regression cases:
  - `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_treats_fully_worked_micro_example_as_possible_leakage`
- After metrics:
  - Unit tests pass; empirical after-metrics require a rerun on dev ablation cases before prompt freeze.
- Held-out data affected? no; this was based on dev/regression review.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260511_repair_quality_guard

- Date: 2026-05-11
- Affected prompt: `docs/common/aichat_repair_response_v1_system_prompt.md`
- Runtime or offline: offline Repair Generator prompt family
- Failure cases:
  - Repair stress: `repair_stress_002`, `repair_stress_011`, `repair_stress_013`, `repair_stress_018`.
  - Dev ablation: `cp_bridge_005` and `cp_bridge_006` in `bridge_contract+guard+repair`, where repair became off-topic or too weak.
- Coach evidence:
  - Coach notes identified three recurring repair failures: invalid numeric examples, vague questions that do not help the student advance, and incomplete fill-in slots.
- Before metrics:
  - In 20-case repair stress blind review, repair reduced major/answer leakage from 100% to 5%, but quality dropped in 3/20 cases.
- Change summary:
  - Added repair quality safeguards: do not repair into a vague question, keep one concrete current task, self-check numeric examples, and provide complete fill-in slots.
- Regression cases:
  - `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_requires_concrete_valid_micro_task`
- After metrics:
  - Unit tests pass; empirical after-metrics require a rerun of repair stress or dev ablation.
- Held-out data affected? no; this was based on dev/regression review.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260511_repair_abstract_leakage_shapes

- Date: 2026-05-11
- Affected prompt: `docs/common/aichat_repair_response_v1_system_prompt.md`
- Runtime or offline: offline Repair Generator prompt family
- Failure cases:
  - Project-owner review identified that the "common repair methods" section listed concrete algorithm/term recipes such as DP, check, and mid.
  - This risked turning Repair into a finite algorithm-specific template list rather than a bridge-family repair policy.
- Coach evidence:
  - Dev/review discussion emphasized that repair should generalize by leakage shape, such as representation meaning, relation/formula, predicate condition, flow/strategy, code/template, and fully worked micro-example.
- Before metrics:
  - No held-out metrics affected; this is a dev prompt abstraction patch before prompt freeze.
- Change summary:
  - Rewrote "common repair methods" as an abstract leakage-shape to repair-action policy.
  - Removed concrete algorithm terms from that section.
  - Added a rule that the Repair Generator must not apply templates by concrete algorithm name.
- Regression cases:
  - `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_uses_abstract_leakage_shapes_not_algorithm_specific_recipes`
- After metrics:
  - Unit tests pass; empirical after-metrics require rerunning repair stress or dev ablation.
- Held-out data affected? no; this was based on dev/regression review.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260511_leakage_repair_instruction_abstract_shapes

- Date: 2026-05-11
- Affected prompt: `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- Runtime or offline: offline Leakage Judge / runtime guard candidate prompt family
- Failure cases:
  - The Leakage Judge's `repair_instruction` examples still used concrete algorithm terms such as DP, check, and mid.
  - Because Repair consumes `repair_instruction`, these examples could reintroduce algorithm-specific templates even after Repair prompt abstraction.
- Coach evidence:
  - Project-owner review requested that repair guidance be phrased by common bridge/leakage shapes rather than by specific algorithms.
- Before metrics:
  - No held-out metrics affected; this is a dev prompt abstraction patch before prompt freeze.
- Change summary:
  - Rewrote `repair_instruction` examples as abstract leakage-shape instructions.
  - Replaced concrete wording in the leakage-level/rules section where possible with representation, relation/formula, predicate condition, strategy, code/template, and fully worked micro-example language.
  - Kept schema enum keys unchanged for backward compatibility.
- Regression cases:
  - `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_uses_abstract_repair_instructions`
- After metrics:
  - Unit tests pass; empirical after-metrics require rerunning dev ablation or repair stress.
- Held-out data affected? no; this was based on dev/regression review.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260512_definition_first_bridge_leak

- Date: 2026-05-12
- Affected prompt:
  - `docs/common/aichat_leakage_judge_v1_system_prompt.md`
  - `docs/common/aichat_repair_response_v1_system_prompt.md`
- Runtime or offline: offline Leakage Judge / Repair Generator prompt family
- Failure cases:
  - Dev ablation blind review flagged major leakage where the response began with a definition of the very concept the student was trying to infer, then followed with a question or micro-example.
  - This pattern appeared in representation/semantics cases and state-template cases; it is a critical bridge leak even if the rest of the response looks question-based.
- Coach evidence:
  - Major leakage notes for `cp_bridge_005`, `cp_bridge_003`, and related dev cases described the issue as “开头直接定义/模板搬运/把学生本轮要悟出的语义说穿”.
- Before metrics:
  - In the 10-case dev ablation blind review, 8/120 rows were labeled major bridge leakage.
- Change summary:
  - Leakage Judge now explicitly treats an opening definition sentence as possible critical bridge leakage when it directly names or explains the missing concept before asking a question.
  - Repair now explicitly deletes such definition-first leaks and converts them into an observation task, comparison task, or blank slot.
- Regression cases:
  - `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_flags_definition_first_bridge_leaks`
  - `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_removes_definition_first_leaks`
- After metrics:
  - Unit tests pass; empirical after-metrics require rerunning dev ablation or a targeted prompt smoke.
- Held-out data affected? no; this was based on dev/regression review.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260512_answer_slot_question_leak

- Date: 2026-05-12
- Affected prompt: `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- Runtime or offline: offline Leakage Judge / runtime guard candidate prompt family
- Failure cases:
  - Targeted regression smoke after the definition-first patch showed that some generators no longer stated the answer directly, but still asked the student to fill exact forbidden slots.
  - Examples included asking for add/subtract positions, true/false follow-up actions, boundary directions, or semantic labels when those slots were exactly the current missing bridge.
- Coach/self-review evidence:
  - `definition_first_regression_smoke_20260512.zh.md` identified answer-slot questions as a remaining leakage route in `cp_bridge_001`, `cp_bridge_002`, `cp_bridge_005`, and `cp_bridge_010`.
- Before metrics:
  - The targeted smoke was qualitative and development-only; no held-out metrics affected.
- Change summary:
  - Leakage Judge now explicitly treats answer-slot questions as possible critical bridge leakage when the question asks the student to fill forbidden positions, directions, actions, or true/false semantics.
  - Repair instructions should move such prompts upstream to observations about affected objects, candidate meaning, observable evidence, or dependency sources.
- Regression cases:
  - `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_flags_answer_slot_questions`
- After metrics:
  - Unit tests pass; empirical after-metrics require rerunning targeted regression smoke or dev ablation.
- Held-out data affected? no; this was based on dev/regression review.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260512_internal_field_update_leak

- Date: 2026-05-12
- Affected prompt: `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- Runtime or offline: offline Leakage Judge / runtime guard candidate prompt family
- Failure cases:
  - A targeted rerun on `cp_bridge_005` showed the Guard passing a response that directly specified internal maintenance effects such as updating a node field and tag value before asking the student to infer the semantic role.
  - This is not full code, but it can directly complete the student's missing data-structure operation semantics.
- Coach/self-review evidence:
  - The dev review already marked lazy-tag semantics leaks as major when the response explains the exact meaning or field effect before the student has inferred it.
- Before metrics:
  - Targeted smoke only; no held-out metrics affected.
- Change summary:
  - Leakage Judge now explicitly treats internal field update actions as possible critical bridge leakage when the student is missing data-structure operation semantics, representation meaning, or local maintenance logic.
  - Repair instructions should delete filled field changes, marker changes, push/merge actions, and filled traces, replacing them with object/operation inputs and blank observation tables.
- Regression cases:
  - `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_flags_internal_field_update_leaks`
- After metrics:
  - Unit tests pass; empirical after-metrics require rerunning targeted regression smoke.
- Held-out data affected? no; this was based on dev/regression review.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260512_answer_slot_upstream_observation_split

- Date: 2026-05-12
- Affected prompt: `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- Runtime or offline: offline Leakage Judge / runtime guard candidate prompt family
- Failure cases:
  - A 5-case post-repair smoke showed that `--post-repair-fallback-on-leak` only helps when the post-repair judge catches the bad repair.
  - `cp_bridge_002` and `cp_bridge_005` remained risky because the candidate or repaired response asked the student to fill the exact missing predicate/semantic slot, while the post-repair judge treated the question form as safe.
- Coach/self-review evidence:
  - `definition_first_post_repair_self_review_20260512.zh.md` and `post_repair_fallback_smoke_20260512.zh.md` both identify answer-slot / filled-table leakage as the remaining failure pattern.
- Before metrics:
  - In the post-repair fallback 5-case smoke, the automatic post-repair judge reported `repair_still_leaks_rate=0.000`, but manual self-review still flagged answer-slot risk in `cp_bridge_002` and `cp_bridge_005`.
- Change summary:
  - Added a harder binary distinction between safe upstream observation tasks and unsafe answer-slot questions.
  - The prompt now says that question wording cannot lower leakage severity when the response asks the student to directly fill the current missing bridge.
  - It explicitly covers true/false semantics, follow-up actions, key positions, directions, field updates, compensation objects, and complete rules as answer slots.
- Regression cases:
  - `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_distinguishes_upstream_observation_from_answer_slots`
- After metrics:
  - Unit test passes.
  - Targeted 5-case rerun with `--post-repair-fallback-on-leak` completed with no stage errors.
  - Automatic metrics improved superficially (`critical_bridge_leakage_rate=0.000`, `repair_still_leaks_rate=0.000`), but self-review still found 4/5 rows with major bridge leakage.
  - Conclusion: prompt-only Leakage Judge calibration remains insufficient for answer-slot / filled-table / worked-example recall.
- Held-out data affected? no; this is a dev/regression prompt patch before prompt freeze.
- Human approval:
  - Pending project-owner review.

### judge_patch_20260512_leaked_elements_schema_tolerance

- Date: 2026-05-12
- Affected layer: offline Leakage Judge schema validation / runner analyzability
- Runtime or offline: offline evaluation support
- Failure cases:
  - EDF core dev ablation produced a recoverable stage error in `cp_bridge_005` / `bridge_contract_guard`: the Leakage Judge returned `leakage_level > 0` but left `leaked_elements` empty.
- Coach/self-review evidence:
  - The candidate still needed analysis; dropping the whole guard result as `schema_invalid` made dev summaries noisier without improving safety.
- Before metrics:
  - `edf_core_ablation_20260512` had one `leakage_judge` stage error caused by `leaked_elements must be non-empty when leakage_level > 0`.
- Change summary:
  - Validation now normalizes this recoverable omission to `leaked_elements=["unknown_leaked_element"]`.
  - The Leakage Judge prompt remains strict: positive leakage should still identify leaked elements.
  - This is an analyzability patch, not evidence that the guard is more accurate.
- Regression cases:
  - `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_validate_leakage_judge_schema_normalizes_empty_positive_leaked_elements`
- After metrics:
  - Targeted schema test passes.
- Held-out data affected? no; this is a dev/pre-held-out validation tolerance patch.
- Human approval:
  - Pending project-owner review before prompt/judge freeze.

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
