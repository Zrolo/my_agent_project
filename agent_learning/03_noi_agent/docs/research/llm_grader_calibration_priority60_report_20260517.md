# LLM Grader Calibration Priority60 Report 20260517

## Status

This is the `priority60_adjudicated` exploratory/tooling result under the `kimi_cli` backend. It is not the current paper-facing calibration evidence. The paper-facing view is the DeepSeek-aligned report: `llm_grader_calibration_deepseek_sensitivity_report_20260518.md`.

This file is retained because it shows that LLM-grader calibration is backend-sensitive: the Kimi exploratory run has some case-specific critical recall, while the DeepSeek-backed run has critical recall 0 on priority60. This further supports the claim that automatic graders are auxiliary signals and cannot replace human review.

The LLM grader remains a scalable auxiliary grader. It does not replace human coaches or adjudicated references.

## Inputs And Outputs

| item | value |
| --- | --- |
| reference | `priority60_adjudicated` labels |
| prompt pack | `docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl` |
| predictions | `docs/research/llm_grader_calibration_predictions_priority60_adjudicated_20260517.jsonl` |
| metrics JSON | `docs/research/llm_grader_calibration_metrics_priority60_adjudicated_20260517.json` |
| tasks | 60 adjudicated rows × 3 grader types = 180 |
| backend | `kimi_cli` |

## Run Integrity

| check | result |
| --- | --- |
| total tasks | 180 |
| final ok rows | 180 |
| residual error / invalid rows | 0 |
| retry needed | yes, 4 non-ok rows after first full pass |
| average latency | 39.8s/task |
| max latency | 232.8s/task |

Latency by grader:

| grader | n | avg latency | max latency |
| --- | ---: | ---: | ---: |
| `likert_only_judge` | 60 | 25.5s | 112.8s |
| `generic_rubric_judge` | 60 | 41.1s | 232.8s |
| `case_specific_bridge_rubric_judge` | 60 | 52.7s | 193.7s |

## Main Metrics

| grader | n | invalid | unknown | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `likert_only_judge` | 60 | 0.000 | 1.000 | NA | NA/NA/NA | NA | NA | NA | 0.087 | 0.933 |
| `generic_rubric_judge` | 60 | 0.000 | 0.000 | 0.517 | NA/0.000/NA | 1.000 | 0.450 | 0.700 | 0.167 | 0.867 |
| `case_specific_bridge_rubric_judge` | 60 | 0.000 | 0.000 | 0.567 | 0.833/0.312/0.455 | 0.688 | 0.450 | 0.650 | 0.450 | 0.783 |

Critical confusion:

| grader | TP | FP | TN | FN |
| --- | ---: | ---: | ---: | ---: |
| `generic_rubric_judge` | 0 | 0 | 44 | 16 |
| `case_specific_bridge_rubric_judge` | 5 | 1 | 43 | 11 |

`likert_only_judge` does not output leakage / ready fields, so it cannot be used for safety calibration. It only tests holistic score behavior.

## Interpretation

Can write:

- the case-specific bridge-rubric judge detects `major_bridge_leakage` / `answer_leakage` better than the generic rubric judge, because generic recall is 0 on this reference set;
- the case-specific judge also has better overall correlation and MAE than generic and Likert-only judges;
- this supports the value of case-specific rubrics for open-ended tutoring-response evaluation.

Must also write:

- the case-specific judge's critical recall is only 0.3125;
- major leakage false negative rate remains 0.6875;
- student-ready agreement is only 0.45;
- therefore it cannot replace human coaches and should only be used as a scalable auxiliary grader or dev-stage triage signal.

Do not write:

- LLM graders can replace human review;
- the case-specific judge reliably catches all critical bridge leakage;
- priority60 alone completes grader validation;
- LLM grader labels are gold.

## Main Risk

The most important paper risk is false negatives: if an automatic grader marks human-labeled major/answer leakage as non-critical, it will be too optimistic on safety. The case-specific judge is better than the generic judge, but still misses 11/16 critical-positive rows.

This supports the conservative paper wording:

```text
Case-specific bridge rubrics improve auxiliary grading relative to generic rubrics, but human review remains necessary for high-stakes critical-bridge leakage evaluation.
```

## DeepSeek Follow-Up

The DeepSeek-aligned calibration is now complete:

- `llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.md`: 180/180 ok;
- `llm_grader_calibration_metrics_adj_coachA_sample20_deepseek_20260518.md`: 60/60 ok;
- `llm_grader_calibration_metrics_adj_coachB_sample20_deepseek_20260518.md`: 60/60 ok;
- `llm_grader_calibration_deepseek_sensitivity_report_20260518.md`: paper-facing combined interpretation.

Note: the adj+CoachA/B sample20 views contain no human critical-positive rows, so they cannot replace the priority60 critical recall / false-negative analysis.

## Kimi Follow-Up

The follow-up files now exist:

- `llm_grader_calibration_metrics_adj_coachA_sample20_20260518.md`: 60/60 ok;
- `llm_grader_calibration_metrics_adj_coachB_sample20_20260518.md`: 51/60 ok, with 9 Kimi/Moonshot 429 backend errors;
- `llm_grader_calibration_sensitivity_report_20260518.md`: combined interpretation across the three reference views.

These Kimi files are retained only as exploratory/tooling records.
