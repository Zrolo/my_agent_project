# Coach Seed Labeling Workbook v1

This folder contains the first coach-facing CSV/XLSX workbooks generated from `bridgebench_cp_seed_v1.jsonl`.

For new independent labels, prefer [coach_seed_labeling_workbook_v2.md](coach_seed_labeling_workbook_v2.md). V2 separates turn type, student state, bridge family, bridge subtype, focus id, and leakage boundary more clearly. Keep v1 for compatibility with the first trial labels.

Use this guide together with [coach_seed_labeling_guide_v1.md](coach_seed_labeling_guide_v1.md).

## Files

| File | Use |
| --- | --- |
| `coach_seed_labeling_workbook_v1.zh.xlsx` | Recommended coach-facing Excel workbook. It has Chinese headers, a short instruction sheet, label explanations, wider columns, frozen panes, and dropdown options for every yellow coach-label column. |
| `coach_seed_labeling_workbook_v1.csv` | Blind labeling workbook. Coach columns are blank. Seed gold columns and gold-like `topic` are omitted. Use this for independent coach labels. |
| `coach_seed_labeling_workbook_v1.prefilled.csv` | Internal review workbook. Existing seed gold labels and `topic` are included and copied into coach columns when available. Use this only to audit the current seed labels. |
| `coach_seed_labeling_workbook_v1.review.csv` | Internal reference workbook. It may include seed gold and `topic`, but does not prefill coach columns unless `--prefill-coach` is used. |

## Recommended Workflow

1. Open `coach_seed_labeling_workbook_v1.zh.xlsx`.
2. Go to the `标注表` sheet.
3. Fill only the yellow coach columns.
4. Use the dropdown options in every yellow label column.
5. Leave `review_status=unlabeled` until a row is complete.
6. Change `review_status` to `labeled` when the row is ready.
7. Use `coach_seed_labeling_workbook_v1.prefilled.csv` only when reviewing or correcting the existing seed gold labels.

CSV fallback:

1. Open `coach_seed_labeling_workbook_v1.csv`.
2. Fill only the `coach_*` columns.
3. Leave `review_status=unlabeled` until a row is complete.
4. Change `review_status` to `labeled` when the row is ready.
5. Use `coach_seed_labeling_workbook_v1.prefilled.csv` only when reviewing or correcting the existing seed gold labels.

Do not give the prefilled or review file to a second annotator if you want independent agreement statistics. The blind workbook intentionally removes `topic` because seed topics such as `state_design` or `tree_path_difference` are close to the gold focus labels.

## Coach Columns

| Column | Meaning |
| --- | --- |
| `coach_problem_solving_state` | Current student state, such as `problem_representation_unclear` or `strategy_application_gap`. |
| `coach_bridge_family` | Broad missing bridge family. |
| `coach_secondary_bridge_family` | Optional secondary family when a turn crosses two bridge types. Leave blank if not needed. |
| `coach_bridge_subtype` | More specific subtype, such as `dp_state_design`, `check_condition`, or `tree_path_difference`. |
| `coach_known_focus` | Existing focus id from `focus_registry_v1.json`, or `unknown`. |
| `coach_bridge_evidence` | Short quote or observation supporting the bridge label. |
| `coach_missing_bridge_description` | One-sentence description of the missing reasoning bridge. |
| `coach_help_seeking_type` | `instrumental_help`, `executive_help`, `help_avoidance`, or `unclear`. |
| `coach_allowed_help_level` | Strongest appropriate help for this turn: `L1`, `L2`, or `L3`. |
| `coach_help_forms` | One or more forms separated by semicolons, such as `guiding_question;micro_example`. |
| `coach_forbidden_content` | What the tutor must not directly complete. |
| `coach_needs_new_focus` | `true` only when no existing focus matches. |
| `coach_confidence` | 1-5 confidence score. |
| `coach_notes` | Short ambiguity notes or disagreement reasons. |
| `review_status` | `unlabeled`, `labeled`, `needs_discussion`, or `review_seed_gold`. |

## Regenerate Workbooks

Blind workbook:

```bash
python3 -m evals.aichat.export_coach_seed_labeling_workbook \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-csv docs/research/coach_seed_labeling_workbook_v1.csv
```

Chinese Excel workbook:

```bash
python3 -m evals.aichat.export_coach_seed_labeling_workbook_xlsx \
  --input-csv docs/research/coach_seed_labeling_workbook_v1.csv \
  --focus-registry docs/research/focus_registry_v1.json \
  --output-xlsx docs/research/coach_seed_labeling_workbook_v1.zh.xlsx
```

Prefilled review workbook:

```bash
python3 -m evals.aichat.export_coach_seed_labeling_workbook \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-csv docs/research/coach_seed_labeling_workbook_v1.prefilled.csv \
  --prefill-coach
```

Include seed gold reference columns without prefilling coach fields:

```bash
python3 -m evals.aichat.export_coach_seed_labeling_workbook \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-csv docs/research/coach_seed_labeling_workbook_v1.review.csv \
  --include-seed-gold
```

Validate a filled workbook:

```bash
python3 -m evals.aichat.validate_coach_workbook \
  --input-csv docs/research/coach_seed_labeling_workbook_v1.csv \
  --focus-registry docs/research/focus_registry_v1.json
```

Export a blind response-review workbook from offline eval results:

```bash
python3 -m evals.aichat.export_coach_response_review_workbook \
  --input-jsonl evals/aichat/bridge_offline_eval_results.jsonl \
  --output-csv docs/research/coach_response_review_workbook_v1.csv \
  --key-csv docs/research/coach_response_review_workbook_v1.key.csv
```

The response-review workbook hides `tutor_mode`, `guard_mode`, and model provider from the coach-facing CSV. The `.key.csv` file is internal and maps anonymized response ids back to experimental conditions.

## Next Step

The current seed workbook contains 50 calibration rows. After these rows are labeled, use disagreement analysis to decide whether to revise the taxonomy before collecting the 100-200 turn development split.
