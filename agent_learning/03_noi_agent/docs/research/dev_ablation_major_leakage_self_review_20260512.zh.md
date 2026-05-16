# Dev Ablation Major Leakage 自盲评与修复记录（2026-05-12）

本记录基于 `dev_ablation_safe_scaffold_blind_review_analysis_20260512.zh.md`。它是开发阶段自盲评和 prompt/rubric 修复记录，不是最终 held-out 论文结果。

## 观察到的问题

10 个 dev cases、12 个系统条件、120 条盲评回复中，共有 8 条被标为 `major_bridge_leakage`。这些失败不是完整代码或完整题解泄露，而是更隐蔽的 critical bridge leakage：

1. **开头定义句泄露**：回复第一句直接解释学生正在缺的概念，再接一个问题。例如直接定义某个标记“表示还没做什么”。
2. **完整推演微型例子泄露**：例子贴题但把关键中间关系算完，学生只剩确认。
3. **经典模板搬运泄露**：把常见状态含义、标记规则或更新顺序模板直接放进回复。
4. **连续补桥泄露**：同一轮先替学生判断局部结果，再继续问后续动作、边界方向或操作位置，相当于连续补完两个关键桥。

## 修复原则

本次不新增算法特例清单，只按抽象泄露形态修：

- 对 Bridge Contract Tutor：禁止用开头定义句替学生命名或解释当前 missing bridge；先给观察对象或空白栏位。
- 对 Bridge Contract Tutor：禁止同一轮既给出局部判断，又追问后续边界/动作/位置。
- 对 DBox-inspired baseline：禁止把经典模板或标准定义搬给学生；`current_substep` 必须是学生可完成的小任务，不是答案句。
- 对 Leakage Judge：明确“开头定义句”可以是 critical bridge leakage。
- 对 Repair：明确删除 definition-first leak，改成观察任务、对比任务或空白栏位。

## 已修改位置

- `evals/aichat/run_bridge_offline_eval.py`
- `docs/common/aichat_leakage_judge_v1_system_prompt.md`
- `docs/common/aichat_repair_response_v1_system_prompt.md`
- `docs/research/prompt_patch_log.md`
- `docs/research/judge_prompt_patch_log.md`

## 回归测试

新增或更新：

- `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_bridge_contract_prompt_blocks_definition_first_and_followup_action_leaks`
- `test_bridge_offline_eval_runner_unit.py::BridgeOfflineEvalRunnerTests.test_dbox_prompt_blocks_canonical_template_and_definition_leaks`
- `test_leakage_judge_v1_unit.py::LeakageJudgeV1Tests.test_leakage_judge_prompt_flags_definition_first_bridge_leaks`
- `test_repair_response_v1_unit.py::RepairResponseV1Tests.test_repair_prompt_removes_definition_first_leaks`

## 仍不能声明什么

这次修复只说明 prompt/rubric 已经覆盖 dev 盲评暴露出的共性失败模式。不能声明：

- Bridge Contract 已经显著优于强 baseline；
- Guard/Repair 已经完全解决 critical bridge leakage；
- DBox-inspired baseline 已经被正式击败；
- 这些修复会在 held-out test 上稳定提升。

下一步仍然是冻结前的 targeted smoke，然后进入 50-case held-out、部分双教练标注和 judge calibration。
