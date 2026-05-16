# Dialogue-State v3 50-case Case/Source Gate Pass 20260516

This note records that the dialogue-state v3 50-case set has passed Coach A's case/source review gate. This status means the cases have been reviewed for problem source, dialogue context, student wording, bridge labels, forbidden content, and success criteria. It does not mean AI responses have been blind-reviewed, and it does not mean gold/reference labels are complete.

## Review Flow

1. Full review: Coach A reviewed all 50 case/source rows.
   - accept: 32
   - revise: 18
   - drop: 0
   - discuss: 0
2. Round1 targeted re-check: Coach A re-checked the 18 revised rows.
   - accept: 15
   - still revise: 3
3. Round2 replacement re-check: after replacing the 3 `problem_bridge_mismatch` rows, Coach A re-checked the 3 replacement candidates.
   - accept: 3
   - revise: 0

## Round2 Replacement

| slot | Original source | New source | Decision |
|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | P2672 "Salesman" | P3374 "Fenwick Tree 1" | accept |
| `dialogue_v3_036_correctness_invariant` | P10709 "Party" | P1223 "Queueing for Water" | accept |
| `dialogue_v3_037_correctness_invariant` | P10728 "Swords" | P1080 "King's Game" | accept |

## Reviewed Candidate Dataset

Exported:

- `docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl`
- `docs/research/dialogue_state_v3_50_reviewed_candidate_validation_report_20260516.json`

Validation summary:

- `row_count=50`
- `reference_label_status=reviewed_candidate`: 50 rows
- `problem_source_platform_counts={"luogu": 50}`
- `recent_dialogue_distribution={"none": 10, "short": 25, "long": 15}`
- `student_code_excerpt_distribution={"none": 33, "present": 17}`
- `student_message_length_distribution={"short": 20, "medium_short": 15, "medium_long": 10, "long": 5}`
- `error_count=0`

## Boundary

`reviewed_candidate` only means the case/source set passed review. It is not:

- gold data;
- an adjudicated reference;
- a coach response review result;
- a formal frozen reference.

For paper headline results, the project still needs:

1. prompt / rubric / grader freeze;
2. AI response generation on the reviewed candidate set;
3. anonymous human coach blind review;
4. partial double review and agreement / adjudication;
5. paired analysis and LLM Judge calibration.

## Next Step

The project can now enter the **prompt/rubric freeze gate**. Case content should not change before freeze unless the case/source review gate is explicitly reopened and logged as a patch.
