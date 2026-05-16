# 真实 AIChat 日志候选筛选记录 20260512

本文记录 2026-05-12 对线上学生 AIChat 真实对话的只读筛选。该筛选用于形成后续 Research v1 真实日志候选池，不直接产生 gold label，也不直接进入 50-case held-out headline result。

## 数据源

线上服务目录：

```text
/opt/noi-agent
```

只读数据表：

```text
aichat_messages
```

本次未修改线上数据库，也未写入服务器文件。筛选输出保存在本机私有目录，包含脱敏后的候选 turn，需人工复查后才能进入研究数据。

## 原始统计

| 指标 | 数量 |
|---|---:|
| AIChat message 总数 | 1426 |
| 学生消息 | 713 |
| AI 回复 | 713 |
| 学生数 | 14 |
| 会话数 | 106 |
| 题目数 | 38 |
| 日期范围 | 2026-04-23 至 2026-05-12 |
| 含题面/题目上下文的学生消息 | 703 |
| 含学生代码的学生消息 | 136 |
| 消息数不少于 4 的多轮会话 | 82 |

## 筛选方法

每个学生 turn 与其后的第一条 AI 回复配对，形成候选样本。筛选脚本对每条学生 turn 打分，主要正向信号包括：

- 有下一条 AI 回复；
- 有题面或题号上下文；
- 有学生代码或明显 debug 信号；
- 学生表达了困惑、卡点或错误；
- 出现算法/实现/调试关键词；
- 来自多轮会话；
- 文本长度足以标注。

过滤或降权信号包括：

- 过短无信息回复，例如“好的”“懂了”“继续”；
- 缺少下一条 AI 回复；
- 明显外部复制噪声或非信息学竞赛内容；
- 需要人工进一步判断的泛泛问题。

本轮只使用正则与启发式筛选，不使用 LLM 自动决定 gold label。

## 候选池结果

| 阶段 | 数量 |
|---|---:|
| 原始学生 turn | 713 |
| 分数达到候选阈值 | 672 |
| 多样性约束后候选池 | 70 |
| 推荐优先审查 | 45 |
| 备选 | 21 |
| 排除 | 4 |

70 条候选池的特征：

| 指标 | 数量 |
|---|---:|
| 含学生代码 | 29 |
| 含题面/题目上下文 | 68 |
| 来自多轮会话 | 59 |

45 条推荐优先审查样本的类别分布：

| 类别 | 数量 |
|---|---:|
| graph_tree_modeling | 13 |
| debugging_wa_tle_re | 12 |
| implementation_boundary | 8 |
| dp_state_transition | 4 |
| binary_search_check | 4 |
| data_structure_semantics | 2 |
| general_cp_question | 2 |

推荐样本中，26 条含学生代码，38 条来自多轮会话。

## 隐私处理

本轮私有候选文件做了以下初步脱敏：

- `student_id` 哈希化；
- `session_id` 哈希化；
- 邮箱、手机号、非洛谷 URL、明显联系方式做正则替换；
- 原始账号、真实姓名、密码不导出。

但这只是自动脱敏，不能视为最终匿名化。进入论文或共享给外部教练前，还需要人工检查：

- 学生是否在文本中自报姓名、学校、联系方式；
- 代码注释中是否包含个人信息；
- 截图式复制内容或外部平台广告是否混入；
- 是否包含不适合公开的真实课堂细节。

## 研究使用建议

这些真实日志适合三种用途：

1. **dev/regression cases**：用于补充真实学生短回复、代码 debug、多轮上下文等开发样例。
2. **held-out candidate pool**：在 prompt / grader 冻结后，从推荐样本中抽取一部分，由教练审查后加入真实日志 held-out 子集。
3. **paper qualitative examples**：只选脱敏、获得人工确认、教学价值高的少量 case。

不建议直接做：

- 不经教练复核就当 gold label；
- 不经人工脱敏就进入论文；
- 用这些真实日志继续调 prompt 后，又把同一批当 held-out headline result；
- 把线上日志与 synthetic 50-case 混成同一指标而不分层说明。

## 下一步

建议下一步由教练先审查 45 条推荐样本：

- 保留 20-30 条作为真实日志 candidate set；
- 标记每条是否可公开展示；
- 补上 missing bridge、forbidden content、success criteria；
- 确认是否含代码、是否含长上下文、是否代表真实学生短回复；
- 决定哪些进入 dev/regression，哪些保留为 held-out。

正式论文中应把这些样本称为：

```text
real AIChat log candidates, coach-reviewed and anonymized before use
```

而不是直接称为 gold dataset。
