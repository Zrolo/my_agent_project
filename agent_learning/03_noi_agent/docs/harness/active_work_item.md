# 当前工作项

## 本文件的写入标准

只写**当前正在推进的一轮任务**：

- 当前目标
- 本轮非目标
- 本轮需要加载的 contract 文件
- 本轮涉及文件
- 验收标准
- 当前风险 / 下一步

不要写：

- 长期规则
- 已完成的全部历史
- 与当前任务无关的讨论

---

## 当前目标

## 本轮并行新增目标：NOI review mode routing + eval 基线

在不改 review JSON schema、不删现有 guard、不动 SSE/confirm_pool/A/B/C 触发器的前提下：

1. 在 `generate_review(...)` 入口归一化 `submission_result`
2. 用 `_detect_review_mode(...)` 把 review 分成：
   - `failed_verdict`
   - `stuck_bridge`
   - `independent_reflect`
   - `editorial_transfer`
3. 在 `_build_review_system_prompt(mode=...)` 末尾追加 4 套 supplement
4. 建立 `promptfoo` 评测骨架，先把真实 `cases.jsonl`、`run_review_case.py` 和 `promptfoo.yaml` 落到仓库
5. 用 baseline vs mode-route 做对比，不靠主观感觉判断 prompt 有没有进步

把“学生分流闭环 + confirm 迁移验证”这一轮继续往学生端真实体验推进，当前优先落地：

1. 保持当前 A/B/C 主链、remedy 收紧、confirm_pool 最小表与 self-check confirm 状态机稳定
2. 在不改 review JSON schema、不做多段生成的前提下，把“打卡后等待黑盒”改成“固定阶段可见”
3. 当前后端已经接通 `GET /api/checkins/{checkin_id}/stream`，用固定阶段埋点推送：
   - `received`
   - `queued`
   - `llm_start`
   - `llm_done`
   - `review_parse`
   - `review_saved`
   - `quiz_generating`
   - `completed`
   - `failed`
4. 当前前端已经从“只流状态”推进到“状态 + 正文草稿预览”：`pending` 时优先用 `fetch + ReadableStream` 订阅 SSE，失败后退回现有轮询
5. 当前 review 卡已做第一轮瘦身：默认只留 4 条主视图，详细诊断折叠
6. 当前 quiz 已开始沉淀模板与路径边的数据库骨架，但还未切换成模板优先生成
7. 在这条新链稳定后，再继续做浏览器级学生端联调，并决定是否扩第二批固定题

---

## 本轮非目标

本轮不做：

- 新的学生端页面或模式选择
- review JSON schema 变更
- 删除现有 guard
- SSE / confirm_pool / A/B/C 分流触发器 / 多 agent 链路
- review 正文 token 流式输出
- review 多段生成或分段写库
- 重型独立 `Reviewer` 实例
- 全量自动化 confirm_pool 导入
- 全量洛谷标签映射
- 后端真实生成耗时优化
- retry 恢复首轮 `problem_card / analysis_source / local_problem_id`

---

## 本轮需要加载的 contract 文件

- `docs/harness/ai_output_contracts.md`
- `docs/harness/review_quiz_quality_gate.md`
- `docs/subjects/noi/confirm_pool_mapping_v1.json`

---

## 本轮涉及文件

- `docs/harness/current_system_state.md`
- `docs/harness/active_work_item.md`
- `evals/review/export_cases.py`
- `evals/review/run_review_case.py`
- `evals/review/run_review_case_kimi_cli.py`
- `evals/review/promptfoo.yaml`
- `evals/review/promptfoo.kimi-cli.yaml`
- `evals/review/build_promptfoo_sample.py`
- `evals/review/promptfoo.kimi-cli.sample.yaml`
- `evals/review/cases.jsonl`
- `evals/review/promptfoo_tests.jsonl`
- `evals/review/README.md`
- `api_server.py`
- `database.py`
- `review_engine.py`
- `prepare_confirm_pool.py`
- `seed_confirm_pool.py`
- `static/app.js`
- `test_review_stream_api_unit.py`
- `docs/superpowers/specs/2026-04-04-review-streaming-content-and-quiz-template-design.md`
- `docs/superpowers/plans/2026-04-04-review-streaming-content-and-quiz-template-implementation-plan.md`
- `test_learning_routing_unit.py`
- `docs/subjects/noi/confirm_pool_tag_stats_v1.json`
- `docs/subjects/noi/confirm_pool_mapping_v1.json`
- `docs/subjects/noi/confirm_pool_seed_v1.json`
- `docs/harness/project_invariants.md`

