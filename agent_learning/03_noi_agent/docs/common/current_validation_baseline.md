# 当前验证基线与上线前验收清单

## 这份文档解决什么问题

当前仓库里同时存在两套验证口径：

- 一套是最近随着 `review_mode / review_family / observability / manual review` 一起补起来的新回归
- 一套是更早期的默认脚本回归（`run_test.sh`、`test_review_api_flow.py`、`test_v1_2_flow.py`）

现在的真实状态是：

- 新回归大部分是绿的
- 旧回归里有至少两条已经和当前系统行为不一致，不能再直接当作“发布绿灯”

所以这份文档只做三件事：

1. 列清楚当前**可信测试清单**
2. 列清楚当前**已失效旧测试清单**
3. 给出一份**上线前最小验收 checklist**

---

## 一、当前可信测试清单

下面这些是 2026-04-06 实际跑过、且当前能代表系统现状的验证。

| 类别 | 命令 | 结果 | 覆盖范围 | 结论 |
| --- | --- | --- | --- | --- |
| 后端核心回归 | `python3 -m unittest test_review_async_api_unit.py test_review_engine_messages_unit.py test_review_quality_eval_unit.py test_review_eval_kimi_cli_unit.py` | `79/79` 通过 | review API、family/mode 返回、observability、quality eval、kimi cli runner | 当前最可信的后端主回归 |
| 前端 UI 回归 | `node --test test_review_family_ui.mjs test_teacher_manual_review_ui.mjs test_teacher_stats_ui.mjs` | `16/16` 通过 | family-aware 展示、人工复核 UI、教师统计页、统计卡片 drill-down helper | 当前最可信的前端主回归 |
| 前端语法检查 | `node --check static/app.js static/review_family_ui.js static/teacher_manual_review_ui.js` | 通过 | 学生端主脚本、family helper、教师复核 helper | 说明当前前端脚本可解析 |
| Python 语法检查 | `python3 -m py_compile api_server.py database.py review_engine.py` | 通过 | FastAPI 主入口、数据库层、review engine | 说明核心 Python 文件可编译 |
| 学习流 API 集成 | `python3 test_learning_flow_api_integration.py` | `2/2` 通过 | review quiz/self-check/remedy 相关 API 主链 | 当前学习流 API 口径基本可用 |
| focus 检测 | `python3 test_focus_detection.py` | 通过 | focus taxonomy 检测规则 | 当前 focus 检测链路可用 |
| 服务启动 smoke | 启动 `uvicorn api_server:app --host 127.0.0.1 --port 8765` 后访问 `/` 和 `/app` | `200 / 200` | 服务启动、静态前端挂载、主页面入口 | 项目能启动，页面能打开 |

### 推荐作为当前发布绿灯的最小命令组

```bash
python3 -m py_compile api_server.py database.py review_engine.py
python3 -m unittest test_review_async_api_unit.py test_review_engine_messages_unit.py test_review_quality_eval_unit.py test_review_eval_kimi_cli_unit.py
python3 test_learning_flow_api_integration.py
python3 test_focus_detection.py
node --test test_review_family_ui.mjs test_teacher_manual_review_ui.mjs test_teacher_stats_ui.mjs
node --check static/app.js static/review_family_ui.js static/teacher_manual_review_ui.js
```

---

## 二、当前已失效旧测试清单

下面这些不是“语法错了”，而是**测试预期已经和当前系统行为脱节**。  
它们现在不能继续被当作发布绿灯。

| 测试 / 脚本 | 当前状态 | 失败现象 | 失效原因判断 |
| --- | --- | --- | --- |
| `bash run_test.sh` | 失败 | 第一条 `test_review_api_flow.py` 就失败 | 这个脚本不再代表当前真实基线 |
| `python3 test_review_api_flow.py` | 失败 | 旧断言要求 `/api/checkins/me` 里的 `review_last_error` 立刻包含 `RuntimeError` | 当前异步 review 流里，checkin 会保留、`review_status=pending`，但列表接口不再立刻回显这个错误字符串 |
| `python3 test_v1_2_flow.py` | 失败 | 旧测试在创建 checkin 后立刻调用 `/api/reviews/{id}/quiz/generate`，实际返回 `400: 复盘尚未完成，暂时不能生成理解小测` | 旧测试假设“创建 checkin 后 review 已同步完成”，而当前 review 已是异步生成链路 |
| `TESTING.md` 中把 `run_test.sh` 当“当前默认测试入口” | 与现状不一致 | 文档仍写默认跑本地 API 回归 + v1.2 流程回归 | 文档口径漂移，需要后续修正 |

