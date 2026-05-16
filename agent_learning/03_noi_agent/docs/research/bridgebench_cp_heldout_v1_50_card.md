# BridgeBench CP Held-out v1 50 Draft Dataset Card

Date: 2026-05-12

File: `docs/research/bridgebench_cp_heldout_v1_50_draft.jsonl`

Coach A review workbook: `docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx`

Coach B overlap workbook: `docs/research/coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx`

This is the **50-case held-out draft** for Research v1. It is meant for coach review, editing, and partial double annotation before the formal held-out main experiment. It is not adjudicated gold and should not be used as a final paper headline result yet.

## Status

| Item | Status |
|---|---|
| Number of cases | 50 |
| Dataset status | `draft_needs_coach_review` |
| Directly usable as gold? | No |
| Reused from the 20-case dev/regression set? | No; case IDs use `heldout_cp_###` |
| Needs Coach A review? | Yes |
| Needs Coach B double annotation? | Yes, at least 20 cases |
| Coach A review workbook exported? | Yes, `coach_seed_labeling_workbook_heldout_v1_50_coach_a_full.zh.xlsx` |
| Coach B overlap workbook exported? | Yes, `coach_seed_labeling_workbook_heldout_v1_50_coach_b_overlap_20.zh.xlsx` |

## Why This Workbook Has No AI Response

This dataset card describes **case/reference annotation**, not response blind review. In this stage, coaches review:

- whether the student message is realistic;
- whether the problem/context is sufficient;
- whether recent dialogue changes what the student has already stated;
- whether the current missing bridge, forbidden content, and success criteria are reasonable.

Therefore, the 50-case reference-labeling workbook **does not need AI responses**. AI responses will be generated later by the frozen system conditions and exported into a separate response blind-review workbook. That later workbook will include both the prior context AI reply and the target AI response to score.

## Recent Dialogue Distribution

| recent_dialogue type | Count | Meaning |
|---|---:|---|
| `none` | 10 | `recent_dialogue = N/A`, simulating a true single-turn input |
| `short` | 25 | One to two short prior turns, simulating a student who has already given some state or bottleneck evidence |
| `long` | 15 | Two to four prior turns, simulating a student who has been probed and has partially stated known information |

This distribution is intentional: Research v1 should not evaluate only single-turn Q&A. It should also evaluate whether AIChat can use recent dialogue to decide what the student has already stated and what remains missing. `recent_dialogue` affects critical bridge leakage: the same AI response may be justified confirmation when the student has already stated the bridge, but leakage when the student has not.

## Student Code Excerpt Distribution

| student_code_excerpt type | Count | Meaning |
|---|---:|---|
| `none` | 38 | `student_code_excerpt = N/A`; the student describes the bottleneck without code |
| `present` | 12 | The student provides a local code snippet, failing fragment, or condition slot |

These 12 code-bearing cases cover common AIChat debugging, boundary, local-condition, and code-understanding situations. They do not license the tutor to rewrite full code; coaches should still judge whether the response stays evidence-based and avoids directly completing the critical bridge.

## Fields

Each row contains:

- `case_id`
- `category`
- `problem_ref`
- `student_message`
- `problem_context`
- `recent_dialogue`
- `student_code_excerpt`
- `student_known_state`
- `missing_bridge`
- `allowed_help_level`
- `forbidden_content`
- `success_criteria`
- `review_notes_for_coach`
- `reference_label_status`

## Category Distribution

| Category | Count |
|---|---:|
| `dp_state` | 5 |
| `dp_transition` | 5 |
| `binary_search_predicate` | 5 |
| `binary_search_boundary` | 4 |
| `graph_tree_modeling` | 5 |
| `greedy_correctness` | 5 |
| `data_structure_semantics` | 5 |
| `implementation_boundary` | 5 |
| `debugging_evidence` | 4 |
| `policy_request` | 7 |

## Usage Rules

1. These 50 cases must not be used to tune prompts and then reported as headline held-out results in the same version.
2. Coaches may first edit draft wording and `success_criteria`; only after review should the dataset be frozen.
3. If a row is not suitable for judging response quality or leakage, replace it instead of forcing it into the set.
4. Before the main experiment, every row should answer two questions:
   - What counts as a good response?
   - What counts as prematurely completing the current missing bridge?

## Next Step

1. Coach A reviews all 50 cases.
2. Coach B independently labels at least 20 cases; the current overlap subset includes 8 code-bearing cases to estimate agreement on code-present turns.
3. Compute agreement and adjudicate disagreements.
4. Freeze the dataset as `bridgebench_cp_heldout_v1_50.jsonl`.
5. Run the main experiment with frozen prompt / judge / rubric versions.
