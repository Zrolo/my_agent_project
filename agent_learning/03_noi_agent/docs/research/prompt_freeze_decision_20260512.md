# Prompt Freeze Decision 20260512

This file records the Research v1 freeze decision before moving from development ablations to the 50-case held-out experiment. It is not a final paper result and not an online AIChat deployment decision.

## 2026-05-16 Update

This file preserves the early 2026-05-12 freeze decision. After Coach A's case/source gate passed, the next response generation on the dialogue-state v3 50-case reviewed candidate set has been narrowed to a new 7-condition main table:

```text
dialogue_state_v3_main
```

The updated gate is recorded in [dialogue_state_v3_prompt_rubric_freeze_gate_20260516.md](dialogue_state_v3_prompt_rubric_freeze_gate_20260516.md). Future response generation on the reviewed candidate set should prefer that 2026-05-16 gate over the earlier 8-condition `heldout_main` candidate matrix in this file.

## Decision Summary

The current decision is to **conditionally freeze main-experiment prompt / judge / rubric candidates and move into 50-case held-out preparation**.

This means:

- stop adding new baselines or large prompt rewrites;
- use dev / regression evidence to select main conditions;
- once the 50-case held-out run begins, do not tune the same prompt / judge / rubric versions on those held-out results;
- treat all dev results as development evidence, not paper headline claims.

## Online Rollout Note

On 2026-05-12, the online student AIChat exposed `enhanced_prompt_only_clean` as the optional `教练引导` answer style. The default `简洁提示` answer style still maps to `current_system`.

This product change does not alter the freeze decision in this file:

- `教练引导` is an online prompt-only UX option, not held-out experimental evidence;
- it does not enable Bridge Judge, Runtime Bridge Contract, Leakage Guard, Repair, or risk-triggered routing;
- the 50-case held-out main experiment must still use the frozen offline conditions, fixed model/runtime configuration, and blind-review protocol in this file;
- any future real-log analysis must stratify by `aichat_prompt_mode` and must not merge `教练引导` turns into the old `current_system` bucket.

## Candidate Main Conditions

Keep the 50-case main table around eight conditions:

| Condition | Role | Decision |
|---|---|---|
| `current_system` | deployment baseline | Keep, to show real online-system failure modes |
| `enhanced_prompt_only` | strong prompt-only baseline | Keep, to control for prompt wording effect |
| `codehelp_codeaid_no_direct_solution_tutor` | programming guardrail baseline | Keep, to test whether no-direct-solution prompting is sufficient |
| `dbox_inspired_decomposition_tutor + guard` | literature-inspired decomposition + safety baseline | Keep, as the strongest algorithmic-programming education baseline |
| `bridge_inspired_expert_decision_tutor` | expert-decision baseline | Keep, to compare against generic expert-decision injection |
| `single_llm_structured + guard` | strong single-LLM baseline | Keep, to answer "why not one LLM?" |
| `bridge_contract_predicted + guard` | missing-bridge-aware guarded method | Keep, to evaluate Bridge Contract + Guard |
| `bridge_contract_predicted + guard + repair` | missing-bridge-aware guarded + repair method | Keep, to evaluate Repair trade-offs |

## Appendix / Dev Conditions

The following conditions should stay in appendix, stress, or development analysis:

- `dbox_inspired_decomposition_tutor`
- `bridge_contract_predicted`
- `bridge_contract_shuffled`
- `bridge_contract_oracle`
- `bridge_contract_safe_scaffold`
- `edf_inspired_adaptive_scaffolding_tutor`
- `edf_inspired_adaptive_scaffolding_tutor + guard`
- `risk_triggered_simulation`

EDF-inspired remains only a dev / appendix candidate. In the 10-case AI preliminary review, it trailed `dbox_inspired_decomposition_tutor + guard` and `bridge_contract_predicted + guard + repair`, and adding Guard did not improve EDF. It is therefore not recommended for the 50-case main table.

## Freeze Candidates

The following can enter `v1.0-dev frozen for held-out` candidate status, pending final project-owner approval:

- response review rubric v2;
- short constructed response interaction policy;
- enhanced prompt-only prompt;
- DBox-inspired prompt;
- CodeHelp/CodeAid-style prompt;
- Bridge-inspired expert-decision prompt;
- Bridge Contract tutor prompt;
- Leakage Guard prompt;
- Repair prompt;
- model/runtime configuration protocol;
- blind review export schema, including `上下文 AI 回复` and `AI 回复（要评分）` columns.

## Claims Still Not Allowed

Even after freeze, do not claim:

- Guard reliably prevents critical bridge leakage;
- Repair reliably solves leakage;
- Bridge Contract architecture alone caused all quality gains;
- EDF/Copa or DBox was fully reproduced;
- dev ablation results are final held-out results.

Safer wording:

> Development ablations were used to select and freeze evaluation conditions. Final claims require the frozen 50-case held-out evaluation, coach reference labels, and judge calibration.

## Engineering Decision

- The offline runner continues to record `stage_errors`, but recoverable Leakage Judge schema omissions are normalized so `leakage_level > 0` with `leaked_elements=[]` remains analyzable instead of becoming an invalid stage.
- This normalization is only for experimental analyzability. The Leakage Judge prompt still requires positive leakage to identify leaked elements.
- Static lint remains a high-recall review trigger, not coach gold.

## Go / No-go

Before the 50-case held-out run:

1. The project owner confirms the main experiment matrix in this file.
2. The project owner confirms prompt / judge / rubric versions.
3. The 50-case held-out draft receives coach review.
4. Coach A labels all cases, and Coach B labels at least 20 cases.
5. The judge calibration protocol has executable outputs.

If these are not satisfied, the project remains in dev / pre-held-out stage.
