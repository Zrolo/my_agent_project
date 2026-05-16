# Dialogue-State v3 50-case Case/Source Gate 通过记录 20260516

本记录说明 dialogue-state v3 50-case 数据集已完成 Coach A case/source review gate。该状态表示 case 本身已经通过题源、上下文、学生话术、桥梁标签、禁止内容和成功标准复核；它不表示 AI 回复已被盲评，也不表示 gold/reference label 已完成。

## 审核流程

1. Full review：Coach A 审核 50 条 case/source。
   - 接受：32
   - 修改：18
   - 丢弃：0
   - 讨论：0
2. Round1 targeted re-check：Coach A 复核 18 条修订样本。
   - 接受：15
   - 仍需修改：3
3. Round2 replacement re-check：替换 3 条 `problem_bridge_mismatch` 样本后，Coach A 复核 3 条 replacement candidates。
   - 接受：3
   - 修改：0

## Round2 replacement

| slot | 原题源 | 新题源 | 决策 |
|---|---|---|---|
| `dialogue_v3_035_data_structure_operation_semantics` | P2672《推销员》 | P3374《【模板】树状数组 1》 | 接受 |
| `dialogue_v3_036_correctness_invariant` | P10709《Party》 | P1223《排队接水》 | 接受 |
| `dialogue_v3_037_correctness_invariant` | P10728《Swords》 | P1080《国王游戏》 | 接受 |

## Reviewed candidate 数据集

已导出：

- `docs/research/bridgebench_cp_dialogue_state_v3_50_reviewed_candidate.jsonl`
- `docs/research/dialogue_state_v3_50_reviewed_candidate_validation_report_20260516.json`

校验摘要：

- `row_count=50`
- `reference_label_status=reviewed_candidate`：50 条
- `problem_source_platform_counts={"luogu": 50}`
- `recent_dialogue_distribution={"none": 10, "short": 25, "long": 15}`
- `student_code_excerpt_distribution={"none": 33, "present": 17}`
- `student_message_length_distribution={"short": 20, "medium_short": 15, "medium_long": 10, "long": 5}`
- `error_count=0`

## 重要边界

`reviewed_candidate` 只表示 case/source 通过审核。它不是：

- gold data；
- adjudicated reference；
- Coach response review result；
- formal frozen reference。

后续如果要进入论文 headline result，仍需：

1. 冻结 prompt / rubric / grader；
2. 用 reviewed candidate 生成 AI responses；
3. 做匿名人类教练盲评；
4. 至少做部分双评审和 agreement / adjudication；
5. 做 paired analysis 和 LLM Judge calibration。

## 下一步

现在可以进入 **prompt/rubric freeze gate**。在 freeze 前不应继续改 case 内容；若必须改，应重新打开 case/source review gate 并记录 patch。
