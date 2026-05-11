# DBox Official Materials Review v1

This note records the offline inspection of the official DBox supplementary package `pn2271.zip`. Its purpose is to anchor our DBox-inspired baseline in the official materials without claiming a DBox reproduction.

## Package Contents

The package contains:

- `Prompts.pdf`
- `ReadMe.txt`
- backend source code: `Source Code/Back End/server.py`
- frontend source code: `Source Code/Front End/UserStudy.html`, `UserStudy_logical.js`, `DBox_try.html`, and related assets

The `ReadMe.txt` describes a Flask backend and a frontend HTML interface communicating through HTTP.

## Confirmed DBox Mechanisms

The prompts and source code show four main interactions:

| Function | Input | Role |
|---|---|---|
| From Editor to Step Tree | problem + learner code | Generate a step tree and label node statuses |
| Check Step Tree | problem + learner step tree | Check learner steps, add missing nodes, and generate hints |
| Copy to Comments | problem + learner code + learner steps | Map step-tree nodes to code lines |
| Check Match | problem + learner code + learner steps | Classify nodes as implemented, incorrectly implemented, or still to be coded |

This confirms that DBox is an interactive step-tree and code-step alignment system, not a single-turn tutor response prompt.

## Node And Hint Fields

The official prompts use node-status concepts including:

- `correct`
- `incorrect`
- `missing`
- `can / cannot be further divided`

They also generate fields such as:

- `general_hint`
- `detailed_hint`
- `correctStep`
- `code`
- `correct_code`
- `psuedo_code` / pseudocode

For our single-turn benchmark, `general_hint` is the safest first-level hint signal to adapt. `detailed_hint`, `correctStep`, `correct_code`, and pseudocode are disabled because they can directly complete the current critical bridge.

## Implications For Research v1

We retain:

- step-tree-style decomposition;
- current-substep localization;
- the spirit of correct / incorrect / missing / divisible node statuses;
- question-form `general_hint`;
- supportive guidance for the current missing or incorrect node.

We do not retain:

- the interactive step-tree UI;
- multi-turn co-decomposition;
- repeated failed attempts;
- reveal substep;
- reveal code;
- detailed hints;
- correctStep;
- correct_code;
- pseudocode;
- code-line mapping;
- real-student learning-gain, engagement, or critical-thinking studies.

## Runner Mapping

Research v1 uses:

```text
tutor_mode=dbox_inspired_decomposition_tutor
```

The runner emits:

```json
{
  "baseline_group": "literature_inspired_decomposition",
  "decomposition_view": [
    {"step_id": "s1", "step_name": "...", "status": "known_or_not_relevant"},
    {"step_id": "s2", "step_name": "...", "status": "current_stuck_step"},
    {"step_id": "s3", "step_name": "...", "status": "defer"}
  ],
  "current_substep": "...",
  "hint_level": "general_question",
  "student_visible_response": "..."
}
```

The compact status mapping is:

| DBox concept | Research v1 mapping |
|---|---|
| correct / already useful part | `known_or_not_relevant` |
| incorrect / missing / divisible current stuck point | `current_stuck_step` |
| later unaddressed work | `defer` |

## Paper Wording

Acceptable:

```text
We consulted the official DBox supplementary materials and implemented a single-turn DBox-inspired decomposition baseline.
```

Avoid:

```text
We reproduce DBox.
```

Recommended:

```text
We adapt DBox's step-tree, node-status, and general-hint principles to a single-turn DBox-inspired baseline, without reproducing its interactive UI, multi-turn co-decomposition, progressive reveal, code-step alignment, or real-student study.
```

## Source Anchors

- Local official package: `/Users/kongyouli/Downloads/pn2271.zip`
- Extracted read-only review copy: `/tmp/dbox_pn2271/SupplementaryMaterials`
- DBox paper anchor: [ar5iv](https://ar5iv.org/html/2502.19133v1)
- DBox ACM anchor: [ACM DL](https://dl.acm.org/doi/abs/10.1145/3706598.3713748)
