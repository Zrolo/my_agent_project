# Real-Student Online 2-Case Adjudication Packet Status 20260520

## 使用边界

本文档记录 9-case 真人教练二审焦点包中 2 条裁决记录的生成、验证和集成状态。它只说明 workflow status，不公开学生原文、完整代码、完整 AIChat 回复、case-level labels、student hashes、problem hashes、hash salt 或可逆映射。

本步骤不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，不修改线上 AIChat、prompt 或 active mode，也不改变学生可见回复。

## Packet Status

| item | value | boundary |
| --- | ---: | --- |
| adjudication cases extracted from 9-case focus review | 2 | private adjudication workflow |
| adjudication rows currently completed | 2 | internal adjudication completed |
| adjudication rows pending | 0 | no adjudication rows pending |
| rows passing internal privacy review | 2 | not public-reporting permission |
| rows with consent/reporting gate completed | 0 | case-level reporting not allowed |
| reportable case-level evidence | 0 | gate pending |

## Private Files

The private adjudication packet is stored under `.local_private/`:

```text
.local_private/real_student_online_2case_adjudication_packet_20260520.xlsx
```

Template validation output:

```text
.local_private/real_student_online_2case_adjudication_packet_template_validation_20260520.json
```

Completed adjudication validation output:

```text
.local_private/real_student_online_2case_adjudication_packet_human_adjudicated_validation_20260520.json
```

## Interpretation

The two remaining focus rows were separated into a short adjudication packet and have now been adjudicated internally. This is an internal review-management step. It is not a new experiment, not a condition comparison, not learning-outcome evidence, and not a reportable result.

## Claim Gate

| check | result |
| --- | --- |
| 新增 dialogue-state v3 主实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改线上 AIChat / prompt / active mode | no |
| 改变学生可见回复 | no |
| 把 adjudication packet 写成 main result | no |
| 把 adjudication packet 写成 learning outcome study | no |
| 公开 case-level labels | no |

## Next Step

The adjudication workbook has been validated and integrated. The remaining gate is privacy/consent/reporting, not adjudication. Public documents must continue to avoid case-level labels and examples unless that gate is separately completed.
