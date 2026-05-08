# BridgeTutor Rubric v1

## Purpose

This rubric defines how to evaluate an AI tutor turn in competitive programming learning.

The target is not whether the AI gives a correct solution. The target is whether the AI identifies the student's missing bridge, gives a controlled scaffold, avoids leaking the key bridge, and leaves the student with one clear next step.

Use this rubric for:

- Offline comparison between baselines.
- Teacher review of sampled AIChat turns.
- Calibration of an Eval Judge LLM.
- Paper analysis of bridge-aware scaffolding quality.

Do not use this rubric as a formal student grade.

## Core Terms

| Term | Meaning |
| --- | --- |
| Bridge | The missing intermediate relation between the problem evidence and the next solvable step. |
| Bridge family | A general bridge type, such as representation, transition, predicate, modeling, aggregation, ordering, mapping, boundary, or complexity. |
| Student problem-solving state | Where the student appears blocked in the problem-solving process, such as text comprehension, representation, strategy, implementation, debugging, or reflection. |
| Help-seeking type | Whether the student is asking for instrumental help, asking for executive help, avoiding help, or giving insufficient evidence. |
| Known focus | A project-specific focus already in the current system, such as `state_design`, `check_condition`, or `tree_path_difference`. |
| Bridge leakage | The AI gives the key intermediate relation directly, so the student no longer needs to cross it. |
| Answer leakage | The AI gives a complete solution, complete proof, or complete AC-style code. |
| Scaffold | A small hint, micro-example, comparison, or question that helps the student advance half a step to one step. |
| Turn-level help strength | The recommended scaffold strength for the current student turn only. It can rise or fall in the next turn as the student's understanding changes. |

## Turn-Level Help Strength

Use `allowed_help_level_gold` to annotate the help strength that should be allowed for the current student message, not for the whole AIChat session.

The same student can move between levels across turns:

- If the student makes progress or states the key relation, the next turn should usually use a lighter scaffold.
- If the student remains stuck at the same point, gives repeated short answers, or shows a deeper misconception, the next turn can use a stronger scaffold.
- If the student directly asks for the answer, method name, or code, do not increase help strength only because the request is strong. Apply leakage control.

| allowed_help_level_gold | Meaning | Allowed support | Still forbidden |
| --- | --- | --- | --- |
| `L1` | Light hint. | Ask one focused question, request evidence, or give a direction hint. | Do not fill the missing bridge or key judgement. |
| `L2` | Half-step scaffold. | Give a micro-example, binary choice, local relation, counterexample, table, or small diagram. | Do not give the full algorithmic relation or solution path. |
| `L3` | Strong scaffold. | Give a checklist, local pseudocode, or one minimal code diagnosis point. | Do not give complete solution, complete AC code, full transition equation, or full `check` condition. |

Optional qualitative analysis can also record the output form used by the tutor:

| help_form | Meaning |
| --- | --- |
| `question` | Focused follow-up question. |
| `hint` | Direction hint. |
| `micro_example` | Small example with a few objects. |
| `counterexample` | Minimal counterexample or contrast case. |
| `diagram` | Table, Mermaid graph, or other stable visual aid. |
| `checklist` | Short implementation or reasoning checklist. |
| `local_pseudocode` | A few lines of local pseudocode, not a fill-in answer shell. |
| `code_diagnosis` | One minimal suspicious code location or debugging evidence request. |
| `summary` | Summarize and close the current bridge before moving on. |

## Student Problem-Solving States

Use `student_state` to describe the student's observable state in the learning process. This is not the same as `bridge_family`.

`student_state` answers: where is the student stuck?

`bridge_family` answers: what missing intermediate relation should the scaffold target?

