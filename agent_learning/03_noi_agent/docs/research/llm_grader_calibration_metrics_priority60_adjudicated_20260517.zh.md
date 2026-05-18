# LLM Grader Calibration Metrics

注意：本文件是 `kimi_cli` exploratory/tooling run 的指标，不是论文主 calibration evidence。论文主口径请使用 `llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.zh.md` 和 `llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md`。

这些指标将 LLM grader prediction 与 coach/adjudicated reference 对比。LLM grader 仍是辅助 grader，不是 gold label。

| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `case_specific_bridge_rubric_judge` | 60 | 60 | 0.000 | 0.000 | 0.567 | 0.833/0.312/0.455 | 0.688 | 0.450 | 0.650 | 0.450 | 0.783 |
| `generic_rubric_judge` | 60 | 60 | 0.000 | 0.000 | 0.517 | NA/0.000/NA | 1.000 | 0.450 | 0.700 | 0.167 | 0.867 |
| `likert_only_judge` | 60 | 60 | 0.000 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.087 | 0.933 |

解释见：

- `llm_grader_calibration_priority60_report_20260517.zh.md`
- `llm_grader_calibration_priority60_report_20260517.md`
