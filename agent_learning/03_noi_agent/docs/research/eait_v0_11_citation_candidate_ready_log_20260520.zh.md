# EAIT v0.11 Citation Candidate Ready Log 20260520

## 修改范围

本轮基于 `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_10_submission_gate_hygiene.zh.md` 创建：

- `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_11_citation_candidate_ready.zh.md`

同步参考：

- `eait_citation_placeholder_resolution_matrix_20260520.zh.md`
- `citation_verification_log.csv`

## 主要修改

1. 将 Related Work 中 6 处 `citation placeholders` 替换为 `candidate citation keys pending author approval`。
2. 将 AI writing disclosure 中的 `citation placeholders` 改为 `candidate citation keys`。
3. 保留 Related Work 的原有结构：prior work -> limitation/gap -> our position。
4. 未加入正式 bibliography，未把候选 citation keys 视为作者已终审 citation。

## Claim Gate 检查

| 项目 | 结果 |
| --- | --- |
| 是否新增实验 | no |
| 是否新增 main condition | no |
| 是否修改 dialogue-state v3 主实验数字 | no |
| 是否重算主表 | no |
| 是否改变 evidence class | no |
| 是否把 pilot / replay 写成 main result | no |
| 是否把 all-50 写成 headline | no |
| 是否把 217 responses 写成 independent cases | no |
| 是否写显著全面胜出 | no |
| 是否写 Guard-only 修复最终输出 | no |
| 是否写 Repair 主实验因果 | no |
| 是否写 LLM grader 替代人类教练 | no |
| 是否新增未经核验正式 citation | no；仅加入 candidate citation keys pending author approval |

## Candidate Citation Key Groups

| Related Work group | candidate keys |
| --- | --- |
| AI tutoring / ITS for programming | `chrysafiadi2023fuzzyITS`; `sharma2022pacificITS`; `wang2023realContextITS`; `gong2025genAIDFProgramming`; `guner2025chatgptProgramming`; `garcia2025chatgptProgrammingReview` |
| LLM feedback and scaffolding | `guo2024chatgptTeacherFeedback`; `fokides2025chatgptEducatorFeedback`; `chen2026adaptiveFeedbackVR`; `gong2025genAIDFProgramming`; `ma2025dbox` |
| Rubric-based expert evaluation | `gonzalezMujico2024rubricFrameworks`; `durgungoz2025aiGeneratedQuizzes`; `li2025aiExplainsGrading`; `maurya2025mrbench` |
| Answer leakage and tutor robustness | `zhao2026answerLeakage` |
| Algorithmic-programming scaffolding and DBox | `ma2025dbox`; `maurya2025mrbench`; `yang2025elaboration` |
| LLM graders and calibration | `atasoy2025chatgptEvaluator`; `li2025aiExplainsGrading`; `guo2024chatgptTeacherFeedback`; `fokides2025chatgptEducatorFeedback`; `maurya2025mrbench` |

## Remaining Human Checks

1. 作者需要决定哪些 candidate keys 进入正式 bibliography。
2. DBox 的 ACM BibTeX 仍需作者终审；当前只把 DOI/arXiv/外部元数据作为候选核验基础。
3. Answer Leakage Robustness 当前按 arXiv preprint 处理，若投稿前已有正式 venue，应更新。
4. EAIT 2025/2026 文章在投稿前需要最终核对卷、期、页码、DOI、作者拼写。
5. v0.11 仍不是最终投稿稿；它是 citation-candidate-ready draft。
