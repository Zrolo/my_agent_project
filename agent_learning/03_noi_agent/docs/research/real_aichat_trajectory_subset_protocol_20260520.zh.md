# Real-AIChat Trajectory Subset Protocol

Date: 2026-05-20

## 使用边界

Real trajectory subset 只用于回应“只有单轮”的生态效度质疑。它不修改线上 AIChat，不新增 main experiment condition，不重算 dialogue-state v3 主表，不评估 learning outcome，也不说明学生学会了。

## 目标

选择 20-30 条真实 AIChat 多轮轨迹，用于检查真实多轮上下文如何影响 missing-bridge 判断、context sufficiency 和短期解释。该 subset 只支持 ecological validity / context sufficiency / short-horizon interpretation。

## 数据单位

每条 trajectory 建议包含：

- target turn 前 1-3 轮；
- target student message；
- target response；
- 后 1-2 轮学生追问，如果有；
- context sufficiency note；
- missing bridge interpretation note；
- observed next-turn progress as short-horizon signal, if available。

## Reporting Boundary

允许写：

- 多轮上下文有助于判断当前 missing bridge。
- 某些 target turns 需要前文才能判断 forbidden content。
- observed next-turn progress 只能作为 short-horizon signal。
- trajectory subset 是 ecological-validity evidence。

不能写：

- 学生学会了。
- 长期学习效果提高。
- 线上系统有效性被证明。
- 多轮模拟证明教学效果。
- online intervention evidence。

## Unsafe Wording List

以下措辞 must be avoided in current evidence:

- "students learned"
- "learning gains"
- "deployed system effectiveness"
- "multi-turn simulation proves"
- "online intervention"

如果未来做 simulated multi-turn，只能作为 appendix stress test；不得写成真实学生学习效果。

## Privacy Boundary

公开材料不得包含学生原文、完整代码、完整 AIChat 回复、真实身份、hash salt 或可逆映射。若 consent/reporting gate 未完成，只能报告 aggregate/process counts 和 protocol readiness。
