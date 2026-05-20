# Real-Student Online 30-Case Second Coach Focus Packet Status 20260520

## 使用边界

本文档记录 30-case real-student online AIChat pilot 的 9-case 真人教练二审焦点包生成与闭环状态。该焦点包来自内部 AI preliminary triage 的优先级筛选；后续二审与 2-case 裁决已在内部 workflow 中完成。

该焦点包不新增实验、不新增 condition、不修改线上 AIChat、不改变学生可见回复、不重算 dialogue-state v3 主表，也不构成论文结果。

## Focus Packet Status

| item | value | boundary |
| --- | ---: | --- |
| source packet | 30-case internal coach-review packet | private workflow input |
| focus cases selected for second coach review | 9 | focus workflow completed internally |
| selection rule | discussion / arbitration / low-confidence triage flag | prioritization rule only |
| second-coach-reviewed rows | 7 | aggregate workflow status only |
| rows adjudicated after second review | 2 | aggregate workflow status only |
| rows still requiring adjudication | 0 | adjudication closed internally |
| reportable case-level evidence | 0 | consent/reporting gate pending |

## Selection Rule

The focus packet contains cases selected from the AI preliminary triage when at least one of the following internal triage flags was present:

- 是否需要裁决 = 是
- 是否需要讨论 = 是
- 复核信心 = 低

This rule is used only to reduce reviewer burden and prioritize uncertain cases. It does not convert AI preliminary labels into human labels.

## Workbook Structure

The private focus workbook contains separate sheets for:

- 填写说明
- 案例上下文
- 二审评分
- AI预复核参考
- 隐私与报告门

The AI preliminary reference is separated from the real-coach scoring sheet so that the second coach can fill their own judgment. The resulting human review must still be checked against the privacy and reporting gate before any public reporting.

## Manuscript-Safe Wording

```text
For internal workflow management, a 9-case focus packet was prepared for second-coach review. The focus set was selected from a preliminary triage of the 30-case packet, but the triage labels are not treated as human evidence or manuscript results.
```

## Claim Gate

| check | result |
| --- | --- |
| 新增 dialogue-state v3 主实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改线上 AIChat / prompt / active mode | no |
| 改变学生可见回复 | no |
| 把 9-case focus packet 写成 reportable result | no |
| 把 focus packet 写成 main result | no |
| 公开 case-level labels | no |

## Updated Workflow Status

The human second-coach focus workbook has been received and validated. Seven rows completed second-coach review status, and the two remaining rows were adjudicated through a separate 2-case adjudication packet. Public reporting remains blocked by the consent/reporting gate.

## Next Step

Do not publish case-level labels or examples unless the privacy/consent/reporting gate is separately completed. If time allows, the full 30-case packet can receive additional coach review as a separate internal workflow.
