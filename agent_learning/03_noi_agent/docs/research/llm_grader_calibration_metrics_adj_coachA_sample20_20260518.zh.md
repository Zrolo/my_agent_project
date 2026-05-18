# LLM Grader Calibration Metrics: adj+CoachA Sample20

注意：本文件是 `kimi_cli` exploratory/tooling run 的指标，不是论文主 calibration evidence。论文主口径请使用 `llm_grader_calibration_metrics_adj_coachA_sample20_deepseek_20260518.zh.md`。

这些指标把 LLM grader prediction 与 `priority60 adjudicated + Coach A` sample20 reference labels 对齐比较。LLM grader 仍只作为 scalable auxiliary grader，不能替代人类教练或裁决标签。

## Run Integrity

| check | result |
| --- | --- |
| reference view | `priority60 adjudicated + Coach A` sample20 |
| tasks | 20 rows x 3 grader types = 60 |
| backend | `kimi_cli` |
| final ok rows | 60/60 |
| residual error / invalid rows | 0 |

## Metrics

| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `case_specific_bridge_rubric_judge` | 20 | 20 | 0.000 | 0.000 | 0.650 | NA/NA/NA | NA | 0.600 | 0.600 | 0.106 | 0.550 |
| `generic_rubric_judge` | 20 | 20 | 0.000 | 0.000 | 0.700 | NA/NA/NA | NA | 0.650 | 0.650 | 0.492 | 0.450 |
| `likert_only_judge` | 20 | 20 | 0.000 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.311 | 0.600 |

## Interpretation Boundary

该 sample20 reference view 没有 human critical-positive rows，因此不能用于估计 critical precision / recall / F1 或 major leakage false negative rate。它只用于检查 rater-view sensitivity 下的 overall、leakage-label、student-ready 与 safe-ready agreement。
