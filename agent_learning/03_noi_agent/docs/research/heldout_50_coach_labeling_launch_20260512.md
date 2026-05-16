# Held-out 50 Coach Labeling Launch 20260512

This file launches the Research v1 50-case held-out coach review and partial double annotation. It is not a paper result; it is preparation for freezing the dataset before the formal main experiment.

## Files

| Purpose | File |
|---|---|
| 50-case held-out draft JSONL | `docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl` |
| Coach A full labeling workbook | `docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx` |
| Coach B 20-case overlap JSONL | `docs/research/bridgebench_cp_heldout_v1_50_coach_b_overlap_20.jsonl` |
| Coach B 20-case overlap workbook | `docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx` |
| Dataset card | `docs/research/bridgebench_cp_heldout_v1_50_card.md` |
| Structure validation report | `docs/research/bridgebench_cp_heldout_v1_50_validation_report.json` |

## Current Validation Status

The latest structure validation passes:

```text
row_count = 50
recent_dialogue_distribution = none: 10, short: 25, long: 15
student_code_excerpt_distribution = none: 38, present: 12
reference_label_status = draft_needs_coach_review
dev_seed_overlap = 0
error_count = 0
```

This means the dataset can enter coach review, but it is not gold yet.

## Case Labels First, AI Response Review Later

This step is **case/reference annotation**, not AI-response blind review, so the workbook intentionally does not include a target AI response to score. Coaches are reviewing the task itself:

- whether the student message is realistic;
- whether the context and recent dialogue are sufficient;
- what the student has already stated;
- whether the missing bridge, forbidden content, and success criteria are reasonable.

After Coach A / B complete reference labeling and the held-out set is frozen, frozen prompt / judge / rubric versions will be used to generate AI responses for each system condition. That later response blind-review workbook will include:

- `上下文 AI 回复`: the previous assistant response from recent dialogue, when available;
- `AI 回复（要评分）`: the target system response to score.

## Coach A Task

Coach A reviews all 50 cases and produces the single-coach reference draft.

Please check:

1. whether the student message sounds like a real competitive-programming student;
2. whether `problem_context` is sufficient for judging the current bottleneck;
3. whether `recent_dialogue` changes what the student has already stated;
4. whether the current turn has a reasonable missing bridge;
5. whether `forbidden_content` matches the bridge the tutor should not directly complete;
6. whether `success_criteria` can support later blind review of tutor responses.

For rows marked `review_status=labeled`, fill at least:

- `turn_type`
- `diagnosis_uncertainty`
- `student_problem_solving_state`
- `student_attempt_level`
- `student_already_stated_bridge`
- `policy_risk_type`
- `primary_bridge_family`
- `primary_bridge_subtype_id`
- `evidence_type`
- `evidence_quote`
- `registered_focus_id`
- `focus_match_status`
- `help_seeking_type`
- `max_scaffold_level`
- `help_forms`
- `general_forbidden_content`
- `bridge_specific_forbidden_content`
- `leakage_risk`
- `coach_confidence`
- `review_status`

If a case should not enter held-out evaluation, set `review_status=needs_discussion` and explain the issue in `coach_free_notes`.

## Coach B Task

Coach B independently labels the 20-case overlap subset. The subset still covers all 10 categories and oversamples code-bearing rows in categories where code exists, so agreement can be estimated for both text-only bottlenecks and code-present turns.

Coach B should not inspect Coach A labels. The overlap labels will support:

- bridge family agreement;
- subtype / focus relaxed agreement;
- help level agreement;
- leakage risk agreement;
- coach confidence distribution;
- needs-adjudication case list.

## Double-annotation Subset

Coach B subset:

```text
heldout_cp_016, heldout_cp_017,
heldout_cp_011, heldout_cp_012,
heldout_cp_030, heldout_cp_032,
heldout_cp_041, heldout_cp_042,
heldout_cp_001, heldout_cp_002,
heldout_cp_006, heldout_cp_007,
heldout_cp_020, heldout_cp_021,
heldout_cp_025, heldout_cp_026,
heldout_cp_035, heldout_cp_036,
heldout_cp_046, heldout_cp_049
```

