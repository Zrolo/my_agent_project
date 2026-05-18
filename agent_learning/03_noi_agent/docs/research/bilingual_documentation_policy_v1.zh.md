# Research v1 双语文档规范

## 目的

从 2026-05-12 起，Research v1 中新增的研究文档应保持中英文成对：

```text
英文：*.md
中文：*.zh.md
```

中文文档是教练和项目内部讨论的主读面；英文文档是外部 AI 审查、论文协作和投稿写作的伴随材料。

## 适用范围

本规范适用于 `docs/research/` 下新增的 Markdown 研究文档，包括：

- 实验报告；
- 盲评分析；
- prompt / judge / repair patch 说明；
- baseline、scope、methodology、policy 文档；
- calibration、error analysis、dev gate 文档。

不要求 Excel、CSV、JSONL、JSON registry、图片或临时 ad hoc 输出都中英文成对。自动生成的 offline summary 如果是 Markdown 报告，应同时输出英文 `*.md` 和中文 `*.zh.md`。

## 历史债务

当前仓库里有一批历史 Markdown 文档只有一种语言版本。它们被记录为 legacy debt，不阻止后续开发，但不应继续扩大。

后续原则：

```text
新文档必须成对；
旧文档逐步补齐；
不要为了赶进度新增单语研究报告。
```

## 校验命令

运行：

```bash
python3 -m evals.aichat.validate_research_bilingual_docs \
  --root docs/research \
  --output-json docs/research/bilingual_docs_validation_report.json
```

默认情况下，validator 会允许当前已知 legacy unpaired 文档，但会拦截新增的单语 Markdown 文档。

如果需要查看所有未配对文档，包括历史债务，可以运行：

```bash
python3 -m evals.aichat.validate_research_bilingual_docs \
  --root docs/research \
  --output-json docs/research/bilingual_docs_validation_report.strict.json \
  --no-default-legacy-allowlist
```

## 写作约定

- 中文版文件名使用 `.zh.md`。
- 英文版文件名使用普通 `.md`。
- 两个版本不需要逐字直译，但必须表达同一结论、同一实验边界、同一主要指标和同一限制。
- 如果某个版本先完成，另一个版本可以稍后补，但不能进入提交/推送前的完成状态。
- 论文相关结论、实验数字、风险 caveat 必须两个版本一致。
