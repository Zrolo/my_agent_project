# 教师端论文数据导出中心设计

## Summary

本设计新增教师端“论文数据导出中心”。目标不是让教师下载整库，而是把系统中与论文分析、日常教学诊断相关的数据整理成可控、可解释、可追溯的数据包。

导出必须同时满足两类需求：

1. 教师带班需要知道真实学生是谁，因此教师识别版允许包含学生真实姓名、账号和班级信息。
2. 论文写作、统计分析和外部分享不能暴露学生身份，因此论文匿名版默认使用稳定匿名 ID，不包含姓名、账号、完整聊天原文或完整代码。

第一版优先做后端 zip 数据包和教师端下载入口，不做复杂可视化分析。

## Design Goals

- 让教师能定期下载论文所需数据，不需要直接登录服务器或手动拷贝数据库。
- 保留教师识别学生问题的能力，但防止误把真实姓名放进论文数据。
- 数据字段直接服务当前论文主线：有边界的 AI 解题辅导、理解证据、复盘补救、教师可见证据。
- 导出数据应可被 Excel、Python、SPSS/R 直接读取。
- 每次导出都记录审计日志，便于后续说明数据来源。

## Non-Goals

- 不导出完整数据库。
- 不默认导出完整 AIChat 原文。
- 不默认导出学生完整代码。
- 不在第一版做自动统计显著性检验。
- 不在第一版做论文图表生成器。
- 不把教师端现有看板替换成研究平台。

## User Roles

### Teacher

教师可以下载两种数据包：

- 教师识别版：用于带班诊断，包含真实姓名和账号。
- 论文匿名版：用于论文统计和外部分析，不含真实姓名和账号。

### Maintainer

维护者可以在服务器上查看导出日志、排查导出失败、必要时限制导出范围。

### Student

学生不直接访问导出中心。学生数据进入导出前必须经过字段筛选和隐私规则处理。

## Export Modes

### Teacher Identifiable Package

用途：老师自己看，判断哪些学生需要帮助。

包含：

- `student_id`
- 登录账号
- 显示姓名
- 班级或分组信息（如现有账号数据中存在）
- 最近活跃、最近题目、AIChat 使用情况
- 做题记录、复盘结果、验证结果
- 教师建议关注原因

限制：

- 文件名必须带 `teacher_identifiable`。
- README 明确写明：该包含学生真实身份，不应进入论文附件或外部分享。
- 默认仍不导出完整聊天原文和完整代码。

### Research Anonymous Package

用途：论文统计、画图、发给合作者做分析。

包含：

- `student_hash`，例如 `stu_8f31c2`
- 题号、标签、难度
- 事件类型、时间戳、阶段判断、结果
- Review 路径、Quiz 通过情况、做题记录方式

不包含：

- 真实姓名
- 登录账号
- 原始学生 ID
- 完整聊天原文
- 完整代码

匿名规则：

- 使用稳定哈希，保证同一学生跨文件可关联。
- 哈希盐来自服务器环境变量 `NOI_RESEARCH_EXPORT_SALT`。
- 如果未设置盐，后端应拒绝生成匿名包，并提示维护者配置。

## Export Formats

第一版生成 zip 文件：

```text
research_export_2026-04-01_2026-05-01_teacher_identifiable.zip
research_export_2026-04-01_2026-05-01_anonymous.zip
```

zip 内部结构：

```text
README.md
export_manifest.json
students.csv
daily_usage.csv
aichat_events.jsonl
problem_completions.csv
problem_closures.csv
checkins.csv
reviews.csv
review_quizzes.csv
teacher_attention.csv
learning_issue_stats.csv
summary.json
```

若某类数据当前表不存在或没有记录，仍生成空文件，并在 `export_manifest.json` 中标记 `row_count: 0`。

## Data Files

### README.md

说明：

- 导出时间范围。
- 导出模式：教师识别版 / 论文匿名版。
- 是否包含文本摘要。
- 每个文件的用途。
- 隐私提醒。
- 字段解释入口。

### export_manifest.json

记录导出元数据：

