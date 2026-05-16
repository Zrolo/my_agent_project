# Dialogue-State v3 Prompt / Rubric Freeze Gate 20260516

This note records the prompt / rubric / grader freeze gate before response generation on the dialogue-state v3 50-case reviewed candidate set. The goal is to move the next experiment from continued prompt tuning to fixed-condition response generation and blind review.

## Current Status

Dataset:

- `docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl`
- `reference_label_status=reviewed_candidate`
- `case_source_review_status=coach_A_case_source_review_passed`

Validation report:

- `docs/research/dialogue_state_v3_50_reviewed_candidate_validation_report_20260516.json`
- `row_count=50`
- `error_count=0`

Important boundary:

- `reviewed_candidate` only means the case/source set has passed Coach A review;
- it is not gold data;
- it is not an adjudicated reference;
- it is not an AI response blind-review result;
- it cannot yet support paper headline claims.

## Freeze Target

This gate freezes the experimental surface for the next response generation / blind review:

1. dataset input;
2. main experiment condition set;
3. tutor / judge / repair model configuration;
4. response review rubric v3;
5. case-specific rubric fields;
6. blind review workbook schema;
7. stage logging fields.

After freeze, the same 50-case response results should not be used to revise these prompts / rubrics / graders. If a revision is necessary, the freeze gate must be reopened and logged as a patch.

## Main Condition Set

The next run uses the new condition set:

```text
dialogue_state_v3_main
```

It is fixed to 7 conditions:

| condition_id | tutor_mode | pipeline_mode | Role |
|---|---|---|---|
| `enhanced_prompt_only_clean` | `enhanced_prompt_only` | `tutor_only_no_diagnosis` | strong prompt-only baseline |
| `codehelp_codeaid_clean` | `codehelp_codeaid_no_direct_solution_tutor` | `tutor_only_no_diagnosis` | no-direct-solution programming guardrail baseline |
| `dbox_inspired_clean` | `dbox_inspired_decomposition_tutor` | `tutor_only_no_diagnosis` | DBox-inspired decomposition baseline |
| `dbox_inspired_guard` | `dbox_inspired_decomposition_tutor` | `tutor_plus_guard` | DBox-inspired + Guard strong baseline |
| `bridge_guided_dbox_style_guard` | `bridge_guided_dbox_style_tutor` | `tutor_plus_guard` | missing-bridge-guided decomposition hybrid |
| `bridge_contract_compact_guard` | `bridge_contract_compact` | `tutor_plus_guard` | compact Bridge Contract + Guard |
| `bridge_contract_compact_guard_repair` | `bridge_contract_compact` | `tutor_plus_guard_plus_repair` | compact Bridge Contract + Guard + Repair |

EDF-inspired, oracle/shuffled contract, risk-triggered routing, and safe scaffold are not included in the main table for this run. They remain appendix / development / stress-test conditions.

## Repair Fairness Add-on

To avoid the fairness concern that Repair is only attached to Bridge Contract, this gate allows one narrow appendix run:

```text
dialogue_state_v3_repair_fairness_addon
```

This set contains only 1 condition:

| condition_id | tutor_mode | pipeline_mode | Purpose |
|---|---|---|---|
| `dbox_inspired_guard_repair` | `dbox_inspired_decomposition_tutor` | `tutor_plus_guard_plus_repair` | Check whether adding Repair to DBox-inspired + Guard changes the quality / leakage trade-off |

This add-on is not part of the main table and does not change the 7-condition `dialogue_state_v3_main` design. It is used only for appendix / sensitivity analysis to answer:

```text
Whether improvements from Bridge Contract + Repair are due to Repair itself rather than missing-bridge-aware generation.
```

Add-on command:

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516 \
  --condition-set dialogue_state_v3_repair_fairness_addon \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

Expected output:

```text
50 cases × 1 condition = 50 rows
```

Analysis should merge this 50-row add-on with `dbox_inspired_guard`, `bridge_contract_compact_guard`, and `bridge_contract_compact_guard_repair` from the main run.

## Model And Runtime Configuration

The main experiment compares tutoring harnesses, not models. The next response generation is fixed to:

```text
tutor_model_provider = deepseek_flash
tutor_model = deepseek-v4-flash
tutor_thinking_mode = profile_default / effective enabled
judge_provider = deepseek
judge_model = deepseek-v4-flash
judge_thinking_mode = disabled
repair_provider = deepseek
repair_model = deepseek-v4-flash
repair_thinking_mode = disabled
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS = 25
max token budgets = provider/default Research v1 values
```

Do not pass `--chat-thinking-mode disabled` in this run. Any comparison of thinking enabled vs disabled should be a separate model-setting ablation.

## Rubric / Workbook Freeze

This response review uses:

- `docs/research/response_review_rubric_v3.zh.md`
- `docs/research/response_review_rubric_v3.md`
- `docs/research/evaluation_protocol_v3.zh.md`
- `docs/research/evaluation_protocol_v3.md`
- `docs/research/case_specific_rubric_policy_v1.zh.md`
- `docs/research/case_specific_rubric_policy_v1.md`

The blind review workbook must show:

- original problem link / problem id;
- necessary problem statement / public summary;
- recent dialogue;
- context AI reply;
- current student message;
- AI response to score;
- success criteria;
- forbidden content;
- critical bridge boundary;
- acceptable reveal;
- expected student next action.

The blind review workbook must hide:

- condition / system name;
- tutor model;
- judge model;
- whether Guard / Repair was used;
- final response source.

## Response Generation Command

After this freeze gate passes, generate 50-case × 7-condition responses:

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516 \
  --condition-set dialogue_state_v3_main \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

Expected output:

```text
50 cases × 7 conditions = 350 rows
```

Run an integrity check immediately after generation. Empty responses, missing pairs, stage warnings, or duplicate pairs require targeted reruns and merge before any coach-facing blind review export.

## Claims Still Not Allowed

Even after this gate passes, do not claim:

- Bridge Contract outperforms DBox-inspired;
- Guard reliably prevents critical bridge leakage;
- Repair reliably solves leakage;
- LLM Judge can replace coach blind review;
- the 50-case set is a gold benchmark;
- reviewed candidate results can support paper headline claims.

The safer statement is:

```text
The case/source reviewed candidate set is ready for frozen response generation and coach blind review.
```

## Go / No-go

Go conditions:

- reviewed candidate validation `ok=true`;
- `dialogue_state_v3_main` condition set is implemented in the runner and covered by unit tests;
- rubric v3 / evaluation protocol v3 / case-specific rubric policy are fixed;
- model configuration is recorded in this note;
- reviewers receive only the blind review workbook, not the hidden key.

No-go conditions:

- case content keeps changing without reopening the case/source gate;
- new main-table conditions are added;
- prompts / rubrics are changed without a patch record;
- response generation has integrity blockers;
- condition keys are exposed before coach blind review.

## Next Step

1. Generate the 350-row response run using this gate command.
2. Run integrity checks and targeted reruns if needed.
3. Export Chinese and English blind review workbooks plus the hidden key.
4. Run a 5-case calibration blind review first.
5. Then proceed to Coach A full blind review and Coach B partial re-review.
