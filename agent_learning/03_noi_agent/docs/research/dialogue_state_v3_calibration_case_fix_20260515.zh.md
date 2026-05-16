# Dialogue-State v3 校准样本修正记录（2026-05-15）

本记录说明 6 条 calibration case 试填后，对数据生成规则做出的修正。该记录只用于 case/source review 阶段，不构成正式实验结果。

## 校准结论

6 条 calibration case 中，`dialogue_v3_001` 与 `dialogue_v3_048` 可接受；`dialogue_v3_011`、`dialogue_v3_018`、`dialogue_v3_026`、`dialogue_v3_043` 建议修改。主要问题不是题源不可用，而是部分样本的 `recent_dialogue -> student_message -> missing_bridge -> success_criteria` 链条不够一致。

## 已修正内容

- `dialogue_v3_018`：边界/顺序类 follow-up 不再生成“分支怎么拆”式学生回复，改为围绕“旧值、覆盖、顺序”表达卡点。
- `dialogue_v3_026`：建模/对象关系类 follow-up 不再生成二分 `true/false` 或边界方向话术，改为围绕“对象、关系、覆盖/依赖”表达卡点。
- `dialogue_v3_043`：实现边界类前置概念缺口不再生成“可行性/状态语义”话术，改为围绕“字符、输入、下标、初值/范围”表达卡点。
- `dialogue_v3_011`：转移/递推来源类 follow-up 已改成“部分跟上”的学生回复，修订后的预期状态为 `F2/clarify`，早先偏乐观的标签已废弃。该样本现在要求教练重点复核：学生是否已经把“前驱/来源”关系具体对应到题面动作。

## 生成规则改动

- follow-up 学生回复现在根据 bridge bucket 选择不同话术，不再只按 context type 生成通用回复。
- 短回复场景也加入 bucket-aware fallback，避免短句被压缩成与目标桥梁不一致的 generic phrase。
- 实现边界类优先于普通 boundary 规则匹配，避免 `implementation_boundary` 被误判为边界更新/循环方向类。

## 验证

- 已加入并通过 bucket-aware follow-up 与固定 calibration case 导出的回归覆盖。
- 相关 dialogue-state、审核表、校验器、held-out 风格校验、上下文审计与双语文档测试通过：47 个测试全部通过。
- 已重新生成 dialogue-state v3 JSONL、中英文 50-case review workbook 与 6-case calibration workbook。

## 后续使用建议

下一步仍应先做 5-6 条 calibration re-check，再进入完整 50-case case/source review。`dialogue_v3_011` 仍是重点复核样本，但当前预期状态已经是 `F2/clarify`；需要确认的是这条修订后的链条是否已经足够连贯、可接受。
