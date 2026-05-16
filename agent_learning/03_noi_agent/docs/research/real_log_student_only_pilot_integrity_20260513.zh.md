# 真实 AIChat student-only pilot 消融完整性检查 20260513

- Manifest: `evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513/manifest.json`
- 期望结果行数：48
- combined JSONL 行数：48
- 有最终回复的行数：46
- 盲评表行数：46
- 可作为完整分析：False
- 可作为 headline 结果：False

## 阻断原因

```json
[
  "empty_final_response_rows"
]
```

解释：本次 run 的 condition-case 组合没有缺失，但有 2 条最终回复为空。因此它可以作为真实日志 pilot 的问题定位材料，但不能作为完整消融结果或论文 headline。

## 警告

```json
[
  "stage_errors_present"
]
```

解释：另有 3 条虽然有最终回复，但某些阶段出现 timeout。它们可以进入 dev 观察，但正式实验需要重跑或在报告中明确标注。

## 空最终回复行

```json
[
  {
    "case_id": "real_aichat_247",
    "condition_id": "dbox_inspired_guard"
  },
  {
    "case_id": "real_aichat_257",
    "condition_id": "edf_inspired_clean"
  }
]
```

## 定向重跑 pair

```json
[
  {
    "case_id": "real_aichat_247",
    "condition_id": "dbox_inspired_guard"
  },
  {
    "case_id": "real_aichat_257",
    "condition_id": "edf_inspired_clean"
  }
]
```

## 定向重跑命令

```bash
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl /Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_ai_prelim_exportable_20260513.jsonl --output-dir evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_targeted_rerun/dbox_inspired_guard --condition-set edf_core --condition-id dbox_inspired_guard --case-id real_aichat_247
python3 -m evals.aichat.run_dev_ablation_suite --input-jsonl /Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_ai_prelim_exportable_20260513.jsonl --output-dir evals/aichat/ad_hoc_runs/real_log_student_only_pilot_20260513_targeted_rerun/edf_inspired_clean --condition-set edf_core --condition-id edf_inspired_clean --case-id real_aichat_257
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

1. 保留本 run 作为 `real-log pilot / dev realism check`；
2. 不把本 run 写成完整比较结果；
3. 若要使用 8 条真实日志做更完整 pilot，应只重跑失败的 2 个 condition-case，或整批重跑一次并通过本完整性检查；
4. 正式 50-case held-out 前，所有 run 都必须通过同类完整性检查。
