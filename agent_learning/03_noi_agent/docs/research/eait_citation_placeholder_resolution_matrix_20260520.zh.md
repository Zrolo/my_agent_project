# EAIT Citation Placeholder Resolution Matrix 20260520

## 使用边界

本文档为 `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_10_submission_gate_hygiene.zh.md` 的 Related Work citation placeholders 提供核验进度和替换建议。它不新增实验、不修改数字、不改变 evidence class，也不自动把候选文献写入正式 bibliography。正式投稿前，作者仍需核对 BibTeX、DOI、作者拼写、卷页和期刊格式。

## Source Verification Status

| key | source status | verified facts | safe use | boundary |
| --- | --- | --- | --- | --- |
| `chrysafiadi2023fuzzyITS` | Springer EAIT verified | Published 2022-11-17; volume 28, pages 6453-6483; computer programming ITS; user experience/adaptivity/learning outcomes evaluation. | programming ITS evaluation framing | Do not use to claim our system improves learning outcomes. |
| `sharma2022pacificITS` | Springer EAIT verified | Published 2022-01-05; volume 27, pages 6197-6209; programming tutor / ITS design background. | programming tutor / ITS design background | Do not use as empirical support for our benchmark results. |
| `wang2023realContextITS` | Springer EAIT verified | Published 2023-01-07; volume 28, pages 9113-9148; systematic review of ITS in real educational contexts. | cautious real-context ITS evaluation framing | Do not use to frame our pilot as learning-outcome evidence. |
| `gong2025genAIDFProgramming` | Springer EAIT verified | Published 2024-12-09; volume 30, pages 9689-9709; GenAI dialogic feedback at programming problem-solving stages. | GenAI feedback in programming education | Do not use to claim our work evaluates staged learning gains. |
| `guner2025chatgptProgramming` | Springer EAIT verified | Published 2025-01-15; volume 30, pages 12681-12707; student interaction profiles with ChatGPT in programming learning. | ChatGPT interaction in programming learning | Do not use to claim online AIChat effectiveness. |
| `garcia2025chatgptProgrammingReview` | Springer EAIT verified | Published 2025-03-01; volume 30, pages 16721-16745; rapid review of ChatGPT in computer programming education. | programming education + ChatGPT review context | Do not use as evidence for CP missing-bridge leakage. |
| `guo2024chatgptTeacherFeedback` | Springer EAIT verified | Published 2023-08-29; volume 29, pages 8435-8463; ChatGPT vs teacher feedback in EFL writing. | AI feedback vs teacher feedback framing | Do not use to claim ChatGPT replaces teachers. |
| `fokides2025chatgptEducatorFeedback` | Springer EAIT verified | Published 2024-07-27; volume 30, pages 2577-2621; ChatGPT correction/feedback compared with educators. | mixed AI-vs-human feedback performance | Do not transfer language-writing results to CP tutoring performance. |
| `chen2026adaptiveFeedbackVR` | Springer EAIT verified | Published 2026-03-24; adaptive feedback in VR grounded in Feedback Intervention Theory. | adaptive feedback / feedback-strength framing | Not programming tutoring; use only for general feedback design background. |
| `gonzalezMujico2024rubricFrameworks` | Springer EAIT verified | Published 2023-12-13; volume 29, pages 13299-13324; validated rubric-based frameworks and external assessment. | rubric-based framework and rater reliability framing | Do not claim it validates our rubric. |
| `durgungoz2025aiGeneratedQuizzes` | Springer EAIT verified | Published 2025-09-19; volume 30, pages 25335-25357; expert review of AI-generated quiz question quality. | AI-generated content + expert quality review | Do not use to justify student outcome claims. |
| `li2025aiExplainsGrading` | Springer EAIT verified | Published 2025-09-08; volume 30, pages 24931-24964; human graders with AI assessment insights. | human-in-the-loop grading / AI support | Do not use to say AI graders replace educators. |
| `atasoy2025chatgptEvaluator` | Springer EAIT verified | Published 2025-04-25; volume 30, pages 20385-20415; human raters show stronger classification accuracy than AI systems. | AI evaluator remains auxiliary | Do not use to claim our DeepSeek grader is reliable. |
| `yusuf2025aivaluate` | Springer EAIT verified | Published 2025-09-03; volume 30, pages 24649-24693; LLM-augmented assessment agent and teacher burden. | teacher-burden / assessment-support framing | Do not use as evidence that our workflow reduces teacher burden. |
| `maurya2025mrbench` | ACL Anthology verified | NAACL 2025 long paper; pages 1234-1251; DOI `10.18653/v1/2025.naacl-long.57`; eight pedagogical dimensions; 192 conversations and 1,596 responses. | AI tutor evaluation taxonomy / human-annotated response evaluation | Math tutoring domain; not CP-specific leakage evidence. |
| `ma2025dbox` | DOI / DBLP / author PDF checked; ACM page still needs author-side final citation verification | DOI `10.1145/3706598.3713748`; CHI 2025; DBox co-decomposition. | algorithmic-programming scaffolding and DBox-inspired baseline positioning | Do not write faithful DBox reproduction or deployed DBox comparison. |
| `yang2025elaboration` | ACL Anthology verified | ACL 2025 long paper; pages 59-104; DOI `10.18653/v1/2025.acl-long.4`; human-LLM competitive programming benchmark. | CP human-LLM collaboration / benchmark context | Do not use to claim tutoring leakage or learning-effect evidence. |
| `zhao2026answerLeakage` | arXiv verified | arXiv:2604.18660; title, authors, date visible; adversarial student attacks and final-answer leakage robustness. | nearby-work contrast for final-answer leakage / adversarial attacks | Do not describe our work as answer-leakage robustness benchmark. |

