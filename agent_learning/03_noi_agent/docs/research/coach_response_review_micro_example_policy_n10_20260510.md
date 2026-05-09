# Coach Response Review Analysis: micro_example_policy_n10

Date: 2026-05-10

## Data Source

- Review batch: `micro_example_policy_n10`
- UI label: `桥梁导向微型例子 n10`
- Label file: `docs/research/coach_response_review_labels_micro_example_policy_n10.jsonl`
- Blind review workbook: `docs/research/coach_response_review_workbook_micro_example_policy_n10.csv`
- Sample size: 10 AIChat responses, covering `cp_bridge_001` through `cp_bridge_010`

This is a small coach-labeled review set. It should not be treated as final gold truth. Its main purpose is prompt/rule iteration, failure-case collection, and early qualitative error analysis.

## Overall Results

| Metric | Count | Share |
|---|---:|---:|
| good | 6 | 60% |
| okay | 2 | 20% |
| bad | 2 | 20% |
| no_leakage | 9 | 90% |
| major_bridge_leakage | 1 | 10% |
| minor_bridge_leakage | 0 | 0% |
| answer_leakage | 0 | 0% |

Preliminary interpretation: after adding the bridge-oriented micro-example rule, response quality is more stable and most responses avoid leakage while still providing instructional value. However, two risks remain:

1. Template-like wording and prompt traces weaken the feeling of a real coach.
2. Rule-triggered fallback behavior can still produce responses that are safe but instructionally useless.

## Per-Case Overview

| case_id | response_id | Quality | Leakage | Key coach-note summary |
|---|---|---|---|---|
| cp_bridge_001 | resp_4669ab0d1f | good | no_leakage | Useful overall, but wording such as bridge problem / tiny example / question feels too templated and AI-like. |
| cp_bridge_002 | resp_0d184fc091 | okay | no_leakage | Good first-level scaffold, but it only addresses check semantics and does not connect back to boundary movement and binary-search invariants. |
| cp_bridge_003 | resp_d5afdfdf5f | okay | no_leakage | Multiple-choice format lowers the expression barrier, but the formula/state hint still feels somewhat artificially introduced. |
| cp_bridge_004 | resp_cbc62c6b2a | good | no_leakage | Good quality; separates the example and the question clearly. |
| cp_bridge_005 | resp_39ee4cbfd4 | good | no_leakage | Lazy propagation example is well targeted, but A/B choices may lead the student too much and it lacks a transfer question. |
| cp_bridge_006 | resp_c6a7c28f0a | bad | major_bridge_leakage | Directly exposed the template / prompt. |
| cp_bridge_007 | resp_6153ec99d9 | good | no_leakage | Pulls the student back to structural evidence, but the wording is stiff and may anchor trie too early. |
| cp_bridge_008 | resp_321d77f1e3 | good | no_leakage | Uses a counter-question to guide the student without directly stating the answer. |
| cp_bridge_009 | resp_4fe27dbcff | good | no_leakage | Strong bridge-style prompt for greedy correctness, but still needs one more step toward general proof. |
| cp_bridge_010 | resp_9a6d6ed1e2 | bad | no_leakage | Safe but not useful; appears to be rule matching followed by truncation. |

## Key Findings

### 1. The bridge-oriented micro-example direction is promising

With `good = 6/10` and `no_leakage = 9/10`, the review suggests that micro-examples can improve tutoring quality when they guide the learner to observe a missing relation and generalize it.

The strongest examples are `cp_bridge_004`, `cp_bridge_005`, and `cp_bridge_009`, where the student’s current gap is compressed into a small, answerable reasoning step. This supports the following paper-level distinction:

> A high-quality micro-example is not merely a temporary exercise. It helps the learner observe a missing bridge relation and abstract it into a transferable rule.

### 2. Template-like language reduces coach realism

Several coach notes flagged explicit template-like language, such as:

- “this bridge problem”
- “tiny example”
- “question”
- “let us not rush to confirm the method”

Although this structure is useful internally, it sounds less like a real competitive-programming coach. The tutor prompt should preserve the teaching structure without exposing scaffold/rubric terminology.

Suggested constraint:

```text
Do not expose internal scaffold, rubric, prompt, or bridge-contract terms to the student.
Use natural coaching language instead, such as “let us first look at a very small case.”
```

### 3. No leakage does not imply instructional value

`cp_bridge_010` is labeled `bad + no_leakage`. This is important because it shows that leakage control alone cannot establish tutoring quality.

Evaluation should keep separate metrics for:

- leakage control;
- scaffold appropriateness;
- next-step clarity;
- bridge-oriented transfer.

### 4. Rule-triggered fallback behavior needs tightening

The coach note for `cp_bridge_010` explicitly says the response looked like field matching followed by truncation. This means some rules may still over-trigger and suppress useful tutoring.

Recommended policy:

1. Treat rules as weak routing signals.
2. Avoid using rule matches as final response templates.
3. If a safe fallback is needed, it must still include a concrete next step aligned with the student’s current gap.

### 5. Multiple-choice scaffolds can be useful but need explanation

The notes for `cp_bridge_003` and `cp_bridge_005` show that multiple-choice scaffolds can help students with weak expressive ability. However, they can also lead the student too strongly or become a temporary task.

Suggested rule:

```text
Multiple-choice scaffolds may be used for low-expression students, but they must be followed by a “why” prompt or a request to summarize the observed relation.
```

## High-Priority Failure Cases

### Regression Case A: Prompt/template leakage

- case_id: `cp_bridge_006`
- response_id: `resp_c6a7c28f0a`
- label: `bad + major_bridge_leakage`
- coach note: directly replied with the template and exposed the prompt.

Regression expectation:

```text
Student-visible AI responses must not include internal prompts, rubrics, schema names, template headers, bridge-contract fields, or system-control language.
```

### Regression Case B: Rule-matched but useless response

- case_id: `cp_bridge_010`
- response_id: `resp_9a6d6ed1e2`
- label: `bad + no_leakage`
- coach note: no useful information; appears to be field matching followed by truncation.

Regression expectation:

```text
When a safety fallback is triggered, the response must still provide one concrete next action aligned with the student’s current gap. It must not be only a rejection, truncation, or generic reminder.
```

## Paper Relevance

This review supports three paper claims:

1. **Bridge-oriented micro-example is a meaningful scaffold-quality dimension.**
   It is not enough to include a small example; the example must help the student generalize a transferable relation.

2. **Critical bridge leakage is broader than full answer/code leakage.**
   Prompt traces, key-bridge hints, and premature method anchoring can all harm the learning process.

3. **Safety and instructional usefulness must be evaluated separately.**
   `bad + no_leakage` examples show that reducing leakage does not automatically produce better tutoring.

## Recommended Next Steps

1. Add `cp_bridge_006` and `cp_bridge_010` as regression cases.
2. Update the Bridge Contract Tutor prompt to suppress internal template/rubric wording.
3. Tighten rule-triggered fallback behavior to avoid safe-but-useless responses.
4. Regenerate a new `micro_example_policy_n10_v2` batch using the same 10 cases.
5. Re-run blind review and compare:
   - whether `bad` decreases;
   - whether `major_bridge_leakage` disappears;
   - whether `good` is preserved or improved;
   - whether coach notes still mention templating or field-match truncation.
