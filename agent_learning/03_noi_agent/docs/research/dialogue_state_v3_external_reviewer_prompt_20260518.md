# Dialogue-State v3 External Reviewer Prompt 20260518

The block below can be copied directly to another AI or reviewer. Its goal is to make the reviewer start from the real GitHub files and audit the current CP-MissingBridgeBench dialogue-state v3 evidence package, rather than relying on chat summaries.

```text
You are now acting as an external methods reviewer, statistical auditor, and paper-interpretation reviewer for the CP-MissingBridgeBench project.

Do not judge only from this description. First open the GitHub project:

Repository: https://github.com/Zrolo/my_agent_project
Branch: codex/bridge-research-annotation
Project path: agent_learning/03_noi_agent
Review entrypoint: use the current branch tip
Fixed evidence-package base checkpoint: 33a5dd7 Add dialogue-state v3 evidence package gates

Your task is not to add experiments, modify the online system, edit prompts, or rerun active mode. The current goal is to audit whether the dialogue-state v3 evidence package is submission-ready, traceable, and not over-interpreted.

Read these files first:

1. docs/research/dialogue_state_v3_external_review_handoff_20260518.md
2. docs/research/index.md
3. docs/research/dialogue_state_v3_evidence_manifest_20260518.json
4. docs/research/dialogue_state_v3_paper_claims_final_gate_20260518.md
5. docs/research/project_status_after_taxonomy_revision_20260517.md
6. docs/research/evaluation_protocol_v3.md
7. docs/research/response_review_rubric_v3.md
8. docs/research/dialogue_state_v3_main_paper_ready_tables_20260517.md
9. docs/research/dialogue_state_v3_pairwise_win_tie_loss_20260517.md
10. docs/research/human_review_reliability_section_draft_20260517.md
11. docs/research/paper_results_discussion_manuscript_dialogue_state_v3_20260518.md
12. docs/research/repair_same_candidate_stress_result_20260517.md
13. docs/research/dbox_guard_repair_fairness_report_20260517.md
14. docs/research/llm_grader_calibration_deepseek_sensitivity_report_20260518.md

If you can run code, run these commands from agent_learning/03_noi_agent:

python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
python3 -m json.tool docs/research/dialogue_state_v3_evidence_manifest_20260518.json >/tmp/dialogue_state_v3_evidence_manifest_check.json

Focus on these questions:

1. Is the evidence manifest sufficient to trace paper claims to report / input / script / output / checksum?
2. Does the main headline use only the main_scaffold_eval slice, rather than pooling all 50 cases into one mean?
3. Do the current results support only trade-off / trend / stable advantage wording, rather than absolute winner / significant dominance wording?
4. Is Guard-only correctly described as guard-instrumented / runtime signal, not as a rewrite / repair condition?
5. Is Repair causality supported only by same-candidate before/after stress, not by main-condition means alone?
6. Is DBox+Repair described only as targeted fairness sensitivity, not as a full main experimental condition?
7. Is the DeepSeek LLM grader described only as an auxiliary grader, not as a replacement for human coaches?
8. Is the taxonomy stably framed as cognitive bridge family + leakage mechanism + surface anchor, avoiding the impression that it is tuned only to DP/check/lazy/tree/local-code cases?
9. Are Coach A / Coach B / priority60 adjudication correctly described as human-review evidence candidates, not final gold?
10. What are the three most likely strict-reviewer attacks on the Results / Discussion draft?

Please output:

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

Recommended minimal fixes:
- ...

Pay special attention to these forbidden claims:

- Do not say Bridge Contract significantly outperforms all baselines.
- Do not say Guard-only fixes the final output.
- Do not say Repair causality is proven by main-condition means.
- Do not say Coach A, Coach B, or priority60 adjudicated labels are final gold.
- Do not say the all-50 aggregate is the headline.
- Do not say DBox+Repair has completed full 50-case double-coach validation.
- Do not say the LLM grader can replace human coaches.

The safest current paper interpretation is:

CP-MissingBridgeBench reveals quality-safety-burden trade-offs in turn-level CP tutoring.
DBox-inspired decomposition is a strong baseline.
Bridge Contract compact + Guard/Repair shows stable overall and critical-leakage-control advantages, but paired uncertainty supports trend/trade-off wording rather than broad significant dominance.
Guard-only is instrumentation, not final-response rewrite.
Repair has same-candidate causal evidence for leakage reduction, with student-burden trade-off.
DBox+Repair is targeted fairness sensitivity, not a full main condition.
Human review and adjudication remain necessary; LLM graders are auxiliary only.
```
