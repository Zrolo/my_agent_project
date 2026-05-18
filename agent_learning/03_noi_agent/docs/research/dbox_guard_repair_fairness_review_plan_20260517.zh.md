# DBox Guard+Repair Fairness Add-On Review Plan 20260517

## 当前状态

已定位 `dbox_inspired_guard_repair` 生成包：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/
```

已有生成数据，但当前未发现已完成的人审 label JSONL。因此不能把 DBox+Repair 纳入主结果表，也不能写“Bridge+Repair 优于所有公平 repair baselines”。

## 生成包摘要

| metric | value |
| --- | ---: |
| generated_rows | 50 |
| repair_applied | 17 |
| repair_still_leaks | 1 |
| post_repair_rewrite_or_block | 4 |
| final_static_risk | 19 |

已生成补评候选包：

- `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_candidate_list_20260517.xlsx`
- `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_candidate_list_20260517.csv`

当前候选数：20。

已生成 coach-facing direct-fill workbook：

- `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.zh.xlsx`
- hidden key: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.key.csv`
- source review CSV: `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.csv`

这个 workbook 只保留 `盲评表` 作为填写入口；最终汇总脚本读取 `盲评表`。不要让教练填写 internal candidate list，也不要把 hidden key 发给教练。

## 最小补评方案

时间充足时：50-case 全量补评 `dbox_inspired_guard_repair`。

时间紧时：补评 15-20 个 headline-sensitive cases。优先包括：

1. DBox clean / DBox guard 有 leakage 的 case；
2. DBox guard 与 Bridge repair 排名接近或结论敏感的 case；
3. student-ready yes/no flip 的 case；
4. `main_scaffold_eval` 中影响 headline 的 case；
5. DBox repair 实际触发、post-repair 仍被 judge 标记、final static risk 为高的 case。

## 评审方式

1. 教练只填写 `dbox_guard_repair_fairness_review20_workbook_20260517.zh.xlsx` 的 `盲评表` 黄色评分列。
2. 只展示最终回复，不展示 `dbox_inspired_guard_repair` condition 名。
3. 使用 dialogue-state v3 主实验同一 rubric：overall、would-show、leakage label、student burden、notes。
4. 与主实验相同的 case-specific rubric 一起展示。
5. 完成后比较：
   - `dbox_inspired_guard`
   - `dbox_inspired_guard_repair`
   - `bridge_contract_compact_guard_repair`

建议填写的最低字段：

- `coach_overall_quality_score`
- `coach_would_show_to_student`
- `coach_leakage_label`
- `coach_bridge_reveal_justification`
- `coach_scaffold_sufficiency_score`
- `coach_student_response_burden`
- `coach_reviewer_confidence`
- `coach_needs_discussion`
- `coach_notes`
- `review_status`

重大泄露、答案泄露、不愿给学生看、总体质量 1/2、低置信或需要讨论的样本必须写备注。

## 需要回答的问题

| question | interpretation |
| --- | --- |
| DBox+Repair 是否明显改善 DBox guard？ | 若是，说明 Repair 对 literature-inspired baseline 也有价值。 |
| DBox+Repair 是否接近 Bridge+Repair？ | 若接近，论文要弱化 Bridge-specific 方法结论，强调 repair-enabled guard pipeline。 |
| DBox+Repair 是否超过 Bridge+Repair？ | 若超过，主论文应公平报告，不能保留 Bridge 绝对优越叙事。 |
| DBox+Repair 是否仍有 higher leakage / burden？ | 可作为 Bridge Contract compact 的增量证据，但仍需 paired uncertainty。 |

## 当前论文口径

在补评完成前可以写：

```text
We generated a DBox-inspired Guard+Repair fairness add-on and include it as a planned supplementary human-review check.
```

不能写：

```text
Bridge+Repair 对所有 repair-enabled fair baselines 都有确定优势。
```
