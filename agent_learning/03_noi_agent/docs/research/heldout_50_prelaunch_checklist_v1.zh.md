# 50-case Held-out Prelaunch Checklist v1

日期：2026-05-12

本清单用于决定 Research v1 是否可以从 dev/regression 阶段进入正式 50-case held-out 主实验。它不是论文结果，而是防止过拟合、weak baseline、prompt drift 和 judge drift 的发车检查。

## Go / No-go 总结

当前状态：**No-go for final held-out run，Go for held-out draft coach review**。

原因：

- strong prompt、DBox-inspired、CodeHelp/CodeAid-style、Bridge-inspired、Bridge Contract、Guard、Repair 的离线链路已经具备；
- 10-case dev ablation 和 Repair stress 已完成开发阶段验证；
- 但 prompt / judge / rubric 还没有完成项目负责人确认后的版本冻结；
- model/runtime configuration 尚未作为 held-out 主实验版本锁定；
- Leakage Guard 只能作为 dev signal，不能作为 gold；
- 50-case held-out 草稿已建立并通过结构校验，但 Coach A 审查、Coach B 复标、裁决和冻结还未完成。
- formal frozen-status preflight 已添加；当前草稿会被正确拦截为 `frozen_status_required`，见 [heldout_50_formal_preflight_report_20260513.zh.md](heldout_50_formal_preflight_report_20260513.zh.md)。

## 1. Scope Lock

| 检查项 | 状态 | 备注 |
|---|---|---|
| 论文定位为 evaluation framework paper | pass | 主线是 CP-MissingBridgeBench，不是线上多 Agent 系统 |
| 不把 `current_system` 作为唯一科研 baseline | pass | 已加入 strong prompt 和 literature-inspired baselines |
| 不声称完整复现 DBox | pass | 使用 DBox-inspired single-turn decomposition baseline |
| 不新增新模块进入 Research v1 主线 | pass | 下一步是 freeze / held-out / double annotation |

## 2. Prompt Freeze Readiness

| Prompt / condition | Prelaunch status | 进入 50-case 方式 |
|---|---|---|
| `current_system` | snapshot-required | deployment baseline；冻结当前线上路径快照 |
| `enhanced_prompt_only` | freeze-candidate | main baseline |
| `codehelp_codeaid_no_direct_solution_tutor` | freeze-candidate | main or appendix baseline |
| `dbox_inspired_decomposition_tutor` | freeze-candidate | appendix or paired comparison |
| `dbox_inspired_decomposition_tutor + guard` | freeze-candidate + guard caveat | main baseline |
| `bridge_inspired_expert_decision_tutor` | freeze-candidate | main baseline |
| `single_llm_structured + guard` | freeze-candidate + guard caveat | strong single-LLM guarded baseline |
| `bridge_contract_predicted + guard` | guarded-only | main method condition, but not safety proof |
| `bridge_contract_predicted + guard + repair` | freeze-candidate + repair caveat | main or appendix condition |
| `bridge_contract_safe_scaffold` | appendix-only | fallback / stress condition only |

## 3. Judge / Grader Readiness

| Judge / grader | Prelaunch status | 使用方式 |
|---|---|---|
| Runtime Bridge Diagnoser | freeze-candidate | 可作为 diagnosis/control signal；需要与 coach label 比较 |
| Runtime Leakage Guard | dev-signal-only | 与 coach leakage label 和 static lint 同时报，不单独当 gold |
| Static lint dev gate | screening-only | 高召回复查信号，不是安全裁决 |
| Offline Bridge Grader | pending-definition | 不进入 headline 自动评分 |
| Offline Leakage Grader | pending-definition | 不进入 headline 自动评分 |
| Offline Response Grader | pending-definition | 暂用 coach blind review |
| Offline Repair Grader | pending-definition | 暂用 coach before/after review |

## 3.5 Model / Runtime Configuration

| 检查项 | 状态 | 备注 |
|---|---|---|
| Tutor provider 固定 | pending-freeze | 主实验建议固定为 `deepseek_flash` |
| Tutor model 固定 | pending-freeze | `deepseek-v4-flash` |
| Tutor thinking mode 固定 | pending-freeze | 主质量实验建议使用 `profile_default` / effective enabled；旧 `disabled` 结果只作 dev evidence |
| Judge / Guard / Repair provider 固定 | pending-freeze | 默认 `judge_provider=deepseek` |
| Judge / Guard / Repair thinking mode 固定 | pass-by-design | offline judge stack 默认 `thinking=disabled` |
| Leakage Judge timeout 固定 | freeze-candidate | 真实日志 8-case pilot 中，`NOI_LEAKAGE_JUDGE_TIMEOUT_SECONDS=25` 解决了剩余 stage timeout |
| Judge / Repair max token budget | pass-by-design | 保持当前默认值；不要因 timeout 症状提高到 128k |
| Model-setting ablation 分离 | required | DeepSeek vs Kimi / MiMo 或 thinking enabled vs disabled 必须另开实验，不混入主表 |

