# 50-case AI Draft Reference Dev Run 原始完整性报告

## 结论

原始 `heldout_main` 全量 dev run 未通过完整性检查，不能直接用于分析或盲评。

失败原因不是缺少 case-condition 组合，也不是模型整体失败，而是 1 行 guard-only block 导致 `final_response_text` 为空。

## Run 信息

- Manifest: `evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513/manifest.json`
- 预期行数: 400
- 合并行数: 400
- 有最终回复行数: 399
- 盲评表行数: 400
- analysis ready: false
- headline ready: false

## 阻塞原因

- `empty_final_response_rows`
- `review_row_count_mismatch`

## 空最终回复行

- `heldout_cp_015` × `bridge_contract_guard`

## 处理方式

该问题已通过 runner 修正和定向补跑解决。合并后的可用 run 见：

- `evals/aichat/ad_hoc_runs/heldout_50_ai_reference_dev_20260513_merged/manifest.json`
- [heldout_50_ai_reference_dev_merged_integrity_20260513.zh.md](heldout_50_ai_reference_dev_merged_integrity_20260513.zh.md)

## 说明

保留本报告是为了记录 dev run 的失败原因和修复过程。后续分析应使用 merged run，而不是这个原始 run。
