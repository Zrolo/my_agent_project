# Project Status After Taxonomy Revision 20260517

## 当前阶段

当前项目状态是：

```text
formal human-review evidence candidate + taxonomy framing stabilized
```

`taxonomy_specificity_revision_20260517` 已把论文口径锁为：

```text
cognitive bridge family + leakage mechanism + surface anchor
```

其中 bridge bucket 是 Research v1 operational cognitive bridge family；DP state、binary-search check、lazy propagation、tree difference、local code 等是 surface anchors。

## 已完成

| area | status |
| --- | --- |
| 50-case generation | dialogue-state v3 50-case reviewed candidate 已完成 |
| response generation | 7-condition 主表 350 rows 已完成 |
| Coach A review | 350 rows 全量盲评完成 |
| Coach B review | 350 rows 全量复评完成 |
| priority60 adjudication | 高优先级 A/B 分歧 60 rows 已裁决 |
| sensitivity analysis | Coach A/B only 与 adj+CoachA/B 已完成 |
| slice analysis | main scaffold / caution / clarification / policy slices 已完成 |
| taxonomy specificity wording | P0/P1 reviewer-facing wording 已完成并推送 |
| paired uncertainty | main_scaffold_eval 配对 W/T/L、bootstrap CI、permutation 已有 |
| DBox repair add-on generation | `dbox_inspired_guard_repair` 50-row 生成包已有 |
| repair stress template | 30-row same-candidate natural repair template 与盲评工作簿已生成 |
| DBox+Repair fairness add-on human review | 20-case headline-sensitive 补评已完成，并生成 fairness sensitivity report |
| LLM grader calibration prompt packs | priority60 adjudicated 60-row pack 与 adj+CoachA/B sample20 packs 已生成；CoachB sample20 pack 已补齐 prompt context |
| LLM grader calibration results | DeepSeek-backed priority60 180/180 ok；adj+CoachA sample20 60/60 ok；adj+CoachB sample20 60/60 ok。此前 Kimi-backed 结果降级为 exploratory/tooling record |

## 仍需完成

| task | current state | priority |
| --- | --- | --- |
| paper-ready tables | 本轮已整理主表与 pairwise doc | P0 complete / maintain |
| Repair same-candidate stress labels | 30/30 blind before/after pairs 已完成；结果显示 leakage improved 16/30、worse 0/30、major leakage 7 -> 0，但 burden worsened 12/30 | P0 complete |
| DBox+Repair fairness add-on full review | 已完成 20-case targeted review；若时间允许可扩到 50-case 或二教练复评 risk cases | P1 optional |
| LLM grader calibration | DeepSeek-backed 三个 reference views 已完成；结果显示 case-specific rubric 改善部分辅助指标，但 priority60 critical recall 仍为 0 | P1 complete / paper wording conservative |
| Results / Discussion prose | dialogue-state v3 draft 已更新；已新增 manuscript-style 压缩正文和正式 section draft `paper_results_discussion_section_dialogue_state_v3_20260518.zh.md` / `.md` | P1 complete / needs final paper editing |
| targeted adjudication extension | 已有计划和 candidate workbook；是否追加取决于时间 | P1 optional |

## 当前论文主张边界

论文应写成 evaluation framework + trade-off，而不是系统绝对胜利：

```text
CP-MissingBridgeBench 能揭示 LLM tutors 在 quality、critical-bridge leakage 和 student burden 之间的权衡。
```

可以写：

- DBox-inspired decomposition 是强 baseline；
- Bridge Contract compact + Guard/Repair 在主人工评审口径下呈现较有利的 overall 和 critical-leakage-control trend；
- no-direct-solution 不等于无 critical bridge leakage；
- student-ready / rank 对 rater strictness 敏感；
- Repair 因果解释已有 same-candidate stress 支撑；DBox+Repair fairness 目前是 targeted sensitivity，不是 full 50-case 双教练补评。

不能写：

- Bridge Contract 全面显著优于所有 baseline；
- Guard-only 修复最终输出；
- Repair 已被主实验证明因果有效；
- Coach A/B 或 priority60 是 final gold；
- 50-case set 覆盖全部 CP tutoring 情景。

## 下一步执行顺序

1. 以 `paper_results_discussion_section_dialogue_state_v3_20260518.zh.md` / `.md` 为基底，进入真正论文格式编辑。
2. 视时间决定是否扩展 DBox+Repair 到 50-case 或二教练复评 risk cases。
3. 视时间决定是否追加 targeted adjudication extension。
4. 最后统一检查 claim wording、table captions、limitations 和 appendix 边界。
