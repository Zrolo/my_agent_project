# Literature Baseline Smoke1 Report - 2026-05-11

This report records a 1-case smoke test for the new literature baselines. It checks schema stability and obvious leakage risk only. It is not a paper result.

## Input

- Seed file: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Case: `cp_bridge_001`
- Model provider: `deepseek_flash`
- Pipeline: `tutor_only_no_diagnosis`
- Online student AIChat: not touched

## Systems

| System | Output file | LLM calls | Error |
|---|---|---:|---|
| `dbox_inspired_decomposition_tutor` | `evals/aichat/ad_hoc_runs/dbox_inspired_smoke1_20260511.jsonl` | 1 | none |
| `codehelp_codeaid_no_direct_solution_tutor` | `evals/aichat/ad_hoc_runs/codehelp_codeaid_smoke1_20260511_v2.jsonl` | 1 | none |
| `bridge_inspired_expert_decision_tutor` | `evals/aichat/ad_hoc_runs/bridge_inspired_expert_decision_smoke1_20260511_v2.jsonl` | 1 | none |
| `socratic_no_answer_tutor` | `evals/aichat/ad_hoc_runs/socratic_no_answer_smoke1_20260511_v5.jsonl` | 1 | none |

## Observations

### DBox-inspired

The output contained the expected fields:

- `baseline_group=literature_inspired_decomposition`
- `decomposition_view`
- `current_substep`
- `hint_level=general_question`
- `final_response_text`

The output did not contain disabled DBox-style fields such as `correctStep`, `correct_code`, `detailed_hint`, pseudocode, reveal code, or reveal substep.

Risk: the response still frames the student task around endpoint/LCA marking. It does not provide the complete formula, but coach review is needed to judge whether it is too strong.

### CodeHelp/CodeAid-style

The output contained the expected fields:

- `baseline_group=literature_inspired_guardrail`
- `self_check`
- `final_response_text`

After prompt tightening, the response shifted toward a tiny-chain observation task and did not provide full marking formulas or code. It still references endpoint/LCA relevance, so coach review should judge whether this is minor leakage.

### Bridge-inspired Expert Decision

The output contained:

- `baseline_group=literature_inspired_expert_decision`
- `student_error_or_gap`
- `remediation_strategy`
- `teaching_intention`
- `final_response_text`

The first smoke produced a formula-like root-path decomposition in the student-visible response. The prompt was tightened to forbid formula-like decomposition, parent/neighbor-of-LCA hints, and analogy-to-formula conversion.

The second student-visible response no longer exposed the root-path formula or LCA-parent compensation. However, the internal `student_error_or_gap` field may still mention answer-bearing slots such as `fa[lca]`. This field is an internal trace and must not be shown in student-facing responses or blind-review workbooks.

### Socratic/no-answer

The output contained:

- `baseline_group=literature_inspired_socratic`
- `question_intent`
- `final_response_text`

Earlier smoke runs exposed an important boundary: even a no-answer Socratic prompt can leak by pre-filling answer-bearing slots, such as asking where to subtract after endpoint +1 marks. The prompt was tightened to forbid formula-like decomposition, parent/neighbor-of-LCA hints, exact u/v/LCA operation questions, `+1/-1` marking hints, and pre-filled endpoint marks.

The fifth student-visible response shifted toward drawing a tiny path and observing which nodes should be counted. It still mentions an upward aggregation observation task, so coach blind review is needed to judge whether it remains too strong.

## Prompt Patch

| Baseline | Patch |
|---|---|
| `codehelp_codeaid_no_direct_solution_tutor` | For answer-bearing slots such as u/v/LCA operations or check direction, ask for tiny-example observation rather than exact operations |
| `bridge_inspired_expert_decision_tutor` | Forbid formula-like decomposition, parent/neighbor-of-LCA hints, and analogy-to-formula conversion |
| `socratic_no_answer_tutor` | Forbid formula-like decomposition, endpoint/LCA operation questions, `+1/-1` marking hints, and pre-filled endpoint marks; ask only neutral observation questions |

## Next Steps

1. Run a 3-case smoke covering tree path difference, binary-search check, and DP state/transition.
2. Ensure blind-review workbooks show only `final_response_text`, not internal traces.
3. Run a 10-20 case dev ablation across strong prompt, literature baselines, DBox-inspired, Bridge-inspired, and Bridge Contract variants.
