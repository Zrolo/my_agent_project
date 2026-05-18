# LLM Grader Calibration Plan Or Report 20260517

## 当前状态

当前是 calibration plan + DeepSeek completed report 状态：`priority60_adjudicated`、`adj+CoachA sample20` 和 `adj+CoachB sample20` 都已有 DeepSeek-backed prediction / metrics。早先 `kimi_cli` 结果仅保留为 exploratory/tooling 记录，不作为论文主 calibration evidence。仓库已有 prompt-pack 生成脚本：

```text
evals/aichat/prepare_llm_grader_calibration_pack.py
```

本轮新增离线 runner 与汇总脚本：

```text
evals/aichat/run_llm_grader_calibration.py
evals/aichat/summarize_llm_grader_calibration.py
```

`run_llm_grader_calibration.py` 只有在显式执行非 dry-run 时才会调用 judge backend；`summarize_llm_grader_calibration.py` 只汇总已有 prediction JSONL。它们不替代人类评分。LLM grader 只能作为 scalable auxiliary grader。

本轮已生成固定 prompt packs，并已运行其中三个 reference views：

| pack | reference rows | grader tasks |
| --- | ---: | ---: |
| `llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl` | 60 | 180 |
| `llm_grader_calibration_pack_adj_coachA_sample20_20260517.jsonl` | 20 | 60 |
| `llm_grader_calibration_pack_adj_coachB_sample20_20260517.jsonl` | 20 | 60 |

对应 reference files：

- `llm_grader_calibration_reference_priority60_adjudicated_20260517.jsonl`
- `llm_grader_calibration_reference_adj_coachA_sample20_20260517.jsonl`
- `llm_grader_calibration_reference_adj_coachB_sample20_20260517.jsonl`

`adj_coachB_sample20` 的原始 label rows 缺少部分题面与 case-specific rubric 字段；本轮用 `adj_coachA_sample20` 中同 case / condition 的非标签上下文字段补齐。该步骤只补 prompt context，不改变 Coach B 的评分标签。

## 待比较的三种 judge

| judge | 输入 | 目的 |
| --- | --- | --- |
| `likert_only_judge` | problem / student message / response + Likert prompt | 检查单纯整体评分是否足够 |
| `generic_rubric_judge` | 通用 tutor rubric | 检查没有 case-specific bridge 信息时的上限 |
| `case_specific_bridge_rubric_judge` | success criteria、forbidden content、critical boundary、acceptable reveal、expected next action | 检查 case-specific bridge rubric 是否更接近人审 |

## 参考标签

| reference | 用途 |
| --- | --- |
| `priority60 adjudicated labels` | 高分歧、高风险、小 N；最接近裁决 reference |
| `priority60 adjudicated + Coach A labels` | 主论文结果口径 |
| `priority60 adjudicated + Coach B labels` | rater strictness sensitivity |
| Coach A only / Coach B only | 可选，用于观察 grader 是否偏向某一位教练 |

## 指标

| metric | 解释 |
| --- | --- |
| overall agreement / correlation | overall Pearson / Spearman / MAE |
| leakage label accuracy | 四类 leakage label 一致率 |
| critical binary precision / recall / F1 | major/answer vs non-critical 的二值指标 |
| major leakage false negative rate | 人类为 major/answer，grader 判非 critical 的比例 |
| student-ready agreement | ready yes/borderline/no 一致率 |
| safe-ready agreement | ready 且 no leakage 的一致率 |
| unknown / low-confidence rate | grader 输出 UNKNOWN 或低置信比例 |

## 最小执行流程

1. 用 `prepare_llm_grader_calibration_pack.py` 生成三类 judge prompt pack。
2. 固定模型、温度、输出 JSON schema，并记录失败/UNKNOWN。
3. 用 `run_llm_grader_calibration.py` 把模型输出解析成 `grader_prediction` 字段。
4. 用 `summarize_llm_grader_calibration.py` 汇总指标。
5. 分别报告 priority60-only、adj+CoachA、adj+CoachB。

若 labels JSONL 缺少题面或 rubric 字段，必须用 `--context-jsonl` 从同一批 case 的完整 reference 中补齐 prompt context；不能让某个 rater view 因上下文缺失而被低估。

### Runner dry-run

在正式调用模型前，先干跑检查 pack 行数、已有输出和第一条任务：

```bash
python3 -m evals.aichat.run_llm_grader_calibration \
  --pack-jsonl docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl \
  --output-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_deepseek_20260518.jsonl \
  --dry-run \
  --limit 3
```

正式小批量 smoke 建议先跑 6-12 个 task，确认 JSON schema 和 UNKNOWN 行为后再扩展：

```bash
python3 -m evals.aichat.run_llm_grader_calibration \
  --pack-jsonl docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl \
  --output-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_deepseek_20260518.jsonl \
  --backend deepseek \
  --limit 12 \
  --judge-timeout-seconds 240
```

汇总命令：

