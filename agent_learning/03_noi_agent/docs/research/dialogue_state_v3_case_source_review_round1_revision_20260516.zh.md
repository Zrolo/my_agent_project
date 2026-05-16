# Dialogue-State v3 50-case Coach A Round1 修订记录 20260516

本记录说明 Coach A 完整审核 `dialogue_state_v3_50_source_and_case_review_zh6_case_source_reviewed (1).xlsx` 后，对 dialogue-state v3 50-case 草稿所做的第一轮修订。该阶段仍是 case/source review gate，不评价任何 AI condition 的回复质量。

## Coach A 审核结果

- 审核样本数：50
- `accept`：32
- `revise`：18
- `drop`：0
- `discuss`：0
- 主要问题类型：
  - `context_mismatch`：11
  - `bridge_label_issue`：7
- 审核置信度：
  - `high`：42
  - `medium`：8

原始结构化汇总见：

- `docs/research/dialogue_state_v3_case_review_summary_coach_A_20260516.json`
- `docs/research/dialogue_state_v3_case_review_summary_coach_A_20260516.zh.md`
- `docs/research/dialogue_state_v3_case_review_summary_coach_A_20260516.md`

## 已修订的样本

本轮保留原 50 条题源和桥梁桶配额，不重排数据集。修订集中在学生当前回复、跟随状态证据、局部 missing bridge 或 success criteria，使 `recent_dialogue -> student_message -> missing_bridge -> success_criteria` 链条更一致。

| 范围 | 桥梁桶 | Coach A 问题 | 修订方式 |
|---|---|---|---|
| `dialogue_v3_027`-`030` | 贡献汇总/差分/前缀 | 学生当前回复像二分 true/边界方向，不像回应贡献标记 | 改成围绕加减标记、抵消点、前缀/公共点汇总的位置问题 |
| `dialogue_v3_031`-`035` | 数据结构操作/维护语义 | 学生回复偏二分、调试或实现边界，未聚焦 update/query 维护语义 | 改成节点/结构里维护什么摘要、一次 update 后哪个维护量应变化、query 为什么能由维护量拼出 |
| `dialogue_v3_036`-`040` | 正确性/不变量 | 近期对话讲交换/不变量，但当前回复转向样例错误、打印量或更新顺序 | 改成比较相邻选择交换后哪个量不变或不变差、如何形成局部交换理由 |
| `dialogue_v3_044` | 实现边界 | 学生问单字符/空格，但 missing bridge 过泛 | 改成输出图中单个字符位置如何对应题面方块的格子/边/角 |
| `dialogue_v3_045`-`047` | 调试证据/最小反例 | 当前问题偏概念语义，不像调试证据 | 改成最小反例、最小坏样例、中间变量检查点或最小时间点手算 |

## 保持不变的设计约束

- 题源仍为洛谷真实题源，旧线上 AI 回复不进入数据集。
- 学生问题长度分布仍保持：`short=20 / medium_short=15 / medium_long=10 / long=5`。
- 轮次分布仍保持：`initial=10 / followup=40`。
- 学生跟随状态仍为：`NA=10 / F1=6 / F2=19 / F3=10 / F4=5`。
- 当前版本仍标记为 `draft_needs_coach_review`，不称为 gold。

## 生成与验证

已重新生成：

- `docs/research/bridgebench_cp_dialogue_state_v3_50_draft.jsonl`
- `docs/research/dialogue_state_v3_50_source_and_case_review.zh.xlsx`
- `docs/research/dialogue_state_v3_50_source_and_case_review.en.xlsx`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18.zh.xlsx`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18.en.xlsx`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_20260516.json`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_20260516.zh.md`
- `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18_20260516.md`
- `docs/research/dialogue_state_v3_generation_report_20260513.json`
- `docs/research/dialogue_state_v3_validation_report_20260513.json`

验证结果：

- `row_count=50`
- `ok=true`
- `error_count=0`

## 下一步

这版应把 `docs/research/dialogue_state_v3_case_review_coach_A_round1_recheck_18.zh.xlsx` 发回 Coach A 做 targeted re-check，重点只看 18 条修订样本是否已经解决 `context_mismatch` 和 `bridge_label_issue`。如果 18 条通过，即可生成 `reviewed_candidate` 版本，然后进入 prompt/rubric freeze 和 AI response generation 前的最终检查。
