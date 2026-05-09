# Tutor Thinking 消融 Smoke 报告 2026-05-09

状态：仅 3 条样本 smoke，不是论文正式结果。

英文版：`docs/research/tutor_thinking_ablation_smoke_report_20260509.md`

## 目的

这次 smoke 用相同的离线研究链路，单独观察 Tutor 生成阶段的延迟：

- `pipeline_mode=tutor_only`
- `tutor_mode=bridge_contract`
- `judge_schema_mode=retrieval_augmented_compact_judge`
- `judge_provider=deepseek`
- `chat_model_provider=deepseek_flash`

唯一变化的实验变量是 Tutor thinking mode：

- `--chat-thinking-mode enabled`
- `--chat-thinking-mode disabled`

## 输入

- Seed 文件：`docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- 样本：`cp_bridge_001`、`cp_bridge_002`、`cp_bridge_003`
- Focus registry：`docs/research/focus_registry_v1.json`

## 命令

```bash
NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=20 python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_enabled_smoke3.jsonl \
  --limit 3 \
  --pipeline-mode tutor_only \
  --tutor-mode bridge_contract \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --judge-provider deepseek \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode enabled \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json

NOI_BRIDGE_JUDGE_TIMEOUT_SECONDS=20 python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_disabled_smoke3.jsonl \
  --limit 3 \
  --pipeline-mode tutor_only \
  --tutor-mode bridge_contract \
  --judge-schema-mode retrieval_augmented_compact_judge \
  --judge-provider deepseek \
  --chat-model-provider deepseek_flash \
  --chat-thinking-mode disabled \
  --max-retries 1 \
  --focus-registry docs/research/focus_registry_v1.json
```

## 结果

| Tutor 模型 | Thinking 模式 | 完成数 | 错误数 | 平均 LLM 调用 | 总延迟 p50 ms | 总延迟 p95 ms | Tutor 延迟范围 ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `deepseek_flash` | `enabled` | 3/3 | 0 | 2.000 | 40918.400 | 41220.855 | 21923.205-35726.892 |
| `deepseek_flash` | `disabled` | 3/3 | 0 | 2.000 | 14081.960 | 16963.281 | 6145.421-10444.663 |

逐样本阶段延迟：

| 样本 | Thinking | 总延迟 ms | Bridge Judge ms | Tutor ms |
| --- | --- | ---: | ---: | ---: |
| `cp_bridge_001` | enabled | 40918.400 | 6342.989 | 34574.247 |
| `cp_bridge_002` | enabled | 28052.861 | 6127.711 | 21923.205 |
| `cp_bridge_003` | enabled | 41220.855 | 5492.550 | 35726.892 |
| `cp_bridge_001` | disabled | 14081.960 | 5644.357 | 8436.996 |
| `cp_bridge_002` | disabled | 16963.281 | 6517.299 | 10444.663 |
| `cp_bridge_003` | disabled | 11663.749 | 5517.083 | 6145.421 |

## 盲评导出

合并后的 JSONL：

```text
evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_enabled_vs_disabled_smoke3.jsonl
```

英文 summary：

```text
evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_enabled_vs_disabled_smoke3_summary.md
```

中文 summary：

```text
evals/aichat/ad_hoc_runs/tutor_thinking_ablation_20260509/bridge_contract_deepseek_flash_enabled_vs_disabled_smoke3_summary.zh.md
```

盲评表：

```text
docs/research/coach_response_review_workbook_deepseek_flash_thinking_smoke3.csv
```

Key 文件，不能给盲评教练看：

```text
docs/research/coach_response_review_workbook_deepseek_flash_thinking_smoke3.key.csv
```

## 解释

这次 smoke 说明：即使 LLM 调用次数相同，Tutor thinking mode 也可能显著影响延迟。两个条件下每条样本都是 2 次 LLM 调用：Bridge Judge + Tutor。Bridge Judge 基本稳定在 5.5-6.5 秒，而 Tutor 阶段差异很大。

`thinking=disabled` 在这次小批中明显更快，但不能只根据延迟决定线上默认模式。下一步必须用盲评表检查它是否降低脚手架质量，或者是否更容易泄露关键桥梁。

## 下一步

请先用盲评表评价回复质量，再决定是否调整线上 AIChat 的默认策略。建议评分维度：

- 是否贴合当前缺失桥梁；
- 脚手架强度是否合适；
- 是否控制关键桥梁泄露；
- 下一步行动是否清楚；
- 是否保持单焦点；
- 整体教练偏好。

不要仅凭延迟把 `thinking=disabled` 提升为线上默认。
