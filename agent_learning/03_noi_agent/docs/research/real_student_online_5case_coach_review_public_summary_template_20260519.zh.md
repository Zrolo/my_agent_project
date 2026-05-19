# Real-Student Online 5-Case Coach Review Public Summary Template 20260519

## 使用边界

本模板只用于在教练完成 5-case dry run 复核后，生成公开安全的 aggregate summary。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

在 consent/reporting gate 完成前，本模板不得填入 case-level labels、学生示例、学生原文、完整代码或完整 AI 回复。即使教练已完成内部复核，公开 summary 仍只能报告流程可执行性和字段充分性。

## Required Aggregate Fields

| field | value | reporting boundary |
| --- | ---: | --- |
| dry-run cases reviewed by coach |  | process status only |
| cases passing privacy review for internal review |  | not public case release |
| cases needing additional redaction |  | aggregate only |
| cases excluded for privacy risk |  | aggregate only |
| context sufficient |  | aggregate only |
| context partial |  | aggregate only |
| context insufficient / unclear |  | aggregate only |
| cases mappable to existing taxonomy |  | aggregate only |
| cases uncertain or not mappable |  | aggregate only |
| cases needing second coach/adjudication |  | aggregate only |
| reportable after consent/status gate |  | must be 0 until gate complete |

## Field-Sufficiency Summary

Use short aggregate notes only:

```text
The 5-case dry run was used to check whether the online pilot schema could represent real-student dialogue-state cases. [N] cases could be represented without adding schema fields; [N] cases required field clarification; [N] cases required additional privacy redaction. These counts are process evidence only and are not reported as learning outcomes or model-performance results.
```

## Allowed Public Statements

- The 5-case dry run tested annotation feasibility.
- The private coach review packet exists locally and is ignored by Git.
- The validator found `[N]` errors and `[N]` reporting-gate warnings.
- The schema / annotation guide did or did not require revision.
- Consent/reporting gate remains pending unless explicitly completed.

## Forbidden Public Statements

- Any full student message.
- Any full recent dialogue.
- Any full code excerpt.
- Any full AIChat response.
- Any case-level leakage label while consent/reporting gate is pending.
- Any paraphrased case example that could identify the student/problem.
- Any claim that 5-case dry run is a main result.
- Any claim that 5-case dry run evaluates long-term learning.
- Any claim that pilot changes dialogue-state v3 main results.

## Claim Gate

| check | required result |
| --- | --- |
| 是否新增实验 | no |
| 是否新增主实验 condition | no |
| 是否修改 dialogue-state v3 主表 | no |
| 是否改变 evidence class | no |
| 是否改变学生可见回复 | no |
| 是否把 AI 预标注写成 final coach label | no |
| 是否把 pending-consent cases 写成 reportable evidence | no |
| 是否公开 case-level labels | no, unless consent/reporting gate is complete and privacy review permits |
