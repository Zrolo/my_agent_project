# 学生端页面契约修复实施计划

## 范围

只修学生端：

- 路由补全
- 历史列表/详情阶段拆分
- 返回历史列表
- 新建打卡后的详情跳转

不动 teacher 路由。

## 实施步骤

1. 扩展学生端路由解析与构建
   - 更新 `static/student_routes.js`
   - 后端补齐 `/app/chat`、`/app/checkin`

2. 先补失败测试
   - `test_student_routes.mjs`
   - `test_review_async_api_unit.py`
   - `test_review_stage_layout.mjs`

3. 调整学生端结构
   - `checkin-tab` 仅保留打卡输入页
   - `history-tab` 增加：
     - `history-list-stage`
     - `history-detail-stage`
   - 增加“返回历史列表”按钮

4. 调整前端路由与阶段切换
   - `applyStudentRoute`
   - `showStudentTab`
   - `selectCheckin`
   - 新建打卡成功后的跳转

5. 回归验证
   - 学生路由单测
   - SPA 入口测试
   - 历史详情布局测试
   - 全量 `run_test.sh`

## 风险控制

- 保留现有复盘详情核心 ID，避免大面积改渲染逻辑
- teacher 侧完全不动，降低回归范围
- 历史详情仍复用已有 review shell，只调整所属页面语义
