# Online AIChat Prompt Mode Rollout 20260512

This note records a student-facing AIChat product change deployed on 2026-05-12. The change improves day-to-day student experience and logs answer-style selection for future real-log analysis. It is not a Research v1 held-out result, and it does not mean Bridge Judge, Leakage Guard, Repair, or risk-triggered routing is active online.

## Rollout

The student AIChat UI now has an independent answer-style toggle:

| UI label | Backend value | Meaning |
|---|---|---|
| `简洁提示` | `current_system` | Default path; preserves current online AIChat behavior and remains the deployment baseline |
| `教练引导` | `enhanced_prompt_only_clean` | Adds stronger prompt-only coaching constraints to the existing `chat()` path |

The existing model-speed toggle remains independent:

| UI label | Backend value | Meaning |
|---|---|---|
| `快速` | `deepseek_flash` | Flash model configuration |
| `专业` | `deepseek_pro` | Pro model configuration |

Every online student request should therefore record both:

```text
chat_model_provider
aichat_prompt_mode
```

`教练引导` is not a new model and not a multi-judge architecture. It still uses the model selected by the student and only changes the prompt-only guidance before generating the student-visible reply.

## Not Deployed

This rollout does not enable:

- Bridge Judge;
- Runtime Bridge Contract;
- Leakage Guard;
- Repair Generator;
- post-repair second-pass guard;
- risk-triggered routing;
- full multi-judge execution on every turn.

The online `教练引导` option should be described only as a prompt-only product option, not as a full Bridge-aware Tutor.

## Deployment Verification

Deployment directory:

```text
/opt/noi-agent
```

Service:

```text
noi-agent.service
```

Post-deployment checks verified that:

- the frontend build completed successfully;
- the service restarted and remained active;
- the deployed static asset contains `回答方式`, `简洁提示`, `教练引导`, `aichat_prompt_mode`, and `enhanced_prompt_only_clean`;
- a `/chat` test request returned:
  - `prompt_mode = enhanced_prompt_only_clean`;
  - `prompt_mode_label = 教练引导`;
  - about 41.9 seconds latency on the smoke case.

The temporary verification account was removed from the online account file after testing, and the service was restarted again.

## Research Boundary

This rollout changes how future real student logs should be interpreted:

- default `简洁提示=current_system` remains usable as the deployment baseline;
- if a student selects `教练引导`, that turn should not be merged into the old `current_system` bucket;
- live logs must be stratified by `aichat_prompt_mode`;
- paper case studies using real logs must report which answer style was used;
- online logs may support development error analysis and future deployment discussion, but they must not tune the frozen 50-case held-out prompt / judge / rubric.

Safe paper wording:

> After the development-stage prompt-only baseline showed better day-to-day tutoring behavior, we exposed it as an optional online answer style for product use. This online option is logged separately and is not treated as held-out experimental evidence.

## Monitoring

Future online monitoring should track at least:

- request count and share by `aichat_prompt_mode`;
- combinations of `chat_model_provider` and `aichat_prompt_mode`;
- p50 / p95 latency;
- whether the student progresses in the next turn;
- student complaints about replies being too verbose or too weak;
- teacher-sampled critical bridge leakage;
- any complete code, complete solution, exact state definition, full recurrence, or full check-condition leakage.

These monitoring results are deployment / shadow-style evidence. They cannot replace the 50-case held-out evaluation, double coach annotation, and judge calibration.
