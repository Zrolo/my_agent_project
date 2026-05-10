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
  "available_known_focus": [
    {
      "focus_id": "tree_path_difference",
      "bridge_family": "aggregation_bridge",
      "description": "树上路径贡献转成端点/LCA 差分标记并 DFS 汇总。",
      "aliases": ["树上差分", "LCA 标记"]
    }
  ]
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
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1 \
  --tutor-mode current_system \
  --guard-mode predicted \
  --pipeline-mode tutor_plus_guard_plus_repair \
  --focus-registry docs/research/focus_registry_v1.json \
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

Use explicit tutor provider ids for model-controlled runs. The legacy provider id `deepseek` resolves to `deepseek_pro`; use `deepseek_flash` when testing the fast student-facing route. `--chat-thinking-mode disabled` temporarily sets `NOI_CHAT_THINKING_MODE=disabled` only around the tutor generation stage and records `models.chat_thinking_mode` in the output row. Keep this variable explicit in latency experiments because DeepSeek thinking mode can dominate `current_system` tutor latency.

Do not treat `--chat-thinking-mode disabled` as the quality default. In a 5-case smoke comparison on 2026-05-08, disabling thinking reduced `current_system` tutor latency substantially but lost 4/5 pairwise quality comparisons under the coaching rubric, especially on DP state and transition bridge cases where it more readily completed the critical bridge. Use disabled mode for latency-only smoke tests, and report enabled vs disabled separately in any quality experiment.

Use `--judge-provider deepseek` for the default DeepSeek V4 Flash judge stack. Use `--judge-provider kimi` when DeepSeek is unavailable or when running model-family ablations. `--max-retries` retries failed offline judge stages that return `_failed=true`; retry counts are written to each output row.

Offline judge calls disable the OpenAI SDK's internal retry loop by default through `NOI_OFFLINE_JUDGE_SDK_MAX_RETRIES=0`. Keep provider retries explicit in the runner with `--max-retries`; otherwise stage latency becomes hard to interpret because SDK retries and runner retries multiply each other.

### Official Token Parameter Compatibility

The offline judge stack follows the current provider docs:

- DeepSeek Chat Completion uses `max_tokens` for the maximum generated output length.
- Kimi Chat Completion marks `max_tokens` as deprecated and uses `max_completion_tokens`.

The default offline judge output budget is `98304` generated tokens for Bridge Judge, Leakage Judge, and Repair Response, matching the existing Kimi long-form review benchmark convention (`NOI_REVIEW_MAX_TOKENS=98304`). DeepSeek's current model page lists a maximum output of 384K tokens for `deepseek-v4-flash` / `deepseek-v4-pro`, so `98304` is within the documented DeepSeek range. Override with `NOI_BRIDGE_JUDGE_MAX_TOKENS`, `NOI_LEAKAGE_JUDGE_MAX_TOKENS`, or `NOI_REPAIR_RESPONSE_MAX_TOKENS` when running cost-sensitive smoke tests.

Do not switch Kimi judge calls back to `max_tokens`. If Kimi returns truncated content, raise the corresponding `NOI_*_MAX_TOKENS`; if it returns `empty_content`, treat it as provider-output instability and inspect the raw stage error before changing schema logic.

### Local Key / Endpoint Check

The local `.env` is loaded through `noi_agent.load_local_env_if_present()`, not by shell `source`. For this workspace, the DeepSeek key has been verified against the official `/user/balance` endpoint and returned `is_available=true`. The local Moonshot key is valid against `https://api.moonshot.cn/v1/models`, but returns 401 against `https://api.moonshot.ai/v1/models`; keep `MOONSHOT_BASE_URL` aligned with the key's issuing platform unless a new key is created for the `.ai` endpoint.

Use `--tutor-mode current_system` for the current AIChat baseline. In this mode Bridge Judge is an observer: it diagnoses the turn, but the tutor reply is still generated by the current AIChat flow and does not consume the Bridge Judge contract.

Use `--tutor-mode bridge_contract` for the first Bridge-conditioned tutor baseline. In this mode the offline runner inserts a compact Bridge Contract before the current student turn:

- `missing_bridge`
- `allowed_help_level`
- `help_form` / `help_forms`
- `forbidden_content`
- `leakage_risk`

This is still offline-only. It does not change production `chat()`.

Use `--tutor-mode single_llm_structured` for the one-call structured baseline. In this mode the runner skips Bridge Judge and asks one tutor LLM call to output:

- `runtime_bridge_contract`
- `student_response`
- `self_check`

This baseline answers the reviewer question: "Why not let one LLM diagnose, respond, and self-check in a single call?" It should usually be run with `--pipeline-mode tutor_only` first. Guard and repair can be added later as separate ablations, but the headline single-LLM comparison should report that the bridge contract and response came from the same LLM call.

