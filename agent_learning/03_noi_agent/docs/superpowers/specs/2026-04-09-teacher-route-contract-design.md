# 教师端页面契约修复设计

## 背景

当前教师端已经有多个真实页面语义：

- 配额管理
- 学员打卡
- 错误统计
- 人工复核
- 关注学员

但实现上仍然只是前端 tab 切换，没有 URL 契约。这会导致：

- 刷新后丢失当前页
- 无法深链接到统计或人工复核
- 浏览器返回键无效

## 目标

给教师端建立最小而稳定的页面契约：

- `/app/teacher`
- `/app/teacher/quota`
- `/app/teacher/checkins`
- `/app/teacher/stats`
- `/app/teacher/manual-review`
- `/app/teacher/flags`

## 设计

### 1. 路由约定

默认：

- `/app/teacher` 视为 `quota`

其余路径一一对应教师页签。

### 2. 前端路由同步

新增 teacher route helper：

- `parseTeacherRoute`
- `buildTeacherRoute`

在教师端新增：

- `getTeacherRouteFromLocation`
- `updateTeacherLocation`
- `applyTeacherRoute`

### 3. showTeacherTab 扩展

`showTeacherTab` 新增可选参数：

- `skipRouteSync`

行为：

- 正常点击页签时同步 URL
- 程序内部切页时可跳过 URL 写回

### 4. 刷新 / 返回行为

- 教师登录后，按当前 URL 恢复目标页签
- 浏览器 `popstate` 时恢复教师当前页签

### 5. 数据加载策略

保持最小改动：

- 继续沿用 `showMainInterface` 的预加载
- `manual-review-tab` 仍在切换时触发 `loadTeacherReviewSamples`
- 其余标签不新增复杂懒加载

## 非目标

这次不做：

- 教师端子页面布局重构
- 统计页 URL 参数过滤
- 学生端进一步模块拆分

## 验收标准

- 教师页签都有对应 URL
- 刷新后保留当前教师页
- 浏览器返回键可在教师页签之间切换
- `/app/teacher/*` 直接打开时返回 SPA 入口
