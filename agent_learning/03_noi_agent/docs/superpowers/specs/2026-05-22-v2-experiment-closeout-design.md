# CP-MissingBridgeBench v2 Experiment Closeout Design

## Purpose

This spec defines the closeout process for the CP-MissingBridgeBench v2 100-case / 700-response experiment. The goal is to turn the completed review artifacts into a stable, auditable benchmark evidence package before any manuscript rewrite or v4 method development.

The closeout is evidence-facing, not method-development-facing. It does not modify prompts, rerun online AIChat, change student-visible responses, add experimental conditions, or revise the v3 dialogue-state main tables.

## Current Research Position

The project direction is now benchmark/evaluation-first:

- CP-MissingBridgeBench evaluates premature reasoning-step disclosure / critical bridge leakage in competitive-programming tutoring.
- The v2 real-log-grounded 100-case experiment is the main asset to close out.
- DBox-inspired + Guard appears to be a strong baseline in the current v2 review.
- Bridge Contract / Repair variants are treated as evaluated designs and failure-analysis targets, not as already proven superior methods.
- v4 prompt and framework development is deferred until v2 results are frozen.

## Scope

The closeout covers:

1. Data integrity checks for the 100-case / 700-response review package.
2. v2 result recomputation from existing reviewed artifacts.
3. Same-case paired comparisons and uncertainty summaries.
4. Stratified analysis of result patterns.
5. Failure-mode analysis for Bridge Contract and Repair variants.
6. Human-review reliability and adjudication-status reporting.
7. v2 evidence freeze manifest and privacy boundary documentation.

The closeout does not cover:

- Editing the manuscript narrative.
- Designing or running v4 prompts.
- Changing production AIChat.
- Generating additional student-facing responses.
- Reassigning v3 dialogue-state evidence classes.
- Publishing case-level real-student material.

## Inputs

The implementation plan should resolve the exact current filenames, but the expected input categories are:

- v2 100-case source-selection manifest.
- v2 case-freeze workbook or freeze CSV.
- v2 700-response generation file.
- v2 human coach review workbook or exported CSV.
- v2 review schema and validator scripts.
- Existing v2 analysis scripts, if present.
- Existing second-coach / focus-review / adjudication artifacts, if present.

Private or restricted materials remain private. The closeout must not copy raw student text, full code, complete AIChat replies, identity mappings, hash salts, or private workbooks into public outputs.

## Phase 1: Data Integrity Audit

The integrity audit checks whether the reviewed v2 package is internally coherent.

Required checks:

- Exactly 100 unique case ids are present.
- Each case has exactly 7 reviewed design responses.
- Exactly 700 response-level review rows are present, unless a documented exclusion exists.
- Each response row has a valid case id, anonymized design id, and response id.
- Review fields required by the v2 rubric are non-empty.
- Enum fields use allowed values.
- No duplicate response ids are present.
- Design labels shown to reviewers are anonymized or otherwise documented.
- No response-generation failure, JSON parse failure, or fallback response is silently included without a status flag.
- Case-freeze fields needed for interpretation are present.

Output:

- `v2_data_integrity_report`.
- Machine-readable validation summary, if practical.

## Phase 2: Main v2 Results

The main v2 summary recomputes results only from existing v2 reviewed artifacts.

Required metrics:

- Overall quality mean by design.
- Student-ready count by design.
- Safe-ready count by design.
- Major + answer leakage count by design.
- Answer leakage count by design.
- Learner-burden distribution by design.
- Helpfulness and scaffold-quality summaries if those fields exist in the review table.
- Within-case rank summaries if rank fields exist.

Required design focus:

- DBox-inspired + Guard.
- Bridge Contract + Guard.
- Bridge Contract + Guard/Repair.
- Bridge-guided DBox-style + Guard.
- Prompt-only and no-direct-solution variants as lower-complexity reference designs.

Output:

- `v2_main_results_summary`.
- Result tables suitable for later manuscript use, with no claim of method victory unless supported by the reviewed numbers.

## Phase 3: Same-Case Paired Comparisons

Paired comparisons must use case-level pairing. The closeout must not treat 700 response-level reviews as 700 independent cases.

Required pairs:

- Bridge Contract + Guard vs DBox-inspired + Guard.
- Bridge-guided DBox-style + Guard vs DBox-inspired + Guard.
- Bridge Contract + Guard/Repair vs DBox-inspired + Guard.
- Bridge Contract + Guard/Repair vs Bridge Contract + Guard.
- Prompt-only and no-direct-solution variants vs DBox-inspired + Guard.

