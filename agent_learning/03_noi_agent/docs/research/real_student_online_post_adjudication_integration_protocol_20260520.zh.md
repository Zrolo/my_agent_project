# Real-Student Online Post-Adjudication Integration Protocol 20260520

## 目标

本文档说明 2-case 人工裁决完成后，如何把裁决状态合并回 9-case real-student online AIChat pilot workflow。该流程只用于内部证据治理和公开安全状态更新，不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，也不修改线上 AIChat。

## 输入文件

完成裁决后，预期输入为：

```text
.local_private/real_student_online_2case_adjudication_packet_human_adjudicated_20260520.xlsx
```

该文件应由裁决者从以下模板另存：

```text
.local_private/real_student_online_2case_adjudication_packet_20260520.xlsx
```

## 集成前检查

必须先运行：

```bash
python3 evals/aichat/validate_real_student_2case_adjudication_review.py \
  .local_private/real_student_online_2case_adjudication_packet_human_adjudicated_20260520.xlsx
```

通过条件：

- 2 行均不再是 `待裁决`。
- required fields 均已填写。
- allowed values 合法。
- `当前AIChat回复字段说明` 仍为 `线上已展示回复，观察项，非实验条件`。
- 若 `知情/报告门 = 可报告`，则 `隐私复核状态` 必须为 `可内部复核`。

## 集成输出

集成脚本应输出私有汇总：

```text
.local_private/real_student_online_post_adjudication_integrated_summary_20260520.json
.local_private/real_student_online_post_adjudication_integrated_summary_20260520.zh.md
```

以及公开安全状态：

```text
docs/research/real_student_online_post_adjudication_public_status_20260520.zh.md
docs/research/real_student_online_post_adjudication_public_status_20260520.json
```

## 公开报告边界

即使 2-case 裁决完成，也不自动允许公开 case-level labels 或评分分布。公开文档只能说明：

- 9-case focus review 是否已完成裁决闭环。
- 仍有多少 rows 被 privacy/consent/reporting gate 阻断。
- reportable case-level evidence 是否仍为 0。
- 是否仍需 ethics/privacy/data availability review。

不得公开：

- 学生原文。
- 完整代码。
- 完整 AIChat 回复。
- case-level labels。
- student hashes / problem hashes 明细。
- hash salt 或可逆映射。

## Manuscript-Safe Wording

```text
The 9-case focus review workflow was completed internally after adjudicating the remaining two rows. Because the consent/reporting gate was not completed, the workflow is treated as internal ecological-validity review management rather than reportable case-level evidence.
```

## Claim Gate

| check | required result |
| --- | --- |
| 新增 dialogue-state v3 主实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改线上 AIChat / prompt / active mode | no |
| 改变学生可见回复 | no |
| 把 pilot 写成 main result | no |
| 把 pilot 写成 learning outcome study | no |
| 公开 case-level labels | no |
