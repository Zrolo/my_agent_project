# 50-case Held-out Main Experiment Runbook v1

Date: 2026-05-13

This runbook defines the reproducible execution flow for the Research v1 formal 50-case held-out main experiment. It is not an experiment result. Run it only after prompts, judges, rubrics, model/runtime configuration, and the dataset are frozen.

## Preconditions

Before the formal run:

- Coach A has reviewed all 50 held-out task/reference cases;
- Coach B has independently labeled at least 20 overlap cases;
- low-confidence, multi-bridge, and major-leakage disagreements have been adjudicated;
- the held-out input JSONL is frozen, for example:

```text
docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl
```

- the 50-case results will not be used to tune the same prompt / judge / rubric versions;
- `prompt_patch_log.md`, `judge_prompt_patch_log.md`, and the review rubric version are frozen.

If these conditions are not met, the run is only a dry run or development check and cannot support held-out headline claims.

## Dataset Formal Preflight

First run the overall readiness check to confirm that Coach A/B labels, frozen export, and formal preflight are complete:

```bash
python3 -m evals.aichat.check_heldout_50_readiness \
  --output-json docs/research/heldout_50_readiness_YYYYMMDD.json \
  --output-md-zh docs/research/heldout_50_readiness_YYYYMMDD.zh.md \
  --output-md docs/research/heldout_50_readiness_YYYYMMDD.md
```

Proceed to the main experiment only when `ready_for_main_experiment=true` and `blocking_reasons=[]`.

The formal main experiment accepts only a frozen reference dataset. Before starting the run:

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_formal_preflight_report.json \
  --require-frozen-status
```

Go criteria:

```text
ok = true
row_count = 50
error_count = 0
require_frozen_status = true
```

If the dataset still uses `draft_needs_coach_review`, this check will return `frozen_status_required`. In that case, proceed only with coach review / adjudication / freeze export, not the formal 400-row main experiment.

The current draft preflight record is [heldout_50_formal_preflight_report_20260513.md](heldout_50_formal_preflight_report_20260513.md).

After Coach A / B review and required adjudication, export the frozen JSONL:

```bash
python3 -m evals.aichat.export_heldout_frozen_reference \
  --draft-jsonl docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --coach-a-workbook docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx \
  --output-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --reference-status adjudicated_reference
```

If only a Coach A single-coach reference is available and adjudication is not complete, use `--reference-status coach_reference` and do not describe the file as an adjudicated reference in the paper.

## Main Condition Set

The offline runner uses:

```text
--condition-set heldout_main
```

This condition set contains 8 main-table conditions:

| condition_id | tutor_mode | pipeline_mode | Paper role |
|---|---|---|---|
| `current_system_deployment` | `current_system` | `tutor_only_no_diagnosis` | deployment baseline |
| `enhanced_prompt_only_clean` | `enhanced_prompt_only` | `tutor_only_no_diagnosis` | strong prompt-only baseline |
| `codehelp_codeaid_clean` | `codehelp_codeaid_no_direct_solution_tutor` | `tutor_only_no_diagnosis` | programming guardrail baseline |
| `dbox_inspired_guard` | `dbox_inspired_decomposition_tutor` | `tutor_plus_guard` | DBox-inspired decomposition + guard baseline |
| `bridge_inspired_expert_decision_clean` | `bridge_inspired_expert_decision_tutor` | `tutor_only_no_diagnosis` | expert-decision baseline |
| `single_llm_structured_guard` | `single_llm_structured` | `tutor_plus_guard` | strong single-LLM guarded baseline |
| `bridge_contract_guard` | `bridge_contract` | `tutor_plus_guard` | Bridge Contract + Guard method |
| `bridge_contract_guard_repair` | `bridge_contract` | `tutor_plus_guard_plus_repair` | Bridge Contract + Guard + Repair method |

EDF-inspired, oracle/shuffled contract, safe scaffold, and risk-triggered simulation remain appendix / development conditions.

## Fixed Runtime Configuration

The main experiment compares tutoring harnesses, not models. Default fixed configuration:

```text
Tutor provider: deepseek_flash
Tutor model: deepseek-v4-flash
Tutor thinking mode: profile_default / effective enabled
Judge provider: deepseek
Judge model: deepseek-v4-flash
Judge thinking mode: disabled
Leakage Judge timeout: 25s
Max token budgets: current defaults, not raised to 128k
```

Do not pass `--chat-thinking-mode disabled` in the formal run unless the run is explicitly declared as a thinking-mode ablation.

## Main Run Command

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD \
  --condition-set heldout_main \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

Expected output:

```text
50 cases × 8 conditions = 400 rows
```

## Integrity Check

Immediately after the run:

```bash
python3 -m evals.aichat.check_ablation_run_integrity \
  --manifest evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD/manifest.json \
  --output-json docs/research/heldout_50_main_integrity_YYYYMMDD.json \
  --output-md docs/research/heldout_50_main_integrity_YYYYMMDD.md
