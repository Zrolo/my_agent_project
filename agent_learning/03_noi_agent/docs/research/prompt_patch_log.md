# Prompt Patch Log

This log records slow-variable changes to prompts, rubrics, registries, routers, or repair policy. Each patch should be tied to failure evidence and regression checks.

## Governance Rules

- Prompt changes are slow-variable updates. They should not happen automatically during a student conversation.
- Student-facing tutor prompts are tracked here. Judge and grader prompts are tracked separately in `judge_prompt_patch_log.md`.
- Prompt tuning should happen on dev/regression cases, not on held-out test cases used for headline results.
- A prompt patch requires failure evidence, regression checks, and human approval before it is treated as a frozen research version.
- When possible, patch one layer at a time: tutor prompt, repair prompt, rubric, registry, router, or fallback policy.

## Freeze Targets

Status labels:

- `freeze-candidate`: can enter held-out only after project-owner approval and version stamping.
- `snapshot-required`: must be captured exactly as the deployment baseline before held-out.
- `guarded-only`: should not be used as a standalone safety headline.
- `appendix-only`: useful for stress/fallback analysis, not main quality claims.
- `blocked`: should not enter held-out until the listed blocker is resolved.

| Prompt family | Current freeze target | Freeze readiness status | Held-out role |
|---|---|---|---|
| Main Tutor / current AIChat prompt | `current_system_snapshot_20260512` | `snapshot-required` | deployment baseline only; do not tune during held-out |
| Enhanced Prompt-Only Tutor prompt | `enhanced_prompt_only_v1.0-dev` | `freeze-candidate` | strong prompt-only main baseline |
| Bridge Contract Tutor prompt | `bridge_contract_tutor_prompt_v1.0-dev` | `guarded-only` | main comparison only with Guard / Guard+Repair; standalone Bridge Contract stays appendix/dev |
| Repair Generator prompt | `repair_prompt_v1.0-dev` | `freeze-candidate` with regression caveat | main or appendix condition; must report repair_still_leaks and quality delta |
| Deterministic fallback policy text | `fallback_policy_v1.0-dev` | `appendix-only` | high-risk fallback / stress analysis, not main quality evidence |

## patch_20260511_enhanced_prompt_only_runner

- Date: 2026-05-11
- Affected layer: offline strong prompt-only tutor baseline
- Failure/risk pattern:
  - External review identified a mismatch between the baseline protocol and the shared offline runner: `enhanced_prompt_only` was a key strong prompt-only baseline in the research design, but it was not available in `run_bridge_offline_eval.py`.
  - Without this mode in the same runner, Research v1 could not cleanly separate prompt wording effects from predicted missing-bridge diagnosis effects.
- Change:
  - Added `enhanced_prompt_only` to the shared offline runner and CLI `--tutor-mode` choices.
  - Allowed `enhanced_prompt_only` with `--pipeline-mode tutor_only_no_diagnosis` so it can run as a standalone response/latency baseline without Bridge Judge or candidate retrieval.
  - Added a strong tutoring control prompt that gives Socratic, single-focus, bridge-oriented micro-example guidance without a concrete Bridge Contract.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_enhanced_prompt_only_runs_without_bridge_diagnosis`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_cli_accepts_enhanced_prompt_only_tutor_mode`
- Verification:
  - `python3 -m unittest test_bridge_offline_eval_runner_unit.py` passed on 2026-05-11.
- Human approval:
  - Pending project-owner review before prompt freeze.

## patch_20260511_bridge_first_topic_second

- Date: 2026-05-11
- Affected layer: offline tutor prompts / Bridge Contract control message
- Failure/risk pattern:
  - Recent DBox/Socratic/Bridge-inspired smoke tests showed that prompt examples around tree path difference, DP state, and binary-search check can become over-specific regression hints.
  - The project owner raised the broader concern that algorithm-specific prompt coverage can never be exhaustive and may overfit to algorithms already listed in the prompt.
