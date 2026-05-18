# Prompt / Judge / Rubric Freeze Readiness Report

Date: 2026-05-12

This report checks whether Research v1 is ready to freeze tutor prompts, judge prompts, and review rubrics before the formal 50-case held-out experiment. Summary:

> The project has completed the core P1 development work: dev ablation, Repair stress, DBox-inspired baseline, strong prompt-only baseline, static-lint dev gate, model/runtime configuration protocol, and bilingual documentation governance. However, not all prompts should be treated as frozen yet. The project should enter a **freeze readiness review**: decide which components can be locked as `v1.0-dev`, which should remain dev/appendix conditions, and which still require regression or human approval.

## Current Decision

| Layer | Current State | Ready For Held-out Headline? | Reason |
|---|---|---:|---|
| `enhanced_prompt_only` | Integrated in the runner and covered by dev ablation | Conditionally yes | It is the required strong prompt baseline; the project owner still needs to approve and lock the prompt version |
| `dbox_inspired_decomposition_tutor` | Integrated in the runner; DBox reproduction gap documented | Conditionally yes | It is a literature-inspired baseline, not a DBox reproduction; the prompt must be version-locked before the main run |
| `dbox_inspired_decomposition_tutor + guard` | Covered in dev ablation | Conditionally yes | Needed to test whether the Guard signal transfers across generators; guard-only does not mean the final response was rewritten |
| `bridge_contract_predicted` | Covered in dev ablation | Not as a standalone safety headline | Quality signal is promising, but dev review still shows critical bridge leakage |
| `bridge_contract_predicted + guard` | Covered in dev ablation | Not enough to claim Guard solves leakage | Leakage Guard recall remains unstable for answer-slot, filled-table, and worked-example leakage |
| `bridge_contract_predicted + guard + repair` | Covered in dev ablation and Repair stress | Conditionally main table or appendix | Repair stress shows positive pilot evidence, but natural trigger rate, repair_still_leaks, and quality loss still need held-out reporting |
| `bridge_contract_safe_scaffold` | Offline appendix condition | No main table | Safe but low quality; better treated as high-risk fallback / stress appendix |
| Response review rubric v2 | Bilingual and updated with burden field | Conditionally yes | Needs coach approval before becoming the 50-case review rubric |
| Static lint dev gate | Implemented in summary | Screening only | High-recall review trigger, not a human leakage label |
| Model/runtime config | Protocol added | Conditionally yes | The main experiment must fix the tutor model, thinking mode, and judge / guard / repair stack; see `model_runtime_configuration_v1.md` |

## Evidence That Must Stay Development-only

The following should remain dev / pilot evidence:

- 20-case fair mini-study;
- 10-case dev ablation;
- 3-case prompt-controlled ablation;
- Repair stress all20 before/after;
- short constructed response smoke;
- static lint dev gate;
- self-review after the answer-slot Guard patch.

They can guide prompt changes, condition selection, and regression design, but they should not be final paper headline results.

## Preconditions Before Freeze

Before the 50-case held-out experiment:

1. Every tutor prompt in the main experiment must have a version name and human approval in `prompt_patch_log.md`.
2. Runtime Leakage Guard and main Offline Grader prompts in `judge_prompt_patch_log.md` must be marked as `v1.0-dev frozen for held-out`, or explicitly kept as dev-only.
3. `response_review_rubric_v2.zh.md` / `.md` must be locked as the 50-case review rubric.
4. `model_runtime_configuration_v1.zh.md` / `.md` must lock the main-experiment tutor model, thinking mode, and judge / guard / repair stack.
5. `dev_gate` should remain in summaries, but paper wording must state that it is not coach gold.
6. Once the 50-case held-out set is created, results from that set must not be used to tune the same prompt / judge / rubric / model runtime versions reported as headline results.
7. Every main condition should log:
   - `tutor_mode`
   - `pipeline_mode`
   - prompt version
   - judge prompt version
   - repair prompt version, when applicable
   - tutor model provider
   - chat thinking mode
   - judge model
   - final response source
   - static lint risk
   - stage errors

## Recommended Main Conditions

Keep the main table around eight conditions:

| Condition | Purpose |
|---|---|
| `current_system` | deployment baseline |
| `enhanced_prompt_only` | strong prompt-only baseline |
| `codehelp_codeaid_no_direct_solution_tutor` | programming guardrail baseline |
| `dbox_inspired_decomposition_tutor + guard` | literature-inspired decomposition + fair guard baseline |
| `bridge_inspired_expert_decision_tutor` | expert-decision baseline |
| `single_llm_structured + guard` | strong single-LLM + guard baseline |
| `bridge_contract_predicted + guard` | missing-bridge-aware guarded method |
| `bridge_contract_predicted + guard + repair` | missing-bridge-aware guarded + repair method |

Appendix / stress conditions:

- `dbox_inspired_decomposition_tutor`
- `bridge_contract_predicted`
- `bridge_contract_shuffled`
- `bridge_contract_oracle`
- `bridge_contract_safe_scaffold`
- `risk_triggered_simulation`

## Current Blockers

| Blocker | Impact | Recommended Handling |
---|---|---|
| Leakage Guard recall is unstable for answer-slot / filled-trace / worked-example leakage | Cannot claim Guard reliably prevents leakage | Report coach label, LLM Guard label, and static lint together in held-out |
| `repair_stress_004` still has major leakage | Cannot claim Repair fully solves leakage | Add it to regression and report repair_still_leaks_rate |
| Bridge Contract alone can be high-quality but leaky | Cannot frame Bridge Contract as a safety mechanism | Frame it as pedagogical organization / controllable signal; evaluate safety through Guard, Repair, and routing |
| `bridge_contract_safe_scaffold` has low quality | Not suitable for the main quality table | Keep it as high-risk deterministic fallback appendix |
| 23 legacy research docs remain unpaired bilingually | Does not block experiments, but affects external collaboration polish | Backfill core legacy docs gradually |

## Recommended Next Step

1. Treat this report as the freeze readiness checkpoint.
2. Project owner reviews `prompt_patch_log.md` and `judge_prompt_patch_log.md`, then decides which prompts become `v1.0-dev frozen`.
3. Project owner reviews `model_runtime_configuration_v1.md`, then decides whether the main experiment uses `deepseek_flash` + `profile_default` uniformly.
4. Build the 50-case held-out dataset and dataset card.
5. Run Coach A full labeling + Coach B labels on at least 20 cases.
6. Run the main experiment on frozen versions, without tuning prompts on held-out results.

## Paper Wording

Safe wording:

> Before held-out evaluation, we used development ablations and repair stress tests to select baseline conditions and freeze prompt/rubric versions. Development results were not used as headline claims.

Do not write:

> We have proved that Bridge Contract + Guard + Repair is best.

The current evidence supports only this:

> Bridge Contract, Guard, Repair, and literature-inspired baselines are ready for fair 50-case held-out comparison, but final claims require frozen-version held-out results, double-coach labels, and judge calibration.