| student_state | Meaning | Typical student evidence |
| --- | --- | --- |
| `text_comprehension_blocked` | The student cannot parse the statement language, input/output, or basic terms. | "题目看不懂", "样例是什么意思", "这句话在说什么". |
| `problem_representation_unclear` | The student understands words locally but cannot form the objects, states, variables, or structure of the problem. | "不知道什么当点什么当边", "dp 数组每格表示什么". |
| `strategy_generation_blocked` | The student understands the problem but has no plausible approach. | "题目懂了但完全没思路", "不知道从哪个算法想". |
| `strategy_misconception` | The student has a strategy, but the strategy is wrong and the student may not realize why. | "我觉得直接贪心就行吧", "样例过了为什么不对". |
| `strategy_application_gap` | The student has the right broad strategy but cannot turn it into the key relation, proof step, or algorithm operation. | "知道要二分但 check 不会写", "知道 LCA 但不知道怎么加减". |
| `implementation_execution_gap` | The student has the right idea but cannot express it correctly in code. | "思路会但代码写不出来", "这个循环/函数怎么落地". |
| `debugging_verification_gap` | The student has code or a near-complete solution but fails on boundary, data type, counterexample, or local bug diagnosis. | "样例能过大数据错", "总是少算一个", "WA 但不知道哪里错". |
| `reflection_transfer_gap` | The student completed or nearly completed one problem but cannot explain, generalize, or recognize when to reuse the idea. | "这题会了但下次怎么判断", "为什么这里能用这个套路". |

### Relation to Coach's Practical Categories

The coach's practical categories can be mapped into `student_state` instead of being used as the final paper taxonomy:

| Coach category | Recommended `student_state` |
| --- | --- |
| 代码错误问题 | `debugging_verification_gap` or `implementation_execution_gap` |
| 题目理解但是不知道思路 | `strategy_generation_blocked` |
| 题目理解有思路，但是做不出来 | `strategy_application_gap` or `implementation_execution_gap` |
| 题目理解有思路，但是思路错了自己又不知道 | `strategy_misconception` |
| 题目理解对了，思路对了，代码也能写个大概，但是边界条件还有细节问题 | `debugging_verification_gap` |
| 无法理解题目的意思，不知道考什么 | `problem_representation_unclear` |
| 连题目都看不懂 | `text_comprehension_blocked` |

## Bridge Families

| bridge_family | Student is missing | Typical examples |
| --- | --- | --- |
| `representation_bridge` | What a state, variable, node, array cell, or maintained value means. | DP state meaning, trie node count, segment tree node value. |
| `transition_bridge` | Which previous cases or states lead to the current one. | DP transition completeness, recursion decomposition. |
| `predicate_bridge` | What a condition, `check`, or boolean test is verifying. | Binary search feasibility check, branch condition. |
| `modeling_bridge` | How problem objects and constraints become a structure. | Graph nodes/edges, difference constraints, object-relation modeling. |
| `selection_bridge` | Why a local choice is safe or preferable. | Greedy basis, exchange argument entry point. |
| `aggregation_bridge` | How many local effects are compressed, accumulated, and restored. | Prefix sum, difference array, tree path difference. |
| `ordering_bridge` | Why updates or enumeration must happen in a specific order. | 0/1 knapsack reverse loop, topological order. |
| `mapping_bridge` | Which problem action maps to which algorithm operation. | Union operation, heap pop/push, segment tree update/query. |
| `boundary_bridge` | Why initialization, stopping condition, or smallest case is valid. | Base case, `n=1`, empty interval, index boundary. |
| `complexity_bridge` | How data range constrains feasible methods. | `O(n^2)` TLE, direct enumeration feasibility. |
| `unknown_bridge` | There is a bridge, but the family is not clear enough from evidence. | Insufficient or ambiguous student evidence. |

## Help-Seeking Types

Use `help_seeking_type` to describe the student's request behavior, not their algorithmic weakness.

| help_seeking_type | Meaning | Typical evidence |
| --- | --- | --- |
| `instrumental_help` | The student asks for a hint, explanation, check, or next step while still doing part of the work. | "给我一点提示", "我哪里想错了", "check(mid) 为什么这样". |
| `executive_help` | The student asks the tutor to take over planning, solving, coding, or deciding the method. | "直接告诉我做法", "帮我写完整代码", "这题用什么算法". |
| `help_avoidance` | The student appears stuck but does not ask for help, rejects hints, or only repeats failure signals. | "算了不会", "我就是不会", no attempt after repeated prompts. |
| `unclear` | There is not enough evidence to infer the help-seeking type. | Very short or ambiguous message. |

## AI Response Quality Rubric

