# Paper Abstract / Conclusion Draft: Dialogue-State v3 20260518

## 使用边界

本文档提供 dialogue-state v3 论文的摘要和结论投稿安全草稿。它不新增实验、不修改数据、不接入线上 active mode。所有表述遵循 `dialogue_state_v3_paper_claims_final_gate_20260518.zh.md`。

核心边界：

- 这是一篇 evaluation-framework paper，不是线上部署系统论文。
- 主 headline 只使用 31-case `main_scaffold_eval` slice。
- 50-case evidence package 是 formal human-review evidence candidate，不是 final gold。
- Guard-only 是 instrumentation，不是 final-response rewrite。
- Repair 因果证据来自 same-candidate stress test，不来自主实验 condition 均值本身。
- LLM grader 只能作为 auxiliary signal，不能替代人类教练。

## Candidate Title

```text
CP-MissingBridgeBench:
Turn-Level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation
for LLM Tutors in Competitive Programming
```

## Abstract Draft

Large language models are increasingly used as programming tutors, but avoiding final code or direct answers is not sufficient for pedagogically safe help. In competitive programming, a short hint can still reveal the key intermediate reasoning step the student should derive next. We call this local reasoning gap a missing bridge, and define critical bridge leakage as prematurely completing that bridge without necessarily giving the full solution.

We introduce CP-MissingBridgeBench, a turn-level evaluation framework for LLM tutors in competitive programming. Each case includes problem context, recent dialogue, a student message, and a case-specific rubric specifying success criteria, forbidden content, acceptable reveal, and the expected next student action. Our dialogue-state v3 evidence package contains 50 reviewed candidate cases, 7 anonymized tutoring-harness conditions, and 350 AI responses double-reviewed by two coaches with priority adjudication, paired uncertainty, slice analysis, Repair same-candidate stress testing, DBox+Repair fairness sensitivity, and DeepSeek LLM-grader calibration.

The evidence shows that CP-MissingBridgeBench reveals quality-safety-burden trade-offs across tutoring harnesses. DBox-inspired decomposition is a strong baseline; no-direct-solution prompting does not eliminate critical bridge leakage; and Bridge Contract compact + Guard/Repair shows favorable overall-quality and high-severity leakage-control trends under the primary human-review view. At the same time, student-ready and rank judgments are rater-sensitive, Guard-only is only instrumentation in the current pipeline, Repair reduces leakage in same-candidate stress testing with a student-burden trade-off, and LLM graders remain auxiliary rather than replacements for human review.

## 中文摘要草稿

大语言模型正在被用于编程辅导，但“不直接给代码或最终答案”并不等于教学上安全。在算法竞赛辅导中，一个很短的提示也可能提前说穿学生本应自己推出的关键中间推理。我们将学生当前理解到下一步有效解题动作之间缺失的局部推理称为 missing bridge，并将未给完整题解或代码、但提前补完该桥梁的行为定义为 critical bridge leakage。

我们提出 CP-MissingBridgeBench，一个面向算法竞赛 LLM Tutor 的 turn-level 评测框架。每条 case 包含题目上下文、近期对话、学生当前问题，以及 case-specific rubric，明确 success criteria、forbidden content、acceptable reveal 和 expected student next action。dialogue-state v3 evidence package 包含 50 条 reviewed candidate cases、7 个匿名 tutoring-harness conditions 和 350 条 AI responses，由两位教练完成全量盲评，并配套 priority adjudication、paired uncertainty、slice analysis、Repair same-candidate stress test、DBox+Repair fairness sensitivity 和 DeepSeek LLM-grader calibration。

当前证据支持克制结论：CP-MissingBridgeBench 能揭示不同 tutoring harness 的 quality-safety-burden trade-off；DBox-inspired decomposition 是强 baseline；no-direct-solution prompting 不能消除 critical bridge leakage；Bridge Contract compact + Guard/Repair 在主人工评审口径下呈现有利的整体质量和高严重度泄露控制趋势。同时，student-ready 和 rank 对评分者口径敏感，Guard-only 在当前 pipeline 中只是 instrumentation，Repair 的因果证据来自 same-candidate stress test 且伴随 student-burden trade-off，LLM grader 只能作为辅助信号。

## Short Abstract Draft

We introduce CP-MissingBridgeBench, a turn-level evaluation framework for LLM tutors in competitive programming. The benchmark focuses on missing bridges: local reasoning gaps between a student's current understanding and the next useful solving action. It also defines critical bridge leakage, where a tutor avoids full code or final answers but prematurely reveals the key intermediate reasoning the student should infer. In dialogue-state v3, 50 reviewed cases, 7 anonymized tutor harnesses, and 350 AI responses are evaluated by two coaches with priority adjudication, paired uncertainty, stress testing, and LLM-grader calibration. The evidence supports a trade-off claim: DBox-inspired decomposition is a strong baseline, no-direct-solution prompting is not safety-complete, and Bridge Contract compact + Guard/Repair shows favorable quality and high-severity leakage-control trends, while rater sensitivity, Repair burden trade-offs, and automatic-grader limitations remain important.

## Conclusion Draft

本文认为，算法竞赛辅导需要比 direct answer / code leakage 更细的评测对象。核心教学风险往往是局部的：Tutor 可以不泄露最终答案，却仍然补完学生当前最需要自己跨过的 missing bridge。CP-MissingBridgeBench 通过 case-specific rubric、人类盲评和证据分层报告，把这个风险变成可标注、可复核的评测对象。

dialogue-state v3 evidence package 支持三个主要结论。第一，该 benchmark 能揭示 generic helpfulness 或 no-direct-solution 检查看不到的 quality-safety-burden trade-off。第二，强 baseline 很重要：DBox-inspired decomposition 表现稳健，no-direct-solution prompting 相比 prompt-only 更强，但仍可能出现 critical bridge leakage。第三，Bridge Contract compact + Guard/Repair 在主人工评审口径下呈现有利的 overall quality 和 high-severity leakage control 趋势，但应解释为 bounded trend，而不是全面显著胜出。

这项研究也明确了当前证据不能证明什么。50-case set 不是算法竞赛辅导全覆盖。Coach labels 和 priority60 adjudication 是 expert reference views，不是 final gold。Guard-only 在主实验中提供 runtime leakage signal，但不改写 final response。Repair 的因果证据来自 same-candidate stress test，其中 leakage severity 改善，但 student burden 可能上升。DeepSeek-backed LLM grader 可以作为辅助信号，但 critical leakage 漏检风险太高，不能替代人类评审。

后续工作应扩展 benchmark 的题型、学生状态和真实对话分布；对 rater-sensitive outcomes 做更充分的多评审裁决；在必要时补全 repair-enabled baseline comparison；并改进 critical bridge leakage 的自动评审，同时不能把自动评审当成 gold。当前贡献是一个可复核的 evaluation framework 和 evidence package，用于研究如何在 LLM tutoring 中保留学生的 missing bridge，而不是宣称某个 tutor harness 已经完整解决算法竞赛辅导。

## Paper-Safe Closing Sentence

```text
CP-MissingBridgeBench turns missing-bridge preservation and critical-bridge leakage into auditable evaluation objects, enabling more precise analysis of how LLM tutoring harnesses trade off helpfulness, safety, and student reasoning burden.
```

## 不安全摘要 / 结论写法

不要写：

- Bridge Contract significantly outperforms all baselines.
- Guard-only fixes or rewrites final student-visible responses.
- Repair causality is proven by the main experiment alone.
- priority60 adjudication is final gold.
- The 50-case set covers all competitive-programming tutoring situations.
- DeepSeek or any LLM grader can replace human coaches.
