# Claims And Evidence Matrix v1

This matrix constrains paper-facing claims. Every claim must map to evidence. Claims without enough evidence should be written only as pilot observations, hypotheses, or future work.

## Status Legend

| Status | Meaning |
|---|---|
| `supported_pilot` | Supported by pilot or smoke evidence, but not enough for a final paper conclusion |
| `needs_main_experiment` | Needs the 50-case held-out set or a more complete main experiment |
| `needs_judge_validation` | Needs grader calibration against coach reference labels |
| `needs_repair_stress` | Needs a dedicated repair stress test |
| `needs_freeze` | Needs prompt / judge / rubric freeze before held-out evaluation |
| `future_work` | Should not be a main Research v1 conclusion |

## Claim Matrix

| Claim | Current Evidence | Gap | Next Evidence | Status |
|---|---|---|---|---|
| Missing bridge is a better construct than coarse algorithm labels for competitive-programming tutoring turns | Bridge schema, focus registry, 20-case pilot, coach workbook; a 50-case held-out draft exists and passes structural validation | Still needs Coach A review, Coach B double annotation, adjudication, and the frozen main experiment | Coach A reviews all 50 draft cases; Coach B labels 20; agreement + adjudication; frozen main experiment | `needs_main_experiment` |
| Critical bridge leakage captures an important risk beyond complete answer/code leakage | Mini-study and response review include examples where the model does not give full code but reveals the key bridge | Need stable leakage labels and grader calibration | Coach leakage labels; offline leakage grader precision/recall/F1; critical false-negative rate | `needs_judge_validation` |
| Current AIChat is a deployment baseline, not a full Bridge-aware tutor | `aichat_current_flow_v1.md` snapshots the online flow; v2 judge is mostly soft control | Must keep online active behavior separate from offline research modules | Implementation status matrix; scope lock; paper wording audit | `supported_pilot` |
| A strong single-LLM baseline must be included in the main experiment | The 20-case mini-study showed `single_llm_structured` is competitive | Need single-LLM + guard / repair variants | Include `single_llm_structured + guard` and `single_llm_structured + guard + repair` in the main matrix | `needs_main_experiment` |
| Using only `current_system` creates weak-baseline risk | External review and the 3-case prompt-controlled ablation show strong prompt wording may explain much of the quality gain | Need literature-inspired baselines and a formal 50-case held-out comparison | Add `enhanced_prompt_only`, `socratic_no_answer_tutor`, `codehelp_codeaid_no_direct_solution_tutor`, `dbox_inspired_decomposition_tutor`, `dbox_inspired_decomposition_tutor + guard`, and `bridge_inspired_expert_decision_tutor`; expand prompt-controlled ablation | `needs_main_experiment` |
| Bridge Contract may improve scaffold fit and controllability | Bridge Contract runner, contract schema, and pilot blind-review examples exist | It is not yet shown to beat prompt-tuned single-LLM baselines | Held-out comparison; response blind review; qualitative error analysis | `needs_main_experiment` |
| Leakage Guard can reduce critical bridge leakage | Leakage Judge and guard pipeline exist | Need to prove the guard is accurate and not relying on oracle forbidden content | Predicted-only guard; coach leakage labels; precision/recall/F1; false-positive rewrite rate | `needs_judge_validation` |
| Repair can reduce leakage while preserving some tutoring quality | Repair Generator and before/after tooling exist; 20-case repair stress coach blind review is complete: 20/20 pairs labeled, repaired response wins 14, ties 3, loses 3; leakage improves 19, ties 1; candidate major/answer leakage rate is 100%, repaired major/answer leakage rate is 5% | This is a high-leakage stress set and single-coach review, not natural 50-case held-out evidence; `repair_stress_004` still has major leakage; some repairs harm example correctness or instructional quality | Use `repair_stress_004` and low-quality repairs as regression cases; report natural trigger rate, repair quality delta, and repair_still_leaks_rate in the 50-case held-out run | `supported_pilot` |
| Risk-triggered routing can reduce latency/cost | Routing policy and control harness policy exist | Need simulation data | Full multi-judge vs risk-triggered simulation; p50/p95 latency; LLM calls; under/over-trigger rate | `future_work` |
| LLM Judge can support open-ended semantic evaluation | Agent-eval methodology document exists | Need formal calibration protocol and UNKNOWN handling | `llm_judge_calibration_protocol_v1`; judge validation report | `needs_judge_validation` |
| Prompt effects and architecture effects can be separated | Prompt patch log exists; 3-case prompt-controlled blind review shows `enhanced_prompt_only` is strong, while `bridge_contract_predicted` beats `bridge_contract_shuffled` | 3 cases are too few; need 10-20 case prompt-controlled ablation, dev/test split, and prompt freeze | Use 20 old seeds as dev/regression; expand prompt-controlled ablation; use 50 new seeds as held-out; keep prompt/judge patch logs | `needs_main_experiment` |
| Static lint / dev gate can stop high-risk conditions from entering headline tables automatically | Offline summary now includes `dev_gate`; answer-slot, filled-trace, worked-example, repair-still-leaks, critical leakage, or error rows trigger `review_required`; the short constructed-response smoke marks all three conditions as requiring review | Static lint is a high-recall review trigger, not coach gold | Use dev gate as a pre-50-case screening rule; report `automatic_headline_ready` and reasons per condition | `supported_pilot` |
| Research v1 documents should be bilingual | Bilingual documentation policy and validator now exist; among 129 research Markdown files, new docs have no unpaired violation and 23 historical unpaired docs are tracked as legacy debt | Legacy documents still need gradual backfill; validator currently allows a legacy allowlist | New docs must be paired as `.md` / `.zh.md`; backfill core legacy docs gradually | `supported_pilot` |
| The feedback-control harness helps organize the system | `control_harness_policy_v1.md` exists | It must not become the main innovation or cause concept creep | Keep it as system design principle and deployment simulation only | `supported_pilot` |

## Paper Wording Constraints

### Can Be Written As Results

A claim can enter Results / Conclusion only when:

- it has held-out test data;
- it uses coach reference labels or calibrated graders;
- tutor prompts and judge prompts are frozen;
- baselines are fair;
- metrics cover the relevant quality, leakage, and cost dimensions.

### Pilot Observation Only

Use pilot / preliminary language when a finding:

- uses only the 20 old seeds;
- was measured after prompt tuning without held-out re-evaluation;
- relies on a single coach's subjective judgment;
- lacks blind review;
- involves no actual repair trigger;
- uses oracle forbidden content.

### Future Work Only

Do not put these into main conclusions for Research v1:

- real online risk-triggered active mode;
- long-term learning gains;
- long-term student modeling;
- complete NOI/OI algorithm ontology;
- automatic prompt patching;
- full multi-judge every turn as the default online strategy.

## Most Urgent Evidence Gaps

1. Coach review and freeze of the 50-case held-out draft.
2. Partial double annotation and adjudication.
3. Strong prompt-only and literature-inspired baselines in the main comparison.
4. `single_llm_structured + guard / repair` baselines.
5. LLM Judge calibration report.
6. Prompt / judge prompt freeze logs.
7. Gradual bilingual backfill for the 23 legacy single-language research docs.
