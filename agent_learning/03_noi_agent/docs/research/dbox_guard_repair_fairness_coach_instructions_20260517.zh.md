# DBox Guard+Repair Fairness Coach Instructions 20260517

## 给教练的文件

请只使用：

```text
evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/dbox_guard_repair_fairness_review20_workbook_20260517.zh.xlsx
```

不要查看或填写：

- `dbox_guard_repair_fairness_candidate_list_20260517.csv`
- `dbox_guard_repair_fairness_candidate_list_20260517.xlsx`
- `dbox_guard_repair_fairness_review20_workbook_20260517.key.csv`

这些是研究端内部文件，包含抽样原因、condition 映射或主实验对比信息。

## 评审任务

本轮是 DBox-inspired Guard+Repair 的公平性补评。目标不是证明某个系统一定更好，而是回答：

1. DBox+Repair 是否比 DBox Guard 更安全或更可用；
2. DBox+Repair 是否接近 `bridge_contract_compact_guard_repair`；
3. Repair 是否带来 student burden trade-off；
4. DBox+Repair 是否仍有 critical bridge leakage。

## 填写方式

只在 `盲评表` 的黄色评分列填写。最终汇总脚本只读取 `盲评表`。

优先填写这些字段：

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

诊断维度如 `是否抓住卡点 0-2`、`是否贴合题目/对话 0-2`、`下一步是否清楚 0-2` 可以继续填，用于后续错误分析。

## 评分口径

使用 dialogue-state v3 主实验同一 rubric。先看：

1. 学生当前问题；
2. case-specific rubric：成功标准、本轮禁止补完、关键桥泄露边界、允许透露、期望学生下一步；
3. AI 回复；
4. 黄色评分列。

不要根据系统名、Repair 触发情况或主实验结果评分。教练只需要判断这条学生可见回复是否适合给学生。

## 必须写备注的情况

以下情况必须在 `coach_notes` 写一句原因：

- `coach_leakage_label` 是 `major_bridge_leakage` 或 `answer_leakage`；
- `coach_would_show_to_student` 是 `no`；
- `coach_overall_quality_score` 是 1 或 2；
- `coach_reviewer_confidence` 是 `low`；
- `coach_needs_discussion` 是 `yes`。

## 论文使用方式

这批补评完成前，论文只能写：

```text
We generated a DBox-inspired Guard+Repair fairness add-on and include a targeted human-review check for headline-sensitive cases.
```

不能写：

```text
Bridge+Repair 已经压过所有 fair repair-enabled baselines。
```
