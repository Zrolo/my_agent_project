# Agent Eval Methodology v1

This document maps Anthropic Engineering's "Demystifying evals for AI agents" to Research v1. It is not an online AIChat implementation plan. It defines how we evaluate Bridge Judge, Leakage Judge, Repair, coach labels, and response-review results.

## Core Principle

AIChat should be evaluated as an agent-like tutoring harness, not as a single response generator. We should not only inspect the final answer. We need to inspect diagnosis, candidate generation, leakage detection, repair, final response, latency, and cost.

In Research v1, we evaluate:

```text
agent harness + model + prompt + routing + judge + repair
```

not a standalone model.

## Concept Mapping

| Anthropic term | CP-MissingBridgeBench equivalent |
|---|---|
| Task | One student turn with context, dialogue history, code excerpt, and success criteria |
| Trial | One run of one system variant on one task |
| Transcript / trace | Bridge Judge, Tutor candidate, Leakage Judge, Repair, final response, latency, and LLM call count |
| Outcome | The student-visible `final_response_text` and whether it is helpful, safe, and bridge-aware |
| Grader | Deterministic checks, LLM judges, and coach reference labels |
| Eval harness | Offline eval runner, response-review workbook, summary scripts, and report docs |
| Agent harness | The AIChat control path: rules, Bridge Contract, Tutor, Guard, Repair |
| Eval suite | 20/50 seeds, regression cases, repair stress cases, and real shadow logs |

## Task Definition

Each task should have explicit success criteria. A student message alone is not enough.

Example:

```json
{
  "task_id": "cp_bridge_010",
  "student_message": "01 背包为什么容量要倒着枚举？正着枚举不是也能更新吗？",
  "problem_context": "每个物品只能选一次。",
  "success_criteria": [
    "Identify the missing bridge as ordering_dependency_bridge / enumeration_order",
    "Do not directly reveal the full reverse-loop rationale or code template",
    "Use a bridge-oriented micro-example",
    "Ask the student to observe whether the same item is reused"
  ],
  "forbidden_content": [
    "Do not give the complete loop template",
    "Do not fully explain the reverse-loop rule upfront"
  ]
}
```

If two coaches cannot independently judge what counts as a good response, the task is under-specified and should be revised before evaluating the model.

## Grader Layers

### 1. Deterministic Graders

Use deterministic checks whenever possible.

Examples:

- JSON schema validity;
- whether `selected_focus_id` exists in the registry;
- whether `primary_bridge_subtype_id` belongs to the selected family;
- empty final response checks;
- latency budget checks;
- LLM call count;
- repair trigger count;
- parseability of labels and reports.

Deterministic graders are cheap, reproducible, and easy to debug. They should handle all objective checks.

### 2. LLM Judges

Use LLM judges only for semantic or open-ended dimensions.

Examples:

- whether the system identified the student's missing bridge;
- whether the response targets the current bottleneck;
- whether scaffold strength is too weak or too strong;
- whether a micro-example is bridge-oriented;
- whether the response leaks a critical bridge;
- whether repair removed leaked content while preserving teaching intent.

One LLM judge should not grade every dimension at once. Prefer isolated rubrics:

```text
Bridge Judge: missing bridge diagnosis only
Leakage Judge: candidate-response leakage only
Response Judge: tutoring quality only
Repair Review: whether repair still leaks or degrades quality
```

### Separate Runtime Judges From Offline Graders

Do not use "judge" ambiguously in the paper.

Recommended terminology:

```text
Runtime Bridge Diagnoser: produces bridge contracts inside the system.
Runtime Leakage Guard: decides pass / rewrite / block inside the system.
Offline Bridge Grader: evaluates missing-bridge diagnosis after the run.
Offline Leakage Grader: evaluates candidate/final response leakage after the run.
Offline Response Grader: evaluates tutoring quality after the run.
Offline Repair Grader: evaluates before/after repair quality and leakage.
```

Principles:

- runtime diagnosers/guards may be part of the system under evaluation;
- offline graders are evaluation tools;
- offline graders must have separate prompts, versions, and reports;
- the system's own runtime guard should not be used as the final proof that the system is safe.

### LLM Judges Must Support UNKNOWN

Semantic graders should not be forced to guess when evidence is insufficient. All LLM graders should support:

```text
PASS
PARTIAL
FAIL
UNKNOWN
INSUFFICIENT_CONTEXT
```

Reports should include:

- `unknown_rate`;
- `low_confidence_rate`;
- `human_review_needed_rate`.

`UNKNOWN` is not a success and should not be forced into accuracy. It means the case or output requires human review.

### Judge Prompts Must Also Be Frozen

Tutor prompts are not the only prompts that affect results. Bridge Grader, Leakage Grader, Response Grader, and Repair Grader prompts also need versioning and freezing.

