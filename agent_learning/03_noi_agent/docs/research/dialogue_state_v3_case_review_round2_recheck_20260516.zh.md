# Dialogue-State v3 Coach A Round2 Targeted Re-check 20260516

本记录汇总 Coach A 对 18 条 round1 修订样本的 targeted re-check 结果。该阶段仍是 case/source review gate，不评价任何 AI condition 的回复质量，也不改变 prompt。

## 2026-05-16 解决状态

本记录中的 3 条 unresolved slot 已通过 replacement 处理解决：

- `dialogue_v3_035_data_structure_operation_semantics`：替换为 P3374《【模板】树状数组 1》，Coach A 接受。
- `dialogue_v3_036_correctness_invariant`：替换为 P1223《排队接水》，Coach A 接受。
- `dialogue_v3_037_correctness_invariant`：替换为 P1080《国王游戏》，Coach A 接受。

因此，dialogue-state v3 50-case 已导出 `reviewed_candidate` 版本。详见 [dialogue_state_v3_case_source_gate_pass_20260516.zh.md](dialogue_state_v3_case_source_gate_pass_20260516.zh.md)。

## 输入文件

- `/Users/kongyouli/Downloads/dialogue_state_v3_case_review_coach_A_round1_recheck_18_zh_rechecked.xlsx`

## 结构化结果

- 复核样本数：18
- `accept`：15
- `revise`：3
- `drop`：0
- `discuss`：0
- 需要后续处理的问题类型：
  - `problem_bridge_mismatch`：3

汇总文件：

- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_summary_20260516.json`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_summary_20260516.zh.md`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_summary_20260516.md`

## 仍需处理的样本

| case_id | 当前桥梁桶 | Coach A 复核意见 | 处理建议 |
|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | 数据结构操作/维护语义 | P2672 更像贪心/贡献选择题，当前 update/query 和节点摘要量不贴题 | 不再硬修。优先替换为真正有 update/query 或维护摘要的题；若保留 P2672，应移出数据结构桶 |
| `dialogue_v3_036_correctness_invariant` | 正确性/不变量 | P10709 本质更像状态表示/转移递推的相邻限制 DP，不适合相邻交换证明 | 不再硬修。优先替换为真正需要交换论证的贪心题；若保留 P10709，应移入 DP 状态/转移桶 |
| `dialogue_v3_037_correctness_invariant` | 正确性/不变量 | P10728 更像排序后判断支配关系/维护扫描不变量，不是两个选择顺序互换 | 可改成支配关系/扫描不变量样本，或替换为交换论证题；进入正式主集前必须再复核 |

## 决策

这 3 条不应直接进入正式 response generation。原因不是学生话术小修，而是题目、桥梁桶和 missing bridge 之间仍有结构性错配。继续把它们硬塞进原桶，会污染后续系统比较。

推荐下一步：

1. 保留 47 条已通过/可用样本。
2. 为 3 条 unresolved slot 生成或筛选 replacement candidates：
   - 1 条真实数据结构 update/query 维护语义样本；
   - 2 条真正适合正确性/不变量，尤其是交换论证、支配关系或扫描不变量的样本。
3. 生成 3 条 replacement re-check workbook，只让 Coach A 审这 3 条。
4. 3 条通过后，再导出 `reviewed_candidate` 版本。

## 当前状态

该记录描述的是 replacement 前的 round1 re-check 状态。replacement 复核通过后，50-case 已升级为 `reviewed_candidate`，但仍不能称为 gold，也不能直接进入论文 headline result；后续仍需 prompt/rubric freeze、AI response blind review、部分双评审和 adjudication。
