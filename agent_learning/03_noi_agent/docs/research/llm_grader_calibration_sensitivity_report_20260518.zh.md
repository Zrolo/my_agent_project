# LLM Grader Calibration Kimi Exploratory Sensitivity Report 20260518

## Reviewer-Facing Status

本文件记录的是 `kimi_cli` exploratory/tooling run，不是当前论文主 calibration evidence。当前应进入论文口径的是 DeepSeek-aligned report：

```text
docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md
```

保留本文件的目的只是说明：LLM grader calibration 对 backend 敏感，因此 automatic grader 只能作为 auxiliary signal，不能替代 human review。

## 结论摘要

本轮完成了 `priority60_adjudicated` 主参考口径和 `adj+CoachA sample20` sensitivity；`adj+CoachB sample20` 因 Kimi/Moonshot 429 后端错误仍有 9/60 rows 未成功，因此只作为 partial sensitivity。

最稳的论文结论仍是：

```text
case-specific bridge-rubric judge 相比 generic rubric 更适合作为 scalable auxiliary grader，但它仍有较高 critical false-negative 风险，不能替代人类教练或裁决流程。
```

## Reference Views

| reference view | rows | tasks | status | role |
| --- | ---: | ---: | --- | --- |
| `priority60_adjudicated` | 60 | 180 | 180/180 ok | 主 calibration evidence，含 high-risk / high-disagreement critical positives |
| `adj+CoachA sample20` | 20 | 60 | 60/60 ok | rater-view sensitivity |
| `adj+CoachB sample20` | 20 | 60 | 51/60 ok | partial rater-view sensitivity；9 rows 为 backend 429 |

## Main Metrics

| reference | grader | valid | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| priority60 | `likert_only_judge` | 60/60 | NA | NA/NA/NA | NA | NA | NA | 0.087 | 0.933 |
| priority60 | `generic_rubric_judge` | 60/60 | 0.517 | NA/0.000/NA | 1.000 | 0.450 | 0.700 | 0.167 | 0.867 |
| priority60 | `case_specific_bridge_rubric_judge` | 60/60 | 0.567 | 0.833/0.312/0.455 | 0.688 | 0.450 | 0.650 | 0.450 | 0.783 |
| adj+CoachA sample20 | `likert_only_judge` | 20/20 | NA | NA/NA/NA | NA | NA | NA | 0.311 | 0.600 |
| adj+CoachA sample20 | `generic_rubric_judge` | 20/20 | 0.700 | NA/NA/NA | NA | 0.650 | 0.650 | 0.492 | 0.450 |
| adj+CoachA sample20 | `case_specific_bridge_rubric_judge` | 20/20 | 0.650 | NA/NA/NA | NA | 0.600 | 0.600 | 0.106 | 0.550 |
| adj+CoachB sample20 partial | `likert_only_judge` | 17/20 | NA | NA/NA/NA | NA | NA | NA | 0.439 | 0.647 |
| adj+CoachB sample20 partial | `generic_rubric_judge` | 17/20 | 0.824 | NA/NA/NA | NA | 0.529 | 0.412 | 0.572 | 0.529 |
| adj+CoachB sample20 partial | `case_specific_bridge_rubric_judge` | 17/20 | 0.824 | NA/NA/NA | NA | 0.471 | 0.471 | 0.349 | 0.647 |

## What The Sensitivity Says

`priority60_adjudicated` 是最重要的 reference view，因为它包含 high-risk / high-disagreement rows，并且有 16 个 human critical-positive rows。这里 case-specific bridge-rubric judge 明显优于 generic rubric：generic critical recall 为 0，而 case-specific recall 为 0.312，precision 为 0.833。

但这个优势不能写成“自动 grader 已可靠解决 leakage grading”。case-specific judge 仍漏掉 11/16 个 human critical-positive rows，major leakage false negative rate 为 0.688。对论文来说，这支持“case-specific rubric improves auxiliary grading”而不是“LLM judge replaces human review”。

`adj+CoachA sample20` 与 `adj+CoachB sample20` 主要检查 rater-view sensitivity。这两个 sample20 reference views 没有 human critical-positive rows，因此不能用于 critical recall / false-negative 结论。它们显示 generic 与 case-specific 在 non-critical sample 上的 leakage-label agreement 可接近，但 ready / safe-ready agreement 仍不高，说明 student-ready 与 safe-ready 口径对 rater strictness 仍敏感。

## Paper Wording

可以写：

- case-specific bridge rubrics improve the usefulness of LLM graders as auxiliary dev-stage signals relative to generic rubrics on the high-risk priority60 reference;
- the best auxiliary grader still misses many human critical-positive rows, so human review and adjudication remain necessary;
- rater-view sensitivity remains visible, especially for student-ready and safe-ready labels.

不能写：

- LLM grader 可以替代 human review；
- LLM grader labels 是 gold；
- priority60 足以完成 final automatic-grader validation；
- case-specific judge 已经可靠捕捉所有 critical bridge leakage。

## Remaining Gap

`adj+CoachB sample20` 仍有 9 条 backend 429 error。后续可以用同一 prediction JSONL 和 `--retry-non-ok` 补跑；补齐前，不应把 CoachB sample20 写成 complete calibration result。