- Change:
  - `single_llm_structured` now explicitly follows `bridge-first, topic-second, focus-top-k`.
  - The Bridge Contract control message now says to control teaching actions by `missing_bridge.family`, while concrete algorithm names only help choose context and example language.
  - Concrete examples such as DP/check/LCA are documented as regression boundaries, not as an exhaustive algorithm prompt list.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_single_llm_structured_prompt_is_bridge_first_topic_second`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_message_is_bridge_first_not_algorithm_specific`
- Verification:
  - `test_bridge_offline_eval_runner_unit.py` passed after the prompt assertions were added.
  - 3-case `single_llm_structured` smoke emitted valid rows with `stage_errors={}`.
  - The smoke still showed over-complete micro-examples on `cp_bridge_001` and `cp_bridge_002`; therefore this patch is a design-principle cleanup, not evidence that prompt-only control is sufficient.
- Human approval:
  - Pending project-owner review before prompt freeze.

## patch_20260511_bridge_contract_current_substep

- Date: 2026-05-11
- Affected layer: Bridge Contract Tutor control message
- Failure/risk pattern:
  - Dev ablation blind review showed `bridge_contract` had the highest response quality, but all 10 outputs had minor or major bridge leakage.
  - Failure notes repeatedly pointed to fully worked micro-examples: the tutor organized good examples but completed the current bridge for the student.
  - Project-owner review requested borrowing DBox's decomposition discipline without claiming to use DBox's step-tree interface.
- Change:
  - Added a single-turn decomposition constraint to `_bridge_contract_message()`.
  - The Bridge Contract Tutor must internally identify one `current_substep`, keep the visible response focused on that current minimal substep, and provide only first-level hints.
  - The prompt explicitly avoids claiming or displaying a full decomposition tree; this remains a single-turn Bridge Contract control message, not a DBox reproduction.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_message_uses_current_substep_without_step_tree_claim`
- Verification:
  - `python3 -m unittest test_bridge_offline_eval_runner_unit.py test_leakage_judge_v1_unit.py test_repair_response_v1_unit.py` passed on 2026-05-11.
- Human approval:
  - Pending project-owner review before prompt freeze.

## patch_20260511_generation_prompt_abstract_bridge_shapes

- Date: 2026-05-11
- Affected layer: offline tutor generation prompts
- Failure/risk pattern:
  - Project-owner review identified that prompt rules should not rely on concrete algorithm coverage.
  - Several generation prompts still used concrete algorithm examples or answer-bearing slots such as specific path nodes, concrete predicate terms, or named algorithm examples.
  - This could make the system look stronger on covered algorithms while weaker or less stable on uncovered algorithms.
- Change:
  - Rewrote enhanced prompt, single-LLM structured prompt, DBox-inspired baseline prompt, CodeHelp/CodeAid-style prompt, Socratic/no-answer prompt, and Bridge-inspired prompt constraints toward abstract bridge shapes.
  - Replaced concrete algorithm examples with categories such as representation meaning, relation/formula, predicate condition, dependency/update direction, contribution/aggregation rule, and local code slot.
  - Kept algorithm topic enums for structured diagnosis, but clarified that concrete algorithm names are context signals rather than generation templates.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_generation_control_prompts_use_abstract_bridge_shapes_not_algorithm_examples`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_literature_baseline_prompts_do_not_encode_specific_answer_bearing_slots`
- Verification:
  - `python3 -m unittest test_bridge_offline_eval_runner_unit.py test_leakage_judge_v1_unit.py test_repair_response_v1_unit.py` passed on 2026-05-11.
  - `rg` check found no remaining high-risk concrete phrases in the patched runner/Leakage/Repair prompts.
- Human approval:
  - Pending project-owner review before prompt freeze.

## patch_20260512_bridge_contract_clean_offline_prompt

- Date: 2026-05-12
- Affected layer: offline Bridge Contract Tutor generation path
- Failure/risk pattern:
  - After prompt abstraction, a `bridge_contract` smoke on `cp_bridge_001` produced an unrelated trie response even though Bridge Judge correctly diagnosed `aggregation_contribution_bridge`.
  - Inspection showed that `bridge_contract` still called the online `noi_agent_chat()` path and inherited the large production AIChat system prompt, including unrelated product fallback examples.
  - This made the research ablation less clean: `bridge_contract` was partly measuring the online AIChat prompt instead of a clean offline Bridge Contract Tutor.
- Change:
  - Added a clean `Offline Bridge Contract Tutor` system prompt.
  - Changed `_call_bridge_contract_tutor()` to call `_chat_completion_create()` directly instead of `noi_agent_chat()`.
  - Kept the online `current_system` baseline unchanged.
  - Added stronger answer-bearing micro-example constraints: no candidate answer marks/formulas/boundary actions/code lines, no binary choices over forbidden signs/directions/locations, and contribution/aggregation examples must start from affected objects and expected aggregate results rather than artificial marks.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_tutor_uses_clean_offline_prompt_not_online_chat`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_tutor_uses_bridge_result_in_clean_system_prompt`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_tutor_system_prompt_forbids_answer_bearing_micro_example_slots`
