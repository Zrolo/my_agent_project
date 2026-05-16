# Dialogue-State v3 主实验生成完整性记录（2026-05-16）

## 结论

Dialogue-state v3 reviewed-candidate 50-case 已完成主实验回复生成与完整性修复。最终合并后的主实验包包含：

- 50 条 reviewed-candidate case；
- 7 个主表 condition；
- 350 条 case-condition 回复；
- 350 条可进入盲评表的目标 AI 回复；
- 无缺失 pair；
- 无重复 pair；
- 无空 `final_response_text`；
- 无 stage warning。

因此，本生成包可以进入后续人类教练 response blind review。它仍然不是实验结论，也不表示任何 condition 已经胜出。

## 主实验 Condition

主表固定为 7 个 condition：

1. `enhanced_prompt_only_clean`
2. `codehelp_codeaid_clean`
3. `dbox_inspired_clean`
4. `dbox_inspired_guard`
5. `bridge_guided_dbox_style_guard`
6. `bridge_contract_compact_guard`
7. `bridge_contract_compact_guard_repair`

这些 condition 来自 `dialogue_state_v3_prompt_rubric_freeze_gate_20260516` 中固定的 reviewed-candidate response generation plan。

## 生成与修复过程

初次主实验运行目录：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516/
```

初次运行完成 350 条 combined rows，但有 11 条空 `final_response_text`，因此不能直接进入盲评。随后按 integrity checker 给出的 pair 做 targeted rerun，并将成功补跑结果合并为新的 run pack。

最终合并目录：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/
```

最终完整性检查：

```text
docs/research/dialogue_state_v3_main_merged_integrity_20260516.json
docs/research/dialogue_state_v3_main_merged_integrity_20260516.md
```

完整性结果：

```text
expected_row_count = 350
combined_row_count = 350
final_response_row_count = 350
review_row_count = 350
blocking_reasons = []
warning_reasons = []
analysis_ready = true
headline_ready = true
```

## 可交付文件

主实验盲评表：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/coach_response_review_workbook_dev_ablation.zh.xlsx
```

主实验按题分 sheet 盲评表（推荐给教练使用）：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/coach_response_review_workbook_dialogue_state_v3_main_by_case_20260516.zh.xlsx
```

匿名 key：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/coach_response_review_workbook_dev_ablation.key.csv
```

完整回复 JSONL：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/combined_dev_ablation.jsonl
```

manifest：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/manifest.json
```

## DBox + Repair 公平性附录

为避免只给 Bridge Contract 系列加入 Repair 而造成不公平，本轮额外生成了一个 appendix/sensitivity condition：

```text
dbox_inspired_guard_repair
```

该 add-on 不进入主表，只用于回答：

```text
如果 DBox-inspired + Guard 也加 Repair，质量/安全权衡是否变化？
```

附录运行目录：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/
```

附录完整性结果：

```text
expected_row_count = 50
combined_row_count = 50
final_response_row_count = 50
review_row_count = 50
blocking_reasons = []
warning_reasons = []
analysis_ready = true
headline_ready = true
```

附录完整性检查：

```text
docs/research/dialogue_state_v3_repair_fairness_addon_integrity_20260516.json
docs/research/dialogue_state_v3_repair_fairness_addon_integrity_20260516.md
```

附录按题分 sheet 盲评表：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/coach_response_review_workbook_dialogue_state_v3_dbox_repair_addon_by_case_20260516.zh.xlsx
```

## 研究边界

本记录只说明：

```text
reviewed-candidate 50-case 的主实验和 DBox+Repair 附录回复已经生成完整，可以进入盲评。
```

本记录不说明：

```text
任何 condition 的教学质量更高；
任何 condition 的泄露更少；
Guard / Repair 已经因果有效；
这些结果已经可以写成论文 headline。
```

正式结论仍需等待：

1. 人类教练盲评；
2. 至少部分双评审；
3. agreement / adjudication；
4. paired analysis；
5. LLM grader calibration；
6. Repair same-candidate stress test。
