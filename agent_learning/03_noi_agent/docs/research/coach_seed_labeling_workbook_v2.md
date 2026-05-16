# Coach Seed Labeling Workbook v2

This workbook supersedes the v1 coach seed workbook for new independent labels.

The v2 schema separates four decisions that were previously mixed together:

1. Whether the current turn is diagnosable.
2. The student's current problem-solving state.
3. The missing bridge family and subtype.
4. The registered focus id, or whether a new focus is needed.

## Files

| File | Use |
| --- | --- |
| `coach_seed_labeling_workbook_v2.zh.xlsx` | Recommended Chinese Excel workbook for coach labeling. It contains dropdowns, Chinese explanations, frozen panes, and no seed gold/topic hints. |
| `focus_registry_v1.json` | Candidate focus registry used by the workbook dropdowns and validation scripts. |
| `bridge_subtype_registry_v2.json` | Family-constrained subtype registry. The validator uses it to ensure `primary_bridge_subtype_id` belongs to `primary_bridge_family`. |

Do not use `coach_seed_labeling_workbook_v1.prefilled.csv` or any review workbook for independent labeling. Those files can expose seed labels or gold-like hints.

## Recommended Workflow

1. Open `coach_seed_labeling_workbook_v2.zh.xlsx`.
2. Go to the `标注表` sheet.
3. Read `学生当前问题（先看）` and `题目/上下文`.
4. Start from `这一轮类型`, then fill the yellow columns from left to right.
5. Use dropdowns when available. For multi-select fields, use English semicolon `;` between values.
6. If there is no recent dialogue or code, keep `N/A`.
7. Do not use `1` as a placeholder.
8. Set `标注状态` to `已标完（labeled）` only after the row is complete.

## Key Changes From v1

| v1 field | v2 replacement |
| --- | --- |
| `coach_known_focus` | `registered_focus_id`; this means system focus id, not what the student already knows. |
| `coach_bridge_subtype` | `primary_bridge_subtype_id` plus `primary_bridge_subtype_note`. |
| `coach_bridge_evidence` | `evidence_type` plus `evidence_quote`. |
| `coach_forbidden_content` | `general_forbidden_content` plus `bridge_specific_forbidden_content`. |
| `coach_allowed_help_level` | `max_scaffold_level`, now supports `L0` through `L3`. `L4_forbidden` is reserved for response leakage evaluation, not recommended help. |
| `coach_notes` | `coach_note_tags` plus free-text `coach_free_notes`. |

## Important Fields

| Column | Meaning |
| --- | --- |
| `turn_type` | First decision: normal diagnosable learning turn, insufficient context, complete solution/code request, critical bridge request, algorithm confirmation, local completion, debugging, etc. |
| `policy_risk_type` | Policy/leakage risk for the turn, separated from the student's cognitive state. |
| `diagnosis_uncertainty` | Whether the current evidence is enough to diagnose the bridge. |
| `student_problem_solving_state` | Current problem-solving state, such as modeling gap, method application gap, debugging localization gap. |
| `student_attempt_level` | How much work the student has already shown. |
| `student_already_knows` | Free-text field for what the student already said they know, such as LCA, brute force, or "probably DP". |
| `student_already_stated_bridge` | Whether the key bridge has already been stated by the student or exposed by a previous tutor. This is crucial for leakage judgments. |
| `primary_bridge_family` | Main missing bridge family, using the CP-specific v2 taxonomy. |
| `primary_bridge_subtype_id` | Abstract dot-notation subtype for quantitative analysis. It must match the selected `primary_bridge_family` and should describe a transferable bridge shape, not a single algorithm instance. |
| `registered_focus_id` | Existing system focus id from `focus_registry_v1.json`, or `unknown` / `not_applicable`. |
| `focus_match_status` | Whether the row matches an existing focus or needs a new one. |
| `max_scaffold_level` | Strongest appropriate help for this turn. `L0` means clarify/request evidence only. Valid values are `L0`, `L1`, `L2`, and `L3`. |
| `bridge_specific_forbidden_content` | The abstract leakage shape that the AI must not directly complete, such as an exact state definition, full recurrence, guard condition, boundary update rule, or fully worked trace. |
| `coach_note_tags` | Short structured note tags such as `multi_bridge_case` or `needs_discussion`. |
| `coach_free_notes` | Free-text coach notes for disagreement discussion or case-specific comments. |

