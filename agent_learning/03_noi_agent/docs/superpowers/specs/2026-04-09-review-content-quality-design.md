# Review 内容质量提升设计

- 日期：2026-04-09
- 适用范围：`review_engine.py`、知识兜底卡、理解检查文案
- 状态：待实现

## 1. 背景

当前学生主链路已经成立：

- 第一轮结构化复盘
- 第二轮 follow-up / remedy
- 第三轮 bottom-out / final micro-confirm
- 三轮失败后的 knowledge bailout

现在更主要的问题不是功能缺失，而是**内容质感**：

- 有些复盘还是偏“系统说明”，不像老师带着学生学
- 有些知识卡虽然结构完整，但还不够像学生能真正看懂的小课
- 一些高频桥虽然已经有题链，但知识卡和确认题仍然偏抽象

本轮目标是：

> 在不增加新功能的前提下，把 `review_engine` 的话术和知识兜底卡收成更白话、更贴桥、更像学生能学会的小课。

---

## 2. 本轮目标

本轮只做内容质量提升，覆盖：

1. 第一轮 review prompt 的学生化约束
2. remedy / bottom-out prompt 的白话要求
3. 高频桥知识卡内容
4. 对应 knowledge confirm 题干的具体化

重点覆盖这些高频桥：

- `modeling.method_selection`
- `modeling.scale_estimation`
- `string.trie.shared_prefix_merging`
- `graph.tree_diameter.tree_diameter_candidates`

---

## 3. 非目标

本轮明确不做：

- 新功能
- 新路由
- 新数据库字段
- 新 UI 设计
- OI Wiki 检索注入
- 新的 quiz 流程分支

---

## 4. 设计原则

### 4.1 面向学生，不面向评审

内容首先要回答：

- 这一步到底在讲什么
- 我现在该先看哪一个对象或关系
- 我能不能用一句自己的话说出来

不是先追求：

- 术语完整
- 方法名齐全
- 看起来像“标准题解”

### 4.2 一步只讲一件事

不管是 review 还是知识卡，都优先遵守：

- 先讲当前桥
- 再讲这个桥在整种方法里的位置
- 最后只给一个很小的确认动作

### 4.3 用初中生能听懂的话

内容默认采用：

- 短句
- 先……再……最后……
- 对象先于术语
- 关系先于方法名

### 4.4 知识卡像小课，不像百科段落

每张卡固定两段：

1. `bridge_explanation`
   - 当前桥为什么卡住
   - 现在先把什么讲清楚
2. `algorithm_overview`
   - 这个桥在整种方法里扮演什么角色

---

## 5. 具体改动

## 5.1 Review prompt

收紧这几类约束：

- 更明确要求“短句、白话”
- 更明确要求“先讲对象，再讲关系，再讲这一步”
- 更明确要求 `guided_walkthrough` 不要塞多层信息
- 更明确要求 `try_now` 检查“当前桥是否打通”，不要变成表面动作

## 5.2 Remedy / bottom-out prompt

加强这些要求：

- remedy 更像“把桥缩小一步”
- bottom-out 更像“把这一小步重新讲一遍”
- 都优先使用：
  - 小样例
  - 小对比
  - 小分类

## 5.3 知识卡

重点改造这些卡：

- `modeling.method_selection`
  - 更明确强调“题面信号 / 结构信号”
- `modeling.scale_estimation`
  - 更明确强调“两层一起变大 / 双层枚举先炸”
- `string.trie.shared_prefix_merging`
  - 更明确强调“公共前缀先合并，不再重看所有消息”
- `graph.tree_diameter.tree_diameter_candidates`
  - 更明确强调“三类候选”和“经过新边时两边都接最远点”

## 5.4 Knowledge confirm

对应确认题不改流程，只改文案：

- 更具体
- 更贴当前桥
- 少抽象提法

---

## 6. 验收标准

完成后，至少满足：

1. prompt 测试能明确看到：
   - 白话
   - 短句
   - 先讲对象，再讲关系
2. 高频桥知识卡的 `bridge_explanation` 和 `algorithm_overview` 更具体
3. knowledge confirm 题更像“当前桥确认题”，不是抽象方法题
4. 现有回归测试通过
