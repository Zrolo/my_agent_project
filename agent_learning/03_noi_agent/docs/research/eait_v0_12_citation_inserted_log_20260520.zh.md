# EAIT v0.12 Citation Inserted Log 20260520

## 输入依据

本轮依据用户提供的严格 author-decision pass 执行：

- keep: `chrysafiadi2023fuzzyITS`, `wang2023realContextITS`, `gong2025genAIDFProgramming`, `guner2025chatgptProgramming`, `guo2024chatgptTeacherFeedback`, `gonzalezMujico2024rubricFrameworks`, `li2025aiExplainsGrading`, `atasoy2025chatgptEvaluator`, `maurya2025mrbench`, `ma2025dbox`, `zhao2026answerLeakage`
- appendix: `garcia2025chatgptProgrammingReview`, `chen2026adaptiveFeedbackVR`, `durgungoz2025aiGeneratedQuizzes`, `yusuf2025aivaluate`, `yang2025elaboration`
- delete: `sharma2022pacificITS`, `fokides2025chatgptEducatorFeedback`

## 修改文件

1. `eait_reference_confirmation_table_20260520.zh.md`
   - 将 `author_decision` 从 TODO 更新为 keep / appendix / delete。
   - 追加 Author-decision pass 说明。

2. `paper_submission_manuscript_dialogue_state_v3_nonoverlap_framing_v0_12_citation_inserted.zh.md`
   - 基于 v0.11 创建。
   - 将 Related Work 中的候选 citation key 标记替换为正文 `\cite{...}`。
   - 正文只使用 keep 文献。
   - appendix/delete 文献未进入正文引用。

3. `eait_v0_12_references_draft_20260520.bib`
   - 从 18 条候选文献压缩为 11 条 main-text keep 文献。
   - 删除当前主文 bibliography 中的 appendix/delete 文献。

4. `eait_v0_12_references_draft_20260520.zh.md`
   - 改为 main-text keep-only reference list。
   - 明确列出 appendix/background only 与 deleted 文献。

## Related Work 引用分配

| section | inserted citation keys |
| --- | --- |
| 2.1 AI tutoring / ITS for programming | `chrysafiadi2023fuzzyITS`, `wang2023realContextITS`, `gong2025genAIDFProgramming`, `guner2025chatgptProgramming` |
| 2.2 LLM feedback and scaffolding | `gong2025genAIDFProgramming`, `guo2024chatgptTeacherFeedback`, `ma2025dbox` |
| 2.3 Rubric-based expert evaluation | `gonzalezMujico2024rubricFrameworks`, `li2025aiExplainsGrading`, `maurya2025mrbench` |
| 2.4 Answer leakage and tutor robustness | `zhao2026answerLeakage` |
| 2.5 Algorithmic-programming scaffolding and DBox | `ma2025dbox`, `maurya2025mrbench` |
| 2.6 LLM graders and calibration | `atasoy2025chatgptEvaluator`, `li2025aiExplainsGrading`, `maurya2025mrbench` |

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
| 是否写 Bridge Contract 显著或全面胜出 | no |
| 是否写 Guard-only 修复最终输出 | no |
| 是否写 Repair 主实验因果 | no |
| 是否写 LLM grader 替代人类教练 | no |
| 是否把 `zhao2026answerLeakage` 写成本文同类 benchmark | no |
| 是否把 `ma2025dbox` 写成 faithful reproduction | no |

## Remaining TODO

1. 作者最终确认 EAIT / Springer citation style。
2. 作者确认 arXiv preprint `zhao2026answerLeakage` 是否可进入正式投稿 bibliography。
3. 作者最终核对 DBox 的 ACM/CHI BibTeX。
4. 投稿前仍需 result-number verification、ethics/privacy/data availability final review。
