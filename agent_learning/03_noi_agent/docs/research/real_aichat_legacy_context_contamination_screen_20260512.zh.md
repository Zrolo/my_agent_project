# 真实 AIChat 旧上下文污染筛选 20260512

本文记录对 45 条真实线上 AIChat 推荐候选的二次筛选。目标是判断候选 turn 之前的旧线上 `current_system` AI 回复是否已经影响学生状态，尤其是否已经把关键桥讲穿。

## 为什么需要这一步

真实线上对话很有价值，因为它包含真实学生短回复、真实代码 debug 和真实多轮上下文。但这些日志中的历史 AI 回复来自旧线上系统，质量不稳定。

因此：

- 学生真实问题可以作为候选；
- 旧 AI 回复不能作为 gold tutor response；
- 旧 AI 回复如果位于目标 turn 之前，只能作为 `recent_dialogue` 上下文，并且必须检查是否污染学生状态；
- 旧 AI 回复如果位于目标 turn 之后，只能作为 `observed_current_system_response`，不能当标准答案。

## 筛选对象

输入：

```text
recommended_real_aichat_45_for_coach.csv
```

每条候选包含：

- 目标学生 turn；
- 目标 turn 之前的少量上下文；
- 目标 turn 之前最近一条 AI 回复，即 `context_ai_reply`；
- 目标 turn 之后旧系统给出的 AI 回复，即 `assistant_reply`。

本轮只检查 `context_ai_reply` 和更早的 assistant 上下文是否污染目标 turn。`assistant_reply` 不用于判断学生状态污染，因为它发生在目标学生 turn 之后。

## 标签定义

| 字段 | 含义 |
|---|---|
| `legacy_ai_context_contamination=none` | 目标 turn 前没有旧 AI 回复上下文 |
| `legacy_ai_context_contamination=low` | 有旧 AI 回复，但主要是泛化提示、追问或轻脚手架，没有明显补完关键桥 |
| `legacy_ai_context_contamination=medium` | 旧 AI 回复含部分算法概念、局部关系或较强提示，可能影响学生当前表述 |
| `legacy_ai_context_contamination=high` | 旧 AI 回复可能已经给出代码、完整做法、精确定义、转移、check 语义、边界更新或其他关键桥 |

对应研究使用建议：

| `recommended_research_use` | 含义 |
|---|---|
| `main_eval_candidate` | 可进入真实日志主评测候选池，仍需人工脱敏和教练复核 |
| `dev_or_contextual_candidate` | 适合 dev、error analysis、robustness，不建议进入 headline held-out |
| `exclude_from_main_eval` | 不建议进入主实验，可作为旧系统污染或失败案例分析 |

## 筛选结果

45 条推荐候选的污染分布：

| 污染等级 | 数量 |
|---|---:|
| none | 25 |
| low | 8 |
| medium | 4 |
| high | 8 |

研究使用建议：

| 用途 | 数量 |
|---|---:|
| main_eval_candidate | 33 |
| dev_or_contextual_candidate | 4 |
| exclude_from_main_eval | 8 |

33 条主评测候选的类别分布：

| 类别 | 数量 |
|---|---:|
| graph_tree_modeling | 11 |
| debugging_wa_tle_re | 9 |
| implementation_boundary | 6 |
| binary_search_check | 4 |
| dp_state_transition | 1 |
| data_structure_semantics | 1 |
| general_cp_question | 1 |

33 条主评测候选中：

- 18 条含学生代码；
- 26 条来自多轮会话。

## 解释边界

这次筛选使用启发式规则，不是教练最终判断。规则主要检查：

- 是否出现完整代码、伪代码、完整解法或“代码如下”；
- 是否出现具体 DP 状态/转移、check 返回语义、边界更新、lazy 语义等可能补完关键桥的表述；
- 是否有长篇旧 AI 解释，使学生当前短问题依赖旧系统输出；
- 是否只是追问、泛化提示或轻量 micro-task。

最终能否进入主实验，仍需教练人工确认：

- 旧 AI 上下文是否真正改变了学生已知状态；
- 目标学生 turn 是否仍能独立标注 missing bridge；
- 是否可安全脱敏；
- 是否代表真实算法竞赛辅导场景。

## 输出文件

私有筛选文件保存在本机：

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/
```

主要文件：

```text
recommended_real_aichat_45_with_legacy_context_screen.csv
main_eval_clean_real_aichat_candidates.csv
dev_contextual_real_aichat_candidates.csv
excluded_legacy_contaminated_real_aichat_candidates.csv
legacy_context_contamination_summary.json
```

这些文件含真实学生文本的脱敏版本，不应直接提交到公开仓库。

## 下一步

建议下一步：

1. 教练审查 `main_eval_clean_real_aichat_candidates.csv` 中 33 条；
2. 删除仍有隐私或噪声的样本；
3. 选出 20-30 条真实日志 candidate；
4. 为每条补：
   - `missing_bridge`；
   - `forbidden_content`；
   - `success_criteria`；
   - `legacy_context_contamination`；
   - `public_display_ok`；
5. 决定哪些进入 dev/regression，哪些保留为 held-out real-log subset。

论文中应明确：

> Real AIChat logs were screened for legacy-system context contamination before use. Old AI replies were used only as context or deployment-baseline evidence, not as gold tutor responses.

## Subagent 自评后的修正

2026-05-12 使用独立 GPT-5.5 / xhigh subagent 对真实日志筛选结果做了审稿人式自评。自评结论是：

- 这批样本适合进入教练审查，但当前形态不能直接进入主评测；
- `privacy_status` 仍是自动脱敏后的 `needs_manual_review`，不能公开分享；
- 33 条主候选类别偏斜，图/树、debug 和实现边界占比较高，DP、数据结构、贪心不足；
- `low` 污染样本仍需逐条教练复判，不能自动视为干净；
- 旧 AI 上下文必须完整可审计，不能只展示最近一条 AI 回复；
- 审查表不应默认 `隐私风险=none` 或 `建议split=heldout_real_candidate`。

根据该自评，已生成修正版教练审查表：

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_main_eval_candidate_review_33_20260512_v2.zh.xlsx
```

