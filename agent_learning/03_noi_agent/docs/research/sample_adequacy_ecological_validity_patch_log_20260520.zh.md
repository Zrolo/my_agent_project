# Sample Adequacy And Ecological Validity Patch Log

Date: 2026-05-20

Scope: EAIT-facing manuscript and public real-student pilot documentation patch. This patch does not add experiments, does not add main experiment conditions, does not recompute dialogue-state v3 tables, does not modify online AIChat, and does not change evidence class.

## 1. Modified Files

### Manuscript

- `docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_6_sample_adequacy_ecological_validity.zh.md`
  - Created from `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_5_research_review_polished.zh.md`.
  - Rewrote the Abstract around a high-resolution, human-reviewed diagnostic benchmark for critical-bridge leakage in competitive-programming LLM tutoring.
  - Added `Sample Adequacy And Evidence Boundaries`.
  - Added an evidence hierarchy table distinguishing the fixed offline benchmark, the 31-case headline scaffold slice, sensitivity/appendix layers, and real-student AIChat ecological-validity layers.
  - Added a benchmark coverage table using existing dialogue-state v3 case metadata only.
  - Added a real-student AIChat ecological-validity appendix boundary.
  - Added ethics, privacy, data availability, and AI-writing disclosure wording.
  - Reinforced limitations around population prevalence, learning outcomes, deployed AIChat claims, and auxiliary LLM grader status.

- `docs/research/sample_adequacy_ecological_validity_patch_log_20260520.zh.md`
  - Added this patch log to connect each writing/template change to the relevant claim-gate risk and remaining human-review items.

### Public 5-Case Coach Review Template / Schema

- `docs/research/real_student_online_5case_coach_review_cn_schema_v2.json`
  - Added public template fields for problem context and scoring sufficiency.
  - Added allowed values for complete-problem-context, summary-sufficiency, full-statement-needed, summary-source, and current-AIChat-response field boundary.

- `docs/research/real_student_online_5case_coach_review_form_cn_v2.csv`
  - Regenerated the public CSV template with the new Chinese fields.
  - Kept only placeholders and non-sensitive workflow fields; no student raw text, complete code, complete AIChat replies, or identity information is included.

- `docs/research/real_student_online_5case_coach_review_form_cn_v2.xlsx`
  - Regenerated the public Excel template with Chinese dropdowns, comments, frozen panes, and conditional formatting.
  - Added the field label explaining that the current AIChat response is an observed online response, not an experimental condition.

- `docs/research/real_student_online_5case_coach_review_guide_cn_v2_20260520.zh.md`
  - Added coach-facing guidance for task summary, constraints/input-output summary, current student-state summary, context sufficiency, and full-problem-statement needs.
  - Added a boundary note: `当前AIChat回复（已脱敏）` means the online AIChat response already shown to the student; it is an observation item and not a baseline, condition, control, or Repair output.

- `docs/research/real_student_online_5case_coach_review_cn_v2_change_log_20260520.zh.md`
  - Recorded the context-field and current-AIChat boundary strengthening.

- `docs/research/real_student_online_5case_dry_run_execution_log_20260519.zh.md`
  - Recorded that the public Chinese coach-review template now separates problem context, student-state summary, and observed-current-AIChat field boundary.

### Public Template Scripts And Tests

- `evals/aichat/export_real_student_5case_coach_review_cn_xlsx.py`
  - Added the new Chinese columns, dropdown options, field comments, and dynamic conditional-formatting references.
  - Kept export behavior limited to the public 5-case template.

- `evals/aichat/validate_real_student_5case_coach_review_cn_v2.py`
  - Added validation requirements for reviewed rows with sufficient or partially sufficient context.
  - The validator does not require real identity fields and does not touch dialogue-state v3 main tables.

- `evals/aichat/tests/test_export_real_student_5case_coach_review_cn_xlsx.py`
  - Added checks for the new problem-context columns, dropdowns, guide text, and workbook layout.

- `evals/aichat/tests/test_validate_real_student_5case_coach_review_cn_v2.py`
  - Added checks that reviewed rows require the new problem-context and context-sufficiency fields when context is available.

## 2. Claim-Gate Risks Addressed

