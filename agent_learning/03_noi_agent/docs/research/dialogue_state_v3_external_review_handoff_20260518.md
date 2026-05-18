# Dialogue-State v3 External Review Handoff 20260518

This document is the entry point for an external AI or human reviewer. It adds no experiments, changes no online system, and does not alter main-experiment data. Its goal is to let a reviewer independently check whether the dialogue-state v3 evidence package is reproducible, submission-ready, and not over-interpreted.

## Review Target

- Repository: `https://github.com/Zrolo/my_agent_project`
- Branch: `codex/bridge-research-annotation`
- Primary review target: `33a5dd7 Add dialogue-state v3 evidence package gates`
- Branch-tip policy: if the branch tip is newer than `33a5dd7`, first audit the fixed evidence package, then separately note whether later commits change evidence files, scripts, or paper wording.
- Project path inside repo: `agent_learning/03_noi_agent`
- Working paper title:

```text
CP-MissingBridgeBench:
Turn-level Missing-Bridge Diagnosis and Critical-Bridge Leakage Evaluation
for LLM Tutors in Competitive Programming
```

The current status is `formal human-review evidence candidate`, not `final gold`. The main headline must use only the `main_scaffold_eval` slice; do not pool all 50 cases into one headline mean.

Checkpoint interpretation:

- `dbbbd5c` is the evidence-content base recorded in some machine-readable manifest metadata.
- `33a5dd7` is the fixed evidence-package gates checkpoint for this external audit; it includes the manifest, claim gate, verify / reproduce scripts, and extension plan.
- Branch-tip commits after `33a5dd7` mainly update reviewer-facing handoff / prompt wording. If a reviewer uses a newer branch tip, first audit the `33a5dd7` evidence package, then separately note whether later commits change evidence files, scripts, or paper wording.

## Reviewer Non-Goals

Please do not:

- Add new experimental conditions.
- Change online AIChat or active mode.
- Modify prompts, main-experiment data, or held-out data.
- Call Coach A, Coach B, or the priority60 adjudicated merge gold.
- Describe Guard-only as a rewrite / repair condition.
- Describe the 20-case DBox+Repair add-on as a full main experiment.
- Replace human coaches with the LLM grader.
- Propose new modules unless explicitly labeled as future work; this task is evidence validation, not system expansion.
- Treat sensitivity analyses, stress tests, or calibration runs as main results.

## Recommended Reading Order

### 1. Main Entry And Claim Gate

Read first:

- `docs/research/index.md`
- `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`
- `docs/research/dialogue_state_v3_paper_claims_final_gate_20260518.md`
- `docs/research/project_status_after_taxonomy_revision_20260517.md`

Goal: confirm current project state, evidence manifest, and allowed / forbidden paper wording.

### 2. Evaluation Protocol And Taxonomy

Then read:

- `docs/research/evaluation_protocol_v3.md`
- `docs/research/response_review_rubric_v3.md`
- `docs/research/baseline_protocol_v1.md`
- `docs/research/dialogue_state_v3_observed_error_taxonomy_20260517.md`
- `docs/research/taxonomy_specificity_revision_summary_20260517.md`

Check that the taxonomy is framed as:

```text
cognitive bridge family + leakage mechanism + surface anchor
```

Bridge buckets are operational cognitive bridge families. DP state, binary-search check, lazy propagation, tree difference, and local code are surface anchors, not the taxonomy itself.

### 3. Main Results And Interpretation Boundary

Focus on:

- `docs/research/dialogue_state_v3_main_paper_ready_tables_20260517.md`
- `docs/research/dialogue_state_v3_pairwise_win_tie_loss_20260517.md`
- `docs/research/human_review_reliability_section_draft_20260517.md`
- `docs/research/paper_results_discussion_manuscript_dialogue_state_v3_20260518.md`
- `docs/research/paper_results_discussion_section_dialogue_state_v3_20260518.md`

Check:

- The main scaffold headline uses only the 31-case `main_scaffold_eval` slice.
- Paired uncertainty prevents strong claims of significant comprehensive dominance.
- Coach A/B disagreement is reported directly rather than hidden.

### 4. Guard / Repair / DBox Fairness / LLM Grader

Focus on:

