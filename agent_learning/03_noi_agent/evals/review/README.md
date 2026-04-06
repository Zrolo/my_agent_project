# Review Eval Notes

- `cases.jsonl`: 真实打卡样例源数据
- `promptfoo_tests.jsonl`: promptfoo 可直接消费的测试集
- `run_review_case.py`: 调用真实 `generate_review(...)`
- `run_review_case_kimi_cli.py`: 复用项目 prompt builder，但通过 `kimi-cli` 直接请求 `kimi-k2.5`
- `review_rubric_v2.json`: 当前 review 四字段质量评测标准
- `promptfoo.yaml`: baseline vs mode-route 对比配置
- `promptfoo.kimi-cli.yaml`: baseline vs mode-route 的 `kimi-cli` 评测配置
- `build_promptfoo_sample.py`: 生成每种 mode 各 1 条的 sample 测试集
- `promptfoo.kimi-cli.sample.yaml`: 基于 sample 测试集的 `kimi-cli` 评测配置

运行前请先导出环境变量：

```bash
export OPENAI_API_KEY="$MOONSHOT_API_KEY"
export OPENAI_API_BASE_URL="https://api.moonshot.cn/v1"
```

基线与对比命令：

```bash
python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/export_cases.py
npx promptfoo@latest eval -c /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.yaml
```

`kimi-cli` 版快速对比命令：

```bash
python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/export_cases.py
/opt/homebrew/bin/promptfoo eval --max-concurrency 2 --filter-first-n 1 -c /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.kimi-cli.yaml
```

sample 版命令：

```bash
python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/build_promptfoo_sample.py
/opt/homebrew/bin/promptfoo eval --max-concurrency 1 -c /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/promptfoo.kimi-cli.sample.yaml
```

直接质量评测命令：

```bash
python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_quality_eval.py /tmp/promptfoo_tests.sample.no_editorial.no_rubric.jsonl
```

重复跑聚合命令：

```bash
python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_quality_eval.py /tmp/promptfoo_tests.sample.no_editorial.no_rubric.jsonl 2
```

这条脚本会直接输出：

- `json_ok_rate`
- `fields_ok_rate`
- `rubric_avg_score`
- `rubric_max_score`
- `rubric_avg_ratio`
- `repeats`
- 每个 case 的 `attempts`

适合在 `promptfoo` 的 `llm-rubric` 落表太慢时，继续沿同一批 case 做 baseline vs mode-route 对比。
当前 rubric 规则已从脚本内联文本收成 `review_rubric_v2.json`，后续更新 judge 标准时优先改 rubric 文件，不直接改脚本主体。

当前已验证：

- `python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/export_cases.py`
  - 当前会导出 `20` 条真实 case
  - 当前分布：
    - `independent_reflect = 6`
    - `failed_verdict = 6`
    - `stuck_bridge = 6`
    - `editorial_transfer = 2`
- `python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_case.py`
  - 已能对单条真实 case 返回 review JSON
- `python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/run_review_case_kimi_cli.py`
  - 已能对单条真实 case 返回 `kimi-cli -> kimi-k2.5` 的 review JSON
  - 当前 runner 会显式给 `kimi-cli` 注入 Moonshot 配置，避免默认 `kimi-code` provider 导致的 `LLM not set`
  - 当前 runner 会自动去掉 `kimi-cli` 返回里的 ```json fenced code block```，再做 JSON 解析
- `python3 /Users/kongyouli/Downloads/my_agent_project/agent_learning/03_noi_agent/evals/review/build_promptfoo_sample.py`
  - 已能生成 `4` 条 sample 测试集：
    - `editorial_transfer = 1`
    - `failed_verdict = 1`
    - `independent_reflect = 1`
    - `stuck_bridge = 1`
- `/opt/homebrew/bin/promptfoo eval -c .../promptfoo.yaml`
  - 已确认能成功启动，不存在 config/exec provider 级错误
- `/opt/homebrew/bin/promptfoo eval -c .../promptfoo.kimi-cli.yaml`
  - 已确认能成功启动 baseline + mode-route 的 `kimi-cli` 双 provider，不存在 exec provider 级错误
- `python3 .../run_review_quality_eval.py /tmp/promptfoo_tests.sample.no_editorial.no_rubric.jsonl`
  - 已确认能成功跑出 non-editorial sample 的三指标
  - 最新一轮结果：
    - `baseline_current_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 0.667`、`rubric_avg_score = 1.667`
    - `mode_route_kimi_cli`：`json_ok_rate = 1.0`、`fields_ok_rate = 1.0`、`rubric_avg_score = 2.667`
  - 当前脚本已支持重复跑与聚合，适合用来判断同一 prompt 的随机波动

当前未完成：

- baseline vs mode-route 的全量三指标还未跑完
- 当前瓶颈是：
  - 单条 `generate_review(...)` 本身较慢
  - `llm-rubric` 也会再走一轮模型调用
  - 即便切到 `kimi-cli`，单条真实 review 仍需要几十秒，完整 provider-case 组合依旧耗时明显偏长
