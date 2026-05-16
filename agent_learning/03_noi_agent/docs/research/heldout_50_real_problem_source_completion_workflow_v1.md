# 50-case Real Problem Source Completion Workflow v1

Date: 2026-05-13

## Goal

The 50-case held-out dataset must be traceable to real competitive-programming problem sources, such as Luogu, Codeforces, AtCoder, NOI/NOIP, or ICPC regional contests. The current draft `problem_context` fields describe task types, but they are not enough for a formal paper dataset.

This workflow turns the current 50-case draft into a source-traceable, reviewable, and publication-safe dataset.

## Source Fields

Each case must include:

| Field | Meaning |
| --- | --- |
| `problem_source_platform` | Source platform, such as `luogu`, `codeforces`, or `atcoder` |
| `problem_source_id` | Platform problem id, such as `P1048` or `ABCxxx_F` |
| `problem_source_url` | Original problem link; must be an `http://` or `https://` URL |
| `problem_statement` | Necessary statement for local coach blind review; can be a sufficiently complete rewritten statement |
| `problem_statement_public_summary` | Rewritten summary that can be kept in public artifacts |
| `problem_statement_rights_note` | Copyright and usage-boundary note |
| `problem_statement_access_level` | `local_review_only` / `public_summary_only` / `open_license` / `original_link_only` |

## Export The Completion Sheet

Export a source-completion table from the current draft JSONL:

```bash
python3 -m evals.aichat.export_heldout_source_completion_workbook \
  --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_ai_reference_draft_20260513.jsonl \
  --output-csv docs/research/heldout_50_source_completion_workbook_20260513.csv \
  --output-xlsx docs/research/heldout_50_source_completion_workbook_20260513.zh.xlsx
```

The output table includes:

- `case_id`
- `category`
- `problem_ref`
- `student_message`
- `student_message_length_bucket`
- `problem_context`
- `recent_dialogue`
- `student_code_excerpt`
- `missing_bridge`
- blank source fields to complete

## Filling Rules

1. Sources must be real and accessible; do not invent problem ids or links.
2. Cases need not all come from one platform, but a familiar domestic platform such as Luogu is a useful primary source for Chinese coaches.
3. The problem must match the case's intended bridge, such as DP state semantics, binary-search predicate semantics, tree path marking, lazy propagation, or greedy correctness.
4. Do not copy long platform statements into public artifacts just to fit the case. Public artifacts should prefer the original link plus a rewritten summary.
5. If local blind review needs full task meaning, keep the necessary statement in `problem_statement` and set `problem_statement_access_level` to `local_review_only` or `public_summary_only`.

## Merge Back Into JSONL

After filling the CSV, merge it back into JSONL:

```bash
python3 -m evals.aichat.apply_heldout_source_completion \
  --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_ai_reference_draft_20260513.jsonl \
  --source-csv docs/research/heldout_50_source_completion_workbook_20260513.csv \
  --output-jsonl docs/research/bridgebench_cp_heldout_v1_50_with_sources_20260513.jsonl \
  --require-complete
```

`--require-complete` fails when any case is missing a source row or required source metadata, preventing partial datasets from entering held-out evaluation.

## Validate After Merge

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_with_sources_20260513.jsonl \
  --expected-count 50 \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_with_sources_validation_report_20260513.json
```

The validation should check:

- source fields are complete;
- URLs are valid;
- `problem_statement_access_level` uses an allowed value;
- `student_message_length_distribution` is close to `20/15/10/5`;
- recent-dialogue and code-excerpt coverage is sufficient.

## Current Draft Status

As of 2026-05-13, the current 50-case AI reference draft is still missing:

- 50/50 source platforms;
- 50/50 platform problem ids;
- 50/50 original links;
- 50/50 necessary statements;
- 50/50 public statement summaries;
- 50/50 copyright/usage notes;
- 50/50 statement access levels.

The student-message length distribution is also too short-heavy: `short=40`, `medium_short=10`, `medium_long=0`, `long=0`, which does not meet the recommended distribution.

Therefore, the next step is source completion and length-distribution repair, not formal coach blind review.
