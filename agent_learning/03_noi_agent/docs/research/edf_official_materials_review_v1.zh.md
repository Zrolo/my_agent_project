# EDF / Copa 官方材料扫描报告 v1

日期：2026-05-12

论文：[Evidence-Decision-Feedback: Theory-Driven Adaptive Scaffolding for LLM Agents](https://arxiv.org/abs/2602.01415)

官方补充材料仓库：[claytoncohn/AIED26_Supplementary_Materials](https://github.com/claytoncohn/AIED26_Supplementary_Materials)

本报告用于判断 EDF / Copa 是否适合作为 CP-MissingBridgeBench 的论文 baseline。结论先行：

> 当前材料适合支持一个 **EDF-inspired adaptive scaffolding baseline**，但不适合作为“可运行代码复现 baseline”。论文中不应写“we reproduce Copa/EDF”；应写“we implement an EDF-inspired baseline adapted to our single-turn CP tutoring benchmark”。

## 扫描范围

本次只读扫描了官方补充材料仓库，临时克隆到本地，不提交原始材料到本项目。

仓库 commit：

```text
841742c86147b07d69f68976c1f2ae2cc9700545
```

仓库包含：

```text
README.md
supplementary_materials.pdf
task_rubrics.pdf
agent_prompts/
  1d_truck_task/
    strategy_agent_truck_task.txt
    assessment_agent_prompt_truck_task.txt
    knowledge_agent_truck_task.txt
    dialogue_agent_truck_task.txt
  2d_drone_task_one_package/
    strategy_agent_one_package_drone_task.txt
    assessment_agent_one_package_drone_task.txt
    knowledge_agent_one_package_drone_task.txt
    dialogue_agent_one_package_drone_task.txt
  2d_drone_task_two_packages/
    strategy_agent_two_package_drone_task.txt
    assessment_agent_two_package_drone_task.txt
    knowledge_agent_two_package_drone_task.txt
    dialogue_agent_two_package_drone_task.txt
```

没有发现：

```text
LICENSE
requirements.txt
package.json
Python / JS / TS application source
可直接运行的 Copa 后端或前端
```

因此，这个仓库公开的是 **prompt / interface specification / task rubric**，不是完整系统源码。

## 论文和材料的核心结构

论文将 EDF 定义为三段式：

```text
Evidence -> Decision -> Feedback
学生证据 -> 教学决策 -> 学生可见反馈
```

官方材料中的 Copa 由四类 sub-agent 组成：

| Agent | EDF 角色 | 作用 |
|---|---|---|
| StrategyAgent | Evidence | 根据最近 C2STEM 行为序列判断学习策略，如 `TINKERING`、`TOOL_USE`、`RUN_REPEAT` |
| AssessmentAgent | Evidence | 根据模型状态、策略和历史 learner state 判断当前 learner state |
| KnowledgeAgent | Evidence | 比较学生模型和 expert model，识别 ZPD 中的 immediate next step，并推荐检索的 domain knowledge |
| DialogueAgent | Decision + Feedback | 根据 student query、learner model、dialogue state 和 dialogue policy 生成学生可见回复 |

DialogueAgent 的策略空间包括：

```text
PROBE_UNDERSTANDING
SET_GOAL
SUGGEST_ACTION
PROVIDE_DOMAIN_KNOWLEDGE
PROMOTE_SELF_EFFICACY
STRATEGY_RECOMMENDATION
SUPPORT_ENGAGEMENT
AWAIT_ACTION
SEEK_HELP
END_GAME
GET_CLARIFICATION
```

官方 prompt 还要求：

```text
PROBE_UNDERSTANDING 应该是主要策略；
学生必须先解释为什么，再建议实施动作；
学生可见回复短，≤100 characters；
hidden learner state / mastery / retrieved knowledge 不应直接告诉学生；
遇到循环失败时选择 SEEK_HELP；
完整任务完成时才进入 END_GAME。
```

这些原则和我们当前“低负担但有认知价值”的 AIChat 方向高度相关。

## 与 CP-MissingBridgeBench 的相似点

EDF/Copa 和我们项目的结构相似：

| EDF / Copa | CP-MissingBridgeBench |
|---|---|
| student logs / chat / model state | student turn / recent_dialogue / problem_context |
| learner state | student_problem_solving_state / student_known_state |
| immediate next step / ZPD | missing_bridge / next_student_action |
| dialogue policy | allowed_help_level / help_forms / policy_risk |
| hidden model evidence not shown | runtime contract / judge trace not shown |
| feedback must avoid overreliance | critical bridge leakage control |

因此，EDF 很适合作为相关工作和机制 baseline 的理论依据。

## 与本项目的关键差异

不能直接复现 Copa 的原因：

1. Copa 依赖 C2STEM 环境日志、block-based model state、task mastery、physics/computing rubric 和 dyad classroom context。
2. 它是多轮、真实课堂、open-ended computational modeling 环境，不是单轮算法竞赛问答。
3. 它通过 StrategyAgent / AssessmentAgent / KnowledgeAgent 异步维护 learner model，我们当前 held-out benchmark 只有单轮输入、近期对话和题目上下文。
4. 它的评价指标包括 scaffold adaptivity、understanding-mastery alignment、student reliance、feedback interpretability 和学生/教师感知；我们当前主要评价 response quality、critical bridge leakage、student-ready pass、latency 和 LLM calls。
5. 官方仓库没有完整运行代码，只有 prompt、rubric 和补充说明。

## 许可证和复用边界

仓库中未发现 `LICENSE` 文件。出于科研和工程稳妥性：

```text
可以引用论文和仓库；
可以借鉴高层结构和策略空间；
不建议把官方 prompt 原文复制进本项目；
不应声称复现 Copa；
不应把其课堂学习收益结果和我们的单轮 benchmark 结果直接比较。
```

## 能否作为 baseline？

可以，但只能作为：

```text
edf_inspired_adaptive_scaffolding_tutor
```

而不是：

```text
Copa reproduction
EDF reproduction
official Copa baseline
```

建议 baseline 内部结构：

```json
{
  "evidence_summary": "...",
  "student_understanding_estimate": "low|medium|high|unknown",
  "dialogue_state": "information_seeking|suggesting|not_understanding|frustration|acknowledging|off_task",
  "dialogue_policy": "probe_understanding|set_goal|suggest_action|provide_domain_knowledge|promote_self_efficacy|get_clarification",
  "feedback_intent": "...",
  "final_response_text": "..."
}
```

该 baseline 不应使用我们的细粒度字段：

```text
primary_bridge_family
selected_focus_id
registered_focus_id
bridge_specific_forbidden_content
```

但可以使用同一输入：

```text
student_message
problem_context
recent_dialogue
student_known_state
```

这样它能公平回答：

> 通用 evidence-decision-feedback adaptive scaffolding 是否已经足够？还是 CP-specific missing bridge contract 仍有额外价值？

## 是否进入主实验？

建议当前阶段：

```text
不进入 50-case 主表；
进入 10-case / 20-case dev ablation 或 appendix；
如果表现明显强，再考虑替换主表中的 bridge_inspired_expert_decision_tutor 或作为额外主表条件。
```

理由：

1. 主表已经有 DBox-inspired、CodeHelp/CodeAid-style、Bridge-inspired、enhanced prompt 和 Bridge Contract 系列，继续扩大会稀释主线。
2. EDF 更像通用自适应脚手架理论 baseline，不如 DBox 那样贴近 algorithmic programming。
3. 它没有可运行源码，只能做 literature-inspired adaptation。

## 推荐论文写法

英文：

```text
We include EDF as related work and optionally implement an EDF-inspired adaptive scaffolding baseline. This is not a reproduction of Copa: the public supplementary repository provides prompts and task rubrics rather than a runnable system, and Copa depends on C2STEM logs, mastery rubrics, and multi-turn classroom interactions that are outside our single-turn CP tutoring benchmark.
```

中文：

```text
我们将 EDF 作为相关工作，并可选实现一个 EDF-inspired adaptive scaffolding baseline。该 baseline 不是 Copa 复现：官方补充材料主要提供 prompts 和 task rubrics，而不是可运行系统；Copa 依赖 C2STEM 环境日志、任务 mastery rubric 和多轮课堂交互，这些都不属于我们的单轮算法竞赛辅导 benchmark。
```

## 结论

EDF/Copa 对我们有价值，但价值主要在三点：

1. 支撑“证据 -> 决策 -> 反馈”的理论 framing；
2. 提供一个通用 adaptive scaffolding baseline 的设计依据；
3. 提醒我们记录 grounding / alignment / faithfulness，而不只记录质量均分。

它不应替代 DBox-inspired baseline，也不应扩大成新的主实验核心。当前最稳的处理方式是：

```text
引用 EDF；
记录官方材料扫描；
可选实现 edf_inspired_adaptive_scaffolding_tutor；
先放 dev/appendix，不进入默认主表。
```
