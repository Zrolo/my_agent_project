# Coach Seed Labeling Guide v1

## Purpose

This guide tells a competition coach how to label seed turns for **CP-MissingBridgeBench**.

The goal is not to label whether the student is generally good or bad. The goal is to label one current tutoring turn:

```text
Given the recent dialogue and this student message,
what reasoning bridge is missing right now,
what help is appropriate next,
and what must the tutor avoid directly completing?
```

The labels become gold references for:

- Bridge Judge diagnosis accuracy;
- AIChat tutor response quality;
- critical bridge leakage detection;
- repair response quality;
- paper baseline comparisons.

## Unit To Label

Label the current student turn, not the whole chat session.

Use the recent dialogue only as context. If the student understood something in an earlier turn, do not label that same thing as missing again unless the current turn shows it is still unstable.

For each seed, the coach should answer:

| Question | Field |
| --- | --- |
| Where is the student currently blocked? | `problem_solving_state` |
| What exact reasoning step is missing? | `missing_bridge.description` |
| Which broad bridge family best explains it? | `missing_bridge.family` |
| Is it an existing known focus? | `missing_bridge.known_focus` |
| What kind of help is the student asking for? | `help_seeking_type` |
| What is the strongest help allowed this turn? | `allowed_help_level_gold` |
| What must the AI not directly complete? | `forbidden_content` |
| How confident are you in this label? | `confidence` |

## Labeling Workflow

1. Read the current student message.
2. Skim the recent dialogue and problem context.
3. Decide whether the student lacks meaning, strategy, application, implementation, debugging, or reflection.
4. Write the missing bridge in one sentence.
5. Choose the closest known focus from `focus_registry_v1.json`.
6. Set the allowed help level for this turn.
7. Write the forbidden completion: what would count as over-helping or leaking the key bridge.
8. Add a short note if the case is ambiguous.

Do not start by choosing an algorithm name. A bridge is not "DP" or "binary search". A bridge is the missing relation that lets the student move one step forward.

## Problem-Solving State

Choose the state that best describes the student's current block.

| Label | Meaning | Typical student signal | Good next move |
| --- | --- | --- | --- |
| `text_comprehension_blocked` | The student cannot parse the statement, objects, or goal. | "题目都看不懂", "不知道要我求什么" | Restate objects and goal; ask one comprehension check. |
| `problem_representation_unclear` | The student roughly understands the task but cannot represent objects, states, variables, or invariants. | "dp 每格表示什么", "lazy 到底表示什么" | Ask what information must be kept; use tiny example. |
| `strategy_generation_blocked` | The student understands the problem but has no plausible approach. | "没思路", "不知道从哪里下手" | Ask for constraints, simple case, or candidate property. |
| `strategy_misconception` | The student has an idea but the idea is wrong or unsafe. | "我觉得直接贪心选最大", but this fails. | Ask for counterexample or condition that breaks the idea. |
| `strategy_application_gap` | The student knows the method name or high-level idea but cannot apply the key step. | "知道要二分，但 check 不会写" | Build the missing bridge with micro-example. |
| `implementation_execution_gap` | The student knows the idea but cannot translate it into code structure. | "递归怎么写", "pushdown 怎么落代码" | Request/localize pseudo-code slots or code skeleton only if allowed. |
| `debugging_verification_gap` | The student has code or output but cannot locate why it fails. | "WA 了不知道错哪", "边界总错" | Ask for failing case, expected/actual output, or trace one step. |
| `reflection_transfer_gap` | The student solved or got AC but cannot explain or transfer. | "AC 了但感觉是蒙的" | Ask for summary, invariant, or one similar variant. |

If two labels seem possible, choose the earliest missing step that blocks progress. For example, "知道要 DP 但状态不会设" is representation, not implementation.

## Bridge Family

Choose the broad reasoning bridge. Then write a specific subtype and description.

| Family | What Is Missing | Examples |
| --- | --- | --- |
| `representation_bridge` | Mapping problem information into a state, variable, node meaning, lazy meaning, or stored value. | DP state meaning; lazy tag meaning; trie node count meaning. |
| `transition_bridge` | How one state, recursion, or process step comes from previous cases. | DP transition sources; DFS return relation; recursion split. |
| `predicate_bridge` | How a condition/check/if maps to the target claim. | Binary search `check(mid)`; feasibility test; validity condition. |
| `modeling_bridge` | Turning statement objects and constraints into graph, interval, state, or data-structure model. | Build graph edges; encode dependency; map object relation. |
| `selection_bridge` | Why a method or local choice is appropriate. | Greedy basis; method selection; safe choice proof. |
| `aggregation_bridge` | How local contributions combine into a global answer. | Tree path difference; prefix sums; segment tree lazy aggregation. |
| `ordering_bridge` | Why loops, traversal, update, or processing order must be this way. | Reverse 0/1 knapsack loop; topological order; sort order. |
| `mapping_bridge` | How one representation corresponds to another. | Index compression; original object to compressed coordinate. |
| `boundary_bridge` | Boundary, initialization, type range, off-by-one, or edge case reasoning. | `long long`; left/right bound; base case; n=1. |
| `complexity_bridge` | Matching constraints to complexity or optimizing a too-slow approach. | TLE diagnosis; why O(n^2) fails; data range selection. |
| `unknown_bridge` | Not enough evidence to choose. | "不会" without problem/context; vague frustration. |

