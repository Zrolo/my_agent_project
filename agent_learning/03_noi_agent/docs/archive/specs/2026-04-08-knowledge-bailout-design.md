# Knowledge Bailout Design

## Summary

When a student still fails after:

- main quiz
- follow-up quiz
- remedy / bottom-out
- final micro confirm

the system should not immediately stop at teacher follow-up.

Instead, v1 adds one **knowledge bailout** step:

- stay on the same review detail page
- show a prebuilt knowledge card
- explain the current bridge in middle-school-friendly language
- add a very short algorithm overview
- then give exactly one `knowledge_confirm` question
- after that, always stop

This is not a fourth normal quiz round. It is a different scaffold type used only after the three-round ladder is exhausted.

## Product Decisions

- Student-first priority: get a usable bailout path online quickly.
- V1 uses **prebuilt knowledge cards**, not OI Wiki retrieval.
- V1 keeps the student on the current detail page.
- V1 stores bailout outcome in existing learning-flow artifacts where possible.
- V1 adds a short `productive failure` opening to reduce shame and keep motivation.

## Behavior

### Trigger

Trigger knowledge bailout only when:

- the student fails `final_micro_confirm`

Do not trigger earlier.

### Student Flow

1. Student fails final micro confirm.
2. System switches to `knowledge_bailout`.
3. Detail page keeps all earlier quiz history visible.
4. Under the history stack, show a new knowledge bailout block:
   - opening
   - bridge explanation
   - optional visual hint
   - short algorithm overview
   - one knowledge confirm question
5. If knowledge confirm is correct:
   - `mastery_status = assisted_success`
6. If knowledge confirm is incorrect:
   - `mastery_status = not_mastered`
   - `learning_status = needs_teacher_followup`

### Teacher Visibility

Teacher should be able to tell:

- the student entered knowledge bailout
- whether the student passed after the knowledge card
- whether the student still needed teacher follow-up

V1 should encode this through:

- `bridge_path`
- quiz history
- teacher sample text

## Knowledge Card Shape

Each card is prebuilt and tied to a bridge-level concept.

V1 card fields:

- `card_id`
- `opening`
- `bridge_explanation`
- `visual_hint`
- `algorithm_overview`
- `micro_action`

V1 priority cards:

- `dp.state_design`
- `dp.transition_design`
- `binary_search.check_condition`
- `greedy.greedy_basis`
- `string.trie.shared_prefix_merging`
- `graph.tree_diameter.tree_diameter_candidates`
- `modeling.scale_estimation`
- `modeling.method_selection`

## Interface Decisions

### Backend

- Add one new learning state:
  - `knowledge_bailout`
- Add one new quiz role:
  - `knowledge_confirm`
- Store card identity and card content in the created `knowledge_confirm` quiz `meta`, so detail refresh can reconstruct the knowledge block without adding a new table.

### Frontend

- Reuse the existing review detail quiz timeline.
- Show knowledge bailout as a new step below old quiz history.
- Do not hide earlier rounds.
- The knowledge confirm question should render like a normal quiz card, but with a distinct title/lead.

### Outcome Encoding

Use new bridge paths:

- `knowledge_bailout_success`
- `knowledge_bailout_failed`

These must feed:

- mastery display
- teacher badges/notes
- detail summary

## Constraints

- Only one knowledge bailout per review.
- Only one knowledge confirm question after the card.
- No recursive follow-up after knowledge confirm.
- No page jump.
- No OI Wiki retrieval in v1.
