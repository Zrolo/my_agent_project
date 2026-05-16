# Dialogue-State v3 Round2 Replacement Candidates 20260516

本记录说明 Coach A round2 复核后，对 3 条 `problem_bridge_mismatch` 样本所做的 replacement 处理。当前记录的是 case/source review gate 内的数据修订，不评价 AI 回复质量，也不冻结正式实验。

## 2026-05-16 状态更新

Coach A 已复核 3 条 replacement candidates，结果全部接受：

- `dialogue_v3_035_data_structure_operation_semantics`：接受
- `dialogue_v3_036_correctness_invariant`：接受
- `dialogue_v3_037_correctness_invariant`：接受

因此，dialogue-state v3 50-case 已升级为 `reviewed_candidate`。详见 [dialogue_state_v3_case_source_gate_pass_20260516.zh.md](dialogue_state_v3_case_source_gate_pass_20260516.zh.md)。

## 被替换的问题样本

| slot | 原题源 | 原问题 | 决策 |
|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | P2672《推销员》 | 更像贪心/贡献选择，不适合 update/query 数据结构维护语义 | 替换 |
| `dialogue_v3_036_correctness_invariant` | P10709《Party》 | 更像相邻限制 DP 状态/转移，不适合相邻交换证明 | 替换 |
| `dialogue_v3_037_correctness_invariant` | P10728《Swords》 | 更像排序后支配关系/扫描不变量，不是交换论证 | 替换 |

## 新 replacement candidates

| slot | 新题源 | 桥梁桶 | 选择理由 |
|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | P3374《【模板】树状数组 1》 | 数据结构操作/维护语义 | 题面明确有单点加和区间求和，适合测试 update/query 维护摘要语义 |
| `dialogue_v3_036_correctness_invariant` | P1223《排队接水》 | 贪心/不变量/正确性 | 适合用相邻交换比较两个排队顺序对总等待时间的影响 |
| `dialogue_v3_037_correctness_invariant` | P1080《国王游戏》 | 贪心/不变量/正确性 | 适合用相邻交换比较两个大臣前后顺序对局部最坏奖励的影响 |

## 已生成产物

- `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- `docs/research/dialogue_state_v3_50_source_and_case_review.en.xlsx`
- `docs/research/coach_seed_labeling_workbook_dialogue_state_v3_50.zh.xlsx`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3.zh.xlsx`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3.en.xlsx`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3_20260516.json`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3_20260516.zh.md`
- `docs/research/dialogue_state_v3_case_review_round2_replacement_recheck_3_20260516.md`

## 复核要求（已完成）

Coach A 已只复核 3 条 replacement candidates，重点判断：

1. 题源是否适合当前桥梁桶；
2. `recent_dialogue -> student_message -> missing_bridge -> success_criteria` 是否连贯；
3. 禁止内容是否不过严、不过松；
4. 是否可进入正式 response generation 前的 `reviewed_candidate` 集。

## 当前状态

这 3 条已通过，50-case 已导出 `reviewed_candidate` 版本。该状态仍不能称为 gold；它只表示 case/source gate 已通过，后续仍需 prompt/rubric freeze、AI response generation、人类盲评、部分双评审和 adjudication。
