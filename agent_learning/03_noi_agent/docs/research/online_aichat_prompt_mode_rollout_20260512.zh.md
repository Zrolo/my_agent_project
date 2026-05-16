# 线上 AIChat 回答方式上线记录 20260512

本文记录 2026-05-12 线上学生 AIChat 的一次产品侧改动。该改动用于改善学生日常使用体验，并为后续真实日志分析保留模式标记；它不是 Research v1 的正式 held-out 结果，也不表示 Bridge Judge、Leakage Guard、Repair 或 risk-triggered routing 已经接入线上 active mode。

## 上线内容

学生端 AIChat 增加了独立的“回答方式”切换：

| 前端名称 | 后端参数 | 含义 |
|---|---|---|
| `简洁提示` | `current_system` | 默认路径，保留当前线上 AIChat 行为，可继续作为 deployment baseline |
| `教练引导` | `enhanced_prompt_only_clean` | 在既有 `chat()` 路径上加入更强的 prompt-only 教练引导约束 |

原有模型速度切换保持独立：

| 前端名称 | 后端参数 | 含义 |
|---|---|---|
| `快速` | `deepseek_flash` | flash 模型配置 |
| `专业` | `deepseek_pro` | pro 模型配置 |

因此线上一次学生请求至少需要同时记录：

```text
chat_model_provider
aichat_prompt_mode
```

其中 `教练引导` 不是新模型，也不是多 Judge 架构。它仍使用学生当前选择的模型，只改变学生可见回复生成前的 prompt-only guidance。

## 未上线内容

本次改动没有接入：

- Bridge Judge；
- Runtime Bridge Contract；
- Leakage Guard；
- Repair Generator；
- post-repair second-pass guard；
- risk-triggered routing；
- full multi-judge every turn。

线上 `教练引导` 只能被描述为 prompt-only product option，不能被描述为完整 Bridge-aware Tutor。

## 部署验证

部署目录：

```text
/opt/noi-agent
```

服务：

```text
noi-agent.service
```

上线后完成了以下验证：

- 前端构建成功；
- 服务重启后保持 active；
- 静态资源包含 `回答方式`、`简洁提示`、`教练引导`、`aichat_prompt_mode` 和 `enhanced_prompt_only_clean`；
- `/chat` 测试请求返回：
  - `prompt_mode = enhanced_prompt_only_clean`；
  - `prompt_mode_label = 教练引导`；
  - 测试样例延迟约 41.9 秒。

测试账户只用于临时验证，验证后已从线上账号文件中移除并重启服务。

## 研究边界

本次上线会影响未来真实学生日志的解释：

- 默认 `简洁提示=current_system` 仍可作为 deployment baseline；
- 如果学生选择 `教练引导`，该轮不能再简单归入旧 `current_system`；
- 真实线上日志必须按 `aichat_prompt_mode` 分层分析；
- 如果论文使用真实日志 case，必须说明该 case 来自哪种回答方式；
- 线上日志可以用于 dev error analysis 和 future deployment discussion，但不能回头污染已经冻结的 50-case held-out prompt / judge / rubric。

论文中更安全的表述是：

> After the development-stage prompt-only baseline showed better day-to-day tutoring behavior, we exposed it as an optional online answer style for product use. This online option is logged separately and is not treated as held-out experimental evidence.

中文表述：

> 开发阶段 prompt-only baseline 显示出更好的日常辅导体验后，我们将其作为线上可选回答方式提供给学生。该线上选项会被单独记录，不作为 held-out 主实验结论。

## 后续监控

后续线上观察应至少统计：

- `aichat_prompt_mode` 的使用次数和占比；
- `chat_model_provider` 与 `aichat_prompt_mode` 的组合；
- p50 / p95 latency；
- 学生下一轮是否继续推进；
- 学生是否抱怨“讲太多”或“提示太少”；
- 教练抽查中的 critical bridge leakage；
- 是否出现直接给完整代码、完整题解、完整状态定义、完整转移或完整 check 条件的情况。

这些监控结果只能作为 deployment / shadow-style evidence，不能替代 50-case held-out、双教练标注和 judge calibration。
