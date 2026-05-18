# LLM Grader Calibration Smoke12 Priority60 20260517

## Status

This is an LLM-grader calibration toolchain smoke, not a completed calibration report. It only checks that:

- the prompt pack can be run with a fixed backend;
- model outputs can be parsed as JSON;
- strict schema validation catches out-of-range scores;
- the summarizer can report metrics by grader type.

## Input

| item | value |
| --- | --- |
| prompt pack | `docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl` |
| output predictions | `docs/research/llm_grader_calibration_predictions_priority60_smoke12_20260517.jsonl` |
| metrics JSON | `docs/research/llm_grader_calibration_smoke12_metrics_priority60_20260517.json` |
| selected tasks | first 12 tasks |
| effective rows per grader | 4 |
| backend | `kimi_cli` |

## Important Fix

The first smoke produced parseable JSON, but generic / case-specific judges sometimes returned `overall_quality = 7/8` and `scaffold_sufficiency` values outside the 0-2 range. To avoid silently contaminating metrics, this pass made two fixes:

1. `run_llm_grader_calibration.py` now applies strict schema validation.
2. `prepare_llm_grader_calibration_pack.py` now makes output ranges explicit:
   - `overall_quality` must be 1-5;
   - `scaffold_sufficiency` must be 0-2;
   - categorical fields must use exact enum values.

After regeneration, the smoke was rerun and one transient backend timeout was filled with `--retry-non-ok`.

## Smoke Result

| grader | n | valid_n | status | invalid rate | overall MAE | leakage acc | student-ready agreement | safe-ready agreement |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `likert_only_judge` | 4 | 4 | 4 ok | 0.000 | 0.750 | NA | NA | NA |
| `generic_rubric_judge` | 4 | 4 | 4 ok | 0.000 | 0.750 | 0.750 | 0.750 | 0.750 |
| `case_specific_bridge_rubric_judge` | 4 | 4 | 4 ok | 0.000 | 0.750 | 0.750 | 0.500 | 0.750 |

Latency:

- average latency: 37.4s/task;
- max latency: 84.7s/task;
- case-specific / generic rows may be slow enough that full calibration should use resume + retry.

## Interpretation Boundary

No paper claim should be made from this smoke because:

- each grader has only 4 valid rows;
- rows are taken from the beginning of the pack, not a stratified sample;
- the 12 tasks contain no human critical-positive row, so critical precision / recall / F1 cannot be estimated;
- the Likert-only judge intentionally does not output leakage / ready fields.

Internal method note allowed:

```text
A 12-task smoke confirmed that the grader runner, strict schema validation, retry path, and summarizer work end to end. The smoke is not used as calibration evidence.
```

## Next Step

Formal calibration still requires the full runs:

1. `priority60_adjudicated` 180 tasks;
2. `adj+CoachA sample20` 60 tasks;
3. `adj+CoachB sample20` 60 tasks.

Run:

```bash
python3 -m evals.aichat.run_llm_grader_calibration \
  --pack-jsonl docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl \
  --output-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_20260517.jsonl \
  --backend kimi_cli \
  --judge-timeout-seconds 240
```

If there are timeout or invalid rows:

```bash
python3 -m evals.aichat.run_llm_grader_calibration \
  --pack-jsonl docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl \
  --output-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_20260517.jsonl \
  --backend kimi_cli \
  --retry-non-ok \
  --judge-timeout-seconds 240
```
