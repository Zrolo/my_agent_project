# Bridge Contract Prompt 学生可用性小修记录（2026-05-13）

## 背景

`dev10` 人工盲评显示，`bridge_contract_guard` 的重大泄露控制较稳，但学生可直接使用率和自然度不够稳定。尤其在状态/表示类问题中，部分回复容易把学生需要自己形成的状态语义讲得过直，或者把提示写成规则清单，学生读起来不够像一位教练在接着当前对话往前带。

本次修改只作用于离线研究工具链中的 Bridge Contract Tutor prompt，不接入线上学生 AIChat，不改变评测架构，也不作为正式实验结论。

## 修改内容

在 `evals/aichat/run_bridge_offline_eval.py` 的 Bridge Contract Tutor system prompt 中新增两类约束：

1. 学生可见回复形状：
   - 一句承接学生当前说法；
   - 一个很小的观察任务；
   - 一个可短答的问题；
   - 不要像规则清单一样回复；
   - 不要连续追问多个问题。

2. 状态/表示类桥的第一层提示：
   - 不要直接给出表示对象承载的完整语义、目标量、最优性含义或可行性含义；
   - 不要把“这个量表示什么”提前替学生说完；
   - 先问哪些输入因素、边界对象、历史选择或约束会影响后续决策；
   - 让学生先列出影响后续决策的因素。

## 边界

这不是算法特例规则扩张，而是把状态/表示类桥抽象成更通用的教学动作：先让学生观察“哪些因素会影响后续决策”，再让学生形成表示语义。具体失败样例应进入 regression case、rubric example 或 error analysis，不应直接写进生成 prompt。后续正式 held-out 实验前仍需要冻结 prompt，并用教练盲评验证该修改是否真的提升学生可用性。

## 验证

已新增并通过单测：

- `test_bridge_contract_tutor_prompt_blocks_state_definition_leakage`
- `test_bridge_contract_tutor_prompt_requires_teacher_like_response_shape`

相关回归测试通过：

```text
python3 -m unittest test_bridge_offline_eval_runner_unit.py test_dbox_inspired_decomposition_tutor_unit.py test_literature_baseline_tutors_unit.py
```

结果：`Ran 67 tests ... OK`。
