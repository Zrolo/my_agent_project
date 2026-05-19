# Real-Student Online 5-Case Coach Review Protocol 20260519

## 使用边界

本协议用于复核 real-student online 5-case dry run 的本地私有标注包。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

5 个 dry-run cases 仍处于 consent/reporting gate pending 状态。教练复核可用于内部检查 annotation schema 和 annotation guide 是否可执行，但不能写成可公开报告的 deep-pilot evidence、学生示例或个案发现。

## 私有材料位置

私有材料只保存在本地 `.local_private/` 目录，已被 `.gitignore` 排除：

- `.local_private/real_student_online_5case_annotation_packet_20260519.csv`
- `.local_private/real_student_online_5case_annotation_packet_20260519.md`
- `.local_private/real_student_online_5case_annotation_summary_20260519.md`
- `.local_private/real_student_online_5case_coach_review_packet_20260519.csv`
- `.local_private/real_student_online_5case_coach_review_packet_20260519.md`

这些文件可包含脱敏学生问题、recent dialogue、必要代码片段、当前 AIChat 回复和 AI 预标注，不得提交到 GitHub、论文公开补充材料或公开审稿附件。

## Coach Review Questions

每个 case 复核以下问题：

1. Privacy：脱敏是否足够，是否仍需删除身份线索、完整代码、完整对话或题目外私人信息。
2. Context sufficiency：当前材料是否足以判断 missing bridge。
3. Missing bridge：学生当前尚未完成的 case-specific reasoning bridge 是什么。
4. Forbidden content：这一轮 tutor 不应直接补完什么。
5. Acceptable reveal：哪些提示仍然保留学生推理机会。
6. Expected next student action：理想脚手架后，学生下一步应做什么。
7. Taxonomy fit：是否能映射到现有 cognitive bridge family；若不能，记录 candidate boundary。
8. Current AIChat leakage concern：当前系统回复是否可能提前补完 critical bridge。
9. AI preannotation agreement：是否同意 AI 预标注；不同意时记录原因。

## Allowed Labels

### `coach_review_status`

- `pending`
- `reviewed`
- `needs_second_coach`
- `excluded_privacy_risk`
- `excluded_insufficient_context`

### `coach_privacy_review_status`

- `passed_for_internal_review`
- `needs_more_redaction`
- `excluded_privacy_risk`

### `coach_context_sufficiency`

- `sufficient`
- `partial`
- `insufficient`
- `unclear`

### `coach_current_aichat_leakage_concern`

- `yes_high`
- `yes_medium`
- `yes_low`
- `no`
- `unclear`
- `not_judged_insufficient_context`

### `coach_matches_existing_taxonomy`

- `yes`
- `no`
- `uncertain`

### `coach_disagrees_with_ai_preannotation`

- `yes`
- `partial`
- `no`
- `not_applicable`

### `adjudication_needed`

- `yes`
- `no`

## Review Procedure

1. Read the private packet case by case.
2. Ignore AI preannotation at first pass; write an independent coach judgment.
3. Compare the independent judgment with AI preannotation.
4. Mark disagreement and adjudication need explicitly.
5. Do not copy full student text, full code, or full AI response into public notes.
6. If privacy is not sufficient, stop that case and mark `needs_more_redaction` or `excluded_privacy_risk`.
7. If context is insufficient, route the case to clarification-safety interpretation rather than forcing an ordinary missing bridge.

## Public Reporting Boundary

Before consent/status gate is complete, public-facing files may report only:

- 5-case dry-run process exists;
- private packet exists locally and is ignored by Git;
- coach review status counts, if they contain no case-level findings;
- field sufficiency issues in aggregate;
- whether annotation guide/schema needs revision.

Before consent/status gate is complete, public-facing files must not report:

- full student messages;
- full recent dialogue;
- full student code;
- full AIChat responses;
- individual student or problem hash tables;
- case-level leakage labels;
- paraphrased examples that could identify the case;
- deep-pilot findings as evidence for the paper.

## Claim Gate

| check | required result |
| --- | --- |
| 是否新增实验 | no |
| 是否新增主实验 condition | no |
| 是否修改 dialogue-state v3 主表 | no |
| 是否改变 evidence class | no |
| 是否改变学生可见回复 | no |
| 是否使用第三方公开社区数据 | no |
| 是否把 AI 预标注写成 final coach label | no |
| 是否把 pending-consent cases 写成 reportable evidence | no |
