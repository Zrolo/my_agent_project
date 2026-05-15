# Formal Evaluation Protocol v1

Date: 2026-05-14

This document defines the formal evaluation protocol draft for CP-MissingBridgeBench. It is not a result report. Its purpose is to lock the roles of primary, secondary, and exploratory experiments before looking at formal held-out results, reducing cherry-picking, p-hacking, benchmark overfitting, and test-set contamination risks.

## Core Principle

Data should affect conclusions, but formal results must not retroactively determine the experiment design.

Allowed:

- use development data to fix the runner, export workbooks, context injection, and dataset quality;
- compare prompts, conditions, follow-up formats, and AI-student simulation on dev sets;
- freeze the formal protocol based on development evidence;
- honestly report negative results, failure modes, and uncertainty after formal evaluation.

Not allowed:

- switch the primary experiment after seeing formal held-out results;
- promote a condition to the main method because it happened to win;
- remove a metric because it produced an unfavorable result;
- modify prompts on the same formal test set and still call it held-out;
- treat AI self-review as coach gold;
- present draft or context-contaminated runs as paper headline results.

## Data Splits

### Development / Regression Set

Purpose:

- prompt tuning;
- runner fixes;
- workbook field fixes;
- condition selection;
- follow-up / AI-student simulation feasibility testing;
- leakage rubric and static-lint development.

Repeated runs and modifications are allowed here, but all changes must be recorded in `prompt_patch_log.md`, `judge_prompt_patch_log.md`, or the relevant runbook.

### Draft Held-out Cases

Current clean draft:

```text
docs/research/bridgebench_cp_heldout_v3_50_draft.jsonl
```

This version fixes the `recent_dialogue` / `student_message` mismatch found in v2, but it remains `draft_needs_coach_review` and must not be called gold.

Purpose:

- dataset-quality review;
- generation-only stability check;
- verify that problem sources, statements, student messages, recent dialogue, and code snippets are natural and reviewable.

Not allowed:

- paper headline claims;
- prompt tuning followed by calling the same data held-out;
- replacing Coach A / Coach B reference labels.

### Frozen Held-out Reference

The formal main experiment must use a frozen reference JSONL, for example:

```text
docs/research/bridgebench_cp_heldout_v3_50_frozen.jsonl
```

Go conditions:

- 50 cases have completed source/context review;
- Coach A has labeled the full set;
- Coach B has independently labeled at least 20 overlap cases;
- low-confidence, multi-bridge, and major disagreement cases have been adjudicated or marked;
- `validate_heldout_50_dataset --require-frozen-status` passes;
- prompts, judges, repair, review rubric, and model/runtime configuration are frozen.

## Experiment Levels

### Primary Experiment: Single-turn Held-out Evaluation

The primary experiment remains the 50-case single-turn evaluation.

Purpose:

- evaluate turn-level missing-bridge diagnosis;
- evaluate critical bridge leakage;
- compare tutoring harnesses on quality, leakage, latency, and call cost.

The primary experiment does not claim:

- to equal real long-term classroom learning outcomes;
- that one framework is best in all interaction settings;
- to prove multi-turn student learning gains.

Recommended main-table conditions should be frozen before the formal run, for example:

```text
current_system_deployment
enhanced_prompt_only_clean
codehelp_codeaid_clean
dbox_inspired_guard
bridge_inspired_expert_decision_clean
single_llm_structured_guard
bridge_contract_compact_guard
bridge_contract_compact_guard_repair
```

The actual condition set is defined by the frozen runbook. It must not be changed after seeing formal results.

### Secondary Experiment: Controlled Follow-up Stress Test

The controlled follow-up stress test is secondary, not a replacement for the primary experiment.

Purpose:

- test whether systems continue coherently after short student replies;
- test whether systems repeat ineffective questions, jump steps, or leak the critical bridge too early;
- compare conditions under the same follow-up probes.

Suggested design:

- 10-15 dev/frozen follow-up cases;
- each case has 1-2 fixed short student follow-up probes;
- every condition receives the same probe;
- evaluate continuity, scaffold adjustment, leakage, and student-readiness.

Paper wording:

```text
controlled follow-up stress test
```

Do not call it:

```text
real student multi-turn learning experiment
```

### Exploratory Experiment: AI-student Dynamic Simulation

AI-student simulation is exploratory / appendix only unless a separate simulator protocol is frozen in advance.

Purpose:

- discover multi-turn interaction failure modes;
- observe whether systems repeat, jump steps, or leak under F1-F4 student followability profiles;
- produce error-analysis episodes.

Risks:

