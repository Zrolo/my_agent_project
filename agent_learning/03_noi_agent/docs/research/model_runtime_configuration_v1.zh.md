# Model Runtime Configuration v1

本文档规定 Research v1 消融实验中的模型与运行配置，避免把 **模型差异** 误当成 **prompt / contract / guard / repair 架构差异**。

## 核心原则

正式主实验只比较 tutoring harness，不比较模型家族。除非专门声明为 model-setting ablation，同一批主实验必须固定：

- tutor 生成模型；
- tutor thinking mode；
- Bridge Judge / Leakage Guard / Repair stack；
- prompt / rubric / registry 版本；
- seed set 和 blind-review protocol。

论文写作中应明确：

```text
The main ablation fixes the tutor model and judge stack, and varies only the tutoring harness condition.
```

中文表述：

```text
主消融实验固定 tutor 模型和 judge stack，只改变 tutoring harness 条件。
```

## 默认模型配置

### Tutor / Candidate Response

当前 dev ablation runner 默认：

```text
chat_model_provider = deepseek_flash
```

在 `noi_agent.py` 中，`deepseek_flash` 对应：

```text
model = deepseek-v4-flash
thinking = enabled by profile default
```

因此，除非命令行显式传入 `--chat-thinking-mode disabled`，新的 dev / held-out 质量实验应记录为：

```text
tutor_model_provider = deepseek_flash
tutor_model = deepseek-v4-flash
chat_thinking_mode = profile_default
effective_tutor_thinking = enabled
```

### Bridge Judge / Leakage Guard / Repair

当前 offline judge stack 默认：

```text
judge_provider = deepseek
judge_model = deepseek-v4-flash
thinking = disabled
```

这个 stack 用于：

- Bridge Judge；
- Leakage Guard；
- Repair Response；
- post-repair second-pass guard（如果启用）。

注意：Repair 是 generator，不是 judge；但当前实现为了离线实验控制，使用同一 offline judge provider。

## Stage Ownership

盲审表里的 `final_response_text` 可能来自不同 stage：

| `final_response_source` | 学生可见回复来源 | 模型解释 |
| --- | --- | --- |
| `candidate` | Tutor candidate response | `chat_model_provider`，默认 `deepseek_flash` |
| `repair` | Repair Response | `judge_provider`，默认 `deepseek-v4-flash` thinking disabled |
| `safe_fallback` | deterministic fallback | 非 LLM |
| `blocked` | 被 Guard 阻断 | 无学生可见自然回复 |

因此分析时不能只看 `tutor_model_provider`。必须同时报告：

- `final_response_source`；
- `repair_applied`；
- `blocked`；
- `models.judge_model`；
- `models.tutor_model_provider`；
- `models.chat_thinking_mode`。

## Blind Review Visibility

教练盲审表应隐藏：

- system / condition 名称；
- tutor model provider；
- judge model provider；
- whether guard or repair was used；
- response source。

这些信息只保留在 key file / JSONL 中，供分析阶段合并。

## 旧实验解释

已有部分 pilot / smoke 使用过：

```text
chat_thinking_mode = disabled
```

例如早期 20-case mini-study 和 thinking ablation。它们仍可作为 development evidence，但不能与 `profile_default/enabled` 的主实验混合成 headline result。

文档和报告中应区分：

```text
deepseek-v4-flash + profile_default/enabled
deepseek-v4-flash + disabled
deepseek legacy provider / deepseek_pro
```

旧 provider id `deepseek` 在 tutor 侧可能解析为 `deepseek_pro`，因此旧 repair stress / ad hoc run 若记录 `tutor_model_provider=deepseek`，应单独解释，不能默认等同于 `deepseek_flash`。

## Formal 50-case Rule

50-case held-out 主实验前必须冻结一份 model/runtime config：

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

2026-05-13 的真实 AIChat student-only 8-case pilot 中，原始 merged run 仍有 3 条 `leakage_judge` stage timeout。保持 max token 默认值不变、只将：

```text
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25
```

用于这 3 个 condition-case 的定向重跑后，新的 `merged_timeout25` run 达到：

```text
combined_row_count = 48
final_response_row_count = 48
stage_warning_rows = []
analysis_ready = true
headline_ready = true
```

因此当前证据支持以下运行原则：

```text
max token budget: keep provider/default Research v1 values; do not raise to 128k for timeout symptoms.
Leakage Judge timeout: use 25 seconds as the candidate held-out setting.
Timeout interpretation: APITimeoutError should be treated as request/provider latency unless logs show truncation or context/token-limit errors.
```

不要把 `APITimeoutError` 直接解释成 max token 不够。max token 解决的是输出预算；本轮错误来自请求超时，而不是 `context length exceeded`、`max_tokens exceeded`、`truncated` 或 JSON 截断。

正式 50-case held-out 前，实验命令应显式记录：

```bash
NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25
```

同时继续保持：

```text
NOI_BRIDGE_JUDGE_MAX_TOKENS: default
NOI_LEAKAGE_JUDGE_MAX_TOKENS: default
NOI_REPAIR_RESPONSE_MAX_TOKENS: default
```

如果后续 50-case 中仍出现 Bridge Judge 或 Repair Response timeout，应单独做对应 stage 的 timeout calibration，不要一次性提高所有 timeout 或 max token。

如果需要比较 thinking enabled vs disabled，或 DeepSeek vs Kimi / MiMo，应另设 model-setting ablation，不应混入主 harness ablation。

## 线上回答方式不是模型消融

2026-05-12 线上学生 AIChat 增加了独立的回答方式切换：

| 前端名称 | 后端参数 | 研究解释 |
|---|---|---|
| `简洁提示` | `current_system` | 默认线上行为，可作为 deployment baseline |
| `教练引导` | `enhanced_prompt_only_clean` | prompt-only 教练引导选项，不是新模型，也不是 Bridge / Guard / Repair 架构 |

该回答方式与模型速度选择相互独立。也就是说：

```text
快速 + 简洁提示 = deepseek_flash + current_system
快速 + 教练引导 = deepseek_flash + enhanced_prompt_only_clean
专业 + 简洁提示 = deepseek_pro + current_system
专业 + 教练引导 = deepseek_pro + enhanced_prompt_only_clean
```

因此真实线上日志必须同时记录并分析：

```text
chat_model_provider
aichat_prompt_mode
```

`教练引导` 的线上使用只能作为 product / deployment observation，不应直接混入 50-case held-out 主实验表。50-case 主实验仍应使用冻结的 offline condition、固定模型配置和盲审协议。

## Reporting Template

每份实验报告必须列出：

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

可以写：

```text
Under a fixed DeepSeek V4 Flash tutor and judge stack, we compare tutoring harness variants.
```

不应写：

```text
Bridge Contract is better than other models.
```

也不应把旧 `thinking disabled` pilot 与新 `profile_default/enabled` held-out 混成同一主表。
