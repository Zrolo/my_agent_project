# EAIT v0.10 Submission Gate Hygiene Log 20260520

## 修改文件

- `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_10_submission_gate_hygiene.zh.md`

## 基于文件

- `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_9_real_student_post_adjudication_status.zh.md`

## 修改目的

v0.10 是投稿前 claim-gate 小修版本。它不新增实验、不改数字、不改 evidence class，只降低 all-50 sensitivity 被误读为 headline ranking 的风险。

## 具体修改

在 Results / RQ3 中，将一句 all-case sensitivity 的具体排名式表述改为更保守的边界表述：

- before: all-case sensitivity 中写出某 condition 在 Coach A、Coach B、priority60+CoachA、priority60+CoachB 下有最高 overall score。
- after: all-case sensitivity 只用于检查 bounded trend interpretation 是否对 rater views 敏感；不用于 headline ranking。

## Submission Gate Audit

| check | result |
| --- | --- |
| 新增实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改任何数字 | no |
| 改变 evidence class | no |
| 把 all-50 aggregate 写成 headline | no |
| 把 217 response-level reviews 写成 independent cases | no |
| 写显著全面胜出 | no |
| 写 Guard-only 修复最终输出 | no |
| 写 Repair 主实验因果 | no |
| 写 LLM grader 替代人类教练 | no |
| 写 pilot / real-student workflow 为 main result | no |
| 新增 citation | no |

## Remaining Submission Blockers

1. Related Work 仍有 citation placeholders，正式投稿前必须做 citation verification pass。
2. Result-number verification 仍需作者最终核对。
3. Ethics/privacy/data availability wording 仍需按 EAIT submission policy 最终人工检查。
4. Real-student pilot 的 `reportable case-level evidence` 仍为 0；不能报告 case-level labels、score distributions、leakage rates 或学生示例。
