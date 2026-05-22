# CP-MissingBridgeBench v4.1 实验协议（2026-05-22）

## 1. 本轮目标

v4.1 不是对 v2 结果的补丁式美化，也不是为了把 Bridge Contract / Repair 写成胜利方法。本轮目标是开发并验证一个新的候选 tutoring design：

> Bridge-aware DBox hybrid: decomposition first, bridge boundary second.

也就是说，v4.1 借鉴 DBox-style decomposition 的推进能力，同时用 case-specific bridge boundary 控制回复不要替学生完成当前缺失的推理步骤。

本协议只启动 v4.1 的实验开发路线，不修改 dialogue-state v3 主实验，不重算主表，不修改线上 AIChat，不改变学生可见回复，不新增现有论文结果。

## 2. 为什么不能直接跑 100-case

v2 100-case / 700-response 人工评审已经显示：`DBox-inspired + Guard` 是当前最强设计，而 Bridge Contract / Repair 变体没有自动胜出。因此 v4.1 必须按新方法开发处理，不能直接把 100-case 当 prompt tuning 场地。

如果直接在 100-case 上边跑边改，会产生两个问题：

- 100-case 被用作调参集，后续结果难以作为 held-out evidence。
- prompt 失败后继续修补，会让论文陷入 post-hoc prompt optimization，而不是可复核实验。

因此 v4.1 采用三阶段门控：

1. 20-case dev stabilization：只用于 prompt 稳定和故障排查。
2. 30-case holdout：prompt 冻结后验证，不再调 prompt。
3. 100-case final evaluation：只有 holdout 达标后才执行。

## 3. v4.1 设计原则

### 3.1 Bridge Judge 只生成可控边界

Bridge Judge 可以为内部审计生成较具体的 `private_bridge_target`，但给 Tutor 的字段必须是 `tutor_visible_boundary` 和 `allowed_support`。Tutor 不应直接看到完整答案骨架。

核心分离：

- `private_bridge_target`：内部 freeze / Guard / human audit 使用，不直接给 Tutor 当可复述内容。
- `tutor_visible_boundary`：给 Tutor 的边界说明，只说明不能跨哪类推理步骤。
- `forbidden_content_pattern`：模式级 forbidden content，不写完整公式、完整 check、完整代码或完整证明。
- `allowed_support`：允许的帮助方向，必须具体但不越界。

### 3.2 Tutor 先做分解，再控桥

v4.1 Tutor 不采用“Bridge Contract-first”的空泛安全路线，而采用：

1. 识别学生当前卡点。
2. 给出 1--2 个结构化分解步骤。
3. 指向一个具体下一步动作。
4. 不替学生完成 `private_bridge_target`。

回复必须能推进学生半步，不能只说“你再想想状态/转移/边界”。

### 3.3 Guard 与教练标签一致

Guard 输出必须使用与教练评分一致的泄露标签：

- `no_leakage`
- `minor_bridge_leakage`
- `major_bridge_leakage`
- `answer_leakage`

Guard 是辅助诊断，不替代人类教练。

### 3.4 Repair 只做定点修复

Repair 不允许默认整段重写。它应尽量保留原回复中安全且有用的部分，只软化或删除越界句。

Repair 输出必须记录：

- `repair_scope`
- `preserved_helpful_parts`
- `removed_or_softened_parts`
- `anti_vagueness_check`

如果 Repair 后回复变成泛泛鼓励，也视为失败。

## 4. Prompt 语言规则

v4.1 采用：

- JSON keys：英文，保持工程解析稳定。
- JSON values：按语义可中文，可包含必要英文算法术语。
- 学生可见回复：中文为主。
- 专有缩写首次解释，例如 dynamic programming（动态规划，DP）。

不采用“所有 JSON 字段名中文化”。原因是中文字段名容易导致解析不稳定，也不利于工程复现；但学生可见内容必须符合中文教学场景。

## 5. Stage 1：20-case dev stabilization

输入清单：

`docs/research/cp_missingbridgebench_v4_20case_dev_selection_manifest_20260522.csv`

选择原则：

