# Submission Draft Skeleton: Dialogue-State v3 20260519

## 使用边界

本文档是投稿准备阶段的 manuscript skeleton，不是论文终稿。它按章节给出写作目标、当前已有证据、允许使用的 claim、禁止使用的 claim 和待人工补写内容。它不新增实验、不修改结果。

## 1. Abstract

- 写作目标：用克制的一段话说明评测问题、benchmark 贡献、人审设置和有边界的发现。
- 当前已有证据：50 个 reviewed cases、7 个 conditions、350 条 responses、双教练评审、priority60 adjudication、paired uncertainty、stress / sensitivity / calibration reports。
- 允许使用的 claim：CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring。
- 禁止使用的 claim：某个 tutor harness 完全解决 CP tutoring 或显著全面优于所有 baseline。
- 待人工补写内容：确定字数、venue style，以及是否加入数值亮点。

## 2. Introduction

- 写作目标：说明 missing bridge 和 critical bridge leakage 是 no-direct-answer rules 之后仍存在的学习/安全失败。
- 当前已有证据：task definition docs、result tables、no-direct-solution baseline 行为。
- 允许使用的 claim：no-direct-code / no-direct-solution prompting 不等于没有 critical bridge leakage。
- 禁止使用的 claim：已有 tutoring systems 都是 weak strawmen，或本工作已经解决全部问题。
- 待人工补写内容：加入核验后的引用和一个简洁 motivating example。

## 3. Related Work

- 写作目标：定位 AI tutoring、programming-help assistants、DBox-inspired decomposition、LLM-as-judge 和 agent-eval methodology。
- 当前已有证据：citation checklist 和 candidate citation IDs。
- 允许使用的 claim：prior work motivates baselines and evaluation dimensions。
- 禁止使用的 claim：声称 faithful reproduction of DBox、CodeHelp、CodeAid、EDF/Copa 或其他相关系统，除非 settings 完全匹配。
- 待人工补写内容：打开每篇 cited source，核验 BibTeX，并更新 `citation_verification_log.csv`。

## 4. Task Definition: Missing Bridge and Critical Bridge Leakage

- 写作目标：定义 missing bridge、critical bridge leakage、acceptable reveal、forbidden content 和 expected student next action。
- 当前已有证据：`evaluation_protocol_v3`、`response_review_rubric_v3`、taxonomy revision summary。
- 允许使用的 claim：critical bridge leakage 可以在没有直接给代码或完整题解时发生。
- 禁止使用的 claim：taxonomy 是 universal 或完整覆盖所有 CP tutoring。
- 待人工补写内容：润色定义，并加入一个不暴露敏感证据的例子。

## 5. CP-MissingBridgeBench / Dialogue-State v3

- 写作目标：描述 50-case dialogue-state v3 evidence candidate、slice structure 和 case-specific rubric workflow。
- 当前已有证据：reviewed candidate JSONL、context readiness audit、paper table source。
- 允许使用的 claim：主 headline 使用 31-case `main_scaffold_eval` slice。
- 禁止使用的 claim：all 50 cases 是 headline 或完整覆盖 CP tutoring。
- 待人工补写内容：决定 dataset detail 放主文还是 appendix。

## 6. Systems and Baselines

- 写作目标：解释 7 个 offline human-review harnesses 及其解释边界。
- 当前已有证据：baseline protocol、methods/evaluation draft、table source。
- 允许使用的 claim：DBox-inspired decomposition 是 strong baseline；Guard-only variants 是 guard-instrumented。
- 禁止使用的 claim：Guard-only rewrites final output；DBox-inspired 是 faithful DBox reproduction。
- 待人工补写内容：压缩 condition descriptions 以适配主文表格。

## 7. Human Review Protocol

