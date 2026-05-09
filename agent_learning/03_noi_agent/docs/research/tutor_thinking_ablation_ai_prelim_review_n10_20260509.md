# Tutor Thinking Ablation AI Preliminary Review n=10 2026-05-09

Status: AI preliminary review only. This is not coach gold and must not be used as final paper evidence without human review.

Chinese version: `docs/research/tutor_thinking_ablation_ai_prelim_review_n10_20260509.zh.md`

## Summary

| Thinking mode | Rows | Avg total score | Avg leakage-control score | Avg scaffold score | Any leakage | Major/answer leakage | Pairwise wins/ties |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `enabled` | 10 | 8.700 | 0.900 | 1.100 | 6/10 | 5/10 | 3/10 |
| `disabled` | 10 | 9.700 | 1.300 | 1.400 | 4/10 | 3/10 | 8/10 |

## Interpretation

- On 10 cases, `thinking=disabled` is much faster in the latency summary and has a slightly higher AI-preliminary average total score.
- The quality picture is still mixed: disabled wins many cases because it is often more concise and less revealing, but it still has major leakage on some bridge-completion cases.
- Both modes have serious leakage failures in this preliminary review. This supports using thinking mode as a routing variable rather than a global default switch.
- This is an AI preliminary review. A coach should review at least the disagreement and major-leakage cases before any paper claim.

## Per-Case Preliminary Review

| Case | Thinking | Total | Leakage label | Rank | Short note |
| --- | --- | ---: | --- | ---: | --- |
| `cp_bridge_001` | enabled | 5 | `no_leakage` | 2 | AI 预评：回复偏到“不要用 ASCII 画图/用表格表达”，没有真正处理端点/LCA 标记缺口。安全但不贴题。 |
| `cp_bridge_001` | disabled | 10 | `no_leakage` | 1 | AI 预评：用 1-2-3 小路径让学生直觉标记，安全且有下一步，但还没有引出向上汇总或 LCA 修正。 |
| `cp_bridge_002` | enabled | 9 | `major_bridge_leakage` | 2 | AI 预评：直接给出 check(4)=false、check(3)=true，并说明可行性方向，基本补完当前 check 语义桥。 |
| `cp_bridge_002` | disabled | 12 | `no_leakage` | 1 | AI 预评：用 mid=5 让学生自己判断是否可行，没有直接给 true/false 映射，脚手架清楚。 |
| `cp_bridge_003` | enabled | 9 | `major_bridge_leakage` | 2 | AI 预评：直接列出“前 i 个物品容量 j 最大价值”等状态定义候选，给出了核心状态语义。 |
| `cp_bridge_003` | disabled | 11 | `minor_bridge_leakage` | 1 | AI 预评：用单株药草问 dp[3] 存什么，提示较强但仍要求学生构造格子含义。 |
| `cp_bridge_004` | enabled | 11 | `minor_bridge_leakage` | 2 | AI 预评：直接指出当前药草只有采/不采两种情况，贴合转移桥但给了较强结构。 |
| `cp_bridge_004` | disabled | 12 | `no_leakage` | 1 | AI 预评：用“之前背包里有没有这株药”让学生分辨来源状态，更少直接补转移。 |
| `cp_bridge_005` | enabled | 9 | `major_bridge_leakage` | 2 | AI 预评：直接解释 lazy 是父节点已更新、子节点未同步并说出准确语义，完成了当前语义桥。 |
| `cp_bridge_005` | disabled | 12 | `no_leakage` | 1 | AI 预评：用 [1,2] 子节点是否已加 5 的选择题让学生判断，贴合 lazy 语义且较安全。 |
| `cp_bridge_006` | enabled | 9 | `major_bridge_leakage` | 2 | AI 预评：完整解释 Trie 共享前缀、O(L) 查询和节点计数，基本直接回答了证明桥。 |
| `cp_bridge_006` | disabled | 9 | `major_bridge_leakage` | 1 | AI 预评：也直接解释共享前缀和路径终点子树，仍是 major leakage；但例子更紧凑、学生下一步更明确。 |
| `cp_bridge_007` | enabled | 12 | `no_leakage` | 2 | AI 预评：没有直接确认 trie，要求学生找前缀证据；合格 L1，但问题稍泛。 |
| `cp_bridge_007` | disabled | 12 | `no_leakage` | 1 | AI 预评：同样不直接确认算法名，并明确要求找“前缀/互为前缀”的题面证据；稍更聚焦。 |
| `cp_bridge_008` | enabled | 9 | `major_bridge_leakage` | 1 | AI 预评：完整说明 a[mid]==x 时 r=mid 的原因，补完左边界桥；表达清楚但泄露重。 |
| `cp_bridge_008` | disabled | 8 | `major_bridge_leakage` | 2 | AI 预评：同样直接说出 r=mid 和原因，泄露重；下一步偏“你明白了吗”，比 enabled 弱。 |
| `cp_bridge_009` | enabled | 12 | `no_leakage` | 1 | AI 预评：用活动表让学生填结果，保留交换论证给学生发现，贴合正确性桥。 |
| `cp_bridge_009` | disabled | 9 | `major_bridge_leakage` | 2 | AI 预评：直接给出交换论证骨架“最优解没选 x 就换 y”，完成了正确性桥。 |
| `cp_bridge_010` | enabled | 2 | `no_leakage` | 1 | AI 预评：没有利用已有题目上下文，只要求题号或卡住行；安全但基本无教学价值。与 disabled 同等差。 |
| `cp_bridge_010` | disabled | 2 | `no_leakage` | 1 | AI 预评：同样没有处理倒序枚举桥，只要求题号或卡住行；安全但基本无教学价值。与 enabled 同等差。 |

## Output Files

- Filled blind-style CSV: `docs/research/coach_response_review_workbook_deepseek_flash_thinking_n10.ai_prelim.csv`
- Keyed AI preliminary CSV: `docs/research/coach_response_review_workbook_deepseek_flash_thinking_n10.ai_prelim.keyed.csv`