详细规则见 [model_runtime_configuration_v1.zh.md](model_runtime_configuration_v1.zh.md)。

正式 50-case 主实验应使用：

```text
--condition-set heldout_main
```

完整执行命令和完整性门禁见 [heldout_50_main_experiment_runbook_v1.zh.md](heldout_50_main_experiment_runbook_v1.zh.md)。

## 4. Dataset Requirements

50-case held-out 创建前必须满足：

- 不从当前 20-case dev/regression 里抽样当主实验 held-out；
- 覆盖 DP、二分、树图、贪心、数据结构、实现边界、调试、直接要答案/代码/算法确认/局部补全；
- 每条 case 至少包含：
  - `case_id`
  - `student_message`
  - `problem_context`
  - `recent_dialogue`
  - `student_known_state`
  - `missing_bridge`
  - `allowed_help_level`
  - `forbidden_content`
  - `success_criteria`
  - `review_notes_for_coach`
- 每条 case 都要能让教练判断什么算“好回复”和什么算“过度补桥”。
- `recent_dialogue` 分布必须避免退化成纯单轮问答：默认要求 `N/A` 不超过 10 条，长上下文不少于 15 条。
- 正式主实验前必须通过 frozen-status preflight：
- 正式主实验前先运行 readiness check：

```bash
python3 -m evals.aichat.check_heldout_50_readiness \
  --output-json docs/research/heldout_50_readiness_YYYYMMDD.json \
  --output-md-zh docs/research/heldout_50_readiness_YYYYMMDD.zh.md \
  --output-md docs/research/heldout_50_readiness_YYYYMMDD.md
```

- 然后必须通过 frozen-status preflight：

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_frozen.jsonl \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_formal_preflight_report.json \
  --require-frozen-status
```

该检查必须 `ok=true`，否则不能进入 headline run。

## 5. Coach Annotation Requirements

进入 headline 前至少需要：

| 项 | 要求 |
|---|---|
| Coach A | 标全部 50 条 task/reference，并完成 response blind review |
| Coach B | 独立标至少 20 条 task/reference 或关键 response review subset |
| Agreement | 报告 bridge family、help level、leakage label、would-show、overall quality 的一致性 |
| Adjudication | 对低置信、多桥梁、重大泄露分歧样本做裁决 |
| Low-confidence handling | `coach_reviewer_confidence=low` 或 `needs_discussion=yes` 不直接作为 headline 结论 |

## 6. Main Experiment Logging Requirements

每条输出必须保留：

- `case_id`
- `condition_id`
- `tutor_mode`
- `pipeline_mode`
- prompt version
- judge prompt version
- repair prompt version, if applicable
- `models.tutor_model_provider`
- `models.chat_thinking_mode`
- `models.judge_model`
- `models.judge_provider`
- `candidate_response_text`
- `final_response_text`
- `final_response_source`
- `runtime_bridge_contract`
- `leakage_judge_result`
- `post_repair_leakage_judge_result`
- `repair_applied`
- `repair_still_leaks`
- `blocked`
- `candidate_static_leakage_risk_lint`
- `final_static_leakage_risk_lint`
- `stage_errors`
- `latency_ms`
- `llm_call_count`

## 7. Headline Claim Rules

可以作为 headline 的结果必须满足：

- 来自 50-case held-out；
- 使用 freeze 后版本；
- 有 coach blind review 或校准过的 grader；
- 不把 static lint / runtime Guard 当 gold；
- 按 case 做 paired comparison，不把所有 response rows 当独立样本；
- 报告质量、泄露、student-ready、回复负担、延迟和调用次数。

不能作为 headline：

- dev ablation 均值；
- 3-case smoke；
- 单教练低置信样本；
- self-review；
- 只由 LLM Guard 自动给出的 leakage rate；
- prompt 修改后没有 held-out 复验的结果。

## 8. Prelaunch Decision

当前建议：

1. 先让项目负责人确认 `prompt_patch_log.md` 和 `judge_prompt_patch_log.md` 的 freeze readiness 状态。
2. 把 `current_system` 作为 deployment snapshot，而不是继续改它。
3. 对 `enhanced_prompt_only`、DBox-inspired、Bridge-inspired、CodeHelp/CodeAid-style、Bridge Contract guarded variants 做版本锁定。
4. 按 [model_runtime_configuration_v1.zh.md](model_runtime_configuration_v1.zh.md) 锁定主实验模型和 thinking mode。
5. 将 Leakage Guard 明确写成 dev signal / runtime guard，而不是 coach gold。
6. 审查并冻结 50-case held-out 草稿数据集。

一句话：

> 现在已有 50-case 草稿，可以进入教练审查；但还不能直接开跑主实验。先冻结 prompt / judge / rubric / model runtime 版本、审查数据、完成复标和裁决，再跑正式 held-out。
