# Field Usage Registry v1

Status: code-grounded snapshot for AIChat research planning.
Scope: selected bridge/focus/control fields that affect or appear near AIChat, research annotation, and evaluation.

## Runtime Control Fields

| Field | Definition | Written by | Read by | Stored in DB | Student-visible effect | Current research note |
| --- | --- | --- | --- | --- | --- | --- |
| `level_control.max_level` | Maximum allowed self-reported help level, `L1/L2/L3` | `analyze_student_turn()` | `chat()`, `build_system_prompt()`, `enforce_level_gate()` | no | yes, hard gate uses it | This is the current hard control field. |
| `level_control.bridge_redline` | Whether the current turn has bridge-leakage risk | `analyze_student_turn()` and `merge_intent_with_control()` | `build_system_prompt()`, `_infer_zpd_level()`, `map_judge_to_tutor_control()` | no | yes, prompt redline | It is a risk flag, not a typed missing-bridge diagnosis. |
| `risk_control.risk_tags` | Risk labels such as `direct_request`, `type_confirm`, `bridge_attempt` | `_detect_risks()`, `chat()` classifier branch | `build_system_prompt()`, `_select_tutor_control()`, guards | no | yes, prompt constraints | Classifier branch appends tags but does not currently lower `max_level`. |
| `risk_control.highest_risk` | Highest-priority risk label | `analyze_student_turn()`, updated by classifier branch | `build_system_prompt()` | no | yes, prompt constraints | Priority logic is rule-based. |
| `tutor_control.tutor_action` | Existing action chosen for the tutor reply | `_select_tutor_control()` or Judge v2 mapping | `build_system_prompt()`, `build_policy_override_reply()` | no | yes, controls reply style | This is the main action route for the main LLM. |
| `tutor_control.allowed_help` | Natural-language allowed-help instruction | `_select_tutor_control()` or `_judge_allowed_help_text()` | `build_system_prompt()` | no | yes, prompt constraint | Soft instruction, not the hard gate. |
| `tutor_control.forbidden` | Natural-language forbidden content list | `_select_tutor_control()` or Judge v2 mapping | `build_system_prompt()` | no | yes, prompt constraint | Current list is general; it is not generated from typed `missing_bridge`. |
| `tutor_control.learning_phase` | Current phase and recommended action metadata | `evaluate_learning_phase()` or Judge v2 mapping | `build_system_prompt()`, guards | no | yes, prompt and routing | Useful for qualitative analysis; not yet a Bridge Schema. |

## Pedagogical Judge v2 Fields

| Field | Definition | Written by | Read by | Stored in DB | Student-visible effect | Current research note |
| --- | --- | --- | --- | --- | --- | --- |
| `student_intents` | 1-3 intent labels | `pedagogical_judge_v2()` | `_validate_judge_schema()`, `map_judge_to_tutor_control()` | log file only when enabled | indirect | Pedagogical-intent signal. |
| `primary_intent` | First intent in `student_intents` | `pedagogical_judge_v2()` | `_validate_judge_schema()`, logs | log file only when enabled | indirect | Used for control metadata. |
| `phase` | Learning phase enum | `pedagogical_judge_v2()` | `_zpd_level_from_judge_help()`, `map_judge_to_tutor_control()` | log file only when enabled | indirect | Pedagogical phase, not bridge subtype. |
| `action_category` | questioning/scaffolding/diagnosis/transition/safety | `pedagogical_judge_v2()` | `_judge_allowed_help_text()`, `map_judge_to_tutor_control()` | log file only when enabled | indirect | Routes soft tutor behavior. |
| `action_subtype` | Category-specific action | `pedagogical_judge_v2()` | `_JUDGE_ACTION_TO_TUTOR_ACTION`, `_JUDGE_ACTION_TO_RECOMMENDED_ACTION` | log file only when enabled | indirect | Replaces existing `tutor_action` when v2 succeeds. |
| `allowed_help_level` | Judge v2's `L1/L2/L3` recommendation | `pedagogical_judge_v2()` | `map_judge_to_tutor_control()` | log file only when enabled | soft only | Currently does not update `level_control.max_level`. |
| `confidence` | Judge confidence, 0 to 1 | `pedagogical_judge_v2()` | validation and logs | log file only when enabled | no gating currently | No confidence-gated override exists yet. |
| `injection_detected` | Prompt-injection detection | `pedagogical_judge_v2()` | `map_judge_to_tutor_control()` | log file only when enabled | yes, adds forbidden item | Safety field, not bridge diagnosis. |

## Bridge/Focus Fields

| Field | Definition | Written by | Read by | Stored in DB | Student-visible effect | Current research note |
| --- | --- | --- | --- | --- | --- | --- |
| `bridge_family` | Research annotation family label | Teacher research annotation UI/API | Annotation export | yes, in `bridge_research_annotations` | no direct effect | Coach gold-label candidate, not runtime controller. |
| `known_focus` | Existing focus closest to a coach-labeled issue | Teacher research annotation UI/API | Annotation export | yes | no direct effect | Useful for finding coverage gaps. |
| `missing_link` | Coach-written missing step description | Teacher research annotation UI/API | Annotation export | yes | no direct effect | This is closest to the proposed `missing_bridge.description`. |
| `forbidden_completion` | What AI should not directly complete this turn | Teacher research annotation UI/API | Annotation export | yes | no direct effect | Research label; not yet injected into AIChat runtime. |
| `needs_new_focus` | Whether current focus taxonomy misses the issue | Teacher research annotation UI/API | Annotation export | yes | no direct effect | Helps taxonomy refinement. |
| `target_focus` | Understanding-check target relationship | `generate_understanding_check()` path | understanding-check judge | no | yes in check flow | Runtime focus-like field, but not AIChat Bridge Judge output. |
| `key_bridge` | Review/checkin diagnostic bridge text | Review/checkin engine paths | review UI/eval paths | yes in review/checkin records | yes in review/checkin, not AIChat main loop | Mature in review mode, not yet first-class in AIChat. |

## Existing Gap

The project already contains meaningful bridge/focus vocabulary in review, teacher, docs, and eval paths. AIChat runtime, however, does not yet have a first-class per-turn field equivalent to:

```json
{
  "missing_bridge": {
    "family": "...",
    "subtype": "...",
    "description": "...",
    "evidence": []
  },
  "forbidden_content": [],
  "leakage_risk": "low|medium|high"
}
```

That means the current paper claim should be conservative:

```text
The current implementation is pedagogical-control-aware and has bridge-related weak signals.
```

The next research implementation should aim for:

```text
The system performs explicit turn-level missing-bridge diagnosis and uses it for scaffold selection and leakage control.
```
