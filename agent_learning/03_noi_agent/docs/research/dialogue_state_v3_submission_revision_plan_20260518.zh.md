# Dialogue-State v3 投稿前修订计划 20260518

## 1. 当前状态

Dialogue-state v3 当前应被描述为：

```text
formal human-review evidence candidate + evidence-package audit passed with minor revision items
```

它不是 final gold，也不是完整线上系统验证。当前证据足以支撑一篇以评测框架、人工评审、质量-安全-学生负担权衡为主线的论文初稿，但论文写作必须保持以下边界：

- 主 headline 只使用 `main_scaffold_eval` slice。
- all-50 aggregate 只作为 appendix / sensitivity。
- Coach A、Coach B、priority60 adjudicated labels 都不能写成 gold。
- Guard-only 只能写成 guard-instrumented / runtime signal。
- Repair 因果证据只来自 same-candidate stress test。
- DBox+Repair 只是 targeted fairness sensitivity，不是 full main condition。
- DeepSeek LLM grader 只能作为 auxiliary calibration，不能替代人类教练。

## 2. 外部审查后已处理的修订

已完成的小修包括：

1. Web-AI review bundle v2 已补入 `evals.review` 相关依赖，使核心 unit tests 在 bundle 内可复跑。
2. `dbbbd5c`、`33a5dd7` 和 branch tip 的关系已在 index、handoff 和 reviewer prompt 中说明：
   - `dbbbd5c` 是 evidence-content base；
   - `33a5dd7` 是 evidence-package gates checkpoint；
   - 后续 branch-tip commit 主要收紧 handoff / prompt / wording。
3. 论文正向表述中的强胜出口径已降级为 `favorable trend`。
4. Results / Discussion 中已显式区分 main result、sensitivity、stress test 和 calibration。
5. `verify_dialogue_state_v3_reports.py`、`reproduce_dialogue_state_v3_tables.py` 和核心 unit tests 已在完整仓库通过。

## 3. P0：进入论文正文前必须完成

### P0.1 固定 Methods / Evaluation 写作骨架

写作来源：

- `docs/research/evaluation_protocol_v3.zh.md`
- `docs/research/response_review_rubric_v3.zh.md`
- `docs/research/baseline_protocol_v1.zh.md`
- `docs/research/dialogue_state_v3_evidence_manifest_20260518.json`
- `docs/research/dialogue_state_v3_paper_claims_final_gate_20260518.zh.md`

正文需要说明：

- missing bridge 是学生从当前已知到下一步动作之间缺失的关键推理桥；
- critical bridge leakage 是没有直接给完整代码/题解，但提前说穿学生本应推出的关键中间推理；
- taxonomy 使用 `cognitive bridge family + leakage mechanism + surface anchor`；
- concrete algorithm patterns 只是 surface anchors，不是 benchmark 只覆盖这些小场景；
- 7 个 condition 是离线 human-review harness，不等于线上默认系统；
- 盲审使用 case-specific rubric，先定义 success criteria / forbidden content / acceptable reveal / expected next action，再评分。

验收标准：

- 不出现 `final gold`、`Guard repairs final output`、`Bridge Contract significantly outperforms all baselines` 这类表述。
- 不把 all-50 平均写成主 headline。

### P0.2 固定 Results 主表和段落

写作来源：

- `docs/research/dialogue_state_v3_main_paper_ready_tables_20260517.zh.md`
- `docs/research/dialogue_state_v3_pairwise_win_tie_loss_20260517.zh.md`
- `docs/research/paper_results_discussion_section_dialogue_state_v3_20260518.zh.md`
- `evals/aichat/reproduce_dialogue_state_v3_tables.py`
- `evals/aichat/verify_dialogue_state_v3_reports.py`

正文推荐顺序：

1. Human review reliability。
2. Main scaffold evaluation。
3. Pairwise uncertainty。
4. Sensitivity and slice analysis。
5. Observed error taxonomy。
6. Repair same-candidate stress。
7. DBox+Repair fairness add-on。
8. DeepSeek LLM grader calibration。