### Known Focus

Use `known_focus` when the current bridge matches a focus in `focus_registry_v1.json`.

Common current focus ids:

| Focus | Use When |
| --- | --- |
| `state_design` | DP/state/array cell meaning is missing. |
| `transition_design` | State exists, but sources/recurrence are missing. |
| `check_condition` | `check(mid)` or feasibility predicate is unclear. |
| `enumeration_order` | Loop/update/traversal order is unclear. |
| `greedy_basis` | Greedy choice seems plausible but proof/safety is missing. |
| `tree_path_difference` | LCA/path contribution marking and DFS aggregation are unclear. |
| `general_modeling` | Problem objects have not been abstracted into computable form. |
| `constraint_modeling` | Constraints have not been mapped into relations or states. |
| `boundary_debug` | Edge cases, initialization, or special cases cause errors. |
| `method_selection` | Student is guessing or confirming the method name. |
| `data_type` | Overflow, precision, sentinel, or range type is the issue. |
| `loop_boundary` | 0/1 indexing, loop range, or off-by-one is the issue. |
| `recursion_structure` | Base case, recursion split, or return meaning is unclear. |
| `complexity_fit` | Student cannot judge whether complexity can pass. |
| `lazy_semantics` | Lazy tag meaning or pushdown timing is unclear. |
| `shared_prefix_merging` | Trie/shared prefix storage and counting are unclear. |
| `left_bound_update` | Binary-search bound update direction is unclear. |

Set `needs_new_focus=true` only when the student turn is clear but no existing focus matches well.

## Help-Seeking Type

| Label | Meaning | Example |
| --- | --- | --- |
| `instrumental_help` | Student wants a hint, explanation, diagnosis, or next step while still learning. | "check 返回什么我总写反" |
| `executive_help` | Student asks the AI to do the work for them. | "直接给完整代码" |
| `help_avoidance` | Student resists explanation or wants to skip thinking. | "别问我，直接说答案" |
| `unclear` | Not enough evidence. | "不会" |

Use `executive_help` for direct answer/code requests even if the underlying bridge can be inferred.

## Allowed Help Level

This is the strongest appropriate help for the current turn. It can rise or fall across a conversation.

| Level | Allowed | Not Allowed |
| --- | --- | --- |
| `L1` | Ask for missing context, current attempt, evidence, or one observation direction. | Do not give algorithm name, state definition, recurrence, check condition, or code structure. |
| `L2` | Give a tiny example, one guiding question, one local hint, or a half-step relation. | Do not finish the current critical bridge. Do not give full recurrence/check/code. |
| `L3` | Give local pseudo-code, checklist, partial structure, or code diagnosis when the student already has substantial work. | Do not provide full solution, full code, or complete proof. |

Important rule: a stronger student request does not automatically allow stronger help. If the student asks "直接给代码", the level is often `L1`, not `L3`.

## Forbidden Content

`forbidden_content` is the content the tutor must not directly complete in this turn.

Write it as a concrete coaching boundary:

| Case | Good Forbidden Content |
| --- | --- |
| DP state design | "Do not directly give the full `dp[j]` definition and recurrence." |
| DP transition | "Do not write the full transition equation." |
| Binary search check | "Do not directly write the complete check condition and bound update direction." |
| Tree path difference | "Do not directly give the full endpoint/LCA marking formula." |
| Lazy segment tree | "Do not directly give the full pushdown implementation." |
| Direct code request | "Do not provide complete code or a submit-ready solution." |

Forbidden content is not the same as wrong content. It is content that may be correct but pedagogically too strong for the current turn.

## Confidence

Use 1-5:

| Score | Meaning |
| --- | --- |
| 5 | Very clear; another coach would likely agree. |
| 4 | Clear enough; minor subtype ambiguity. |
| 3 | Plausible but needs context or second review. |
| 2 | Weak evidence; label is mostly a guess. |
| 1 | Cannot responsibly label from the available turn. |

Use confidence <= 3 when the student message is vague, the problem context is missing, or two bridge families are genuinely hard to separate.

## Response Quality Rubric

When reviewing a system response, score each dimension 0-2.

