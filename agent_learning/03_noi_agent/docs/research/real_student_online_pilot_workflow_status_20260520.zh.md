# Real-Student Online AIChat Pilot Workflow Status 20260520

## 用途

本文档是 real-student online AIChat pilot 的总控状态页，用于说明当前工作流做到了哪一步、哪些文件可交给教练/裁决者、哪些内容仍不能进入论文公开结果。

本 pilot 只用于 ecological validity / taxonomy-rubric transfer workflow，不作为 dialogue-state v3 主结果，不评估 learning outcome，不比较 7 个 offline conditions，不修改线上 AIChat，也不改变学生可见回复。

## Data Funnel

| layer | count | role | reporting boundary |
| --- | ---: | --- | --- |
| raw AIChat message rows | 1156 | online log corpus summary | aggregate/process count only |
| sessions | 87 | online log corpus summary | aggregate/process count only |
| paired user-assistant turns | 578 | online log corpus summary | aggregate/process count only |
| substantial candidate turns | 137 | candidate-turn screening pool | not deep annotation sample |
| candidate sessions | 59 | candidate-turn screening pool | not deep annotation sample |
| selected pilot candidate cases | 30 | deep-review candidate packet | not main result |
| hashed students covered | 11 | aggregate coverage only | do not publish hash-level table |
| hashed problems covered | 15 | aggregate coverage only | do not publish hash-level table |

## Current Workflow Snapshot

| workflow item | status | count | public-reporting status |
| --- | --- | ---: | --- |
| 5-case human coach dry run | completed and validated | 5 | public workflow status only |
| 30-case full-problem coach packet | prepared | 30 | not human-reviewed as full packet |
| AI preliminary triage on 30-case packet | completed | 30 | internal triage only; not human evidence |
| focus cases selected for second-coach review | prepared | 9 | private review packet |
| human second-coach focus review | closed internally after adjudication | 9 reviewed/adjudicated | public workflow status only |
| 2-case adjudication packet | completed and integrated | 2 | public workflow status only |
| reportable case-level evidence after gate | blocked | 0 | consent/reporting gate pending |

## Current Gate

The 2-case adjudication workbook has been received, validated, and integrated into the private workflow summary. The remaining blocker is not adjudication; it is the privacy/consent/reporting gate. Until that gate changes, reportable case-level evidence remains 0.

## Reviewed / Prepared Private Files

| file | role |
| --- | --- |
| `.local_private/real_student_online_5case_human_coach_reviewed_cleaned_20260520.xlsx` | 5-case human coach dry-run reviewed workbook |
| `.local_private/real_student_online_30case_human_coach_review_packet_cn_v2_full_problem_20260520.xlsx` | complete 30-case coach review packet with full problem statements |
| `.local_private/real_student_online_30case_second_coach_focus_packet_human_reviewed_20260520.xlsx` | 9-case focus packet after human second-coach review |
| `.local_private/real_student_online_2case_adjudication_packet_human_adjudicated_20260520.xlsx` | 2-case adjudication workbook after human adjudication |
| `.local_private/real_student_online_post_adjudication_integrated_summary_20260520.json` | private post-adjudication integrated summary |

## Public-Safe Documents

| document | purpose |
| --- | --- |
| `real_student_online_5case_human_coach_review_public_status_20260520.zh.md` | 5-case human review public-safe status |
| `real_student_online_30case_coach_review_packet_status_20260520.zh.md` | 30-case packet preparation and full-problem status |
| `real_student_online_30case_ai_prelim_triage_status_20260520.zh.md` | AI preliminary triage boundary and process status |
| `real_student_online_30case_second_coach_focus_packet_status_20260520.zh.md` | 9-case focus packet status |
| `real_student_online_30case_second_coach_focus_human_review_public_status_20260520.zh.md` | 9-case human second-review public-safe status |
| `real_student_online_2case_adjudication_packet_status_20260520.zh.md` | 2-case adjudication packet status |
| `real_student_online_2case_adjudication_handoff_20260520.zh.md` | instructions for the human adjudicator |
| `real_student_online_post_adjudication_integration_protocol_20260520.zh.md` | protocol for integrating adjudication after completion |
| `real_student_online_post_adjudication_public_status_20260520.zh.md` | public-safe status after adjudication integration |
| `real_student_online_5case_30case_progress_log_20260520.zh.md` | chronological workflow log |

## Scripts

| script | purpose |
| --- | --- |
| `evals/aichat/validate_real_student_30case_second_coach_focus_review.py` | validate 9-case second-coach focus review workbook |
| `evals/aichat/export_real_student_2case_adjudication_packet.py` | export the 2 adjudication rows from the focus review |
| `evals/aichat/validate_real_student_2case_adjudication_review.py` | validate completed 2-case adjudication workbook |
| `evals/aichat/integrate_real_student_2case_adjudication.py` | integrate completed adjudication into workflow status |

## Verification Commands Already Used

```bash
python3 evals/aichat/validate_real_student_2case_adjudication_review.py \
  .local_private/real_student_online_2case_adjudication_packet_human_adjudicated_20260520.xlsx

python3 evals/aichat/integrate_real_student_2case_adjudication.py
```

## Claim And Privacy Gate

| check | current result |
| --- | --- |
| 新增 dialogue-state v3 主实验 | no |
| 新增 main experiment condition | no |
| 重算 dialogue-state v3 主表 | no |
| 修改线上 AIChat / prompt / active mode | no |
| 改变学生可见回复 | no |
| 把 pilot 写成 main result | no |
| 把 pilot 写成 learning outcome study | no |
| 把 AI preliminary triage 写成 human evidence | no |
| 公开学生原文 / 完整代码 / 完整 AIChat 回复 | no |
| 公开 hash 明细 / hash salt / 可逆映射 | no |
| 公开 case-level labels | no |
| reportable case-level evidence after gate | 0 |

## Next Human Action

当前 human adjudication workflow 已闭环。下一步不是继续生成 case-level 结果，而是完成 ethics/privacy/data availability review 与 consent/reporting gate；在 gate 完成前，公开材料仍只能报告 workflow status 和 aggregate/process counts。
