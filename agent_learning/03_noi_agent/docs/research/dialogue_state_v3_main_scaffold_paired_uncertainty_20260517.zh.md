# Dialogue-State v3 Main-Scaffold Paired Uncertainty (20260517)

## 范围

本报告只使用 `main_scaffold_eval` slice（31 个 case），避免把 clarification / policy safety 样本混入主脚手架质量比较。主口径是 `priority60_adjudicated_plus_coachA`；同时保留 Coach A only、Coach B only、`priority60_adjudicated_plus_coachB` 作为 sensitivity。

统计口径：同一 case 内成对比较；`Δ overall` 为前一个 condition 减后一个 condition；bootstrap CI 为 case-level paired bootstrap 95% CI；p 值为随机符号翻转 paired permutation test（20,000 次 Monte Carlo）；W/T/L 按 overall 分数逐 case 计数。`Δ critical leaks` 为前者 critical/answer 级泄露数减后者，负数代表前者更少。

## 主口径：priority60 adjudicated + Coach A

| comparison | n | Δ overall | 95% bootstrap CI | paired p | W/T/L | Δ ready | Δ safe-ready | Δ critical leaks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | 31 | +0.2903 | [-0.0968, +0.6452] | 0.2016 | 14/10/7 | -1 | -1 | -2 |
| `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | 31 | +0.0645 | [-0.2258, +0.3548] | 0.8322 | 7/18/6 | -1 | -1 | +0 |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | 31 | +0.2903 | [-0.0323, +0.6129] | 0.1358 | 12/14/5 | +1 | +1 | -2 |
| `dbox_inspired_guard` vs `dbox_inspired_clean` | 31 | +0.0000 | [-0.3548, +0.3548] | 1.0000 | 7/15/9 | +2 | +2 | +0 |
| `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | 31 | +0.6774 | [+0.2581, +1.0645] | 0.0046 | 18/10/3 | +12 | +12 | -7 |
| `bridge_contract_compact_guard` vs `dbox_inspired_guard` | 31 | +0.2258 | [-0.0645, +0.5484] | 0.2360 | 12/12/7 | +0 | +0 | -2 |

## 读法

- `bridge_contract_compact_guard_repair` 相对 `dbox_inspired_guard` 的 overall 均值更高（+0.2903），且 critical/answer 泄露少 2 条，但 CI 跨 0、paired p≈0.2016；这支持“趋势优势/权衡更好”，不支持写成显著胜利。
- `bridge_contract_compact_guard_repair` 相对 `bridge_contract_compact_guard` 的 Δ overall 只有 +0.0645，W/T/L=7/18/6，critical 泄露相同；主实验不能证明 Repair 本身造成提升。
- `dbox_inspired_guard` 相对 `dbox_inspired_clean` 的 Δ overall 为 0，说明 guard-only 条件不能被解释为最终回复修复收益。
- `codehelp_codeaid_clean` 相对 `enhanced_prompt_only_clean` 在主口径上较稳（+0.6774，CI 不跨 0），显示 strong prompt-only 在该 slice 中不是一个足够安全/稳健的上界。

## Sensitivity

| scenario | comparison | Δ overall | 95% bootstrap CI | paired p | W/T/L |
| --- | --- | --- | --- | --- | --- |
| coach_A_only | `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | +0.2581 | [-0.1613, +0.6774] | 0.3063 | 14/9/8 |
| coach_A_only | `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | -0.0645 | [-0.4194, +0.2903] | 0.8557 | 7/16/8 |
| coach_A_only | `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | +0.1935 | [-0.1613, +0.5161] | 0.3637 | 12/13/6 |
| coach_A_only | `dbox_inspired_guard` vs `dbox_inspired_clean` | -0.0645 | [-0.4194, +0.2903] | 0.8585 | 7/14/10 |
| coach_A_only | `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | +0.4839 | [+0.0968, +0.8710] | 0.0372 | 16/10/5 |
| coach_A_only | `bridge_contract_compact_guard` vs `dbox_inspired_guard` | +0.3226 | [+0.0000, +0.6452] | 0.0866 | 13/12/6 |
| coach_B_only | `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | +0.0323 | [-0.1935, +0.2581] | 1.0000 | 7/18/6 |
| coach_B_only | `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | +0.0968 | [-0.1613, +0.3548] | 0.6359 | 8/17/6 |
| coach_B_only | `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | +0.0645 | [-0.1935, +0.3226] | 0.8089 | 7/18/6 |
| coach_B_only | `dbox_inspired_guard` vs `dbox_inspired_clean` | +0.0323 | [-0.2581, +0.3226] | 1.0000 | 9/14/8 |
| coach_B_only | `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | +0.0323 | [-0.2903, +0.3548] | 1.0000 | 7/15/9 |
| coach_B_only | `bridge_contract_compact_guard` vs `dbox_inspired_guard` | -0.0645 | [-0.3548, +0.2258] | 0.8377 | 5/18/8 |
| priority60_adjudicated_plus_coachA | `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | +0.2903 | [-0.0968, +0.6452] | 0.2016 | 14/10/7 |
| priority60_adjudicated_plus_coachA | `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | +0.0645 | [-0.2258, +0.3548] | 0.8322 | 7/18/6 |
| priority60_adjudicated_plus_coachA | `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | +0.2903 | [-0.0323, +0.6129] | 0.1358 | 12/14/5 |
| priority60_adjudicated_plus_coachA | `dbox_inspired_guard` vs `dbox_inspired_clean` | +0.0000 | [-0.3548, +0.3548] | 1.0000 | 7/15/9 |
| priority60_adjudicated_plus_coachA | `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | +0.6774 | [+0.2581, +1.0645] | 0.0046 | 18/10/3 |
| priority60_adjudicated_plus_coachA | `bridge_contract_compact_guard` vs `dbox_inspired_guard` | +0.2258 | [-0.0645, +0.5484] | 0.2360 | 12/12/7 |
| priority60_adjudicated_plus_coachB | `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | +0.0323 | [-0.2258, +0.2903] | 1.0000 | 7/17/7 |
| priority60_adjudicated_plus_coachB | `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | +0.0323 | [-0.2258, +0.2903] | 1.0000 | 7/17/7 |
| priority60_adjudicated_plus_coachB | `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | +0.0968 | [-0.1290, +0.3226] | 0.5848 | 8/18/5 |
| priority60_adjudicated_plus_coachB | `dbox_inspired_guard` vs `dbox_inspired_clean` | +0.0645 | [-0.1935, +0.3226] | 0.8177 | 9/16/6 |
| priority60_adjudicated_plus_coachB | `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | +0.2581 | [-0.0645, +0.6129] | 0.2208 | 10/16/5 |
| priority60_adjudicated_plus_coachB | `bridge_contract_compact_guard` vs `dbox_inspired_guard` | +0.0000 | [-0.2581, +0.2581] | 1.0000 | 7/16/8 |

## 论文写法建议

可以写：Bridge Contract compact + Guard/Repair 在主脚手架 slice 上表现出更好的 overall/leakage trade-off，但大多数核心比较的不确定区间跨 0，结论应报告为 paired uncertainty 而非单一均值胜利。student-ready 与 rank 对评审口径敏感，应作为限制报告。

不要写：Guard-only 已实际降低最终回复泄露；Repair 的因果效果已由主实验证明；Bridge Contract 显著全面优于所有 baseline。

机器可读结果见 `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.csv` 和 `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.json`。
