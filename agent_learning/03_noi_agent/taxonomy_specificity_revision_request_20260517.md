# Taxonomy Specificity Revision Request (2026-05-17)

## Purpose

This memo is for an external/local AI reviewer that cannot access clickable local file links.

Please judge which project documents should be revised so that the human review / error taxonomy is framed as:

```text
cognitive bridge family + leakage mechanism + surface anchor
```

rather than as a small list of concrete algorithm scenes such as DP state definition, recurrence, check condition, binary-search boundary, tree difference, lazy propagation, fully worked micro-example, or local code completion.

The goal is not to add new experiments or change the online system. The goal is to decide how to revise paper wording, review instructions, and taxonomy documentation so reviewers do not interpret the benchmark as overfitted to a few hand-picked algorithm patterns.

## Recommended Framing

The current project already contains an abstract bridge taxonomy in several places. The main issue is that some paper-facing and reviewer-facing documents still foreground concrete examples.

Recommended top-level framing:

| Layer | Meaning | Examples |
| --- | --- | --- |
| Cognitive bridge family | What kind of learning step the student is missing | representation semantics, modeling relation, transition/action mapping, predicate semantics, dependency/order, aggregation, correctness/invariant, complexity, implementation, debugging evidence, reflection |
| Leakage mechanism | How the tutor crosses the line | direct bridge completion, answer-slot compression, worked-trace completion, local implementation completion, proof completion, decision completion, debugging diagnosis completion, over-constrained scaffold |
| Surface anchor | The concrete algorithm or local instance | DP state, binary-search check, lazy propagation, tree difference, LCA marking, local code, greedy proof, geometry predicate, search pruning |

Suggested paper sentence:

```text
The bridge families are cognitive tutoring categories, not an algorithm list. Concrete algorithm patterns such as DP state definitions, binary-search checks, lazy propagation, or tree-difference marking are treated as surface anchors instantiating broader bridge families and leakage mechanisms.
```

Chinese version:

```text
bridge family 是学生学习过程中的认知桥类型，不是算法清单。DP 状态定义、二分 check、lazy 标记、树上差分等只是这些认知桥和泄露机制的具体表层实例。
```

## P0: Highest Priority Revisions

These are most likely to affect paper interpretation.

### 1. `docs/research/evaluation_protocol_v3.zh.md`

Approximate lines: 79-87.

Current issue:

The `Case memo` section lists major/answer leakage categories as:

- over-complete micro-example
- direct state/transition/check/boundary completion
- local code leakage
- context mismatch
- unclear rubric boundary

Risk:

This looks like the project’s error taxonomy only covers DP / check / boundary / local-code cases.

Recommended revision:

Replace or augment the list with abstract leakage mechanisms:

- direct bridge completion
- answer-slot compression
- worked-trace completion
- local implementation completion
- proof / invariant completion
- decision-rule completion
- debugging diagnosis completion
- modeling-plan completion
- over-constrained scaffold
- context mismatch
- unclear case-specific rubric boundary

Keep state/transition/check/boundary/local code as examples under surface anchors, not as the primary taxonomy.

### 2. `docs/research/evaluation_protocol_v3.md`

Approximate lines: 79-87.

Same issue and same recommended revision as the Chinese file above.

### 3. `docs/research/response_review_rubric_v3.zh.md`

Approximate lines: 46-61.

Current issue:

The rubric defines `critical_leakage_label + bridge_reveal_justification` well, but does not explicitly say that leakage mechanisms are abstract and algorithm-independent.

Risk:

Readers may infer the leakage taxonomy from scattered examples elsewhere, which over-emphasize DP/check/lazy/code.

Recommended revision:

Add a subsection after “泄露与透露正当性”:

```text
## 泄露机制不是算法类别

泄露标签判断的是 AI 是否替学生完成当前 missing bridge，而不是这道题属于哪种算法。
常见泄露机制包括：直接补完关键桥、把关键桥压缩成答案槽位、完整推演 micro-example、补完局部实现、补完证明/不变量、直接给决策规则、直接诊断 bug 根因、过度约束学生下一步。
DP/check/lazy/差分/局部代码只是这些机制的 surface anchors。
```

