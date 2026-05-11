# Dev Ablation Suite Smoke Report 20260511

中文报告。英文版见 [dev_ablation_suite_smoke_report_20260511.md](dev_ablation_suite_smoke_report_20260511.md)。

## 目的

本 smoke 只验证 P1 dev ablation 工具链是否能端到端运行，不作为论文结论。

它检查：

- `enhanced_prompt_only` 是否已经进入 shared offline runner；
- DBox-inspired、DBox-inspired + Guard、Bridge Contract 等条件是否能在同一 suite 中运行；
- suite 是否能生成 per-condition JSONL、combined JSONL、双语 summary、匿名盲评 CSV、key CSV 和中文 XLSX；
- DBox-inspired 的结构化输出是否能被稳定解析。

## 命令

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1 \
  --limit 1 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 0
```

随后针对 DBox + Guard 解析不稳定问题，用 `--max-retries 1` 单独重跑：

```bash
python3 - <<'PY'
from pathlib import Path
from evals.aichat.run_dev_ablation_suite import run_dev_ablation_suite

run_dev_ablation_suite(
    input_jsonl=Path("docs/research/bridgebench_cp_seed_v2_gold_20.jsonl"),
    output_dir=Path("evals/aichat/ad_hoc_runs/dev_ablation_20260511_dbox_guard_retry_smoke1"),
    conditions=[{
        "condition_id": "dbox_inspired_guard",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    }],
    limit=1,
    chat_model_provider="deepseek_flash",
    judge_provider="deepseek",
    max_retries=1,
)
PY
```

## 输出

主 smoke 输出目录：

- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/manifest.json`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/combined_dev_ablation.jsonl`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/combined_dev_ablation_summary.json`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/combined_dev_ablation_summary.md`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/combined_dev_ablation_summary.zh.md`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/coach_response_review_workbook_dev_ablation.csv`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/coach_response_review_workbook_dev_ablation.key.csv`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/coach_response_review_workbook_dev_ablation.zh.xlsx`

DBox + Guard retry smoke 输出目录：

- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_dbox_guard_retry_smoke1/manifest.json`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_dbox_guard_retry_smoke1/combined_dev_ablation.jsonl`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_dbox_guard_retry_smoke1/coach_response_review_workbook_dev_ablation.zh.xlsx`

## 结果摘要

主 smoke：

- case count: 1
- condition count: 11
- combined rows: 11
- completed rows: 9
- review workbook rows: 9
- stage errors: 2 个 DBox-inspired tutor 解析错误

初次失败原因：

```text
ValueError: invalid decomposition status at item 1: known
```

原因是模型把 DBox decomposition node status 写成 `known`，而旧 validator 只接受 `known_or_not_relevant`、`current_stuck_step`、`defer`。

修正：

- validator 现在会把常见别名规范化：
  - `known` -> `known_or_not_relevant`
  - `current` / `missing` / `stuck` -> `current_stuck_step`
  - `deferred` / `future` / `later` -> `defer`

修正后：

- `dbox_inspired_clean` 能正常输出 decomposition trace 和学生回复；
- `dbox_inspired_guard` 在 `max_retries=1` 下成功完成；
- DBox + Guard retry smoke 输出 `final_response_source=candidate`、`safe_action=pass`、`llm_call_count=3`。

## 延迟观察

主 smoke 的单 case 全矩阵已经很慢：

- p50 total latency: 55155 ms
- p95 total latency: 244735 ms

这进一步支持当前路线：

```text
10-20 case dev ablation 必须作为离线批处理运行；
full multi-stage pipeline 不应进入线上默认路径；
论文必须报告 latency / LLM call count。
```

## 结论

本 smoke 验证了：

1. `run_dev_ablation_suite.py` 能生成 P1 dev ablation 所需的完整评测包；
2. `enhanced_prompt_only` 已经可以和 literature-inspired baselines、Bridge Contract variants 放在同一 runner 中比较；
3. DBox-inspired 结构字段需要做轻量规范化，否则真实模型输出会因小别名漂移导致整行失败；
4. 下一步可以运行 10-20 case dev ablation，但要使用 `--max-retries 1`，并预期运行时间较长。

本报告不证明任何系统优劣，只说明工具链已经准备好进入小规模 dev ablation。
