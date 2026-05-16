# 50-case 真实题源补全流程 v1

日期：2026-05-13

## 目标

50-case held-out 数据集必须来自真实算法竞赛题源，例如洛谷、Codeforces、AtCoder、NOI/NOIP、ICPC 区域赛等。当前草稿里的 `problem_context` 只能说明题型，不足以作为正式论文数据来源。

本流程用于把当前 50-case 草稿补成可追溯、可盲评、可公开说明的数据集。

## 题源字段

每条 case 必须补齐：

| 字段 | 说明 |
| --- | --- |
| `problem_source_platform` | 题目来源平台，例如 `luogu`、`codeforces`、`atcoder` |
| `problem_source_id` | 平台题号，例如 `P1048`、`ABCxxx_F` |
| `problem_source_url` | 原题链接，必须是 `http://` 或 `https://` |
| `problem_statement` | 本地教练盲评所需的必要题面，可以是足够完整的改写题面 |
| `problem_statement_public_summary` | 公开材料中可保留的改写摘要 |
| `problem_statement_rights_note` | 题面版权/使用边界说明 |
| `problem_statement_access_level` | `local_review_only` / `public_summary_only` / `open_license` / `original_link_only` |

## 导出补全表

从当前 draft JSONL 导出题源补全表：

```bash
python3 -m evals.aichat.export_heldout_source_completion_workbook \
  --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_ai_reference_draft_20260513.jsonl \
  --output-csv docs/research/heldout_50_source_completion_workbook_20260513.csv \
  --output-xlsx docs/research/heldout_50_source_completion_workbook_20260513.zh.xlsx
```

输出表包含每条 case 的：

- `case_id`
- `category`
- `problem_ref`
- `student_message`
- `student_message_length_bucket`
- `problem_context`
- `recent_dialogue`
- `student_code_excerpt`
- `missing_bridge`
- 需要补齐的题源字段

## 填写原则

1. 题源必须真实可访问，不能编造题号或链接。
2. 不要求所有题都来自同一平台，但主来源建议优先选择国内教练熟悉的平台，例如洛谷。
3. 题目要和 case 的算法桥梁匹配，例如 DP 状态、二分 check、树上差分、懒标记、贪心正确性等。
4. 不要为了贴合 case 而复制大段平台题面到公开材料。公开版本优先保留原题链接和改写摘要。
5. 如果本地盲评需要完整题意，可在 `problem_statement` 放必要题面，并把 `problem_statement_access_level` 标为 `local_review_only` 或 `public_summary_only`。

## 合并回 JSONL

补全 CSV 后，合并回 JSONL：

```bash
python3 -m evals.aichat.apply_heldout_source_completion \
  --input-jsonl docs/research/bridgebench_cp_heldout_v1_50_ai_reference_draft_20260513.jsonl \
  --source-csv docs/research/heldout_50_source_completion_workbook_20260513.csv \
  --output-jsonl docs/research/bridgebench_cp_heldout_v1_50_with_sources_20260513.jsonl \
  --require-complete
```

`--require-complete` 会在缺题源行或不完整行存在时失败，防止半成品进入 held-out。

## 合并后校验

```bash
python3 -m evals.aichat.validate_heldout_50_dataset \
  --dataset docs/research/bridgebench_cp_heldout_v1_50_with_sources_20260513.jsonl \
  --expected-count 50 \
  --output-json docs/research/bridgebench_cp_heldout_v1_50_with_sources_validation_report_20260513.json
```

校验必须关注：

- 题源字段是否齐全；
- URL 是否有效；
- `problem_statement_access_level` 是否为允许取值；
- `student_message_length_distribution` 是否接近 `20/15/10/5`；
- 近期对话和代码片段覆盖是否足够。

## 当前草稿状态

截至 2026-05-13，当前 50-case AI reference draft 仍缺：

- 50/50 条题源平台；
- 50/50 条平台题号；
- 50/50 条原题链接；
- 50/50 条必要题面；
- 50/50 条公开题面摘要；
- 50/50 条题面版权/使用说明；
- 50/50 条题面访问级别。

学生问题长度也偏短：当前为 `short=40`、`medium_short=10`、`medium_long=0`、`long=0`，未达到建议分布。

因此下一步不是直接让教练正式盲评，而是先完成题源补全和长度分布修正。
