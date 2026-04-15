# 教师端页面契约修复实施计划

## 范围

只做教师端页签路由化：

- URL 同步
- 刷新恢复
- 浏览器返回
- 后端 SPA 入口补齐

## 实施步骤

1. 新增 `static/teacher_routes.js`
2. 补测试
   - `test_teacher_routes.mjs`
   - `test_review_async_api_unit.py`
3. 补后端 `/app/teacher/*` SPA 入口
4. 在 `app.js` 中新增 teacher route 同步与恢复逻辑
5. 全量回归

## 风险控制

- 不改 teacher 页面内容结构
- 不改 teacher 统计和人工复核业务逻辑
- 只在现有 tab 切换之上增加 route contract