验收标准：

- `bridge_contract_compact_guard_repair` 只能写成主人工评审口径下呈现 favorable overall / critical-leakage-control trend。
- pairwise CI 跨 0 的比较不能写成 significant dominance。
- Repair 的因果段落必须引用 same-candidate stress，而不是主实验 condition 均值。

### P0.3 固定 Discussion / Limitations

必须正面写出的限制：

- 50-case set 是 high-risk dialogue-state CP tutoring evidence candidate，不覆盖所有 CP tutoring 情景。
- student-ready 和 rank 对评分者严格程度敏感。
- priority60 adjudication 覆盖高优先级分歧，但不是 final gold。
- Guard-only 是 instrumentation，不是 rewrite。
- DBox+Repair 只有 20-case targeted sensitivity。
- LLM grader 在 DeepSeek priority60 上 critical recall 很弱，不能替代人审。

验收标准：

- 不把限制写成附带小字，而是在 Discussion 中作为方法学边界正面报告。

### P0.4 最终 claim gate 检查

投稿前运行：

```bash
python3 evals/aichat/verify_dialogue_state_v3_reports.py
python3 evals/aichat/reproduce_dialogue_state_v3_tables.py --output-json /tmp/dialogue_state_v3_reproduced_final.json
python3 -m unittest test_dialogue_state_v3_evidence_package_unit.py test_llm_grader_calibration_pack_unit.py
rg -n -e "final gold" -e "Guard fixes final output" -e "Guard repairs" -e "significantly outperforms all baselines" -e "all 50 cases headline" -e "stable\\s+advantage" docs evals
```

若 `rg` 命中 historical / forbidden wording 说明文档，需要人工判断是否是“禁止表述列表”中的反例，而不是论文正向主张。

## 4. P1：正文成稿时完成

1. 写 Introduction：强调 turn-level CP tutoring 中的 missing bridge 与 critical bridge leakage，而不是把论文包装成一个线上产品系统。
2. 写 Related Work：对比 no-direct-answer prompting、Socratic tutoring、LLM-as-judge、agent evaluation 和 programming-help benchmarks。
3. 做 Figure / Table 清单：
   - Figure 1：student turn → case-specific rubric → tutor response → human review / guard / repair evidence。
   - Table 1：benchmark slices and case counts。
   - Table 2：conditions and interpretation boundaries。
   - Table 3：main scaffold results。
   - Table 4：paired W/T/L and uncertainty。
   - Table 5：repair stress and DBox+Repair sensitivity。
4. 整理 Appendix：
   - human review reliability；
   - observed error taxonomy；
   - full sensitivity tables；
   - repair same-candidate protocol；
   - DBox+Repair fairness add-on；
   - DeepSeek LLM grader calibration；
   - evidence manifest and reproduction commands。
5. 决定 legacy bilingual docs validator debt 是否修复。它不阻塞主证据，但如果投稿 artifact 要完全干净，可以补齐 historical docs pairing 或在 README 中保留明确 exemption。

## 5. 当前明确不做

当前阶段不要做：

- 不新增主实验 condition；
- 不接入线上 active mode；
- 不修改 prompt；
- 不改 main experiment raw data；
- 不回头改 held-out cases；
- 不用 LLM grader 替代人工标签；
- 不把 DBox+Repair 20-case add-on 扩写成主实验结果。

## 6. 推荐执行顺序

1. 先把 Methods / Evaluation 写成论文正文草稿。
2. 再把 Results 从现有 `paper_results_discussion_section` 压缩成投稿正文长度。
3. 接着写 Discussion / Limitations，锁定 claim gate。
4. 然后整理 figures / tables。
5. 最后写 Abstract / Introduction，因为这两部分最容易过度宣传，应在结果边界完全固定后再写。

一句话版本：

```text
下一步不是继续扩实验，而是把现有 dialogue-state v3 evidence package 写成一篇边界清楚、可复核、不过度声称的论文初稿。
```