---

## 验收标准

0. `submission_result` 进入 `generate_review(...)` 后已统一归一化为小写值
0. `_detect_review_mode(...)` 与 4 套 `system prompt supplement` 有单测保护
0. `evals/review/` 目录已能从真实数据库导出 `cases.jsonl`
0. `run_review_case.py` 能对单条 case 返回真实 review JSON
0. `promptfoo.yaml` 至少能成功起跑，不存在配置级错误
0. `promptfoo.kimi-cli.yaml` 至少能成功起跑，不存在 provider 接入级错误
0. `build_promptfoo_sample.py` 能生成 sample 测试集，`promptfoo.kimi-cli.sample.yaml` 能成功起跑
1. `test_learning_routing_unit.py` 通过
2. `test_review_async_api_unit.py` 与 `test_review_engine_messages_unit.py` 不回退
3. `prepare_confirm_pool.py` 能输出稳定 JSON 统计
4. `seed_confirm_pool.py` dry-run 与实际导入都可用
5. `confirm_pool` 已至少有 8 个固定种子题可命中
6. 固定池优先于 LLM 的命中顺序已被 `test_learning_routing_unit.py` 回归保护
7. `current_system_state.md`、`active_work_item.md`、`project_invariants.md` 已同步
8. `project_invariants.md` 不再和当前三标签实现冲突
9. `GET /api/checkins/{checkin_id}/stream` 能按阶段推进，且 owner 之外访问返回 404
10. `static/app.js` 在 `pending` 时优先订阅流式状态/草稿，流不可用时自动退回轮询
11. `pending` 卡能显示 4 字段草稿预览，而不是只显示静态等待
12. quiz 首次生成后能入库到模板表，并记录最小路径边

---

## 当前风险

0. 当前 `promptfoo` 全量评测虽然已经成功启动，但 `40` 个 provider-case 组合在真实 LLM 上耗时很长；当前瓶颈是生成耗时，不是配置错误
0. 当前 `kimi-cli` 版 promptfoo 也已成功启动，但单条真实 review 仍需几十秒；它解决的是“评测链接法”，不是“单条评测很快”
0. `kimi-cli` 默认配置原本走 `kimi-code` provider；当前 runner 已显式注入 Moonshot 配置并对 fenced JSON 做兼容，否则会遇到 `LLM not set` 或 `invalid_json`
0. 已完成第二轮“去 editorial、去 llm-rubric”的快指标复测：baseline 和 mode-route 当前都达到 `json_ok_rate = 1.0`、`fields_ok_rate = 1.0`
0. mode-route 上一轮暴露出的 JSON 稳定性问题，已通过“禁止字段内容出现半角双引号”这条 prompt 约束显著收敛
0. 又捕获到一类新的 `invalid_json`：`stuck_bridge` 的 `transfer_signal` 会把题面特征再次包进半角双引号；当前已在 `stuck_bridge` supplement 中新增“不加引号”约束，并通过单点回测和整组快指标复测确认已收敛
0. 最新一轮“去 editorial、去 llm-rubric”的快指标为：
   - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 24.31`
   - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`avg_elapsed_seconds = 29.98`
0. 已开始继续收“报告太元知识化”的问题：当前全局规则新增 `next_action / suggested_topic` 要优先回到当前题，不写专项训练、经典题、做3道、变式或拓展；`failed_verdict` 也要求优先指出当前题该先检查哪一处代码、判断或输出
0. 对 `failed_verdict_296` 的回测已确认这条规则有效：`next_action` 已回到当前题的 `且/或` 判断逻辑，不再默认滑向“做3道”式建议
0. 当前主线已经从“先收 JSON 稳定性”切到“继续跑带 `llm-rubric` 的非 editorial sample”，验证 mode-route 是否真的在质量分上优于 baseline
0. 已新增 `evals/review/run_review_quality_eval.py`，绕开 promptfoo 落表慢的问题，直接沿用同一批 case 和同一套 rubric 输出三指标
0. 当前这条直接质量评测链已经跑出一轮 non-editorial sample 结果：
   - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 0.667`、`rubric_avg_score = 1.667`
   - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`rubric_avg_score = 2.667`