- Verification:
  - `python3 -m unittest test_bridge_offline_eval_runner_unit.py test_leakage_judge_v1_unit.py test_repair_response_v1_unit.py` passed on 2026-05-12.
  - `bridge_contract` 1-case rerun on `cp_bridge_001` no longer produced unrelated trie content.
- Empirical caveat:
  - Even after the clean prompt and stronger constraints, repeated `cp_bridge_001` tutor-only reruns still produced answer-bearing contribution/marking examples.
  - This is dev evidence that prompt-only Bridge Contract control is insufficient for high-risk aggregation/contribution bridges; Guard/Repair or stricter route policy remains necessary.
- Human approval:
  - Pending project-owner review before prompt freeze.

## patch_20260512_deterministic_safe_scaffold_offline_route

- Date: 2026-05-12
- Affected layer: offline route / fallback policy
- Failure/risk pattern:
  - Repeated `cp_bridge_001` tutor-only reruns showed that even a clean Bridge Contract prompt can still produce answer-bearing contribution/aggregation micro-examples.
  - Continuing to add algorithm-specific prompt rules would inflate prompts and overfit dev cases.
- Change:
  - Added offline-only `pipeline_mode=deterministic_safe_scaffold`.
  - This mode runs Bridge Judge, then skips Tutor / Leakage Judge / Repair and returns a deterministic L1 safe scaffold.
  - For `aggregation_contribution_bridge`, the scaffold asks the student to list true affected objects and expected final counts, without mentioning auxiliary marks, signs, exact locations, formulas, or code.
  - The mode is not included in the default dev ablation suite and does not affect online AIChat.
  - Added `--include-safe-scaffold` to `run_dev_ablation_suite.py` so this condition can be appended explicitly as `bridge_contract_safe_scaffold` for appendix / stress comparisons.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_deterministic_safe_scaffold_pipeline_skips_tutor_and_uses_safe_fallback`
  - `test_dev_ablation_suite_unit.py::DevAblationSuiteTests.test_include_safe_scaffold_adds_appendix_condition_without_changing_defaults`
- Verification:
  - `python3 -m unittest test_bridge_offline_eval_runner_unit.py test_leakage_judge_v1_unit.py test_repair_response_v1_unit.py` passed on 2026-05-12.
  - 1-case smoke on `cp_bridge_001` with `pipeline_mode=deterministic_safe_scaffold` completed with `error_count=0`, `llm_call_count=1`, and `final_response_source=safe_fallback`.
  - `run_dev_ablation_suite --include-safe-scaffold --limit 1` completed with 12 conditions; the review key includes `bridge_contract_safe_scaffold` with `final_response_source=safe_fallback`.
- Human approval:
  - Pending project-owner review before any main-table inclusion.

## patch_20260512_definition_first_and_followup_action_leak_control

- Date: 2026-05-12
- Affected layer: offline Bridge Contract Tutor prompt / DBox-inspired baseline prompt
- Failure/risk pattern:
  - The 10-case dev ablation blind review found 8 major bridge leakage rows.
  - The recurring failure was not answer/code leakage. It was answer-bearing tutoring prose: opening definition sentences, fully worked micro-examples, canonical templates, and follow-up questions that asked for the next boundary/action after the response had already supplied the key local judgment.
  - Examples included lazy-tag semantics being defined in the first sentence, rolling-array order being fully worked out, exact contribution markings being shown, and classic state templates being copied into the response.
- Change:
  - Added a Bridge Contract constraint: do not use an opening definition sentence to name or explain the current missing bridge; give an observation task first.
  - Added a Bridge Contract constraint: do not both judge a local result and ask for the next action/boundary/location in the same turn.
  - Added DBox-inspired constraints: do not copy canonical templates or standard definitions, do not define first and then ask, and do not write `current_substep` as an answer sentence.
  - Kept the patch abstract by bridge/leakage shape; no algorithm-specific recipe list was added.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_prompt_blocks_definition_first_and_followup_action_leaks`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_dbox_prompt_blocks_canonical_template_and_definition_leaks`
- Verification:
  - `.venv/bin/python test_bridge_offline_eval_runner_unit.py test_leakage_judge_v1_unit.py test_repair_response_v1_unit.py` passed on 2026-05-12.
- Empirical caveat:
  - This is a prompt/rubric regression patch based on dev data. It does not replace the need for 50-case held-out evaluation after prompt freeze.
- Human approval:
  - Pending project-owner review before prompt freeze.

## patch_20260512_repair_answer_slot_leak_control

- Date: 2026-05-12
- Affected layer: repair prompt
- Failure/risk pattern:
  - A targeted 2-case rerun after answer-slot leakage judge calibration produced no stage errors, but both `cp_bridge_001` and `cp_bridge_005` were rewritten into new answer-bearing slot questions.
  - The repair removed fully worked content, but still asked the student to fill critical locations/actions or the exact missing semantic phrase, which can preserve the same critical bridge leakage in a subtler form.
- Change:
  - Added a repair-level rule that leaked content must not be rewritten as answer slots such as key position, key direction, key action, true/false follow-up action, or "还没____" semantic blanks when those slots are the current missing bridge.
  - Added an upstream repair action: ask for affected objects, observable facts, candidate meaning, target outcome, or visible differences instead of asking for the forbidden completion itself.
  - Added a rule that repair must not copy filled critical tables, key field values, marker values, truth conclusions, update results, or local traces from the original candidate. If a table remains useful, it must be changed into a blank table or object/observation list.
  - Kept the patch abstract by leakage shape; no algorithm-specific repair recipe was added.
- Regression checks:
  - `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_does_not_turn_leaks_into_answer_slot_questions`
  - `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_removes_filled_critical_tables_from_candidate`
- Verification:
  - `.venv/bin/python -m unittest test_repair_response_v1_unit.py` passed on 2026-05-12.
- Empirical caveat:
  - This patch addresses the repair prompt contract. A second leakage check after repair is still needed before claiming repair success in formal results.
- Human approval:
  - Pending project-owner review before prompt freeze.

## patch_20260512_short_constructed_response_policy

- Date: 2026-05-12
- Affected layer: offline tutor prompts / response review rubric / review workbook guide
- Failure/risk pattern:
  - Project-owner discussion identified that default A/B or multiple-choice prompts can let students guess rather than construct a bridge relation.
  - Education literature review suggested using very short constructed responses as the default, while reserving multiple-choice for low-risk fallback or comparison questions.
  - Existing prompts and review guides still described low burden as "1-2 words, one option, or one short sentence", which could nudge generators and reviewers toward choice-question scaffolds.
- Change:
  - Updated Enhanced Prompt-Only, Single-LLM Structured, Bridge Contract Tutor, and DBox-inspired prompts to prefer short constructed responses: one or two keywords, a local judgment, or one short sentence.
  - Added a stronger multiple-choice constraint: use choices sparingly; if choices are used, the options must not carry the critical bridge answer and should generally be a fallback after the student is stuck.
  - Updated the minimal sufficient student effort policy and response-review rubric to separate low typing burden from low thinking value.
  - Updated the Chinese review workbook guide and dropdown wording for `coach_student_response_burden`.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_generation_prompts_assume_students_will_reply_briefly`
  - `test_coach_response_review_xlsx_unit.py::CoachResponseReviewXlsxTests.test_export_xlsx_uses_chinese_headers_and_dropdown_options`
