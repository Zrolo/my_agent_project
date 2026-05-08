# Coach Seed Labeling Workbook v1

This folder contains coach-facing CSV workbooks generated from `bridgebench_cp_seed_v1.jsonl`.

Use this guide together with [coach_seed_labeling_guide_v1.md](coach_seed_labeling_guide_v1.md).

## Files

| File | Use |
| --- | --- |
| `coach_seed_labeling_workbook_v1.csv` | Blind labeling workbook. Coach columns are blank and seed gold columns are omitted. Use this for independent coach labels. |
| `coach_seed_labeling_workbook_v1.prefilled.csv` | Internal review workbook. Existing seed gold labels are included and copied into coach columns. Use this only to audit the current seed labels. |

## Recommended Workflow

1. Open `coach_seed_labeling_workbook_v1.csv`.
2. Fill only the `coach_*` columns.
3. Leave `review_status=unlabeled` until a row is complete.
4. Change `review_status` to `labeled` when the row is ready.
5. Use `coach_seed_labeling_workbook_v1.prefilled.csv` only when reviewing or correcting the existing seed gold labels.

Do not give the prefilled file to a second annotator if you want independent agreement statistics.

## Coach Columns

| Column | Meaning |
| --- | --- |
| `coach_problem_solving_state` | Current student state, such as `problem_representation_unclear` or `strategy_application_gap`. |
| `coach_bridge_family` | Broad missing bridge family. |
| `coach_known_focus` | Existing focus id from `focus_registry_v1.json`, or `unknown`. |
| `coach_missing_bridge_description` | One-sentence description of the missing reasoning bridge. |
| `coach_help_seeking_type` | `instrumental_help`, `executive_help`, `help_avoidance`, or `unclear`. |
| `coach_allowed_help_level` | Strongest appropriate help for this turn: `L1`, `L2`, or `L3`. |
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

## Next Step

After the first 20 rows are reviewed, expand `bridgebench_cp_seed_v1.jsonl` to 50 rows and regenerate both workbooks.