| Dimension | 2 | 1 | 0 |
| --- | --- | --- | --- |
| `bridge_identification` | Directly targets the missing bridge. | Partly related but too broad or indirect. | Targets the wrong issue. |
| `groundedness` | Uses the given problem/dialogue evidence. | Some grounding, but generic. | Generic tutoring unrelated to context. |
| `scaffold_appropriateness` | Help strength matches allowed level. | Slightly too weak or too strong. | Gives answer/code or asks useless generic questions. |
| `bridge_leakage_control` | Does not complete the forbidden bridge. | Minor clue leakage but student still must reason. | Completes the critical bridge or gives solution/code. |
| `next_step_clarity` | Student has one clear, answerable next step. | Next step exists but is broad or multi-part. | No usable next step. |
| `single_focus_coherence` | Stays on one focus. | Mostly one focus, with some drift. | Multiple unrelated goals or topic drift. |

Total score range: 0-12.

## Leakage Labels

| Label | Meaning |
| --- | --- |
| `no_leakage` | Does not reveal the current critical bridge. |
| `minor_bridge_leakage` | Gives a clue stronger than ideal, but still leaves the student meaningful reasoning. |
| `major_bridge_leakage` | Directly completes the current missing bridge, such as state definition, recurrence, check condition, or marking formula. |
| `answer_leakage` | Gives full solution, complete code, or submit-ready answer. |

If unsure between minor and major, ask:

```text
After reading this reply, does the student still need to construct the current bridge?
```

If no, label `major_bridge_leakage`.

## Examples

### Example 1: Tree Path Difference

Student:

```text
我知道要 LCA，但不知道每条路径到底在哪里加减标记。
```

Coach label:

| Field | Value |
| --- | --- |
| `problem_solving_state` | `strategy_application_gap` |
| `bridge_family` | `aggregation_bridge` |
| `known_focus` | `tree_path_difference` |
| `missing_bridge.description` | Path contribution must be compressed into endpoint/LCA markings and recovered by DFS aggregation. |
| `allowed_help_level_gold` | `L2` |
| `forbidden_content` | Do not directly give the full endpoint/LCA marking formula. |

Good next help:

```text
Use a 3-node or 4-node path and ask which nodes should be counted before introducing the full marking rule.
```

Bad next help:

```text
s++, t++, lca--, parent(lca)--, then DFS sum.
```

### Example 2: DP State Design

Student:

```text
我不知道 dp 数组每一格到底应该表示什么，只知道像背包。
```

Coach label:

| Field | Value |
| --- | --- |
| `problem_solving_state` | `problem_representation_unclear` |
| `bridge_family` | `representation_bridge` |
| `known_focus` | `state_design` |
| `allowed_help_level_gold` | `L2` |
| `forbidden_content` | Do not directly give the full `dp[j]` definition and recurrence. |

Good next help:

```text
Use one herb and a few time capacities; ask what each table cell should store.
```

Bad next help:

```text
dp[j] means the maximum value within time j; transition is dp[j]=max(dp[j], dp[j-t]+v).
```

### Example 3: Direct Code Request

Student:

```text
直接给我完整代码吧。
```

Coach label:

| Field | Value |
| --- | --- |
| `help_seeking_type` | `executive_help` |
| `allowed_help_level_gold` | `L1` |
| `forbidden_content` | Do not provide complete code or submit-ready solution. |

Good next help:

```text
Ask the student to paste their current attempt or identify the first stuck step.
```

Bad next help:

```text
Provide a code skeleton with blanks that already reveals the algorithm structure.
```

## Blind Pairwise Review

For baseline comparison, hide the system name before rating.

For each pair of responses to the same seed, choose:

```text
A better / B better / tie
```

Judge by:

1. Which reply better targets the missing bridge?
2. Which reply gives the right amount of help?
3. Which reply avoids forbidden completion?
4. Which reply gives one clear next step?
5. Which reply is easier for a real student to answer?

Do not prefer a reply just because it is longer, more polished, or more confident.

## Seed Expansion Checklist

When adding new seed turns, aim for coverage across:

- at least 8-10 bridge families;
- DP state and transition;
- binary-search predicate and boundary;
- tree/graph aggregation;
- greedy basis;
- modeling from statement;
- implementation/debugging turns with code evidence;
- direct answer/code requests;
- vague "不会" turns with missing context;
- AC-but-unclear reflection turns.

For the first 50-turn coach seed set:

| Category | Suggested Count |
| --- | ---: |
| representation/state/lazy/model meaning | 8 |
| transition/recursion/process relation | 7 |
| predicate/check/binary-search condition | 6 |
| aggregation/tree/path/prefix contribution | 6 |
| selection/greedy/method choice | 5 |
| modeling/constraint mapping | 5 |
| boundary/debug/code evidence | 7 |
| direct request/vague/missing context/reflection | 6 |

## Agreement Plan

For the first paper iteration:

1. Coach A labels all 50 seed turns.
2. Coach B labels 10-15 overlapping turns without seeing Coach A's labels.
3. Discuss disagreements and refine this guide.
4. Freeze the label set before running final baseline comparisons.

Report agreement on:

- `problem_solving_state`;
- `missing_bridge.family`;
- `known_focus`;
- `allowed_help_level_gold`;
- `leakage_label` for response evaluation.

If agreement is low, do not hide it. Use disagreement examples to refine family boundaries and explain limitations.
