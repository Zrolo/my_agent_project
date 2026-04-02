# Review / Quiz 质量门（Harness 级）

## 本文件的写入标准

只写运行契约层的最小质量门，且只写跨 focus 通用的规则。

适合写：

- `review` 放行条件
- `quiz` 放行条件
- `fallback_explain` 必触条件
- `fallback_explain` 克制规则
- 复测门触发条件

不要写：

- 具体题目样例
- 某个 focus 的特殊规则
- 某次 prompt 调参经验
- 某次联调现象

---

## 一、Review 放行条件

`review` 只有同时满足下面条件，才允许进入 `quiz` 阶段：

1. `key_bridge` 必须指向学生这次真实卡住的核心桥梁。
2. `next_step` 必须是该桥梁下的一个可执行小步，不能退化成泛化建议。
3. `main_block / key_bridge / next_step / transfer_signal` 必须围绕同一个结构问题展开，不能各自说不同的事。
4. 输出不能滑成学习口号、方法建议或“以后遇到这类题”的泛化表达。
5. 不能用“同类题”“相似题”替代本题的结构判断。

### `key_bridge` 的判定标准

`key_bridge` 看的不是题面像不像，而是学生当前缺失的那一步结构连接是否被抓对。

如果桥梁抓错，即使后续表述流畅，也不放行。

---

## 二、Quiz 放行条件

`quiz` 只有同时满足下面条件，才允许放给学生：

1. 正确答案必须是结构事实，不是学习建议。
2. 题目必须贴着原题语境，测的是当前桥梁，不是泛算法常识。
3. 当当前理解检查链路进入 `main`、`followup`、`confirm` 这三种 `quiz` 角色中的任一角色时，产物必须满足对应角色边界；如果发生角色切换，仍要围绕同一座桥展开。
4. 每个错误选项都必须对应一个具体结构误区。
5. `bridge_feedback` 必须说明学生答对的是哪一层结构事实，以及它和原题卡点的关系。
6. `distractor_feedback` 必须指出该错误选项具体错在哪个结构，而不是只说“不对”。

### `confirm` 的判定标准

`confirm` 的目标是换角度验证同一座桥，不是换一道同类题。

判断时只看核心结构事实有没有变化，重点看这三类对象是否改变：

- 状态含义
- 转移条件
- 建模对象

如果这三类核心结构事实中的任意一类已经变化，就不是 `confirm`，而是换题，应拦截。

---

## 三、Fallback 必触条件

出现下面任一情况，必须退回 `fallback_explain`，不允许硬出题：

1. 当前桥梁无法稳定落成结构事实题。
2. 模型产出的正确答案本质上属于学习建议。
3. 题目已经滑成口号题、策略题或泛方法题。
4. `confirm` 所依赖的新情境已经改变了核心结构事实。

### 核心结构事实变化的判定

只要不是在验证同一座桥，而是在换一套结构关系，就算核心结构事实变化。

这里优先看：

- 状态含义是否变了
- 转移条件是否变了
- 建模对象是否变了

---

## 四、Fallback 克制规则

`fallback_explain` 只负责守门，不负责补讲。

它的职责只限于：

- 明确说明当前桥梁不适合出结构事实题

它不应做这些事：

- 展开完整讲解
- 替代 `remedy`
- 偷偷变成新的教学正文
- 顺手生成另一套可替代的题目

---

## 五、复测门触发条件

复测是否触发，只看这次提交实际改了哪些对象，不看抽象逻辑怎么描述。

### 0. 复测触发对象定义

下面这些对象，指的是执行时真正会影响质量门的改动边界；五类对象必须按互斥口径判类，不要一项改动同时落入多个桶：

- `review prompt`：只指 review 生成链路里的通用 prompt 文本或拼装逻辑改动；不包含 quiz prompt、共享 snippets，也不包含后端 guard。
- `quiz prompt`：只指 `prompts/quiz-content/system.md`、`prompts/quiz-content/user.md` 这两类 quiz 主模板改动；不包含共享规则 snippets，也不包含单 focus snippets。
- `全局规则`：只指跨多个 focus 复用的共享规则片段改动，例如 `prompts/snippets/structural-quiz-rules.md`、`bridge-feedback-rules.md`、`distractor-rules.md`、`json-output-rules.md`、`role-main.md`、`role-followup.md`、`role-confirm.md`；不包含 `quiz-content/*.md` 主模板，也不包含 `focus-*.md`。
- `focus snippet`：只指 `prompts/snippets/focus-*.md` 这类单 focus 规则片段。
- `后端通用 guard`：只指后端对 review / quiz / fallback 的通用守卫逻辑，例如 `review_engine.py` 里非单 focus 的 guard；不包含 prompt 文件本身。

### 1. 全量复测

出现下面任一情况，必须做全量复测：

1. `review prompt` 改动。
2. `quiz prompt` 改动。
3. 全局规则改动。
4. 后端通用 guard 改动。

全量复测的目的，是确认这套质量门的整体一致性没有被改坏。

全量复测的样例范围，统一锚定到 `docs/subjects/noi/focus_quality_eval_v1.md` 当前登记的全部样例。

也就是说：只要触发全量复测，就把该文档当前覆盖的所有 focus、所有样例组全部复测一遍，不只看某个局部分支。

### 2. 局部复测

只改单个 `focus snippet` 时，做局部复测。

局部复测的样例来源，锚定到 `docs/subjects/noi/focus_quality_eval_v1.md`。

第一版默认每个 `focus` 只登记 3 组样例：

- `易滑坡坏例`
- `应 fallback`
- `应放行`

如果未来该文档把某个 `focus` 的样例扩到超过 3 组，局部复测应以该文档当前登记的该 `focus` 全部样例为准，而不是死守 3 组。

如果一次提交同时改多个 `focus snippet`，就需要把对应多个 `focus` 在该文档里登记的全部样例一起复测。

局部复测不替代全量复测：只要这次提交还动到了 `review prompt`、`quiz prompt`、全局规则或后端通用 guard，就必须走全量复测。

### 3. 复测升级规则

如果局部复测中发现下面任一情况，必须升级为全量复测：

1. 同一次提交里，后来又补改了 `review prompt`、`quiz prompt`、全局规则或后端通用 guard。
2. 局部复测暴露出该 `focus` 之外的样例也被影响。
3. 局部复测发现 `confirm`、`fallback_explain` 或 review / quiz 门禁口径已经不稳定。

---

## 六、最小原则

这份 harness 文档只保留最小质量门，统一按下面原则执行：

1. 先判结构，再谈表达。
2. 先判同桥，再判同类。
3. 宁可 `fallback`，也不放坏题。
4. `confirm` 只验证同一座桥，不验证相似外观。
5. 复测只在门禁口径可能变化时升级。
