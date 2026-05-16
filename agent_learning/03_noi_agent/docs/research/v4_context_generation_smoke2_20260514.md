# v4 Context Generation Smoke2 20260514

中文版本：`v4_context_generation_smoke2_20260514.zh.md`

This report records a 2-case × 5-condition generation-only smoke run on `bridgebench_cp_heldout_v4_50_draft.jsonl`. It checks context flow and response completeness only; it is not a paper-level result.

## Configuration

- Input: `docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl`
- Output directory: `evals/aichat/ad_hoc_runs/v4_context_generation_smoke2_20260514`
- Condition set: `dbox_bridge_hybrid`
- Cases: 2
- Conditions: 5
- Expected rows: 10
- Actual rows: 10
- Empty responses: 0
- Integrity: pass

## Main Observations

- `generation_context_source=parsed_recent_dialogue` and `generation_message_count=3`, which confirms that the runner parses the synthetic follow-up dialogue as history and appends the current student question as the final user message.
- The v4 context mismatch issue is largely fixed at the smoke level: models now see the prior AI probe and the current short student reply instead of inferring the stuck point from the problem statement alone.
- Quality risk remains: some conditions still produce definition-first / answer-slot style responses, such as directly asking the student to define `dp[i][j]` or the full semantic meaning of a table cell. This means context alignment is not a substitute for leakage and scaffolding review.

## Conclusion

v4 can continue as the candidate input for the generation-only main scaffold dev run, but the formal run must still check whether state/representation semantics are directly revealed. This smoke does not establish condition rankings; it only shows that the data pipeline is better suited for follow-up tutoring-turn evaluation than v3.
