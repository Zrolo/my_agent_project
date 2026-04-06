# Review 人工抽样复核 SOP

这份文档定义 review 上线后的人工抽样复核流程，用来回答：

1. `mode routing` 是否分对。
2. review 是否贴题。
3. 学生看完后是否具备明确下一步。

关联文档：
- `/Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/docs/common/review_observability_spec.md`

---

## 1. 适用范围

本 SOP 只用于上线后的抽样复核，不用于：

- 离线 prompt 评测
- 大规模教学测评
- 教师正式打分

它的目标是快速发现：
- mode 分错
- review 太空
- review 看似合格但学生仍无法继续

---

## 2. 抽样频率

建议频率：
- 每天一次

建议样本量：
- `10-20` 条

建议抽样原则：

1. 各 mode 都要覆盖
2. 优先抽学生反馈为 `confused`
3. 再抽一部分 `understood` 作为对照

---

## 3. 复核字段

每条抽样只填 4 项：

```json
{
  "session_id": "uuid",
  "problem_id": "string",
  "review_mode": "string",
  "mode_correct": "correct | incorrect | unsure",
  "review_grounded": "grounded | mixed | vague",
  "student_can_move_next": "yes | no | unsure",
  "notes": "string"
}
```

---

## 4. 字段判断口径

### 4.1 `mode_correct`

判断问题：
- 这条输入被分到这个 mode，是否合理？

填写规则：
- `correct`
  - mode 与学生真实状态一致
- `incorrect`
  - 明显分错
- `unsure`
  - 信息不足，无法判断

### 4.2 `review_grounded`

判断问题：
- 这条 review 是否真的贴当前题，不是在讲泛泛方法？

填写规则：
- `grounded`
  - 明显贴题，点名对象、条件或操作
- `mixed`
  - 一半贴题，一半抽象
- `vague`
  - 主要是空话或泛化表述

### 4.3 `student_can_move_next`

判断问题：
- 学生看完这条 review 后，是否具备明确下一步？

填写规则：
- `yes`
  - 看完后知道下一步该查什么、做什么
- `no`
  - 看完后仍不知如何继续
- `unsure`
  - 信息不足，无法判断

---

## 5. 复核步骤

每条样本按下面顺序看：

1. 看学生输入
   - 题目标题
   - `problem_context`
   - `bottleneck_text`
   - 是否有代码
2. 看系统检测到的 `review_mode`
3. 看生成出的四个学生端字段
   - `main_block`
   - `key_bridge`
   - `next_step`
   - `transfer_signal`
4. 再填：
   - `mode_correct`
   - `review_grounded`
   - `student_can_move_next`
5. 若有特殊问题，在 `notes` 写一句话

---

## 6. 备注怎么写

`notes` 只写一句，优先记录：

- 为什么 mode 分错
- 哪个字段最空
- 学生为什么仍然无法继续

示例：

- `把 independent_reflect 误分成 failed_verdict，学生其实已经做出来了`
- `key_bridge 只报算法名，没有贴当前题动作`
- `next_step 太泛，学生仍不知道先检查哪一处`

---

## 7. 第一周复核重点

第一周重点盯三类问题：

1. 哪个 mode 最容易被分错
2. 哪个 mode 最容易“看起来过关，但学生仍没看懂”
3. 哪类输入最容易导致 review 太空

第一周不要求统计长期学习收益，也不要求对老师教学效果下结论。

---

## 8. 复核完成后的最小输出

每天抽样复核后，至少给出 3 行结论：

1. 今天 `mode_correct` 最低的是哪个 mode
2. 今天 `review_grounded` 最差的共性是什么
3. 今天最值得回放的 1-2 条 session 是哪几条

这三行比大段主观总结更适合指导下一轮产品迭代。
