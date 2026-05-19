# Real-Student Online AIChat Pilot Dry-Run Checklist v1

## 使用边界

本 checklist 用于 real-student online AIChat pilot 的正式采集前试跑。试跑只使用我们自己系统线上 AIChat / 教学场景中的真实学生问题，不使用第三方公开社区、洛谷讨论区、公开论坛、问答网站或社交媒体数据。试跑不修改 dialogue-state v3 主实验，不新增主实验 condition，不新增 baseline，不重算主表，不改变 evidence class，不上线 active mode，不改变学生可见回复，也不评估长期学习效果。

## 试跑目标

正式收集 20-30 个 pilot cases 前，先试跑 5 个 real-student dialogue-state cases。试跑只检查采集流程、脱敏流程、schema 字段、annotation guide 和 reporting template 是否可执行。

试跑通过后，再扩展到 20-30 个 cases。试跑不产生 main result，不进入 dialogue-state v3 主表，也不作为 7 个 offline conditions 的比较数据。

## 1. 样本来源检查

| check item | pass / revise / fail | note |
| --- | --- | --- |
| 5 个 cases 均来自我们自己系统线上 AIChat / 教学场景 |  |  |
| 未使用洛谷讨论区、题解区、评论区或任何公开社区内容 |  |  |
| 未使用第三方平台学生对话、公开求助帖、论坛或社交媒体数据 |  |  |
| 不需要抓取第三方页面才能理解学生问题 |  |  |
| 每个 case 都是一个可定义的 dialogue-state，而不是完整学习轨迹 |  |  |

## 2. 隐私与脱敏检查

| check item | pass / revise / fail | note |
| --- | --- | --- |
| 不记录真实姓名 |  |  |
| 不记录学校、班级、教师姓名 |  |  |
| 不记录手机号、邮箱、账号或登录名 |  |  |
| `student_id_hash` 已生成，且研究目录不保存可逆映射 |  |  |
| `problem_id_hash` 已生成，且不含公开社区链接或讨论串 ID |  |  |
| `timestamp_bucket` 使用粗粒度时间桶，不保存精确时间戳 |  |  |
| `student_message_redacted` 已脱敏 |  |  |
| `recent_dialogue_redacted` 已脱敏 |  |  |
| `student_code_excerpt_redacted` 已脱敏，且只保留必要片段 |  |  |
| `ai_response_current_system_redacted` 已脱敏 |  |  |
| 如需论文示例，只保留 paraphrased / anonymized example 版本 |  |  |
| `privacy_review_status` 可稳定判断 |  |  |
| `consent_status` 可稳定记录 |  |  |

## 3. Schema 字段可用性检查

使用 `real_student_online_case_schema_v1.json` 和 `real_student_online_pilot_data_collection_form_v1.csv` 试填 5 个 cases。

| check item | pass / revise / fail | note |
| --- | --- | --- |
| 所有 required fields 都能填写 |  |  |
| `student_code_excerpt_redacted` 可在无代码时留空 |  |  |
| `new_bridge_candidate` 可在无需新增候选时留空 |  |  |
| `forbidden_content` 可记录为字符串数组或 CSV 中的分隔列表 |  |  |
| `coach_missing_bridge_family` 的 enum 足以覆盖 5 个试跑 cases |  |  |
| `context_sufficiency` 的 allowed values 足以表达上下文状态 |  |  |
| `observed_next_turn_progress` 的 allowed values 足以表达下一轮状态 |  |  |
| `notes` 足以记录 ambiguity、redaction decision 或 taxonomy-fit concern |  |  |

## 4. Missing Bridge 标注检查

| check item | pass / revise / fail | note |
| --- | --- | --- |
| 每个 case 都能区分学生已知内容与当前 missing bridge |  |  |
| `coach_missing_bridge_instance` 不是完整题解或完整代码 |  |  |
| `coach_missing_bridge_family` 能映射到现有 taxonomy，或被标记为 `candidate_new_bridge` / `unclear_bridge` |  |  |
| `surface_anchor` 能描述真实对话中的算法/实现表面场景 |  |  |
| `expected_next_student_action` 能写成学生下一步可执行动作 |  |  |
| `forbidden_content` 能定义本轮不应直接补完的 critical bridge |  |  |

## 5. Context Sufficiency 检查

| check item | pass / revise / fail | note |
| --- | --- | --- |
| 能判断 case 是 `sufficient`、`partial`、`insufficient` 还是 `unclear` |  |  |
| 上下文不足的 case 没有被强行标注为普通 scaffold case |  |  |
| 需要澄清的 case 能在 reporting template 中计入 clarification need |  |  |
| 当前 AIChat 是否泄露 critical bridge 的判断只用于 pilot notes / appendix，不改变学生可见回复 |  |  |

## 6. Reporting Template 生成检查

用 5 个试跑 cases 填写 `real_student_online_reporting_template_20260519.zh.md` 的核心表格，检查是否可以生成：

| reporting item | pass / revise / fail | note |
| --- | --- | --- |
| number of pilot cases |  |  |
| number of students |  |  |
| bridge family coverage |  |  |
| surface anchor coverage |  |  |
| matches_existing_taxonomy: yes / no / uncertain |  |  |
| new bridge candidates |  |  |
| proportion requiring clarification |  |  |
| examples after paraphrase |  |  |
| limitations |  |  |
| statement: not used as main result |  |  |

## 7. 通过标准

5-case dry run 通过的最低条件：

1. 所有 5 个 cases 均来自我们自己系统线上 AIChat / 教学场景。
2. 所有 5 个 cases 均通过隐私脱敏检查，或明确标记为 `needs_redaction` / `excluded_privacy_risk` 并不进入报告。
3. schema required fields 可以实际填写。
4. 至少可以稳定判断 `context_sufficiency`。
5. 能对可用 cases 标注 missing bridge、surface anchor、forbidden content 和 expected next student action。
6. reporting template 能生成 pilot-level summary。
7. 试跑没有导致任何主实验修改、baseline 新增、active mode 上线或学生可见回复改变。

## 8. 扩展到 20-30 Cases 前的决策

| decision item | yes / no / needs revision | note |
| --- | --- | --- |
| 脱敏流程可执行 |  |  |
| schema 字段够用 |  |  |
| annotation guide 可执行 |  |  |
| reporting template 可生成 |  |  |
| 不需要修改 dialogue-state v3 主实验 |  |  |
| 不需要新增主实验 condition 或 baseline |  |  |
| 不需要改变学生可见回复或上线 active mode |  |  |

只有当上述项目通过后，才扩展到 20-30 个 real-student dialogue-state cases。扩展后仍只作为 taxonomy / rubric ecological validity check，可放入 Discussion / Appendix，不作为 main result。
