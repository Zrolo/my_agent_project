# Research v1 Scope Lock

Status: active scope guard for the `codex/bridge-research-annotation` branch.

This document prevents Research v1 from drifting into an unbounded product rewrite. It should be updated only when the research scope changes deliberately.

## Paper Direction

Research v1 supports the following paper direction:

```text
CP-MissingBridgeBench:
面向算法竞赛 LLM 辅导的逐轮缺失桥梁诊断与关键桥梁泄露评测框架
```

The core claim is not "we built a complete online multi-agent tutor." The core claim is:

```text
Competitive-programming tutoring turns can be annotated and evaluated through
missing bridges, scaffold strength, help form, and critical bridge leakage.
```

## In Scope

Research v1 includes:

- a CP-specific missing bridge schema;
- coach-facing seed labeling workflow;
- annotation reliability protocol;
- compact runtime bridge contract;
- Bridge Judge diagnosis experiments;
- Bridge Contract Tutor response generation experiments;
- Leakage Judge detection experiments;
- Repair Generator offline experiments;
- current_system vs single_llm_structured vs bridge_contract ablations;
- response blind review workflow;
- risk-triggered routing simulation;
- latency, LLM call count, and stage error reporting;
- Chinese and English research reports.

## Out Of Scope

Research v1 explicitly excludes:

- online full multi-judge execution on every student turn;
- automatic system prompt rewriting during chat;
- Repair modifying prompts, rubrics, registries, or policies;
- automatic weekly prompt deployment without human approval;
- long-term student memory or student model layer;
- full NOI/OI algorithm ontology coverage;
- using control theory as the paper's primary novelty;
- treating single-coach labels as absolute ground truth;
- claiming long-term contest-score improvement from small pilot data.

## Online AIChat Boundary

Current online AIChat remains the baseline unless a later active-mode rollout is explicitly approved.

Research v1 tools may run:

- offline;
- in shadow mode;
- in local smoke tests;
- in exported review workbooks.

They must not silently change student-visible replies in production.

## Variable Timescales

### Slow Variables

Slow variables are system rules and must not change inside a student conversation:

- system prompt;
- policy prompt;
- Bridge Judge prompt;
- Leakage Judge prompt;
- Repair prompt;
- rubric;
- bridge schema;
- focus registry;
- algorithm topic registry;
- risk routing policy;
- deterministic fallback policy.

Slow-variable updates require review, regression cases, smoke tests, and human approval.

### Mid Variables

Mid variables change per turn:

- runtime bridge contract;
- missing bridge summary;
- allowed scaffold level;
- help forms;
- must-not-reveal list;
- leakage risk;
- next student action.

They guide a single tutor response without rewriting global rules.

### Fast Variables

Fast variables exist only inside one turn:

- candidate response;
- leakage judge result;
- repair response;
- final response;
- stage latency;
- final response source.

Repair may change the final response for this turn only.

## Patch Rule

Every prompt, rubric, registry, router, fallback, or repair-policy change should have:

- a failure case id or review evidence;
- the affected layer;
- before metrics or qualitative baseline;
- after metrics or smoke result;
- regression case ids;
- human approval.

Do not bundle many layers into one patch unless the experiment is explicitly testing a combined change.

## Data Language

Use careful wording:

- `single_coach_reference`: one coach's expert label.
- `double_annotated_reference`: two independent coach labels exist.
- `adjudicated_gold`: disagreements have been reviewed and resolved.

Do not call single-coach labels "the unique correct answer."

## Promotion Path

The only approved path from research to product is:

```text
offline eval -> shadow mode -> risk-triggered active mode
```

Full multi-judge every turn is a comparison condition, not the default online strategy.
