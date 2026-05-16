# CP-MissingBridgeBench Evaluation Protocol v2

Date: 2026-05-15

This protocol governs response evaluation for Research v1 and later AIChat / CP-MissingBridgeBench experiments. Its goal is not to remove all subjectivity from educational review, but to turn coach judgment into a calibrated, auditable, and reportable expert reference.

## 1. Why v2 is needed

Competitive-programming tutoring responses are not simple correct/incorrect outputs. A response may:

- avoid full code but reveal the critical bridge;
- avoid leakage but be too vague to help the student continue;
- sound natural but fail to answer the current student question;
- use a micro-example that already demonstrates the relation the student was supposed to infer.

These require educational judgment. Following AI tutor and agent evaluation practice, open-ended tutoring tasks should use rubric-based human review, sample-specific criteria, partial double annotation, adjudication, and calibrated LLM graders rather than relying only on automatic metrics.

## 2. Roles

| Role | Purpose | Final truth? |
| --- | --- | --- |
| Coach A | Main reviewer for all samples | expert reference |
| Coach B | Independent reviewer for 20%-40% of samples | agreement / calibration |
| Adjudicator | Resolves major disagreements | adjudicated reference |
| AI prelim reviewer | Development-stage triage | no |
| Offline deterministic checks | Empty outputs, code blocks, internal tags, latency | objective engineering checks |
| LLM judge / grader | Auxiliary semantic grading | no, must be calibrated against coach reference |

Papers should use `coach reference`, `expert reference`, or `adjudicated reference`, and should avoid calling a single coach label absolute ground truth.

## 3. Data split

| Split | Purpose | Prompt tuning allowed? |
| --- | --- | --- |
| dev / regression set | Prompt/rubric repair and error discovery | yes, with patch log |
| calibration set | Coach calibration | discussion allowed; not headline |
| held-out test set | Formal system result | no prompt changes after seeing results |
| repair stress set | Same-candidate before/after Repair analysis | separate report |

The current `dbox_bridge_hybrid_generation_only_50_20260515_merged` run is a dev / regression run, not a final held-out headline result.

## 4. Standard review workflow

### Step 0: Freeze versions

Before formal held-out evaluation, freeze:

- tutor prompts;
- Bridge Contract prompts;
- DBox-inspired / Bridge-guided prompts;
- Guard prompt;
- Repair prompt;
- review rubric;
- AI prelim reviewer prompt or heuristic script;
- model/runtime configuration.

Do not revise prompts after inspecting held-out results.

### Step 1: Calibration round

Before blind review, sample 5 cases for a calibration round.

Workflow:

1. Coach A and Coach B review the same samples.
2. They first give independent judgments.
3. They then discuss disagreements, especially:
   - what counts as `major_bridge_leakage`;
   - what counts as justified concept explanation;
   - what counts as safe but insufficient scaffolding;
   - when student response burden is too high;
   - when a micro-example is scaffolding versus leakage.
4. New boundary rules are written into the rubric or calibration notes.

Calibration samples are not used as headline results.

### Step 2: Blind review

Coaches see anonymous response ids and do not see condition names.

Each sample is read in this order:

1. problem link, necessary statement, and context;
2. recent dialogue;
3. previous AI prompt / scaffold;
4. current student question;
5. target AI response.

All scores apply only to the target AI response, not to the recent dialogue itself.

### Step 3: Required notes

`coach_notes` is required when:

- `coach_leakage_label = major_bridge_leakage`;
- `coach_leakage_label = answer_leakage`;
- `coach_would_show_to_student = no`;
- `coach_overall_quality_score <= 2`;
- `coach_preference_rank = 1` or worst in the case;
- `coach_needs_discussion = yes`;
- the context appears mismatched;
- reviewer confidence is low.

Notes should explain the reason, not merely say “good” or “bad”.

Recommended format:

```text
Strength: ...
Problem: ...
Suggestion: ...
```

### Step 4: Partial double annotation

In formal 50-case evaluation, at least 20%-40% of cases should be independently reviewed by Coach B.

The overlap sample should cover:

- bridge families;
- difficulty levels;
- code and no-code cases;
- follow-up turns;
- AI-prelim high-risk samples;
- cases with large condition differences.

### Step 5: Agreement report

Report at least:

- percent agreement for categorical labels;
- weighted agreement / weighted kappa for ordinal scores;
- win/tie/loss agreement for preference ranks;
- agreement on `major_bridge_leakage`;
- agreement on `would_show_to_student`;
- `needs_adjudication_case_ids`.

For small samples, prioritize percent agreement, disagreement examples, and adjudication notes over over-interpreting p-values.

### Step 6: Adjudication

Adjudicate samples when:

- Coach A/B differ between `no_leakage` and `major/answer`;
- `would_show_to_student` differs between `yes` and `no`;
- overall quality differs by 2 or more levels;
- either coach marks `needs_discussion=yes`;
- context appears mismatched.

Adjudication outputs:

- final label;
- adjudication note;
- whether the sample enters headline metrics;
- whether the sample is kept for error analysis only.

## 5. Metric layers

### Subjective / expert metrics

- overall quality;
- core6 / micro7;
- scaffold appropriateness;
- scaffold sufficiency;
- next-step clarity;
- would show to student;
- preference rank.

### Semi-objective pedagogical risk

- leakage label;
- bridge reveal justification;
- student response burden;
- context alignment flag.

### Objective engineering metrics

- empty final response;
- stage error;
- internal tag leakage;
- latency p50 / p95;
- LLM call count;
- token usage;
- repair applied;
- blocked / fallback.

These should be reported separately rather than collapsed into one score.

## 6. AI prelim reviewer rules

AI prelim review may be used for:

- development-stage triage;
- finding high-risk rows;
- selecting Coach B overlap samples;
- prioritizing human review.

AI prelim review must not be used for:

- replacing coach reference;
- headline results;
- proving one condition is better;
- automatic prompt patching.

LLM judges / graders must be calibrated against coach reference, with precision, recall, false negative, false positive, and unknown rates reported.

## 7. Result wording boundaries

Acceptable:

```text
In coach-calibrated blind review, a condition showed higher student-ready pass on the dev set.
```

Not acceptable:

```text
AI prelim review proves that one system is significantly better.
```

Acceptable:

```text
The result suggests that DBox-style scaffolding is a strong baseline and that Bridge-guided DBox-style should enter held-out evaluation.
```

Not acceptable:

```text
Bridge-guided DBox-style has been proven to outperform DBox.
```

## 8. Immediate project requirements

From this protocol onward, response blind review must satisfy:

1. The workbook includes review workflow, rubric explanations, and required-note rules.
2. Human coaches use anonymous workbooks.
3. Key files are not shown during blind review.
4. AI prelim reports are marked `dev only / not coach gold`.
5. Human final analysis is separated from AI prelim analysis.
6. Formal held-out results include partial double annotation and adjudication.