## Boundary Rules

Use `turn_type` for the interaction scenario, not the detailed cognitive gap.

Use `algorithm_topic` / `registered_focus_id` / notes for concrete algorithm context. Do not create separate bridge subtypes for every algorithm. For example, a Dijkstra stale priority-queue entry should be labeled as `predicate.obsolete_candidate_guard`, not as a Dijkstra-only bridge subtype. See `bridge_taxonomy_abstraction_policy_v1.md`.

For example:

```text
学生：我知道要 LCA，但不知道每条路径到底在哪里加减标记。
```

Recommended labels:

| Field | Label |
| --- | --- |
| `turn_type` | `diagnosable_learning_turn` |
| `student_problem_solving_state` | `method_application_gap` |
| `student_already_knows` | `LCA` |
| `primary_bridge_family` | `aggregation_contribution_bridge` |
| `primary_bridge_subtype_id` | `aggregation.path_contribution_marking` |
| `registered_focus_id` | `tree_path_difference` |

Do not create a separate `turn_type` for "knows the algorithm but cannot adapt it." That idea belongs in `student_problem_solving_state=method_application_gap`.

## Family-Subtype Constraint

Each bridge subtype belongs to exactly one bridge family in `bridge_subtype_registry_v2.json`.

For example:

| Family | Valid subtype |
| --- | --- |
| `predicate_condition_bridge` | `predicate.feasibility_truth_direction` |
| `aggregation_contribution_bridge` | `aggregation.path_contribution_marking` |
| `correctness_invariant_bridge` | `correctness.local_choice_exchange_argument` |

The validator reports an error if a row mixes unrelated values, such as `primary_bridge_family=aggregation_contribution_bridge` with `primary_bridge_subtype_id=predicate.feasibility_truth_direction`.

## Regenerate Workbook

```bash
python3 -m evals.aichat.export_coach_seed_labeling_workbook_v2 \
  --seed-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --focus-registry docs/research/focus_registry_v1.json \
  --output-xlsx docs/research/coach_seed_labeling_workbook_v2.zh.xlsx
```

## Validate A Filled Workbook

```bash
python3 -m evals.aichat.validate_coach_workbook_v2 \
  --input docs/research/coach_seed_labeling_workbook_v2.zh.xlsx \
  --focus-registry docs/research/focus_registry_v1.json
```

The validator accepts Chinese dropdown values such as `可以诊断的学习轮次（diagnosable_learning_turn）` and extracts the machine id inside parentheses. It reports hard errors for invalid enums, unknown focus ids, placeholder `1`, empty evidence on labeled rows, and family/subtype mismatches. It reports warnings when `turn_type` and `policy_risk_type` appear inconsistent.

## Current Scope

The v2 workbook is for offline research labels only. It does not change the online AIChat runtime.

## Reliability Note

Labels exported from one filled workbook are **single-coach expert reference labels**, not unique ground truth.

Use them for smoke tests and early diagnosis debugging. For paper metrics, follow
[annotation_reliability_protocol_v1.md](annotation_reliability_protocol_v1.md):

1. Ask a second coach to label 20%-30% of the same rows independently.
2. Run `evals.aichat.summarize_coach_label_agreement`.
3. Review `needs_adjudication_case_ids`.
4. Use an adjudicated reference file for headline benchmark numbers.

The code may still use filenames or fields containing `gold` for runner
compatibility, but the research interpretation should be `single_coach_reference`
until adjudication is complete.
