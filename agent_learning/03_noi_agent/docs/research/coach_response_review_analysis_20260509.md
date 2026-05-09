# Coach Response Review Mini-Analysis (2026-05-09)

## Data Source

- Coach labels: `/Users/kongyouli/Downloads/response_review_labels_20260509154713.csv`
- Anonymous key: `docs/research/coach_response_review_workbook_deepseek_flash_thinking_n10.key.csv`
- Review set: 20 responses across 10 cases.
- System condition: `bridge_contract` tutor, `predicted` guard, `tutor_only` pipeline, `deepseek_flash`.
- Compared variable: `chat_thinking_mode = enabled / disabled`, 10 responses each.

This is a small coach-labeled review set, not a final gold-standard dataset. It is best interpreted as early evidence for prompt/rubric iteration and qualitative error analysis.

## Overall Distribution

| Metric | Count | Share |
|---|---:|---:|
| good | 6 | 30% |
| okay | 9 | 45% |
| bad | 5 | 25% |
| no_leakage | 17 | 85% |
| minor_bridge_leakage | 2 | 10% |
| answer_leakage | 1 | 5% |

The main issue is not widespread answer leakage. Many responses avoid leakage, but their scaffolding quality is unstable. In particular, many micro-examples do not help the student understand the missing bridge.

## Thinking-Mode Comparison

| Condition | n | good | okay | bad | no leakage | minor leakage | answer/code leakage |
|---|---:|---:|---:|---:|---:|---:|---:|
| thinking enabled | 10 | 2 | 5 | 3 | 8 | 1 | 1 |
| thinking disabled | 10 | 4 | 4 | 2 | 9 | 1 | 0 |

In this small batch, `thinking disabled` received slightly better coach ratings: more good responses, fewer bad responses, and no answer leakage. This should not be overgeneralized, but it supports an engineering hypothesis:

> DeepSeek Flash thinking mode did not reliably improve Bridge Contract Tutor quality in this batch, and may increase abstraction, drift, or leakage risk.

## Qualitative Findings

### 1. Micro-examples often become temporary tasks

Several labels note that the AI gives a small example, but the student may treat it as a local task rather than a reasoning bridge.

Common problems:

- Asking the student to calculate a value, choose A/B, or fill a blank.
- Not stating what relation the example is meant to reveal.
- Not asking the student to generalize the observation into a transferable rule.

This means `micro_example` should not be treated as a binary feature. We should distinguish:

- Low-quality micro-example: the student completes a temporary fill-in task.
- High-quality bridge-oriented micro-example: the student observes a relation and abstracts a transferable rule.

### 2. Examples may be too abstract or too small to transfer

Some responses are directionally useful but hard to transfer. Coach notes mention that examples can be too small, too abstract, or insufficiently connected back to the original problem.

This suggests that tutor prompts should require a transfer bridge after examples:

> What relation in the original problem does this small example represent, and what should the student observe next time?

### 3. Some responses ask too many questions

In the trie-confirmation cases, the coach noted that a chain of questions can leave the student unsure what to answer first. For uncertain method-confirmation turns, a better pattern is:

1. Give one observation direction.
2. Ask one answerable question.
3. Let the student discover why the structure resembles the target method.

### 4. Some “why” questions need a brief explanation before guided transfer

For questions such as why 0/1 knapsack iterates capacity backwards, the coach noted that purely Socratic questioning is insufficient. The tutor should sometimes give a concise conceptual explanation, then guide transfer.

This means AIChat should not reduce all tutoring to questioning. For correctness, invariant, and ordering-dependency gaps, a short explanation plus a guided question may be more appropriate.

### 5. A small number of critical leakage cases remain

There were 3 leakage-related labels:

- `answer_leakage`: 1 response.
- `minor_bridge_leakage`: 2 responses.

Typical risks:

- The student only vaguely says “it seems like knapsack,” but the AI jumps to the key idea.
- The student has not built the state semantics, but the AI asks a question that presupposes the answer.
- The AI gives the solution and then asks the student to choose between options.

## Prompt Implications

The strongest prompt update is not a new module, but a micro-example rule:

```text
When using a micro-example, follow four steps:
1. State the bridge relation the example is meant to reveal.
2. Give a small example that remains close to the original problem.
3. Ask exactly one local, answerable question.
4. Ask the student to abstract the observation into a transferable rule.

Do not merely ask the student to complete a temporary fill-in, choice, or calculation task.
```

Two additional constraints should be added:

```text
If the student asks a “why / meaning / principle” question, give a brief conceptual explanation before asking a guided transfer question.
Keep one main question per response; avoid chains of multiple questions.
```

## Paper Positioning

This finding is worth including in the paper, but it should not become a new baseline. It fits best as:

1. a subcriterion in the response-quality rubric;
2. a qualitative error-analysis theme;
3. a design principle for bridge-aware scaffolding.

Suggested wording:

> A micro-example is considered bridge-oriented only when it explicitly frames the relation to be observed and prompts the learner to generalize the observation into a transferable rule.

## Next Step

1. Add the `bridge-oriented micro-example` rule to the Bridge Contract Tutor prompt.
2. Regenerate 10-20 offline responses before changing online AIChat.
3. Re-run the same one-card blind review process.
4. If the improvement is stable, then consider applying the rule to the online AIChat system prompt.
