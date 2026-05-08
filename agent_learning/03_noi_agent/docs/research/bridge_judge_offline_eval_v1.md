# Bridge Judge Offline Evaluation v1

## Goal

Build an offline research loop before changing AIChat production behavior.

The goal is to test whether a schema-based Bridge Judge can outperform the current keyword/rule matching approach on:

- identifying the student's problem-solving state;
- identifying the student's missing bridge;
- distinguishing bridge diagnosis from help-seeking behavior;
- handling unknown or not-yet-registered bridges;
- reducing bridge leakage when paired with a tutor response;
- providing structured learning evidence for paper analysis.

## Non-Goals

- Do not replace AIChat routing in the first phase.
- Do not rely on student-facing logs as the only evidence.
- Do not export full chat content by default.
- Do not claim multi-LLM is better before comparing it to single-LLM structured prompting.

## Systems to Compare

| System | Description | Purpose |
| --- | --- | --- |
| `rule_matching_current` | Current keyword/rule route logic. | Measures current project baseline. |
| `single_llm_structured` | One LLM outputs bridge schema and student reply in one call. | Tests whether one model is enough. |
| `bridge_judge_only` | Lightweight LLM outputs only bridge schema. | Tests bridge identification quality. |
| `bridge_judge_plus_tutor` | Bridge Judge output conditions the tutor reply. | Tests controlled scaffolding. |
| `bridge_judge_plus_tutor_plus_guard` | Adds pre-send leakage guard. | Tests leakage reduction. |

## Bridge Judge Input

Use only the context needed for bridge diagnosis:

```json
{
  "student_message": "学生当前轮输入",
  "prior_messages_compact": "最近 2-4 轮摘要，可为空",
  "problem_ref": "题号，可为空",
  "problem_context": "题面压缩摘要或学生提供的题目上下文",
  "student_code_excerpt": "可选，最多保留相关片段",
  "available_known_focus": ["当前系统已注册的 focus 列表，可为空"]
}
```

## Bridge Judge Output Schema

```json
{
  "student_state": "text_comprehension_blocked|problem_representation_unclear|strategy_generation_blocked|strategy_misconception|strategy_application_gap|implementation_execution_gap|debugging_verification_gap|reflection_transfer_gap",
  "bridge_family": "representation_bridge|transition_bridge|predicate_bridge|modeling_bridge|selection_bridge|aggregation_bridge|ordering_bridge|mapping_bridge|boundary_bridge|complexity_bridge|unknown_bridge",
  "known_focus": "state_design|transition_design|check_condition|enumeration_order|greedy_basis|tree_path_difference|tree_diameter_candidates|lazy_semantics|shared_prefix_merging|left_bound_update|general_modeling|constraint_modeling|method_selection|complexity_fit|data_type|loop_boundary|recursion_structure|boundary_debug|implementation_debug|unknown",
  "help_seeking_type": "instrumental_help|executive_help|help_avoidance|unclear",
  "missing_link": "学生缺失的中间关系",
  "evidence_spans": ["从学生输入或题面中抽取的证据"],
  "allowed_help_level": "L1|L2|L3",
  "forbidden_completion": "本轮不能直接给出的内容",
  "confidence": 0.0,
  "needs_new_focus": false
}
```

## Evaluation Metrics

### Bridge Diagnosis

| Metric | Definition |
| --- | --- |
| Student state accuracy | Predicted `student_state` equals gold label. |
| Bridge family accuracy | Predicted `bridge_family` equals gold label. |
| Known focus accuracy | Predicted `known_focus` equals gold label when gold is not `unknown`. |
| Help-seeking type accuracy | Predicted `help_seeking_type` equals gold label. |
| Unknown bridge recall | Predicted `needs_new_focus=true` for gold unknown-focus examples. |
| Missing link quality | Human 0-2 score for whether `missing_link` captures the key relation. |
| Evidence grounding | Human 0-2 score for whether evidence spans come from real input/context. |

### Tutor Reply Quality

Use `BridgeTutor Rubric v1`:

- Bridge Identification
- Groundedness
- Scaffold Appropriateness
- Bridge Leakage Control
- Next-Step Clarity
- Single-Focus Coherence

