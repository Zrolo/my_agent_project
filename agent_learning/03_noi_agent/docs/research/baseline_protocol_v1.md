# Baseline Protocol v1

This document defines the Research v1 baseline protocol and prevents weak-baseline bias. The current deployed AIChat system remains important, but it is a deployment baseline rather than the only research baseline.

## Core Position

Research v1 should not claim:

```text
Bridge Contract + Guard + Repair beats current_system.
```

The stronger claim is:

```text
CP-MissingBridgeBench compares different tutoring harnesses across pedagogical quality, critical bridge leakage, and cost.
```

The main experiments must include:

- the current deployed system;
- strong prompt-only baselines;
- literature-inspired tutoring baselines;
- Bridge Contract variants;
- shuffled / oracle contract controls;
- Guard / Repair ablations;
- latency and LLM call-count metrics.

## Baseline Layers

### Level 0: Deployment Baseline

| Baseline | Description | Purpose |
| --- | --- | --- |
| `current_system` | The current online AIChat flow with rules, legacy judge, Pedagogical Judge v2 soft control, main LLM, self-reported level hard gate, and output guards | Fix the real deployed system state and identify product failure modes |

Writing constraint:

```text
`current_system` is a deployment baseline, not the sole research baseline.
```

### Level 1: Simple LLM Tutor Baseline

| Baseline | Description | Purpose |
| --- | --- | --- |
| `vanilla_llm_tutor` | A minimal competitive-programming tutor prompt with a no-full-answer constraint | Measures the basic tutor-prompt baseline |

Example prompt constraint:

```text
You are a competitive-programming tutor. Help the student understand the current problem, but do not provide a complete solution or full code.
```

### Level 2: Strong Prompt-Only Baselines

| Baseline | Description | Purpose |
| --- | --- | --- |
| `single_llm_structured` | One LLM call outputs a runtime bridge contract, student response, and self-check | Answers "Why not let one LLM do diagnosis, response, and self-check?" |
| `enhanced_prompt_only` | Strong tutoring instructions but no concrete Bridge Contract | Isolates prompt wording effect |

`enhanced_prompt_only` should include:

- Socratic guidance;
- no direct answer;
- single focus;
- bridge-oriented micro-example;
- ask student to infer;
- avoid full code / full solution;
- respect student-known state.

If this baseline matches or beats Bridge Contract variants, the paper must not attribute gains to architecture alone.

### Level 3: Literature-Inspired Baselines

These conditions are **literature-inspired baselines**, not direct reproductions of prior systems. Current public baselines do not directly target Chinese competitive-programming turn-level missing-bridge tutoring.

| Baseline | Inspired by | Design intent |
| --- | --- | --- |
| `socratic_no_answer_tutor` | MathDial / tutoring-dialogue scaffolding | Guide through questions and minimal hints without direct answers |
| `mrbench_taxonomy_prompt` | MRBench / AI tutor pedagogical taxonomy | Generate responses under multi-dimensional pedagogical quality constraints |
| `codehelp_codeaid_no_direct_solution_tutor` | CodeHelp / CodeAid programming guardrails | Tests whether ordinary no-direct-solution guardrails are already sufficient |
| `dbox_inspired_decomposition_tutor` | DBox / algorithmic programming co-decomposition | Single-turn step-tree-style decomposition scaffolding that helps only one current substep |
| `bridge_inspired_expert_decision_tutor` | Bridge / novice-expert decision modeling | Internally identify student issue, remediation strategy, and teaching intention before responding |

Writing constraint:

```text
We derive literature-inspired baselines from prior tutoring and programming-education systems.
We do not claim direct reproduction unless code, data, and settings are actually matched.
```

`dbox_inspired_decomposition_tutor` is a DBox-inspired baseline, not a DBox reproduction. It adapts the official materials' step-tree, node-status, and `general_hint` principles, but it does not implement an interactive step-tree UI, multi-turn node editing, progressive reveal, code-step alignment, or a real-student learning-outcome study. Because this benchmark is single-turn, the DBox-inspired baseline uses only first-level general hints, guiding questions, or decomposition micro-tasks. Reveal substep, reveal code, `detailed_hint`, `correctStep`, `correct_code`, and pseudocode are disabled.

### Level 4: Missing-Bridge-Aware Methods

| Method | Description | Purpose |
| --- | --- | --- |
| `bridge_contract_predicted` | Bridge Judge predicts a compact contract before tutor generation | Tests whether predicted missing-bridge diagnosis adds value |
| `bridge_contract_predicted + guard` | Adds post-generation Leakage Guard | Tests critical bridge leakage detection |
| `bridge_contract_predicted + guard + repair` | Repairs once when the guard asks for rewrite/block | Tests whether repair reduces leakage while preserving quality |

These are the main method conditions, but the paper should not assume they always beat strong prompt-only baselines.

### Level 5: Negative Controls And Upper Bounds

| Condition | Description | Purpose |
| --- | --- | --- |
| `bridge_contract_shuffled` | Uses another case's oracle contract | Negative control for whether concrete contract content matters |
| `bridge_contract_oracle` | Uses coach-reference contract | Analysis / upper-bound condition for correct diagnosis information |
| `oracle_contract_with_guard` | Oracle contract plus predicted guard | Tests whether correct diagnosis can still induce leakage |

Interpretation rules:

