# Real Student Language Style Guide v1

This document records language-style observations from real online AIChat student questions. It is used when writing synthetic-but-grounded cases, `recent_dialogue`, review-workbook context, and paper data descriptions.

This is not a public release of raw student logs. Real logs are used only for local style induction and candidate screening; public materials should use redacted, rewritten, or synthetic examples.

## Usage Boundary

- Use for: generating held-out `student_message`, `recent_dialogue`, code-snippet scenes, and coach review context.
- Do not use for: publishing verbatim student logs, publishing historical AI replies, or claiming synthetic questions are real student utterances.
- Recommended paper wording: `synthetic-but-grounded student questions inspired by anonymized real AIChat usage patterns`.

## Common Real-Student Style Features

Real student turns usually look unlike annotation forms or polished lesson plans:

1. Very short, assuming the AI already knows the context
   Examples: `这题为什么要二分？`, `然后怎么处理强连通分量之间的边？`

2. Missing subject or full background
   Examples: `这里从哪转？`, `mid 满足改哪边？`, `这个为什么对？`

3. Frequent informal question words
   Examples: `为什么`, `怎么`, `到底`, `该不该`, `从哪`, `能不能`.

4. Half-formed solution ideas
   Example: `我第一反应是树的直径，但为什么能用我不知道。`

5. Code pasted with little explanation
   Students may paste a loop, `check()`, or segment-tree `update()` and only ask: `这里为什么错？`

6. Uncertainty rather than abstract categories
   Examples: `样例能看懂，但自己不会推。`, `我总是写反。`

7. Longer contexts usually become specific through turns
   They should not start as a polished three-sentence self-diagnosis. A more realistic pattern is: “I read the problem” → AI asks a light question → student narrows to a concrete stuck point.

## Invalid Patterns

Avoid these in `student_message` or `recent_dialogue`:

- `学生知道可能要记录中间结果，但说不清...`
- `缺少把题面对象和状态语义对应起来的关系。`
- `我想获得可迁移的概念关系。`
- `请通过一个观察问题让我理解当前关系。`
- `我当前卡在状态表示桥。`
- `我希望你不要泄露 critical bridge。`
- Every item says: `这题状态到底该记录什么？`
- Every `recent_dialogue` starts with: `题意基本能复述，但还没有完整做法。`

These sound like an annotator, paper author, or system prompt, not a real student.

## Student-Message Length Distribution

The 50-case held-out draft uses this distribution:

| Length bucket | Count | Target style |
| --- | ---: | --- |
| short | 20 | one short question, often underspecified |
| medium_short | 15 | one question with light context |
| medium_long | 10 | current idea plus concrete stuck point |
| long | 5 | multi-sentence description, often after repeated confusion |

Short questions are not low-quality by default. In online AIChat, students often avoid long explanations; short turns can still carry diagnostic value.

## Common Short Question Templates

These are style references, not fixed templates.

| Bridge type | More student-like short questions |
| --- | --- |
| State / representation semantics | `这个状态怎么想？`, `dp 这一格是啥意思？`, `数组里到底存什么？` |
| Transition / recurrence source | `这里从哪转来？`, `这一步怎么递推？`, `当前格怎么算？` |
| Predicate / check | `这题为什么要二分？`, `check 该判什么？`, `true 表示可行吗？` |
| Boundary / order | `mid 满足改哪边？`, `最后取 l 还是 r？`, `循环为啥倒着来？` |
| Modeling / object relation | `这题怎么建模？`, `哪些东西当点？`, `这个限制怎么连边？` |
| Contribution / prefix / difference | `贡献加到哪里？`, `这里怎么打标记？`, `差分减在哪？` |
| Data-structure semantics | `这个结构维护什么？`, `query 查出来是啥？`, `lazy 到底表示啥？` |
| Correctness / invariant | `贪心为什么对？`, `会不会有反例？`, `排序依据凭什么？` |
| Implementation boundary | `初始化怎么设？`, `下标从几开始？`, `int 会不会爆？` |
| Debugging evidence | `WA 怎么找反例？`, `样例过了还错。`, `该打印哪个变量？` |
| Direct answer/code request | `直接给代码行吗？`, `完整题解发我。`, `能直接告诉答案吗？` |

## `recent_dialogue` Writing

The goal of `recent_dialogue` is to simulate one or two prior natural turns. It should not complete the diagnosis for the student.

### Short Context

Recommended: around 3 lines.

```text
学生：这题我读完了，但还没开始写。
AI：先别急着写代码，告诉我你现在不确定哪里。
学生：check 该判什么？
```

### Long Context

Recommended: around 5 lines.

```text
学生：我看了题面，样例大概能跟。
AI：你先说已经想到哪一步，我再接着问。
学生：我有个贪心想法，但怕是假的。
AI：那先抓一个最不确定的点，不用一次讲完整题解。
学生：样例看起来对，可我不知道怎么证明这个策略一定对。
```

### Avoid

```text
学生：我知道可能要记录中间结果，但说不清一个格子或状态里的量表示什么。
AI：请指出当前最卡住的一步。
学生：我缺少把题面对象、已处理范围和状态值语义对应起来的表示关系。
```

This is too annotation-like, and the final line directly restates the gold missing bridge.

## Code Scenes

Real students often paste code without a full explanation. A generated code scene can look like:

```text
bool check(long long x) {
    long long used = 0;
    // 这里不知道 true 应该表示 x 可行还是不可行
    return used <= limit;
}
```

The student question can be:

```text
这里 check 返回 true 到底表示啥？
```

The code should expose the student’s stuck point, but it should not encode the official solution.

## Relationship To Paper Data

This guide supports three research goals:

1. Reduce template artifacts in synthetic cases.
2. Make held-out cases closer to real online AIChat use.
3. Ensure baselines face natural student questions rather than prompts engineered for one method.

Recommended paper wording:

> Student turns were synthetic-but-grounded: they were generated from real problem statements and target bridge labels, while their surface style was guided by anonymized real AIChat usage patterns. Historical AI replies were not used as generation inputs.

## Generator Checklist

Before generating or modifying held-out cases:

- `student_message` should not repeat within the same bucket.
- Avoid meta-language such as `学生知道`, `缺少把`, `可迁移`, `当前关系`, or `bridge`.
- The final line of `recent_dialogue` should be a natural student stuck point, not a gold label.
- Long contexts should become specific through turns, not start as a complete self-diagnosis.
- Some cases should include pasted code or buggy-code contexts.
- Synthetic questions must not be claimed as verbatim real student utterances.
