# Implementation Status Matrix

Date: 2026-05-11; updated 2026-05-12

本文件用于区分“当前线上已经发生的行为”“离线研究工具链”“shadow/proposed 设计”和“尚未实现的计划”。论文和外部审查不得把这些状态混写。

## 状态标签

| Status | 含义 |
|---|---|
| `online_active` | 已在学生在线 AIChat 主流程中生效 |
| `offline_eval_only` | 只在离线研究 runner、报告、workbook 或 smoke eval 中使用 |
| `teacher_tool_only` | 只在教师端/研究端工具使用，不影响学生回复 |
| `shadow_or_proposed` | 已有设计或计划，但未改变学生可见回复 |
| `not_implemented` | 尚未实现 |
| `doc_only` | 仅文档化，作为边界或计划 |

## Online AIChat Baseline

| Module / Behavior | Status | Evidence / Notes | 论文表述 |
|---|---|---|---|
| `chat()` main online path | `online_active` | 当前学生 AIChat 入口仍是既有 `chat()` 路径 | 可作为 `current_system` baseline |
| rules / `analyze_student_turn()` | `online_active` | 用于快速规则风险和 tutor control 信号 | 可说 rules 是当前 baseline 的一部分 |
| legacy learning phase judge | `online_active` | 当前流程文档已记录 | 可作为 baseline path，不作为新贡献 |
| Pedagogical Judge v2 soft control | `online_active` | 主要影响 `tutor_control`，不直接更新 hard gate | 不能说它已经是 hard bridge controller |
| model self-reported `[LEVEL:Lx]` hard gate | `online_active` | 当前 hard gate 依赖模型自报 level | 可作为 baseline limitation |
| online answer-style toggle | `online_active` | 2026-05-12 上线；默认 `简洁提示=current_system`，可选 `教练引导=enhanced_prompt_only_clean`；只改变 prompt-only guidance，不接入 Bridge Judge / Guard / Repair | 可作为产品侧 UX 改动和日志分层字段；不能作为 held-out 实验证据 |
| `aichat_prompt_mode` request / response field | `online_active` | 线上请求和响应记录回答方式；未来真实日志必须按该字段分层 | 若使用线上日志 case，必须报告 prompt mode |
| content-level independent leakage judge in online chat | `not_implemented` | Research v1 有离线 Leakage Judge，但未接入线上 active mode | 不能声称线上已有独立泄题检测闭环 |
| online full multi-judge every turn | `not_implemented` | scope lock 明确不作为默认线上策略 | 不应声称已上线 |

## Offline Research Harness

| Module / Behavior | Status | Evidence / Notes | 论文表述 |
|---|---|---|---|
| Bridge Judge / compact diagnoser | `offline_eval_only` | 用于 seed diagnosis、contract generation 和 smoke eval | 可作为离线系统变体 |
| Runtime bridge contract schema | `offline_eval_only` | `runtime_bridge_contract_schema_v1.json` | 可作为研究中的 compact control signal |
| Bridge Contract Tutor | `offline_eval_only` | runner 支持 bridge_contract 相关模式 | 可作为 ablation condition |
| Leakage Judge / Guard | `offline_eval_only` | 离线检测 candidate / final response | 可作为 guard ablation，但需校准 |
| Repair Generator | `offline_eval_only` | 离线 repair；自然 mini-study 中不一定触发；已有 20-case repair stress development run 和 20 对 before/after 教练盲评分析 | 可作为 pilot evidence；正式效果仍需 held-out 自然样本与 judge calibration |
| Response blind review workbook | `teacher_tool_only` | 教师端/Excel/workbook 盲评流程 | 可作为 coach review workflow |
| Repair before/after review | `teacher_tool_only` | all20 Repair stress 已有 20 对完整标注；修复后质量更好 14、持平 3、更差 3，泄露减轻 19、持平 1 | 可作为 Repair stress pilot，不作为最终 held-out 结论 |
| bilingual reports | `offline_eval_only` | 中文为教练主读面，英文为外部协作面；已有 bilingual policy 和 validator | 可作为研究协作规范 |
| bilingual docs validator | `offline_eval_only` | `validate_research_bilingual_docs.py` 默认允许 23 个 legacy debt，但拦截新增单语 Markdown | 可作为文档治理工具 |
| static lint dev gate | `offline_eval_only` | summary 已输出 `dev_gate`，answer-slot / filled-trace / worked-example 等风险触发 review_required | 可作为 dev 阶段筛选信号，不是 coach gold |

## Proposed / Shadow / Future

| Module / Behavior | Status | Evidence / Notes | 论文表述 |
|---|---|---|---|
| shadow mode for real AIChat logs | `shadow_or_proposed` | 设计方向明确，但未作为 active 学生回复控制 | 只能写 future deployment path |
| risk-triggered active mode | `shadow_or_proposed` | 有 routing policy 和 control harness policy | 可做 deployment simulation，不能写已上线 |
| deterministic safe response for direct code/solution request | `shadow_or_proposed` | 设计上应优先上线，但需确认当前 online 行为 | 可作为 active-mode promotion plan |
| automatic prompt patch after repair | `not_implemented` | 明确禁止；慢变量必须离线更新 | 不应实现，不应主张 |
| long-term student memory layer | `not_implemented` | scope lock 排除 Research v1 | future work |
| complete NOI/OI algorithm ontology | `not_implemented` | Research v1 只需 stratified coverage | future work |

## Dataset / Evaluation Status

| Artifact | Status | Notes |
|---|---|---|
| 20 old seeds | `offline_eval_only` | 已用于 pilot、prompt tuning、regression；不再作为正式 held-out test |
| 50 held-out test set | `offline_eval_only` | 已有 `bridgebench_cp_heldout_v1_50_draft.jsonl` 草稿和 dataset card；validator 通过 50 条数量、必填字段和 dev seed id overlap 检查 | 只能写成 draft held-out，仍需 Coach A 审查、Coach B 复标和冻结 |
| partial double annotation | `not_implemented` | 需 Coach B 独立标至少 20 条 |
| adjudicated reference | `not_implemented` | 主实验 headline metrics 前需要 |
| LLM Judge calibration protocol | `doc_only` after this update | 协议先建，报告后补 |
| repair stress set | `offline_eval_only` | `repair_stress_cases_v1.jsonl` 已扩到 20 条；已有 all20 自动 stress run、40 行 before/after 盲评表和 20 对 paired analysis | 仍需把 `repair_stress_004` 等失败样本纳入 regression；正式结论还需 held-out 自然样本 |
| bilingual documentation debt | `doc_only` | 当前 129 个 research Markdown；新增文档无单语违规；23 个历史未配对文档列为 legacy debt | 后续逐步补齐，不阻塞当前 Research v1 |
| pass^3 stability eval | `not_implemented` | 用于 online reliability discussion |

## 论文声明边界

### 可以说

- 当前线上 AIChat 是 `current_system` baseline。
- 线上学生端已有可选 `教练引导=enhanced_prompt_only_clean` 回答方式；默认仍是 `简洁提示=current_system`。
- Research branch 已形成 offline evaluation harness。
- Bridge Contract、Guard、Repair 是离线可消融的研究模块。
- mini-study 是 pilot，不是最终投稿级证据。

### 不可以说

- 当前线上 AIChat 已经完整 Bridge-aware。
- `教练引导` 已证明 Research v1 方法有效。
- Repair 已经在线修复学生回复。
- Leakage Judge 已经在线阻断所有泄露。
- risk-triggered routing 已经成熟上线。
- 20-case pilot 能证明最终效果。