### 4. `docs/research/response_review_rubric_v3.md`

Approximate lines: 46-61.

Same issue and same recommended revision as the Chinese file above.

### 5. `docs/research/dialogue_state_v3_human_review_result_packet_20260517.zh.md`

Approximate lines: 100-122.

Current issue:

The packet reports context slices and main-scaffold results, but does not explicitly state taxonomy scope.

Risk:

A reviewer may interpret the 50-case set as an arbitrary collection of DP/check/boundary/code cases rather than sampled cognitive bridge coverage.

Recommended revision:

Add a “Taxonomy Scope” section before or after the slice analysis:

```text
本 50-case dialogue-state v3 不是算法题型清单，而是按 cognitive bridge family 采样的开放式辅导回复评测。`state_representation_semantics`、`predicate_check_semantics`、`boundary_update_order` 等 bucket 是 surface anchors；论文主张应上提为 representation semantics、predicate/decision semantics、dependency/order control、aggregation/contribution accounting、correctness/invariant reasoning、implementation/debugging evidence 等学习卡点类型。
```

Also mention coverage gaps:

```text
The current set under-samples math property, counting/inclusion-exclusion, geometry predicates, search pruning/deduplication, and reflection/transfer. These should be reported as coverage limitations or future extensions.
```

### 6. `docs/research/dialogue_state_v3_human_review_result_packet_20260517.md`

Approximate lines: 98-120.

Same issue and same recommended revision as the Chinese file above.

### 7. `docs/research/paper_results_interpretation_guardrails_20260517.zh.md`

Current issue:

The document already handles Guard-only and Repair causal wording, but does not yet include the taxonomy-specificity risk.

Recommended revision:

Add a section:

```text
## Taxonomy / Coverage Guardrail

不要写成：本 benchmark 只评估 DP 状态、转移、check、边界、lazy、差分和局部代码。

可以写成：这些是 high-risk surface anchors；主 taxonomy 是学生学习过程中的 cognitive bridge families 和 tutor leakage mechanisms。

必须报告：当前 50-case set 覆盖了 representation、transition、predicate、ordering、modeling、aggregation、data-structure operation、correctness、implementation、debugging、policy request 等 family，但对 math/counting/geometry/search/reflection 的覆盖仍有限。
```

### 8. `docs/research/paper_results_interpretation_guardrails_20260517.md`

Same issue and same recommended revision as the Chinese file above.

## P1: Reviewer-Facing Tooling And Instructions

These affect human reviewer mental models.

### 9. `docs/research/coach_blind_review_instructions_v1.zh.md`

Approximate lines: 237-255.

Current issue:

The “common boundary cases” mostly use lazy, `dp[j]`, worked examples, and multiple-choice examples.

Risk:

Coaches may learn that leakage means mainly DP/lazy/check leakage, not broader bridge completion.

Recommended revision:

Add a preface:

```text
以下例子只是 surface anchors，不是穷尽 taxonomy。判断泄露时先看是否替学生完成当前 missing bridge，再看具体算法实例。
```

Add additional examples for:

- proof/invariant completion
- debugging diagnosis completion
- modeling relation completion
- complexity bottleneck completion
- search pruning/deduplication completion

### 10. `docs/research/coach_blind_review_instructions_v1.md`

Same issue and same recommended revision as the Chinese file above.

### 11. `evals/aichat/export_coach_response_review_workbook_xlsx.py`

Approximate lines: 495-548.

Current issue:

The workbook instruction sheet examples heavily mention:

- “状态怎么设”
- DP
- lazy
- check(mid)
- dp state definition
- full recurrence

Risk:

This is reviewer-facing and may bias human review toward a narrow algorithm-specific view.

Recommended revision:

Keep concrete examples, but rewrite them as:

```text
抽象类别 + surface anchor example
```

For example:

