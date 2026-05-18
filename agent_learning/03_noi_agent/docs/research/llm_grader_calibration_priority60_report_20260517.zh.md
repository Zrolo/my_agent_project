# LLM Grader Calibration Priority60 Report 20260517

## 状态

这是 `kimi_cli` backend 下的 `priority60_adjudicated` exploratory/tooling 结果，不是当前论文主 calibration evidence。当前应进入论文口径的是 DeepSeek-aligned report：`llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md`。

保留本文件的价值是说明 LLM grader calibration 对 backend 敏感：Kimi exploratory run 中 case-specific judge 有一定 critical recall，而 DeepSeek-backed run 在 priority60 上 critical recall 为 0。这进一步支持 “automatic grader 只能作为 auxiliary signal，不能替代 human review”。

LLM grader 仍只能作为 scalable auxiliary grader，不能替代人类教练或裁决标签。

## 输入与输出

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

`likert_only_judge` 不输出 leakage / ready 字段，因此不能用于 safety calibration，只能观察 overall score behavior。

## 解释

可以写：

- case-specific bridge-rubric judge 明显比 generic rubric 更能识别 `major_bridge_leakage` / `answer_leakage`，因为 generic 在本参考集上 critical recall 为 0；
- case-specific judge 的 overall correlation 和 MAE 也优于 generic 与 Likert-only；
- 这说明 case-specific rubric 对开放式 tutoring response evaluation 有帮助。

必须同时写：

- case-specific judge 的 critical recall 只有 0.3125；
- major leakage false negative rate 仍为 0.6875；
- student-ready agreement 只有 0.45；
- 因此它不能替代人类教练，最多作为 scalable auxiliary grader 或 dev-stage triage signal。

不能写：

- LLM grader 可以替代 human review；
- case-specific judge 已经可靠捕捉所有 critical bridge leakage；
- priority60 alone 足以完成 grader validation；
- LLM grader labels 是 gold。

## 主要风险

对论文最重要的风险是 false negative：如果自动 grader 把人类标为 major/answer leakage 的回复判成 non-critical，它会在安全维度上过于乐观。当前 case-specific judge 虽然比 generic 好，但仍漏掉 11/16 个 critical-positive rows。

这支持论文中的保守口径：

```text
Case-specific bridge rubrics improve auxiliary grading relative to generic rubrics, but human review remains necessary for high-stakes critical-bridge leakage evaluation.
```

## DeepSeek Follow-Up

已完成 DeepSeek-aligned calibration：

- `llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.zh.md`：180/180 ok；
- `llm_grader_calibration_metrics_adj_coachA_sample20_deepseek_20260518.zh.md`：60/60 ok；
- `llm_grader_calibration_metrics_adj_coachB_sample20_deepseek_20260518.zh.md`：60/60 ok；
- `llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md`：论文主口径综合解释。

注意：adj+CoachA/B sample20 没有 human critical-positive rows，因此不能取代 priority60 中的 critical recall / false-negative 分析。

## Kimi Follow-Up

后续已生成：

- `llm_grader_calibration_metrics_adj_coachA_sample20_20260518.zh.md`：60/60 ok；
- `llm_grader_calibration_metrics_adj_coachB_sample20_20260518.zh.md`：51/60 ok，9 条为 Kimi/Moonshot 429 backend error；
- `llm_grader_calibration_sensitivity_report_20260518.zh.md`：三种 reference view 的综合解释。

这些 Kimi 文件只保留为 exploratory/tooling record。