- 从 all-sufficient v2 100-case source manifest 中确定性抽样。
- 覆盖 dominant real-log families：debugging / implementation。
- 覆盖 mid-frequency families：data structure / aggregation.
- 保留少量 rare/boundary families：correctness / boundary order / state representation / policy.
- 优先选择 privacy_review_status=passed；稀有 family 不足时允许 pending，但只做内部 dev，不公开 case-level 内容。
- 不按模型表现选择，不按 Bridge Contract / Repair 支持程度选择，不按预期结果好看选择。

Stage 1 检查项：

- JSON 是否稳定可解析。
- Bridge Judge 是否把 private target 与 tutor-visible boundary 分开。
- Tutor 是否有具体下一步动作。
- Tutor 是否避免泄露当前 missing bridge。
- Guard 是否能发现 major/answer leakage。
- Repair 是否定点修复而不是整体保守化。
- 回复是否不空泛、不高负担。

Stage 1 可调内容：

- prompt wording。
- schema field explanation。
- failure-mode instruction。
- anti-vagueness instruction。

Stage 1 不可作为论文结果。

## 6. Prompt freeze gate

20-case dev 完成后，必须冻结：

- Judge prompt version。
- Tutor prompt version。
- Guard prompt version。
- Repair prompt version。
- model/version/decoding settings。
- generation script commit。
- dev-case list。

冻结后不得因 holdout 结果继续改 prompt。若改 prompt，必须重开新版本，例如 v4.2，并重新记录 dev/holdout 边界。

## 7. Stage 2：30-case holdout

30-case holdout 从未用于 dev tuning 的 v2 source cases 中选择。选择时覆盖 debugging、implementation、data structure、aggregation，以及少量 rare/boundary cases。

通过标准不是“必须显著赢”，而是对当前最强 baseline `DBox-inspired + Guard` 达到可接受对比：

- overall delta 不低于 -0.10。
- major+answer leakage 不高于 DBox-inspired + Guard 超过 1 case。
- student-ready 不低于 DBox-inspired + Guard 超过 3 cases。
- safe-ready 不低于 DBox-inspired + Guard 超过 3 cases。
- high burden 不明显增加。
- answer leakage = 0。

若 holdout 未达标，v4.1 不进入 100-case final evaluation，不写成方法优势。

## 8. Stage 3：100-case final evaluation

只有 Stage 2 通过后才执行 100-case final evaluation。

100-case final 可以有两种范围：

1. Minimal fair comparison：v4.1 vs DBox-inspired + Guard。
2. Full matrix：v4.1 加入 7-design matrix 的扩展比较。

优先推荐 minimal fair comparison。若 full matrix 成本过高，不应强行扩展。

100-case final 仍是 offline response generation，不进入线上 AIChat，不展示给学生，不评估 learning outcome。

## 9. 人类评审要求

v4.1 若要进入论文结果，必须有人类教练盲审或至少与 v2 同标准的可复核评审包。AI preliminary review 只能用于 dev triage。

评审维度沿用 50-case / v2 审核逻辑：

- 是否抓住学生当前卡点。
- 是否接住题目和当前材料。
- 帮助强度是否合适。
- 是否泄露关键桥。
- 下一步是否清楚。
- 学生回复负担是否过高。
- 总体质量和是否愿意给学生看。

## 10. 公开边界

本实验不得公开：

- 学生原文。
- 完整代码。
- 完整 observed AIChat response。
- row-level hash 表。
- hash salt 或可逆映射。
- 私有 workbook。

若 consent/reporting gate 仍 pending，只能公开 aggregate/process counts 和 protocol，不公开 case-level 内容。

## 11. 成功与失败都如何写

如果 v4.1 达标：

> v4.1 is a follow-up candidate design that narrows the gap with the strongest DBox-inspired + Guard baseline while preserving bridge-boundary discipline.

如果 v4.1 不达标：

> The v4.1 development run further supports the benchmark's diagnostic value: bridge-aware constraints are not sufficient unless they are paired with decomposition quality, concrete next actions, and targeted repair.

无论成功或失败，都不能写：

- deployed system superiority。
- learning gains。
- online intervention。
- LLM judge replaces coach review。
- Repair causally explains main-experiment improvement。
