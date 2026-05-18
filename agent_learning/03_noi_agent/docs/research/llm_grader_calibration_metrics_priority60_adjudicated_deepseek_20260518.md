# LLM Grader Calibration Metrics: Priority60 DeepSeek

These metrics compare DeepSeek-backed LLM grader predictions with `priority60_adjudicated` coach/adjudicated references. LLM graders remain auxiliary graders, not human-review replacements.

## Run Integrity

| check | result |
| --- | --- |
| reference view | `priority60_adjudicated` |
| tasks | 60 rows x 3 grader types = 180 |
| backend | `deepseek` |
| model | `deepseek-v4-flash`, thinking disabled via offline judge profile |
| final ok rows | 180/180 |
| residual error / invalid rows | 0 |

## Metrics

| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `case_specific_bridge_rubric_judge` | 60 | 60 | 0.000 | 0.000 | 0.617 | NA/0.000/NA | 1.000 | 0.467 | 0.533 | 0.167 | 1.033 |
| `generic_rubric_judge` | 60 | 60 | 0.000 | 0.000 | 0.583 | NA/0.000/NA | 1.000 | 0.433 | 0.400 | -0.140 | 1.033 |
| `likert_only_judge` | 60 | 60 | 0.000 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.129 | 1.200 |

## Interpretation Boundary

This DeepSeek-backed run is the model-aligned calibration view for the current project. It shows that the case-specific bridge-rubric judge improves leakage-label accuracy and ready/safe-ready agreement relative to the generic rubric, but neither generic nor case-specific DeepSeek grader detects the human critical-positive rows in this priority60 reference. The critical recall is 0 and the major leakage false-negative rate is 1.000.

This supports a conservative paper claim: case-specific rubrics can improve auxiliary grading signals, but DeepSeek-backed LLM graders are not reliable enough to replace human review for critical-bridge leakage.
