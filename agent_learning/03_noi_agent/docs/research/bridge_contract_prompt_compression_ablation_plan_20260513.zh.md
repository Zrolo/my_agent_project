# Bridge Contract Prompt 压缩消融计划（2026-05-13）

## 背景

`dev10` 人工盲评显示，`bridge_contract_guard` 的重大泄露较低，但学生可直接使用率和自然度仍不够稳定。当前 Bridge Contract Tutor prompt 规则较多，存在模型注意力从“自然辅导”漂移到“逐条避错”的风险。

因此本轮不继续给 long prompt 加规则，而是新增两个压缩版离线 tutor mode，用于开发阶段消融。

## 新增条件

新增离线 tutor mode：

- `bridge_contract_compact`
- `bridge_contract_minimal`

新增 dev condition set：

```text
prompt_compression
```

包含 4 个条件：

```text
dbox_inspired_guard
bridge_contract_guard
bridge_contract_compact_guard
bridge_contract_minimal_guard
```

## 设计原则

`bridge_contract_guard` 保留现有 long prompt，作为安全控制较强的对照。

`bridge_contract_compact_guard` 只保留核心控制：

- 使用 Bridge Contract；
- 只推进一个当前最小子步骤；
- 回复形状为“承接一句 + 小观察任务 + 可短答问题”；
- 不直接补完整关键桥；
- 保留 `[LEVEL:L1|L2|L3]` 标签。

`bridge_contract_minimal_guard` 进一步压缩，只保留最小生成约束，用来测试规则极简时质量是否上升、泄露是否变多。

## 解释边界

这不是正式 prompt freeze，也不是最终论文结论。它的作用是回答开发阶段问题：

```text
Bridge Contract 当前效果受益于结构化 contract，还是被过重 prompt 拖累？
压缩 prompt 是否能提升自然度和 student-ready rate？
压缩后 critical bridge leakage 是否明显上升？
```

只有当压缩版在 dev 消融中同时保持泄露可控、质量不低于 long prompt，才考虑进入后续正式 held-out 条件。

## 验证

已新增单测覆盖：

- `bridge_contract_compact` / `bridge_contract_minimal` tutor mode；
- compact prompt 比 long prompt 明显更短；
- minimal prompt 比 compact 更短；
- compact prompt 仍保留核心 Bridge Contract 控制；
- `prompt_compression` condition set 只包含本轮 4 个条件。