Eight of these overlap rows include `student_code_excerpt`, covering code-posting, local-condition completion, and debugging-evidence scenarios.

## Boundaries

- These 50 cases are currently `draft_needs_coach_review`, not adjudicated gold.
- Coaches may edit case wording and `success_criteria` during review.
- On 2026-05-13, the Coach A / B workbooks were regenerated with abstract bridge subtype dropdowns. Concrete algorithm context should be recorded through `algorithm_topic`, `registered_focus_id`, or `primary_bridge_subtype_note`; do not add separate subtypes for Dijkstra / SPFA / Floyd-style algorithm instances.
- Bridge-specific forbidden content should use abstract leakage shapes, such as `no_exact_guard_condition`, `no_exact_boundary_update_rule`, and `no_fully_worked_micro_trace`. See `bridge_taxonomy_abstraction_policy_v1.md`.
- Once frozen as held-out, results from the same batch must not be used to tune prompt / judge / rubric versions reported as headline results.
- EDF-inspired remains a dev / appendix candidate and is not part of the current recommended main table.
- Main-experiment prompt / judge / rubric versions should be frozen according to `prompt_freeze_decision_20260512.md` before running.

## Next Commands

After Coach A / B complete their workbooks, first validate:

```bash
python3 -m evals.aichat.validate_coach_workbook_v2 \
  --input docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx
```

Export Coach A JSONL:

```bash
python3 -m evals.aichat.export_coach_v2_gold_jsonl \
  --input docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx \
  --output-jsonl docs/research/coach_reference_heldout_v1_50_a.jsonl
```

Export Coach B similarly to:

```text
docs/research/coach_reference_heldout_v1_50_b_overlap_20.jsonl
```

Then compute agreement summary and adjudicate disagreements.

After both Coach A / B JSONL files are exported, compute agreement:

```bash
python3 -m evals.aichat.summarize_coach_label_agreement \
  --annotator-a-jsonl docs/research/coach_reference_heldout_v1_50_a.jsonl \
  --annotator-b-jsonl docs/research/coach_reference_heldout_v1_50_b_overlap_20.jsonl \
  --output-json docs/research/coach_agreement_heldout_v1_50_overlap20_20260512.json \
  --output-md-zh docs/research/coach_agreement_heldout_v1_50_overlap20_20260512.zh.md \
  --output-md docs/research/coach_agreement_heldout_v1_50_overlap20_20260512.md
```

This summary is only for deciding which cases need adjudication. In the paper, call it `coach reference agreement`, not absolute ground truth.

Generate the adjudication workbook from the agreement summary:

```bash
python3 -m evals.aichat.export_coach_adjudication_workbook \
  --agreement-json docs/research/coach_agreement_heldout_v1_50_overlap20_20260512.json \
  --annotator-a-jsonl docs/research/coach_reference_heldout_v1_50_a.jsonl \
  --annotator-b-jsonl docs/research/coach_reference_heldout_v1_50_b_overlap_20.jsonl \
  --draft-jsonl docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --output-xlsx docs/research/coach_adjudication_workbook_heldout_v1_50_overlap20.zh.xlsx
```

This workbook presents key Coach A / Coach B labels side by side and exports only `needs_adjudication_case_ids`. If you want a human to inspect all 20 overlap rows, add:

```text
--include-all-paired
```

The adjudication workbook is not an AI-response blind-review workbook; it is used to produce the final held-out reference.

After the required adjudication, export the formal frozen held-out JSONL:

```bash
python3 -m evals.aichat.export_heldout_frozen_reference \
  --draft-jsonl docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl \
  --coach-a-workbook docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx \
  --output-jsonl docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --reference-status coach_reference
```

If Coach A / Coach B disagreements have been adjudicated, use:

```text
adjudicated_reference
```

The exporter does not fabricate labels. If any of the 50 cases lacks `review_status=labeled`, it fails with `missing_labeled_reference`. After export, rerun formal preflight:

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_formal_preflight_report.json \
  --require-frozen-status
```

Only when this check returns `ok=true` should the 400-row main experiment start.
