# Dev Ablation Suite Smoke Report 20260511

Chinese version: [dev_ablation_suite_smoke_report_20260511.zh.md](dev_ablation_suite_smoke_report_20260511.zh.md).

## Purpose

This smoke test only validates the P1 development-ablation toolchain. It is not a paper result.

It checks whether:

- `enhanced_prompt_only` is available in the shared offline runner;
- DBox-inspired, DBox-inspired + Guard, and Bridge Contract conditions can run in one suite;
- the suite generates per-condition JSONL, combined JSONL, bilingual summaries, anonymized review CSV, key CSV, and Chinese XLSX workbook;
- DBox-inspired structured outputs can be parsed robustly.

## Commands

Main smoke:

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1 \
  --limit 1 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 0
```

After finding a DBox + Guard parsing instability, the DBox + Guard condition was rerun with one retry:

```bash
python3 - <<'PY'
from pathlib import Path
from evals.aichat.run_dev_ablation_suite import run_dev_ablation_suite

run_dev_ablation_suite(
    input_jsonl=Path("docs/research/bridgebench_cp_seed_v2_gold_20.jsonl"),
    output_dir=Path("evals/aichat/ad_hoc_runs/dev_ablation_20260511_dbox_guard_retry_smoke1"),
    conditions=[{
        "condition_id": "dbox_inspired_guard",
        "tutor_mode": "dbox_inspired_decomposition_tutor",
        "pipeline_mode": "tutor_plus_guard",
        "guard_mode": "predicted",
    }],
    limit=1,
    chat_model_provider="deepseek_flash",
    judge_provider="deepseek",
    max_retries=1,
)
PY
```

## Outputs

Main smoke output directory:

- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/manifest.json`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/combined_dev_ablation.jsonl`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/combined_dev_ablation_summary.json`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/combined_dev_ablation_summary.md`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/combined_dev_ablation_summary.zh.md`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/coach_response_review_workbook_dev_ablation.csv`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/coach_response_review_workbook_dev_ablation.key.csv`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_smoke1/coach_response_review_workbook_dev_ablation.zh.xlsx`

DBox + Guard retry smoke output directory:

- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_dbox_guard_retry_smoke1/manifest.json`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_dbox_guard_retry_smoke1/combined_dev_ablation.jsonl`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260511_dbox_guard_retry_smoke1/coach_response_review_workbook_dev_ablation.zh.xlsx`

## Summary

Main smoke:

- case count: 1
- condition count: 11
- combined rows: 11
- completed rows: 9
- review workbook rows: 9
- stage errors: 2 DBox-inspired tutor parsing errors

Initial failure:

```text
ValueError: invalid decomposition status at item 1: known
```

The model emitted `known` for a DBox decomposition node status, while the old validator only accepted `known_or_not_relevant`, `current_stuck_step`, and `defer`.

Fix:

- the validator now normalizes common aliases:
  - `known` -> `known_or_not_relevant`
  - `current` / `missing` / `stuck` -> `current_stuck_step`
  - `deferred` / `future` / `later` -> `defer`

After the fix:

- `dbox_inspired_clean` emits a valid decomposition trace and student response;
- `dbox_inspired_guard` succeeds with `max_retries=1`;
- the DBox + Guard retry smoke produced `final_response_source=candidate`, `safe_action=pass`, and `llm_call_count=3`.

## Latency Note

The single-case full matrix is already slow:

- p50 total latency: 55155 ms
- p95 total latency: 244735 ms

This supports the current design:

```text
10-20 case dev ablation must run as offline batch work;
full multi-stage pipelines should not become the online default path;
the paper must report latency and LLM call count.
```

## Conclusion

This smoke validates that:

1. `run_dev_ablation_suite.py` generates the full P1 development-ablation review pack;
2. `enhanced_prompt_only` can now be compared with literature-inspired baselines and Bridge Contract variants in the same runner;
3. DBox-inspired structured fields need light normalization to avoid row-level failures from harmless status aliases;
4. the next 10-20 case dev ablation should run with `--max-retries 1` and should be expected to take nontrivial time.

This report does not prove any system is better. It only shows that the toolchain is ready for a small development ablation.
