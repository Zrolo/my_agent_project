# 50-case Held-out Prelaunch Checklist v1

Date: 2026-05-12

This checklist decides whether Research v1 is ready to move from dev/regression into the formal 50-case held-out experiment. It is not an experiment result; it is a guard against overfitting, weak-baseline bias, prompt drift, and judge drift.

## Go / No-go Summary

Current state: **No-go for the final held-out run, Go for held-out draft coach review**.

Reason:

- the offline chains for strong prompt, DBox-inspired, CodeHelp/CodeAid-style, Bridge-inspired, Bridge Contract, Guard, and Repair are available;
- the 10-case dev ablation and Repair stress runs have completed development-stage checks;
- prompt / judge / rubric versions still need project-owner approval and version freezing;
- the model/runtime configuration has not yet been locked as the held-out main-experiment version;
- Leakage Guard remains a dev signal rather than a gold label;
- the 50-case held-out draft exists and passes structural validation, but Coach A review, Coach B double annotation, adjudication, and freeze are not complete.
- a formal frozen-status preflight gate has been added; the current draft is correctly blocked with `frozen_status_required`, see [heldout_50_formal_preflight_report_20260513.md](heldout_50_formal_preflight_report_20260513.md).

## 1. Scope Lock

| Check | Status | Notes |
|---|---|---|
| Paper is an evaluation framework paper | pass | The core is CP-MissingBridgeBench, not an online multi-agent system |
| `current_system` is not the only research baseline | pass | Strong prompt and literature-inspired baselines are included |
| No claim of reproducing DBox | pass | The baseline is DBox-inspired single-turn decomposition |
| No new modules added to the Research v1 main line | pass | Next stage is freeze / held-out / double annotation |

## 2. Prompt Freeze Readiness

| Prompt / condition | Prelaunch status | 50-case role |
|---|---|---|
| `current_system` | snapshot-required | deployment baseline; snapshot the current online path |
| `enhanced_prompt_only` | freeze-candidate | main baseline |
| `codehelp_codeaid_no_direct_solution_tutor` | freeze-candidate | main or appendix baseline |
| `dbox_inspired_decomposition_tutor` | freeze-candidate | appendix or paired comparison |
| `dbox_inspired_decomposition_tutor + guard` | freeze-candidate + guard caveat | main baseline |
| `bridge_inspired_expert_decision_tutor` | freeze-candidate | main baseline |
| `single_llm_structured + guard` | freeze-candidate + guard caveat | strong single-LLM guarded baseline |
| `bridge_contract_predicted + guard` | guarded-only | main method condition, but not safety proof |
| `bridge_contract_predicted + guard + repair` | freeze-candidate + repair caveat | main or appendix condition |
| `bridge_contract_safe_scaffold` | appendix-only | fallback / stress condition only |

## 3. Judge / Grader Readiness

| Judge / grader | Prelaunch status | Use |
|---|---|---|
| Runtime Bridge Diagnoser | freeze-candidate | diagnosis/control signal; compare with coach labels |
| Runtime Leakage Guard | dev-signal-only | report with coach leakage labels and static lint; not gold |
| Static lint dev gate | screening-only | high-recall review trigger, not final judgment |
| Offline Bridge Grader | pending-definition | not ready for headline automated grading |
| Offline Leakage Grader | pending-definition | not ready for headline automated grading |
| Offline Response Grader | pending-definition | use coach blind review for now |
| Offline Repair Grader | pending-definition | use coach before/after review for now |

## 3.5 Model / Runtime Configuration

| Check | Status | Notes |
|---|---|---|
| Tutor provider fixed | pending-freeze | Recommended main experiment value: `deepseek_flash` |
| Tutor model fixed | pending-freeze | `deepseek-v4-flash` |
| Tutor thinking mode fixed | pending-freeze | Main quality experiments should use `profile_default` / effective enabled; old `disabled` runs stay dev evidence |
| Judge / Guard / Repair provider fixed | pending-freeze | Default `judge_provider=deepseek` |
| Judge / Guard / Repair thinking mode fixed | pass-by-design | The offline judge stack defaults to `thinking=disabled` |
| Leakage Judge timeout fixed | freeze-candidate | In the real-log 8-case pilot, `NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25` resolved the remaining stage timeouts |
| Judge / Repair max-token budget | pass-by-design | Keep current defaults; do not raise to 128k for timeout symptoms |
| Model-setting ablations separated | required | DeepSeek vs Kimi / MiMo or thinking enabled vs disabled must be separate experiments, not mixed into the main table |

