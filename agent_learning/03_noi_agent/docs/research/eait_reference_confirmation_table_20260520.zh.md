# EAIT Reference Confirmation Table 20260520

## 使用边界

本文档用于把 v0.11 中的 `candidate citation keys pending author approval` 转成作者可审阅的引用确认表。它不新增实验、不修改数字、不改变 evidence class，也不自动把任何文献写入正式投稿稿。正式进入 manuscript / bibliography 前，作者需要逐条确认 `author_decision`。

## 作者确认表

| citation_key | default_recommendation | manuscript_location | source_status | safe_use | claim_gate_boundary | author_decision |
| --- | --- | --- | --- | --- | --- | --- |
| `chrysafiadi2023fuzzyITS` | keep_main | 2.1 AI tutoring / ITS for programming | DOI/Crossref verified | Programming ITS evaluation framing. | Do not use to claim CP-MissingBridgeBench improves learning outcomes. | keep |
| `sharma2022pacificITS` | keep_main_or_trim | 2.1 AI tutoring / ITS for programming | DOI/Crossref verified | Programming tutor / ITS design background. | Design/background only; not empirical support for our benchmark results. | delete |
| `wang2023realContextITS` | keep_main | 2.1 AI tutoring / ITS for programming; limitations | DOI/Crossref verified | Real-context ITS evaluation caution. | Do not frame the pilot as learning-outcome evidence. | keep |
| `gong2025genAIDFProgramming` | keep_main | 2.1 and 2.2 | DOI/Crossref verified | GenAI feedback in programming problem solving. | Do not claim our benchmark evaluates staged learning gains. | keep |
| `guner2025chatgptProgramming` | keep_main | 2.1 AI tutoring / ITS for programming | DOI/Crossref verified | ChatGPT interaction in programming learning. | Do not use to claim current AIChat effectiveness. | keep |
| `garcia2025chatgptProgrammingReview` | keep_main_or_trim | 2.1 AI tutoring / ITS for programming | DOI/Crossref verified | Broad ChatGPT programming education review context. | Do not use as direct evidence for critical-bridge leakage. | appendix |
| `guo2024chatgptTeacherFeedback` | keep_main | 2.2 LLM feedback; 2.6 grader calibration | DOI/Crossref verified | AI feedback vs teacher feedback framing. | Do not claim ChatGPT replaces teacher feedback. | keep |
| `fokides2025chatgptEducatorFeedback` | keep_main_or_trim | 2.2 LLM feedback; 2.6 grader calibration | DOI/Crossref verified | Mixed AI-vs-educator feedback framing. | Writing domain only; do not transfer results to CP tutoring performance. | delete |
| `chen2026adaptiveFeedbackVR` | appendix_or_discussion | 2.2 LLM feedback and scaffolding | DOI/Crossref verified; online-first | General adaptive feedback / feedback-strength framing. | Non-programming VR context; use only as general design background. | appendix |
| `gonzalezMujico2024rubricFrameworks` | keep_main | 2.3 Rubric-based expert evaluation | DOI/Crossref verified | Rubric-based framework and external assessment framing. | Do not claim it validates our rubric. | keep |
| `durgungoz2025aiGeneratedQuizzes` | appendix_or_trim | 2.3 Rubric-based expert evaluation | DOI/Crossref verified | Expert review of AI-generated educational content. | Do not use for student outcome claims. | appendix |
| `li2025aiExplainsGrading` | keep_main_or_trim | 2.3 expert evaluation; 2.6 LLM graders | DOI/Crossref verified | Human-in-the-loop AI grading support. | Do not say AI graders replace educators. | keep |
| `atasoy2025chatgptEvaluator` | keep_main | 2.6 LLM graders and calibration | DOI/Crossref verified | AI evaluator versus human rater framing. | Supports auxiliary framing, not DeepSeek reliability. | keep |
| `yusuf2025aivaluate` | appendix_or_discussion | Discussion / teacher burden if needed | DOI/Crossref verified | Teacher-burden and AI-supported assessment workflow. | Do not claim our workflow reduces teacher burden. | appendix |
| `maurya2025mrbench` | keep_main | 2.3 and 2.5/2.6 | DOI/Crossref verified | AI tutor evaluation taxonomy and human-annotated tutor response evaluation. | Math tutoring domain; not CP-specific leakage evidence. | keep |
| `ma2025dbox` | keep_main | 2.2 and 2.5 DBox positioning | DOI/Crossref verified | Algorithmic-programming co-decomposition scaffold comparison point. | Do not claim faithful DBox reproduction or deployed DBox comparison. | keep |
| `yang2025elaboration` | appendix_or_short_main | 2.5 CP benchmark context | DOI/Crossref verified | Human-LLM competitive programming benchmark context. | Do not use as tutoring-leakage or learning-effect evidence. | appendix |
| `zhao2026answerLeakage` | keep_main_as_preprint | 2.4 Answer leakage and tutor robustness | arXiv verified from existing log; no DOI used | Adjacent contrast for adversarial final-answer leakage. | Do not describe our work as an answer-leakage robustness benchmark. | keep |

