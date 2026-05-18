# LLM Grader Calibration Plan (20260517)

## Goal

Test whether an LLM grader can serve as a scalable auxiliary grader, not as a replacement for human coaches. The main question is whether a case-specific bridge rubric judge aligns better with adjudicated labels than generic rubric or likert-only judges.

## Graders

| grader | input | role |
| --- | --- | --- |
| `likert_only_judge` | response + coarse Likert rubric | Test whether a simple rating scale is enough |
| `generic_rubric_judge` | response + generic tutoring rubric | Test non-case-specific review ability |
| `case_specific_bridge_rubric_judge` | response + success criteria / forbidden content / critical boundary / acceptable reveal | Test whether MissingBridgeBench case-specific information improves agreement |

## Reference Labels

1. `priority60_adjudicated_labels`: high-disagreement rows only; closest high-risk gold, but small and difficult.
2. `priority60_adjudicated_plus_coachA`: primary paper analysis view.
3. `priority60_adjudicated_plus_coachB`: rater-strictness sensitivity.
4. Optional: Coach A only / Coach B only, to test whether the grader follows one coach's strictness.

## Metrics

- Critical binary precision / recall / F1.
- Major leakage false negative rate: human major/answer but grader non-critical.
- Student-ready agreement: binary agreement and Cohen kappa.
- Safe-ready agreement: ready and non-major/answer agreement.
- Overall correlation: Spearman / Kendall plus mean absolute error.
- Calibration slices: report main_scaffold_eval, clarification_safety_slice, and policy_safety_slice separately.

## Minimum Outputs

- `llm_grader_calibration_results_20260517.csv`: row-level human labels plus three grader predictions.
- `llm_grader_calibration_report_20260517.zh.md/.md`: metric tables, error examples, false-negative analysis.

## Paper Wording

Safe claim: the case-specific bridge rubric judge is closer to coach-adjudicated labels but remains a scalable auxiliary grader. Do not claim that the LLM Judge replaces human review or that priority60 is enough to validate a final automatic evaluator.
