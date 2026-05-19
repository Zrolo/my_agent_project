# Research Paper Writing Review Polish Log 20260519

## 输入与输出

- 输入稿件：`docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_4_sample_unit_clarity.zh.md`
- 输出稿件：`docs/research/paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_5_research_review_polished.zh.md`
- 本日志：`docs/research/research_paper_writing_review_polish_log_20260519.zh.md`

## Mini-Outline

- Problem: LLM tutors can help CP learners too much by crossing the learner's missing reasoning bridge.
- Construct: critical bridge leakage is evaluated at the case-specific tutoring-turn level.
- Method: 50 case-level situations, 350 response-level outputs, 7 anonymized offline harnesses, blind human review, and evidence-class hierarchy.
- Main evidence: the 31-case `main_scaffold_eval` slice, corresponding to 217 response-level reviews.
- Supporting evidence: rater sensitivity, paired uncertainty, stress/fairness sensitivity, error taxonomy, and LLM-grader calibration.
- Boundary: no online-system claim, no all-50 headline, no final gold labels, no LLM-grader replacement claim.

## Review Findings

| Issue | Severity | Fix |
| --- | --- | --- |
| Main manuscript began with an internal `使用边界` section, which reads like a working note rather than a paper section. | medium | Removed from the paper body; boundary information is preserved in this log. |
| Abstract was slightly over the earlier 180-240 word EAIT target and had one avoidable phrase. | medium | Compressed wording without changing numbers or claims. |
| Results contained repeated `Appendix candidate:` labels, which look like drafting notes. | medium | Rewrote them as formal appendix-routing sentences. |
| Phrases such as `evidence package` and `paper-facing calibration` sounded like internal audit language. | low | Replaced with `evaluation set` and `calibration reported here`. |
| Appendix note for `dialogue_v3_045_debugging_evidence` used reviewer-facing but still informal wording. | low | Reframed as an `Audit note`; did not reassign slice. |

## Claim-Evidence Map

| Claim | Evidence | Status |
| --- | --- | --- |
| Critical bridge leakage is distinct from final-answer disclosure. | Task definition, running binary-search example, case-specific rubric fields. | supported |
| Main scaffold headline uses 31 case-level situations and 217 response-level reviews. | Slice table and Methods unit-of-analysis paragraph. | supported |
| All-50 aggregate is not the headline. | Methods slice table, Results opening, evidence hierarchy. | supported |
| DBox-inspired decomposition is a strong offline baseline. | Main scaffold table and bounded discussion of DBox-inspired conditions. | supported |
| Bridge Contract compact + Guard/Repair shows favorable but bounded trends. | Main scaffold table plus paired uncertainty boundaries. | supported |
| Repair has stress evidence but not main-experiment causal proof. | Same-candidate stress section and explicit evidence boundary. | supported |
| LLM graders remain auxiliary. | DeepSeek calibration section, critical recall 0 and major FN 1.000. | supported |

## Self-Review Checklist

| Dimension | Status | Note |
| --- | --- | --- |
| Contribution clarity | pass | The paper now foregrounds a case-specific human-review benchmark for critical-bridge leakage. |
| Writing clarity | pass with remaining work | Citation placeholders still need formal replacement before submission. |
| Experimental strength | pass within evidence boundary | Claims remain bounded to existing evidence; no new experiments were added. |
| Evaluation completeness | pass within current package | Sensitivity/stress/calibration are kept as supporting evidence. |
| Method design soundness | pass with caveat | `dialogue_v3_045_debugging_evidence` remains flagged for manual audit rather than silently reassigned. |

## Claim Gate 检查

| 检查项 | 结果 |
| --- | --- |
| 是否新增实验 | no |
| 是否修改数字 | no |
| 是否改变 evidence class | no |
| 是否重新分配 slice | no |
| 是否把 all-50 写成 headline | no |
| 是否把 217 tutor responses 写成 217 independent cases | no |
| 是否违反 claim gate | no |