```json
{
  "exported_at": "2026-05-01T20:30:00+08:00",
  "start_date": "2026-04-01",
  "end_date": "2026-05-01",
  "mode": "teacher_identifiable",
  "include_text_samples": false,
  "generated_by": "teacher",
  "files": [
    {"name": "students.csv", "row_count": 18},
    {"name": "aichat_events.jsonl", "row_count": 320}
  ]
}
```

### students.csv

教师识别版字段：

- `student_id`
- `login_account`
- `display_name`
- `active`
- `created_at`
- `last_active_at`

论文匿名版字段：

- `student_hash`
- `active`
- `created_at`
- `last_active_at`

### daily_usage.csv

按天汇总：

- `date`
- `active_students`
- `aichat_turns`
- `problem_completion_count`
- `closure_quiz_count`
- `closure_quiz_passed`
- `checkin_count`
- `review_count`
- `review_quiz_count`

用途：论文中画系统使用趋势。

### aichat_events.jsonl

每行是一条 AIChat 事件或回合摘要。

字段：

- `event_id`
- `student_key`：教师识别版为 `student_id`，匿名版为 `student_hash`
- `created_at`
- `problem_id`
- `session_id`
- `role`
- `message_length`
- `has_code`
- `model_provider`
- `judge_primary_intent`
- `judge_phase`
- `judge_action_category`
- `judge_action_subtype`
- `allowed_help_level`
- `injection_detected`
- `router_model_used`（如果未来启用）
- `router_recommended_model`（如果未来启用）

默认不包含：

- `content`
- 完整代码

可选 `include_text_samples=true` 时，只加入：

- `content_excerpt`：最多 120 字，且仅用于教师识别版或人工批准的研究抽样。

### problem_completions.csv

来自学生“记录做完的题”。

字段：

- `completion_id`
- `student_key`
- `created_at`
- `problem_id`
- `problem_title`
- `problem_url`
- `completion_method`
- `result`
- `summary_length`
- `summary_quality`
- `evidence_level`
- `points_awarded`

教师识别版可选增加：

- `student_summary_excerpt`，最多 120 字。

论文匿名版默认只导出长度与质量判断，不导出原文总结。

### problem_closures.csv

来自 AIChat “我已理解，结束本题”验证。

字段：

- `closure_id`
- `student_key`
- `created_at`
- `problem_id`
- `session_id`
- `quiz_status`
- `quiz_type`
- `passed`
- `attempt_count`
- `points_awarded`
- `focus_summary`
- `failure_reason_category`

用途：衡量 AIChat 对话是否产生理解证据。

### checkins.csv

来自深入复盘或打卡。

字段：

- `checkin_id`
- `student_key`
- `created_at`
- `problem_id`
- `problem_title`
- `problem_url`
- `status`
- `error_type`
- `bottleneck_layer`
- `handoff_type`
- `has_chat_context_summary`
- `reflection_length`

默认不导出完整学生反思。

### reviews.csv

来自 Review LLM 结构化复盘。

字段：

- `review_id`
- `checkin_id`
- `student_key`
- `created_at`
- `review_status`
- `review_mode`
- `error_layer`
- `key_bridge`
- `bridge_path`
- `mastery_status`
- `learning_status`
- `knowledge_bailout_triggered`
- `teacher_followup_needed`

用途：论文中统计有界补救路径。

### review_quizzes.csv

来自 Review 内嵌验证题。

字段：

- `quiz_id`
- `review_id`
- `student_key`
- `created_at`
- `quiz_kind`
- `quiz_focus`
- `status`
- `attempt_count`
- `passed`
- `judgement`

用途：分析 main / remedy / bottom-out 的通过情况。

### teacher_attention.csv

来自教师端建议关注和教师标记。

字段：

- `event_id`
- `student_key`
- `created_at`
- `severity`
- `reason_category`
- `evidence_source`
- `teacher_action`
- `status`
- `resolved_at`

用途：分析系统是否把证据交给教师。

### learning_issue_stats.csv

按时间范围聚合：

- `issue_category`
- `topic`
- `problem_ref`
- `student_count`
- `example_count`
- `suggested_teacher_action`

用途：论文中说明班级层教学问题聚合。

### summary.json

一页机器可读摘要：

