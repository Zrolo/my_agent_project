# Real-Student Online 30-Case AI Preliminary Triage Status 20260520

## 使用边界

本文档只记录 30-case real-student online AIChat pilot 的内部 AI preliminary triage 状态。该步骤用于帮助安排真人教练二审优先级，不是 human coach evidence，不是 final gold，不是论文结果，也不进入 dialogue-state v3 主实验。

AI preliminary triage 不修改线上 AIChat，不改变学生可见回复，不新增 main experiment condition，不重算 dialogue-state v3 主表，也不替代真人教练判断。

## Process Status

| item | value | boundary |
| --- | ---: | --- |
| input private 30-case packet | 1 workbook | internal packet only |
| AI preliminary rows completed | 30 | triage support only |
| rows flagged for real-coach focus review | 9 | selection for second coach review |
| rows not flagged for focus review | 21 | still not human-reviewed evidence |
| public case-level labels | 0 | suppressed until human review and reporting gate |
| reportable result evidence | 0 | AI preliminary labels are not reportable results |

## Why This Step Exists

The 30-case workbook is wide and information-dense. The AI preliminary triage was used only to identify cases that should be prioritized for real coach review, especially cases with lower confidence or possible disagreement. It does not establish leakage rates, model quality, taxonomy validity, or online-system performance.

## Public-Safe Interpretation

论文或公开附录中可以安全表述为：

```text
After preparing the 30-case internal coach-review packet, we ran an internal AI preliminary triage to identify cases that should receive prioritized real-coach review. The triage produced a 9-case focus packet. These AI preliminary annotations are not treated as human coach evidence, final labels, or paper results.
```

## Forbidden Interpretation

- 不得写成真人教练复核结果。
- 不得写成 final gold。
- 不得报告 AI preliminary 的 leakage distribution、score distribution 或 case-level labels。
- 不得写成 Real-AIChat pilot 的 completed result。
- 不得写成 LLM grader / judge 可以替代人类教练。
- 不得把 observed current AIChat response 写成 baseline、condition、control、online condition 或 repair output。

## Claim Gate

| check | result |
| --- | --- |
| 新增 dialogue-state v3 主实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改线上 AIChat / prompt / active mode | no |
| 改变学生可见回复 | no |
| 把 AI preliminary 写成 human coach evidence | no |
| 把 AI preliminary 写成 paper result | no |
| 公开 case-level labels | no |

## Next Step

将 9-case focus packet 交给真人教练二审。只有真人教练完成复核，并且 privacy/consent/reporting gate 允许后，才可以考虑公开 aggregate process-level summary；case-level 示例仍需单独脱敏和人工确认。