Example:

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-jsonl evals/aichat/ad_hoc_runs/single_llm_structured_smoke.jsonl \
  --tutor-mode single_llm_structured \
  --pipeline-mode tutor_only \
  --chat-model-provider deepseek_flash \
  --limit 3
```

Use `--guard-mode predicted` for the fair default experiment. In this mode Leakage Judge receives only the forbidden content predicted by Bridge Judge. Use `--guard-mode oracle` only as an upper-bound experiment; oracle mode may add `gold_forbidden_completion` from the seed row to the guard input and is not comparable to runtime behavior.

Use `--pipeline-mode` to isolate ablations:

| Mode | Stages run | Primary use |
| --- | --- | --- |
| `diagnosis_only` | Bridge Judge only | Bridge diagnosis accuracy. |
| `tutor_only_no_diagnosis` | Tutor only, no Bridge Judge and no candidate retrieval | Fair `current_system` response/latency baseline. Valid only with `--tutor-mode current_system`. |
| `tutor_only` | Bridge Judge + tutor | Tutor quality without output guard. |
| `tutor_plus_guard` | Bridge Judge + tutor + Leakage Judge | Leakage detection without repair. |
| `tutor_plus_guard_plus_repair` | Bridge Judge + tutor + Leakage Judge + Repair | Full offline safety pipeline. |

For `single_llm_structured`, `tutor_only` means one LLM call only; Bridge Judge is not run. `diagnosis_only` is invalid for `single_llm_structured` because the baseline is defined by producing both a structured contract and a student-facing response in the same call.

The default is `tutor_plus_guard_plus_repair` for backward compatibility with earlier smoke runs. Report `pipeline_mode` in every baseline table, because it changes both response quality and latency.

Use `--judge-schema-mode` to isolate Judge label-load ablations:

| Mode | Meaning | Primary use |
| --- | --- | --- |
| `full_schema_judge` | Bridge Judge behaves like the original richer diagnostic judge. | Baseline for observing label overload. |
| `compact_contract_judge` | Runner records a compact runtime bridge contract from the Bridge Judge result. | Tests whether tutor control can rely on fewer fields. |
| `retrieval_augmented_compact_judge` | Runner first retrieves top-k algorithm topics and registered focus candidates, passes only those focus candidates to Bridge Judge, and records a compact contract. | Tests whether top-k retrieval reduces focus drift and prompt load. |

`full_schema_judge` remains the default so old smoke commands keep working. New research runs should include at least `compact_contract_judge` and `retrieval_augmented_compact_judge` when studying whether fine labels overload the Judge.

Then summarize the JSONL results into a JSON metrics file and a Markdown report:

```bash
python3 -m evals.aichat.summarize_bridge_offline_eval \
  --input-jsonl evals/aichat/bridge_offline_eval_results.jsonl \
  --output-json evals/aichat/bridge_offline_eval_summary.json \
  --output-md evals/aichat/bridge_offline_eval_summary.md \
  --output-md-zh evals/aichat/bridge_offline_eval_summary.zh.md
```

All research reports should have both English and Chinese Markdown versions. The summary script writes the English Markdown report to `--output-md` and the Chinese Markdown report to `--output-md-zh`; when `--output-md-zh` is omitted, it defaults to `<output-md stem>.zh.md`.

Each output row keeps the seed gold labels and appends:

- `bridge_judge_result`
- `tutor_response`
- `leakage_judge_result`
- `repair_result` when the Leakage Judge requests `rewrite` or `block`
- `candidate_response_text`, the original tutor reply before guard or repair
- `final_response_text`, the response that should be used for coach response review
- `final_response_source`, one of `candidate`, `repair`, `blocked`, or `none`
- `repair_applied` and `blocked`
- `guard_contract`, including `guard_mode` and the actual forbidden content passed to Leakage Judge
- `runtime_bridge_contract` when `judge_schema_mode` is compact or retrieval-augmented compact
- `candidate_retrieval` when `judge_schema_mode=retrieval_augmented_compact_judge`
- `prompt_budget_estimate`, a lightweight token estimate for comparing prompt load
- `latency_ms`, including Bridge Judge / tutor / Leakage Judge / repair / total latency
- `llm_call_count`, the number of attempted LLM stages for the case, including explicit runner retries
- `stage_errors`, keyed by failed stage, with the provider `_reason` when available
- `retry_count`, the total retries used across offline judge stages
- `error` when a stage fails

The summary report includes:

- bridge family / known focus / student state accuracy;
- known focus accuracy on registered focus only;
- unknown focus recall;
- allowed help level and help-seeking type accuracy;
- leakage rate, critical bridge leakage rate, answer/code leakage rate;
- rewrite / block / repair rates;
- invalid label rate, focus out-of-registry rate, self-contradiction rate, and average prompt-token estimate for compact contract runs;
- average LLM call count;
- p50 / p95 total latency;
- stage error counts;
- groups by `tutor_mode`, `guard_mode`, `pipeline_mode`, `judge_schema_mode`, and `tutor_model_provider`;
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
