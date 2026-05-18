# Paper Methods / Evaluation Draft: Dialogue-State v3 20260518

## 1. Scope

CP-MissingBridgeBench evaluates a specific failure mode in competitive-programming tutoring: the student has expressed a partial idea or blocker, but still lacks the key reasoning bridge between their current state and the next useful solving action. We call this gap a missing bridge.

The dialogue-state v3 evidence package focuses on turn-level tutor response evaluation. Each case includes problem context, recent dialogue, the student's current message, a case-specific rubric, and candidate responses from several tutoring harnesses. This evaluation does not claim full coverage of all CP tutoring situations and does not validate an online active-mode system. It is a formal human-review evidence candidate for comparing quality-safety-burden trade-offs across offline tutoring harnesses.

The paper headline should use only the `main_scaffold_eval` slice. `main_eval_with_caution`, `clarification_safety_slice`, `policy_safety_slice`, and the all-50 aggregate are sensitivity / appendix evidence only.

## 2. Core Concepts

### Missing Bridge

A missing bridge is the local reasoning gap that the student has not yet crossed but needs in order to make the next useful solving move. It is not a fixed algorithm label. The same DP problem, for example, may involve different missing bridges at different tutoring turns: state semantics, transition source, boundary initialization, correctness reasoning, or implementation debugging.

### Critical Bridge Leakage

Critical bridge leakage occurs when a tutor does not directly provide a full solution or full code, but prematurely reveals the intermediate reasoning that the student should still derive. This is different from ordinary informative tutoring: a good tutor may provide context, light hints, checks, or low-burden next steps. The leakage risk comes from completing the current missing bridge too early.

### Taxonomy Framing

The taxonomy uses three layers:

```text
cognitive bridge family + leakage mechanism + surface anchor
```

`state_representation_semantics`, `transition_recurrence_source`, and `predicate_check_semantics` are operational cognitive bridge families. DP state, binary-search check, lazy propagation, tree difference, local code, greedy proof, and debugging trace are surface anchors that instantiate broader cognitive bridges and leakage mechanisms in concrete algorithmic contexts. The paper should not describe the benchmark as only covering DP/check/lazy/tree/local-code scenes.

## 3. Dataset And Slices

Dialogue-state v3 contains 50 reviewed candidate cases. Each case preserves the current dialogue state rather than presenting only an isolated problem statement and question. The 50 cases are separated by paper use:

| slice | case_n | paper use |
| --- | ---: | --- |
| `main_scaffold_eval` | 31 | Main scaffold-quality, leakage, and burden comparison |
| `main_eval_with_caution` | 5 | Sensitivity / appendix |
| `clarification_safety_slice` | 10 | Clarification, non-over-inference, and context-insufficient safety |
| `policy_safety_slice` | 4 | Safety redirection for direct answer/code requests |

This slicing is part of the interpretation protocol. The main table should not pool all four case types into one headline mean.

## 4. Case-Specific Rubric

Before scoring each case, we fix a case-specific rubric with at least:

- `success_criteria`: what a successful tutor response should help the student do in this turn;
- `forbidden_content`: the bridge, answer, or code content that should not be revealed yet;
- `critical_bridge_boundary`: the boundary of the current missing bridge;
- `acceptable_reveal`: light hints, clarifications, or background information that are allowed;
- `expected_student_next_action`: the most reasonable low-burden next student action.

This makes the review conditional on the student's current state, problem context, and turn-level teaching goal, rather than on a generic notion of whether a response "sounds like a good tutor."

## 5. Conditions

The main human review compares 7 anonymized conditions, for 350 responses in total. Coaches do not see condition names during blind review. After de-anonymization, the paper may describe them as:

| condition | role | interpretation boundary |
| --- | --- | --- |
| `enhanced_prompt_only_clean` | Strong prompt-only baseline | Strong tutoring prompt baseline without case-specific Bridge Contract. |
| `codehelp_codeaid_clean` | No-direct-solution programming-help baseline | Tests whether no-direct-code / no-direct-solution guardrails are sufficient for critical bridge leakage. |
| `dbox_inspired_clean` | Literature-inspired decomposition baseline | DBox-inspired single-turn decomposition scaffold; not a DBox reproduction. |
| `dbox_inspired_guard` | DBox-inspired + guard-instrumented variant | Guard-only mainly provides runtime leakage signal in the current main experiment; it does not rewrite final responses. |
| `bridge_guided_dbox_style_guard` | Bridge-guided decomposition variant | Uses bridge signal to guide a DBox-style response; still a guard-instrumented condition. |
| `bridge_contract_compact_guard` | Bridge Contract compact + guard-instrumented method | Uses compact bridge contract and guard signal; Guard-only is not a rewrite condition. |
| `bridge_contract_compact_guard_repair` | Bridge Contract compact + Guard/Repair method | The student-visible response may come from the Repair stage; main experiment means show condition-level trends, not Repair causality by themselves. |

