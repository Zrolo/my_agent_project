# EDF / Copa Official Materials Review v1

Date: 2026-05-12

Paper: [Evidence-Decision-Feedback: Theory-Driven Adaptive Scaffolding for LLM Agents](https://arxiv.org/abs/2602.01415)

Official supplementary repository: [claytoncohn/AIED26_Supplementary_Materials](https://github.com/claytoncohn/AIED26_Supplementary_Materials)

This report assesses whether EDF / Copa can be used as a baseline for CP-MissingBridgeBench. Bottom line:

> The released materials support an **EDF-inspired adaptive scaffolding baseline**, but not a runnable code reproduction baseline. The paper should not claim "we reproduce Copa/EDF"; it should say "we implement an EDF-inspired baseline adapted to our single-turn CP tutoring benchmark."

## Scan Scope

I inspected the official supplementary repository in a read-only local clone and did not commit the original materials into this project.

Repository commit:

```text
841742c86147b07d69f68976c1f2ae2cc9700545
```

The repository contains:

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

I did not find:

```text
LICENSE
requirements.txt
package.json
Python / JS / TS application source
runnable Copa frontend or backend
```

Therefore, the repository releases **prompts / interface specification / task rubrics**, not full system source code.

## Core Structure

The EDF paper frames scaffolding as:

```text
Evidence -> Decision -> Feedback
student evidence -> pedagogical decision -> student-facing feedback
```

The released Copa materials include four sub-agents:

| Agent | EDF role | Function |
|---|---|---|
| StrategyAgent | Evidence | Classifies learning strategies from recent C2STEM action sequences |
| AssessmentAgent | Evidence | Infers learner state from model state, strategy, and history |
| KnowledgeAgent | Evidence | Compares the student model to an expert model, identifies a ZPD-aligned immediate next step, and recommends domain knowledge retrieval |
| DialogueAgent | Decision + Feedback | Uses student query, learner model, dialogue state, and dialogue policy to generate the student-facing response |

Dialogue policies include:

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

The prompts emphasize that probing should be primary, students should explain why before implementation suggestions, hidden learner state / mastery / retrieved knowledge should not be revealed, and responses should remain short and peer-like.

## Similarity To CP-MissingBridgeBench

| EDF / Copa | CP-MissingBridgeBench |
|---|---|
| student logs / chat / model state | student turn / recent_dialogue / problem_context |
| learner state | student_problem_solving_state / student_known_state |
| immediate next step / ZPD | missing_bridge / next_student_action |
| dialogue policy | allowed_help_level / help_forms / policy_risk |
| hidden model evidence not shown | runtime contract / judge trace not shown |
| feedback should avoid overreliance | critical bridge leakage control |

EDF is therefore useful as related work and as a mechanism baseline.

## Key Differences

Copa cannot be directly reproduced in our benchmark because:

1. Copa depends on C2STEM environment logs, block-based model state, task mastery, physics/computing rubrics, and dyad classroom context.
2. It is a multi-turn classroom system for open-ended computational modeling, not a single-turn competitive-programming response task.
3. Its StrategyAgent / AssessmentAgent / KnowledgeAgent maintain a learner model asynchronously; our held-out benchmark has only student message, recent dialogue, and problem context.
4. Its evaluation focuses on scaffold adaptivity, understanding-mastery alignment, student reliance, interpretability, and perceptions; our current evaluation focuses on response quality, critical bridge leakage, student-ready pass, latency, and LLM calls.
5. The official repository does not contain runnable application code.

## License And Reuse Boundary

No `LICENSE` file was found in the repository. For research and engineering safety:

```text
cite the paper and repository;
derive high-level design ideas and policy labels;
do not copy official prompt text into this project verbatim;
do not claim Copa reproduction;
do not directly compare Copa's classroom learning outcomes against our single-turn benchmark results.
```

## Baseline Recommendation

Use it only as:

```text
edf_inspired_adaptive_scaffolding_tutor
```

Do not call it:

```text
Copa reproduction
EDF reproduction
official Copa baseline
```

Suggested internal output:

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

This baseline should not use our CP-specific fields:

```text
primary_bridge_family
selected_focus_id
registered_focus_id
bridge_specific_forbidden_content
```

It may use the same input context:

```text
student_message
problem_context
recent_dialogue
student_known_state
```

This lets us test whether generic evidence-decision-feedback adaptive scaffolding is sufficient, or whether CP-specific missing bridge contracts add value.

## Main Experiment Placement

Recommendation:

```text
Do not add it to the default 50-case main table yet.
Use it in 10-case / 20-case dev ablation or appendix first.
If it is clearly strong, consider replacing bridge_inspired_expert_decision_tutor or adding it as an extra main-table condition.
```

Reasons:

1. The main table is already large.
2. EDF is a general adaptive scaffolding framework rather than an algorithmic-programming-specific baseline like DBox.
3. The repository provides prompts and rubrics, not runnable code.

## Suggested Paper Wording

```text
We include EDF as related work and optionally implement an EDF-inspired adaptive scaffolding baseline. This is not a reproduction of Copa: the public supplementary repository provides prompts and task rubrics rather than a runnable system, and Copa depends on C2STEM logs, mastery rubrics, and multi-turn classroom interactions that are outside our single-turn CP tutoring benchmark.
```

## Conclusion

EDF/Copa is valuable for our project in three ways:

1. it supports the evidence-to-decision-to-feedback framing;
2. it motivates a generic adaptive scaffolding baseline;
3. it suggests logging grounding / alignment / faithfulness rather than only aggregate response scores.

It should not replace the DBox-inspired baseline and should not become the core of the main experiment. The safest path is:

```text
cite EDF;
record this official-materials scan;
optionally implement edf_inspired_adaptive_scaffolding_tutor;
keep it in dev/appendix first, not the default main table.
```
