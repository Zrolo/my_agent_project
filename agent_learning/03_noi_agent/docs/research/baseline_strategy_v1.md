# Baseline Strategy v1

This document addresses a core research risk:

```text
Can the paper stand if current_system is the only baseline?
```

Answer:

```text
No. current_system is useful as a deployment baseline, but Research v1 needs strong prompt-only and literature-adapted baselines.
```

## Why current_system Is Not Enough

`current_system` represents the deployed AIChat state and is valuable for identifying real product failure modes. It cannot, by itself, prove that Bridge Contract, Guard, or Repair has research value.

If the paper only compares:

```text
current_system
vs
bridge_contract_predicted + guard + repair
```

reviewers can reasonably ask whether the method only beats a weak in-house system.

## Baseline Set

The minimum main experiment should include:

| Baseline | Type | Purpose |
|---|---|---|
| `current_system` | deployment baseline | Fix the current online system and its failure modes |
| `enhanced_prompt_only` | strong prompt-only baseline | Isolate prompt wording effects |
| `codehelp_codeaid_no_direct_solution_tutor` | programming guardrail baseline | Test whether ordinary no-direct-solution guardrails are sufficient |
| `dbox_inspired_decomposition_tutor` | DBox-inspired baseline | Test whether decomposition scaffolding is already strong |
| `dbox_inspired_decomposition_tutor + guard` | guard-instrumented decomposition baseline | Test whether the Guard signal transfers across generator families; guard-only does not mean the final response was rewritten |
| `bridge_inspired_expert_decision_tutor` | Bridge-inspired baseline | Test whether generic expert-decision prompting approaches Bridge Contract |
| `bridge_contract_predicted` | ours | Test predicted missing-bridge contracts |
| `bridge_contract_predicted + guard` | ours + safety instrumentation | Test the critical bridge leakage guard signal; do not interpret it as output repair except for block fallback |
| `bridge_contract_predicted + guard + repair` | ours + safety | Test the quality-leakage trade-off of repair |

If the main table becomes too large, the paper can report a 7-system main table and move full ablations to the appendix.

## Literature-adapted Is Not Reproduction

Research v1 does not claim to reproduce DBox, CodeHelp, CodeAid, Bridge, MathDial, or MRBench. Existing work differs from our setting in language, data, interaction design, and experimental protocol.

Use:

```text
We implement literature-adapted baselines, not direct reproductions.
```

## What Each Comparison Tests

| Claim | Required comparison | If unsupported |
|---|---|---|
| The deployed system has real failure modes | `current_system` human review | This only shows product weakness, not the main contribution |
| Prompt wording matters | `enhanced_prompt_only` vs `single_llm_structured` | Prompt effect may be small |
| Decomposition scaffold is a strong baseline | `dbox_inspired_decomposition_tutor` vs `enhanced_prompt_only` | DBox-inspired may not be a strong default |
| Guard signal transfers across generators | `dbox + guard` vs `dbox`; `bridge + guard` vs `bridge`; same-candidate guard/repair stress | Guard-only claims must be limited to detection/intervention signal; output repair requires repair/block evidence |
| Contract content matters | `bridge_contract_predicted` vs `bridge_contract_shuffled` | Bridge Contract may be acting like a prompt wrapper |
| Critical bridge leakage is necessary | low answer/code leakage but high bridge leakage | The core metric is weakened if bridge leakage is absent |
| Repair helps | repair stress before/after | If quality drops, report a trade-off |

## If A Strong Baseline Wins

That does not necessarily invalidate the paper.

If `enhanced_prompt_only` or `dbox_inspired_decomposition_tutor + guard` wins, the conclusion can be:

```text
Strong prompting or decomposition scaffolding is a better default generation path, while missing-bridge schema and critical bridge leakage remain valuable as evaluation, guard, or routing signals.
```

The paper should not bet on:

```text
Bridge Contract is always the best system.
```

It should bet on:

```text
CP-MissingBridgeBench reveals quality, leakage, and cost trade-offs across tutoring harnesses.
```

## Related Documents

Baseline definitions:

- [baseline_protocol_v1.zh.md](baseline_protocol_v1.zh.md)
- [baseline_protocol_v1.md](baseline_protocol_v1.md)

DBox boundary:

- [dbox_reproduction_gap_v1.zh.md](dbox_reproduction_gap_v1.zh.md)
- [dbox_official_materials_review_v1.zh.md](dbox_official_materials_review_v1.zh.md)
