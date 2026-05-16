# Dialogue-State v3 50-case Coach A Round1 Revision Log 20260516

This note records the first revision pass after Coach A reviewed `dialogue_state_v3_50_source_and_case_review_zh6_case_source_reviewed (1).xlsx`. This stage is still the case/source review gate; it does not evaluate any AI condition responses.

## Coach A Review Result

- Reviewed cases: 50
- `accept`: 32
- `revise`: 18
- `drop`: 0
- `discuss`: 0
- Main issue types:
  - `context_mismatch`: 11
  - `bridge_label_issue`: 7
- Reviewer confidence:
  - `high`: 42
  - `medium`: 8

Structured summaries:

- `docs/research/dialogue_state_v3_case_review_summary_coach_A_20260516.json`
- `docs/research/dialogue_state_v3_case_review_summary_coach_A_20260516.zh.md`
- `docs/research/dialogue_state_v3_case_review_summary_coach_A_20260516.md`

## Revised Cases

This pass keeps the original 50 problem sources and bridge-bucket quotas. Revisions focus on the current student message, followability evidence, and selected missing-bridge / success-criteria text so that the `recent_dialogue -> student_message -> missing_bridge -> success_criteria` chain is coherent.

| Range | Bridge bucket | Coach A issue | Revision |
|---|---|---|---|
| `dialogue_v3_027`-`030` | Aggregation / contribution / prefix | Student replies sounded like binary-search true/boundary direction rather than contribution marking | Rewrote them around marking positions, cancellation points, and prefix/common-point aggregation |
| `dialogue_v3_031`-`035` | Data-structure operation semantics | Student replies drifted toward binary search, debugging, or implementation boundary rather than update/query semantics | Rewrote them around maintained summaries, which quantity changes after update, and why query can be composed from maintained values |
| `dialogue_v3_036`-`040` | Correctness / invariant | Recent dialogue was about exchange/invariants, but current replies drifted to sample mismatch, printed variables, or update order | Rewrote them around adjacent-choice exchange and what quantity stays unchanged or does not get worse |
| `dialogue_v3_044` | Implementation boundary | Student asked about a single character/space, but the missing bridge was too generic | Rewrote the bridge as mapping one output character position to a block cell/edge/corner |
| `dialogue_v3_045`-`047` | Debugging evidence / minimal counterexample | Current questions were more conceptual than debugging-evidence oriented | Rewrote them around minimal counterexamples, minimal bad inputs, intermediate variables, or a small hand-check point |

## Preserved Design Constraints

- Problem sources remain real Luogu problems; old online AI replies are not used as data.
- Student-message length distribution remains: `short=20 / medium_short=15 / medium_long=10 / long=5`.
- Turn distribution remains: `initial=10 / followup=40`.
- Student followability remains: `NA=10 / F1=6 / F2=19 / F3=10 / F4=5`.
- The dataset remains `draft_needs_coach_review`; it is not gold data.

## Generation And Validation

Regenerated artifacts:

- `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- `docs/research/dialogue_state_v3_50_source_and_case_review.en.xlsx`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18.zh.xlsx`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18.en.xlsx`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_20260516.json`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_20260516.zh.md`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_20260516.md`
- `docs/research/dialogue_state_v3_generation_report_20260513.json`
- `docs/research/dialogue_state_v3_validation_report_20260513.json`

Validation:

- `row_count=50`
- `ok=true`
- `error_count=0`

## Next Step

Send `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18.zh.xlsx` back to Coach A for targeted re-check of the 18 revised cases only. If these pass, export a `reviewed_candidate` dataset version, then proceed to prompt/rubric freeze and the pre-response-generation gate.
