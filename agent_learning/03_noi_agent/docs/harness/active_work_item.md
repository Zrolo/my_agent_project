# 当前工作项

## 本文件的写入标准

只写**当前正在推进的一轮任务**：

- 当前目标
- 本轮非目标
- 本轮需要加载的 contract 文件
- 本轮涉及文件
- 验收标准
- 当前风险 / 下一步

不要写：

- 长期规则
- 已完成的全部历史
- 与当前任务无关的讨论

---

## 当前目标

基于已经落地的质量门和 12 组样例，开始第一轮 `review + quiz` 质量收紧实施，优先修上游桥梁判断，再决定哪些 focus 能继续放行、哪些必须 fallback。

本轮目标是：

1. 把 `review -> key_bridge / next_step` 的稳定性作为第一优先级收紧
2. 依据 `review_quiz_quality_gate.md` 和 `focus_quality_eval_v1.md` 判定 4 个高风险 focus 的放行 / fallback 边界
3. 为后续 prompt / snippet / guard 改动建立固定复测顺序

---

## 本轮非目标

本轮不做：

- 新增 focus
- 新功能开发
- 页面视觉继续细修
- 题库推荐升级
- 自动化复测平台
- harness 与代码的一致性自动检查

---

## 本轮需要加载的 contract 文件

- `docs/harness/ai_output_contracts.md`
- `docs/harness/review_quiz_quality_gate.md`
- `docs/subjects/noi/focus_quality_eval_v1.md`

---

## 本轮涉及文件

- `docs/harness/current_system_state.md`
- `docs/harness/active_work_item.md`
- `docs/harness/ai_output_contracts.md`
- `docs/harness/review_quiz_quality_gate.md`
- `docs/subjects/noi/focus_quality_eval_v1.md`
- `review_engine.py`
- `prompts/quiz-content/system.md`
- `prompts/quiz-content/user.md`
- `prompts/snippets/role-main.md`
- `prompts/snippets/role-followup.md`
- `prompts/snippets/role-confirm.md`
- `prompts/snippets/focus-general_modeling.md`
- `prompts/snippets/focus-constraint_modeling.md`
- `prompts/snippets/focus-greedy_basis.md`
- `prompts/snippets/focus-method_selection.md`

---

## 验收标准

1. `review` 的 `key_bridge / next_step` 在 4 个高风险 focus 上不再明显漂到泛建议
2. `quiz` 在该放行的样例上能落到结构事实，在该 fallback 的样例上能主动退回
3. `confirm` 不再把换题误当成同桥验证
4. 本轮改动完成后，能按质量门区分全量复测和局部复测
5. `current_system_state.md` 与 `active_work_item.md` 反映本轮真实进展，而不是上一轮已完成文档任务

---

## 当前风险

1. 如果先追求 coverage，很容易为了“能出题”把坏题重新放回来
2. `review` 和 `quiz` 可能会分别收紧，但桥梁口径不一致
3. `general_modeling / constraint_modeling / greedy_basis / method_selection` 这 4 个 focus 最容易一改就互相影响

---

## 下一步建议

1. 先针对 `review -> key_bridge / next_step` 做第一轮实现计划
2. 再决定 4 个高风险 focus 是优先改 prompt、focus snippet，还是优先改后端 guard
3. 每次只改一类规则，改完立即按质量门复测，不做大杂烩联改