0. 当前已能确认：mode-route 在 non-editorial sample 上不只是追平快指标，而且质量分也明显优于 baseline
0. 继续收 `stuck_bridge_57` 低分样例时，已观察到同一 prompt 在不同轮次上仍有随机波动：单点回测可返回合法 JSON，但单 case 质量评测里 mode-route 偶发又会掉到 `fields_ok = 0`
0. 当前剩余风险已经从“规则没写到”缩到“同一 prompt 的稳定性波动”；后续需要用重复跑或更稳的聚合方式来判断质量，不宜只看单次结果
0. `run_review_quality_eval.py` 当前已支持 `repeats` 聚合；已用 `stuck_bridge_57` 做 `repeats=2` 的最小验证，baseline 和 mode-route 当前都在 `rubric_avg_score = 2.0`，但 mode-route 仍有 `3 分 / 1 分` 的轮次波动
0. 已继续针对这条低分 case 收 prompt：`stuck_bridge` 现在额外要求不要只写限制条件、最优选择、当前进度这些抽象词
0. 当前 quality eval 的 judge 规则已正式收成 `evals/review/review_rubric_v2.json`，后续继续改评测标准时优先改 rubric 资产，不再直接把规则写死在脚本里
0. 当前真实高质量 `editorial_transfer` 样例只有 `2` 条，距离“每类 5-7 条”的理想覆盖仍有缺口
1. 当前 `minimum_spanning_tree <- 生成树` 这条映射仍偏宽，尚未进首批固定池
2. `binary_search_answer <- 二分` 当前仍标为 `defer`
3. 当前 `structure_type` 命中仍只是第一版标签映射，不是完整覆盖
4. 还没按当前版本的浏览器走查清单完成学生端真实 confirm 联调
5. 当前 `kimi-k2.5` 真实存在超时边界；即使服务已不再无限 `pending`，单条记录仍可能进入 `failed`
6. 旧进程如果没重启到带 timeout 的实例，个别 review 可能长期卡在 `pending`
7. 已用真实 `P5536` 样例复现：输入本身能过校验，但 review 生成仍可能长时间停在 `pending` 或最终 timeout
8. 当前已确认一个新的质量风险：`P5536` 这类树直径公式题，模型可能给出较准 diagnosis，但学生端字段会被 `greedy_basis` 模板盖偏
9. 当前 `max_tokens = 1200` 虽能把 `generate_review(...)` 的直接烟雾耗时压到约 `35.92s`，但会把部分输出压成“信息不足”式保守复盘，参数仍需校准
10. 当前工作区依然很脏，后续提交需要谨慎拆分
11. review prompt 压缩 v1 虽已上线实验，但仍需继续盯 3 个边界：
   - 全是泛标签时不能把标签行重新塞回 prompt
   - 关键错误公式如果在代码中段，裁剪后也必须保留下来
   - `problem_card` 不能把和当前卡点最相关的 `problem_context` 细节完全遮掉
