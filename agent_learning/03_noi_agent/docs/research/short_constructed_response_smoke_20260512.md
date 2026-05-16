# Short Constructed Response Prompt Smoke 2026-05-12

This development-stage smoke checks whether the “prefer short constructed responses, use multiple-choice sparingly” prompt patch reduces answer-slot critical-bridge leakage. It is not a held-out result and not a coach blind-review result.

## Setup

- Input: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Cases: first 3 development cases
- Output directory: `evals/aichat/ad_hoc_runs/short_constructed_response_smoke_20260512_after_answer_slot_patch/`
- Conditions:
  - `enhanced_prompt_only`
  - `dbox_inspired_decomposition_tutor`
  - `bridge_contract`
- Checks: runner stage errors + static leakage-risk lint.

## Results

| Condition | Completed / total | Runner errors | Final static risk | Answer-slot | Filled-trace | Worked-example | Avg LLM calls | P50 latency ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| enhanced_prompt_only | 3/3 | 0 | 0.667 | 0.333 | 0.333 | 0.000 | 1.0 | 38432.719 |
| dbox_inspired_decomposition_tutor | 3/3 | 0 | 1.000 | 0.333 | 0.667 | 0.000 | 1.0 | 19932.202 |
| bridge_contract | 3/3 | 0 | 0.667 | 0.667 | 0.333 | 0.000 | 2.0 | 47519.210 |

## Findings

1. The runner path is stable: all three conditions completed with `error_count=0`.
2. “Do not default to multiple-choice” does not eliminate answer-slot behavior. The models still reformulate the critical bridge as short answer slots, such as:
   - `should check(4) return true or false`
   - `where should it be handled`
   - `what value should each node get`
   - `what should dp[i][j] record`
3. The DBox-inspired baseline still shows filled-trace / answer-slot risk. A single-turn step-tree-style prompt is not a stable substitute for leakage control.
4. Bridge Contract remains vulnerable to turning a correct missing-bridge diagnosis into a direct request for the student to fill the missing bridge itself. This supports the earlier claim that correct diagnosis does not imply safe tutoring.

## Research v1 Implication

This smoke does not support continuing to add prompt rules indefinitely. The safer conclusion is:

```text
Short constructed response is an interaction design principle, not a leakage-control mechanism.
Prompt wording may reduce some multiple-choice tendency, but it does not reliably prevent answer-slot leakage.
```

Next steps should treat answer-slot / filled-trace as explicit failure types for Guard, Repair, static lint, and coach blind review, rather than relying only on Tutor prompt control.

## Recommendation

1. Stop adding long prompt rules for this same failure mode, to avoid prompt creep.
2. Keep `answer-slot` and `filled-trace` risk columns in dev ablation reports.
3. For high-risk bridge families, evaluate `+ guard`, `+ repair`, or deterministic fallback instead of expecting `tutor_only` to be safe.
4. Before the formal 50-case evaluation, freeze prompts and evaluate strong prompt, DBox-inspired, and Bridge Contract variants on held-out answer-slot leakage.
