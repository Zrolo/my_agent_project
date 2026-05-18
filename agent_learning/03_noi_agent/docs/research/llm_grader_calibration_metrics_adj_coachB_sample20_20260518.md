# LLM Grader Calibration Metrics: adj+CoachB Sample20

Note: this file is from a `kimi_cli` exploratory/tooling run, not the paper-facing calibration evidence. Use `llm_grader_calibration_metrics_adj_coachB_sample20_deepseek_20260518.md` for the paper-facing view.

These metrics compare LLM grader predictions with the `priority60 adjudicated + Coach B` sample20 reference labels. LLM graders remain scalable auxiliary graders, not replacements for human coaches or adjudicated references.

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

This sample20 reference view contains no human critical-positive rows, so it cannot estimate critical precision / recall / F1 or major leakage false-negative rate. Because 9 backend 429 errors remain, this table is only a partial sensitivity result rather than a complete CoachB calibration completion record.