v2 表的关键修正：

- `隐私风险` 默认改为 `needs_manual_review`；
- `建议split` 默认改为 `undecided`；
- 新增 `完整近期对话（目标turn前，供污染/自包含判断）`；
- 新增 `是否自包含`；
- 新增 `是否需要补充题面/代码上下文`；
- 新增 `是否近重复样本`；
- 新增 `需重点复判`；
- 将旧系统回复字段改为 `目标turn后旧系统回复（baseline观察，非上下文，非gold）`。

因此后续应优先使用 v2 表，而不是早期 v1 表。

## Student-only v3 审查表

后续讨论进一步收紧了真实日志样本的使用方式：主消融不使用旧线上 AI 回复作为上下文，只取真实学生当前提问、题目/代码上下文和教练补充标签。旧线上 AI 回复只保留在审计字段中，用于判断污染和记录旧系统 baseline 观察，不进入新 baseline 的生成输入，也不作为 gold。

已生成 student-only v3 审查表：

```text
/Users/kongyouli/Downloads/real_aichat_candidate_screen_20260512/real_aichat_student_only_candidate_review_33_20260512_v3.zh.xlsx
```

v3 表的关键变化：

- 新增 `删除旧AI后是否可理解`，只有填 `yes` 的样本才允许导出为主评测候选；
- `学生当前问题（主消融输入）` 是后续 baseline 生成的核心输入；
- `目标turn前旧AI上下文（只供审计，不给模型）` 和 `完整近期对话（只供审计，不给模型）` 只用于人工审查；
- `目标turn后旧系统回复（baseline观察，非上下文，非gold）` 只用于记录旧系统表现；
- 导出后的 `generation_input.recent_dialogue` 和 `generation_input.context_ai_reply` 必须为空；
- 旧 AI 上下文只写入 `audit_context`，用于追溯和污染判断。

这意味着论文中的真实日志主评测样本应表述为：

> We use real student questions from online AIChat logs as candidate turns, while historical AI replies are retained only for audit and legacy-baseline observation. They are removed from generation inputs for all new tutor conditions.

中文表述：

> 我们使用线上 AIChat 中的真实学生提问作为候选 turn；历史 AI 回复只用于审计和旧系统观察，不进入任何新 tutor condition 的生成输入。

## 审查后导出工具

已新增导出脚本：

```bash
python3 -m evals.aichat.export_real_log_candidates_from_review \
  --input /path/to/real_aichat_student_only_candidate_review_33_20260512_v3_filled.zh.xlsx \
  --output-jsonl docs/research/real_aichat_candidate_set_v1.jsonl
```

默认只导出 `审查状态=保留主评测` 的行，并且会阻止以下半成品或不干净样本误入主数据集：

- `missing_bridge（教练填）` 为空；
- `forbidden_content（教练填）` 为空；
- `success_criteria（教练填）` 为空；
- `隐私风险` 不是 `none`；
- `建议split=undecided` 或空；
- `删除旧AI后是否可理解` 为空、`no` 或 `uncertain`。
- `是否自包含` 不是 `yes`；
- `是否需要补充题面/代码上下文` 不是 `no`；
- `是否近重复样本` 不是 `no`；
- `是否代表真实卡点` 不是 `yes`；
- `是否适合主评测` 不是 `yes`；
- `需重点复判` 不是 `no`；
- `旧AI上下文污染初筛` 不是 `none` 或 `low`；
- `学生当前问题（主消融输入）` 为空；
- `类别` 为空；
- `题号/URL` 和 `题目标题` 同时为空。

脚本会优先识别 `student_only候选_v3` 工作表；如果没有该工作表，则回退到旧的 `候选样本_v2`。

如需在导出前查看每条被拒原因，可以生成严格筛选报告：

```bash
python3 -m evals.aichat.export_real_log_candidates_from_review \
  --input /path/to/real_aichat_student_only_candidate_review_33_20260512_v3_filled.zh.xlsx \
  --output-jsonl /tmp/real_aichat_candidate_preview.jsonl \
  --screen-report-json /tmp/real_aichat_strict_screen_report.json \
  --allow-incomplete
```

注意：`--allow-incomplete` 只能用于预览结构和生成筛选报告；正式主评测导出不能使用该参数。

如果只是想预览结构，可以加：

```bash
--allow-incomplete
```

但带 `--allow-incomplete` 的输出不能作为主评测数据。
