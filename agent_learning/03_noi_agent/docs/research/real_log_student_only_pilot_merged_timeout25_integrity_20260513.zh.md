# 真实 AIChat student-only timeout25 merged pilot 完整性检查 20260513

- Manifest: `evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_merged_timeout25/manifest.json`
- 期望结果行数：48
- combined JSONL 行数：48
- 有最终回复的行数：48
- 盲评表行数：48
- 可作为完整 dev 分析：True
- 可作为本轮 pilot 的 headline：True

## 阻断原因

```json
[]
```

## 警告

```json
[]
```

解释：在保持 max token 默认值不变的前提下，只将 leakage judge timeout 提高到 25 秒并定向重跑 3 个 stage warning pair 后，merged run 已无缺行、无空最终回复、无 stage warning。

## 重跑配置

```text
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25
max token: 使用当前默认值，不额外设置
chat model provider: deepseek_flash
judge provider: deepseek
chat thinking mode: disabled
condition set: edf_core
```

## 被替换的 pair

```json
[
  {
    "case_id": "real_aichat_1293",
    "condition_id": "dbox_inspired_guard"
  },
  {
    "case_id": "real_aichat_247",
    "condition_id": "edf_inspired_guard"
  },
  {
    "case_id": "real_aichat_249",
    "condition_id": "bridge_contract_guard_repair"
  }
]
```

## 解释边界

这说明本轮 timeout 更像是 request timeout / provider latency / timeout budget 问题，而不是 max token budget 问题。该 run 可以作为真实日志 8-case pilot 的完整 dev 分析包，但仍不能替代正式 50-case held-out、教练标注和 judge calibration。
