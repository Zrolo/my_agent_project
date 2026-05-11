# Literature Baseline Smoke1 Report - 2026-05-11

本报告记录 1-case literature baseline smoke。目的只是检查新增 baseline 的真实输出 schema 和明显泄露风险，不作为论文结果。

## 输入

- Seed file: `docs/research/bridgebench_cp_seed_v2_gold_20.jsonl`
- Case: `cp_bridge_001`
- 模型 provider: `deepseek_flash`
- Pipeline: `tutor_only_no_diagnosis`
- 线上学生 AIChat: 未接入

## 系统

| System | Output file | LLM calls | Error |
|---|---|---:|---|
| `dbox_inspired_decomposition_tutor` | `evals/aichat/ad_hoc_runs/dbox_inspired_smoke1_20260511.jsonl` | 1 | none |
| `codehelp_codeaid_no_direct_solution_tutor` | `evals/aichat/ad_hoc_runs/codehelp_codeaid_smoke1_20260511_v2.jsonl` | 1 | none |
| `bridge_inspired_expert_decision_tutor` | `evals/aichat/ad_hoc_runs/bridge_inspired_expert_decision_smoke1_20260511_v2.jsonl` | 1 | none |
| `socratic_no_answer_tutor` | `evals/aichat/ad_hoc_runs/socratic_no_answer_smoke1_20260511_v5.jsonl` | 1 | none |

## 主要观察

### DBox-inspired

输出了预期字段：

- `baseline_group=literature_inspired_decomposition`
- `decomposition_view`
- `current_substep`
- `hint_level=general_question`
- `final_response_text`

未发现以下禁用字段：

- `correctStep`
- `correct_code`
- `detailed_hint`
- pseudocode
- reveal code / reveal substep

风险：该回复仍把学生思考框到树上差分的端点/LCA 标记问题上。它没有给完整加减公式，但是否过强需要进入盲评。

### CodeHelp/CodeAid-style

输出了预期字段：

- `baseline_group=literature_inspired_guardrail`
- `self_check`
- `final_response_text`

第二轮 prompt tightening 后，回复转向“小链例子 + 让学生观察覆盖次数”，没有直接给完整标记公式，也没有完整代码。它仍会提到路径端点和 LCA 相关性，是否属于 minor leakage 需要教练评审。

### Bridge-inspired expert decision

输出了预期字段：

- `baseline_group=literature_inspired_expert_decision`
- `student_error_or_gap`
- `remediation_strategy`
- `teaching_intention`
- `final_response_text`

第一次 smoke 中，学生可见回复出现了接近答案关系的 root-path formula-like decomposition。随后已收紧 prompt：

- `no formula-like decomposition`
- 不提 parent/neighbor of LCA
- 不把类比转成缺失公式

第二轮学生可见回复没有再出现 root-path formula 或 LCA 父节点补偿。但内部 `student_error_or_gap` 仍可能写出 `fa[lca]` 等答案槽位。该字段是内部 trace，不应出现在学生可见回复或盲评表中。

### Socratic/no-answer

输出了预期字段：

- `baseline_group=literature_inspired_socratic`
- `question_intent`
- `final_response_text`

前几轮 smoke 暴露了一个重要问题：Socratic prompt 即使“不直接给答案”，也会通过提问预填答案槽位，例如“端点 +1 后还要在哪里减 1”。这属于 critical bridge leakage 的风险，因此已追加以下约束：

- 禁止 formula-like decomposition；
- 禁止提 parent/neighbor of LCA；
- 禁止追问 u/v/LCA 的精确操作；
- 树上差分场景禁止提 `+1/-1`、端点标记、减法标记或任何标记位置。

第五轮学生可见回复转向“画一条极小路径、观察最终哪些点应该被计数”的问题。它仍然提到从后代向上累加的观察任务，是否过强需要进入教练盲评。

## Prompt Patch

本次 smoke 触发了 prompt tightening：

| Baseline | Patch |
|---|---|
| `codehelp_codeaid_no_direct_solution_tutor` | 禁止在缺失桥就是 u/v/LCA 操作、check 方向等 answer-bearing slots 时直接追问精确操作；改用 tiny example observation |
| `bridge_inspired_expert_decision_tutor` | 禁止 formula-like decomposition；禁止提 parent/neighbor of LCA；禁止把类比转成缺失公式 |
| `socratic_no_answer_tutor` | 禁止公式化分解、端点/LCA 操作追问、`+1/-1` 标记提示和预填端点标记；只能问中性观察问题 |

## 下一步

1. 用 3-case smoke 覆盖：
   - 树上差分；
   - 二分 check；
   - DP 状态或转移。
2. 导出盲评表时只展示 `final_response_text`，隐藏 internal trace。
3. 在 10-20 case dev ablation 中比较：
   - `enhanced_prompt_only`
   - `socratic_no_answer_tutor`
   - `codehelp_codeaid_no_direct_solution_tutor`
   - `dbox_inspired_decomposition_tutor`
   - `dbox_inspired_decomposition_tutor + guard`
   - `bridge_inspired_expert_decision_tutor`
   - `bridge_contract_predicted`
   - `bridge_contract_predicted + guard`
