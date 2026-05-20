# Real-Student Online 30-Case Second Coach Focus Human Review Public Status 20260520

## 使用边界

本文档只记录 9-case 真人教练二审焦点包的公开安全状态。它不公开学生原文、完整代码、完整 AIChat 回复、case-level labels、student hashes、problem hashes、hash salt 或可逆映射。

本步骤不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，不修改线上 AIChat、prompt 或 active mode，也不改变学生可见回复。

## Public-Safe Status

| item | value | public boundary |
| --- | ---: | --- |
| focus cases in human second-coach packet | 9 | internal pilot review workflow |
| rows with completed second-coach review status | 7 | aggregate workflow status only |
| rows adjudicated after second-coach review | 2 | aggregate workflow status only |
| rows still requiring adjudication | 0 | adjudication closed internally |
| rows passing internal privacy review | 9 | not public-reporting permission |
| rows with consent/reporting gate completed | 0 | case-level reporting not allowed |
| reportable case-level evidence | 0 | gate pending |

## Interpretation

The 9-case focus packet received human second-coach review input, and the two rows that required adjudication have now been closed through the 2-case adjudication workflow. Because the consent/reporting gate remains pending, these materials can only support internal review workflow tracking at this stage. They should not be reported as paper results, leakage rates, model-quality distributions, or learning-outcome evidence.

## Manuscript-Safe Wording

```text
In a private follow-up workflow, a 9-case focus packet from the real-student AIChat pilot received second-coach review input. This process remains behind the privacy and consent/reporting gate; therefore, it is treated as internal workflow evidence rather than reportable case-level results.
```

## Claim Gate

| check | result |
| --- | --- |
| 新增 dialogue-state v3 主实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改线上 AIChat / prompt / active mode | no |
| 改变学生可见回复 | no |
| 把 pilot 写成 main result | no |
| 把 pilot 写成 learning outcome study | no |
| 公开 case-level labels | no |

## Updated Status

The 2-case adjudication packet has been completed and integrated into the private workflow summary. The remaining blocker is the consent/reporting gate. 若未来需要进入论文附录，只能报告公开安全的 aggregate/process counts，并需要单独完成 ethics/privacy/data availability review。