```

Go criteria:

```text
expected_row_count = 400
combined_row_count = 400
final_response_row_count = 400
review_row_count = 400
blocking_reasons = []
warning_reasons = []
analysis_ready = true
headline_ready = true
```

If there are empty responses, missing pairs, duplicate pairs, or stage warnings, do not send the workbook for headline review. First use the `targeted_rerun_commands` from the integrity report.

## Targeted Rerun And Merge

Example:

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25 \
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_targeted_rerun/CONDITION_CASE \
  --condition-set heldout_main \
  --condition-id CONDITION_ID \
  --case-id CASE_ID \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

Merge:

```bash
python3 -m evals.aichat.merge_ablation_reruns \
  --source-manifest evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD/manifest.json \
  --retry-manifest evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_targeted_rerun/CONDITION_CASE/manifest.json \
  --output-dir evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged
```

After merging, rerun the integrity check. Only the merged run that passes integrity checks should be exported for coach blind review.

## Blind-review Workbook

The runner automatically produces:

```text
coach_response_review_workbook_dev_ablation.csv
coach_response_review_workbook_dev_ablation.zh.xlsx
coach_response_review_workbook_dev_ablation.key.csv
```

Give coaches only the `.zh.xlsx` blind-review workbook. Do not give them the key file. The workbook must hide:

- condition / system name;
- tutor model;
- judge model;
- whether Guard / Repair was used;
- final response source.

The blind-review workbook must include:

- `problem_source_platform`, `problem_source_id`, and `problem_source_url`: keeps every case traceable to a real problem source such as Luogu, Codeforces, AtCoder, NOI/NOIP, or ICPC;
- `problem_statement`: coaches need the task statement before judging whether the response is grounded or leaks a relation not already provided by the task;
- `problem_statement_public_summary`, `problem_statement_rights_note`, and `problem_statement_access_level`: separates local coach-review statement information from what can be retained in public artifacts;
- `student_message_length_bucket`: used to check whether the 50-case set covers short, medium-short, medium-long, and long student questions;
- `problem_context`: compressed context, not a replacement for the statement;
- `recent_dialogue` and `context_ai_reply`: needed to decide whether the AI is reasonably confirming a bridge already stated by the student or prematurely completing the current bridge.

The recommended 50-case student-message length distribution is: `short=20`, `medium_short=15`, `medium_long=10`, `long=5`. If the formal dataset does not meet this distribution, preflight should record and fix it so the benchmark is not dominated by short questions.

## AI Self-review Limitation

AI preliminary review may be used for development triage:

```bash
python3 -m evals.aichat.auto_fill_response_review \
  --input-csv evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged/coach_response_review_workbook_dev_ablation.csv \
  --output-csv evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged/coach_response_review_workbook_heldout_50_ai_prelim.csv \
  --output-xlsx evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged/coach_response_review_workbook_heldout_50_ai_prelim.zh.xlsx
```

But AI self-review is not a gold label and cannot replace Coach A / Coach B blind review.

## Result Analysis

After coach review:

```bash
python3 -m evals.aichat.analyze_dev_ablation_review \
  --review-xlsx PATH_TO_FILLED_REVIEW_XLSX \
  --key-csv evals/aichat/ad_hoc_runs/heldout_50_main_YYYYMMDD_merged/coach_response_review_workbook_dev_ablation.key.csv \
  --output-labels-jsonl docs/research/coach_response_review_labels_heldout_50_YYYYMMDD.jsonl \
  --output-json docs/research/heldout_50_main_analysis_YYYYMMDD.summary.json \
  --output-md-zh docs/research/heldout_50_main_analysis_YYYYMMDD.zh.md \
  --output-md docs/research/heldout_50_main_analysis_YYYYMMDD.md
```

The formal report must include:

- quality / core6 / micro-example;
- critical bridge leakage;
- student-ready pass;
- response burden;
- paired win/tie/loss;
- p50 / p95 latency;
- LLM call count;
- stage error count;
- coach agreement / calibration status.

## Allowed Claim

Acceptable:

```text
Under a fixed DeepSeek V4 Flash tutor and judge stack, the frozen 50-case held-out evaluation compares tutoring harness variants.
```

Avoid:

```text
One system is significantly better.
```

unless that claim comes from the frozen 50-case evaluation, coach blind review, paired analysis, and the necessary statistics / confidence intervals.
