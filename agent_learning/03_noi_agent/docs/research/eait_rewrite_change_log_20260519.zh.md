# EAIT Rewrite Change Log 20260519

## 输入与输出

- Source skeleton: `docs/research/paper_submission_manuscript_dialogue_state_v3_20260519.zh.md`
- Dynamic writing skill: `docs/research/dynamic_writing_skill_eait_cp_missingbridgebench_20260519.md`
- Output manuscript: `docs/research/paper_submission_manuscript_dialogue_state_v3_eait_v0_1.zh.md`

## 重排章节

| 原 skeleton 章节 | EAIT v0.1 处理 |
| --- | --- |
| 1. Abstract | 改为 180-240 word English abstract，采用 context-gap-method-finding-boundary 结构。 |
| 2. Introduction | 改为 tutoring tension 开头，并前置 missing bridge / critical bridge leakage 的教育技术问题。 |
| 3. Related Work | 重排为 5 段：AI tutoring / ITS for programming；LLM feedback and scaffolding；rubric-based expert evaluation；LLM graders and calibration；algorithmic-programming scaffolding and benchmarks。 |
| 4. Task Definition | 合并进 `Methods / Evaluation` 的 benchmark construct。 |
| 5. CP-MissingBridgeBench / Dialogue-State v3 | 合并进 `Methods / Evaluation` 的 cases and slices。 |
| 6. Systems and Baselines | 合并进 `Methods / Evaluation` 的 7 offline human-review harnesses。 |
| 7. Human Review Protocol | 合并进 `Methods / Evaluation` 的 blind review protocol。 |
| 8. Main Results | 改写为 Results 中的 main scaffold evaluation、pairwise uncertainty and sensitivity。 |
| 9. Repair Same-Candidate Stress Test | 放入 Results 的 stress-test subsection，明确 evidence class 为 stress test。 |
| 10. DBox+Repair Fairness Sensitivity | 放入 Results 的 targeted sensitivity subsection，明确不是 main condition。 |
| 11. LLM Grader Calibration | 放入 Results 的 auxiliary calibration subsection，明确不能替代 human review。 |
| 12. Discussion | 改写为教育技术启示：no-direct-answer insufficient、case-specific human judgment、repair burden trade-off、LLM graders auxiliary。 |
| 13. Limitations | 合并为 Discussion 的 Limitations subsection。 |
| 14. Ethics, Data Governance, and AI Writing Disclosure | 保留为独立短节。 |

## Claim Gate 检查

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| 是否新增 claim | no | 仅重排和改写已有 claim，未引入新的实证主张。 |
| 是否改数字 | no | 数字均来自现有 evidence docs，未修改数值。 |
| 是否新增 citation | no | Related Work 只按主题组织，未新增 citation key 或 bibliography 条目。 |
| 是否改变 evidence class | no | main / sensitivity / stress / calibration / taxonomy boundaries 均保留。 |
| 是否把 sensitivity / stress / calibration 写成 main result | no | Results 开头和相关小节均显式标注 evidence class。 |
| 是否写显著全面胜出 | no | Bridge Contract 只写 favorable but bounded trends / trade-off。 |
| 是否写 Guard-only 修复最终输出 | no | Guard-only 明确写为 guard-instrumented / runtime leakage signal。 |
| 是否写 Repair 主实验因果 | no | Repair 因果只来自 same-candidate stress test；主实验均值只作为 condition-level trend。 |
| 是否写 Coach labels 是 final gold | no | Coach A/B 和 priority60 均写为 expert reference / adjudicated sensitivity views。 |
| 是否写 LLM grader 可替代人类 | no | LLM grader 写为 auxiliary low-stakes signal；human review remains necessary。 |
| 是否违反 claim gate | no | 已按 `paper_claims_final_submission_gate_20260519.zh.md` 的 forbidden wording 边界改写。 |

## 保留的人工待办

- 投稿前仍需人工核验 citation checklist 和 BibTeX；本次改写未新增 citation。
- 投稿前仍需用 `result_number_verification_log.csv` 核验每个进入正式稿的数字。
- 若要转成 camera-ready English manuscript，需要逐节翻译并再次运行 forbidden wording scan。