All conditions are offline evaluation harnesses, not the online default AIChat system.

## 6. Human Review Protocol

Coach A and Coach B each completed a full blind review of all 350 responses. The review procedure is:

1. Read the problem context and necessary problem statement.
2. Read the case-specific rubric.
3. Read the recent dialogue and the student's current message.
4. Evaluate only the candidate AI response.
5. Fill primary metrics, diagnostic metrics, and reliability fields.
6. Add required notes for high-risk cases.

Required notes are used for major / answer leakage, `show=no`, `overall_quality<=2`, top or last ranking within a case, low confidence, and samples needing discussion.

Coach A, Coach B, and priority60 adjudication are expert reference / adjudicated sensitivity views, not gold. A/B disagreement is treated as real rater sensitivity in pedagogical judgment, not as a failure of the benchmark. The paper controls and reports this uncertainty through double review, priority adjudication, slice analysis, and sensitivity analysis.

## 7. Metrics

Primary metrics include:

| metric | role |
| --- | --- |
| `overall_quality` | 1-5 overall tutoring-quality judgment |
| `student_ready_pass` | Composite judgment of whether the response is ready to show to a student |
| `safe_ready_pass` | Safety-and-usefulness readiness threshold |
| `critical_leakage_label` | `no_leakage` / `minor_bridge_leakage` / `major_bridge_leakage` / `answer_leakage` |
| `scaffold_sufficiency` | Prevents "safe but not helpful" responses from being treated as successful |
| `student_response_burden` | Interaction burden imposed on the student's next reply |

Diagnostic metrics explain errors and calibrate LLM graders; they are not the sole win/loss criterion. They include whether the response identifies the blocker, is grounded in the problem and dialogue, uses appropriate scaffold strength, gives a clear next step, keeps a single focus, and uses a bridge-oriented micro-example when appropriate.

## 8. Analysis Plan

The paper organizes evidence by class:

| evidence class | use |
| --- | --- |
| main result | `main_scaffold_eval` + priority60 adjudicated + Coach A primary view |
| sensitivity | Coach A only, Coach B only, priority60 + Coach A, priority60 + Coach B, all-case appendix |
| slice analysis | Separate reporting for main scaffold, caution, clarification safety, and policy safety |
| paired uncertainty | Same-case W/T/L, mean delta, bootstrap CI, and permutation test |
| stress test | Same-candidate before/after Repair causal stress test |
| fairness sensitivity | DBox+Repair 20-case targeted add-on |
| calibration | DeepSeek LLM grader calibration as auxiliary grader assessment |

Paired comparisons should report win/tie/loss, mean delta, safe-ready delta, major+answer leakage delta, and uncertainty. When CIs cross zero, the paper should use favorable trend / trade-off wording rather than significant dominance.

## 9. Repair And Guard Interpretation

Guard-only conditions are guard-instrumented / guard-checked conditions in the current main experiment. They provide leakage-risk signals; unless a block fallback is triggered, they do not rewrite the final student-visible response. The paper therefore must not state that Guard-only fixed final outputs.

Repair causality comes from the same-candidate before/after stress test. That test fixes the same original candidate and blindly compares before_repair and after_repair responses. The `bridge_contract_compact_guard_repair` main condition supports condition-level trends, but does not by itself prove Repair causality.

## 10. Reproducibility

The main evidence chain is locked by the evidence manifest and reproduction scripts:

- `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`
- `evals/aichat/verify_dialogue_state_v3_reports.py`

Before submission, run:

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_final.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
```

## 11. Paper-Safe Wording

Can write:

- CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
- DBox-inspired decomposition is a strong baseline.
- Bridge Contract compact + Guard/Repair shows favorable overall and critical-leakage-control trends under the primary human-review view.
- No-direct-solution prompting does not eliminate critical bridge leakage.
- Human review remains necessary; LLM graders are auxiliary only.

Cannot write:

- Bridge Contract significantly and comprehensively outperforms all baselines.
- Guard-only fixed final outputs.
- Repair causality is proven by the main-experiment mean alone.
- Priority60 or either coach's labels are gold.
- The all-50 aggregate is the main headline.
- The current 50-case set covers all CP tutoring situations.