- simulator bias;
- diverging trajectories across conditions make strict pairing difficult;
- the simulated student may be too cooperative or too adversarial;
- simulation cannot replace real student studies.

If used in the paper, call it:

```text
exploratory simulated dialogue analysis
```

Do not call it:

```text
student learning outcome
```

## Prompt / Judge Freeze

Before formal held-out evaluation, freeze:

- enhanced prompt-only prompt;
- DBox-inspired prompt;
- CodeHelp/CodeAid-style prompt;
- Bridge-inspired expert-decision prompt;
- Bridge Contract prompt;
- Leakage Guard prompt;
- Repair prompt;
- offline response grader prompt;
- offline leakage grader prompt;
- response review rubric;
- model/runtime configuration.

After freeze:

- do not modify prompts based on formal held-out results;
- if an infrastructure bug must be fixed, such as context injection, empty responses, JSON parsing, or internal tag leakage, record it as an infrastructure fix;
- if the fix changes tutoring or leakage policy, the old formal result is invalidated and must be relabeled as a development run.

## Context Integrity

Formal generation must satisfy:

- `recent_dialogue` and `student_message` are aligned;
- the model sees the same context that reviewers see;
- `recent_dialogue` is parsed into real `user/assistant` messages;
- `student_message` is the final user message;
- `problem_context`, `problem_title`, `problem_url`, and `student_code_excerpt` enter the current user message;
- result rows record `generation_context_source` and `generation_message_count`;
- student-visible responses do not contain internal `[LEVEL:Lx]` tags.

Old v2 / zh5 context-mismatched results are development diagnostics only, not formal context-aware blind-review evidence.

## Metrics

Primary metrics:

- overall quality;
- core6;
- scaffold appropriateness;
- bridge-oriented micro-example;
- student-ready pass;
- critical bridge leakage;
- answer/code leakage;
- p50 / p95 latency;
- LLM call count.

Secondary metrics:

- response burden;
- safe_ready;
- guard rewrite/block rate;
- repair_success_rate;
- repair_still_leaks_rate;
- static lint flags;
- stage errors.

Exploratory metrics:

- AI-student progress;
- simulated followability;
- episode-level coherence;
- repeated-question loop;
- simulator-reported confusion.

## Statistical Reporting

Formal reports must not treat `cases × conditions` rows as independent samples.

Prefer case-level paired reporting:

- win / tie / loss;
- mean paired difference;
- paired bootstrap confidence interval;
- Friedman test;
- Wilcoxon signed-rank with Holm correction;
- McNemar / paired categorical comparison for leakage where applicable.

20-case or smaller samples must be described as:

```text
pilot / development evidence
```

not:

```text
statistically proven headline result
```

## Result Interpretation Rules

If a strong baseline wins:

- do not hide it;
- conclude that the baseline is a strong default strategy, while missing bridge / critical leakage remain useful evaluation and high-risk control signals.

If Bridge Contract only wins on high-risk subsets:

- this may support risk-triggered routing;
- do not claim it should be the unconditional default generation path.

If Guard / Repair reduces leakage but reduces quality:

- report the quality-safety trade-off;
- do not claim leakage is solved.

If all strong baselines are low-leakage and high-quality:

- weaken the system-improvement claim;
- strengthen the benchmark / evaluation-framework contribution;
- analyze whether critical bridge leakage mainly appears in specific high-risk contexts.

## Exclusion Rules

May exclude:

- missing or non-traceable problem source;
- `recent_dialogue` / `student_message` mismatch;
- empty final response after targeted rerun still fails;
- coach determines the case is not a reviewable tutoring scenario;
- obvious duplicate case.

May not exclude:

- a condition scores poorly;
- a case is unfavorable to Bridge Contract;
- a baseline is unexpectedly strong;
- Guard/Repair fails;
- static lint or human scoring exposes an unwanted risk.

## Required Artifacts Before Paper Claims

Before formal paper claims, produce at least:

```text
formal_eval_protocol_v1.zh.md / .md
frozen dataset JSONL
frozen prompt / judge / rubric version notes
Coach A full labels
Coach B overlap labels
adjudication or disagreement report
generation integrity report
blind review workbook and hidden key
paired analysis report
judge calibration report
error analysis report
```

## Current Status

As of 2026-05-14:

- single-turn held-out remains primary;
- controlled follow-up stress test is secondary and still needs a frozen design;
- AI-student simulation is exploratory and cannot replace the primary experiment;
- clean v3 draft has been generated but still needs coach review and frozen export;
- the next 50-case generation-only run must use AIChat-compatible context injection;
- old context-contaminated runs do not enter formal headline results.
