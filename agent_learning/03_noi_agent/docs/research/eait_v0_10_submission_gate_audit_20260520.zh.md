# EAIT v0.10 Submission Gate Audit 20260520

## 审阅对象

- `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_10_submission_gate_hygiene.zh.md`
- `paper_claims_final_submission_gate_20260519.zh.md`
- `real_student_online_pilot_workflow_status_20260520.zh.md`
- `real_student_online_post_adjudication_public_status_20260520.zh.md`

本 audit 不新增实验、不新增 condition、不重算 dialogue-state v3 主表、不修改线上 AIChat、不替换正式 citation。它只记录投稿前风险状态。

## Executive Summary

v0.10 的 claim-gate 状态总体安全。稿件继续把主 headline 限定在 31-case `main_scaffold_eval` / 217 response-level reviews；all-50 aggregate 被写成 sensitivity / appendix evidence；real-student AIChat pilot 被写成 ecological-validity / workflow layer；9-case focus review 与 2-case adjudication 已内部闭环，但 `reportable case-level evidence = 0`。

当前最大 blocker 仍是 Related Work 的 citation placeholders。v0.10 中共有 7 处 `citation placeholders`，正式投稿前必须由作者完成 citation verification pass，不能直接带占位符投稿，也不能用未经核验的正式 citation 静默替换。

## Claim-Gate Audit

| gate | status | notes |
| --- | --- | --- |
| 不新增 dialogue-state v3 主实验 | pass | v0.10 只改写 manuscript，不改实验。 |
| 不新增 main experiment condition | pass | real-student workflow 明确不是 condition comparison。 |
| 不重算 dialogue-state v3 主表 | pass | 未运行主表重算；稿件数字沿用既有 evidence package。 |
| 不把 all-50 aggregate 写成 headline | pass | v0.10 将 all-case sensitivity 改成 appendix-only fragility check，不再写 ranking-style sentence。 |
| 不把 217 response-level reviews 写成 independent cases | pass | 稿件多处说明 217 是 nested response-level reviews。 |
| 不写显著全面胜出 | pass | Bridge Contract + Guard/Repair 写成 favorable / bounded / trend-level。 |
| 不写 Guard-only 修复最终输出 | pass | Guard-only 被写成 instrumentation / runtime signal。 |
| 不写 Repair 主实验因果 | pass | Repair 因果只限 same-candidate stress evidence。 |
| 不写 LLM grader 替代人类 | pass | DeepSeek grader 被写成 auxiliary calibration。 |
| 不把 Coach A/B/priority60 写成 final gold | pass | 只写 expert reference views / sensitivity。 |
| 不把 real-student pilot 写成 main result | pass | 只写 workflow closure / ecological-validity layer。 |
| 不报告 real-student case-level labels | pass | `reportable case-level evidence = 0`。 |

## Remaining Blockers

### Blocker 1: Citation placeholders remain

v0.10 仍有 7 处 citation placeholders：

1. `programming-ITS-evaluation; programming-ITS-design; real-context-ITS-review; programming-GenAI-review; ChatGPT-programming-interaction`
2. `ChatGPT-teacher-feedback-comparison; AI-feedback-mixed-dimensions; automated-feedback-perception; adaptive-feedback-design; algorithmic-programming-scaffolding`
3. `rubric-framework-validation; AI-generated-content-expert-review; human-AI-assessment-support; tutor-response-human-annotation`
4. `final-answer-leakage-under-student-attacks`
5. `DBox; algorithmic-programming-scaffolding; AI-tutor-evaluation-taxonomy; human-LLM-competitive-programming-benchmark`
6. `AI-evaluator-human-raters; AI-assessment-support; automated-writing-evaluation; LLM-evaluator-reliability`
7. AI writing disclosure line mentions citation placeholders as author responsibility.

Required action: replace each placeholder with author-verified formal citations or remove/soften the sentence. Do not add unverified citations.

### Blocker 2: Ethics/privacy/data availability wording still needs venue-specific finalization

The current draft is directionally safe: raw dialogue text, student code, full AIChat responses, identity fields, hash salts, reversible mappings, and identifiable examples are excluded from public release. However, EAIT submission still needs final human review of data availability wording, consent/reporting gate language, and whether any supplementary material is public or restricted.

### Blocker 3: Result-number verification remains required

The current manuscript preserves existing numbers, including 50 / 350 / 31 / 217 and 1156 / 87 / 578 / 137 / 59 / 30 / 11 / 15. Before submission, the author should still complete `result_number_verification_log.csv`.

## Citation Verification: Source Check Started

The following source checks were started from official pages. They are not yet formal manuscript references until the author approves citation keys and bibliography format.

| candidate | verified source status | safe use | boundary |
| --- | --- | --- | --- |
| Gong, Li & Qiao, `Impact of generative AI dialogic feedback on different stages of programming problem solving` | Springer EAIT page verified: published 2024-12-09; volume 30, pages 9689-9709; authors and abstract visible. | programming education + GenAI feedback / problem-solving stages | Do not use to claim our benchmark evaluates learning gains. |
| Güner & Er, `AI in the classroom: Exploring students’ interaction with ChatGPT in programming learning` | Springer EAIT page verified: open access; published 2025-01-15; volume 30, pages 12681-12707; authors and abstract visible. | ChatGPT interaction patterns in programming learning | Do not use to claim our current AIChat is effective or improves learning. |
| Wang et al., `Examining the applications of intelligent tutoring systems in real educational contexts` | Springer EAIT page verified: published 2023-01-07; volume 28, pages 9113-9148; abstract describes real-context ITS review. | cautious real-context ITS evaluation framing | Do not use to justify pilot as learning-outcome evidence. |
| Maurya et al., `Unifying AI Tutor Evaluation` / MRBench | ACL Anthology page verified: NAACL 2025 long paper; pages 1234-1251; DOI and BibTeX visible. | AI tutor evaluation taxonomy / human-annotated tutor-response evaluation | Domain is math tutoring; do not use as CP-specific leakage evidence. |
| DBox | DOI / ACM source still needs author-side verification; automated fetch hit ACM access restriction. | algorithmic-programming co-decomposition related work after verification | Do not write faithful reproduction or deployed DBox comparison. |

## Reviewer-Risk Notes

1. Related Work is structurally good but not submission-ready until placeholders are replaced.
2. Real-student AIChat material is now safer than before because it is framed as workflow closure with `reportable case-level evidence = 0`.
3. The abstract is long and information-dense. Before final EAIT polishing, consider whether Real-AIChat-100 and Replay-30/50 should stay in the abstract or move to Methods/Appendix to reduce perceived over-scoping.
4. The full 30-case packet has not received full human review. The manuscript correctly says the 9-case focus/adjudication workflow is closed internally, not that the full 30-case packet is fully reviewed.
5. No-direct-answer insufficiency is supported only within the reviewed CP tutoring slice and should remain scoped that way.

## Recommended Next Patch

1. Do a citation verification pass using official publisher pages / PDFs / BibTeX.
2. Create `v0.11_citation_ready` only after the author approves citation keys.
3. Keep claim-gate wording unchanged unless citation replacement forces sentence-level narrowing.
4. Do not report private real-student distributions unless consent/reporting gate changes.
