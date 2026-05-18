# Research v1 Bilingual Documentation Policy

## Purpose

Starting on 2026-05-12, new Research v1 Markdown documents should be kept in bilingual pairs:

```text
English: *.md
Chinese: *.zh.md
```

The Chinese document is the primary reading surface for coaches and internal project discussion. The English document is the companion artifact for external AI review, paper collaboration, and submission writing.

## Scope

This policy applies to new Markdown research documents under `docs/research/`, including:

- experiment reports;
- blind-review analyses;
- prompt / judge / repair patch notes;
- baseline, scope, methodology, and policy documents;
- calibration, error-analysis, and dev-gate documents.

Excel, CSV, JSONL, JSON registries, images, and temporary ad hoc outputs do not need bilingual pairs. Auto-generated offline summaries should emit both English `*.md` and Chinese `*.zh.md` Markdown reports when they are meant for review.

## Legacy Debt

The current repository still contains historical Markdown documents that only exist in one language. They are tracked as legacy debt. They should not block ongoing work, but the debt should not grow.

Going forward:

```text
New documents must be paired.
Old documents should be backfilled gradually.
Do not add single-language research reports for convenience.
```

## Validation Command

Run:

```bash
python3 -m evals.aichat.validate_research_bilingual_docs \
  --root docs/research \
  --output-json docs/research/bilingual_docs_validation_report.json
```

By default, the validator allows the current known legacy unpaired documents, but fails on newly added single-language Markdown documents.

To inspect all unpaired documents, including legacy debt, run:

```bash
python3 -m evals.aichat.validate_research_bilingual_docs \
  --root docs/research \
  --output-json docs/research/bilingual_docs_validation_report.strict.json \
  --no-default-legacy-allowlist
```

## Writing Rules

- Chinese files use `.zh.md`.
- English files use plain `.md`.
- The two versions do not need to be literal translations, but they must preserve the same conclusion, experimental boundary, main metrics, and limitations.
- If one version is drafted first, the companion version can follow shortly, but the work should not be treated as complete before both exist.
- Paper-facing claims, experimental numbers, and risk caveats must match across both versions.
