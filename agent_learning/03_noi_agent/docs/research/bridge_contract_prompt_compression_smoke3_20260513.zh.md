# Bridge Contract Prompt 压缩 Smoke3 结果（2026-05-13）

## 目的

本次 smoke 用 3 个 dialogue-state v3 dev case 检查 prompt 压缩条件是否能正常运行，并初步观察压缩是否改善自然度和学生可用性。该结果是 AI 自评开发筛查，不是教练 gold label，也不是论文正式结论。

## 条件

```text
dbox_inspired_guard
bridge_contract_guard
bridge_contract_compact_guard
bridge_contract_minimal_guard
```

运行输出：

```text
evals/aichat/ad_hoc_runs/prompt_compression_smoke3_20260513/
```

## 完整性检查

```text
case_count = 3
condition_count = 4
combined_row_count = 12
final_response_row_count = 12
review_row_count = 12
empty_final_response_rows = 0
stage_warning_rows = 0
headline_ready = true
analysis_ready = true
```

## AI 自评摘要

| condition | overall | core6 | student_ready_pass | minor leakage | major/answer leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| bridge_contract_guard | 4.00 | 2.00 | 3/3 | 0 | 0 |
| bridge_contract_compact_guard | 3.67 | 1.94 | 2/3 | 1 | 0 |
| bridge_contract_minimal_guard | 3.67 | 1.94 | 2/3 | 1 | 0 |
| dbox_inspired_guard | 3.33 | 1.89 | 1/3 | 2 | 0 |

## 初步解释

压缩 prompt 已经能稳定生成可评分回复，且运行结构完整。但在这 3 个状态/表示类 case 上，long `bridge_contract_guard` 并没有被 compact/minimal 超过；AI 自评反而显示 long 版在 student-ready 和 leakage 控制上更稳。

因此当前不能直接把 compact/minimal 替换为默认 Bridge Contract prompt。更合理的下一步是：

1. 保留 long prompt 作为当前 dev baseline。
2. 用 `prompt_compression` condition set 扩到 10-case dev ablation。
3. 重点看 compact/minimal 是否在非状态类 case 上提升自然度。
4. 如果 compact/minimal 的 minor/major leakage 上升，就不要进入正式 held-out 主表。

## 重要边界

本次结果不证明 long prompt 最优，也不证明 compact prompt 无效。它只说明：在小样本状态/表示类 smoke 中，prompt 压缩没有立即带来明显质量优势，且可能削弱防泄露控制。
