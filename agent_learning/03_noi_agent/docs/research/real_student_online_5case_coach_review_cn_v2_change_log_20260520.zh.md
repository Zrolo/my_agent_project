# Real-Student Online 5-Case Coach Review 中文 v2 Change Log 20260520

## 修改内容

- 新增中文教练可填表模板：`real_student_online_5case_coach_review_form_cn_v2.csv`。
- 新增中文 schema：`real_student_online_5case_coach_review_cn_schema_v2.json`。
- 新增中文填写说明：`real_student_online_5case_coach_review_guide_cn_v2_20260520.zh.md`。
- 新增中文校验脚本：`validate_real_student_5case_coach_review_cn_v2.py`。
- 新增中文校验测试：`test_validate_real_student_5case_coach_review_cn_v2.py`。
- 生成本地私有中文 5-case 教练复核表：`.local_private/real_student_online_5case_coach_review_packet_cn_v2_20260520.csv`。

## 为什么修改

原 v1 表格更像 schema / audit packet，字段偏内部，教练不容易直接填写。v2 将评分区改为 dialogue-state v3 / 50-case 人审口径，包括 7 个 0/1/2 小分、泄露标签、总体质量、是否愿意给学生看、学生回答负担、复核信心和备注。

pilot validity 字段仍保留，但放在评分区之后，用于检查真实学生对话是否能映射到现有 cognitive bridge family、surface anchor 和 case-specific rubric。

## 与 50-case 的关系

v2 的 response-level 评分字段对齐 50-case 人审维度：

- `coach_bridge_identification_score`
- `coach_groundedness_score`
- `coach_scaffold_appropriateness_score`
- `coach_bridge_leakage_control_score`
- `coach_next_step_clarity_score`
- `coach_single_focus_coherence_score`
- `coach_bridge_oriented_micro_example_score`
- `coach_micro_example_applicability`
- `coach_leakage_label`
- `coach_overall_quality_score`
- `coach_would_show_to_student`
- `student_response_burden`
- `coach_reviewer_confidence`
- `coach_needs_discussion`
- `coach_notes`

新增的 taxonomy / pilot 字段不替代 50-case 评分维度，只用于 ecological validity check。

## 中文填写约束

- 教练可选值全部使用中文。
- 教练备注要求使用中文。
- 不要求教练填写英文 enum。
- 校验器会拒绝把 `minor_bridge_leakage` 等英文内部标签直接填入中文表。

## Claim Gate

| check | result |
| --- | --- |
| 是否新增主实验 | no |
| 是否新增主实验 condition | no |
| 是否修改 dialogue-state v3 主表 | no |
| 是否改变 evidence class | no |
| 是否改变线上 AIChat 回复 | no |
| 是否把 5-case pilot 写成 main result | no |
| 是否把 pending-consent cases 写成 reportable evidence | no |
| 是否公开学生原文/代码/AI 回复 | no |

## 当前状态

中文 v2 私有表仍处于未复核状态：`reviewed_rows_count=0`，`reportable_after_consent_count=0`。所有 5 个 cases 的知情/报告门仍为待完成，因此不能作为公开 deep-pilot evidence。
