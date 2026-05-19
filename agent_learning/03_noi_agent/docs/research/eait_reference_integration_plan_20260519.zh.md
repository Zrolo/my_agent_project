# EAIT Reference Integration Plan 20260519

## 使用边界

本文档只规划引用位置，不直接修改 manuscript，不新增正文 citation，不把外部论文作为主结果证据。所有引用进入正文前，还需要作者确认 citation key、版本、DOI 和 bibliography 格式。任何外部论文只能用于定位 Related Work、解释研究缺口或支持方法写作背景，不能替代 dialogue-state v3 evidence package。

## 总原则

- Results 不新增外部引用；结果段只引用本研究 evidence package。
- Discussion 可以少量引用，但仅用于教育技术含义的定位，不用于支撑主结果。
- Related Work 是主要 citation 承载区。
- Methods 只在解释 human review、rubric 或 calibration 背景时少量引用；不能让外部文献改变 evidence class。
- `eait_recent_001` 目前只有 closed-access Springer metadata/abstract HTML，未进入 style extraction；若正文引用，应只用于非常低负荷的背景句，并在投稿前用作者可访问版本或图书馆全文核验。

## Related Work 引用槽位

### 2.1 AI Tutoring / ITS For Programming

目标功能：说明 EAIT 接受 programming tutor / ITS / programming education 语境下的系统与评价研究；引出本文为什么不是通用 chatbot paper，而是 programming tutoring evaluation paper。

可放引用：

| 引用对象 | 用途 | 注意 |
| --- | --- | --- |
| Chrysafiadi et al. (2023) | ITS for computer programming；系统评价、适应性、学习结果的 EAIT 写法 | 来自 earlier EAIT pack，可作为 programming ITS anchor |
| Sharma & Harkishan (2022) | Programming ITS design 背景 | 用于“编程学习困难与 tutoring design” |
| Wang et al. (2023) | ITS 在真实教育情境中的应用复杂性 | 用于谨慎 evidence / context-sensitive evaluation |
| Garcia (2025) | ChatGPT programming education rapid review | 放在 programming education + GenAI 背景开头 |
| Güner & Er (2025) | Students interacting with ChatGPT in programming learning | 用于 learner-AI interaction 背景 |
| Gong et al. (2025) | GenAI dialogic feedback at programming problem-solving stages | 当前仅 metadata/abstract 可用；待全文核验后再决定是否放正文 |

建议正文槽位：

> Programming education studies have examined ITS design, AI feedback, and learner interaction with ChatGPT in programming learning. However, this literature mainly frames support at the level of systems, learning activities, or feedback stages, whereas the present study focuses on turn-level missing-bridge leakage.

### 2.2 LLM Feedback And Scaffolding

目标功能：说明生成式反馈可用于支持学习，但反馈强度、形式和时机需要设计；避免把“AI 会反馈”写成“AI 就是好 tutor”。

可放引用：

| 引用对象 | 用途 | 注意 |
| --- | --- | --- |
| Guo & Wang (2024) | ChatGPT feedback 与 teacher feedback 的差异 | 支持“AI feedback 不等于 teacher judgment” |
| Fokides & Peristeraki (2025) | AI 与 educator feedback 多维表现差异 | 支持 mixed evidence 叙述 |
| Ding, Zou, & Kohnke (2025) | ChatGPT as automated writing evaluation / feedback | 可用于 automated feedback / perception 背景 |
| Chen, Wang, & Huang (2026) | Adaptive feedback and feedback intervention theory | 用于 scaffold control / feedback intensity |
| Ma et al. (2025) DBox | Algorithmic programming scaffolding 近邻工作 | 不写成 faithful baseline reproduction |

建议正文槽位：

> Prior studies suggest that AI-generated feedback can support learners, but its pedagogical value depends on how feedback is timed, scoped, and interpreted. CP-MissingBridgeBench therefore evaluates not only whether a response avoids direct answers, but also whether it preserves the student's current reasoning work.

### 2.3 Rubric-Based Expert Evaluation

目标功能：正当化 case-specific rubric、human review、expert judgment 与 reliability reporting。

可放引用：