| risk | patch response |
| --- | --- |
| 50 cases could be criticized as small or overclaimed | v0.6 frames the 50 cases as high-cost, case-specific, human-reviewed diagnostic benchmark units, not a population-level prevalence sample. |
| 217 response-level reviews could be misread as 217 independent cases | v0.6 states that response-level reviews are nested within 31 case-level situations and uses same-case paired comparison language. |
| all-50 aggregate could be mistaken for headline result | v0.6 evidence hierarchy keeps the headline scaffold analysis on 31 cases / 217 response-level reviews and keeps remaining slices as sensitivity / appendix evidence. |
| real-student AIChat pilot could be mistaken for main result | v0.6 and the pilot appendix describe the online layer as ecological-validity / taxonomy-rubric transfer only, not a main result. |
| observed current AIChat response could be mistaken for an experimental condition | v0.6 and the coach-review guide label it as `observed_current_aichat_response` / `线上已展示 AIChat 回复（观察项，非实验条件）`. |
| pilot could be read as deployed-system superiority evidence | v0.6 explicitly says the pilot does not evaluate long-term learning outcomes, online active-mode effectiveness, or deployed AIChat superiority. |
| privacy-sensitive student material could leak through public review templates | public CSV/XLSX templates use placeholders and field schema only; no raw student text, complete code, complete AIChat replies, identity fields, hash salts, or reversible mappings are included. |
| coaches may be unable to judge context sufficiency | public template/schema now includes problem title/anonymous ID, task summary, constraints/input-output summary, current student-state summary, complete-context status, summary sufficiency, full-statement-needed, and summary source. |

## 3. Hard-Constraint Status

- 新增实验: no
- 新增 main experiment condition: no
- 重算 dialogue-state v3 主表: no
- 修改 dialogue-state v3 主实验数字: no
- 修改线上 AIChat / active mode / prompt / 学生可见回复: no
- 改变 evidence class: no
- 把 sensitivity / stress / calibration / pilot 写成 main result: no
- 把 all-50 aggregate 写成 headline: no
- 把 217 response-level reviews 写成独立 case-level 样本: no
- 写 Bridge Contract 显著或全面胜出: no
- 写 Guard-only 修复最终输出: no
- 写 Repair 主实验因果: no
- 写 LLM grader 替代人类教练: no
- 使用洛谷讨论区或第三方公开社区数据: no
- 公开学生原文、完整代码、完整 AIChat 回复、hash salt 或可逆映射: no

## 4. Verification Run

- Python compile check: passed for `export_real_student_5case_coach_review_cn_xlsx.py` and `validate_real_student_5case_coach_review_cn_v2.py`.
- Public 5-case unit tests: passed, `Ran 10 tests ... OK`.
- Public Chinese coach-review validator: passed with `ok=true`, `total_rows=5`, `reviewed_rows_count=0`, and `reportable_after_consent_count=0`; the expected consent/reporting warnings remain for all 5 public placeholder rows.
- Workbook structural inspection: passed; workbook has sheets `填写说明`, `教练复核表`, `下拉选项`, and `50-case字段对照`; the review sheet has 48 columns, 29 dropdown validation ranges, 13 conditional-formatting groups, and frozen pane `T2`.
- Public workbook sensitive-term scan: no hits for raw chat/code markers checked in the public workbook.
- Manuscript dangerous-phrase scan: no hits for `large-scale benchmark`, `217 independent`, `online condition`, `deployed superiority`, `learning outcome improvement`, `LLM grader can replace`, `Guard-only repairs`, or `Repair causally`.
- Citation-placeholder scan: 6 Related Work citation-placeholder groups remain in v0.6 and require manual verification before submission.

## 5. Items Still Requiring Human Confirmation

1. Citation placeholder verification: v0.6 still retains Related Work citation placeholders. These must be replaced only with manually verified formal citations, or removed/reworded before submission.
2. Result-number verification: all manuscript numbers should receive one final human cross-check against the evidence manifest and final tables before submission.
3. Ethics/privacy/data availability final review: the final submission should be reviewed for EAIT-specific disclosure wording and institutional requirements.
4. Real-student pilot consent/reporting gate: the 30 selected pilot candidate cases remain non-reportable as case-level evidence until consent/reporting requirements are complete.
5. `dialogue_v3_045_debugging_evidence` manual audit: the existing non-headline audit discrepancy should be either resolved by human review or kept outside submission-facing claims.
6. Public/private 5-case context summaries: the public template is schema-ready, but actual task summaries and student-state summaries require human-approved redacted content before coach scoring.
