# Bridge Contract Prompt Abstraction Smoke - 2026-05-12

This report records a development smoke test. It checks prompt abstraction and the clean offline Bridge Contract Tutor path. It is not a headline paper result.

## Background

The project owner noted that the Repair / Leakage / Tutor prompts should not enumerate concrete algorithms such as DP, binary search, LCA, or lazy propagation as separate repair rules. They should instead use abstract bridge shapes, such as:

- representation meaning;
- relation or formula;
- predicate condition;
- dependency or update direction;
- contribution or aggregation rule;
- local code slot;
- fully worked micro-example reasoning.

This patch had three goals:

1. Rewrite Leakage Judge, Repair Generator, and offline generation prompts from algorithm-specific recipes to abstract leakage shapes.
2. Remove online `noi_agent_chat()` prompt contamination from the offline `bridge_contract` condition.
3. Check whether a clean offline Bridge Contract Tutor still produces answer-bearing micro-examples on high-risk bridges.

## Changed Scope

This patch only affects the offline research workflow:

- `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- `docs/common/aichat_repair_response_v1_system_prompt.md`
- `evals/aichat/run_bridge_offline_eval.py`
- `test_bridge_offline_eval_runner_unit.py`
- `test_leakage_judge_v1_unit.py`
- `test_repair_response_v1_unit.py`
- `docs/research/prompt_patch_log.md`
- `docs/research/judge_prompt_patch_log.md`

It does not change the student-facing online AIChat path.

## Engineering Check

Command:

```bash
python3 -m unittest \
  test_bridge_offline_eval_runner_unit.py \
  test_leakage_judge_v1_unit.py \
  test_repair_response_v1_unit.py
```

Result:

```text
Ran 55 tests in 0.009s
OK
```

The checks cover:

- generation prompts do not rely on concrete algorithm examples as their main rules;
- DBox / CodeHelp / Socratic / Bridge-inspired baselines do not encode concrete answer-bearing slots;
- Leakage Judge and Repair prompts use abstract leakage shapes;
- offline `bridge_contract` uses a clean system prompt and does not call online `noi_agent_chat()`;
- the clean Bridge Contract prompt forbids candidate answer marks, complete formulas, boundary actions, code lines, and binary choices over key answer slots.

## Smoke Setup

### 11-condition smoke

Command:

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --limit 1 \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260512_prompt_abstraction_smoke1 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1
```

Outputs:

