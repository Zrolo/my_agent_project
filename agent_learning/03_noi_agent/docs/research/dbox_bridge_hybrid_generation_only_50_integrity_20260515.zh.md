# DBox / Bridge Hybrid 50-case Generation-only 完整性检查

- Manifest: `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged/manifest.json`
- 输入数据集: `docs/research/bridgebench_cp_heldout_v4_50_draft.jsonl`
- 条件集: `dbox_bridge_hybrid`
- Case 数: 50
- Condition 数: 5
- 预期行数: 250
- Combined JSONL 行数: 250
- 最终回复非空行数: 250
- 盲评表行数: 250
- Analysis ready: True
- Headline ready: True

## 本轮条件

1. `enhanced_prompt_only_clean`
2. `dbox_inspired_clean`
3. `dbox_inspired_guard`
4. `bridge_contract_compact_guard`
5. `bridge_guided_dbox_style_guard`

## 完整性结论

本轮主运行原始输出中有 1 条空回复：

- `heldout_v4_luogu_018` × `bridge_guided_dbox_style_guard`

原因是 Bridge Judge 输出 JSON 解析失败，导致该行没有进入 tutor 生成。随后已进行 targeted rerun，并将补跑结果 merge 到新的 clean run pack：

- `evals/aichat/ad_hoc_runs/dbox_bridge_hybrid_generation_only_50_20260515_merged`

合并后完整性检查通过：

- 缺失 case-condition pair: 0
- 重复 case-condition pair: 0
- 空 final response: 0
- stage errors: 0
- `[LEVEL:...]` 内部标签残留: 0

## 关键运行统计

| 项目 | 数值 |
| --- | ---: |
| Combined rows | 250 |
| Empty final response | 0 |
| Stage errors | 0 |
| `[LEVEL:...]` hits | 0 |
| final_response_source=candidate | 250 |

## Guard / Leakage 动作分布

| safe_action | 行数 |
| --- | ---: |
| pass | 119 |
| rewrite | 31 |
| 无 Guard 条件 / 不适用 | 100 |

## 各条件延迟

| condition | p50 latency ms | p95 latency ms |
| --- | ---: | ---: |
| `enhanced_prompt_only_clean` | 20301.8 | 49540.2 |
| `dbox_inspired_clean` | 11328.9 | 27239.7 |
| `dbox_inspired_guard` | 22341.8 | 44565.2 |
| `bridge_contract_compact_guard` | 17753.0 | 39984.9 |
| `bridge_guided_dbox_style_guard` | 22449.6 | 53541.0 |

## 自动摘要提醒

本轮虽然完整性通过，但 summary 仍标记为 dev gate 需要复查，主要原因包括：

- `critical_bridge_leakage`
- `final_static_answer_slot_risk`
- `final_static_filled_trace_risk`
- `final_static_worked_example_risk`

这些是静态/自动风险信号，不等同于最终人工结论。下一步应进入 AI 初筛和人类教练盲评，重点确认：

1. 回复是否真的接住了学生当前问题与近期对话。
2. DBox-style scaffold 是否比 Bridge Contract 更自然。
3. Bridge-guided DBox-style 是否在保留自然度的同时减少 critical bridge leakage。
4. Guard 触发 rewrite 的行是否真的比原回复更安全。
5. 静态风险是否存在误报，尤其是 worked-example 和 filled-trace 类提示。
