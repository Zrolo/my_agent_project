# Real AIChat Log Screening 20260512

This note records a read-only screening pass over real student AIChat logs on 2026-05-12. The goal is to build a Research v1 real-log candidate pool. This screening does not create gold labels and does not directly enter the 50-case held-out headline result.

## Source

Online service directory:

```text
/opt/noi-agent
```

Read-only table:

```text
aichat_messages
```

No online database rows were modified, and no files were written to the server. The screening outputs were saved locally as private candidate files containing redacted turns. They require manual review before entering research data.

## Raw Counts

| Metric | Count |
|---|---:|
| Total AIChat messages | 1426 |
| Student messages | 713 |
| AI replies | 713 |
| Students | 14 |
| Sessions | 106 |
| Problems | 38 |
| Date range | 2026-04-23 to 2026-05-12 |
| Student messages with problem context | 703 |
| Student messages with student code | 136 |
| Sessions with at least 4 messages | 82 |

## Screening Method

Each student turn was paired with the next AI reply. The screening script scored each turn with positive signals such as:

- next AI reply exists;
- problem statement or problem reference exists;
- student code or debug signal exists;
- explicit confusion, bottleneck, or error statement;
- algorithm / implementation / debugging keywords;
- multi-turn context;
- enough text for annotation.

Filtering or down-weighting signals included:

- uninformative short replies such as "好的", "懂了", or "继续";
- missing next AI reply;
- obvious external copy noise or non-competitive-programming content;
- broad questions requiring manual judgment.

This screening used regular expressions and heuristics only. It did not use an LLM to create gold labels.

## Candidate Pool

| Stage | Count |
|---|---:|
| Raw student turns | 713 |
| Turns above candidate threshold | 672 |
| Diversity-constrained candidate pool | 70 |
| Recommended for priority review | 45 |
| Backup | 21 |
| Excluded | 4 |

Features of the 70-turn candidate pool:

| Metric | Count |
|---|---:|
| Contains student code | 29 |
| Contains problem context | 68 |
| Comes from multi-turn sessions | 59 |

Primary category distribution for the 45 recommended samples:

| Category | Count |
|---|---:|
| graph_tree_modeling | 13 |
| debugging_wa_tle_re | 12 |
| implementation_boundary | 8 |
| dp_state_transition | 4 |
| binary_search_check | 4 |
| data_structure_semantics | 2 |
| general_cp_question | 2 |

Among the recommended samples, 26 contain student code and 38 come from multi-turn sessions.

## Privacy Handling

The private candidate files apply first-pass automatic redaction:

- `student_id` is hashed;
- `session_id` is hashed;
- email addresses, phone numbers, non-Luogu URLs, and obvious contact handles are replaced by placeholders;
- raw account names, real names, and passwords are not exported.

This is only automatic redaction, not final anonymization. Before paper use or external coach sharing, manually inspect:

- whether students self-disclose names, schools, or contact information;
- whether code comments contain personal information;
- whether copied screenshots / external platform ads are mixed in;
- whether the turn contains sensitive classroom context.

## Research Use

These real logs are suitable for three uses:

1. **Dev / regression cases**: add realistic short replies, code-debug turns, and multi-turn contexts.
2. **Held-out candidate pool**: after prompt / grader freeze, select a subset for coach review and possible real-log held-out use.
3. **Paper qualitative examples**: use only a few manually anonymized, coach-approved, pedagogically meaningful cases.

Do not:

- treat them as gold labels without coach review;
- put them into the paper without manual anonymization;
- tune prompts on these logs and then reuse the same cases as headline held-out results;
- merge real logs and synthetic 50-case results into one metric without stratified reporting.

## Next Step

The recommended next step is coach review of the 45 priority samples:

- keep 20-30 as the real-log candidate set;
- mark whether each case is safe for public display;
- add missing bridge, forbidden content, and success criteria;
- confirm code presence, long context, and short-reply realism;
- decide which cases enter dev/regression and which remain held-out candidates.

In the paper, these should be described as:

```text
real AIChat log candidates, coach-reviewed and anonymized before use
```

not as a gold dataset directly.