## 推荐压缩策略

为避免 EAIT Related Work 变成 citation dump，建议每个小节只保留最能支撑 gap statement 的 2-4 篇：

1. 2.1 可优先保留 `chrysafiadi2023fuzzyITS`, `wang2023realContextITS`, `gong2025genAIDFProgramming`, `guner2025chatgptProgramming`；`sharma2022pacificITS` 和 `garcia2025chatgptProgrammingReview` 可按篇幅保留或删减。
2. 2.2 可优先保留 `guo2024chatgptTeacherFeedback`, `fokides2025chatgptEducatorFeedback`, `gong2025genAIDFProgramming`, `ma2025dbox`；`chen2026adaptiveFeedbackVR` 更适合 Discussion 或 appendix。
3. 2.3 可优先保留 `gonzalezMujico2024rubricFrameworks`, `li2025aiExplainsGrading`, `maurya2025mrbench`；`durgungoz2025aiGeneratedQuizzes` 可删减。
4. 2.4 保留 `zhao2026answerLeakage`，但标明 preprint / adjacent work。
5. 2.5 保留 `ma2025dbox` 和 `maurya2025mrbench`；`yang2025elaboration` 可作为 CP benchmark context 的一句短引或 appendix。
6. 2.6 保留 `atasoy2025chatgptEvaluator`, `li2025aiExplainsGrading`, `maurya2025mrbench`；避免把 AI feedback papers 重复堆到评分段落。

## 仍需人工确认

1. 是否接受 arXiv preprint `zhao2026answerLeakage` 进入正式 EAIT bibliography。
2. DBox 的 ACM/CHI 元数据是否按 DOI/Crossref 条目直接采用。
3. 是否保留 online-first 且暂无卷页的 `chen2026adaptiveFeedbackVR`。
4. 是否删除与 CP 编程 tutoring 距离较远的 AI-generated quizzes / teacher burden 文章。
5. 最终 citation style 使用 APA、Springer basic author-year，还是 LaTeX `\cite{}`。

## Author-decision pass 20260520

本版本把 `author_decision` 从 TODO 改为 keep / appendix / delete。决策原则：主文只保留能直接支撑 gap statement、method framing 或 non-overlap boundary 的文献；领域背景、弱相关或容易造成 citation dump 的文献移入 appendix 或删除。该 pass 不新增实验、不改主实验数字、不改变 evidence class。

### Main-text keep

`chrysafiadi2023fuzzyITS`, `wang2023realContextITS`, `gong2025genAIDFProgramming`, `guner2025chatgptProgramming`, `guo2024chatgptTeacherFeedback`, `gonzalezMujico2024rubricFrameworks`, `li2025aiExplainsGrading`, `atasoy2025chatgptEvaluator`, `maurya2025mrbench`, `ma2025dbox`, `zhao2026answerLeakage`.

### Appendix/background only

`garcia2025chatgptProgrammingReview`, `chen2026adaptiveFeedbackVR`, `durgungoz2025aiGeneratedQuizzes`, `yusuf2025aivaluate`, `yang2025elaboration`.

### Delete from current manuscript bibliography unless specifically needed

`sharma2022pacificITS`, `fokides2025chatgptEducatorFeedback`.

### Remaining caution

`zhao2026answerLeakage` is kept as an adjacent preprint contrast only; it must not make CP-MissingBridgeBench look like an answer-leakage robustness benchmark. `ma2025dbox` is kept only for DBox/non-overlap positioning; do not claim faithful DBox reproduction.