```json
{
  "students": 18,
  "active_students": 12,
  "aichat_turns": 320,
  "problem_completions": 41,
  "closures": {"total": 24, "passed": 15, "failed": 9},
  "checkins": 18,
  "reviews": 18,
  "review_paths": {
    "main_clear": 8,
    "remedy_clear": 5,
    "bottom_out_clear": 2,
    "knowledge_bailout": 3
  },
  "teacher_attention_events": 7,
  "data_readiness": {
    "deployment_study": "partial",
    "bounded_review_analysis": "ready_if_review_count_sufficient",
    "teacher_dashboard_analysis": "needs_teacher_view_logs"
  }
}
```

## API Design

### Preview Endpoint

```text
GET /api/teacher/research-export/preview?start=2026-04-01&end=2026-05-01
```

返回：

```json
{
  "start": "2026-04-01",
  "end": "2026-05-01",
  "counts": {
    "students": 18,
    "aichat_events": 320,
    "problem_completions": 41,
    "closures": 24,
    "checkins": 18,
    "reviews": 18,
    "review_quizzes": 26
  },
  "warnings": [
    "匿名导出需要配置 NOI_RESEARCH_EXPORT_SALT",
    "当前未发现教师查看事件日志，teacher dashboard 分析只能使用 teacher_flags"
  ]
}
```

用途：教师下载前先知道数据量。

### Package Endpoint

```text
GET /api/teacher/research-export/package?start=2026-04-01&end=2026-05-01&mode=teacher_identifiable&include_text_samples=false
```

参数：

- `start`：必填，YYYY-MM-DD。
- `end`：必填，YYYY-MM-DD。
- `mode`：`teacher_identifiable` 或 `anonymous`。
- `include_text_samples`：默认 false。

响应：

- `application/zip`
- 文件名按模式和日期生成。

错误：

- 匿名模式未设置 `NOI_RESEARCH_EXPORT_SALT`：返回 400。
- 时间范围超过允许上限：返回 400。
- 非教师身份：返回 401/403。

### Audit Endpoint

```text
GET /api/teacher/research-export/audit?limit=50
```

返回最近导出记录：

- 导出人。
- 时间范围。
- 模式。
- 是否含文本样例。
- 文件清单和行数。

## Teacher UI

教师端新增页面或放入“高级”页下的“论文数据导出”区。

### Layout

页面分三块：

1. 数据范围
   - 日期范围。
   - 预设：最近 7 天 / 15 天 / 30 天 / 自定义。

2. 导出版本
   - 教师识别版：包含真实姓名，供老师自己看。
   - 论文匿名版：不含真实姓名，供论文统计。

3. 数据内容
   - 默认全选汇总和事件数据。
   - 文本样例默认关闭。
   - 文本样例开关旁写明风险。

按钮：

- `预览数据量`
- `下载教师识别版`
- `下载论文匿名版`

### Copy

教师识别版提示：

> 这个数据包包含学生真实姓名和账号，只用于你自己判断学生学习情况，不要放进论文附件或外部分享。

论文匿名版提示：

> 这个数据包已经去掉学生真实姓名和账号，可用于论文统计。若要展示案例，请再单独人工检查文本样例。

## Privacy Rules

### Default Exclusions

以下字段默认不导出：

- AIChat 完整原文。
- 学生完整代码。
- 初始密码。
- API key。
- 系统 prompt。
- 教师密钥。
- 服务器环境变量。

### Text Sample Rules

当 `include_text_samples=true`：

- 只导出最多 120 字摘要或片段。
- 代码内容仍不导出，只记录代码长度。
- 匿名版文本样例必须额外执行姓名/账号替换。
- README 标记该包含文本样例，需要人工复查后才能进入论文。

### Real Name Rules

- 真实姓名只出现在 `teacher_identifiable` 模式。
- 文件名、manifest 和 README 都必须标记含身份信息。
- 匿名模式下不得出现 `display_name`、`login_account`、原始 `student_id`。

## Audit Logging

新增导出审计表或 JSONL 日志，第一版建议数据库表：

```sql
CREATE TABLE IF NOT EXISTS research_export_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  teacher_id TEXT NOT NULL,
  exported_at TEXT NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT NOT NULL,
  mode TEXT NOT NULL,
  include_text_samples INTEGER NOT NULL DEFAULT 0,
  file_name TEXT NOT NULL,
  manifest_json TEXT NOT NULL,
  status TEXT NOT NULL,
  error_message TEXT
);
```

