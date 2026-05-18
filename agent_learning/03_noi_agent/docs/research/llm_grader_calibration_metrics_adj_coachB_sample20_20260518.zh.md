# LLM Grader Calibration Metrics: adj+CoachB Sample20

注意：本文件是 `kimi_cli` exploratory/tooling run 的指标，不是论文主 calibration evidence。论文主口径请使用 `llm_grader_calibration_metrics_adj_coachB_sample20_deepseek_20260518.zh.md`。

这些指标把 LLM grader prediction 与 `priority60 adjudicated + Coach B` sample20 reference labels 对齐比较。LLM grader 仍只作为 scalable auxiliary grader，不能替代人类教练或裁决标签。

## Run Integrity

| check | result |
| --- | --- |
| reference view | `priority60 adjudicated + Coach B` sample20 |
| tasks | 20 rows x 3 grader types = 60 |
| backend | `kimi_cli` |
| final ok rows | 51/60 |
| residual error rows | 9/60 |
| residual error cause | Kimi/Moonshot 429 backend errors on retry |

## Metrics

| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `case_specific_bridge_rubric_judge` | 20 | 17 | 0.150 | 0.000 | 0.824 | NA/NA/NA | NA | 0.471 | 0.471 | 0.349 | 0.647 |
| `generic_rubric_judge` | 20 | 17 | 0.150 | 0.000 | 0.824 | NA/NA/NA | NA | 0.529 | 0.412 | 0.572 | 0.529 |
| `likert_only_judge` | 20 | 17 | 0.150 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.439 | 0.647 |

## Interpretation Boundary

该 sample20 reference view 没有 human critical-positive rows，因此不能用于估计 critical precision / recall / F1 或 major leakage false negative rate。由于仍有 9 条 backend 429 error，本表只能作为 partial sensitivity，而不是完整 CoachB calibration completion record。
