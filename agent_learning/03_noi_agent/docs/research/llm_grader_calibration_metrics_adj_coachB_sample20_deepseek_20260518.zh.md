# LLM Grader Calibration Metrics: adj+CoachB Sample20 DeepSeek

这些指标把 DeepSeek-backed LLM grader prediction 与 `priority60 adjudicated + Coach B` sample20 reference view 对齐比较。

## Run Integrity

| check | result |
| --- | --- |
| reference view | `priority60 adjudicated + Coach B` sample20 |
| tasks | 20 rows x 3 grader types = 60 |
| backend | `deepseek` |
| model | `deepseek-v4-flash`，offline judge profile 中 thinking disabled |
| final ok rows | 60/60 |
| residual error / invalid rows | 0 |

## Metrics

| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `case_specific_bridge_rubric_judge` | 20 | 20 | 0.000 | 0.000 | 0.900 | NA/NA/NA | NA | 0.450 | 0.550 | 0.040 | 0.950 |
| `generic_rubric_judge` | 20 | 20 | 0.000 | 0.000 | 0.800 | NA/NA/NA | NA | 0.450 | 0.400 | -0.006 | 0.700 |
| `likert_only_judge` | 20 | 20 | 0.000 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.170 | 1.000 |

## Interpretation Boundary

该 sample20 reference view 没有 human critical-positive rows，因此不能用于估计 critical precision / recall / F1 或 major leakage false-negative rate。它只用于检查 rater-view sensitivity 下的 overall、leakage-label、student-ready 与 safe-ready agreement。