```bash
python3 -m evals.aichat.summarize_llm_grader_calibration \
  --predictions-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_deepseek_20260518.jsonl \
  --output-json docs/research/llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.json \
  --output-md docs/research/llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.md
```

## 结果解释规则

可以写：

```text
The case-specific bridge-rubric grader is evaluated as a scalable auxiliary grader against coach/adjudicated references.
```

只有当指标支持时，才能写：

```text
The case-specific bridge-rubric grader better matches coach/adjudicated labels than likert-only or generic-rubric graders.
```

不能写：

```text
LLM grader replaces human review.
LLM grader labels are gold.
Priority60 is sufficient as final automatic-grader validation.
```

## 当前缺口

当前 DeepSeek-backed 三个 reference views 都已完成。Kimi-backed `20260518` 无 `_deepseek_` 后缀结果是 exploratory/tooling run，不能作为论文主 calibration evidence。

## Smoke12 更新

已完成 `priority60_adjudicated` pack 前 12 个 tasks 的工具链 smoke：

- 输出文件：`docs/research/llm_grader_calibration_predictions_priority60_smoke12_20260517.jsonl`
- 指标文件：`docs/research/llm_grader_calibration_smoke12_metrics_priority60_20260517.json`
- 说明文档：`docs/research/llm_grader_calibration_smoke12_priority60_20260517.zh.md`

第一次 smoke 暴露了 schema 风险：部分 generic / case-specific judge 输出 7/8 分或超出 0-2 的 scaffold 分。已修复：

- runner 增加 strict schema validation；
- summarizer 排除 non-ok rows 并报告 invalid rate；
- runner 增加 `--retry-non-ok`；
- prompt pack 明确 `overall_quality` 只能 1-5，`scaffold_sufficiency` 只能 0-2。

重跑后 smoke12 的 12/12 rows 均为 `ok`，invalid rate 为 0。该 smoke 只能证明工具链可运行，不能作为论文 calibration evidence。下一步是完整运行 priority60-only、adj+CoachA sample20 和 adj+CoachB sample20 三个 pack。

## Kimi Exploratory 结果更新

以下 `kimi_cli` 结果只作为 exploratory/tooling 记录，因为它不符合主实验固定 DeepSeek judge stack 的模型配置。

已完成 `priority60_adjudicated` 60-row × 3 judge = 180 tasks：

- prediction 文件：`docs/research/llm_grader_calibration_predictions_priority60_adjudicated_20260517.jsonl`
- metrics 文件：`docs/research/llm_grader_calibration_metrics_priority60_adjudicated_20260517.json`
- 报告：`docs/research/llm_grader_calibration_priority60_report_20260517.zh.md`

完整性：

- 180/180 rows 最终 `ok`；
- 第一轮 full pass 后有 4 条 non-ok，经 `--retry-non-ok` 全部补齐；
- 平均延迟约 39.8s/task，最大延迟约 232.8s/task。

主要指标：

| grader | leakage acc | critical P/R/F1 | major FN | overall r | overall MAE |
| --- | ---: | --- | ---: | ---: | ---: |
| `likert_only_judge` | NA | NA/NA/NA | NA | 0.087 | 0.933 |
| `generic_rubric_judge` | 0.517 | NA/0.000/NA | 1.000 | 0.167 | 0.867 |
| `case_specific_bridge_rubric_judge` | 0.567 | 0.833/0.312/0.455 | 0.688 | 0.450 | 0.783 |

结论：Kimi exploratory run 中 case-specific bridge-rubric judge 优于 generic rubric；但该结果不能作为论文主 calibration evidence。它主要说明 LLM grader calibration 对 backend 敏感。

## DeepSeek Sensitivity 更新 20260518

已用 DeepSeek offline judge profile 补跑全部 reference views：

| reference view | tasks | status | report |
| --- | ---: | --- | --- |
| `priority60_adjudicated` | 180 | 180/180 ok | `docs/research/llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.zh.md` |
| `adj+CoachA sample20` | 60 | 60/60 ok | `docs/research/llm_grader_calibration_metrics_adj_coachA_sample20_deepseek_20260518.zh.md` |
| `adj+CoachB sample20` | 60 | 60/60 ok | `docs/research/llm_grader_calibration_metrics_adj_coachB_sample20_deepseek_20260518.zh.md` |

综合报告见：

```text
docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.zh.md
```

解释边界：

- `priority60_adjudicated` 仍是 critical leakage calibration 的主口径，因为它包含 16 个 human critical-positive rows；
- DeepSeek-backed case-specific judge 改善了一些辅助指标，但 priority60 上 critical recall 仍为 0，major leakage false-negative rate 为 1.000；
- `adj+CoachA/B sample20` 没有 human critical-positive rows，因此不能用于 critical recall / false-negative 结论；
- 当前结论仍是 LLM grader 只能作为 dev-stage auxiliary signal，不能替代 human review / adjudication。
