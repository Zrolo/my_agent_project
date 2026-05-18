# DBox+Repair Fairness Extension Plan 20260518

本计划只提出可选后续路径，不自动生成新实验、不新增主实验 condition、不修改线上系统。当前已完成的 DBox+Repair 结果应继续写作 targeted fairness sensitivity evidence，而不是主实验 headline。

## 当前状态

- 已有 `dbox_inspired_guard_repair` 20-case targeted review。
- 该 review 覆盖 headline-sensitive cases，而不是随机 50-case 全量。
- 当前结果：DBox+Repair overall 3.55，safe-ready 11/20，major+answer leakage 0。
- 相比同 20 case 的 DBox Guard，DBox+Repair 主要降低 severe leakage，并小幅提升 overall。
- 相比同 20 case 的 Bridge Contract compact + Guard/Repair，Bridge 仍有更高 overall / safe-ready。
- 限制：单次补评、targeted sample、与主实验 A/B 流程存在 reviewer/protocol mismatch。

## Option A：第二教练复评 20-case risk/discussion rows

做法：

- 从现有 20-case review 中抽取 `needs_discussion=yes`、borderline show、minor leakage、high burden 的 rows。
- 让第二教练只复评这些 risk/discussion rows。
- 不新增 condition，不重新生成回复，只复核已有 DBox+Repair outputs。

优点：

- 成本最低。
- 能缓解 reviewer/protocol mismatch。
- 对当前 appendix sensitivity 的可信度提升明显。

限制：

- 仍不是完整 50-case DBox+Repair evaluation。
- 仍不能写成主实验 condition-level 结论。

适合写法：

```text
We additionally double-checked the highest-risk DBox+Repair add-on rows; the add-on remains a fairness sensitivity analysis rather than a main condition.
```

## Option B：50-case DBox+Repair full review

做法：

- 使用已有 50-row `dbox_inspired_guard_repair` 生成包。
- 按与主实验一致的 rubric / blind review workflow 补做完整 50-case review。
- 最好由 Coach A/B 双评，至少保留 priority disagreement adjudication。

优点：

- 最强地回应 baseline fairness 问题。
- 可以直接比较：
  - `dbox_inspired_guard`
  - `dbox_inspired_guard_repair`
  - `bridge_contract_compact_guard_repair`

限制：

- 成本最高。
- 如果只做单教练，仍需在论文中写成 supplemental review。
- 会增加论文结果复杂度，可能稀释主贡献。

适合写法：

```text
In a full supplemental DBox+Repair review, we compare repair-enabled DBox against repair-enabled Bridge Contract under the same rubric.
```

## Option C：保持现状，作为 appendix sensitivity 并明确 limitation

做法：

- 不追加人审。
- 保留当前 20-case targeted review。
- 在 Results / Discussion 中明确：
  - DBox+Repair 是 fairness sensitivity；
  - 不是 full 50-case double-coach main condition；
  - 不能用它证明 Bridge+Repair 对所有 repair-enabled baselines 显著胜出。

优点：

- 不增加实验成本。
- 当前证据已经足以说明我们没有忽略 DBox+Repair 公平性问题。
- 论文主线保持清楚。

限制：

- 审稿人仍可能要求更完整的 repair-enabled DBox baseline。
- 只能写 limitation，不能写强比较。

适合写法：

```text
We include a targeted DBox+Repair fairness add-on as appendix sensitivity. It reduces major/answer leakage on the targeted subset but does not replace a full double-coach 50-case add-on review.
```

## 推荐

当前投稿前最稳选择是 **Option C**，并在时间允许时做 **Option A**。只有当审稿目标明确要求 repair-enabled DBox baseline 的完整公平性时，才执行 **Option B**。
