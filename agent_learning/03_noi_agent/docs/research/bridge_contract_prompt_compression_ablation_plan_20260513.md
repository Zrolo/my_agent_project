# Bridge Contract Prompt Compression Ablation Plan (2026-05-13)

## Background

The `dev10` human blind review suggested that `bridge_contract_guard` had relatively low major leakage, but its student-ready rate and conversational naturalness were still unstable. The current Bridge Contract Tutor prompt contains many rules, which may shift the model from natural tutoring toward checklist-style risk avoidance.

Instead of adding more rules to the long prompt, this round introduces two compressed offline tutor modes for development-stage ablation.

## New Conditions

New offline tutor modes:

- `bridge_contract_compact`
- `bridge_contract_minimal`

New dev condition set:

```text
prompt_compression
```

It contains four conditions:

```text
dbox_inspired_guard
bridge_contract_guard
bridge_contract_compact_guard
bridge_contract_minimal_guard
```

## Design Principles

`bridge_contract_guard` keeps the existing long prompt and acts as the stronger-control comparison.

`bridge_contract_compact_guard` keeps only the core controls:

- use the Bridge Contract;
- advance one current minimal substep;
- use the response shape "connective sentence + small observation task + short-answer question";
- do not directly complete the critical bridge;
- keep the `[LEVEL:L1|L2|L3]` tag.

`bridge_contract_minimal_guard` compresses further to test whether very light generator constraints improve quality while increasing leakage risk.

## Scope

This is not a formal prompt freeze or a final paper claim. It answers development-stage questions:

```text
Is Bridge Contract currently helped by structured contract information, or hurt by an overloaded prompt?
Can prompt compression improve naturalness and student-ready rate?
Does critical bridge leakage rise after compression?
```

Compressed variants should only enter later held-out experiments if they keep leakage controlled and do not underperform the long prompt in dev ablation.

## Verification

New unit tests cover:

- `bridge_contract_compact` / `bridge_contract_minimal` tutor modes;
- compact prompt is substantially shorter than the long prompt;
- minimal prompt is shorter than compact;
- compact prompt keeps the core Bridge Contract controls;
- `prompt_compression` condition set contains only the four conditions for this round.
