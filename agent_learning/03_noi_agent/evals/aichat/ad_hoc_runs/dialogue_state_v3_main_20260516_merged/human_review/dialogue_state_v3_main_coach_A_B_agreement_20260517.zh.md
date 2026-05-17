# Dialogue-State v3 Coach A / Coach B Agreement Report (2026-05-17)

本报告比较 Coach A round1 与 Coach B round1 的 350 条完全重叠复评。它用于衡量评分稳定性和筛选裁决样本。

| metric | value |
| --- | --- |
| overlap rows | 350 |
| overall exact | 0.2829 |
| overall within 1 | 0.8429 |
| overall weighted kappa | 0.0242 |
| overall mean delta B-A | -0.5057 |
| show exact | 0.3429 |
| show weighted kappa | -0.0077 |
| leakage exact | 0.6714 |
| leakage weighted kappa | 0.2433 |
| critical binary exact | 0.9029 |
| critical binary kappa | 0.2511 |
| critical precision B vs A | 0.5385 |
| critical recall B vs A | 0.2 |
| rank mean Spearman by case | 0.0264 |
| top-1 agreement cases | 10/50 |
| last-place agreement cases | 10/50 |
| flagged disagreement rows | 244 |


## 解释

- `overall within 1` 高，说明总体质量分虽然口径不同，但大多差异在 1 分内。
- `critical recall B vs A` 较低时，表示 Coach B 标出的 critical leakage 少于 Coach A；这类分歧必须人工裁决。
- `rank mean Spearman` 反映同题 7 条回复排序的一致性；若偏低，说明系统偏好仍不稳定。
- 已导出严重分歧清单：`dialogue_state_v3_main_coach_A_B_disagreements_20260517.csv`。
