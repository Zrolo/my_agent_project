# Real-AIChat-100 Observational Validation Protocol

Date: 2026-05-20

## 使用边界

Real-AIChat-100 是 observational ecological-validity validation。它不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，不比较 7 个 offline harnesses，不评估 learning outcome，不改变线上 AIChat 回复，也不使用洛谷讨论区或任何第三方公开社区数据。

## B1. 目的

Real-AIChat-100 的目的不是比较 7 conditions，而是：

1. 检查 critical-bridge leakage 问题是否出现在真实 AIChat tutoring contexts。
2. 检查 cognitive bridge family、surface anchor 和 case-specific rubric 是否能迁移到真实学生问题。
3. 检查真实场景中 `context_sufficiency_light`、`rough_bridge_family`、`surface_anchor` 和 `help_seeking_type` 的分布。
4. 为 Real-AIChat-Replay-30/50 提供 context-sufficient candidate pool。

## B2. 数据来源

允许的数据来源仅限我们自己的 AIChat / 教学系统日志。禁止使用：

- 洛谷讨论区、题解区、评论区或任何公开社区内容；
- 第三方公开社区、论坛、问答站、社交媒体或公开讨论区；
- 未授权学生数据；
- 任何不满足 privacy / consent / reporting gate 的公开 case-level 展示。

## B3. 选择池

当前 real-student AIChat 漏斗按现有文档记录为：

| layer | count | interpretation |
| --- | ---: | --- |
| raw AIChat message rows | 1156 | source-corpus background only |
| sessions | 87 | source-corpus background only |
| paired user-assistant turns | 578 | paired-turn background only |
| substantial candidate turns | 137 | candidate-turn screening pool |
| candidate sessions | 59 | screening-pool session coverage |

如果后续实际文件中的数字与以上数字不一致，不得自行修改主稿数字；应在 protocol 和 patch log 中标记 `needs result-number verification`。

## B4. Real-AIChat-100 Selection Rule

目标选择 80-100 个真实 target turns。如果不足 100 个满足条件，则使用 `N <= 100` 并报告原因。

纳入条件：

- CP tutoring relevant。
- substantial turn。
- `privacy_review_status` 不得为 `failed`。
- consent/reporting gate 如果 pending，则只允许内部标注和 aggregate reporting。
- 有足够上下文，或可明确标记为 context-insufficient。
- 尽量覆盖不同 `student_id_hash`、`problem_id_hash`、bridge family、surface anchor 和 help-seeking type。
- 不得按 observed AIChat response 好坏选择。
- 不得按是否支持 Bridge Contract / Repair 选择。
- 不得按最终结果好看选择。

## B5. Sampling Fairness / Coverage Constraints

建议但不强制：

- 尽量最大化 unique students。
- 尽量最大化 unique problems。
- 控制单一 student / problem 的占比。
- 如果无法控制，必须在 limitations 中报告 concentration risk。

## B6. Light Annotation Fields

Real-AIChat-100 轻量标注字段由 `real_aichat_100_observational_validation_schema_v1.json` 固定，包括：

- `real_aichat_case_id`
- `source_candidate_turn_id`
- `student_id_hash_private_or_redacted`
- `problem_id_hash_private_or_redacted`
- `session_id_hash_private_or_redacted`
- `cp_tutoring_relevance`
- `substantial_turn`
- `context_sufficiency_light`
- `rough_bridge_family`
- `surface_anchor`
- `help_seeking_type`
- `missing_bridge_identifiable`
- `observed_current_aichat_response_available`
- `observed_current_aichat_response_role`
- `possible_bridge_leakage_concern`
- `candidate_for_replay`
- `candidate_for_trajectory_subset`
- `privacy_review_status`
- `consent_reporting_gate`
- `public_reporting_allowed`
- `selection_reason`
- `exclusion_reason`
- `annotator_id`
- `annotation_date`
- `notes_no_raw_text`

`observed_current_aichat_response_role` 必须固定为 `observed_only_not_condition`。

## B7. Reporting Rule

如果 consent/reporting gate pending：

- 只报告 aggregate counts。
- 不报告 case-level labels。
- 不报告学生原文。
- 不报告完整代码。
- 不报告完整 AIChat 回复。
- 不报告 hash 表。
- 不报告可识别题目/时间组合。

## B8. Manuscript-Safe Wording

English safe wording:

```text
Real-AIChat-100 is an observational ecological-validity layer based on target turns from our own AIChat / teaching system. It is not a condition-comparison experiment. The observed current AIChat response is treated as an observed current-system response rather than as a baseline condition. This layer is used to examine taxonomy and rubric transfer and is not used to recompute dialogue-state v3 results.
```

中文安全写法：

```text
Real-AIChat-100 是基于我们自己 AIChat / 教学系统真实 target turns 的观察性生态效度层。它不是条件比较实验。线上已展示 AIChat 回复只作为 observed current-system response，不作为 baseline condition。该层只用于检查 taxonomy / rubric transfer，不用于重算 dialogue-state v3 结果。
```

## Execution Status

当前已基于 `real_student_online_candidate_screening_form_v1.csv` 的 137 条结构化 screening rows 创建公开脱敏 selection manifest：

- `real_aichat_100_observational_validation_manifest_20260520.csv`
- `real_aichat_100_selection_summary_20260520.json`
- `real_aichat_100_selection_log_20260520.zh.md`

该 manifest 只使用 candidate-turn screening CSV 中已有的结构化字段，不读取 `.local_private/`，不包含学生原文、完整代码、完整 AIChat 回复、真实身份、hash salt、可逆映射或 row-level hash 表。它不是 deep annotation result，不是 7-condition comparison，不是 learning outcome study，也不更新 dialogue-state v3 主表。