| 引用对象 | 用途 | 注意 |
| --- | --- | --- |
| González-Mujico (2024) | Rubric-based framework validation | 支持 rubric/expert assessment 背景 |
| Durgungoz & Durgungoz (2025) | AI-generated educational content + expert review | 支持“AI 输出需要专家质量审查” |
| Li et al. (2025) AI explanations for grading | Human graders + AI support 条件研究 | 用于 human-AI assessment support 背景 |
| Maurya et al. (2025) MRBench | Human-annotated tutor response evaluation taxonomy | 注意数学 tutoring / broad tutor dimensions 与本文不同 |

建议正文槽位：

> Because bridge leakage depends on student state and case context, CP-MissingBridgeBench follows an expert-review logic rather than treating automatic scores as sufficient evidence.

### 2.4 LLM Graders And Calibration

目标功能：解释为什么 LLM grader 只能 auxiliary，不能替代教练；把 calibration 放在合适学术背景里。

可放引用：

| 引用对象 | 用途 | 注意 |
| --- | --- | --- |
| Atasoy & Arani (2025) | ChatGPT as evaluator vs human raters | 支持 human rater stronger / AI assistant framing |
| Li et al. (2025) | GenAI explanations as auxiliary assessment support | 支持 AI support rather than replacement |
| Ding, Zou, & Kohnke (2025) | Automated writing evaluation background | 只作 automated evaluation 远邻 |
| Maurya et al. (2025) MRBench | LLM evaluator reliability / human annotation | 注意不把 MRBench 结论迁移成本研究结果 |

建议正文槽位：

> Work on AI-supported assessment motivates calibration, but the present evidence treats LLM graders as low-stakes auxiliary signals because high-risk critical-bridge leakage remains dependent on human judgment.

### 2.5 Algorithmic-Programming Scaffolding And Benchmarks

目标功能：把本文放入 algorithmic programming + AI tutor evaluation + leakage robustness 的交叉位置。

可放引用：

| 引用对象 | 用途 | 注意 |
| --- | --- | --- |
| Ma et al. (2025) DBox | 最接近 algorithmic programming scaffolding | 说明本文只用 DBox-inspired 单轮 baseline，不复现完整 DBox |
| Maurya et al. (2025) MRBench | AI tutor evaluation taxonomy | 说明本文是 CP-specific leakage construct，不是通用 tutor taxonomy |
| Yang et al. (2025) ELABORATION | Human-LLM competitive programming benchmark | 说明 CP 是 human-LLM 研究场景；不写成 tutoring evidence |
| Zhao, Knezevic, & Kaser (2026) | Answer leakage robustness | 用来区分 final-answer leakage 与 critical-bridge leakage |

建议正文槽位：

> Closely related benchmark work helps position CP-MissingBridgeBench as a CP-specific evaluation of tutoring leakage. Its target is not general task completion or final-answer disclosure alone, but the premature completion of a case-specific reasoning bridge.

## 不应放入正文主张的用法

- 不用任何 corpus paper 支撑 “Bridge Contract compact + Guard/Repair 更优”。
- 不用 DBox 论文证明 `dbox_inspired_clean` 是 faithful DBox reproduction。
- 不用 MRBench 证明 CP-MissingBridgeBench 覆盖所有 tutoring dimensions。
- 不用 answer-leakage robustness work 证明本文已评估 adversarial student attacks。
- 不用 AI grading papers 证明 LLM grader 可替代 coach。
- 不用 Gong et al. (2025) 的 closed-access metadata 作为强事实支撑。

## 建议 v0.4 引用集成策略

1. 先只在 Related Work 加 citation placeholders，不改 Results。
2. 每个小节控制在 3-5 个 citation，不做堆砌。
3. Introduction 只加 2-3 个背景引用：programming GenAI review、AI feedback/scaffolding、AI tutor evaluation。
4. Methods 最多加 1-2 个 rubric/human-review 背景引用。
5. Discussion 只在 “LLM graders remain auxiliary” 和 “Practical implications” 中加少量呼应引用。

## 投稿前核验清单

- BibTeX keys 已统一。
- DOI / page / year / journal 卷期已核验。
- closed-access 或 pre-copyedit 版本已标明来源。
- 所有新增 citation 都只服务于 Related Work / framing。
- 没有新增 empirical claim。
- 没有改变 evidence class。
