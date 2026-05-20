# Real-Student Online Post-Adjudication Public Status 20260520

## 使用边界

本文档只记录 real-student online AIChat pilot 的 post-adjudication 公开安全 workflow status。它不公开学生原文、完整代码、完整 AIChat 回复、case-level labels、student hashes、problem hashes、hash salt 或可逆映射。

## Public-Safe Status

| item | value | boundary |
| --- | ---: | --- |
| second-review focus cases | 9 | internal workflow |
| adjudication cases | 2 | internal workflow |
| adjudication rows completed | 2 | aggregate workflow status only |
| workflow adjudication closed | yes | not a paper result |
| reportable case-level evidence after gate | 0 | controlled by privacy/consent/reporting gate |

## Interpretation

This status can be used to track whether the private review workflow has closed. It does not support leakage-rate reporting, model-quality distributions, deployed-system superiority, or learning-outcome claims unless a separate public-reporting gate is completed.

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
