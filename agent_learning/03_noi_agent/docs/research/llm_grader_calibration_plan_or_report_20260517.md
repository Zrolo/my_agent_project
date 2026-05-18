# LLM Grader Calibration Plan Or Report 20260517

## Current Status

This is now a calibration plan plus DeepSeek completed report: `priority60_adjudicated`, `adj+CoachA sample20`, and `adj+CoachB sample20` all have DeepSeek-backed predictions / metrics. Earlier `kimi_cli` outputs are retained only as exploratory/tooling records, not as the paper-facing calibration evidence. The repo already has a prompt-pack builder:

```text
evals/aichat/prepare_llm_grader_calibration_pack.py
```

This pass adds an offline runner and summarizer:

```text
evals/aichat/run_llm_grader_calibration.py
evals/aichat/summarize_llm_grader_calibration.py
```

`run_llm_grader_calibration.py` calls a judge backend only when explicitly run without `--dry-run`; `summarize_llm_grader_calibration.py` only summarizes existing prediction JSONL. These scripts do not replace human review. LLM graders are only scalable auxiliary graders.

Fixed prompt packs generated in this pass, with three reference views now run:

| pack | reference rows | grader tasks |
| --- | ---: | ---: |
| `llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl` | 60 | 180 |
| `llm_grader_calibration_pack_adj_coachA_sample20_20260517.jsonl` | 20 | 60 |
| `llm_grader_calibration_pack_adj_coachB_sample20_20260517.jsonl` | 20 | 60 |

Reference files:

- `llm_grader_calibration_reference_priority60_adjudicated_20260517.jsonl`
- `llm_grader_calibration_reference_adj_coachA_sample20_20260517.jsonl`
- `llm_grader_calibration_reference_adj_coachB_sample20_20260517.jsonl`

The original `adj_coachB_sample20` label rows lacked some problem-context and case-specific rubric fields. This pass fills those non-label prompt-context fields from the matching `adj_coachA_sample20` case / condition rows. This changes prompt context only; Coach B rating labels are unchanged.

## Three Judges

| judge | input | purpose |
| --- | --- | --- |
| `likert_only_judge` | problem / student message / response + Likert prompt | Test whether a holistic score is sufficient |
| `generic_rubric_judge` | generic tutor rubric | Test the upper bound without case-specific bridge information |
| `case_specific_bridge_rubric_judge` | success criteria, forbidden content, critical boundary, acceptable reveal, expected next action | Test whether case-specific bridge rubrics better match human review |

## Reference Labels

| reference | use |
| --- | --- |
| `priority60 adjudicated labels` | high-risk, high-disagreement, small-N adjudicated reference |
| `priority60 adjudicated + Coach A labels` | main paper view |
| `priority60 adjudicated + Coach B labels` | rater-strictness sensitivity |
| Coach A only / Coach B only | optional rater-bias check |

## Metrics

| metric | meaning |
| --- | --- |
| overall agreement / correlation | overall Pearson / Spearman / MAE |
| leakage label accuracy | four-class leakage-label agreement |
| critical binary precision / recall / F1 | major/answer vs non-critical |
| major leakage false negative rate | human major/answer but grader non-critical |
| student-ready agreement | ready yes/borderline/no agreement |
| safe-ready agreement | ready and no leakage agreement |
| unknown / low-confidence rate | UNKNOWN or low-confidence outputs |

## Minimal Workflow

1. Use `prepare_llm_grader_calibration_pack.py` to create prompt packs for the three judges.
2. Fix model, temperature, output schema, and UNKNOWN handling.
3. Use `run_llm_grader_calibration.py` to parse model outputs into `grader_prediction`.
4. Run `summarize_llm_grader_calibration.py`.
5. Report priority60-only, adj+CoachA, and adj+CoachB separately.

If a labels JSONL lacks problem or rubric fields, use `--context-jsonl` to fill prompt context from a complete reference for the same cases. A rater view should not be penalized because its prompt pack has missing context.

### Runner Dry Run

Before model calls, run a dry run to check pack size, existing outputs, and the first task:

```bash
python3 -m evals.aichat.run_llm_grader_calibration \
  --pack-jsonl docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl \
  --output-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_deepseek_20260518.jsonl \
  --dry-run \
  --limit 3
```

For the first live smoke, run 6-12 tasks before expanding, so schema and UNKNOWN behavior can be checked:

```bash
python3 -m evals.aichat.run_llm_grader_calibration \
  --pack-jsonl docs/research/llm_grader_calibration_pack_priority60_adjudicated_20260517.jsonl \
  --output-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_deepseek_20260518.jsonl \
  --backend deepseek \
  --limit 12 \
  --judge-timeout-seconds 240
```

Summarize with:

