# LLM Grader Calibration DeepSeek Sensitivity Report 20260518

## 状态

本报告是当前应进入论文口径的 LLM grader calibration 结果。它使用 DeepSeek offline judge profile：

```text
backend = deepseek
model = deepseek-v4-flash
thinking = disabled
```

这与主实验的 Bridge Judge / Leakage Guard / Repair stack 对齐。此前无 `_deepseek_` 后缀的 `20260518` calibration 结果来自 `kimi_cli`，只能作为 exploratory/tooling smoke，不应作为论文主 calibration evidence。

## Run Integrity

| reference view | rows | tasks | backend | status | role |
| --- | ---: | ---: | --- | --- | --- |
| `priority60_adjudicated` | 60 | 180 | DeepSeek | 180/180 ok | 主 critical-leakage calibration view |
| `adj+CoachA sample20` | 20 | 60 | DeepSeek | 60/60 ok | rater-view sensitivity |
| `adj+CoachB sample20` | 20 | 60 | DeepSeek | 60/60 ok | rater-view sensitivity |

## Main Metrics

| reference | grader | valid | leakage acc | critical P/R/F1 | major FN | ready agreement | safe-ready agreement | overall r | overall MAE |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| priority60 | `likert_only_judge` | 60/60 | NA | NA/NA/NA | NA | NA | NA | 0.129 | 1.200 |
| priority60 | `generic_rubric_judge` | 60/60 | 0.583 | NA/0.000/NA | 1.000 | 0.433 | 0.400 | -0.140 | 1.033 |
| priority60 | `case_specific_bridge_rubric_judge` | 60/60 | 0.617 | NA/0.000/NA | 1.000 | 0.467 | 0.533 | 0.167 | 1.033 |
| adj+CoachA sample20 | `likert_only_judge` | 20/20 | NA | NA/NA/NA | NA | NA | NA | 0.203 | 0.850 |
| adj+CoachA sample20 | `generic_rubric_judge` | 20/20 | 0.700 | NA/NA/NA | NA | 0.550 | 0.500 | 0.057 | 0.700 |
| adj+CoachA sample20 | `case_specific_bridge_rubric_judge` | 20/20 | 0.650 | NA/NA/NA | NA | 0.650 | 0.700 | 0.645 | 0.550 |
| adj+CoachB sample20 | `likert_only_judge` | 20/20 | NA | NA/NA/NA | NA | NA | NA | 0.170 | 1.000 |
| adj+CoachB sample20 | `generic_rubric_judge` | 20/20 | 0.800 | NA/NA/NA | NA | 0.450 | 0.400 | -0.006 | 0.700 |
| adj+CoachB sample20 | `case_specific_bridge_rubric_judge` | 20/20 | 0.900 | NA/NA/NA | NA | 0.450 | 0.550 | 0.040 | 0.950 |

## Interpretation

`priority60_adjudicated` 仍是最重要的 reference view，因为它包含 16 个 human critical-positive rows。DeepSeek-backed case-specific bridge-rubric judge 相比 generic rubric 有更高的 leakage-label accuracy（0.617 vs 0.583）、student-ready agreement（0.467 vs 0.433）和 safe-ready agreement（0.533 vs 0.400），说明 case-specific rubric 仍有辅助价值。

但最关键的安全指标不够好：generic 和 case-specific DeepSeek grader 的 critical recall 都是 0，major leakage false-negative rate 都是 1.000。也就是说，在 priority60 这批高风险/高分歧样本上，DeepSeek 自动 grader 没有抓住人类裁决为 `major_bridge_leakage` / `answer_leakage` 的 rows。

因此论文不能写 “LLM grader 可以替代 human review”。更准确的写法是：

```text
Case-specific bridge rubrics improve some auxiliary grading signals over a generic rubric, but DeepSeek-backed LLM graders still fail to recover human critical-positive leakage labels on the high-risk priority60 reference. Human review and adjudication remain necessary.
```

## Rater-View Sensitivity

`adj+CoachA sample20` 与 `adj+CoachB sample20` 都没有 human critical-positive rows，因此不能用来估 critical recall / F1。它们只说明：

- case-specific judge 在 CoachA sample20 上 overall r 较高（0.645）且 MAE 较低（0.550）；
- case-specific judge 在 CoachB sample20 上 leakage-label accuracy 较高（0.900），但 ready agreement 与 overall r 仍弱；
- ready / safe-ready 仍受 rater strictness 影响，不能只报单一 rater view。

## Kimi Exploratory Result Boundary

此前生成的 `kimi_cli` calibration 结果可以保留为工具链探索记录，但不能与 DeepSeek 主实验 calibration 混报：

- Kimi priority60 case-specific judge 曾有 critical recall 0.312；
- DeepSeek priority60 case-specific judge critical recall 为 0；
- 这个差异说明 LLM grader calibration 对 judge backend 敏感；
- 因此论文更应该强调 automatic grader 只是 auxiliary signal，而不是 gold。

## Paper Wording

可以写：

- case-specific bridge rubric 在 DeepSeek 上改善了部分 auxiliary grading 指标；
- priority60 上 critical false-negative 风险仍很高；
- automatic LLM grader 不能替代 double human review / adjudication；
- LLM grader calibration 对 backend 敏感，因此论文主结果必须依赖人审。

不能写：

- DeepSeek LLM grader 已能可靠识别 critical bridge leakage；
- case-specific judge 可以替代人类教练；
- Kimi exploratory result 是主实验 calibration；
- LLM grader labels 是 gold。
