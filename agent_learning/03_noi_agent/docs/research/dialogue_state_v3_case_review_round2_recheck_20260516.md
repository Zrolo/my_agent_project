# Dialogue-State v3 Coach A Round2 Targeted Re-check 20260516

This note summarizes Coach A's targeted re-check of the 18 round1 revised cases. This stage remains the case/source review gate. It does not evaluate any AI condition response and does not change prompts.

## 2026-05-16 Resolution Status

The 3 unresolved slots in this note have been resolved through replacement:

- `dialogue_v3_035_data_structure_operation_semantics`: replaced with P3374 "Fenwick Tree 1"; accepted by Coach A.
- `dialogue_v3_036_correctness_invariant`: replaced with P1223 "Queueing for Water"; accepted by Coach A.
- `dialogue_v3_037_correctness_invariant`: replaced with P1080 "King's Game"; accepted by Coach A.

Therefore, the dialogue-state v3 50-case set has been exported as `reviewed_candidate`. See [dialogue_state_v3_case_source_gate_pass_20260516.md](dialogue_state_v3_case_source_gate_pass_20260516.md).

## Input File

- `/Users/kongyouli/Downloads/dialogue_state_v3_case_review_coach_A_round1_recheck_18_zh_rechecked.xlsx`

## Structured Result

- Re-checked cases: 18
- `accept`: 15
- `revise`: 3
- `drop`: 0
- `discuss`: 0
- Remaining issue type:
  - `problem_bridge_mismatch`: 3

Summary files:

- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_summary_20260516.json`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_summary_20260516.zh.md`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_summary_20260516.md`

## Cases Still Needing Action

| case_id | Current bridge bucket | Coach A re-check note | Recommended action |
|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | Data-structure operation semantics | P2672 is closer to greedy/contribution selection; update/query and maintained-node-summary wording does not fit the problem | Do not force another text patch. Replace with a true update/query or maintained-summary problem; if P2672 is retained, move it out of the data-structure bucket |
| `dialogue_v3_036_correctness_invariant` | Correctness/invariant | P10709 is closer to adjacent-restriction DP state/transition reasoning and does not fit an adjacent-exchange proof | Do not force another text patch. Replace with a greedy problem that genuinely needs an exchange argument; if P10709 is retained, move it to a DP state/transition bucket |
| `dialogue_v3_037_correctness_invariant` | Correctness/invariant | P10728 is closer to sorted dominance checking / scan invariant maintenance than swapping two choices | Either rewrite as a dominance/scan-invariant case or replace with an exchange-argument problem; it must be re-checked before entering the formal set |

## Decision

These 3 cases should not enter formal response generation as-is. The issue is structural problem-bridge mismatch, not minor student wording. Forcing them into the original buckets would contaminate downstream system comparisons.

Recommended next step:

1. Keep the 47 accepted/usable cases.
2. Generate or select replacement candidates for the 3 unresolved slots:
   - 1 true data-structure update/query maintenance-semantics case;
   - 2 correctness/invariant cases that genuinely involve exchange reasoning, dominance, or scan invariants.
3. Export a 3-case replacement re-check workbook for Coach A.
4. After these 3 pass, export the `reviewed_candidate` dataset version.

## Current Status

This note describes the round1 re-check status before replacement. After the replacement re-check passed, the 50-case set was promoted to `reviewed_candidate`. It is still not gold data and should not be used for headline claims before prompt/rubric freeze, AI response blind review, partial double annotation, and adjudication.
