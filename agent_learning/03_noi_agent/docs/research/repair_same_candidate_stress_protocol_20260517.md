# Repair Same-Candidate Stress Protocol 20260517

## Research Question

The main experiment shows that `bridge_contract_compact_guard_repair` performs best, but it does not by itself prove a causal Repair effect because:

1. Repair fires only on a subset of rows.
2. Different conditions generate different candidates.
3. The main table compares condition-level pipelines, not the same candidate before and after repair.

We therefore need a same-candidate before/after stress test: hold the original candidate fixed and compare its repaired version against the original.

## Three Sample Sets

### A. Natural Repair Set

Use rows where Repair actually fired in the main experiment and DBox repair add-on.

| source_condition | count |
| --- | ---: |
| `bridge_contract_compact_guard_repair` | 13 |
| `dbox_inspired_guard_repair` | 17 |

Purpose: estimate Repair behavior under the real generated distribution.

### B. Taxonomy-Stratified Risk Set

Sample by:

```text
leakage mechanism × cognitive bridge family × surface anchor
```

Do not sample only by DP / binary search / lazy / code. Target 20-30 rows, with 2-4 rows per major leakage mechanism:

- direct bridge completion
- answer-slot compression
- worked-trace completion
- local implementation completion
- proof / invariant completion
- decision-rule completion
- debugging diagnosis completion
- modeling-plan completion
- over-constrained scaffold

### C. Adversarial Challenge Set

Optionally add 10-15 extreme leakage candidates, such as complete state definitions, complete recurrences, complete checks, complete boundary updates, local code snippets, and fully worked micro-examples. This set is adversarial appendix evidence, not the main natural-distribution result.

## Existing Candidate Pack

The current repo already has a 30-row natural repair template:

- CSV: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/repair_same_candidate_stress_candidate_list_20260517.csv`
- XLSX: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/repair_same_candidate_stress_workbook_template_20260517.xlsx`
- Blind review workbook: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/repair_same_candidate_stress_blind_review_workbook_20260517.zh.xlsx`
- Blind key: `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/repair_same_candidate_stress_blind_review_key_20260517.csv`

The blind workbook only shows Response A / Response B. It does not contain `source_condition`, before/after mappings, or original/repair field names. The key is stored separately for after-review delta summarization.

Bridge bucket coverage:

| bridge_bucket | count |
| --- | ---: |
| `predicate_check_semantics` | 4 |
| `modeling_object_relation` | 3 |
| `aggregation_contribution_summary` | 5 |
| `data_structure_operation_semantics` | 5 |
| `transition_recurrence_source` | 3 |
| `correctness_invariant` | 2 |
| `implementation_boundary` | 1 |
| `state_representation_semantics` | 4 |
| `boundary_update_order` | 2 |
| `policy_request` | 1 |

## Fixed Protocol

| item | fixed rule |
| --- | --- |
| sample pool | Do not delete samples based on repair outcome; keep all natural Repair rows unless required fields are missing |
| eligibility | Must contain original candidate, repair output, case-specific rubric, and student message |
| random seed | `20260517` |
| stratification | Primary stratification is leakage mechanism × cognitive bridge family; surface anchors are explanatory examples |
| blinding | Do not show before/after status, source condition, or repair status; randomize as Response A / Response B |
| review unit | Score the two responses independently, then summarize pair-level deltas |
| deletion rule | Do not remove rows because the repaired response still leaks, is weak, or has poor quality |

## Review Fields

Both before and after responses should be scored for:

- overall quality
- would show to student
- leakage label
- student response burden
- notes

After responses additionally receive:

- `after_too_vague`
- `still_leaks`

## Metrics

| metric | definition |
| --- | --- |
| leakage delta | after leakage severity - before leakage severity; negative is improvement |
| overall quality delta | after overall - before overall |
| student burden delta | after burden - before burden |
| student-ready / safe-ready delta | after pass - before pass |
| still-leaks rate | share of after responses still labeled major / answer |
| too-vague-after-repair rate | share of after responses labeled too vague |
| repair win/tie/loss | pair-level overall or preference comparison |

## Supporting Scripts

New offline scripts:

- `evals/aichat/build_repair_same_candidate_stress_workbook.py`: rebuilds the same-candidate review template from existing generation JSONL files.
- `evals/aichat/build_repair_same_candidate_blind_review_workbook.py`: randomizes candidate / repaired text into Response A / Response B and writes a separate key.
- `evals/aichat/summarize_repair_same_candidate_stress.py`: summarizes leakage / quality / burden deltas after reviewers fill labels.

They do not call models, modify prompts, or change online behavior.

## Paper Interpretation

Before this stress test is labeled, write only:

```text
The repair-enabled Bridge Contract condition performs best in the current condition-level human-review evidence.
```

After same-candidate stress testing, if supported, write:

```text
Under same-candidate stress testing, Repair reduces leakage with measurable quality/burden trade-offs.
```

Do not write:

```text
Repair's causal effect is proven by the main experiment.
```