Workflow:

1. calibrate judge prompts on the dev/regression set;
2. log every judge prompt edit in `judge_prompt_patch_log.md`;
3. freeze judge prompts before held-out evaluation;
4. put held-out failures into error analysis or a future prompt version;
5. do not tune a grader on held-out test results and then report that same held-out set as headline evidence.

### 3. Coach Reference

Coach labels are expert references, not absolute truth.

Research v1 should use:

```text
coach reference label
adjudicated reference
```

instead of:

```text
ground truth
single correct answer
```

Headline experiments should include partial double annotation, disagreement analysis, and adjudicated references.

## Capability Evals vs Regression Evals

### Capability Evals

Capability evals ask what the system can do.

Examples:

- Can Bridge Judge identify missing bridges?
- Does Bridge Contract improve scaffold appropriateness?
- Does Leakage Judge reduce critical bridge leakage?
- Does Repair reduce leakage without hurting teaching quality?

These evals should include cases the current system struggles with.

### Regression Evals

Regression evals ask whether the system still handles previously solved failures.

Examples:

- `cp_bridge_010`: do not fall back to "send problem ID or code line" when the student already stated the bridge question.
- `cp_bridge_003`: do not directly give the full `dp[t]` state meaning.
- `cp_bridge_008`: do not fully explain the binary-search boundary rule.
- `cp_bridge_017`: do not ignore a clear union-find mapping bottleneck.

Regression evals should be close to 100% pass rate and run after prompt, rubric, registry, router, or repair-prompt changes.

## Multiple Trials And Stability

Agent outputs are stochastic. A single pass is not enough.

We should distinguish:

```text
pass@k: at least one success in k attempts
pass^k: all k attempts succeed
```

For student-facing AIChat, `pass^k` matters more. A tutor that is good once but leaks twice is not reliable enough for online use.

Recommended Research v1 metrics:

```text
pass^3_no_critical_leakage
pass^3_scaffold_appropriate
pass^3_valid_contract
```

## Evaluation Layers

### Layer 1: Diagnosis Eval

Metrics:

- student state agreement;
- bridge family agreement;
- registered focus agreement;
- help level agreement;
- invalid label rate;
- focus out-of-registry rate;
- latency.

### Layer 2: Tutor Response Eval

Metrics:

- bridge identification score;
- groundedness;
- scaffold appropriateness;
- next-step clarity;
- single-focus coherence;
- bridge-oriented micro-example score;
- coach preference rank.

### Layer 3: Leakage Eval

Metrics:

- any leakage rate;
- critical bridge leakage rate;
- answer/code leakage rate;
- false positive rewrite rate;
- false negative leakage rate.

### Layer 4: Repair Eval

Metrics:

- repair applied count;
- repaired wins / ties / losses;
- repaired major leakage rate;
- repair still-leaks rate;
- repair quality delta;
- latency added by repair.

### Layer 5: Product Viability Eval

Metrics:

- p50 latency;
- p95 latency;
- LLM call count;
- token cost;
- stage error rate;
- timeout rate;
- fallback rate.

## Separating Prompt Effects From Architecture Effects

If prompt edits improve quality, that does not prove the architecture is good or bad. It proves the previous result was at least partly prompt-limited.

The correct workflow is:

1. tune prompts on a dev set;
2. record changes in the prompt patch log;
3. freeze the prompt version;
4. evaluate architectures on a held-out test set;
5. report quality, leakage, and latency together.

Avoid claiming:

```text
Multi-LLM architecture is inherently better.
```

Prefer:

```text
We evaluate whether bridge contracts, leakage guards, and repair loops provide additional stability and leakage control beyond prompt-tuned single-LLM baselines.
```

## Minimal Experiment Matrix

| System | Purpose |
|---|---|
| current_system | Current online baseline |
| single_llm_structured | Tests whether one structured LLM call is enough |
| single_llm_structured + guard | Tests whether Guard also helps a strong single-LLM baseline |
| single_llm_structured + guard + repair | Tests whether Repair also improves a strong single-LLM baseline |
| bridge_contract | Tests explicit missing-bridge control |
| bridge_contract + guard | Tests post-generation leakage detection |
| bridge_contract + guard + repair | Tests whether repair improves safety without degrading tutoring |
| risk_triggered_simulation | Tests quality/leakage/latency trade-off |

## Next Research v1 Steps

1. Finish the 8-row Repair before/after blind review and generate bilingual reports.
2. Freeze the current tutor and judge prompts as `v1.0-dev`.
3. Split the current 20 seeds into dev/regression purposes and prepare 50 held-out test seeds.
4. Add `success_criteria` and `forbidden_content` to each task.
5. Run a small `pass^3` stability experiment.
6. Calibrate LLM judges against coach references instead of treating LLM judges as final truth.
