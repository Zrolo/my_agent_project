# Open Bridge Observability Design

## Goal

Add an `open_bridge / candidate_bridge` observation layer so unknown or ambiguous bridge cases can be tracked after launch without letting unproven bridge IDs drive student-facing quiz, knowledge card, or remedy behavior.

## Product Rule

The system keeps one stable execution route:

- `stable_focus` drives existing review guard, quiz, knowledge card, and remedy behavior.
- `candidate_bridge_id` records a possible more specific bridge under a stable parent.
- `open_bridge_label` records a human-readable unknown bridge when the system cannot confidently map it.

P0 is intentionally conservative: candidate/open bridge metadata is visible for teacher review and audit, but does not change student behavior.

## Data Shape

Each completed review may carry `bridge_route_meta`:

```json
{
  "status": "known_bridge",
  "stable_focus": "tree_path_difference",
  "card_id": "graph.tree_path_difference",
  "route_confidence": "high",
  "focus_source": "source_rule",
  "matched_signals": ["树上路径", "LCA", "差分"],
  "conflict_signals": ["标记 also matches lazy_semantics"],
  "suppressed_candidates": ["lazy_semantics"],
  "candidate_bridge_id": "tree_path_difference.edge_variant",
  "candidate_parent_focus": "tree_path_difference",
  "candidate_confidence": "medium",
  "open_bridge_label": "树上边贡献差分",
  "open_bridge_reason": "Current problem asks edge pass counts; stable bridge is still point-oriented."
}
```

## P0 Scope

- Add a resolver that wraps the current `_detect_quiz_focus(...)`.
- Persist `bridge_route_meta` on `reviews`.
- Return metadata in review detail and teacher review samples.
- Show teacher-facing route metadata in the review page.
- Add tests for known, candidate, open, and conflict cases.

## Non-Goals

- Do not auto-create bridge IDs.
- Do not let LLM-created candidate IDs drive deterministic quiz/card/remedy.
- Do not change student-facing routing.
- Do not add a full candidate bridge management dashboard.

## Promotion Rule

A candidate bridge may become a formal bridge only after it has enough real samples, teacher approval, student-success evidence, anti-signal tests, and deterministic assets.
