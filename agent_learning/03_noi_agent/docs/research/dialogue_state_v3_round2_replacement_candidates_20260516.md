# Dialogue-State v3 Round2 Replacement Candidates 20260516

This note records the replacement handling for the 3 `problem_bridge_mismatch` cases after Coach A's round2 re-check. It records a data revision inside the case/source review gate. It does not evaluate AI responses and does not freeze the formal experiment.

## 2026-05-16 Status Update

Coach A has re-checked the 3 replacement candidates and accepted all of them:

- `dialogue_v3_035_data_structure_operation_semantics`: accepted
- `dialogue_v3_036_correctness_invariant`: accepted
- `dialogue_v3_037_correctness_invariant`: accepted

Therefore, the dialogue-state v3 50-case set has been promoted to `reviewed_candidate`. See [dialogue_state_v3_case_source_gate_pass_20260516.md](dialogue_state_v3_case_source_gate_pass_20260516.md).

## Replaced Problem Cases

| slot | Original source | Original issue | Decision |
|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | P2672 "Salesman" | Closer to greedy/contribution selection, not update/query data-structure maintenance semantics | Replace |
| `dialogue_v3_036_correctness_invariant` | P10709 "Party" | Closer to adjacent-restriction DP state/transition reasoning, not adjacent-exchange proof | Replace |
| `dialogue_v3_037_correctness_invariant` | P10728 "Swords" | Closer to sorted dominance checking / scan invariant, not exchange reasoning | Replace |

## New Replacement Candidates

| slot | New source | Bridge bucket | Rationale |
|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | P3374 "Fenwick Tree 1" | Data-structure operation semantics | The problem explicitly contains point add and range-sum query, making it suitable for update/query maintained-summary semantics |
| `dialogue_v3_036_correctness_invariant` | P1223 "Queueing for Water" | Correctness / invariant | Suitable for adjacent-exchange comparison of two queue orders and their effect on total waiting time |
| `dialogue_v3_037_correctness_invariant` | P1080 "King's Game" | Correctness / invariant | Suitable for adjacent-exchange comparison of two ministers and the local worst reward after swapping |

## Generated Artifacts

- `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- `docs/research/dialogue_state_v3_50_source_and_case_review.en.xlsx`
- `docs/research/coach_seed_labeling_workbook_dialogue_state_v3_50.zh.xlsx`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3.zh.xlsx`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3.en.xlsx`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3_20260516.json`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3_20260516.zh.md`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3_20260516.md`

## Re-check Request (Completed)

Coach A reviewed only these 3 replacement candidates and checked:

1. whether the problem source fits the bridge bucket;
2. whether `recent_dialogue -> student_message -> missing_bridge -> success_criteria` is coherent;
3. whether forbidden content is neither too strict nor too loose;
4. whether the case can enter the `reviewed_candidate` set before formal response generation.

## Current Status

These 3 cases have passed, and the 50-case set has been exported as `reviewed_candidate`. This status is still not gold data; it only means the case/source gate has passed. Prompt/rubric freeze, AI response generation, human blind review, partial double annotation, and adjudication are still required.
