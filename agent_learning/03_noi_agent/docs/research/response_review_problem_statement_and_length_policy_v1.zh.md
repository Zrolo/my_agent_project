# 回复盲评题面与学生问题长度分布政策 v1

日期：2026-05-13

## 结论

后续所有 AIChat 回复盲评表必须包含真实题源元数据和 `problem_statement`，中文表头为 `原题题面/必要题面`。只给 `problem_context` 不够，因为教练需要先看题面和来源，才能判断学生当前问题到底卡在哪个局部桥梁，以及 AI 是否泄露了题面没有直接给出的关键关系。

同时，50-case held-out 数据集需要记录学生问题长度分布，避免 benchmark 只覆盖很短的学生问题。

## 盲评表字段

从本政策开始，盲评表源信息列至少包含：

| 字段 | 中文表头 | 用途 |
| --- | --- | --- |
| `problem_ref` | 题目编号 | 题目或内部样本编号 |
| `problem_source_platform` | 题目来源平台 | 真实题源平台，例如 Luogu、Codeforces、AtCoder、NOI/NOIP、ICPC 等 |
| `problem_source_id` | 平台题号 | 平台上的题号或比赛题号 |
| `problem_source_url` | 原题链接 | 原题公开链接，必须是 `http://` 或 `https://` URL |
| `problem_statement` | 原题题面/必要题面 | 给教练判断题意、限制、输入输出关系和当前卡点所需的题面信息 |
| `problem_statement_public_summary` | 公开题面摘要 | 公开数据中可保留的改写摘要，用来避免直接复制大段受版权保护题面 |
| `problem_statement_rights_note` | 题面版权/使用说明 | 说明本地盲评、公开发布和引用题源的边界 |
| `problem_statement_access_level` | 题面访问级别 | 标记题面可见范围，见下方取值 |
| `student_message` | 学生当前问题 | 学生本轮原始疑问 |
| `student_message_length_bucket` | 学生问题长度类型 | 标记学生问题是短、中短、中长还是长 |
| `problem_context` | 题目/上下文 | 压缩背景、已知算法域或题目关键条件，不替代题面 |
| `recent_dialogue` | 近期对话 | 判断学生是否已经说出关键桥 |
| `context_ai_reply` | 上下文 AI 回复 | 上一轮 AI 回复，帮助判断本轮是否合理承接 |
| `response_text` | AI 回复（要评分） | 当前需要评分的目标回复 |

## 真实题源与题面粒度

`problem_statement` 不一定必须是公开平台原题全文，但必须足够让教练判断：

- 题目要求求什么；
- 输入/输出或对象关系是什么；
- 关键限制条件是什么；
- 学生问题和题目条件之间有什么关系；
- AI 回复中的某个关系是否已经由题面明示。

如果原题全文存在版权或公开发布风险，研究公开版本可以使用经过改写的 necessary statement；但给教练盲评的本地表格必须提供足够题面信息。公开论文或开源 artifact 中优先保留 `problem_source_url`、`problem_statement_public_summary` 和必要的自写摘要，不直接复制平台长题面。

`problem_statement_access_level` 允许以下取值：

| access level | 解释 |
| --- | --- |
| `local_review_only` | 完整或较完整题面只用于本地教练盲评，不进入公开 artifact |
| `public_summary_only` | 公开 artifact 只保留改写摘要和原题链接 |
| `open_license` | 题面明确允许复用，可按许可证说明公开 |
| `original_link_only` | 公开 artifact 只保留原题链接，不公开题面内容 |

## 学生问题长度桶

自动按去除空白后的字符数划分：

| bucket | 长度 | 解释 |
| --- | ---: | --- |
| `short` | 1-30 字 | 一句很短的问题或局部判断 |
| `medium_short` | 31-70 字 | 一到两句，说明了卡点但细节有限 |
| `medium_long` | 71-140 字 | 有尝试、错误原因或局部推理 |
| `long` | 141 字以上 | 多句描述，可能包含代码片段、反例或较完整尝试过程 |

50-case 主实验建议比例：

| bucket | 比例 | 50-case 数量 |
| --- | ---: | ---: |
| `short` | 40% | 20 |
| `medium_short` | 30% | 15 |
| `medium_long` | 20% | 10 |
| `long` | 10% | 5 |

该比例不是说长问题更好，而是为了让 benchmark 覆盖真实 AIChat 中不同学生表达习惯。真实学生多数会短回复，因此 short 应占最大比例；但正式评测不能只测短问题，否则无法覆盖代码、反例和复杂上下文场景。

## 对现有 50-case 的影响

正式 held-out 前必须完成：

1. 为 50 条 case 补齐 `problem_source_platform`、`problem_source_id`、`problem_source_url`；
2. 为 50 条 case 补齐 `problem_statement`、`problem_statement_public_summary`、`problem_statement_rights_note`、`problem_statement_access_level`；
3. 重新运行 dataset validation，检查题源分布、题面访问级别和 `student_message_length_distribution`；
4. 不满足 20/15/10/5 分布时，调整或补充 case；
5. 重新导出包含题源和题面的中文盲评表；
6. 教练评分前先阅读题源、题面，再阅读学生问题和 AI 回复。

## 边界

本政策不要求把题面喂给线上学生 AIChat，也不要求线上每轮显示题面。它只约束离线研究盲评和 held-out benchmark，以保证教练评分有足够上下文。
