# Real-AIChat-Replay-30/50 Protocol

Date: 2026-05-20

## 使用边界

Real-AIChat-Replay-30/50 是 real-log-grounded offline counterfactual validation。它不修改线上 AIChat，不展示给学生，不新增 dialogue-state v3 main condition，不重算 dialogue-state v3 主表，不并入主结果，也不评估 learning outcome。

## D1. 目的

Real-AIChat-Replay-30/50 的目的：

- 在真实学生起点上检查 7 个 fixed offline harnesses 是否仍表现出不同 bridge-preserving behavior。
- 作为 auxiliary real-log-grounded offline counterfactual validation。
- 不作为 headline result。
- 不并入 dialogue-state v3 主表。
- 不改变线上 AIChat。
- 不评估 learning outcome。

## D2. 为什么需要 Replay

Real-AIChat-100 中的 observed current AIChat response 只来自当前线上系统，不是 7 个 offline harnesses。因此：

- Real-AIChat-100 不能比较 7 conditions。
- 如果要比较 7 fixed harnesses，必须在同一真实学生起点上离线重新生成 7 个 harness responses。
- 这叫 offline counterfactual replay，不是 online deployment。

## D3. Replay Subset Selection

Replay-30 优先从 Real-AIChat-100 中选择 30 个 context-sufficient cases；时间允许再扩到 Replay-50。

选择标准：

- `context_sufficiency_light=sufficient` 优先，`partial` 可少量保留。
- `missing_bridge_identifiable=yes`。
- `privacy_review_status=passed` 或至少 not failed。
- consent/reporting gate 如果 pending，则只做内部 review 和 aggregate reporting。
- 覆盖不同 bridge family、surface anchor、help-seeking type、student 和 problem。
- 不按模型表现选择。
- 不按 observed current AIChat 好坏选择。
- 不按想证明 Bridge Contract 有利选择。

## D4. 7 个 Fixed Offline Harnesses

Replay 使用与 dialogue-state v3 一致的 7 个 offline harnesses，不新增 main condition。当前稿件 / manifest 对应名称为：

| harness name | replay interpretation |
| --- | --- |
| `enhanced_prompt_only_clean` | fixed offline harness |
| `codehelp_codeaid_clean` | fixed offline harness |
| `dbox_inspired_clean` | fixed offline harness; not faithful DBox reproduction |
| `dbox_inspired_guard` | fixed offline guard-instrumented harness |
| `bridge_guided_dbox_style_guard` | fixed offline bridge-guided harness |
| `bridge_contract_compact_guard` | fixed offline Bridge Contract + guard harness |
| `bridge_contract_compact_guard_repair` | fixed offline Bridge Contract + Guard/Repair harness |

如果后续发现名称与 evidence manifest 不一致，必须以 manifest 为准，并在 patch log 中记录 TODO。Replay 中这些仍是 offline harnesses，不是线上部署，不是新增 dialogue-state v3 main condition。

## D5. Replay Input Packet

每个 replay case 必须冻结以下输入：

- `real_aichat_case_id`
- problem/task summary
- key constraints / I/O summary
- recent dialogue summary
- current student message paraphrase or private reference
- student code excerpt reference, redacted/private if any
- current learner state summary
- missing bridge candidate
- forbidden bridge content
- acceptable hint boundary
- expected next student action
- context sufficiency flag
- privacy/reporting status

公开材料不得包含学生原文、完整代码、完整 AIChat 回复、真实身份、hash salt 或可逆映射。

## D6. Generation Rule

- 离线生成。
- 不展示给学生。
- 不修改线上回复。
- 记录 harness version、model version、prompt version、decoding settings 和 generation date。
- 如果当前执行环境不能调用模型生成，则只创建 protocol/template，不伪造 response。

## D7. Blind Coach Review

教练盲审要求：

- response order randomized。
- condition name hidden。
- current observed AIChat response 如果参与 review，必须标记为 observed reference，不纳入 7-condition ranking。
- 每个 response 标注：
  - `bridge_leakage_severity`
  - `answer_or_code_leakage`
  - `helpfulness`
  - `learner_burden`
  - `scaffold_quality`
  - `student_ready`
  - `safe_ready`
  - `coach_confidence`
  - `context_sufficiency_for_judgment`
  - `notes_no_raw_text`

## D8. Double Review

建议：

- Replay-30 至少 10-15 cases 由第二教练复核。
- Replay-50 至少 15-20 cases 由第二教练复核。
- 不把 Coach A/B 写成 final gold。
- 只报告 disagreement / adjudication summary。

## D9. Reporting

只能写：

- auxiliary validation。
- real-log-grounded counterfactual replay。
- same-starting-state offline comparison。
- aggregate trends。
- paired W/T/L 或 bounded descriptive comparison。

不能写，以下措辞 must be avoided：

- deployed system superiority。
- learning outcome improvement。
- online 7-condition experiment。
- main result update。
- Bridge Contract significantly dominates。
- Repair causal effect proven by replay。

## Execution Status

当前仅创建 protocol、case schema/template、coach-review schema/template 和 validators。没有生成 replay responses，没有进行教练盲审，也没有创建 Replay-30 / Replay-50 实际结果。
