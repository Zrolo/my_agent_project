# NOI Agent 阶段三执行清单（2026-04）

## 目标

阶段三不再扩新桥，也不再加新页面。

只做一件事：

- 围绕固定样例池，继续复审高频 bridge 的真实学生链路
- 把还不够像“小课”的地方继续收紧
- 用 bridge 级证据，而不是题号级感觉，决定下一轮修复

---

## 阶段三范围

只继续盯这 3 类当前仍然最值得反复复审的 bridge：

- `method_selection`
- `shared_prefix_merging`
- `lazy_semantics`

原因：

- `method_selection`
  - 仍然最容易和别的桥混在一起
- `shared_prefix_merging`
  - 真实历史里最容易被旧噪音带偏
- `lazy_semantics`
  - 现在已经较稳，但最适合用来检验“知识卡 + 补课 + 小算例”这一整套是不是足够像小课

---

## 固定样例入口

阶段三所有评估优先使用：

- [high_frequency_bridge_sample_pool_2026_04.md](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/high_frequency_bridge_sample_pool_2026_04.md)
- [bridge_audit_board_2026_04.md](/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/bridge_audit_board_2026_04.md)

不再直接把全库里同题所有记录混在一起看。

---

## 先做顺序

### 1. 先复审 `method_selection`

优先样例：

- `P2922`
  - `checkin_id=4701`
  - `review_id=4543`

重点看：

- 首轮 review 有没有稳稳站住“题面信号”
- main / follow-up 有没有继续缩小
- remedy 有没有自然过渡到下一座机制桥

验收标准：

- 不再出现明显漂到泛 bridge
- 学生能看懂“为什么该用 trie”不是凭感觉

### 2. 再复审 `shared_prefix_merging`

优先样例：

- `P2922`
  - `checkin_id=4701`
  - `review_id=4543`
- 对照：
  - `checkin_id=4341`
  - `review_id=4190`

重点看：

- 节点计数语境下的：
  - `review`
  - `main`
  - `follow-up`
  - `remedy`
  - `knowledge card`
  - `knowledge confirm`
- 特别看：
  - `经过次数`
  - `结束次数`
  - `101 / 100 / 11`
  是否都已经稳定出现

验收标准：

- 真实 live 链路不再漂回 `state_design`
- 知识卡和补课已经明显像一节小课

### 3. 复审 `lazy_semantics`

优先样例：

- `P3372`
  - `checkin_id=4226`
  - `review_id=4074`
- 对照：
  - `checkin_id=4084`
  - `review_id=3941`

重点看：

- `lazy` 是否已经稳定被讲成：
  - “这段区间已经确定、但还没下传给孩子的信息”
- 最小算例：
  - `[1,4]`
  - `lazy=3`
  - `3×2`
  是否足够让学生抓住

验收标准：

- 补课和知识卡都不再像模板说明
- 学生能明确区分“区间语义”和“代码流程”

---

## 阶段三产物

阶段三结束时，项目里应该新增或稳定这几样：

- 高频 bridge 的最新复审结论
- 每个目标 bridge 至少 1 条最新可引用 live 样例
- 更新后的 `bridge_audit_board`
- 更新后的 harness 状态文档

---

## 暂停项

阶段三期间先不要继续做：

- 新 teacher 页面
- 新 bridge 扩张
- 大 UI 改版
- 首轮 review 大重构
- 新外部资料源接入

---

## 一句话

阶段三就是：

> 拿固定样例池，持续复审最弱 bridge，把学生链路真正收成“能学进去的小课”。
