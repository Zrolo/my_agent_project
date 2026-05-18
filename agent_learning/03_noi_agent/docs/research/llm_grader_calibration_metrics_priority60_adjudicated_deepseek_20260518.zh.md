# LLM Grader Calibration Metrics: Priority60 DeepSeek

这些指标把 DeepSeek-backed LLM grader prediction 与 `priority60_adjudicated` coach/adjudicated reference labels 对齐比较。LLM grader 仍只作为 auxiliary grader，不能替代人类教练或裁决流程。

## Run Integrity

| check | result |
| --- | --- |
| reference view | `priority60_adjudicated` |
| tasks | 60 rows x 3 grader types = 180 |
| backend | `deepseek` |
| model | `deepseek-v4-flash`，offline judge profile 中 thinking disabled |
| final ok rows | 180/180 |
| residual error / invalid rows | 0 |

## Metrics

| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `case_specific_bridge_rubric_judge` | 60 | 60 | 0.000 | 0.000 | 0.617 | NA/0.000/NA | 1.000 | 0.467 | 0.533 | 0.167 | 1.033 |
| `generic_rubric_judge` | 60 | 60 | 0.000 | 0.000 | 0.583 | NA/0.000/NA | 1.000 | 0.433 | 0.400 | -0.140 | 1.033 |
| `likert_only_judge` | 60 | 60 | 0.000 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.129 | 1.200 |

## Interpretation Boundary

这是当前项目与 DeepSeek 主实验模型配置对齐的 calibration view。结果显示 case-specific bridge-rubric judge 相比 generic rubric 在 leakage-label accuracy、ready / safe-ready agreement 上略有改善，但 generic 和 case-specific DeepSeek grader 都没有识别出 priority60 reference 中的 human critical-positive rows。critical recall 为 0，major leakage false-negative rate 为 1.000。

因此论文最稳的写法是：case-specific rubric 能改善 auxiliary grading signal，但 DeepSeek-backed LLM grader 仍不能替代 human review 来评估 critical-bridge leakage。
