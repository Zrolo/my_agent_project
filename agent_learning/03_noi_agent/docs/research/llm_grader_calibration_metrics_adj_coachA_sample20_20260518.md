# LLM Grader Calibration Metrics: adj+CoachA Sample20

Note: this file is from a `kimi_cli` exploratory/tooling run, not the paper-facing calibration evidence. Use `llm_grader_calibration_metrics_adj_coachA_sample20_deepseek_20260518.md` for the paper-facing view.

These metrics compare LLM grader predictions with the `priority60 adjudicated + Coach A` sample20 reference labels. LLM graders remain scalable auxiliary graders, not replacements for human coaches or adjudicated references.

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

This sample20 reference view contains no human critical-positive rows, so it cannot estimate critical precision / recall / F1 or major leakage false-negative rate. It is only a rater-view sensitivity check for overall, leakage-label, student-ready, and safe-ready agreement.
