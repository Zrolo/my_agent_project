# LLM Grader Calibration DeepSeek Sensitivity Report 20260518

## Status

This report is the LLM-grader calibration result that should be used for the current paper-facing view. It uses the DeepSeek offline judge profile:

```text
backend = deepseek
model = deepseek-v4-flash
thinking = disabled
```

This aligns with the main experiment's Bridge Judge / Leakage Guard / Repair stack. The earlier `20260518` calibration files without a `_deepseek_` suffix came from `kimi_cli`; they should be treated as exploratory/tooling smoke results, not as the paper's main calibration evidence.

## Run Integrity

| reference view | rows | tasks | backend | status | role |
| --- | ---: | ---: | --- | --- | --- |
| `priority60_adjudicated` | 60 | 180 | DeepSeek | 180/180 ok | Main critical-leakage calibration view |
| `adj+CoachA sample20` | 20 | 60 | DeepSeek | 60/60 ok | Rater-view sensitivity |
| `adj+CoachB sample20` | 20 | 60 | DeepSeek | 60/60 ok | Rater-view sensitivity |

## Main Metrics

| reference | grader | valid | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| priority60 | `likert_only_judge` | 60/60 | NA | NA/NA/NA | NA | NA | NA | 0.129 | 1.200 |
| priority60 | `generic_rubric_judge` | 60/60 | 0.583 | NA/0.000/NA | 1.000 | 0.433 | 0.400 | -0.140 | 1.033 |
| priority60 | `case_specific_bridge_rubric_judge` | 60/60 | 0.617 | NA/0.000/NA | 1.000 | 0.467 | 0.533 | 0.167 | 1.033 |
| adj+CoachA sample20 | `likert_only_judge` | 20/20 | NA | NA/NA/NA | NA | NA | NA | 0.203 | 0.850 |
| adj+CoachA sample20 | `generic_rubric_judge` | 20/20 | 0.700 | NA/NA/NA | NA | 0.550 | 0.500 | 0.057 | 0.700 |
| adj+CoachA sample20 | `case_specific_bridge_rubric_judge` | 20/20 | 0.650 | NA/NA/NA | NA | 0.650 | 0.700 | 0.645 | 0.550 |
| adj+CoachB sample20 | `likert_only_judge` | 20/20 | NA | NA/NA/NA | NA | NA | NA | 0.170 | 1.000 |
| adj+CoachB sample20 | `generic_rubric_judge` | 20/20 | 0.800 | NA/NA/NA | NA | 0.450 | 0.400 | -0.006 | 0.700 |
| adj+CoachB sample20 | `case_specific_bridge_rubric_judge` | 20/20 | 0.900 | NA/NA/NA | NA | 0.450 | 0.550 | 0.040 | 0.950 |

## Interpretation

`priority60_adjudicated` remains the key reference view because it contains 16 human critical-positive rows. The DeepSeek-backed case-specific bridge-rubric judge improves some auxiliary metrics relative to the generic rubric: leakage-label accuracy is 0.617 vs 0.583, student-ready agreement is 0.467 vs 0.433, and safe-ready agreement is 0.533 vs 0.400.

The safety-critical result is still weak: both the generic and case-specific DeepSeek graders have critical recall 0 and major leakage false-negative rate 1.000. On this high-risk / high-disagreement priority60 reference, the automatic grader fails to recover the rows humans adjudicated as `major_bridge_leakage` / `answer_leakage`.

The paper-safe wording is:

```text
Case-specific bridge rubrics improve some auxiliary grading signals over a generic rubric, but DeepSeek-backed LLM graders still fail to recover human critical-positive leakage labels on the high-risk priority60 reference. Human review and adjudication remain necessary.
```

## Rater-View Sensitivity

The `adj+CoachA sample20` and `adj+CoachB sample20` views contain no human critical-positive rows, so they cannot estimate critical recall / F1. They only show:

- the case-specific judge has stronger overall correlation on CoachA sample20 (0.645) and lower MAE (0.550);
- the case-specific judge has higher leakage-label accuracy on CoachB sample20 (0.900), while ready agreement and overall correlation remain weak;
- ready / safe-ready remain rater-sensitive, so the paper should not report only one rater view.

## Kimi Exploratory Result Boundary

The previous `kimi_cli` calibration result can remain as a tooling/exploratory record, but it should not be mixed with the DeepSeek-aligned main calibration:

- the Kimi priority60 case-specific judge had critical recall 0.312;
- the DeepSeek priority60 case-specific judge has critical recall 0;
- this difference shows that LLM-grader calibration is backend-sensitive;
- therefore the paper should emphasize that automatic graders are auxiliary signals, not gold labels.

## Paper Wording

Can write:

- case-specific bridge rubrics improve some DeepSeek auxiliary-grading metrics;
- priority60 still exposes high critical false-negative risk;
- automatic LLM graders cannot replace double human review / adjudication;
- LLM-grader calibration is backend-sensitive, so the main paper result must rely on human review.

Do not write:

- DeepSeek LLM graders reliably identify critical bridge leakage;
- case-specific judges can replace human coaches;
- the Kimi exploratory result is the main experiment calibration;
- LLM grader labels are gold.