- Verification:
  - `.venv/bin/python -m unittest test_bridge_offline_eval_runner_unit.py test_coach_response_review_xlsx_unit.py test_coach_response_review_workbook_unit.py test_response_burden_analysis_unit.py` passed on 2026-05-12.
  - 3-condition / 3-case smoke completed with `error_count=0`, but static lint still found answer-slot or filled-trace risk in all three conditions. See `short_constructed_response_smoke_20260512.zh.md`.
- Empirical caveat:
  - This patch should be treated as an interaction-design cleanup, not as a leakage-control fix.
  - The smoke suggests prompt wording alone does not reliably prevent answer-slot leakage; Guard/Repair/static lint and coach review remain necessary.
- Human approval:
  - Project owner approved the short-constructed-response direction in discussion; pending prompt freeze before held-out evaluation.

## patch_20260512_answer_slot_short_response_guard

- Date: 2026-05-12
- Affected layer: offline tutor prompts
- Failure/risk pattern:
  - A 3-condition smoke after the short-constructed-response patch showed that models still converted the current missing bridge into short answer slots.
  - Examples included asking what `check` should return, where an operation should happen, what values nodes should get, or what a state cell should record.
  - These are not necessarily A/B choices, but they can still be critical-bridge leakage because the question asks the student to fill the exact missing bridge itself.