- `representation semantics`: DP state, node summary, mask meaning
- `predicate / decision semantics`: check(mid), if/while, relax condition
- `correctness / invariant`: greedy exchange, settled candidate, monotonic elimination
- `debugging evidence`: minimal failing case, suspicious intermediate variable
- `modeling relation`: object-to-edge/state/constraint mapping
- `complexity bridge`: bottleneck operation and data-range feasibility

Also add an explicit line:

```text
这些例子不是完整 taxonomy；评审时以 case-specific rubric 的 missing bridge 和 forbidden content 为准。
```

### 12. `evals/aichat/coach_labeling_schema_v2.py`

Approximate lines: 178-186, `POLICY_RISK_TYPES`.

Current issue:

`critical_bridge_completion_risk` is described as direct answers completing “state, transition, check, or formula”.

Risk:

The policy risk definition sounds narrower than the actual missing-bridge idea.

Recommended revision:

Change description to something like:

```text
关键桥补全风险：直接回答会补完学生当前缺失的认知桥，例如表示语义、关系建模、转移/动作映射、判定语义、更新顺序、贡献汇总、正确性理由、调试定位或局部实现。
```

### 13. `evals/aichat/coach_labeling_schema_v2.py`

Approximate lines: 357-370, `BRIDGE_SPECIFIC_FORBIDDEN_CONTENT`.

Current issue:

The forbidden-content labels are useful and mostly abstract, but still emphasize formula/state/boundary.

Question for reviewer:

Should we add any of the following labels, or simply document them as leakage mechanisms?

Candidate additions:

- `no_full_proof_completion`
- `no_direct_debug_diagnosis`
- `no_exact_decision_rule`
- `no_overconstrained_answer_slot`
- `no_exact_complexity_bottleneck_solution`

Recommended conservative action:

Do not expand dropdowns unless needed for annotation. Instead, add documentation mapping these mechanisms to existing labels:

- proof completion -> `no_full_invariant_proof`
- debug diagnosis -> `no_complete_local_condition` or a new `no_direct_debug_diagnosis`
- decision rule -> `no_exact_check_condition` / `no_exact_boundary_update_rule` / `no_exact_guard_condition`
- answer-slot compression -> `no_fully_worked_micro_trace` plus judge/rubric instruction

## P2: Data Generation And Experiment Description

These may not require code changes, but the paper should explain their scope.

### 14. `evals/aichat/generate_luogu_heldout_v2_50.py`

Approximate lines: 40-66, `BRIDGE_BUCKET_ORDER` and `DEFAULT_QUOTAS`.

Current issue:

The 50-case generation quota is expressed as 11 concrete buckets:

- state representation
- transition recurrence
- predicate check
- boundary update
- modeling relation
- aggregation contribution
- data structure operation
- correctness invariant
- implementation boundary
- debugging evidence
- policy request

Risk:

This can look like a fixed narrow taxonomy.

Recommended decision:

Probably do not modify the generator now. Instead, document that these are sampled bridge-family anchors for Research v1, not a complete taxonomy of all programming-learning situations.

### 15. `evals/aichat/generate_luogu_heldout_v2_50.py`

Approximate lines: 980-994, `_code_excerpt`.

Current issue:

The code snippets are concrete:

- binary-search boundary
- segment-tree lazy
- implementation indexing
- debugging WA loop
- check predicate
- DP grid
- recurrence
- difference array
- greedy choice
- modeling relation

Recommended decision:

Do not necessarily change the snippets. Add documentation saying they are surface-anchor instantiations used to create realistic CP tutoring contexts.

### 16. `evals/aichat/generate_dialogue_state_v3_50.py`

Approximate lines: 317-342, bucket-to-sheet mapping.

Current issue:

The generated workbook sheet names foreground concrete bridge buckets.

Recommended decision:

Probably keep sheet names, but result packet / paper should include an abstraction mapping:

```text
bucket -> cognitive bridge family -> surface anchor examples
```

### 17. `docs/research/repair_same_candidate_stress_protocol_20260517.zh.md`

Approximate lines: 16-29.

Current issue:

The stress protocol reports coverage only by existing bridge buckets.

Risk:

