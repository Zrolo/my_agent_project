# LLM Grader Calibration Kimi Exploratory Sensitivity Report 20260518

## Reviewer-Facing Status

This file records a `kimi_cli` exploratory/tooling run, not the current paper-facing calibration evidence. The paper-facing view is the DeepSeek-aligned report:

```text
docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.md
```

This file is retained only to document that LLM-grader calibration is backend-sensitive; automatic graders remain auxiliary signals and cannot replace human review.

## Summary

This pass completed the `priority60_adjudicated` main reference view and the `adj+CoachA sample20` sensitivity run. The `adj+CoachB sample20` run remains partial because 9/60 rows still failed with Kimi/Moonshot 429 backend errors after retry.

The paper-safe conclusion is:

```text
The case-specific bridge-rubric judge is more useful than a generic rubric as a scalable auxiliary grader, but it still has substantial critical false-negative risk and cannot replace human review or adjudication.
```

## Reference Views

| reference view | rows | tasks | status | role |
| --- | ---: | ---: | --- | --- |
| `priority60_adjudicated` | 60 | 180 | 180/180 ok | Main calibration evidence with high-risk / high-disagreement critical positives |
| `adj+CoachA sample20` | 20 | 60 | 60/60 ok | Rater-view sensitivity |
| `adj+CoachB sample20` | 20 | 60 | 51/60 ok | Partial rater-view sensitivity; 9 rows failed with backend 429 |

## Main Metrics

| reference | grader | valid | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| priority60 | `likert_only_judge` | 60/60 | NA | NA/NA/NA | NA | NA | NA | 0.087 | 0.933 |
| priority60 | `generic_rubric_judge` | 60/60 | 0.517 | NA/0.000/NA | 1.000 | 0.450 | 0.700 | 0.167 | 0.867 |
| priority60 | `case_specific_bridge_rubric_judge` | 60/60 | 0.567 | 0.833/0.312/0.455 | 0.688 | 0.450 | 0.650 | 0.450 | 0.783 |
| adj+CoachA sample20 | `likert_only_judge` | 20/20 | NA | NA/NA/NA | NA | NA | NA | 0.311 | 0.600 |
| adj+CoachA sample20 | `generic_rubric_judge` | 20/20 | 0.700 | NA/NA/NA | NA | 0.650 | 0.650 | 0.492 | 0.450 |
| adj+CoachA sample20 | `case_specific_bridge_rubric_judge` | 20/20 | 0.650 | NA/NA/NA | NA | 0.600 | 0.600 | 0.106 | 0.550 |
| adj+CoachB sample20 partial | `likert_only_judge` | 17/20 | NA | NA/NA/NA | NA | NA | NA | 0.439 | 0.647 |
| adj+CoachB sample20 partial | `generic_rubric_judge` | 17/20 | 0.824 | NA/NA/NA | NA | 0.529 | 0.412 | 0.572 | 0.529 |
| adj+CoachB sample20 partial | `case_specific_bridge_rubric_judge` | 17/20 | 0.824 | NA/NA/NA | NA | 0.471 | 0.471 | 0.349 | 0.647 |

## Interpretation

`priority60_adjudicated` is the key reference view because it includes high-risk / high-disagreement rows and 16 human critical-positive rows. On this view, the case-specific bridge-rubric judge is better than the generic rubric judge: the generic judge has critical recall 0, while the case-specific judge reaches 0.312 recall and 0.833 precision.

This should not be written as reliable automated leakage grading. The case-specific judge still misses 11/16 human critical-positive rows, with a major leakage false-negative rate of 0.688. The result supports “case-specific rubrics improve auxiliary grading,” not “LLM judges replace human review.”

The `adj+CoachA sample20` and `adj+CoachB sample20` views mainly check rater-view sensitivity. These sample20 views contain no human critical-positive rows, so they cannot support critical recall or false-negative claims. They show that generic and case-specific graders can be close on non-critical leakage-label agreement, while ready and safe-ready agreement remain modest and rater-sensitive.

## Paper Wording

Can write:

- case-specific bridge rubrics improve LLM graders as auxiliary dev-stage signals relative to generic rubrics on the high-risk priority60 reference;
- the best auxiliary grader still misses many human critical-positive rows, so human review and adjudication remain necessary;
- rater-view sensitivity remains visible, especially for student-ready and safe-ready labels.

Do not write:

- LLM graders can replace human review;
- LLM grader labels are gold;
- priority60 is sufficient as final automatic-grader validation;
- the case-specific judge reliably captures all critical bridge leakage.

## Remaining Gap

`adj+CoachB sample20` still has 9 backend 429 errors. It can be completed later by rerunning the same prediction JSONL with `--retry-non-ok`. Until then, it should be described as a partial CoachB sample20 sensitivity result.
