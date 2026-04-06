# NOI Agent 测试说明

## 当前默认测试入口

在项目目录下运行：

```bash
bash /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh
```

这个脚本现在代表的是**当前可信验证基线**，不再跑已经失效的旧脚本回归。

默认会顺序执行：

1. Python 语法检查
2. 核心后端回归
3. 学习流 API 集成回归
4. focus 检测回归
5. 前端 Node 测试
6. 前端语法检查

## 当前默认回归到底跑什么

### 1. Python 语法检查

```bash
python3 -m py_compile api_server.py database.py review_engine.py
```

目的：

- 确认 FastAPI 主入口、数据库层、review engine 都可编译

### 2. 核心后端回归

```bash
python3 -m unittest \
  test_review_async_api_unit.py \
  test_review_engine_messages_unit.py \
  test_review_quality_eval_unit.py \
  test_review_eval_kimi_cli_unit.py
```

目的：

- review API
- `review_mode / review_family`
- observability 事件
- teacher manual review / stats
- review quality eval
- kimi cli runner

### 3. 学习流 API 集成回归

```bash
python3 test_learning_flow_api_integration.py
```

目的：

- quiz / self-check / remedy 的关键 API 主链

### 4. focus 检测回归

```bash
python3 test_focus_detection.py
```

目的：

- `data_type`
- `loop_boundary`
- `recursion_structure`
- `complexity_fit`

### 5. 前端 Node 测试

```bash
node --test \
  test_review_family_ui.mjs \
  test_teacher_manual_review_ui.mjs \
  test_teacher_stats_ui.mjs
```

目的：

- family-aware 展示顺序
- 学生端反馈文案
- 教师人工复核 UI
- 教师统计页与 drill-down helper

### 6. 前端语法检查

```bash
node --check static/app.js static/review_family_ui.js static/teacher_manual_review_ui.js
```

目的：

- 确认当前静态前端主脚本可解析

## 当前不再作为默认测试入口的旧脚本

下面这些**保留文件，但不再进入默认绿灯**：

1. `test_review_api_flow.py`
2. `test_v1_2_flow.py`

原因不是“没价值”，而是它们的测试预期已经和当前系统行为脱节：

- `test_review_api_flow.py`
  - 仍假设历史列表里会立刻回显 `review_last_error`
  - 但当前异步 review 流里，checkin 保留、状态是 `pending`，列表接口不再立刻回显旧断言里的错误字符串

- `test_v1_2_flow.py`
  - 仍假设创建 checkin 后就可以立刻生成 quiz
  - 但当前 review 已经是异步链路，review 未完成时 `quiz/generate` 会返回 400

## 旧测试怎么处理

旧测试并没有被废弃，只是**降级为待重写项**。

具体重写计划见：

- [legacy_test_rewrite_plan.md](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/legacy_test_rewrite_plan.md)

在重写完成之前：

- 它们可以作为历史参考
- 但不能再作为“项目是否可发布”的依据

## 什么时候需要跑 quota 脚本

如果你还想附加运行旧的 quota 手工脚本，可以用：

```bash
bash /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/run_test.sh --with-quota
```

这一步不会影响默认回归是否通过，它只是额外的手工演示脚本：

```bash
python3 test_quota.py
```

它会尝试读取或提示输入 `MOONSHOT_API_KEY`。

## 真实页面怎么验

如果你想继续确认：

- 学生端文案是否自然
- family-aware 展示是否顺畅
- 教师端人工复核和统计 drill-down 是否工作正常

请再对照这份浏览器联调清单：

- [BROWSER_WALKTHROUGH_V1_2.md](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/BROWSER_WALKTHROUGH_V1_2.md)

## 当前推荐的发布判断口径

当前建议使用下面这条判断：

> `run_test.sh` 全绿 + 服务启动 smoke 通过 + 学生端/教师端最小手工走查通过，就可以进入小范围试运行。

不要再使用旧判断：

> `test_review_api_flow.py` 和 `test_v1_2_flow.py` 全绿才算当前版本可发布

这条旧判断现在已经不成立。