Readers may interpret the Repair stress test as covering all leakage scenarios.

Recommended revision:

Add:

```text
This is a high-risk CP tutoring stress set drawn from existing repair-triggered candidates. It is not a full coverage test of all learning situations.
```

Add coverage gaps:

- math property / modular invariant
- counting partition / inclusion-exclusion
- geometry predicate relation
- search pruning / deduplication
- reflection / transfer
- complex debugging diagnosis

### 18. `docs/research/repair_same_candidate_stress_protocol_20260517.md`

Same issue and same recommended revision as the Chinese file above.

## P3: Historical Reports

These are lower priority. They can remain as historical memos if newer paper-facing docs explain the abstraction.

### 19. `evals/aichat/ad_hoc_runs/*/*analysis*.md`

Current issue:

Many historical analysis files repeatedly mention:

- fully worked micro-example
- state/transition/check
- local code

Recommended decision:

Do not batch rewrite historical run artifacts unless needed. Add a note in paper/result packet:

```text
Historical error memos used concrete surface-anchor labels for quick diagnosis; paper analysis maps these to abstract leakage mechanisms.
```

### 20. `docs/research/dev_ablation_bridge_contract_cases_20260511.zh.md`

Current issue:

Early dev cases are heavily DP/binary/lazy oriented.

Recommended decision:

Keep as dev seed record, but do not use it as final coverage evidence.

### 21. `docs/research/repair_stress_v1_all20_report_20260511.zh.md`

### 22. `docs/research/repair_stress_v1_all20_report_20260511.md`

Current issue:

Early repair stress cases are high-leakage concrete algorithm cases.

Recommended decision:

Keep as adversarial high-risk repair stress evidence. Do not describe it as full learning-situation coverage.

## Existing Evidence That Supports Abstraction

The reviewer should not conclude that the project lacks abstraction. These files already support the desired framing:

### A. `docs/research/bridge_taxonomy_coverage_review_v1.md`

Important lines: 1-33, 73-109.

Key message:

```text
Do not enumerate concrete algorithms. Keep abstract bridge shapes and record concrete algorithm context separately.
```

It already recommends:

- `algorithm_topic`
- `bridge_subtype`
- `forbidden_content`

as separate layers.

### B. `docs/research/bridge_taxonomy_abstraction_policy_v1.md`

Important lines: 1-80.

Key message:

```text
Do not turn bridge subtypes into an algorithm list.
```

It explicitly says algorithm information should live in topic/focus/notes, while bridge labels should capture transferable reasoning relations.

### C. `docs/common/aichat_bridge_judge_v1_system_prompt.md`

Important lines: 63-82.

The Bridge Judge prompt already lists broad missing bridge families:

- goal constraint
- modeling
- method selection
- representation/state
- transition/recurrence
- predicate/condition
- ordering/dependency
- aggregation/contribution
- data-structure operation
- correctness/invariant
- complexity/optimization
- implementation/boundary
- debugging/evidence
- reflection/transfer
- unknown/not applicable

### D. `evals/aichat/coach_labeling_schema_v2.py`

Important lines: 163-176 and 207-220.

The schema already covers broad student states and bridge families, including:

- goal comprehension
- modeling/representation
- method selection/application
- misconception/wrong strategy
- correctness reasoning
- complexity optimization
- implementation translation
- debugging evidence/localization
- reflection transfer

This is strong evidence that the project is not inherently DP/check/lazy-specific. The main task is to foreground this abstraction in paper-facing docs and reviewer-facing instructions.

## Suggested External AI Task

Please judge the P0/P1 items above and propose exact wording changes.

Constraints:

1. Do not add new experiments.
2. Do not modify online AIChat behavior.
3. Do not expand annotation dropdowns unless clearly necessary.
4. Prefer documentation and wording changes that map existing concrete examples to abstract categories.
5. Preserve historical reports as historical memos unless they are directly paper-facing.

Primary decision:

```text
Which P0/P1 documents must be revised before paper writing, and what exact wording should replace the currently concrete algorithm-specific taxonomy language?
```
