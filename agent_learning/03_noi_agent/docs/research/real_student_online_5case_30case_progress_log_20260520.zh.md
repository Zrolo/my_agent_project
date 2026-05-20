# Real-Student Online 5-Case / 30-Case Progress Log 20260520

## 完成事项

1. 已将 5-case human coach review 写入公开安全状态文档：
   - `real_student_online_5case_human_coach_review_public_status_20260520.zh.md`
   - `real_student_online_5case_human_coach_review_public_status_20260520.json`
   - `real_student_online_5case_human_coach_review_status_log_20260520.zh.md`
2. 已创建 manuscript v0.8：
   - `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_8_real_student_5case_status.zh.md`
3. 已生成 30-case 内部教练复核工作簿 v1，并发现题面补全问题：
   - `.local_private/real_student_online_30case_human_coach_review_packet_cn_v1_20260520.xlsx`
4. 已根据用户指定的 JMYSOJ 题面页生成 30-case v2 完整题面复核包：
   - `.local_private/real_student_online_30case_human_coach_review_packet_cn_v2_full_problem_20260520.xlsx`
5. 已更新 30-case 题面补全缺口清单，v2 中缺口为 0：
   - `.local_private/real_student_online_30case_problem_statement_completion_needed_v2_20260520.csv`
6. 已记录 30-case 工作簿公开安全状态：
   - `real_student_online_30case_coach_review_packet_status_20260520.zh.md`
7. 已完成 30-case 内部 AI preliminary triage，仅用于真人教练复核优先级安排：
   - `.local_private/real_student_online_30case_ai_prelim_review_gpt55_xhigh_20260520.xlsx`
   - `.local_private/real_student_online_30case_ai_prelim_review_gpt55_xhigh_summary_20260520.json`
   - `real_student_online_30case_ai_prelim_triage_status_20260520.zh.md`
8. 已生成 9-case 真人教练二审焦点包：
   - `.local_private/real_student_online_30case_second_coach_focus_packet_from_ai_prelim_20260520.xlsx`
   - `.local_private/real_student_online_30case_second_coach_focus_packet_summary_20260520.json`
   - `real_student_online_30case_second_coach_focus_packet_status_20260520.zh.md`
9. 已补充 9-case 二审教练交接说明：
   - `real_student_online_30case_second_coach_review_handoff_20260520.zh.md`
10. 已补充 9-case 二审完成稿 validator：
   - `evals/aichat/validate_real_student_30case_second_coach_focus_review.py`
11. 已接收并验证 9-case 真人教练二审完成稿：
   - `.local_private/real_student_online_30case_second_coach_focus_packet_human_reviewed_20260520.xlsx`
   - `.local_private/real_student_online_30case_second_coach_focus_packet_human_reviewed_validation_20260520.json`
   - `.local_private/real_student_online_30case_second_coach_focus_human_reviewed_summary_20260520.json`
   - `real_student_online_30case_second_coach_focus_human_review_public_status_20260520.zh.md`
   - `real_student_online_30case_second_coach_focus_human_review_public_status_20260520.json`
12. 已将 2 条仍需裁决 focus rows 单独导出为人工裁决包：
   - `.local_private/real_student_online_2case_adjudication_packet_20260520.xlsx`
   - `.local_private/real_student_online_2case_adjudication_packet_summary_20260520.json`
   - `.local_private/real_student_online_2case_adjudication_packet_template_validation_20260520.json`
   - `real_student_online_2case_adjudication_packet_status_20260520.zh.md`
   - `real_student_online_2case_adjudication_packet_status_20260520.json`
13. 已补充 2-case 人工裁决交接说明：
   - `real_student_online_2case_adjudication_handoff_20260520.zh.md`
14. 已补充 post-adjudication 集成协议和脚本：
   - `real_student_online_post_adjudication_integration_protocol_20260520.zh.md`
   - `evals/aichat/integrate_real_student_2case_adjudication.py`
15. 已接收、验证并集成 2-case 人工裁决完成稿：
   - `.local_private/real_student_online_2case_adjudication_packet_human_adjudicated_20260520.xlsx`
   - `.local_private/real_student_online_2case_adjudication_packet_human_adjudicated_validation_20260520.json`
   - `.local_private/real_student_online_post_adjudication_integrated_summary_20260520.json`
   - `.local_private/real_student_online_post_adjudication_integrated_summary_20260520.zh.md`
   - `real_student_online_post_adjudication_public_status_20260520.zh.md`
   - `real_student_online_post_adjudication_public_status_20260520.json`

## 30-Case Packet 状态

| item | value |
| --- | ---: |
| selected pilot candidate cases | 30 |
| full problem statements from local `latest.ndjson` | 15 |
| full problem statements from author-specified JMYSOJ problem pages | 15 |
| problem statements needing manual completion | 0 |
| coach-reviewed rows in 30-case packet | 0 |
| AI preliminary triage rows | 30 |
| real-coach focus-review cases selected from triage | 9 |
| second-coach-reviewed focus rows | 7 |
| focus rows still requiring adjudication | 0 |
| 2-case adjudication packet rows | 2 |
| adjudication rows completed | 2 |
| adjudication rows pending | 0 |
| post-adjudication workflow closed | yes |
| 2-case adjudication handoff note | 1 |
| post-adjudication integration protocol | 1 |
| post-adjudication integration script | 1 |
| second-coach handoff note | 1 |
| second-coach focus review validator | 1 |
| reportable case-level evidence | 0 |

## 不变边界

- 没有新增 dialogue-state v3 主实验。
- 没有新增 main experiment condition。
- 没有重算 dialogue-state v3 主表。
- 没有修改线上 AIChat、prompt 或 active mode。
- 没有改变学生可见回复。
- 没有公开学生原文、完整代码、完整 AIChat 回复、hash 明细或 case-level labels。
- 没有把 5-case / 30-case pilot 写成 main result。
- 没有把 pilot 写成 learning outcome study。
- 没有把 AI preliminary triage 写成真人教练证据、final gold 或论文结果。

## 后续事项

1. 完成 ethics/privacy/data availability review 与 consent/reporting gate；在 gate 完成前，reportable case-level evidence 仍为 0。
2. 若时间允许，再将完整 v2 30-case 工作簿交给教练正式复核。
3. 任何公开 manuscript 文字都只能把当前状态写成 pilot workflow / ecological-validity support，而不能写成模型效果或线上系统胜利。
