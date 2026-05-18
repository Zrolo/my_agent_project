# Dialogue-State v3 Pairwise Win/Tie/Loss 20260517

## 范围

本文件复用现有 `dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.csv/json`，只在 `main_scaffold_eval` 31 个 case 上做同题成对比较。`Δ overall` 是前者减后者；bootstrap CI 是 case-level paired bootstrap 95% CI；`paired p` 是随机符号翻转 permutation test。负的 `Δ major+answer` 表示前者 critical/answer 级泄露更少。

## 主口径：priority60 adjudicated + Coach A

| comparison | n | W/T/L | Δ overall | 95% CI | paired p | Δ safe-ready | Δ major+answer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | 31 | 14/10/7 | +0.290 | [-0.097, +0.645] | 0.2016 | -1 | -2 |
| `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | 31 | 7/18/6 | +0.065 | [-0.226, +0.355] | 0.8322 | -1 | +0 |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | 31 | 12/14/5 | +0.290 | [-0.032, +0.613] | 0.1358 | +1 | -2 |
| `dbox_inspired_guard` vs `dbox_inspired_clean` | 31 | 7/15/9 | +0.000 | [-0.355, +0.355] | 1.0000 | +2 | +0 |
| `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | 31 | 18/10/3 | +0.677 | [+0.258, +1.065] | 0.0046 | +12 | -7 |
| `bridge_contract_compact_guard` vs `dbox_inspired_guard` | 31 | 12/12/7 | +0.226 | [-0.065, +0.548] | 0.2360 | +0 | -2 |

## 解释口径

| comparison | paper wording |
| --- | --- |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_guard` | 可以写成 overall / leakage trade-off 趋势优势；CI 跨 0，不能写显著优势。 |
| `bridge_contract_compact_guard_repair` vs `bridge_contract_compact_guard` | 不支持 Repair 因果结论；W/T/L 接近、critical 泄露相同，需要 same-candidate stress test。 |
| `bridge_contract_compact_guard_repair` vs `dbox_inspired_clean` | 可以写成趋势优势；CI 仍跨 0，措辞要保守。 |
| `dbox_inspired_guard` vs `dbox_inspired_clean` | Guard-only 不能解释为最终回复修复收益；当前链路只是 guard-instrumented。 |
| `codehelp_codeaid_clean` vs `enhanced_prompt_only_clean` | 该比较在主口径下较稳，说明 strong prompt-only 在 dialogue-state CP tutoring 中不是足够稳定的上界。 |
| `bridge_contract_compact_guard` vs `dbox_inspired_guard` | 可以写成 critical-leakage control 趋势更好；overall CI 跨 0。 |

## Sensitivity 摘要

- Coach A only 下，`bridge_contract_compact_guard` 的 overall 略高于 repair-enabled 版本，但 `bridge_contract_compact_guard_repair` 的 major+answer leakage 更低。
- Coach B only 下，多数 Δ overall 接近 0，说明 B 的严格口径压缩了整体分差。
- priority60 adjudicated + Coach B 下，Bridge repair 的 overall 仍略高于 DBox variants，但差异很小。
- 因此论文应报告 paired uncertainty，而不是只报均值排名。

机器可读完整 sensitivity 位于 `evals/aichat/ad_hoc_runs/dialogue_state_v3_main_20260516_merged/human_review/dialogue_state_v3_main_scaffold_paired_uncertainty_20260517.csv`。
