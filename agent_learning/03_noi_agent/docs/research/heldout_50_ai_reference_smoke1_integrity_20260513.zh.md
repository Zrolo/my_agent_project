# Held-out 50 AI Reference Smoke1 完整性检查（2026-05-13）

## 总览

- Manifest：`evals/aichat/ad_hoc_runs/heldout_50_ai_reference_smoke1_20260513/manifest.json`
- Combined JSONL：`evals/aichat/ad_hoc_runs/heldout_50_ai_reference_smoke1_20260513/combined_dev_ablation.jsonl`
- Review CSV：`evals/aichat/ad_hoc_runs/heldout_50_ai_reference_smoke1_20260513/coach_response_review_workbook_dev_ablation.csv`
- Case 数：1
- Condition 数：8
- 预期行数：8
- 实际 combined 行数：8
- final response 行数：8
- review workbook 行数：8
- analysis_ready：true
- headline_ready：true

## 条件集

- `current_system_deployment`
- `enhanced_prompt_only_clean`
- `codehelp_codeaid_clean`
- `dbox_inspired_guard`
- `bridge_inspired_expert_decision_clean`
- `single_llm_structured_guard`
- `bridge_contract_guard`
- `bridge_contract_guard_repair`

## Blocking Reasons

```json
[]
```

## Warnings

```json
[]
```

## Empty Final Response Rows

```json
[]
```

## Targeted Rerun Pairs

```json
[]
```

## 结论

这次 `heldout_main` 1-case smoke 通过完整性检查。它只说明主实验 8 个条件在 AI-assisted draft reference 输入格式上能正常产出回复和盲评表，不是正式 50-case 结果。

下一步可以选择：

1. 继续跑 50-case × 8 conditions 的完整 dev generation；
2. 或先人工看这 8 条 smoke 回复，确认回复质量和盲评表字段没有明显问题，再开完整运行。
