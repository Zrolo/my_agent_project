# Bridge-first Prompt Sanity Check - 2026-05-11

This file records a small dev sanity check. It is not a paper experiment and should not be used as a headline metric.

## Question

The project raised a prompt-design risk:

```text
If the prompt only mentions some algorithms such as DP, binary search, LCA, or lazy propagation, will uncovered algorithms perform poorly?
```

The design principle was adjusted to:

```text
bridge-first, topic-second, focus-top-k
```

This means:

- use `primary_bridge_family` first to control the tutoring action;
- use `algorithm_topic` only as lightweight context;
- select `selected_focus_id` only from top-k focus candidates;
- treat concrete algorithm examples as regression boundaries, not as an exhaustive algorithm list.

## Prompt Patch

The patch only affects the offline research pipeline:

- `single_llm_structured` system prompt;
- offline Bridge Contract control message.

The online student AIChat path was not connected to this patch.

## Smoke Setup

- Seed file: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Cases: first 3 dev seeds
  - `cp_bridge_001`: tree path difference / LCA marking
  - `cp_bridge_002`: binary-search check semantics
  - `cp_bridge_003`: DP state semantics
- Tutor mode: `single_llm_structured`
- Pipeline: `tutor_only`
- Judge schema mode: `retrieval_augmented_compact_judge`
- Outputs:
  - `evals/aichat/ad_hoc_runs/bridge_first_single_llm_structured_smoke3_20260511.jsonl`
  - `evals/aichat/ad_hoc_runs/bridge_first_single_llm_structured_smoke3_20260511_v2.jsonl`

## Result

Engineering:

- 3/3 cases emitted rows successfully;
- `stage_errors={}`;
- `llm_call_count=1` for each row;
- the schema was not broken by the prompt patch.

Pedagogical safety:

- `cp_bridge_001` still pre-filled endpoint marks and asked the student to adjust marking positions, which is close to critical bridge leakage;
- `cp_bridge_002` still stated the feasibility meaning of `check(mid)` too explicitly;
- `cp_bridge_003` still came close to asking for the full knapsack state content.

## Interpretation

The sanity check suggests:

```text
bridge-first prompting is necessary, but not sufficient to prevent over-complete micro-examples.
```

It should not be interpreted as:

```text
abstract bridge prompting has solved leakage.
```

The safer conclusion is:

```text
Do not keep adding algorithm-specific prompt rules. Treat over-complete micro-examples as a Guard / Leakage Judge / coach-review issue.
```

## Follow-up

1. Keep `bridge-first, topic-second, focus-top-k` as the prompt design principle.
2. Avoid adding one-off algorithm-specific prompt rules for every failure.
3. Promote `cp_bridge_001`, `cp_bridge_002`, and `cp_bridge_003` to dev/regression cases.
4. Check the following in the 10-20 case dev ablation:
   - `enhanced_prompt_only`
   - `single_llm_structured`
   - `single_llm_structured + guard`
   - `bridge_contract_predicted`
   - `bridge_contract_predicted + guard`
5. Freeze prompts before the 50-case held-out experiment.