- 写作目标：解释 blind review、Coach A/B 全量评分、priority60 adjudication、agreement 和 sensitivity reporting。
- 当前已有证据：human-review result packet、reliability draft、agreement report。
- 允许使用的 claim：Human review and adjudication remain necessary。
- 禁止使用的 claim：Coach A、Coach B 或 priority60 是 final gold。
- 待人工补写内容：决定 agreement metrics 放主文还是 appendix。

## 8. Main Results

- 写作目标：展示 main scaffold table、paired W/T/L、uncertainty 和 slice sensitivity。
- 当前已有证据：paper-ready tables、pairwise report、reproduction JSON、table source。
- 允许使用的 claim：Bridge Contract compact + Guard/Repair 在 primary view 下呈现 favorable overall-quality 和 high-severity leakage-control trends。
- 禁止使用的 claim：significant dominance、stable advantage 或 comprehensive superiority over all baselines。
- 待人工补写内容：把 markdown tables 转成 venue-ready tables，并用 `result_number_verification_log.csv` 核验每个数字。

## 9. Repair Same-Candidate Stress Test

- 写作目标：把 Repair 因果证据和主实验 condition means 分开。
- 当前已有证据：repair same-candidate stress result 和 workbook summary。
- 允许使用的 claim：Repair 在 fixed-candidate stress testing 中降低 leakage severity，但有 student-burden trade-off。
- 禁止使用的 claim：Repair causality 由主实验均值证明，或 Repair fully solves leakage。
- 待人工补写内容：决定 stress-test details 放主文还是 appendix。

## 10. DBox+Repair Fairness Sensitivity

- 写作目标：回应 DBox-inspired baseline 也加 Repair 是否公平的问题，但不把它升格成主实验 condition。
- 当前已有证据：20-case targeted DBox+Repair fairness report。
- 允许使用的 claim：DBox+Repair 是 targeted fairness sensitivity。
- 禁止使用的 claim：它是 full 50-case double-coach main validation。
- 待人工补写内容：除非篇幅允许短段落，否则放 appendix。

## 11. LLM Grader Calibration

- 写作目标：说明 LLM grader 只能辅助，不能替代人类评审。
- 当前已有证据：DeepSeek calibration report 和 reproduced key metrics。
- 允许使用的 claim：case-specific LLM grader 可提供 auxiliary low-stakes signals，但不能替代 coaches。
- 禁止使用的 claim：LLM grader 是 gold 或可单独裁决 critical leakage。
- 待人工补写内容：引用 LLM-as-judge work，清楚报告 critical false-negative risk，并说明 DeepSeek calibration 存在 backend coupling，不是 cross-backend validation。GPT-5.4 cross-backend calibration 应放在 future work 或 revision add-on。

## 12. Discussion

- 写作目标：把 benchmark 解释为 evaluation framework 和 trade-off analysis。
- 当前已有证据：results/discussion draft、claim gate、observed taxonomy。
- 允许使用的 claim：当前证据支持 bounded trends 和 methodological lessons。
- 禁止使用的 claim：system victory、universal benchmark coverage 或 product deployment validation。
- 待人工补写内容：加入对 CP tutoring research 和 benchmark design 的启示。

## 13. Limitations

- 写作目标：明确、正面地写出限制。
- 当前已有证据：reliability report、slice analysis、DBox+Repair sensitivity、LLM grader calibration。
- 允许使用的 claim：rater sensitivity、50-case coverage、targeted add-ons 和 automatic-grader limitations 仍然存在。
- 禁止使用的 claim：限制很小或不影响主解释。
- 待人工补写内容：按目标 venue 调整措辞。

## 14. Ethics, Data Governance, and AI Writing Disclosure

- 写作目标：说明数据边界、人类评审责任和 AI writing assistance。
- 当前已有证据：AI writing disclosure log、human revision checklist、citation/result verification logs。
- 允许使用的 claim：AI 辅助 drafting/editing/checklist generation；人类核验 claim 并负责。
- 禁止使用的 claim：AI 是作者或科学证据来源。
- 待人工补写内容：按 venue policy 调整 disclosure，并核验 privacy/data statements。
