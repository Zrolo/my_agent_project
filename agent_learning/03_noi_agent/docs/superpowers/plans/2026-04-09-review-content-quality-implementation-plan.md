# Review Content Quality Implementation Plan

> Goal: tighten `review_engine` wording and prebuilt knowledge bailout cards so the student-facing content feels more like a small teachable lesson and less like a system explanation.

## Scope

- Prompt wording only
- Prebuilt knowledge cards only
- Existing knowledge confirm quiz wording only

No new routes, UI systems, APIs, or database changes.

## Steps

- [ ] Add focused tests for:
  - more student-friendly prompt language
  - more concrete method-selection / scale-estimation / trie / tree-diameter cards
  - more concrete knowledge confirm wording where needed

- [ ] Update `review_engine.py`:
  - tighten review / remedy / bottom-out prompt wording
  - improve selected knowledge bailout cards
  - improve selected knowledge confirm prompts

- [ ] Run focused tests:
  - `python3 -m unittest -v test_review_engine_messages_unit.py`

- [ ] Run full regression:
  - `bash run_test.sh`