- `evals/aichat/ad_hoc_runs/dev_ablation_20260512_prompt_abstraction_smoke1/combined_dev_ablation.jsonl`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260512_prompt_abstraction_smoke1/combined_dev_ablation_summary.md`
- `evals/aichat/ad_hoc_runs/dev_ablation_20260512_prompt_abstraction_smoke1/coach_response_review_workbook_dev_ablation.zh.xlsx`

Automatic summary:

- rows: 11
- completed: 11
- suite-level errors: 0
- stage error: one `leakage_judge` timeout
- total latency p50: 31.1s
- total latency p95: 117.9s

### Bridge Contract targeted reruns

Target case:

```text
cp_bridge_001
Student: I know LCA is involved, but I do not know where to add or subtract marks for each path.
```

Output directory:

```text
evals/aichat/ad_hoc_runs/bridge_contract_clean_prompt_abstraction_fix_20260512/
```

## Main Findings

### 1. The clean offline prompt removed online prompt contamination

In the first abstraction smoke, `bridge_contract` produced an unrelated trie response for a tree-path contribution case. Inspection showed that the offline condition still used:

```text
bridge_contract -> noi_agent_chat()
```

This inherited the large online AIChat system prompt and product fallback examples, making the offline ablation impure.

After the fix:

```text
bridge_contract -> clean Offline Bridge Contract Tutor prompt -> _chat_completion_create()
```

The targeted rerun no longer produced unrelated trie content. The clean offline prompt is therefore necessary.

### 2. Prompt-only Bridge Contract still leaks on high-risk bridges

Even after the clean prompt explicitly forbids complete formulas, candidate answer marks, binary-choice key slots, and full rules, repeated `cp_bridge_001` tutor-only reruns still produced answer-bearing micro-examples.

The risk is not full code leakage. The risk is:

```text
The micro-example reveals the missing contribution/aggregation bridge by pre-filling operations, signs, locations, or rules.
```

This is exactly the failure mode captured by critical bridge leakage.

### 3. Abstract prompting is necessary but not sufficient

The patch reduces two risks:

- prompts being tied to a concrete algorithm checklist;
- uncovered algorithms becoming unstable because they lack dedicated rules.

But it does not by itself guarantee:

```text
The high-risk missing bridge will not be revealed through a worked micro-example.
```

Therefore this smoke should not be interpreted as:

```text
Abstract bridge-shape prompts make Bridge Contract safe.
```

The more accurate conclusion is:

```text
Abstract bridge-shape prompting is prompt hygiene; critical bridge leakage still needs Guard, Repair, risk-triggered routing, or a more conservative deterministic scaffold.
```

## Impact On Research v1

This smoke supports three decisions:

1. Do not keep adding algorithm-specific prompt rules for isolated failures, because that will inflate prompts and overfit the benchmark.
2. Treat `cp_bridge_001` as a high-risk aggregation/contribution regression case.
3. In the 10-20 case dev ablation, separately inspect:
   - `bridge_contract`
   - `bridge_contract + guard`
   - `bridge_contract + guard + repair`
   - `dbox_inspired_decomposition_tutor + guard`
   - `enhanced_prompt_only`

If high-risk contribution/aggregation cases continue to produce answer-bearing micro-examples, consider a route policy:

```text
critical_bridge_request
+ aggregation_contribution_bridge
+ high leakage risk
=> guard required / repair required / deterministic L1-L2 safe scaffold
```

After this fix, the offline runner also has an optional dev-only pipeline:

```text
pipeline_mode=deterministic_safe_scaffold
```

It is only for research comparison:

- run Bridge Judge first;
- skip Tutor / Leakage Judge / Repair;
- return a deterministic L1 safe scaffold;
- for contribution/aggregation bridges, ask the student to list truly affected objects and expected final counts;
- do not provide auxiliary marks, signs, locations, full formulas, or code;
- do not include this mode in the default dev ablation suite and do not affect online AIChat.

1-case verification:

```bash
python3 -m evals.aichat.run_bridge_offline_eval \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --limit 1 \
  --tutor-mode bridge_contract \
  --pipeline-mode deterministic_safe_scaffold \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 1 \
  --output-jsonl evals/aichat/ad_hoc_runs/bridge_contract_clean_prompt_abstraction_fix_20260512/deterministic_safe_scaffold_limit1.jsonl
```

Result:

- `case_count=1`
- `error_count=0`
- `llm_call_count=1`
- `final_response_source=safe_fallback`
- `stage_errors={}`

Suite-level verification:

```bash
python3 -m evals.aichat.run_dev_ablation_suite \
  --input-jsonl docs/research/bridgebench_cp_seed_v2_gold_20.jsonl \
  --output-dir evals/aichat/ad_hoc_runs/dev_ablation_20260512_safe_scaffold_suite_smoke1 \
  --limit 1 \
  --chat-model-provider deepseek_flash \
  --judge-provider deepseek \
  --max-retries 0 \
  --include-safe-scaffold
```

Result:

- `condition_count=12`
- `combined_row_count=12`
- `bridge_contract_safe_scaffold` appears in the manifest and key CSV
- `bridge_contract_safe_scaffold` has `final_response_source=safe_fallback`
- the review workbook has 11 reviewable rows because one non-safe-scaffold condition produced no reviewable response; safe scaffold was not dropped.

## Claims Not Supported

This report cannot be used to claim that:

- Bridge Contract has solved critical bridge leakage;
- prompt abstraction alone is sufficient for safety;
- the causal effect of Guard / Repair has been proven;
- a 1-case / 11-condition smoke represents the final 50-case held-out result.

## Next Step

Recommended order:

1. Keep this patch, but do not keep adding tree-difference-specific or algorithm-specific rules for `cp_bridge_001`.
2. Mark `cp_bridge_001` as a high-risk regression case in dev ablation reports.
3. Before the 10-20 case dev ablation, decide whether to include `deterministic_safe_scaffold` as an appendix / stress condition:
   - high-risk contribution/aggregation bridges should not default to tutor-only;
   - at least run `+ guard`;
   - severe direct critical-bridge requests can be compared against deterministic safe scaffold.
4. Freeze prompts / graders only before the formal 50-case held-out run.
