# LLM Grader Calibration Metrics: adj+CoachA Sample20 DeepSeek

These metrics compare DeepSeek-backed LLM grader predictions with the `priority60 adjudicated + Coach A` sample20 reference view.

## Run Integrity

| check | result |
| --- | --- |
| reference view | `priority60 adjudicated + Coach A` sample20 |
| tasks | 20 rows x 3 grader types = 60 |
| backend | `deepseek` |
| model | `deepseek-v4-flash`, thinking disabled via offline judge profile |
| final ok rows | 60/60 |
| residual error / invalid rows | 0 |

## Metrics

| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `case_specific_bridge_rubric_judge` | 20 | 20 | 0.000 | 0.000 | 0.650 | NA/NA/NA | NA | 0.650 | 0.700 | 0.645 | 0.550 |
| `generic_rubric_judge` | 20 | 20 | 0.000 | 0.000 | 0.700 | NA/NA/NA | NA | 0.550 | 0.500 | 0.057 | 0.700 |
| `likert_only_judge` | 20 | 20 | 0.000 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.203 | 0.850 |

## Interpretation Boundary

This sample20 reference view contains no human critical-positive rows, so it cannot estimate critical precision / recall / F1 or major leakage false-negative rate. It is only a rater-view sensitivity check for overall, leakage-label, student-ready, and safe-ready agreement.
