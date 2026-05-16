# 真实 AIChat student-only merged pilot 消融完整性检查 20260513

- Manifest: `evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_merged/manifest.json`
- 期望结果行数：48
- combined JSONL 行数：48
- 有最终回复的行数：48
- 盲评表行数：48
- 可作为完整 dev 分析：True
- 可作为 headline 结果：False

## 阻断原因

```json
[]
```

解释：定向补跑已经替换了原 run 中 2 条空最终回复；merged run 不再存在缺行、重复 pair 或空最终回复。

## 警告

```json
[
  "stage_errors_present"
]
```

解释：仍有 3 条虽然有最终回复，但某些阶段出现 timeout。它们可以进入 dev 观察和 AI 预评，但不能作为论文 headline 或正式 held-out 结果。

## 空最终回复行

```json
[]
```

## 定向重跑 pair

```json
[]
```

## 阶段错误警告行

```json
[
  {
    "case_id": "real_aichat_1293",
    "condition_id": "dbox_inspired_guard",
    "stage_errors": {
      "leakage_judge": "APITimeoutError: Request timed out."
    }
  },
  {
    "case_id": "real_aichat_247",
    "condition_id": "edf_inspired_guard",
    "stage_errors": {
      "leakage_judge": "APITimeoutError: Request timed out."
    }
  },
  {
    "case_id": "real_aichat_249",
    "condition_id": "bridge_contract_guard_repair",
    "stage_errors": {
      "leakage_judge": "APITimeoutError: Request timed out."
    }
  }
]
```

## 处理建议

1. merged run 可以作为真实日志 student-only pilot 的完整 dev 分析包；
2. 报告中必须保留 `AI self-review / dev realism check` 标注；
3. 若要作为更干净的 dev 报告，可继续定向重跑 3 条 stage warning pair；
4. 正式 50-case held-out 前，所有 run 都必须无 blocking reasons，并尽量无 stage warning。
