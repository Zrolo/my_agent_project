# Dialogue-State v3 Targeted Adjudication Extension Plan (20260517)

## 目标

不全量裁决 350 条，而是从 Coach A/B 剩余未裁决分歧中追加 30-40 条，优先处理会影响 headline 比较和安全口径的样本。

## 已输出

- 候选表：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/adjudication_extension_candidate_list_20260517.xlsx`
- CSV 版本：`evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/adjudication_extension_candidate_list_20260517.csv`

本轮候选数：40。已排除 priority60 已裁决的 60 条。

## 抽样规则

优先级加权：`main_scaffold_eval`、critical leakage disagreement、student-ready yes/no flip、would-show flip、rank delta >= 4、overall delta >= 2、headline condition，以及 Bridge vs DBox 比较相关条件。

| reason | count |
| --- | --- |
| main_scaffold_eval | 40 |
| would-show flip | 40 |
| headline condition | 40 |
| student-ready flip | 39 |
| Bridge vs DBox comparison affected | 36 |
| rank delta >= 4 | 13 |
| overall delta >= 2 | 13 |

## 建议裁决流程

1. 裁决者只看同一 row 的学生问题、回复和 case-specific rubric，不看 condition 名称。
2. 先裁 `adjudicated_leakage_label` 与 `adjudicated_would_show_to_student`，再裁 overall / sufficiency / burden。
3. 对影响主表的行写一句 `adjudication_notes`，尤其说明是“过强泄露”“太空泛”“接不住上下文”还是“可展示但需轻微改写”。
4. 完成后生成 `priority100_adjudicated_plus_coachA/B` sensitivity；论文可写为：high-priority disagreements plus an additional targeted set affecting headline comparisons were adjudicated。

## 解释边界

这个 targeted extension 仍不是 final gold；它是为了降低最影响论文主张的分歧不确定性，而不是消除全部 rater variance。
