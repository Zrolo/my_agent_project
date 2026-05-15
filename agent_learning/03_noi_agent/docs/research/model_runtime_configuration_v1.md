# Model Runtime Configuration v1

This document defines the model and runtime configuration for Research v1 ablation experiments. Its purpose is to prevent **model differences** from being mistaken for **prompt / contract / guard / repair architecture differences**.

## Core Principle

The main experiments compare tutoring harnesses, not model families. Unless a run is explicitly declared as a model-setting ablation, the same main experiment batch must fix:

- the tutor generation model;
- the tutor thinking mode;
- the Bridge Judge / Leakage Guard / Repair stack;
- prompt / rubric / registry versions;
- the seed set and blind-review protocol.

Recommended paper wording:

```text
The main ablation fixes the tutor model and judge stack, and varies only the tutoring harness condition.
```

## Default Model Configuration

### Tutor / Candidate Response

The current development ablation runner defaults to:

```text
chat_model_provider = deepseek_flash
```

In `noi_agent.py`, `deepseek_flash` maps to:

```text
model = deepseek-v4-flash
thinking = enabled by profile default
```

Therefore, unless `--chat-thinking-mode disabled` is passed explicitly, new development and held-out quality experiments should be recorded as:

```text
tutor_model_provider = deepseek_flash
tutor_model = deepseek-v4-flash
chat_thinking_mode = profile_default
effective_tutor_thinking = enabled
```

### Bridge Judge / Leakage Guard / Repair

The current offline judge stack defaults to:

```text
judge_provider = deepseek
judge_model = deepseek-v4-flash
thinking = disabled
```

This stack is used for:

- Bridge Judge;
- Leakage Guard;
- Repair Response;
- post-repair second-pass guard, when enabled.

Repair is a generator rather than a judge. In the current offline implementation, however, it uses the same offline judge provider for experimental control.

## Stage Ownership

The blind-review `final_response_text` can come from different stages:

| `final_response_source` | Student-visible source | Model interpretation |
| --- | --- | --- |
| `candidate` | Tutor candidate response | `chat_model_provider`, default `deepseek_flash` |
| `repair` | Repair Response | `judge_provider`, default `deepseek-v4-flash` with thinking disabled |
| `safe_fallback` | deterministic fallback | non-LLM |
| `blocked` | blocked by Guard | no natural student-visible response |

Therefore, analysis must not look only at `tutor_model_provider`. It must also report:

- `final_response_source`;
- `repair_applied`;
- `blocked`;
- `models.judge_model`;
- `models.tutor_model_provider`;
- `models.chat_thinking_mode`.

## Blind Review Visibility

Coach blind-review workbooks should hide:

- system / condition name;
- tutor model provider;
- judge model provider;
- whether Guard or Repair was used;
- response source.

These fields remain in the key file / JSONL for analysis after review.

## Interpreting Older Runs

Some existing pilot / smoke runs used:

```text
chat_thinking_mode = disabled
```

For example, early 20-case mini-study runs and the thinking ablation used this mode. They remain useful as development evidence, but they must not be merged with `profile_default/enabled` runs as headline results.

Reports should distinguish:

```text
deepseek-v4-flash + profile_default/enabled
deepseek-v4-flash + disabled
deepseek legacy provider / deepseek_pro
```

The legacy tutor provider id `deepseek` may resolve to `deepseek_pro`. Therefore, old repair stress or ad hoc runs that record `tutor_model_provider=deepseek` need a separate note and should not be treated as equivalent to `deepseek_flash`.

## Formal 50-case Rule

Before the 50-case held-out main experiment, freeze one model/runtime config:

```text
tutor_model_provider: deepseek_flash
tutor_model: deepseek-v4-flash
tutor_thinking_mode: profile_default / enabled
judge_provider: deepseek
judge_model: deepseek-v4-flash
judge_thinking_mode: disabled
repair_provider: deepseek
repair_model: deepseek-v4-flash
repair_thinking_mode: disabled
```

## Offline Timeout / Token Budget Policy

In the 2026-05-13 real AIChat student-only 8-case pilot, the original merged run still had 3 `leakage_judge` stage timeouts. Keeping the max-token budget at the current default and changing only:

```text
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25
```

for targeted reruns of those 3 condition-case pairs produced the `merged_timeout25` run with:

```text
combined_row_count = 48
final_response_row_count = 48
stage_warning_rows = []
analysis_ready = true
headline_ready = true
```

Current evidence therefore supports this runtime policy:

```text
max token budget: keep provider/default Research v1 values; do not raise to 128k for timeout symptoms.
Leakage Judge timeout: use 25 seconds as the candidate held-out setting.
Timeout interpretation: APITimeoutError should be treated as request/provider latency unless logs show truncation or context/token-limit errors.
```

Do not interpret `APITimeoutError` as evidence that max tokens are too low. Max tokens control output budget; this run showed request timeout rather than `context length exceeded`, `max_tokens exceeded`, `truncated`, or JSON truncation.

Before the formal 50-case held-out run, the experiment command should explicitly record:

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25
```

while keeping:

```text
NOI_BRIDGE_JUDGE_MAX_TOKENS: default
NOI_LEAKAGE_JUDGE_MAX_TOKENS: default
NOI_REPAIR_RESPONSE_MAX_TOKENS: default
```

If later 50-case runs show Bridge Judge or Repair Response timeouts, calibrate those stages separately. Do not raise all timeouts or max-token budgets at once.

If the project needs to compare thinking enabled vs disabled, or DeepSeek vs Kimi / MiMo, run that as a separate model-setting ablation. Do not mix it into the main harness ablation.

## Online Answer Style Is Not A Model Ablation

On 2026-05-12, the online student AIChat added an independent answer-style toggle:

| UI label | Backend value | Research interpretation |
|---|---|---|
| `简洁提示` | `current_system` | Default online behavior; usable as the deployment baseline |
| `教练引导` | `enhanced_prompt_only_clean` | Prompt-only coaching option; not a new model and not a Bridge / Guard / Repair architecture |

This answer style is independent of the model-speed selector:

```text
Fast + 简洁提示 = deepseek_flash + current_system
Fast + 教练引导 = deepseek_flash + enhanced_prompt_only_clean
Pro + 简洁提示 = deepseek_pro + current_system
Pro + 教练引导 = deepseek_pro + enhanced_prompt_only_clean
```

Therefore, real online logs must record and analyze both:

```text
chat_model_provider
aichat_prompt_mode
```

Online use of `教练引导` is product / deployment observation. It should not be merged into the 50-case held-out main experiment table. The 50-case main experiment should still use frozen offline conditions, a fixed model/runtime configuration, and the blind-review protocol.

## Reporting Template

Every experiment report should list:

```text
Tutor provider:
Tutor model:
Tutor thinking mode:
Judge provider:
Judge model:
Judge thinking mode:
Repair provider/model:
Prompt versions:
Rubric version:
Dataset split:
Can this run be used for headline held-out claims? yes/no
```

## Allowed Claims

Acceptable:

```text
Under a fixed DeepSeek V4 Flash tutor and judge stack, we compare tutoring harness variants.
```

Avoid:

```text
Bridge Contract is better than other models.
```

Also avoid mixing old `thinking disabled` pilot results with new `profile_default/enabled` held-out results in the same headline table.