See [model_runtime_configuration_v1.md](model_runtime_configuration_v1.md).

The formal 50-case main experiment should use:

```text
--condition-set heldout_main
```

For exact commands and integrity gates, see [heldout_50_main_experiment_runbook_v1.md](heldout_50_main_experiment_runbook_v1.md).

## 4. Dataset Requirements

Before creating the 50-case held-out set:

- do not sample from the current 20-case dev/regression set as headline held-out data;
- cover DP, binary search, graph/tree, greedy, data structures, implementation boundaries, debugging, direct answer/code requests, algorithm confirmation, and local completion;
- every case should include:
  - `case_id`
  - `student_message`
  - `problem_context`
  - `recent_dialogue`
  - `student_known_state`
  - `missing_bridge`
  - `allowed_help_level`
  - `forbidden_content`
  - `success_criteria`
  - `review_notes_for_coach`
- every case must let a coach judge what counts as a good response and what counts as over-completing the bridge.
- `recent_dialogue` should not collapse into pure single-turn Q&A: by default, `N/A` is capped at 10 cases and long-context rows must be at least 15.
- Before the formal main experiment, run the readiness check:

```bash
python3 -m evals.aichat.check_heldout_50_readiness \
  --output-json docs/research/heldout_50_readiness_YYYYMMDD.json \
  --output-md-zh docs/research/heldout_50_readiness_YYYYMMDD.zh.md \
  --output-md docs/research/heldout_50_readiness_YYYYMMDD.md
```

- Then the dataset must pass frozen-status preflight:

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_formal_preflight_report.json \
  --require-frozen-status
```

This check must return `ok=true`; otherwise the dataset cannot enter the headline run.

## 5. Coach Annotation Requirements

Before headline claims:

| Item | Requirement |
|---|---|
| Coach A | Labels all 50 task/reference cases and completes response blind review |
| Coach B | Independently labels at least 20 task/reference cases or a key response-review subset |
| Agreement | Report agreement for bridge family, help level, leakage label, would-show, and overall quality |
| Adjudication | Resolve low-confidence, multi-bridge, and major-leakage disagreement cases |
| Low-confidence handling | Rows with `coach_reviewer_confidence=low` or `needs_discussion=yes` should not drive headline claims |

## 6. Main Experiment Logging Requirements

Every row must preserve:

- `case_id`
- `condition_id`
- `tutor_mode`
- `pipeline_mode`
- prompt version
- judge prompt version
- repair prompt version, when applicable
- `models.tutor_model_provider`
- `models.chat_thinking_mode`
- `models.judge_model`
- `models.judge_provider`
- `candidate_response_text`
- `final_response_text`
- `final_response_source`
- `runtime_bridge_contract`
- `leakage_judge_result`
- `post_repair_leakage_judge_result`
- `repair_applied`
- `repair_still_leaks`
- `blocked`
- `candidate_static_leakage_risk_lint`
- `final_static_leakage_risk_lint`
- `stage_errors`
- `latency_ms`
- `llm_call_count`

## 7. Headline Claim Rules

Headline results must:

- come from the 50-case held-out set;
- use frozen versions;
- have coach blind review or calibrated graders;
- not treat static lint / runtime Guard as gold;
- use paired comparisons by case rather than treating all response rows as independent;
- report quality, leakage, student-ready pass, response burden, latency, and call count.

Do not headline:

- dev ablation means;
- 3-case smoke results;
- single-coach low-confidence rows;
- self-review;
- leakage rates produced only by the LLM Guard;
- results after prompt tuning without held-out re-evaluation.

## 8. Prelaunch Decision

Recommended next actions:

1. Project owner reviews the freeze readiness status in `prompt_patch_log.md` and `judge_prompt_patch_log.md`.
2. Treat `current_system` as a deployment snapshot rather than continuing to tune it.
3. Lock versions for `enhanced_prompt_only`, DBox-inspired, Bridge-inspired, CodeHelp/CodeAid-style, and guarded Bridge Contract variants.
4. Lock the main-experiment model and thinking mode according to [model_runtime_configuration_v1.md](model_runtime_configuration_v1.md).
5. State clearly that Leakage Guard is a dev signal / runtime guard, not coach gold.
6. Review and freeze the 50-case held-out draft dataset.

In one sentence:

> The 50-case draft is ready for coach review, but the formal main experiment should not run yet. Freeze prompt / judge / rubric / model runtime versions, review the dataset, complete double annotation and adjudication, then run the held-out experiment.
