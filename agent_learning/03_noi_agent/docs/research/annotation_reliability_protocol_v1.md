# Annotation Reliability Protocol v1

This document defines how coach labels should be interpreted in the research pipeline.

## Core Position

Coach labels are **expert reference labels**, not absolute ground truth.

The project keeps `gold_*` field names in some JSONL files for runner compatibility, but their research meaning depends on the annotation stage:

| Stage | Meaning | Use |
| --- | --- | --- |
| `single_coach_reference` | One coach's raw expert label. | Smoke tests, prompt debugging, early error analysis. |
| `double_annotated_reference` | Two independent coach labels exist for the same case. | Agreement and ambiguity analysis. |
| `adjudicated_gold` | Disagreements have been reviewed and resolved. | Main paper metrics and final benchmark reporting. |

Do not report a single coach's raw label as the unique correct answer.

## Recommended Workflow

1. Export a blind v2 workbook.
2. Coach A labels all calibration cases.
3. Coach B labels at least 20%-30% of the same cases independently.
4. Convert both workbooks to JSONL reference labels.
5. Run agreement summary:

```bash
python3 -m evals.aichat.summarize_coach_label_agreement \
  --annotator-a-jsonl path/to/coach_a.jsonl \
  --annotator-b-jsonl path/to/coach_b.jsonl \
  --output-json docs/research/coach_agreement_summary.json
```

6. Review cases listed in `needs_adjudication_case_ids`.
7. Produce an adjudicated JSONL file for main experiments.

## What Counts As Agreement

Some labels are exact-match fields:

- `student_problem_solving_state`
- `primary_bridge_family`
- `registered_focus_id`
- `max_scaffold_level`
- `leakage_risk`

Other labels should allow relaxed matching:

- Bridge family agreement can match either coach's primary or secondary bridge.
- Focus agreement can match either `registered_focus_id` or `secondary_registered_focus_id`.

This matters because real tutoring turns can have more than one defensible interpretation.

Example:

```text
学生：check(mid) 到底返回 true 还是 false，我总写反。
```

One coach may label the primary bridge as `predicate_condition_bridge`, while another may mark `implementation_boundary_bridge` as secondary. This is not necessarily a bad label; it is a mixed case that should be adjudicated rather than counted as a simple wrong answer.

## Evidence And Confidence

Every labeled row should include:

- `evidence_quote`: the observable student text or context that supports the label.
- `coach_confidence`: how confident the annotator is.
- `coach_note_tags`: for `needs_discussion`, `multi_bridge_case`, or `acceptable_non_unique`.

Rows with low confidence or missing evidence should be excluded from headline paper metrics or analyzed separately.

## Reporting Language

Use careful wording:

```text
Bridge Judge agreement with single-coach reference labels was 0.90 on the 20-case smoke set.
```

Do not write:

```text
Bridge Judge true accuracy was 0.90.
```

For paper claims, prefer:

```text
We treat coach labels as expert reference labels rather than absolute truth. A subset is double annotated, disagreements are adjudicated, and uncertain or non-unique cases are analyzed separately.
```

## Relationship To Current Files

Current 20-case files:

- `coach_seed_labeling_v2_gold_20.jsonl`: single-coach reference export.
- `bridgebench_cp_seed_v2_gold_20.jsonl`: runner-compatible seed file built from the single-coach reference.

These files are appropriate for smoke testing. They are not yet an adjudicated benchmark.
