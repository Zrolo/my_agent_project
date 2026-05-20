# Real-AIChat External Validation Method Alignment

Date: 2026-05-20

## 使用边界

本文档只为 CP-MissingBridgeBench / EAIT 论文提供外部验证方案的写作与执行边界。它不修改 dialogue-state v3 主实验，不新增 main experiment condition，不重算主表，不修改线上 AIChat、prompt、active mode 或学生可见回复，也不把 pilot / replay / trajectory subset 写成学习效果实验。

## A1. 方法论来源说明

本方案对齐的是 AI+教育论文中常见的验证流程，而不是臆想一个新的线上实验。可对齐的流程包括：

- authentic student interactions + rubric-based coding + human validation：先用真实学生交互作为输入，再用明确 rubric 和人工复核判断教育构念是否可标注。
- authentic tutoring questions + multiple LLM outputs + expert assessment：在真实 tutoring question 上离线生成多个候选输出，由专家盲评其教学适切性。
- teacher/expert-in-the-loop feedback evaluation：同一学生输入上提供多个 AI feedback options，由教师或专家选择、比较或评分。
- offline evaluation before deployment：先进行离线评估和隐私审查，再讨论是否有条件进入 shadow 或 active。
- real trajectory analysis as ecological-validity evidence：用真实多轮上下文检查单轮标注构念在真实对话中的可解释性。

可作为流程对齐对象但暂不作为正式 bibliography 的方向包括：StudyChat、CSTutorBench、teacher-in-the-loop feedback / DPO feedback、Teacher-Authored Prompts for Student-AI Dialogue、REFINE，以及 ACL 2026 Answer Leakage Robustness。由于这些 citation 尚未在本项目中完成正式人工核验，当前文稿只能把它们列为 citation verification TODO，不能直接放入 manuscript references。

## A2. 方法边界

这些文献流程只支持我们的实验结构选择：authentic input、offline multi-output generation、expert rubric assessment、human validation 和 deployment 前的离线审查。它们不支持我们写 learning outcome claim，也不支持写 randomized deployment、student achievement comparison 或 deployed system superiority。

因此，本项目只借鉴流程，不借鉴超出证据边界的主张：

- 我们模仿 authentic input + offline multi-output generation + expert rubric assessment。
- 我们不模仿 learning outcome study。
- 我们不做 randomized deployment。
- 我们不比较学生长期成绩。
- 如果没有正式 citation verification，不把这些文献作为正式引用放入 manuscript references。

## A3. Non-Overlap 表

| nearby work / frame | student behavior | leakage object | setting | unit of analysis | evaluation authority | claim type | what we do not claim |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ACL 2026 Answer Leakage Robustness | adversarial student attacks designed to elicit answers | final answers / complete solutions | tutor robustness under attack | attack episodes or tutor responses under attack | robustness benchmark labels / evaluators | answer-leakage robustness | We do not claim an adversarial robustness benchmark, and we do not reduce critical-bridge leakage to final-answer leakage. |
| DBox / co-decomposition scaffolding | learner collaborates with an LLM-supported decomposition scaffold | decomposition steps and step-tree support | algorithmic-programming learning system | learner-task interaction or decomposition artifact | study protocol / participant evaluation | co-decomposition scaffold system evidence | We do not reproduce DBox, do not evaluate the DBox deployed system, and do not claim DBox is weak. |
| CP-MissingBridgeBench | ordinary CP tutoring help-seeking, not adversarial attacks | intermediate critical reasoning bridge that the learner has not yet crossed | turn-level competitive-programming LLM tutoring | case-specific dialogue state and tutor response | human coaches using case-specific rubrics; LLM judges only auxiliary | diagnostic benchmark for pedagogical bridge preservation | We do not claim deployed AIChat superiority, student achievement gains, final gold labels, or a general AI education safety benchmark. |

## A4. Strict Reviewer Diagnosis

A strict reviewer would likely object under the following failure modes:

| risky move | likely reviewer diagnosis | required prevention |
| --- | --- | --- |
| Real-AIChat-100 is written as a 7-harness comparison | reject-level design confusion | State that Real-AIChat-100 is observational ecological-validity validation only. |
| `observed_current_aichat_response` is written as a baseline condition | major concern about condition mismatch | Label it only as observed current-system response / 线上已展示回复，观察项，非实验条件. |
| Replay-30 is merged into dialogue-state v3 main tables | evidence contamination | Keep Replay-30/50 as auxiliary real-log-grounded offline counterfactual validation. |
| simulated multi-turn is written as learning outcome | reject-level overclaim | Treat simulated multi-turn, if ever done, only as appendix stress test. |
| student raw text, code, complete AIChat responses, identity fields, hash salt, or reversible mappings are public | ethics/privacy blocker | Public outputs must use aggregate counts, schemas, redacted summaries, and paraphrased examples only after reporting gates. |
| the 50 synthetic-grounded benchmark is described as real-student sample | provenance concern | State that dialogue-state v3 is a fixed reviewed dialogue-state benchmark; real AIChat layers are separate ecological-validity layers. |

## Reviewer-Facing Safe Summary

The external validation plan strengthens ecological validity without changing the main experiment. Real-AIChat-100 checks whether the bridge-family taxonomy and case-specific rubric can be applied to real AIChat turns from our own system. Real-AIChat-Replay-30/50, if conducted, reuses the same real-student starting states for offline counterfactual generation under the fixed harnesses. Neither layer updates the dialogue-state v3 main results or supports learning-outcome claims.
