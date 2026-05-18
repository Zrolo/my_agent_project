# LLM Grader Calibration Metrics

Note: this file is from a `kimi_cli` exploratory/tooling run, not the paper-facing calibration evidence. Use `llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.md` and `llm_grader_calibration_deepseek_sensitivity_report_20260518.md` for the paper-facing view.

These metrics compare LLM grader predictions with coach/adjudicated references. LLM graders remain auxiliary graders, not gold labels.

| grader | n | valid | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `case_specific_bridge_rubric_judge` | 60 | 60 | 0.000 | 0.000 | 0.567 | 0.833/0.312/0.455 | 0.688 | 0.450 | 0.650 | 0.450 | 0.783 |
| `generic_rubric_judge` | 60 | 60 | 0.000 | 0.000 | 0.517 | NA/0.000/NA | 1.000 | 0.450 | 0.700 | 0.167 | 0.867 |
| `likert_only_judge` | 60 | 60 | 0.000 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.087 | 0.933 |
