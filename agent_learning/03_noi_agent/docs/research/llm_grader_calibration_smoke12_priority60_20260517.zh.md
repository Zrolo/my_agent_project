# LLM Grader Calibration Smoke12 Priority60 20260517

## 状态

这是 LLM grader calibration 的工具链 smoke，不是正式 calibration report。目的只是确认：

- prompt pack 可以被固定 backend 执行；
- 输出可以解析为 JSON；
- strict schema 能拦截越界评分；
- summarizer 可以按 grader type 输出指标。

## 输入

| item | value |
| --- | --- |
| prompt pack | `docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl` |
| output predictions | `docs/research/llm_grader_calibration_predictions_priority60_smoke12_20260517.jsonl` |
| metrics JSON | `docs/research/llm_grader_calibration_smoke12_metrics_priority60_20260517.json` |
| selected tasks | first 12 tasks |
| effective rows per grader | 4 |
| backend | `kimi_cli` |

## 重要修正

第一轮 smoke 中，generic / case-specific judge 虽能返回 JSON，但出现了 `overall_quality = 7/8` 和 `scaffold_sufficiency` 超出 0-2 的输出。为避免静默污染指标，本轮完成两项修正：

1. `run_llm_grader_calibration.py` 增加 strict schema validation；
2. `prepare_llm_grader_calibration_pack.py` 将 grader prompt 的输出范围写得更明确：
   - `overall_quality` 只能是 1-5；
   - `scaffold_sufficiency` 只能是 0-2；
   - categorical fields 必须使用枚举值。

之后重跑 smoke，并用 `--retry-non-ok` 补掉 1 条 transient backend timeout。

## Smoke 结果

| grader | n | valid_n | status | invalid rate | overall MAE | leakage acc | student-ready agreement | safe-ready agreement |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `likert_only_judge` | 4 | 4 | 4 ok | 0.000 | 0.750 | NA | NA | NA |
| `generic_rubric_judge` | 4 | 4 | 4 ok | 0.000 | 0.750 | 0.750 | 0.750 | 0.750 |
| `case_specific_bridge_rubric_judge` | 4 | 4 | 4 ok | 0.000 | 0.750 | 0.750 | 0.500 | 0.750 |

Latency:

- average latency: 37.4s/task；
- max latency: 84.7s/task；
- case-specific / generic rows may be slow enough that full calibration should use resume + retry.

## 解释边界

不能从本 smoke 写出任何论文结论。原因：

- 每个 grader 只有 4 条有效样本；
- 样本来自 pack 开头，不是 stratified sample；
- 当前 12 条没有 human critical-positive row，因此 critical precision / recall / F1 都无法估计；
- Likert-only judge 本来不输出 leakage / ready 字段，所以只适合看 overall score behavior。

可以写入内部方法记录：

```text
A 12-task smoke confirmed that the grader runner, strict schema validation, retry path, and summarizer work end to end. The smoke is not used as calibration evidence.
```

## 下一步

正式 calibration 仍需完整运行：

1. `priority60_adjudicated` 180 tasks；
2. `adj+CoachA sample20` 60 tasks；
3. `adj+CoachB sample20` 60 tasks。

运行时应使用：

```bash
python3 -m evals.aichat.run_llm_grader_calibration \
  --pack-jsonl docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl \
  --output-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_20260517.jsonl \
  --backend kimi_cli \
  --judge-timeout-seconds 240
```

如果中途有 timeout 或 invalid rows：

```bash
python3 -m evals.aichat.run_llm_grader_calibration \
  --pack-jsonl docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl \
  --output-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_20260517.jsonl \
  --backend kimi_cli \
  --retry-non-ok \
  --judge-timeout-seconds 240
```