Score each dimension from 0 to 2. Total score: 12.

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Bridge Identification | Does not identify the student's missing bridge, or misidentifies it. | Identifies a broad direction but the missing link is vague. | Clearly identifies the missing intermediate relation. |
| Groundedness | Gives generic method advice without using the student's evidence. | Uses some problem or student evidence but still partly generic. | Anchors the reply in specific problem objects, constraints, code, or student wording. |
| Scaffold Appropriateness | Gives a full answer, too much help, or only repeats the student's confusion. | Gives a hint but the size is unstable or not well matched. | Gives half-step to one-step support that the student can still complete. |
| Bridge Leakage Control | Directly reveals the key bridge, formula, state definition, proof, or code. | Has partial leakage risk or strongly implies the full bridge. | Avoids revealing the full bridge while still helping the student move. |
| Next-Step Clarity | No clear next step. | Next step exists but is broad or hard to execute. | Gives exactly one concrete small action or question. |
| Single-Focus Coherence | Covers multiple unrelated concepts or solves the whole problem. | Mostly focused but drifts into adjacent issues. | Stays centered on one bridge and one next move. |

### Response Quality Bands

| Score | Label | Meaning |
| --- | --- | --- |
| 10-12 | High-quality scaffold | Ready for student-facing use. |
| 7-9 | Acceptable scaffold | Useful, but has room for tightening. |
| 4-6 | Weak scaffold | Does not reliably support the student. |
| 0-3 | Failed response | Should be blocked, regenerated, or escalated. |

## Student Learning Evidence Rubric

Use this after the student replies to a scaffold, answers a quiz, or writes a self-explanation.

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Student Uptake | Student ignores the scaffold or asks for the answer again. | Student responds but remains vague or repeats words. | Student engages with the exact small question or action. |
| Self-Explanation | Student cannot explain the relation. | Student uses relevant terms but the relation is incomplete. | Student explains the bridge in their own words. |
| Transfer Signal | Student only names an algorithm or gives no signal. | Student gives a broad signal. | Student names a concrete problem feature that should trigger the bridge. |
| Error Correction | Original misconception remains. | Misconception is partly corrected. | Student explicitly corrects the original wrong idea. |
| Independence | Student still depends on AI for the next step. | Student needs a small prompt. | Student proposes or performs the next step independently. |

## Leakage Labels

| Label | Definition |
| --- | --- |
| `no_leakage` | The reply does not reveal the full bridge or final answer. |
| `minor_bridge_leakage` | The reply strongly hints at the bridge but still leaves some work. |
| `major_bridge_leakage` | The reply gives the missing bridge directly. |
| `answer_leakage` | The reply gives a complete solution, proof, or AC-style code. |

## Recommended Annotation Fields

Each evaluated turn should store:

- `bridge_family_gold`
- `student_state_gold`
- `help_seeking_type_gold`
- `known_focus_gold`
- `missing_link_gold`
- `allowed_help_level_gold` for the current turn only
- `forbidden_completion_gold`
- `response_quality_scores`
- `response_quality_total`
- `leakage_label`
- `student_learning_scores` when a follow-up exists
- `annotator_id`
- `notes`

## Human Review Rule

For paper data, treat human annotation as the reference. Eval Judge LLM scores can be used for scaling, but at least 20-30 percent of samples should be manually reviewed.

If two human annotators are available, report agreement on:

- student state
- bridge family
- known focus
- help-seeking type
- leakage label
- response quality band

Use simple agreement first. If sample size is large enough, add Cohen's kappa.

## Research Basis

This taxonomy treats bridge-aware tutoring as a form of adaptive scaffolding: the tutor diagnoses the student's current problem-solving state, identifies the missing intermediate relation, and then chooses a constrained scaffold.

The `student_state` axis is informed by problem-solving phase models and programming problem-solving frameworks such as:

- Rott et al., "A descriptive phase model of problem-solving processes" ([Springer](https://link.springer.com/article/10.1007/s11858-021-01244-3)).
- Kurniawan et al., "Steps Before Syntax: Helping Novice Programmers Solve Problems using the PCDIT Framework" ([arXiv:2109.08896](https://arxiv.org/abs/2109.08896)).

The `help_seeking_type` axis is informed by intelligent tutoring research on adaptive help seeking and metacognitive feedback, especially work by Roll, Aleven, McLaren, and Koedinger on Help Tutor ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0959475210000538)).
