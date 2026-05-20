# Real-Student Online 5-Case Human Coach Review Status Log 20260520

## 修改文件

- 新增 `docs/research/real_student_online_5case_human_coach_review_public_status_20260520.zh.md`
- 新增 `docs/research/real_student_online_5case_human_coach_review_public_status_20260520.json`

## 私有输入

- 已审核工作簿：`/Users/kongyouli/Downloads/real_student_online_5case_coach_review_packet_cn_v7_human_coach_reviewed_20260520.xlsx`
- 整理后的私有工作簿：`.local_private/real_student_online_5case_human_coach_reviewed_cleaned_20260520.xlsx`
- 私有校验摘要：`.local_private/real_student_online_5case_human_coach_reviewed_validation_20260520.json`
- 私有聚合摘要：`.local_private/real_student_online_5case_human_coach_reviewed_summary_20260520.zh.md`

这些私有文件不得提交到 Git，也不得公开学生原文、完整代码、完整 AIChat 回复、case-level labels、教练逐例备注、hash salt 或可逆映射。

## 公开状态口径

公开文档只记录：

- 5 个 dry-run cases 已完成人类教练内部复核；
- 结构校验错误为 0；
- privacy review status 为可内部复核的 case 数为 5；
- consent/reporting gate 仍为待完成的 case 数为 5；
- reportable case-level evidence 数为 0；
- score / leakage distributions 在 gate 完成前保持 suppressed。

## 服务的风险控制

| risk | mitigation |
| --- | --- |
| 把 5-case dry run 写成 main result | public status 明确 process status only |
| 把 observed current AIChat response 写成 condition/baseline | public status 明确禁止 |
| consent gate 未完成却公开 case-level labels | public status suppresses labels and score distributions |
| 将 pilot 写成 learning outcome | public status 明确禁止 learning outcome / learning gains |
| 污染 dialogue-state v3 主表 | public status 明确 no recomputation / no merge |
| 隐私泄露 | public status excludes raw text, full code, full response, hashes and mappings |

## Claim Gate

| check | result |
| --- | --- |
| 是否新增 dialogue-state v3 主实验 | no |
| 是否新增 main experiment condition | no |
| 是否重算 dialogue-state v3 主表 | no |
| 是否修改线上 AIChat / prompt / active mode | no |
| 是否改变 evidence class | no |
| 是否公开 case-level labels | no |
| 是否公开学生原文 / 完整代码 / 完整 AIChat 回复 | no |

## 后续人工事项

1. 完成 consent/reporting gate 后，决定哪些 aggregate distributions 可以进入 appendix。
2. 若要公开 paraphrased examples，需另走隐私复核和人工改写流程。
3. 若要扩大到 30 cases，先复用当前 split workbook 结构，并保持 observed current AIChat response = 观察项、非实验条件。
4. 不将 5-case 或 30-case pilot 并入 dialogue-state v3 主实验表。
