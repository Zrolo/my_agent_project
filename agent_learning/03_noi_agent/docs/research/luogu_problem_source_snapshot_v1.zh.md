# 洛谷题源快照记录 v1

本文档记录 Research v1 使用的本地洛谷题库快照。该快照用于生成真实题源驱动的 held-out v2 草稿，不提交到 GitHub。

## 快照信息

- 本地路径：`data/local_problem_banks/luogu_latest_20260402.ndjson`
- 原始本地来源：`/Users/kongyouli/Downloads/latest.ndjson`
- 记录日期：2026-05-13
- 行数：15,909
- SHA-256：`d0acee875bf0445936e616efc00f9044797384fb9a13648d072bb8e2744902e1`
- 是否进入 Git：否，已由 `.gitignore` 排除。

## 使用边界

- 该快照只作为本地研究数据源，用于筛选洛谷真实题目并生成 synthetic-but-grounded 学生问题。
- 原始题库文件体积约 139MB，不进入公开仓库。
- 生成的公开研究材料应优先保留题号、洛谷链接和改写摘要；完整题面或较长题面摘录仅用于本地教练复核。
- v2 样本的学生问题不是旧线上系统 AI 回复，也不声称是真实学生原话，而是基于真实题面和目标 bridge 标签合成。

## 下游产物

- `docs/research/bridgebench_cp_heldout_v2_50_draft.jsonl`
- `docs/research/heldout_v2_50_source_and_case_review.zh.xlsx`
- `docs/research/bridgebench_cp_heldout_v2_50_generation_report_20260513.zh.md`

这些产物仍是 draft，需要教练复核后才能进入 Coach A/B 标注、agreement 和 adjudication 流程。
