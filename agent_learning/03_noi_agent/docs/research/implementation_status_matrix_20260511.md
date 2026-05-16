# Implementation Status Matrix

Date: 2026-05-11; updated 2026-05-12

This document separates current online behavior, offline research tooling, shadow/proposed designs, and not-yet-implemented plans. Paper drafts and external reviews should not mix these states.

## Status Labels

| Status | Meaning |
|---|---|
| `online_active` | Active in the student-facing online AIChat path |
| `offline_eval_only` | Used only in offline research runners, reports, workbooks, or smoke evals |
| `teacher_tool_only` | Used only by teacher/research tools; does not affect student responses |
| `shadow_or_proposed` | Designed or proposed, but does not change student-visible replies |
| `not_implemented` | Not implemented |
| `doc_only` | Documented only as a boundary or plan |

## Online AIChat Baseline

| Module / Behavior | Status | Evidence / Notes | Paper Wording |
|---|---|---|---|
| `chat()` main online path | `online_active` | Student AIChat still enters through the existing `chat()` path | Can be used as the `current_system` baseline |
| rules / `analyze_student_turn()` | `online_active` | Used for fast risk and tutor-control signals | Can be described as part of the baseline path |
| legacy learning phase judge | `online_active` | Recorded in the current-flow document | Baseline path only, not a new contribution |
| Pedagogical Judge v2 soft control | `online_active` | Mainly affects `tutor_control`; does not update a hard Bridge controller | Do not claim it is already a hard bridge controller |
| model self-reported `[LEVEL:Lx]` hard gate | `online_active` | Current hard gate depends on model self-report | Can be described as a baseline limitation |
| online answer-style toggle | `online_active` | Deployed on 2026-05-12; default `简洁提示=current_system`, optional `教练引导=enhanced_prompt_only_clean`; changes prompt-only guidance only and does not enable Bridge Judge / Guard / Repair | Product UX change and log stratification field; not held-out experimental evidence |
| `aichat_prompt_mode` request / response field | `online_active` | Online requests and responses record answer style; future real logs must be stratified by this field | Paper case studies using online logs must report prompt mode |
| content-level independent leakage judge in online chat | `not_implemented` | Research v1 has an offline Leakage Judge, but it is not active online | Do not claim online independent leakage detection |
| online full multi-judge every turn | `not_implemented` | Scope lock excludes this as the default online strategy | Do not claim it is deployed |

## Offline Research Harness

| Module / Behavior | Status | Evidence / Notes | Paper Wording |
|---|---|---|---|
| Bridge Judge / compact diagnoser | `offline_eval_only` | Used for seed diagnosis, contract generation, and smoke evals | Offline system variant |
| Runtime bridge contract schema | `offline_eval_only` | `runtime_bridge_contract_schema_v1.json` | Compact control signal in the research harness |
| Bridge Contract Tutor | `offline_eval_only` | Runner supports Bridge Contract modes | Ablation condition |
| Leakage Judge / Guard | `offline_eval_only` | Offline detection over candidate/final responses | Guard ablation; requires calibration |
| Repair Generator | `offline_eval_only` | Offline repair; natural mini-study may not trigger it; 20-case repair stress and 20-pair before/after blind review analysis exist | Pilot evidence only; final effect needs held-out natural samples and judge calibration |
| Response blind review workbook | `teacher_tool_only` | Teacher-side Excel/workbook review flow | Coach review workflow |
| Repair before/after review | `teacher_tool_only` | All20 Repair stress has 20 complete before/after pairs; repaired response wins 14, ties 3, loses 3; leakage improves 19, ties 1 | Repair stress pilot, not final held-out conclusion |
| bilingual reports | `offline_eval_only` | Chinese is coach-facing; English is for external collaboration; bilingual policy and validator exist | Research collaboration norm |
| bilingual docs validator | `offline_eval_only` | `validate_research_bilingual_docs.py` allows 23 legacy debt files by default but fails new single-language Markdown docs | Documentation governance tool |
| static lint dev gate | `offline_eval_only` | Summary emits `dev_gate`; answer-slot / filled-trace / worked-example risks trigger `review_required` | Development-stage screening signal, not coach gold |

## Proposed / Shadow / Future

| Module / Behavior | Status | Evidence / Notes | Paper Wording |
|---|---|---|---|
| shadow mode for real AIChat logs | `shadow_or_proposed` | Direction is defined, but it does not actively control student-visible replies | Future deployment path only |
| risk-triggered active mode | `shadow_or_proposed` | Routing policy and control harness policy exist | Deployment simulation, not deployed system |
| deterministic safe response for direct code/solution request | `shadow_or_proposed` | Should be promoted first in design, but current online behavior must be confirmed | Active-mode promotion plan |
| automatic prompt patch after repair | `not_implemented` | Explicitly forbidden; slow variables update offline | Do not implement or claim |
| long-term student memory layer | `not_implemented` | Excluded from Research v1 by scope lock | Future work |
| complete NOI/OI algorithm ontology | `not_implemented` | Research v1 only needs stratified coverage | Future work |

## Dataset / Evaluation Status

| Artifact | Status | Notes |
|---|---|---|
| 20 old seeds | `offline_eval_only` | Used for pilot, prompt tuning, and regression; not a formal held-out test |
| 50 held-out test set | `offline_eval_only` | `bridgebench_cp_heldout_v1_50_draft.jsonl` and a dataset card now exist; validation passes row count, required fields, and dev-seed ID overlap checks | Wording must remain draft held-out; still needs Coach A review, Coach B double annotation, and freeze |
| partial double annotation | `not_implemented` | Coach B should independently label at least 20 cases |
| adjudicated reference | `not_implemented` | Required before headline metrics |
| LLM Judge calibration protocol | `doc_only` | Protocol exists first; report comes later |
| repair stress set | `offline_eval_only` | `repair_stress_cases_v1.jsonl` has 20 cases; all20 automatic stress run, 40-row before/after workbook, and 20-pair analysis exist | Add `repair_stress_004` and other failures to regression; final conclusion still needs held-out natural samples |
| pass^3 stability eval | `not_implemented` | For online reliability discussion |
| bilingual documentation debt | `doc_only` | 129 research Markdown files; new docs have no unpaired violation; 23 historical unpaired docs are tracked as legacy debt | Backfill gradually; does not block Research v1 |

## Paper Claim Boundary

### Can Say

- Current online AIChat is the `current_system` baseline.
- The online student UI has an optional `教练引导=enhanced_prompt_only_clean` answer style; the default remains `简洁提示=current_system`.
- The research branch has an offline evaluation harness.
- Bridge Contract, Guard, Repair, static lint, and dev gate are offline ablation/evaluation tools.
- Mini-studies and stress tests are pilot evidence, not final submission-grade results.

### Cannot Say

- Current online AIChat is fully Bridge-aware.
- `教练引导` proves the Research v1 method works.
- Repair is already modifying student-facing online replies.
- Leakage Judge already blocks all online leakage.
- Risk-triggered routing is mature and deployed.
- The 20-case pilot proves final effectiveness.
