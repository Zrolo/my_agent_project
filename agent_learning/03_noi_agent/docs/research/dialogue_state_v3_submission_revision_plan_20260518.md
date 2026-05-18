# Dialogue-State v3 Submission Revision Plan 20260518

## 1. Current Status

Dialogue-state v3 should currently be described as:

```text
formal human-review evidence candidate + evidence-package audit passed with minor revision items
```

It is not final gold and not an online-system validation. The current evidence is enough to support a manuscript draft centered on the evaluation framework, human review, and quality-safety-burden trade-offs, but the paper must keep the following boundaries:

- The main headline uses only the `main_scaffold_eval` slice.
- The all-50 aggregate is appendix / sensitivity only.
- Coach A, Coach B, and priority60 adjudicated labels are not gold.
- Guard-only is guard-instrumented runtime signal, not final-response rewrite.
- Repair causality comes only from the same-candidate stress test.
- DBox+Repair is targeted fairness sensitivity, not a full main condition.
- The DeepSeek LLM grader is auxiliary calibration only and cannot replace human coaches.

## 2. Revisions Already Addressed After External Review

The following minor revisions have been addressed:

1. The Web-AI review bundle v2 now includes the relevant `evals.review` dependencies, so the core unit tests can be rerun inside the bundle.
2. The relationship between `dbbbd5c`, `33a5dd7`, and the branch tip is documented in the index, handoff, and reviewer prompt:
   - `dbbbd5c` is the evidence-content base;
   - `33a5dd7` is the evidence-package gates checkpoint;
   - later branch-tip commits mainly tighten handoff / prompt / wording unless explicitly stated otherwise.
3. Positive paper-facing strong-win wording has been downgraded to `favorable trend`.
4. Results / Discussion now explicitly separates main result, sensitivity, stress test, and calibration evidence.
5. `verify_dialogue_state_v3_reports.py`, `reproduce_dialogue_state_v3_tables.py`, and the core unit tests pass in the full repository.

## 3. P0: Required Before Manuscript Integration

### P0.1 Lock the Methods / Evaluation Structure

Writing sources:

- `docs/research/evaluation_protocol_v3.md`
- `docs/research/response_review_rubric_v3.md`
- `docs/research/baseline_protocol_v1.md`
- `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`
- `docs/research/dialogue_state_v3_paper_claims_final_gate_20260518.md`

The paper should explain:

- a missing bridge is the key reasoning step missing between what the student currently knows and the next useful solving action;
- critical bridge leakage occurs when a tutor does not give the full code or solution, but prematurely reveals the intermediate reasoning the student should still derive;
- the taxonomy uses `cognitive bridge family + leakage mechanism + surface anchor`;
- concrete algorithm patterns are surface anchors, not evidence that the benchmark only covers those small scenes;
- the 7 conditions are offline human-review harnesses, not the online default system;
- blind review uses case-specific rubrics: success criteria, forbidden content, acceptable reveal, and expected student next action are defined before scoring.

Acceptance criteria:

- No positive claim uses wording such as `final gold`, `Guard repairs final output`, or `Bridge Contract significantly outperforms all baselines`.
- The all-50 mean is not used as the main headline.

### P0.2 Lock the Results Tables and Paragraphs

Writing sources:

- `docs/research/dialogue_state_v3_main_paper_ready_tables_20260517.md`
- `docs/research/dialogue_state_v3_pairwise_win_tie_loss_20260517.md`
- `docs/research/paper_results_discussion_section_dialogue_state_v3_20260518.md`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`
- `evals/aichat/verify_dialogue_state_v3_reports.py`

Recommended section order:

1. Human review reliability.
2. Main scaffold evaluation.
3. Pairwise uncertainty.
4. Sensitivity and slice analysis.
5. Observed error taxonomy.
6. Repair same-candidate stress.
7. DBox+Repair fairness add-on.
8. DeepSeek LLM grader calibration.

Acceptance criteria:

- `bridge_contract_compact_guard_repair` is described only as showing favorable overall / critical-leakage-control trends under the primary human-review view.
- Pairwise comparisons with CIs crossing 0 are not described as significant dominance.
- Causal Repair wording cites the same-candidate stress test, not the main-experiment condition mean.

### P0.3 Lock Discussion / Limitations

Limitations that must be reported directly:

- The 50-case set is a high-risk dialogue-state CP tutoring evidence candidate, not full CP tutoring coverage.
- Student-ready and rank are sensitive to rater strictness.
- Priority60 adjudication covers high-priority disagreements, but is not final gold.
- Guard-only is instrumentation, not rewrite.
- DBox+Repair is only a 20-case targeted sensitivity add-on.
- The DeepSeek priority60 LLM grader has weak critical recall and cannot replace human review.

Acceptance criteria:

- These limitations are reported as explicit methodological boundaries, not as small-print caveats.

### P0.4 Final Claim-Gate Check

Before submission, run:

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_final.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
rg -n -e "final gold" -e "Guard fixes final output" -e "Guard repairs" -e "significantly outperforms all baselines" -e "all 50 cases headline" -e "stable\\s+advantage" docs evals
```

If `rg` hits historical reports or forbidden-wording lists, manually check whether the hit is a negative example rather than a positive paper claim.

## 4. P1: Complete During Manuscript Drafting

1. Write the Introduction around turn-level missing bridge and critical bridge leakage in CP tutoring, not as an online product-system paper.
2. Write Related Work against no-direct-answer prompting, Socratic tutoring, LLM-as-judge, agent evaluation, and programming-help benchmarks.
3. Prepare the Figure / Table list:
   - Figure 1: student turn -> case-specific rubric -> tutor response -> human review / guard / repair evidence.
   - Table 1: benchmark slices and case counts.
   - Table 2: conditions and interpretation boundaries.
   - Table 3: main scaffold results.
   - Table 4: paired W/T/L and uncertainty.
   - Table 5: repair stress and DBox+Repair sensitivity.
4. Organize the Appendix:
   - human review reliability;
   - observed error taxonomy;
   - full sensitivity tables;
   - repair same-candidate protocol;
   - DBox+Repair fairness add-on;
   - DeepSeek LLM grader calibration;
   - evidence manifest and reproduction commands.
5. Decide whether to clean up legacy bilingual-doc validator debt. It does not block the main evidence, but if the submission artifact needs to be fully clean, either backfill the historical doc pairs or keep an explicit README exemption.

## 5. Explicit Non-Goals

Do not do the following in the current phase:

- do not add new main experiment conditions;
- do not connect online active mode;
- do not modify prompts;
- do not alter main experiment raw data;
- do not edit held-out cases retroactively;
- do not use the LLM grader to replace human labels;
- do not upgrade the 20-case DBox+Repair add-on into a main experiment result.

## 6. Recommended Execution Order

1. Write the Methods / Evaluation manuscript draft first.
2. Compress the existing `paper_results_discussion_section` into submission-length Results.
3. Write Discussion / Limitations and lock the claim gate.
4. Prepare figures and tables.
5. Write Abstract / Introduction last, because those sections are the easiest places to overclaim and should wait until the result boundaries are fixed.

One-line version:

```text
The next step is not to expand experiments, but to turn the existing dialogue-state v3 evidence package into a reproducible, bounded, paper-ready manuscript draft.
```