### Leakage

| Metric | Definition |
| --- | --- |
| Bridge leakage rate | Percent of replies labeled `minor_bridge_leakage` or `major_bridge_leakage`. |
| Major bridge leakage rate | Percent of replies labeled `major_bridge_leakage`. |
| Answer leakage rate | Percent of replies giving complete solution/proof/code. |

### Cost and Product Viability

| Metric | Definition |
| --- | --- |
| Added latency | Extra milliseconds compared with current AIChat. |
| Token multiplier | Tokens used compared with current AIChat. |
| Guard intervention rate | Percent of turns where guard rejects or rewrites. |

## Annotation Protocol

1. Start with `docs/research/bridgebench_cp_seed_v1.jsonl`.
2. Add model predictions next to each example in a separate output file, not in the seed file.
3. Have at least one human reviewer score bridge diagnosis and tutor replies.
4. If two reviewers are available, independently label 20-30 percent of examples.
5. Report agreement on:
   - student state;
   - bridge family;
   - known focus;
   - help-seeking type;
   - leakage label;
   - response quality band.

## Offline Runner

Use the offline runner to produce a JSONL result file without changing online AIChat behavior:

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-jsonl evals/aichat/bridge_offline_eval_results.jsonl \
  --chat-model-provider deepseek \
  --limit 5
```

For model-controlled comparisons, rerun the same seed set with a different tutor provider while keeping the Judge stack on DeepSeek V4 Flash:

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v1.jsonl \
  --output-jsonl evals/aichat/bridge_offline_eval_results.kimi.jsonl \
  --chat-model-provider kimi \
  --limit 5
```

The output row records model metadata under `models`, including `judge_model` and `tutor_model_provider`.

Then summarize the JSONL results into a JSON metrics file and a Markdown report:

```bash
python3 -m evals.aichat.summarize_bridge_offline_eval \
  --input-jsonl evals/aichat/bridge_offline_eval_results.jsonl \
  --output-json evals/aichat/bridge_offline_eval_summary.json \
  --output-md evals/aichat/bridge_offline_eval_summary.md
```

Each output row keeps the seed gold labels and appends:

- `bridge_judge_result`
- `tutor_response`
- `leakage_judge_result`
- `repair_result` when the Leakage Judge requests `rewrite` or `block`
- `error` when a stage fails

The summary report includes:

- bridge family / known focus / student state accuracy;
- allowed help level and help-seeking type accuracy;
- leakage rate, critical bridge leakage rate, answer/code leakage rate;
- rewrite / block / repair rates;
- error cases for manual inspection.

This runner is for offline research only. It should be used to build baseline tables and manual review packs before any Bridge Judge or Leakage Judge logic is promoted to shadow or active runtime.

## Shadow Mode Plan

Only after offline results are promising:

1. Keep current AIChat behavior unchanged.
2. Run Bridge Judge asynchronously after each student turn.
3. Log:
   - current rule result;
   - Bridge Judge result;
   - disagreement flag;
   - student state;
   - help-seeking type;
   - confidence;
   - latency;
   - later Eval Judge rubric scores.
4. Use these logs to decide whether Bridge Judge should enter the main control path.

## Promotion Criteria

Bridge Judge can be promoted from offline to shadow mode if:

- bridge family accuracy is meaningfully higher than current rule matching;
- unknown bridge recall improves on not-yet-registered cases;
- average added latency is acceptable for AIChat;
- human review shows fewer vague or over-specific scaffolds.

Bridge Judge can be promoted from shadow mode to main control only if:

- it reduces bridge leakage or improves next-step clarity in real use;
- teacher review does not show a rise in harmful false positives;
- guard failures have a clear fallback path.

## Paper Framing

The paper should not claim that multi-LLM is automatically better.

The research question is:

> In competitive programming tutoring, when does a schema-based Bridge Judge improve over rule matching or single-LLM prompting for identifying missing problem-solving bridges and controlling bridge leakage?

This supports a measured comparison among:

- current rule matching;
- single LLM structured prompting;
- two-stage Bridge Judge plus Tutor;
- two-stage plus Guard.
