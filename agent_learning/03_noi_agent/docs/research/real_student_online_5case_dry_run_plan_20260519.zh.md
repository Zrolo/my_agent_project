# Real-Student Online 5-Case Dry Run Plan 20260519

## 使用边界

本 dry run 用于检查 real-student online pilot 的 case-specific annotation schema 和 annotation guide 是否可执行。它不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不把 pilot 写成 learning outcome study。

当前 5 个 dry-run cases 只来自已经选入 30 条 pilot candidate cases 的 screening pool。由于 consent/status gate 仍未完成，它们只能用于内部标注流程试跑，不能写成可公开报告的 deep-pilot evidence、学生示例或个案发现。

## 目标

本 dry run 只回答流程问题：

1. `real_student_online_case_schema_v1.json` 的字段是否足够标注真实学生 dialogue-state case。
2. `real_student_online_annotation_guide_v1.zh.md` 是否能指导 missing bridge、surface anchor、context sufficiency、forbidden content 和 expected next student action 的判断。
3. 标注者是否能在不公开学生原文、完整代码或完整 AI 回复的前提下，生成可审计的 paraphrased rubric fields。
4. 哪些字段容易出现歧义，需要在 annotation guide 中增加说明。

## 非目标

- 不报告模型表现。
- 不比较 7 个 offline conditions。
- 不评估长期学习效果。
- 不改变线上 AIChat 回复。
- 不新增 dialogue-state v3 evidence。
- 不把 5 cases 或 30 candidates 写成 main result。
- 不公开完整学生文本、完整代码、完整 AI 回复、逐个学生 hash 或逐个题目 hash。

## 5-Case Selection

5 个 dry-run cases 从 30 条 selected pilot candidate cases 中按覆盖性选择。选择不依据模型表现，也不依据是否支持论文主结论。

| dry_run_case_id | candidate_turn_id | screening_context_sufficiency | screening_rough_bridge_family | screening_surface_anchor | screening_help_seeking_type | screening_confidence | dry_run_role |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `dryrun_20260519_01` | `rs_screen_20260519_001` | sufficient | debugging_bridge | debugging trace | debugging | high | high-confidence debugging case |
| `dryrun_20260519_02` | `rs_screen_20260519_004` | partial | unclear | conceptual hint request | conceptual_hint | low | partial-context / unclear-family case |
| `dryrun_20260519_03` | `rs_screen_20260519_022` | sufficient | aggregation_contribution_bridge | prefix/difference contribution | implementation | medium | aggregation / contribution marking case |
| `dryrun_20260519_04` | `rs_screen_20260519_028` | partial | implementation_bridge | implementation boundary | implementation | medium | partial-context implementation-boundary case |
| `dryrun_20260519_05` | `rs_screen_20260519_032` | sufficient | data_structure_bridge | tree / graph traversal | conceptual_hint | medium | data-structure / tree-anchor conceptual case |

## Annotation Inputs

标注时可使用内部非公开材料作为输入，但不得把以下内容写入公开文档或公开补充材料：

- 完整学生原文；
- 完整 recent dialogue；
- 完整学生代码；
- 完整当前 AIChat 回复；
- 真实姓名、学校、手机号、邮箱、账号；
- 原始 session id、student id、problem id；
- hash salt 或 ID 映射表。

公开或可提交的 dry-run 输出只能包含：

- candidate-level aggregate feasibility；
- paraphrased missing bridge；
- paraphrased forbidden content；
- paraphrased acceptable reveal；
- paraphrased expected next student action；
- taxonomy-fit / field-sufficiency notes；
- unresolved ambiguity categories。

## Dry-Run Steps

1. 对 5 个 `candidate_turn_id` 读取内部脱敏候选材料。
2. 确认材料不含直接身份信息；若仍需脱敏，标记 `privacy_review_status=needs_redaction` 并停止该 case。
3. 按 annotation guide 标注 missing bridge、surface anchor、context sufficiency、forbidden content、acceptable reveal、expected next student action。
4. 判断是否能映射到现有 cognitive bridge family。
5. 记录 schema 是否够用：字段缺失、allowed values 不足、歧义点、需要 coach adjudication 的地方。
6. 只输出 feasibility summary，不输出学生原文或 case-level teaching claims。

## Expected Dry-Run Output

Dry run 完成后应生成一个内部 summary，至少包括：

- 5 cases 中有多少可以完整填写 schema；
- 有多少需要 additional redaction；
- 有多少需要 coach discussion；
- 有多少能映射到现有 bridge family；
- 哪些字段最容易不够用；
- annotation guide 需要补充的规则；
- 明确声明：not main result, not learning outcome, not reportable deep-pilot evidence before consent/status gate。

## Claim Gate

| check | required result |
| --- | --- |
| 是否新增实验 | no |
| 是否新增主实验 condition | no |
| 是否修改 dialogue-state v3 主表 | no |
| 是否改变 evidence class | no |
| 是否改变学生可见回复 | no |
| 是否使用第三方公开社区数据 | no |
| 是否把 5-case dry run 写成 main result | no |
| 是否把 pending-consent candidates 写成 reportable evidence | no |