### 这两条旧测试现在到底哪里不对

#### 1. `test_review_api_flow.py`

它要验证的是：

- review 生成异常时，checkin 仍会保留
- 历史列表里还能看到错误信息

但当前真实行为是：

- `POST /api/checkins` 仍然成功，`review_status = pending`
- 历史列表中 `review_last_error` 当前返回为 `null`

也就是说，**“checkin 保留”这个业务目标还在，但“错误显示字段”已经不再满足旧测试写法**。

#### 2. `test_v1_2_flow.py`

它的前提是假设：

- 创建 checkin 后，review 已经处于可生成 quiz 的状态

但当前真实行为是：

- review 先进入异步生成
- review 没完成时，`/api/reviews/{review_id}/quiz/generate` 会拒绝

所以这不是简单断言错，而是**测试依赖的系统时序已经变了**。

### 当前处理原则

在这些旧测试被重写前：

- 它们可以保留作“历史参考”
- 但**不能**作为当前版本是否可发布的判断依据

---

## 三、上线前最小验收 checklist

这份 checklist 只覆盖当前真正影响首次试运行的关键点，不追求“全量完美”。

### A. 环境与启动

| 检查项 | 标准 |
| --- | --- |
| Python 依赖已安装 | `pip install -r requirements.txt` 成功 |
| `MOONSHOT_API_KEY` 已显式导出 | 不是只放 `.env`，而是当前 shell 可读 |
| 服务可启动 | `uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload` 成功 |
| 根接口可访问 | `GET /` 返回 200 |
| 页面入口可访问 | `GET /app` 返回 200 |

### B. 学生端最小验收

| 检查项 | 标准 |
| --- | --- |
| 登录可用 | `student_a / password` 可以进入学生工作区 |
| AI 解答可用 | 能发送一条问题并得到响应 |
| 打卡提交可用 | 能成功创建一条 checkin |
| review 展示可用 | 打卡后能看到 review 区域，不是空白页 |
| family-aware 顺序可用 | failure/success 两类 review 展示顺序正确 |
| self-check 可用 | 能点自评按钮并触发后续状态变化 |
| 埋点可上报 | 至少能写入 `review_request_submitted / review_shown / review_feedback_submitted` |

### C. 教师端最小验收

| 检查项 | 标准 |
| --- | --- |
| 登录可用 | `teacher / password` 可以进入教师管理区 |
| 全体打卡列表可用 | 能看到学生 checkins |
| 教师统计页可用 | 能加载统计数据，不是空白或报错 |
| 人工复核列表可用 | 能看到样本、提交复核成功 |
| 统计 drill-down 可用 | 点击 mode/family 卡片可切到对应筛选样本 |
| 人工复核统计可用 | 总体、按 mode、按 family 三组 rate 都能显示 |

### D. 自动化回归验收

上线前至少执行一次：

```bash
python3 -m py_compile api_server.py database.py review_engine.py
python3 -m unittest test_review_async_api_unit.py test_review_engine_messages_unit.py test_review_quality_eval_unit.py test_review_eval_kimi_cli_unit.py
python3 test_learning_flow_api_integration.py
python3 test_focus_detection.py
node --test test_review_family_ui.mjs test_teacher_manual_review_ui.mjs test_teacher_stats_ui.mjs
node --check static/app.js static/review_family_ui.js static/teacher_manual_review_ui.js
```

验收标准：

- 所有命令退出码为 `0`
- 前端 Node 测试全绿
- Python 核心回归全绿
- 服务启动 smoke 通过

### E. 本轮明确不作为上线阻塞项的内容

| 项目 | 说明 |
| --- | --- |
| `run_test.sh` 全绿 | 当前不是可信基线，不作为上线阻塞项 |
| `test_review_api_flow.py` 全绿 | 需要按当前异步 review 行为重写 |
| `test_v1_2_flow.py` 全绿 | 需要按当前异步 quiz 前置条件重写 |
| 更复杂的 dashboard / BI 看板 | 当前不是首次试运行阻塞项 |
| 更多 prompt 微调 | 当前优先级低于真实学生反馈收集 |

---

## 四、当前建议的发布判断口径

当前建议使用下面这条判断：

> 如果“服务启动 smoke + 当前可信测试清单 + 学生端/教师端最小手工走查”都通过，就可以进入小范围试运行。

不要再用下面这条旧判断：

> `run_test.sh` 绿了就代表整个项目可上线

这条旧判断现在已经不成立。
