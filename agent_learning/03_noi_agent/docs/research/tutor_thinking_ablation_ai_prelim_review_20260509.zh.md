# Tutor Thinking 消融 AI 预评测 2026-05-09

状态：仅 AI 初步预评，不是教练 gold，不能直接作为论文最终证据。

英文版：`docs/research/tutor_thinking_ablation_ai_prelim_review_20260509.md`

## 汇总

| Thinking 模式 | 行数 | 平均总分 | 平均泄露控制分 | 任意泄露 | 严重/答案泄露 | 成对胜出 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `enabled` | 3 | 9.667 | 0.667 | 3/3 | 1/3 | 2/3 |
| `disabled` | 3 | 10.000 | 1.333 | 1/3 | 1/3 | 1/3 |

## 解释

- `thinking=disabled` 在延迟 smoke 中明显更快，但这份 AI 预评不能证明它可以直接作为线上默认。
- 成对偏好是混合的：enabled 在树上差分和 DP 状态两个样本上更好，disabled 在二分 check 样本上更好。
- 最大风险仍然是关键桥梁泄露。disabled 在 DP 状态样本上有一次 major leakage；enabled 在二分 check 样本上有一次 major leakage，另外两个样本有 minor leakage。
- 这份文件应该作为下一步教练复核的调试材料，不是 adjudicated gold。

## 逐样本预评

| 样本 | Thinking | 总分 | 泄露标签 | 成对排序 | 简短判断 |
| --- | --- | ---: | --- | ---: | --- |
| `cp_bridge_001` | enabled | 11 | `minor_bridge_leakage` | 1 | 更贴近树上差分端点/LCA 标记缺口，但端点 +1 给了较强线索。 |
| `cp_bridge_001` | disabled | 9 | `no_leakage` | 2 | 安全但偏弱，容易让学生答成“路径上每个点都 +1”。 |
| `cp_bridge_002` | enabled | 7 | `major_bridge_leakage` | 2 | 直接给出 check true/false 方向，并跳到边界更新，泄露偏重。 |
| `cp_bridge_002` | disabled | 12 | `no_leakage` | 1 | 用具体 mid 让学生自己判断 true/false，单焦点清楚。 |
| `cp_bridge_003` | enabled | 11 | `minor_bridge_leakage` | 1 | 用表格让学生解释一个格子的语义，贴合状态桥，但行列含义提示较多。 |
| `cp_bridge_003` | disabled | 9 | `major_bridge_leakage` | 2 | 速度快、下一步清楚，但直接说出 dp[j] 的核心语义。 |

## 输出文件

- 已填盲评格式 CSV：`docs/research/coach_response_review_workbook_deepseek_flash_thinking_smoke3.ai_prelim.csv`
- 带模型条件的 AI 预评 CSV：`docs/research/coach_response_review_workbook_deepseek_flash_thinking_smoke3.ai_prelim.keyed.csv`