```bash
python3 -m evals.aichat.summarize_llm_grader_calibration \
  --predictions-jsonl docs/research/llm_grader_calibration_predictions_priority60_adjudicated_deepseek_20260518.jsonl \
  --output-json docs/research/llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.json \
  --output-md docs/research/llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.md
```

## Interpretation Rules

Can write:

```text
The case-specific bridge-rubric grader is evaluated as a scalable auxiliary grader against coach/adjudicated references.
```

Only if supported by metrics, write:

```text
The case-specific bridge-rubric grader better matches coach/adjudicated labels than likert-only or generic-rubric graders.
```

Do not write:

```text
LLM grader replaces human review.
LLM grader labels are gold.
Priority60 is sufficient as final automatic-grader validation.
```

## Current Gap

All three DeepSeek-backed reference views are now complete. Kimi-backed `20260518` files without the `_deepseek_` suffix are exploratory/tooling runs and should not be used as the paper-facing calibration evidence.

## Smoke12 Update

A toolchain smoke has been completed on the first 12 tasks of the `priority60_adjudicated` pack:

- predictions: `docs/research/llm_grader_calibration_predictions_priority60_smoke12_20260517.jsonl`
- metrics JSON: `docs/research/llm_grader_calibration_smoke12_metrics_priority60_20260517.json`
- smoke note: `docs/research/llm_grader_calibration_smoke12_priority60_20260517.md`

The first smoke exposed a schema risk: some generic / case-specific judge outputs used 7/8 scores or scaffold scores outside the 0-2 range. This pass fixes that by:

- adding strict schema validation to the runner;
- making the summarizer exclude non-ok rows and report invalid rate;
- adding `--retry-non-ok`;
- making prompt packs explicit that `overall_quality` is 1-5 and `scaffold_sufficiency` is 0-2.

After rerun and retry, smoke12 has 12/12 `ok` rows and invalid rate 0. This smoke only proves that the toolchain runs end to end; it is not paper calibration evidence. The next step is to complete priority60-only, adj+CoachA sample20, and adj+CoachB sample20.

## Kimi Exploratory Result Update

The following `kimi_cli` results are exploratory/tooling records only because they do not match the main experiment's fixed DeepSeek judge stack.

The `priority60_adjudicated` 60-row × 3 judge = 180 task run is complete:

- predictions: `docs/research/llm_grader_calibration_predictions_priority60_adjudicated_20260517.jsonl`
- metrics: `docs/research/llm_grader_calibration_metrics_priority60_adjudicated_20260517.json`
- report: `docs/research/llm_grader_calibration_priority60_report_20260517.md`

Integrity:

- 180/180 rows are final `ok`;
- 4 non-ok rows after the first full pass were fixed with `--retry-non-ok`;
- average latency was about 39.8s/task, with max latency about 232.8s/task.

Main metrics:

| grader | leakage acc | critical P/R/F1 | major FN | overall r | overall MAE |
| --- | ---: | --- | ---: | ---: | ---: |
| `likert_only_judge` | NA | NA/NA/NA | NA | 0.087 | 0.933 |
| `generic_rubric_judge` | 0.517 | NA/0.000/NA | 1.000 | 0.167 | 0.867 |
| `case_specific_bridge_rubric_judge` | 0.567 | 0.833/0.312/0.455 | 0.688 | 0.450 | 0.783 |

Interpretation: in the Kimi exploratory run, the case-specific bridge-rubric judge is better than the generic rubric judge. This is not the paper-facing calibration evidence; it mainly shows that LLM-grader calibration is backend-sensitive.

## DeepSeek Sensitivity Update 20260518

All reference views have been rerun with the DeepSeek offline judge profile:

| reference view | tasks | status | report |
| --- | ---: | --- | --- |
| `priority60_adjudicated` | 180 | 180/180 ok | `docs/research/llm_grader_calibration_metrics_priority60_adjudicated_deepseek_20260518.md` |
| `adj+CoachA sample20` | 60 | 60/60 ok | `docs/research/llm_grader_calibration_metrics_adj_coachA_sample20_deepseek_20260518.md` |
| `adj+CoachB sample20` | 60 | 60/60 ok | `docs/research/llm_grader_calibration_metrics_adj_coachB_sample20_deepseek_20260518.md` |

Combined report:

```text
docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.md
```

Interpretation boundary:

- `priority60_adjudicated` remains the main critical-leakage calibration view because it contains 16 human critical-positive rows;
- the DeepSeek-backed case-specific judge improves some auxiliary metrics, but priority60 critical recall remains 0 and major leakage false-negative rate is 1.000;
- `adj+CoachA/B sample20` contains no human critical-positive rows, so it cannot support critical recall or false-negative claims;
- the current conclusion remains that LLM graders are dev-stage auxiliary signals and cannot replace human review / adjudication.