- If `bridge_contract_predicted` does not beat `enhanced_prompt_only`, predicted diagnosis does not add average value beyond strong prompting.
- If `bridge_contract_predicted` beats `bridge_contract_shuffled`, the concrete contract is not decorative.
- If `bridge_contract_oracle` does not win, the schema is not necessarily wrong; contract injection, micro-example design, or leakage control may still fail.
- `bridge_contract_oracle` is not a fair runtime baseline.

## Main Experiment Matrix

The 50-case held-out test should include at least:

| Group | System |
| --- | --- |
| Deployment | `current_system` |
| Prompt-only | `enhanced_prompt_only` |
| Literature-inspired | `socratic_no_answer_tutor` |
| Literature-inspired | `codehelp_codeaid_no_direct_solution_tutor` |
| Literature-inspired | `dbox_inspired_decomposition_tutor` |
| Literature-inspired + safety | `dbox_inspired_decomposition_tutor + guard` |
| Literature-inspired | `bridge_inspired_expert_decision_tutor` |
| Ours | `bridge_contract_predicted` |
| Ours + safety | `bridge_contract_predicted + guard` |
| Ours + safety | `bridge_contract_predicted + guard + repair` |

If space allows, include:

- `vanilla_llm_tutor`
- `single_llm_structured`
- `mrbench_taxonomy_prompt`

## Ablation Matrix

| Comparison | Interpretation |
| --- | --- |
| `enhanced_prompt_only - single_llm_structured` | prompt effect |
| `bridge_contract_predicted - enhanced_prompt_only` | predicted diagnosis effect beyond strong prompt |
| `bridge_contract_predicted - bridge_contract_shuffled` | contract validity effect |
| `bridge_contract_oracle - bridge_contract_predicted` | diagnosis upper-bound sanity check |
| `bridge_contract_predicted + guard - bridge_contract_predicted` | guard effect |
| `bridge_contract_predicted + guard + repair - bridge_contract_predicted + guard` | repair effect |

Repair effect must be reported with:

- quality delta;
- major leakage delta;
- student-ready pass delta;
- false-positive rewrite rate;
- repair latency;
- still-leaks-after-repair rate.

## DBox-inspired Baseline Gate

Before `dbox_inspired_decomposition_tutor` enters the 50-case held-out main experiment, it must complete:

1. a 3-case smoke;
2. a 10-20 case development ablation;
3. prompt freeze and version logging.

Minimum entry criteria:

- it produces stable, reviewable responses;
- it does not frequently provide complete solutions;
- its major leakage rate is not clearly higher than `enhanced_prompt_only`;
- its quality is not clearly lower than `enhanced_prompt_only`;
- it uses only first-level general hints, guiding questions, or decomposition micro-tasks;
- reveal substep and reveal code are disabled.

## Metrics

Each baseline should report:

| Metric | Purpose |
| --- | --- |
| `overall_quality` | Coach overall judgment |
| `core6_mean` | Six core pedagogical dimensions |
| `bridge_oriented_micro_example` | Whether examples induce transferable bridge relations |
| `student_ready_pass` | Whether the response can be shown to a student |
| `minor_bridge_leakage_rate` | Minor bridge leakage |
| `major_bridge_leakage_rate` | Critical bridge leakage |
| `answer_code_leakage_rate` | Full answer/code leakage |
| `p50_latency` / `p95_latency` | Latency |
| `llm_call_count` | Call cost |
| `stage_error_rate` | Stability |

## Current Pilot Interpretation

The 3-case prompt-controlled ablation currently suggests:

- `enhanced_prompt_only` is very strong, so prompt wording may explain a substantial part of quality gains;
- `bridge_contract_predicted` ranks first in 2/3 cases and beats `bridge_contract_shuffled`, so concrete contract content still appears meaningful;
- `bridge_contract_oracle` is not automatically best, suggesting that correct diagnosis can still be expanded into leakage if tutor generation is not constrained.

Current safe conclusion:

```text
Bridge Contract gains mix prompt wording, concrete diagnosis information, and modular control signals.
Research v1 must separate these factors with strong baselines and negative-control ablations.
```

## Writing Rules

### Acceptable

```text
We include the current deployed AIChat as a deployment baseline, but not as the sole research baseline.
```

```text
We compare Bridge Contract variants against strong prompt-only and literature-inspired tutoring baselines to avoid weak-baseline bias.
```

```text
The shuffled-contract negative control tests whether the model uses the concrete missing-bridge diagnosis rather than generic tutoring instructions.
```

### Avoid

```text
Our method is better because it beats the current system.
```

```text
Bridge Contract architecture alone causes the quality gain.
```

```text
Oracle contract is a fair runtime baseline.
```

```text
We reproduce MathDial / MRBench / DBox / Bridge.
```

Use `literature-inspired` unless the public code, data, and settings are actually reproduced.

## Immediate Next Steps

1. Expand prompt-controlled ablation from 3 cases to 10-20 cases.
2. Implement or document `socratic_no_answer_tutor`, `dbox_inspired_decomposition_tutor`, and `bridge_inspired_expert_decision_tutor`.
3. Freeze strong prompt and judge prompts before the 50-case held-out test.
4. Treat `current_system` as a deployment baseline in the main table.
5. Frame the paper around quality-leakage-cost trade-offs rather than one architecture always winning.
