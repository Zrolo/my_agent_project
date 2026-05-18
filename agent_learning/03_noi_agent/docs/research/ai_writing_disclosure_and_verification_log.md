# AI Writing Disclosure and Verification Log

## Scope

This log records how generative AI assistance may be used during manuscript preparation. It adds no experiments, changes no data, and does not change the evidence package.

## Allowed AI Assistance

Generative AI tools may be used for:

- drafting assistance;
- editing and language polishing;
- checklist generation;
- evidence organization;
- formatting support;
- consistency scans for forbidden wording.

Generative AI tools must not be treated as a source of scientific evidence. AI-generated text is not accepted into the manuscript until a human author verifies the underlying claim, number, citation, and interpretation.

## Human Verification Requirements

Human authors must manually verify:

- all scientific claims;
- all experimental results;
- all citations and bibliographic metadata;
- all tables and figures;
- all interpretations of human-review, stress-test, sensitivity, and calibration evidence;
- all claims involving Guard-only, Repair, DBox+Repair, priority60 adjudication, all-50 sensitivity, and LLM graders.

AI is not listed as an author. Human authors take full responsibility for the content.

## Suggested Manuscript Disclosure

```text
We used generative AI tools to assist with drafting, editing, and checklist generation. All scientific claims, experimental results, citations, tables, and interpretations were manually verified by the authors, who take full responsibility for the content.
```

## Verification Logs

Use these companion files during manuscript preparation:

- `citation_verification_log.csv`
- `result_number_verification_log.csv`
- `manuscript_human_revision_checklist.md`

No citation should be marked submission-ready until `manually_opened_yes_no` and `quote_or_paraphrase_checked_yes_no` are both `yes`.