Required outputs:

- Mean paired delta.
- Win / tie / loss counts.
- Bootstrap confidence interval if available.
- Permutation p-value if the existing scripts support it.

Interpretation rule:

- If DBox-inspired + Guard leads clearly, report it directly as a strong baseline.
- Do not reframe losing Bridge Contract variants as superior.
- Repair effects from main condition means must not be written as component-level causal effects.

## Phase 4: Stratified Analysis

Stratified analysis asks where observed design differences come from.

Required strata, subject to field availability:

- Help-seeking context: implementation, debugging, algorithm design, clarification, direct answer request.
- Reasoning focus: implementation detail, debugging localization, predicate/check, state definition, transition reasoning, data-structure meaning, boundary/order, correctness/invariant, and other resolved labels.
- Context sufficiency: sufficient, partial, insufficient, unclear.
- Leakage severity.
- Learner burden.

Primary question:

- Is DBox-inspired + Guard strong across strata, or mainly in the implementation/debugging-heavy v2 distribution?

Output:

- `v2_stratified_results_summary`.
- A limitation note if the v2 distribution is heavily concentrated in implementation/debugging cases.

## Phase 5: Failure-Mode Analysis

Failure-mode analysis explains what the benchmark surfaces, not why a design should be declared a winner.

Bridge Contract / Repair failure modes to track:

- Over-conservatism: safe but not useful.
- Generic advice: does not catch the current student bottleneck.
- Boundary failure: still reveals the missing reasoning step.
- Repair over-deletion: removes useful scaffold content.
- Repair burden increase: leaves the student with too many vague tasks.
- Missed concrete next action.
- Debugging mismatch: fails to provide a bounded diagnostic probe in implementation/debugging-heavy cases.

Output:

- `v2_failure_mode_summary`.
- Paraphrased examples only, if examples are included.
- No raw student text, full code, or full AIChat response.

## Phase 6: Human Review Reliability

The closeout must describe review authority conservatively.

Required checks:

- Count single-reviewed cases and responses.
- Count double-reviewed or focus-reviewed cases if available.
- Count adjudicated cases if available.
- Summarize high-severity leakage disagreements if available.

Reporting rule:

- Do not write Coach A, Coach B, focus review, or adjudication as final gold.
- Write them as expert review views, targeted second review, or adjudication support.

Output:

- `v2_human_review_reliability_summary`.

## Phase 7: Evidence Freeze Manifest

After integrity and analysis outputs are generated, freeze the v2 evidence package.

The manifest should record:

- Input artifact paths.
- Output artifact paths.
- Script paths and versions.
- Hashes for reviewed workbooks, exported CSVs, and result summaries where practical.
- Privacy and release boundaries.
- Known limitations.
- Date of freeze.

Freeze rule:

- After the v2 evidence freeze, results are not changed for narrative convenience.
- If a serious data or script defect is discovered later, create a new versioned evidence freeze rather than patching results silently.

Output:

- `v2_evidence_freeze_manifest`.

## Safety Boundaries

The closeout must preserve these boundaries:

- No dialogue-state v3 main-table recomputation.
- No new main experiment condition.
- No online AIChat, prompt, active-mode, quota, migration, or runtime modification.
- No new Real-AIChat result generation.
- No student-visible response change.
- No raw student text, full student code, complete AIChat response, real identity, hash salt, or reversible mapping in public outputs.
- No claim that LLM grader replaces human coach review.
- No claim that Repair caused main-condition improvements unless supported by same-candidate stress evidence.
- No claim that Bridge Contract / Repair is superior if v2 results do not support it.

## Success Criteria

The closeout is complete when:

- Data integrity checks pass or all failures are explicitly documented.
- Main v2 results are recomputed from existing reviewed artifacts.
- Same-case paired comparisons are produced.
- Stratified summaries explain distribution effects.
- Failure modes are summarized without exposing private material.
- Human-review reliability is documented conservatively.
- A versioned v2 evidence freeze manifest exists.
- The project can later rewrite the manuscript around benchmark/evaluation findings without changing the underlying v2 results.

## Implementation Planning Notes

The implementation plan should first identify the exact current v2 artifacts and scripts. If existing scripts already compute part of the closeout, reuse them. If gaps remain, add small, auditable scripts focused only on v2 closeout.

The implementation plan should not start v4 prompt development. v4 belongs to a later design cycle after v2 closeout.