- `docs/research/paper_results_interpretation_guardrails_20260517.md`
- `docs/research/repair_same_candidate_stress_result_20260517.md`
- `docs/research/dbox_guard_repair_fairness_report_20260517.md`
- `docs/research/dbox_repair_fairness_extension_plan_20260518.md`
- `docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.md`

Must check:

- Guard-only is interpreted only as guard-instrumented / runtime signal.
- Repair causal evidence comes only from same-candidate stress.
- DBox+Repair is only targeted fairness sensitivity.
- DeepSeek LLM grader is only an auxiliary grader.

### 5. Implementation And Machine-Readable Evidence

Review scripts:

- `evals/aichat/reproduce_dialogue_state_v3_tables.py`
- `evals/aichat/verify_dialogue_state_v3_reports.py`
- `evals/aichat/run_bridge_offline_eval.py`
- `evals/aichat/prepare_llm_grader_calibration_pack.py`
- `evals/aichat/run_llm_grader_calibration.py`
- `evals/aichat/summarize_llm_grader_calibration.py`
- `evals/aichat/summarize_repair_same_candidate_stress.py`

Machine-readable evidence entry points:

- `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/`
- `evals/aichat/ad_hoc_runs/dialogue_state_v3_repair_fairness_addon_20260516/human_review/`
- `docs/research/llm_grader_calibration_*deepseek_20260518.*`

## Suggested Reproduction Commands

Run from `agent_learning/03_noi_agent`:

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 -m json.tool docs/research/dialogue_state_v3_evidence_manifest_20260518.json >/tmp/dialogue_state_v3_evidence_manifest_check.json
```

If scripts run successfully, report the command, exit status, key output files, whether reproduced numbers match reports, and any mismatched claim IDs. If scripts fail, report the exact failure stage and whether the failure blocks evidence review.

Optional bilingual check:

```bash
python3 -m evals.aichat.validate_research_bilingual_docs --output-json /tmp/dialogue_state_v3_bilingual_check.json
```

Known limitation: the bilingual check currently fails because four historical `20260516 integrity` documents lack Chinese companions and 23 legacy documents are unpaired. Focus on whether this handoff and the 20260518 Markdown additions are paired.

## Reviewer Questions

Please answer clearly:

1. Is the evidence manifest sufficient to trace each claim to report / input / script / output / checksum?
2. Does `verify_dialogue_state_v3_reports.py` cover the core paper numbers? Which additional numbers should be gated?
3. Do the main results support “trade-off / favorable trend in overall and critical-leakage control” rather than “absolute winner”?
4. Is there still a risk that Guard-only is misdescribed as rewrite?
5. Is the same-candidate Repair stress test sufficient for causal Repair wording? Which wording remains too strong?
6. Is the 20-case DBox+Repair add-on sufficient as fairness sensitivity? If not, choose Option A, B, or C.
7. Is DeepSeek LLM grader calibration correctly written as auxiliary, not replacement?
8. Does the taxonomy still risk looking algorithm-specific to a strict reviewer?
9. What are the three most likely strict-reviewer attacks on the current Results / Discussion draft?
10. What are the lowest-cost fixes?

## Reviewer Output Format

Suggested output:

```text
Verdict:
- ready / needs minor revision / needs major revision

Blocking issues:
- ...

Non-blocking issues:
- ...

Overclaim risks:
- ...

Evidence-chain risks:
- ...

Claim-by-claim audit table:

| Claim | Supported? yes/partial/no | Evidence files/scripts | Main/sensitivity/stress/calibration | Risk | Safer wording |
| --- | --- | --- | --- | --- | --- |

Recommended minimal fixes:
- ...
```

## Current Safe Interpretation

The safest current interpretation is:

```text
CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
DBox-inspired decomposition is a strong baseline.
Bridge Contract compact + Guard/Repair shows favorable overall and critical-leakage-control trends under the primary human-review view, but most paired CIs support trend/trade-off wording rather than significant dominance.
Guard-only is instrumentation, not final-response rewrite.
Repair has same-candidate causal evidence for leakage reduction, with student-burden trade-off.
DBox+Repair is targeted fairness sensitivity, not a full main condition.
Human review and adjudication remain necessary; LLM graders are auxiliary only.
```
