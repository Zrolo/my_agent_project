# Response Review Problem Statement And Student-message Length Policy v1

Date: 2026-05-13

## Conclusion

All future AIChat response-review workbooks must include real problem-source metadata and `problem_statement`, shown in Chinese as `原题题面/必要题面`. Providing only `problem_context` is not sufficient because coaches need the task statement and source before judging the student's local bridge and whether the AI reveals a relation not already given by the task.

The 50-case held-out dataset should also track student-message length distribution so the benchmark is not dominated by very short student questions.

## Review Workbook Fields

From this policy onward, the source columns in response-review workbooks should include at least:

| Field | Chinese header | Purpose |
| --- | --- | --- |
| `problem_ref` | 题目编号 | Problem or internal sample id |
| `problem_source_platform` | 题目来源平台 | Real problem-source platform, such as Luogu, Codeforces, AtCoder, NOI/NOIP, or ICPC |
| `problem_source_id` | 平台题号 | Platform problem id or contest problem id |
| `problem_source_url` | 原题链接 | Public source link; must be an `http://` or `https://` URL |
| `problem_statement` | 原题题面/必要题面 | Task information needed for coaches to judge problem meaning, constraints, input/output relations, and the local bottleneck |
| `problem_statement_public_summary` | 公开题面摘要 | Rewritten public summary for artifacts that should not copy long copyrighted statements |
| `problem_statement_rights_note` | 题面版权/使用说明 | Notes the boundary between local review, public release, and source citation |
| `problem_statement_access_level` | 题面访问级别 | Marks statement visibility; see allowed values below |
| `student_message` | 学生当前问题 | The student's current turn |
| `student_message_length_bucket` | 学生问题长度类型 | Marks whether the student question is short, medium-short, medium-long, or long |
| `problem_context` | 题目/上下文 | Compressed context, known algorithm domain, or key task conditions; not a replacement for the statement |
| `recent_dialogue` | 近期对话 | Shows whether the student already stated the bridge |
| `context_ai_reply` | 上下文 AI 回复 | Previous assistant reply, used to judge continuity |
| `response_text` | AI 回复（要评分） | The target response to score |

## Real Sources And Statement Granularity

`problem_statement` does not always need to be the public platform's full original statement, but it must be sufficient for coaches to judge:

- what the task asks for;
- the input/output or object relations;
- important constraints;
- how the student question relates to the task;
- whether a relation in the AI response was already explicit in the task statement.

If the original statement creates copyright or public-release risk, the public research artifact can use a rewritten necessary statement. The local coach-review workbook, however, must provide enough task information for reliable scoring. Public papers or released artifacts should preferably keep `problem_source_url`, `problem_statement_public_summary`, and necessary rewritten context rather than copying long platform statements.

Allowed `problem_statement_access_level` values:

| access level | Meaning |
| --- | --- |
| `local_review_only` | Full or near-full statement is only used in the local coach-review workbook, not in public artifacts |
| `public_summary_only` | Public artifacts keep only a rewritten summary plus the original source link |
| `open_license` | The statement can be reused under a known license |
| `original_link_only` | Public artifacts keep only the original source link, not the statement text |

## Student-message Length Buckets

Buckets are computed from the student message after removing whitespace:

| bucket | Length | Meaning |
| --- | ---: | --- |
| `short` | 1-30 chars | A very short question or local judgment |
| `medium_short` | 31-70 chars | One or two sentences, with limited detail |
| `medium_long` | 71-140 chars | Includes an attempt, error pattern, or local reasoning |
| `long` | 141+ chars | Multi-sentence description, possibly with code, counterexample, or a fuller attempt |

Recommended 50-case main-experiment distribution:

| bucket | Ratio | 50-case count |
| --- | ---: | ---: |
| `short` | 40% | 20 |
| `medium_short` | 30% | 15 |
| `medium_long` | 20% | 10 |
| `long` | 10% | 5 |

This does not mean longer student messages are pedagogically better. It ensures the benchmark covers different student communication styles. Real students often send short replies, so `short` should be the largest bucket; but a formal benchmark should not test only short questions because code, counterexamples, and complex context require longer turns.

## Impact On The Existing 50-case Set

Before formal held-out evaluation:

1. Add `problem_source_platform`, `problem_source_id`, and `problem_source_url` to all 50 cases;
2. add `problem_statement`, `problem_statement_public_summary`, `problem_statement_rights_note`, and `problem_statement_access_level` to all 50 cases;
3. rerun dataset validation and inspect source distribution, statement access levels, and `student_message_length_distribution`;
4. adjust or add cases if the 20/15/10/5 distribution is not met;
5. re-export the Chinese review workbook with problem sources and statements;
6. instruct coaches to read the source and statement before the student question and AI response.

## Boundary

This policy does not require showing the problem statement in the online student AIChat, nor does it require feeding the full statement into every live turn. It governs offline research review and held-out benchmarking so coaches have enough context for reliable scoring.
