# DBox Reproduction Gap v1

This document defines the role of `dbox_inspired_decomposition_tutor` in Research v1. The central boundary is:

```text
We implement a DBox-inspired decomposition baseline, not a reproduction of DBox.
```

## What DBox Is

DBox is an interactive learner-LLM co-decomposition system for algorithmic programming learning. It is not merely a prompt. Its core system includes:

- learner-LLM construction of a step tree;
- separate solution formation and solution implementation stages;
- node status checking, such as correct, incorrect, missing, can be divided, and system generated;
- learner editing and decomposition of step-tree nodes;
- progressive hints;
- reveal substep or reveal code only after repeated failed attempts;
- code-step alignment;
- a user study measuring learning gain, cognitive engagement, critical thinking, and related outcomes.

These are multi-turn interactive system properties, not single-turn response-generation conditions.

The official package `pn2271.zip` further confirms at least four backend/frontend interactions: From Editor to Step Tree, Check Step Tree, Copy to Comments, and Check Match. Its prompts and code include fields such as `general_hint`, `detailed_hint`, `correctStep`, `correct_code`, and code mapping. Therefore, our single-turn baseline can adapt only the step-tree/status/general-hint principles, not reveal-like or answer-bearing fields.

## What Our Benchmark Is

CP-MissingBridgeBench currently evaluates single-turn competitive-programming tutoring responses:

```text
student turn + problem context + recent dialogue
-> one tutor response
-> coach blind review of quality, critical bridge leakage, micro-example quality, and student-readiness
```

The current benchmark does not include:

- an interactive step-tree UI;
- multi-turn co-decomposition;
- node status updates;
- repeated failed attempts;
- reveal-substep or reveal-code triggers;
- live code-step alignment;
- direct measurement of real student learning gains.

Therefore, Research v1 must not claim that it reproduces DBox, and it must not compare its single-turn response-review results directly with DBox's learning-gain, engagement, or critical-thinking results.

## What We Implement

Research v1 implements `dbox_inspired_decomposition_tutor`. It adapts one DBox principle to our single-turn offline setting:

```text
Use decomposition scaffolding to help the student shrink the current large problem into one answerable current substep.
```

The baseline internally emits:

```json
{
  "baseline_group": "literature_inspired_decomposition",
  "decomposition_view": [
    {"step_id": "s1", "step_name": "...", "status": "known_or_not_relevant"},
    {"step_id": "s2", "step_name": "...", "status": "current_stuck_step"},
    {"step_id": "s3", "step_name": "...", "status": "defer"}
  ],
  "current_substep": "...",
  "hint_level": "general_question",
  "student_visible_response": "..."
}
```

The student-visible response does not show a complete step tree. It only:

- breaks the current problem into one smaller current substep;
- asks the student to complete that substep;
- gives a first-level general hint, guiding question, or decomposition micro-task;
- preserves space for the student to infer the critical relation.

## Progressive Hint Limit

Because our benchmark is single-turn and does not observe repeated failed attempts, the DBox-inspired baseline uses only first-level decomposition guidance and question-based hints.

The current baseline forbids:

- reveal substep;
- reveal code;
- detailed pseudocode;
- complete step-tree answers;
- full algorithms;
- full code;
- full state definitions;
- full recurrences;
- full check conditions;
- full boundary update rules;
- direct completion of the current critical bridge.

In particular, `detailed_hint`, `correctStep`, `correct_code`, pseudocode, and code-line mapping from the official materials are not exposed in student-visible responses. They serve only as evidence for the reproduction gap and as disabled DBox features.

## Why This Baseline Is Still Useful

`dbox_inspired_decomposition_tutor` is useful because it reduces weak-baseline bias. It tests:

- whether decomposition scaffolding is already strong enough;
- whether a missing-bridge contract adds value beyond decomposition prompting;
- whether Guard works across decomposition-based generators;
- whether Bridge Contract advantages concentrate in high-risk or complex stuck-point cases.

## Fair Comparison Requirements

The main experiment should include at least:

```text
current_system
enhanced_prompt_only
dbox_inspired_decomposition_tutor
dbox_inspired_decomposition_tutor + guard
bridge_contract_predicted
bridge_contract_predicted + guard
bridge_contract_predicted + guard + repair
```

`dbox_inspired_decomposition_tutor + guard` must be in the main table so that Guard/Repair is not only attached to our method.

Optional appendix conditions:

```text
dbox_inspired_decomposition_tutor + guard + repair
codehelp_codeaid_no_direct_solution_tutor
bridge_inspired_expert_decision_tutor
```

## Gate Before The 50-case Main Experiment

Before entering the 50-case held-out main experiment, the DBox-inspired baseline must pass a 3-case smoke and a 10-20 case development ablation:

- it produces stable, reviewable responses;
- it does not frequently provide complete solutions;
- its major leakage rate is not clearly higher than `enhanced_prompt_only`;
- its quality is not clearly lower than `enhanced_prompt_only`;
- the prompt is frozen and versioned.

## Paper Wording

Recommended:

```text
We implement a DBox-inspired decomposition baseline, not a reproduction of DBox.
```

Longer wording:

```text
We do not reproduce DBox because DBox is an interactive learner-LLM co-decomposition system with a step-tree interface, progressive hints, code-step alignment, and real-student learning-outcome evaluation. Our benchmark evaluates single-turn competitive-programming tutoring responses, so we implement only a DBox-inspired decomposition baseline to test whether decomposition scaffolding is already strong, and whether missing-bridge contracts add value beyond it.
```

## Source Anchors

- [DBox arXiv / ar5iv](https://ar5iv.org/html/2502.19133v1)
- [DBox ACM DL](https://dl.acm.org/doi/abs/10.1145/3706598.3713748)
- [DBox official materials review](dbox_official_materials_review_v1.md)
