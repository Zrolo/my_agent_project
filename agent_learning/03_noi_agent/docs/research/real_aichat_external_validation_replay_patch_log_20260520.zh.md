# Real-AIChat External Validation And Replay Patch Log

Date: 2026-05-20

## I1. 修改文件列表

### 方法与协议文档

- `docs/research/real_aichat_external_validation_method_alignment_20260520.zh.md`
- `docs/research/real_aichat_100_observational_validation_protocol_20260520.zh.md`
- `docs/research/real_aichat_replay_30_50_protocol_20260520.zh.md`
- `docs/research/real_aichat_trajectory_subset_protocol_20260520.zh.md`

### Schema / Template / Validator

- `docs/research/real_aichat_100_observational_validation_schema_v1.json`
- `docs/research/real_aichat_100_observational_validation_template_v1.csv`
- `evals/aichat/validate_real_aichat_100_observational_validation.py`
- `docs/research/real_aichat_replay_30_50_case_schema_v1.json`
- `docs/research/real_aichat_replay_30_50_case_template_v1.csv`
- `evals/aichat/validate_real_aichat_replay_30_50_cases.py`
- `docs/research/real_aichat_replay_30_50_coach_review_schema_v1.json`
- `docs/research/real_aichat_replay_30_50_coach_review_template_v1.csv`
- `evals/aichat/validate_real_aichat_replay_30_50_reviews.py`
- `evals/aichat/tests/test_validate_real_aichat_external_validation.py`

### Manuscript / Coach Review

- `docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_6_sample_adequacy_ecological_validity.zh.md`
- `docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_7_real_aichat_validation_replay_plan.zh.md`
- `docs/research/real_student_online_5case_coach_review_guide_cn_v2_20260520.zh.md`

### 本日志

- `docs/research/real_aichat_external_validation_replay_patch_log_20260520.zh.md`

## I2. 每个文件的修改目的

| file | purpose / reviewer risk addressed |
| --- | --- |
| `real_aichat_external_validation_method_alignment_20260520.zh.md` | Addresses authenticity concern and answer-leakage overlap concern by explaining that the plan follows authentic input + offline multi-output generation + expert rubric assessment, while distinguishing ACL 2026 answer leakage robustness and DBox. |
| `real_aichat_100_observational_validation_protocol_20260520.zh.md` | Addresses sample-size concern, authenticity concern, condition-mismatch concern, and privacy/consent/reporting concern by defining Real-AIChat-100 as observational ecological-validity validation only. |
| `real_aichat_100_observational_validation_schema_v1.json` / template / validator | Provides executable structure checks for Real-AIChat-100 without requiring raw student text, complete code, complete AIChat replies, or identity fields. |
| `real_aichat_replay_30_50_protocol_20260520.zh.md` | Addresses condition-mismatch concern by explaining why observed current AIChat response cannot compare 7 harnesses, and why replay must be offline counterfactual validation. |
| `real_aichat_replay_30_50_case_schema_v1.json` / template / validator | Provides case-packet structure for replay without adding a dialogue-state v3 main condition or exposing private content. |
| `real_aichat_replay_30_50_coach_review_schema_v1.json` / template / validator | Provides blind-review structure and checks that observed references are not counted as offline harness responses. |
| `real_aichat_trajectory_subset_protocol_20260520.zh.md` | Addresses single-turn limitation concern while blocking learning-outcome and online-intervention claims. |
| `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_6_sample_adequacy_ecological_validity.zh.md` | Removes an avoidable dangerous-wording hit in the previous manuscript version while preserving the same evidence boundary. |
| `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_7_real_aichat_validation_replay_plan.zh.md` | Adds evidence hierarchy, unit-of-analysis boundaries, external-validation protocol wording, and safe wording for observed current AIChat response and replay. |
| `real_student_online_5case_coach_review_guide_cn_v2_20260520.zh.md` | Clarifies that added context fields support context sufficiency and rubric transfer, not main results, and that current AIChat response is an observed item. |
| `test_validate_real_aichat_external_validation.py` | Adds regression tests for new validators: required columns, allowed values, observed-only response role, consent/reporting gates, replay context sufficiency, and offline harness count. |

## I3. Hard-Constraint Status

- 没有新增 dialogue-state v3 main experiment: yes
- 没有新增 main condition: yes
- 没有重算主表: yes
- 没有修改线上 AIChat: yes
- 没有修改 prompt / active mode / 学生可见回复: yes
- 没有把 Real-AIChat-100 写成 main result: yes
- 没有把 Replay-30/50 写成 learning outcome study: yes
- 没有公开学生原文、代码、完整回复、身份、hash salt: yes
- 没有读取、复制或提交 `.local_private/` 私有 workbook: yes
- 没有生成或伪造 Real-AIChat-100 实际 selection manifest: yes
- 没有生成或伪造 Replay-30/50 responses 或 coach-review results: yes

## I4. TODO List

1. Citation verification for StudyChat / CSTutorBench / teacher-in-loop feedback / Teacher-Authored Prompts / REFINE / ACL 2026 answer leakage robustness.
2. Result-number verification for all manuscript values before submission.
3. Privacy / consent / data availability final review.
4. Real-AIChat-100 actual selection, if and only if privacy/consent/reporting conditions and source files are ready.
5. Replay-30 actual generation/review, if and only if Real-AIChat-100 cases and offline generation infrastructure are ready.
6. Coach double-review plan for Replay-30/50.
7. Data availability statement finalization.
8. `dialogue_v3_045_debugging_evidence` non-headline audit note remains for human confirmation before submission.

## Verification Notes

- New validator tests: passed (`Ran 10 tests ... OK` for `test_validate_real_aichat_external_validation.py`).
- Combined relevant test suite: passed (`Ran 20 tests ... OK` across existing 5-case tests and new external-validation validator tests).
- Python compile check: passed for the three new validators.
- JSON schema checks: passed for Real-AIChat-100, Replay case, and Replay coach-review schemas.
- Empty template validation: passed for Real-AIChat-100, Replay case packet, and Replay coach-review templates with `total_rows=0`.
- Existing 137-row candidate screening validator: passed with 137 rows, 30 selected pilot candidate cases, and 0 selected reportable after consent/status gate; consent/reporting warnings remain expected.
- Public 5-case Chinese template validator: passed with 5 rows, 0 reviewed rows, 0 reportable rows, and expected consent/reporting warnings.
- Dangerous-wording grep: remaining hits are restricted to required safe-wording blocks or explicit `must be avoided` / strict-reviewer diagnosis examples, not positive manuscript claims.
- Citation scan: v0.7 still contains 6 Related Work citation-placeholder groups; method-alignment docs also contain citation-verification TODO wording.
- Privacy field scan: new public CSV templates and JSON schemas do not include `raw_student_text`, `full_student_code`, `full_aichat_response`, `phone`, `email`, `school`, `real_name`, `hash_salt`, or `reversible_mapping` as public fields. The new validators include these strings only as forbidden field-name checks.