## Placeholder Resolution Suggestions

| manuscript placeholder group | recommended verified citations | safe replacement pattern | still needs author action |
| --- | --- | --- | --- |
| `programming-ITS-evaluation; programming-ITS-design; real-context-ITS-review; programming-GenAI-review; ChatGPT-programming-interaction` | `chrysafiadi2023fuzzyITS`; `sharma2022pacificITS`; `wang2023realContextITS`; `gong2025genAIDFProgramming`; `guner2025chatgptProgramming`; `garcia2025chatgptProgrammingReview` | Cite programming ITS and programming GenAI literature as education-technology context for feedback and tutoring evaluation. | Verify `sharma2022pacificITS` page and final BibTeX. |
| `ChatGPT-teacher-feedback-comparison; AI-feedback-mixed-dimensions; automated-feedback-perception; adaptive-feedback-design; algorithmic-programming-scaffolding` | `guo2024chatgptTeacherFeedback`; `fokides2025chatgptEducatorFeedback`; `chen2026adaptiveFeedbackVR`; `gong2025genAIDFProgramming`; `ma2025dbox` | Cite AI feedback as useful but uneven across dimensions; cite adaptive feedback as design-sensitive. | Confirm whether to include non-programming feedback papers in main Related Work or only Discussion. |
| `rubric-framework-validation; AI-generated-content-expert-review; human-AI-assessment-support; tutor-response-human-annotation` | `gonzalezMujico2024rubricFrameworks`; `durgungoz2025aiGeneratedQuizzes`; `li2025aiExplainsGrading`; `maurya2025mrbench` | Cite rubric/expert-review papers for human criteria, reliability, and expert assessment workflows. | Ensure no sentence implies these validate CP-MissingBridgeBench labels. |
| `final-answer-leakage-under-student-attacks` | `zhao2026answerLeakage` | Use as adjacent contrast: adversarial student attacks and final-answer / complete-solution leakage. | If arXiv-only citation is undesirable for EAIT, mark as preprint and keep contrast modest. |
| `DBox; algorithmic-programming-scaffolding; AI-tutor-evaluation-taxonomy; human-LLM-competitive-programming-benchmark` | `ma2025dbox`; `maurya2025mrbench`; `yang2025elaboration` | Position DBox as co-decomposition scaffold, MRBench as tutor-evaluation taxonomy, and ELABORATION as CP human-LLM benchmark context. | Final-verify DBox ACM BibTeX before use; do not make ELABORATION a tutoring-leakage precedent. |
| `AI-evaluator-human-raters; AI-assessment-support; automated-writing-evaluation; LLM-evaluator-reliability` | `atasoy2025chatgptEvaluator`; `li2025aiExplainsGrading`; `guo2024chatgptTeacherFeedback`; `fokides2025chatgptEducatorFeedback`; `maurya2025mrbench` | Support auxiliary AI-grader framing and human-review necessity. | Keep our DeepSeek calibration as task-specific evidence; do not outsource reliability claim to prior work. |

## Draft Replacement Rule

When creating `v0.11_citation_ready`, replace placeholders only with author-approved citation keys. If a placeholder group has no fully approved citation yet, either keep a visible TODO or rewrite the sentence to remove the external factual dependency.

## Remaining Citation Risks

1. DBox official ACM metadata still needs final author-side verification because automated access to ACM content was restricted.
2. ELABORATION ACL Anthology metadata has been checked, but the author should still decide whether it belongs in main Related Work or an appendix-level CP benchmark context paragraph.
3. Answer Leakage Robustness is currently arXiv 2026; it should be cited as preprint unless a venue appears.
4. Several EAIT 2025/2026 papers are very recent; final issue/page/DOI metadata should be checked immediately before submission.
5. The manuscript should not become a citation dump. Related Work should keep the current prior-work -> gap -> our position structure.
