# Hard-Gate Overfallback Targeted Rerun Report (2026-05-10)

## Goal

This targeted rerun focuses only on the two weakest cases from the previous blind review:

- `cp_bridge_010`: why 0/1 knapsack capacity should be iterated backward.
- `cp_bridge_017`: how a union-find “merge two sets” operation maps to code.

The goal was not to re-evaluate the whole system. It was to verify:

1. Whether `current_system` still falls back to the generic “send the problem id or code line” response.
2. Whether `bridge_contract + guard` blocks over-strong examples.
3. Whether `repair` solves the replacement micro-task for the student after removing leaked content.

## Artifacts

Input subset:

`evals/aichat/ad_hoc_runs/hard_gate_overfallback_20260510/seed_010_017.jsonl`

Outputs:

- `evals/aichat/ad_hoc_runs/hard_gate_overfallback_20260510/current_system_010_017.jsonl`
- `evals/aichat/ad_hoc_runs/hard_gate_overfallback_20260510/bridge_contract_guard_010_017.jsonl`
- `evals/aichat/ad_hoc_runs/hard_gate_overfallback_20260510/bridge_contract_guard_repair_010_017_promptfix.jsonl`

## Summary

| Pipeline | cp_bridge_010 | cp_bridge_017 | Takeaway |
| --- | --- | --- | --- |
| `current_system / tutor_only_no_diagnosis` | L2 response, no old fallback | L2 response, no old fallback | The hard-gate overfallback issue is fixed |
| `bridge_contract / tutor_plus_guard` | Leakage Judge returns `block`; `final_response_text` is empty | `pass`; candidate remains final | The guard catches an over-strong knapsack example |
| `bridge_contract / tutor_plus_guard_plus_repair` after prompt fix | `pass`; asks the student to compute `dp[2]` / `dp[4]` | `pass`; asks the student to map union parameters | Better aligned with bridge-oriented micro-examples |

## Findings

1. The old “send the problem id or code line” reply was a hard-gate fallback artifact, not intended system-prompt behavior.
2. `cp_bridge_010` remains a high-risk tutoring case: if the model computes the whole contrast example, it reveals the bridge that forward iteration reuses the current item.
3. The previous repair prompt was not strict enough. When Leakage Judge instructed repair to ask the student to construct or calculate an example, Repair Generator could still solve that replacement example for the student.
4. The repair prompt now explicitly says that if the repair instruction asks the student to construct, calculate, compare, or observe a replacement micro-example, the repaired response must not complete that task or provide the result. It should only provide the inputs, observation question, and blanks to fill.

## Regression Coverage

Added/updated tests:

- `test_aichat_hard_gate_fallback_regression_unit.py`
- `test_repair_response_v1_unit.py::test_repair_prompt_forbids_solving_replacement_micro_task`

Verification:

```bash
python3 -m unittest test_repair_response_v1_unit.py \
  test_aichat_hard_gate_fallback_regression_unit.py \
  test_aichat_control_precedence_unit.py \
  test_aichat_risk_routing_policy_unit.py \
  test_aichat_runtime_policy_unit.AIChatRuntimePolicyTests.test_level_gate_fallback_should_not_use_removed_small_sample_template -v
```

Result: 24 related tests passed.

## Next Step

Add these two cases to the response-quality regression set. Future tutor-prompt, repair-prompt, or leakage-judge changes should verify:

- No return to safe-but-useless fallback text.
- No direct completion of the missing bridge.
- Micro-examples contain an observation question and a transferable abstraction goal, not just a temporary exercise.
