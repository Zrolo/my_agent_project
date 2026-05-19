# External Review Gate-Repair Log 20260519

## 修订来源

本次修订基于外部 AI 审阅反馈，目标是降低投稿前 claim-gate、privacy/consent gate、sample-unit transparency 和 non-overlap framing 风险。修订不修改 dialogue-state v3 主实验，不新增主实验 condition，不重算主表，不改变线上 AIChat 回复，也不改变 evidence class。

## 输出文件

- `docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_6_review_gate_repair.zh.md`
- `docs/research/real_student_candidate_screening_summary_20260519.json`
- `docs/research/real_student_candidate_screening_summary_20260519.zh.md`
- `docs/research/real_student_candidate_screening_summary_template_20260519.zh.md`
- `docs/research/real_student_online_candidate_screening_execution_log_20260519.zh.md`
- `docs/research/real_student_online_candidate_screening_schema_v1.json`
- `docs/research/real_student_online_deep_sample_selection_protocol_20260519.zh.md`
- `docs/research/real_student_online_pilot_validity_plan_20260519.zh.md`
- `docs/research/real_student_online_privacy_consent_checklist_20260519.zh.md`
- `docs/research/real_student_online_reporting_template_20260519.zh.md`
- `evals/aichat/validate_real_student_candidate_screening.py`
- `evals/aichat/summarize_real_student_candidate_screening.py`

## 主要修订

1. Pilot reporting gate:
   - 将 “30 selected deep cases / deep annotation sample” 的公开口径改为 “30 selected pilot candidate cases pending consent/reporting gate”。
   - 明确当前 `consent_eligibility=pending` 时，30 条不能写成可公开报告的 deep-pilot evidence、学生示例或个案结论。
   - 保留原有数字：1156 message rows、87 sessions、578 paired turns、137 candidate turns、59 candidate sessions、30 selected candidate cases、11 hashed students、15 hashed problems。

2. Hash privacy:
   - summary script 和生成的 public-facing summary 不再列出逐个 `student_id_hash` / `problem_id_hash`。
   - 改为报告 aggregate coverage 与 distribution summary，例如 unique covered、min/median/max cases per hashed id、count distribution。
   - 仍保留 screening CSV 的 hash 字段用于内部审计，但论文/公开补充材料不应展示逐个 hash 表。

3. Validator hardening:
   - 新增 `candidate_turn_id` 唯一性检查。
   - 新增 selected count 检查，默认 expected selected = 30。
   - 新增非 selected 行必须填写 `exclusion_reason`。
   - 保留 selected 行必须有 `candidate_selection_reason`、`privacy_review_status=passed`、`consent_eligibility` 不为 `not_eligible`。
   - 新增 warning：selected candidate 在 `consent_eligibility=eligible` 前不是 reportable deep-pilot evidence。

4. Manuscript v0.6:
   - 将 DBox 相关表述进一步限定为 “DBox-inspired offline single-turn baseline”，明确不是 DBox deployed system 或 faithful reproduction。
   - 将 Abstract 中 “Against final-answer leakage work...” 改为更中性的 “In contrast to...”。
   - 新增 evidence hierarchy table，区分 50 cases、350 outputs、31/217 headline slice、19/133 non-main slices、137 screening pool、30 pending pilot candidates。
   - 降格 all-case sensitivity：不再在 Results 主文写成 all-case ranking 支持，只作为 appendix sensitivity 检查。
   - 新增 Ethics, Privacy, Data Availability, And AI Writing Disclosure 小节，明确敏感数据不公开、公开材料只含聚合统计/schema/scripts/consent-approved paraphrased examples。
   - 对 `dialogue_v3_045_debugging_evidence` 改成非 headline、原 audit slice retained、内部 discrepancy log，不在投稿稿中保留 `needs_manual_audit` 字样。

## 未完成项

Citation placeholders 仍未替换为正式文献引用。本次没有新增未经人工核验的 citation，也没有把 placeholders 擅自替换成正式引用。投稿前仍需要人工 citation verification pass：每个 placeholder 只能替换为已核验 citation，或删除对应外部文献主张，或改成不依赖外部事实的定位句。

## Claim Gate

| check | result |
| --- | --- |
| 是否新增实验 | no |
| 是否新增主实验 condition | no |
| 是否修改数字 | no |
| 是否重算 dialogue-state v3 主表 | no |
| 是否改变 evidence class | no |
| 是否改变线上 AIChat / active mode / prompt / 学生可见回复 | no |
| 是否把 sensitivity / stress / calibration / pilot 写成 main result | no |
| 是否把 Coach A/B/priority60 写成 final gold | no |
| 是否把 all-50 aggregate 写成 headline | no |
| 是否把 217 tutor responses 写成 217 independent cases | no |
| 是否写 Bridge Contract 显著全面胜出 | no |
| 是否写 Guard-only 修复最终输出 | no |
| 是否写 Repair 主实验因果 | no |
| 是否写 LLM grader 替代人类教练 | no |
| 是否使用第三方公开社区数据 | no |
| 是否新增未经核验正式 citation | no |