审计日志不保存 zip 文件本体，只保存元数据和行数。

## Data Access Layer

后端新增导出服务模块，建议文件：

```text
research_export.py
```

职责：

- 日期范围解析和校验。
- 学生 ID 匿名化。
- 查询各类数据。
- 生成 CSV / JSONL。
- 生成 README 和 manifest。
- 打 zip。
- 写审计记录。

`api_server.py` 只负责权限、参数和返回文件流。

### Reuse Existing Data Functions

优先复用：

- `get_class_completion_summary`
- `get_aichat_learning_issue_stats`
- `get_mastery_status_stats`
- `get_bridge_path_stats`
- `get_knowledge_bailout_stats`
- `list_teacher_aichat_observations`
- `get_all_checkins`
- Review / quiz 查询函数

如果现有函数只返回聚合数据，不足以生成事件级数据，再新增只读查询函数。

## Date Range Limits

第一版限制：

- 默认最近 30 天。
- 单次最大 180 天。
- 若超过 180 天，返回 400，提示分段导出。

原因：

- 避免一次性导出过大。
- 避免教师误导出长期敏感数据。
- 让论文统计按阶段分批处理。

## Error Handling

- 某个文件生成失败：整个导出失败，不返回部分 zip。
- 查询为空：生成空文件，不算失败。
- 写审计失败：导出失败，因为审计是隐私要求的一部分。
- zip 生成失败：返回 500，并写失败审计。
- 匿名盐缺失：匿名导出返回 400。

## Testing Plan

### Unit Tests

- 匿名模式不包含真实姓名、账号、原始 student_id。
- 教师识别版包含真实姓名和账号。
- 匿名 hash 稳定：同一学生多次导出 hash 一致。
- 不同 salt 下 hash 不同。
- `include_text_samples=false` 时不导出聊天原文和代码。
- `include_text_samples=true` 时文本截断到 120 字。
- 日期范围超过 180 天返回错误。
- 缺少匿名盐时 anonymous 模式返回错误。
- zip 中包含所有规定文件。
- manifest 行数和实际文件行数一致。
- 导出成功写审计记录。
- 导出失败写失败审计记录。

### API Tests

- 非教师无法访问 preview/package/audit。
- 教师可以 preview。
- 教师可以下载 teacher_identifiable zip。
- 教师可以下载 anonymous zip。
- package endpoint 返回正确 Content-Type 和 filename。

### UI Tests

- 教师端显示两个模式区别。
- 默认不勾选文本样例。
- 点击预览显示数据量和 warning。
- 下载按钮能拿到 zip。
- 匿名盐缺失时 UI 显示维护提示。

## Rollout

### Phase 1: Backend Export Only

- 新增 `research_export.py`。
- 新增 preview/package/audit API。
- 新增审计表。
- 写单元测试和 API 测试。

### Phase 2: Teacher UI

- 教师端新增“论文数据导出”页面或高级页入口。
- 接入 preview 和 package 下载。
- 加隐私提示。

### Phase 3: Paper Data Readiness Report

- 在 zip 中增加 `paper_readiness.md`。
- 自动判断当前数据更适合支持哪些论文结论：
  - 部署统计。
  - AIChat 使用与理解验证。
  - 有界补救路径。
  - 教师端证据聚合。

## Open Decisions

1. 教师识别版是否允许导出文本样例？
   - 建议允许，但默认关闭，并强提示风险。

2. 匿名版是否允许导出文本样例？
   - 建议第一版不允许。若以后需要论文案例，单独做“人工选样导出”。

3. 学生真实姓名来源以哪个字段为准？
   - 建议优先使用学生管理中的 display_name；没有则回退 login_account。

4. 是否记录教师下载后的本地文件 hash？
   - 第一版不需要。

## Acceptance Criteria

- 教师能从网页下载指定日期范围的数据包。
- 教师识别版能帮助老师看清具体学生。
- 论文匿名版不包含真实姓名、账号、原始 student_id、完整聊天原文、完整代码。
- zip 内有 README、manifest、summary 和核心数据文件。
- 每次导出都有审计记录。
- 导出的字段能覆盖论文主线所需的四类证据：AIChat、做题记录、Review、教师关注。