- Change:
  - Added an abstract answer-slot guard to Enhanced Prompt-Only, Single-LLM Structured, Bridge Contract, and DBox-inspired prompts.
  - The prompts now explicitly say not to rewrite the current `missing bridge` as a short-answer slot such as "应该返回什么", "应该在哪里", "分别写什么值", or "这个格子应该记录什么".
  - The Bridge Contract micro-example policy now says to complete only a local observation in this turn and defer full transferable-rule abstraction to a later turn.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_generation_prompts_assume_students_will_reply_briefly`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_tutor_uses_clean_offline_prompt_not_online_chat`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_tutor_system_prompt_forbids_answer_bearing_micro_example_slots`
- Verification:
  - Targeted prompt tests passed on 2026-05-12.
  - Full research unit suite passed on 2026-05-12: 113 tests.
- Empirical caveat:
  - After rerunning the same 3-condition / 3-case smoke, static lint still found answer-slot or filled-trace risk. The result reinforces that prompt-only control is not sufficient for this failure mode.
- Human approval:
  - Pending project-owner review before prompt freeze.

## patch_20260513_scaffold_sufficiency_review_dimension

- Date: 2026-05-13
- Affected layer: response review rubric / review workbook guide / AI preliminary reviewer
- Failure/risk pattern:
  - Project-owner discussion identified that an overly strict leakage framing could reward replies that are safe but not educationally useful.
  - Existing review workbooks had scaffold appropriateness, leakage control, next-step clarity, and student response burden, but no explicit field for under-help / over-withholding.
- Change:
  - Added `coach_scaffold_sufficiency_score` to response-review CSV/XLSX exports.
  - Added Chinese dropdown guidance: `2=信息足够推进，既不泄露也不空泛`; `1=略保守或略空泛，但学生仍能继续`; `0=过度保留，安全但没帮助，或只让学生再想想`.
  - Updated the AI preliminary reviewer to fill the new field for dev triage.
  - Updated bilingual blind-review rubrics and external coach instructions to state that critical-bridge leakage control must be balanced with sufficient scaffolding.
- Regression checks:
  - `test_coach_response_review_workbook_unit.py::CoachResponseReviewWorkbookTests.test_write_review_csv_has_rubric_columns`
  - `test_coach_response_review_xlsx_unit.py::CoachResponseReviewXlsxTests.test_export_xlsx_uses_chinese_headers_and_dropdown_options`
  - `test_auto_fill_response_review_unit.py::AutoFillResponseReviewTests.test_auto_fill_marks_rows_as_ai_prelim_and_preserves_response_text`
- Verification:
  - `python3 -m unittest test_coach_response_review_workbook_unit.py test_coach_response_review_xlsx_unit.py test_auto_fill_response_review_unit.py test_dev_ablation_review_analysis_unit.py` passed on 2026-05-13.
  - `python3 evals/aichat/validate_research_bilingual_docs.py` passed new-doc policy on 2026-05-13 (`unpaired_count=0`; legacy unpaired docs unchanged).
  - `git diff --check` passed for modified review/rubric files on 2026-05-13.
- Empirical caveat:
  - This is an evaluation-rubric correction, not a claim that generation prompts should be loosened before the held-out test. Future reports should inspect leakage and scaffold sufficiency together.
- Human approval:
  - Project owner requested the change in discussion; pending final freeze before held-out evaluation.

## patch_20260510_repair_micro_task_guard

- Date: 2026-05-10
- Affected layer: repair prompt / repair user-message contract
- Failure cases: `cp_bridge_010`
- Evidence:
  - `bridge_contract + guard` correctly identified an over-strong 0/1 knapsack micro-example as `safe_action=block`.
  - A later repair run could still solve the replacement micro-task by explaining the same bridge through another fully worked example.
- Change:
  - `docs/common/aichat_repair_response_v1_system_prompt.md` now states that when the repair instruction asks the student to construct, calculate, compare, or observe a replacement micro-example, the repair response must not solve that task for the student.
  - `noi_agent._build_repair_response_v1_user_message()` now repeats this as a per-call hard constraint.
- Regression checks:
  - `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_forbids_solving_replacement_micro_task`
  - `test_aichat_hard_gate_fallback_regression_unit.py`
- Verification:
  - 24 related unit tests passed on 2026-05-10.
- Human approval:
  - Pending project-owner review.

## patch_20260513_bridge_subtype_abstraction_pass2

- Date: 2026-05-13
- Affected layer: coach annotation schema / bridge subtype registry / seed-label workbook exports
- Failure/risk pattern:
  - Project-owner review noted that several active `bridge_subtype` labels still looked like concrete algorithm instances, such as DP state semantics, lazy tag semantics, binary-search boundary update, prefix-sum variants, heap operation mapping, DSU operation mapping, monotonic-stack mapping, and greedy exchange proof.
  - This could make coaches ask why nearby algorithms such as SPFA, Floyd, or other CP topics do not have equally specific labels, increasing taxonomy drift and annotation burden.
- Change:
  - Renamed active bridge subtypes into transferable reasoning shapes:
    - `state.dp_state_semantics` -> `state.table_or_memo_cell_semantics`
    - `state.lazy_tag_semantics` -> `state.deferred_update_semantics`
    - `predicate.check_truth_direction` -> `predicate.feasibility_truth_direction`
    - `predicate.binary_search_bound_update` -> `predicate.boundary_update_direction`
    - `aggregation.prefix_sum_1d` -> `aggregation.cumulative_range_query`
    - `aggregation.prefix_sum_2d` -> `aggregation.inclusion_exclusion_query`
    - `aggregation.difference_array_range_update` -> `aggregation.boundary_delta_update`
    - `ds.heap_push_pop_mapping` -> `ds.priority_candidate_operation_mapping`
    - `ds.union_find_operation_mapping` -> `ds.component_merge_query_mapping`
    - `ds.monotonic_stack_mapping` -> `ds.dominated_candidate_stack_mapping`
    - `correctness.greedy_exchange_argument` -> `correctness.local_choice_exchange_argument`
  - Kept old IDs in `bridge_subtype_registry_v2.json` as deprecated aliases with `replaced_by`, so old pilot artifacts remain interpretable.
  - Updated workbook dropdown source labels and current unit-test fixtures to use the abstract subtype IDs.
- Regression checks:
  - `test_bridge_subtype_registry_v2_unit.py`
  - `test_coach_seed_labeling_v2_workbook_unit.py`
  - `test_coach_workbook_v2_validation_unit.py`
  - `test_export_coach_v2_gold_jsonl_unit.py`
  - `test_check_heldout_50_readiness_unit.py`
  - `test_export_heldout_frozen_reference_unit.py`
  - `test_export_coach_adjudication_workbook_unit.py`
  - `test_bridge_offline_eval_runner_unit.py`
  - `test_dbox_inspired_decomposition_tutor_unit.py`
  - `test_bridge_judge_v1_unit.py`
- Verification:
  - `python3 -m unittest test_bridge_subtype_registry_v2_unit.py test_coach_seed_labeling_v2_workbook_unit.py test_coach_workbook_v2_validation_unit.py test_export_coach_v2_gold_jsonl_unit.py test_check_heldout_50_readiness_unit.py test_export_heldout_frozen_reference_unit.py test_export_coach_adjudication_workbook_unit.py test_bridge_offline_eval_runner_unit.py test_dbox_inspired_decomposition_tutor_unit.py test_bridge_judge_v1_unit.py` passed on 2026-05-13.
- Empirical caveat:
  - This is a taxonomy-abstraction cleanup before 50-case labeling, not an empirical result. Concrete algorithm context should remain in `algorithm_topic`, `registered_focus_id`, and notes.
- Human approval:
  - Project owner requested a more abstract bridge-subtype design before formal labeling.

## patch_20260514_remove_internal_level_tags_from_offline_research_outputs

- Date: 2026-05-14
- Affected layer: offline Bridge Contract Tutor prompt / Repair Generator prompt / repair stress runner
- Failure/risk pattern:
  - Human review and external critique found student-visible replies containing internal `[LEVEL:Lx]` tags.
  - The tags were useful for the historical online AIChat hard gate, but they are noisy and misleading in offline response-review workbooks.
  - Keeping the tag requirement inside research prompts also wastes model attention on an implementation detail instead of the actual tutoring move.
- Change:
  - Removed the Bridge Contract full/compact/minimal prompt requirement to append `[LEVEL:L1|L2|L3]`.
  - Updated the repair prompt so `repaired_response` explicitly must not contain `[LEVEL]`, JSON, judge, repair, report, or other internal control information.
  - Added stripping of internal level tags in the repair stress runner before `final_response_text` and `repair_result.repaired_response` are exported.
  - Kept existing online AIChat level-tag behavior untouched; this patch only changes offline research tooling and repair stress exports.
- Regression checks:
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_compact_prompt_keeps_core_controls_but_is_shorter`
  - `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_minimal_prompt_is_shorter_than_compact`
  - `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_does_not_request_internal_level_tags`
  - `test_repair_stress_eval_runner_unit.py::RepairStressEvalRunnerTests.test_run_one_case_repairs_and_second_checks_rewritten_response`
- Verification:
  - `python3 -m unittest test_bridge_offline_eval_runner_unit.py test_repair_response_v1_unit.py test_repair_stress_eval_runner_unit.py -v` passed on 2026-05-14.
- Empirical caveat:
  - This patch improves output hygiene and review reliability. It does not by itself prove Guard or Repair improves pedagogical quality.
- Chinese note:
  - 本次修改只去掉离线研究回复和 repair stress 导出中的内部 `[LEVEL]` 标签要求，不改变线上 AIChat 的历史等级闸门机制。目的是减少盲评表里的内部字段污染，让教练评审真正聚焦学生可见回复质量。
