# CP-MissingBridgeBench v4.1 20-case Dev Selection Audit（2026-05-22）

## 1. 目的

本审计记录 v4.1 的 20-case dev stabilization 清单。该清单只用于 prompt 稳定、schema 稳定、JSON 解析、Tutor 具体性、Guard 标签一致性和 Repair 定点修复检查。

该清单不作为论文结果，不进入 100-case final evaluation，不用于声称 v4.1 优于 DBox-inspired + Guard，也不修改任何现有主实验。

## 2. 输入来源

来源文件：

`docs/research/cp_missingbridgebench_v2_100case_source_selection_manifest_v2_2_all_sufficient_20260521.csv`

该来源清单包含 100 个 context-sufficient v2 source cases。当前 dev 清单只使用元数据字段，不包含学生原文、完整代码、完整 AIChat 回复、hash salt 或可逆映射。

## 3. 输出文件

`docs/research/cp_missingbridgebench_v4_20case_dev_selection_manifest_20260522.csv`

字段包括：

- `dev_case_id`
- `source_v2_selection_id`
- `source_candidate_turn_id`
- `source_real_aichat_case_id`
- `rough_bridge_family`
- `surface_anchor`
- `help_seeking_type`
- `context_sufficiency`
- `privacy_review_status`
- `consent_reporting_gate`
- `public_reporting_allowed`
- `dev_selection_bucket`
- `dev_use`
- `frozen_for_prompt_tuning`
- `must_not_use_for_holdout`
- `selection_reason`
- `notes_no_raw_text`

## 4. 分层抽样结果

| family | selected |
|---|---:|
| debugging_bridge | 5 |
| implementation_bridge | 5 |
| data_structure_bridge | 3 |
| aggregation_contribution_bridge | 3 |
| correctness_bridge | 1 |
| boundary_order_bridge | 1 |
| state_representation_bridge | 1 |
| policy_bridge | 1 |
| total | 20 |

Help-seeking type distribution:

| help-seeking type | selected |
|---|---:|
| debugging | 8 |
| implementation | 7 |
| conceptual_hint | 4 |
| code_request | 1 |

Privacy status:

| privacy_review_status | selected |
|---|---:|
| passed | 15 |
| pending | 5 |

Consent/reporting gate:

| field | value |
|---|---|
| consent_reporting_gate | all pending |
| public_reporting_allowed | all no |

## 5. 选择规则

本清单使用 deterministic stratified dev selection：

1. 先覆盖 v2 中占比最高的 implementation/debugging 场景。
2. 再覆盖 data-structure 与 aggregation 场景。
3. 最后保留 correctness、boundary order、state representation、policy/direct-answer 等稀有或边界场景。
4. 每个 family 内优先选择 `privacy_review_status=passed` 的行。
5. 稀有 family 无 passed 行时，保留 pending 行，但只能用于内部 dev，不公开 case-level 内容。
6. 不按 observed AIChat response 好坏选择。
7. 不按 Bridge Contract / Repair 是否可能表现好选择。
8. 不按论文结论是否有利选择。

## 6. 使用边界

这些 20 个 case 是 dev set：

- 可以用于修改 v4.1 prompt。
- 可以用于检查 JSON / schema / generation chain。
- 可以用于 AI-preliminary triage。
- 不可以作为 holdout。
- 不可以作为 final result。
- 不可以公开 case-level 内容。
- 不可以进入论文主结论。

CSV 中 `must_not_use_for_holdout=yes` 用于防止后续误用。

## 7. 下一步

1. 使用 `cp_missingbridgebench_v4_prompt_freeze_draft_v0_1_20260522.md` 生成 20-case dev responses。
2. 对 dev responses 做自动完整性检查：row count、JSON parse、empty response、schema drift。
3. 做 AI-preliminary review 仅用于失败定位。
4. 根据 dev failure 修改 prompt。
5. prompt 稳定后创建 v4.1 prompt-freeze audit。
6. 冻结后再选 30-case holdout，且不得从本 20-case dev 清单中抽取。

## 8. 未触碰事项

本次没有：

- 修改 dialogue-state v3 主实验。
- 新增 main experiment condition。
- 重算主表。
- 修改线上 AIChat、prompt、active mode 或学生可见回复。
- 新增 Real-AIChat 结果。
- 公开学生原文、完整代码或完整 AIChat 回复。
- 将 AI preliminary review 写成人类教练评审。
