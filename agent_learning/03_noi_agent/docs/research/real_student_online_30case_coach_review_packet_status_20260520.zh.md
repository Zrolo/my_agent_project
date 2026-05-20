# Real-Student Online 30-Case Coach Review Packet Status 20260520

## 使用边界

本文档记录 30-case real-student online AIChat pilot 内部教练复核包的生成状态。它只说明工作簿准备情况和题面补全状态；不报告教练评分、case-level labels、泄露分布、学生原文、完整代码、完整 AIChat 回复、student hashes、problem hashes、hash salt 或可逆映射。

本工作不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

## Packet Status

| item | value | boundary |
| --- | ---: | --- |
| selected pilot candidate cases in packet | 30 | internal review packet only |
| cases with full problem statements from local `latest.ndjson` | 15 | problem-statement support for coach review |
| cases with full problem statements from author-specified JMYSOJ problem pages | 15 | problem-statement support for coach review; problem statements only, not student/community data |
| cases requiring manual problem-statement completion | 0 | resolved in v2 packet |
| coach-reviewed cases in this 30-case packet | 0 | packet preparation only |
| AI preliminary triage rows | 30 | workflow prioritization only; not human evidence |
| focus cases selected for real-coach second review | 9 | focus workflow completed internally |
| second-coach-reviewed focus rows | 7 | aggregate workflow status only |
| focus rows adjudicated after second review | 2 | aggregate workflow status only |
| focus rows still requiring adjudication | 0 | adjudication closed internally |
| reportable case-level evidence | 0 | consent/reporting gate pending |

## Problem Statement Completion Gate

The v2 30-case packet has full problem statements for all 30 cases. Fifteen were matched from the local `latest.ndjson` snapshot and fifteen were completed from the author-specified JMYSOJ problem pages. This step adds problem statements for coach context only; it does not add student/community data, does not modify online AIChat, and does not create results.

## Manuscript-Safe Wording

```text
For the next real-student pilot step, we prepared a 30-case internal coach-review packet with full problem statements. Fifteen cases were paired with statements from the local problem-bank snapshot, and fifteen were completed from the author-specified JMYSOJ problem pages. This is a packet-preparation status only; it is not a result, not a condition comparison, and not learning-outcome evidence.
```

## Forbidden Wording

- Do not write that the 30-case packet has completed human review.
- Do not write that AI preliminary triage is human coach review.
- Do not report 30-case leakage rates or model-quality distributions.
- Do not write that the observed current AIChat response is a baseline, condition, control, or Repair output.
- Do not merge 30-case pilot materials into dialogue-state v3 main tables.
- Do not publish student text, full code, complete AIChat responses, case-level labels, or identifiable examples.

## Claim Gate

| check | result |
| --- | --- |
| 新增 dialogue-state v3 主实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改线上 AIChat / prompt / active mode | no |
| 改变 evidence class | no |
| 把 30-case pilot 写成 main result | no |
| 把 30-case pilot 写成 learning outcome study | no |
| 把 AI preliminary triage 写成 human coach evidence | no |
| 公开 case-level labels | no |

## Next Step

The 9-case focus review and 2-case adjudication workflow is closed internally. The remaining blocker is the consent/reporting gate. If time allows, the full 30-case packet can receive additional coach review, but public reporting remains limited by the consent/reporting gate.