12. 已用真实 `P5536` 样例复测压缩版 prompt：当前能在约 37.82 秒内成功返回，但会被压成 `insufficient + low`，说明“可用性保住了，诊断质量还没保住”
13. 已拆链确认：`P5536 -> insufficient` 当前不是 guard 拉回去，而是 `_call_llm()` 在 `completion_tokens = 1200` 时直接返回空字符串，`_parse_review("")` 才回落到默认 `insufficient`
14. 已补双轨实验：`compressed_1400` 和 `minimal4_1200` 都是“请求成功但空正文”，说明当前问题不只是字段数或 1200 上限，而是 `kimi-k2.5` 在这类结构化 review 请求上存在输出阶段异常
14.1 后续继续跑 quality eval 时，不能再默认把 `max_tokens/max_completion_tokens` 压到很低；我们已经验证过，这会在评测链里制造空输出、`invalid_json` 或错误，结果不可直接当作 prompt 质量结论。
15. Moonshot 官方文档对齐已开始落地：review 调用已切到 `response_format=json_object`、`max_completion_tokens`，并去掉了 `kimi-k2.5` 的显式 `temperature`
16. 新的真实边界已收窄：当前极简 JSON 烟雾调用不再出现“成功但空正文”，而是会明确落到 `finish_reason=length` 的截断失败
17. 已继续测 `max_completion_tokens` 档位：`1200/1600/1800` 都会以 `finish_reason=length` 截断，`1400` 反而直接超时；当前没有稳定可用窗口
18. 已确认 `timeout` 不是硬上限：把 `LLM_REQUEST_TIMEOUT_SECONDS` 压到 `5` 后，请求仍在约 `19.5s` 后才超时报错
19. 已把 review 主链改成 `stream=true` 并加了一次定向重试，但默认 `P5536` 样例仍在首次截断后重试失败，整次调用约 `83.78s`；当前这条路仍不足以恢复稳定正文
20. 已按用户要求把 `NOI_REVIEW_MAX_TOKENS` 的代码默认值调回 `32768`；这会减少“默认上限过小”的人为截断，但也会重新放大时长/成本风险，需重新做真实样例验证
21. 已完成一次真实样例复测：当前默认 `32768` 下，`P5536` 样例约 `80.04s` 后恢复出实体正文，说明“默认上限太小”确实是当前主因之一；但时长明显变长，仍需继续盯真实可用性
22. 当前新增的流式状态链只解决“等待黑盒”问题，不直接减少 review 真正生成耗时；如果 review 仍要 50-80 秒，前端只会更可见，不会更快
23. 当前前端流式实现依赖 `fetch + ReadableStream` 才能携带 `Authorization` 头，不能回退成裸 `EventSource`
24. 当前“流式正文”仍是草稿级预览，不是最终结构化复盘的逐 token 正文；最终内容仍以详情接口落库结果为准
25. 当前 quiz 模板库只是“先存、先连边”的骨架，还没切成模板优先检索，因此尚未真正减少 LLM 生成次数

---

## 下一步建议

- 先继续跑出至少一轮可用的 promptfoo 对比结果
- 先优先跑出一轮 sample 版 `promptfoo.kimi-cli.sample.yaml` 对比结果
- 先继续把快指标结果向 rubric 评测和更大样本扩展，确认提升不是偶然波动
- 优先记录三个数字：
  - JSON 合法率
  - 四字段非空率
  - llm-rubric 平均分
- 只有当 mode-route 版本相对 baseline 至少一项上升且整体不退，才继续深化 prompt family

1. 先完成这轮“状态 + 草稿”流式前端联调，确认 `pending -> 草稿长出 -> completed/failed` 在页面上真实可见
2. 若浏览器环境不支持流式读取或流意外断开，确认能自动退回现有轮询，不出现卡死
3. 流式草稿链稳定后，再按 `BROWSER_WALKTHROUGH_V1_2.md` 做 A/B/C 分流闭环联调
4. 再决定 quiz 模板库下一轮是否切到“模板优先，LLM 兜底”
5. review 耗时优化仍放在后面处理：当前更实际的是先确认默认 `32768` 在更多真实样例下是否稳定、时长是否可接受
6. `binary_search_answer` 继续维持 defer，暂不放开
