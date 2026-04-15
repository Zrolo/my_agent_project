# NOI Agent UI Redesign (Inspired by UI/UX Pro Max)

## 1. Background

Current product capability is already strong:

- student workspace has AI chat, check-in review, history, self-check, and family-aware review rendering
- teacher workspace has stats, manual review, observability, and drill-down
- routing and review quality are now good enough for real student trial

Current UI issue is no longer "missing function", but "mixed visual language":

- early generic form/dashboard styling and later refined sections coexist in the same page
- student and teacher areas are both usable, but they do not yet feel like one intentional product
- review output is family-aware in logic, but not yet distinct enough in visual tone
- teacher analytics is functional, but still reads more like an internal tool than a coaching cockpit

This redesign uses the design reasoning style from the `ui-ux-pro-max-skill` repository:

- choose one clear visual direction instead of stacking random modern UI tricks
- design from product intent, not from generic dashboard templates
- define palette, type, hierarchy, layout rhythm, motion, and anti-patterns up front
- preserve the strongest workflows and change presentation, structure, and emphasis before changing logic

## 2. Product Truth

This product is not a generic chat app and not a generic admin panel.

It is a dual-surface learning product:

1. student side: "coaching workspace"
2. teacher side: "diagnostic control room"

The UI should communicate:

- precision over decoration
- coaching over chat
- diagnosis over vague encouragement
- visible progress over feature clutter

## 3. Design Goals

### Primary goals

- make the student area feel like one guided learning workspace
- make failure-diagnosis and success-reflection feel visibly different
- make teacher analytics feel evidence-first and scannable
- reduce the "tool pile" feeling created by many tabs and panels

### Non-goals

- do not split the app into two separate sites
- do not redesign routing logic or review content generation
- do not add new teaching features in this pass
- do not introduce a heavy component framework rewrite

## 4. Direction Options Considered

### Option A: Generic SaaS Dashboard Polish

Characteristics:

- cleaner cards
- softer shadows
- more spacing
- slightly better tabs

Why not chosen:

- too safe
- does not express "teaching workspace"
- would still feel interchangeable with any admin product

### Option B: Editorial Learning Studio

Characteristics:

- warm paper-like surfaces
- strong typography hierarchy
- asymmetric but disciplined layout
- visible distinction between thinking, diagnosis, and action

Why chosen:

- best fit for a coaching product
- supports long-form review content
- makes student work feel serious without becoming dull

### Option C: Futuristic AI Lab

Characteristics:

- dark glassmorphism
- neon accents
- high-contrast "AI console" feeling

Why not chosen:

- mismatches middle-school / olympiad coaching tone
- hurts dense reading tasks
- increases novelty more than clarity

## 5. Chosen Direction

### Design theme

**Editorial Learning Studio with Diagnostic Dashboard accents**

Student side should feel like:

- a disciplined study desk
- a coach's annotated workbook
- a place to think through one problem carefully

Teacher side should feel like:

- a review desk with evidence markers
- an intervention dashboard
- a place to spot weak patterns quickly

## 6. Visual System

### 6.1 Color system

Base mood:

- parchment white instead of flat white
- deep navy instead of black
- bright cobalt for active intelligence
- amber for guidance / warning / teacher evidence
- muted green only for confirmed progress, not as the whole brand

Suggested tokens:

- `--bg-page`: `#f4f1ea`
- `--bg-panel`: `#fffdf8`
- `--bg-panel-strong`: `#f8f4eb`
- `--ink-strong`: `#172033`
- `--ink-main`: `#2a3550`
- `--ink-soft`: `#65708a`
- `--brand-primary`: `#2457d6`
- `--brand-primary-strong`: `#173ea0`
- `--brand-amber`: `#d28b1f`
- `--brand-amber-soft`: `#fff1d6`
- `--brand-success`: `#2e7d5b`
- `--line-soft`: `rgba(23, 32, 51, 0.10)`
- `--line-strong`: `rgba(23, 32, 51, 0.18)`

### 6.2 Typography

Need a more intentional stack than default system sans.

Recommended direction:

- UI/body: `Noto Sans SC`
- section headlines / review stage titles: `Noto Serif SC`
- small labels / pills remain sans

Reason:

- Chinese readability remains strong
- serif headlines create a coaching/editorial character
- student review output gains importance and rhythm

### 6.3 Shape language

- large radii stay, but become more consistent
- cards should feel like "sheets" and "modules", not floating bubbles everywhere
- panels use 20-24px radii
- pills and chips use 999px only where status meaning matters

### 6.4 Shadows and borders

- reduce generic soft SaaS blur
- rely more on layered borders and material contrast
- use one strong ambient shadow family, not many unrelated shadow recipes

### 6.5 Motion

Use only meaningful motion:

- tab/page section fade-slide on switch
- review stage reveal stagger
- drill-down highlight transition in teacher stats

Avoid:

- button bouncing
- glass shimmer
- endless pulse animations

## 7. IA and Layout Changes

## 7.1 Global shell

- keep one app shell
- make header less like a demo container and more like a product masthead
- increase max width from the current narrow demo-style container to a true workspace layout
- use a wider grid for both student and teacher surfaces

### 7.2 Login screen

Current state:

- functional but visually generic

New state:

- split hero login
- left: product promise, learning outcomes, demo account hints
- right: login card
- subtle "coach notebook" background texture

### 7.3 Student area

Student side should become a clear three-state system:

1. ask
2. check in
3. review and confirm

Without changing actual tabs, the UI should emphasize this progression.

Changes:

- stronger shell header with progress framing
- more intentional hero in AI chat
- check-in sidebar feels like a submission workbook
- review area feels like a live coaching board, not another card stack

### 7.4 Review family distinction

This is the most important visual change.

#### Failure diagnosis

Tone:

- practical
- corrective
- action-first

Display order:

- `main_block`
- `key_bridge`
- `next_step`
- `transfer_signal`

Visual treatment:

- subtle amber/cobalt accents
- stronger emphasis on "next action"
- evidence chips and issue framing

#### Success reflection

Tone:

- explanatory
- confidence-building
- transfer-first

Display order:

- `main_block`
- `key_bridge`
- `transfer_signal`
- `next_step`

Visual treatment:

- calmer blue/green accents
- stronger emphasis on "why this works"
- transfer signal displayed as a highlighted teaching takeaway

### 7.5 History tab

Current issue:

- cards are useful but still feel like logs

New direction:

- turn them into study records
- clearer metadata rhythm
- stronger stage labels
- better visual hierarchy between title, state, and extracted review points

### 7.6 Teacher area

Teacher area should feel less like "admin forms" and more like an intervention cockpit.

Changes:

- stats surface becomes a newsroom-style metric wall
- manual review list becomes a stack of evidence dossiers
- mode/family drill-down should visually feel like narrowing a lens

## 8. Component-Level Redesign Targets

### Student

- top masthead
- student tab rail
- AI chat hero
- check-in form groups
- review stage header
- review block cards
- history study cards
- self-check / confirm / remedy controls

### Teacher

- teacher navigation rail/tabs
- stats cards
- manual review cards
- filter banner
- breakdown drill-down cards

## 9. Anti-Patterns to Avoid

- no purple-on-white AI default aesthetic
- no full dark mode pivot in this pass
- no random glassmorphism on educational content
- no excessive gradient backgrounds behind long reading blocks
- no multiple unrelated card styles on one page
- no hiding dense educational content behind too many accordions

## 10. Implementation Strategy

### Phase 1: design tokens and shell cleanup

- consolidate CSS variables
- unify page background, panel surfaces, borders, shadows, type scale
- widen overall workspace

### Phase 2: student workspace redesign

- login
- student shell
- chat hero
- check-in sidebar
- review stage surfaces

### Phase 3: family-aware review polish

- visual distinction between `failure_diagnosis` and `success_reflection`
- family-specific subtitles, chips, block emphasis, ordering polish

### Phase 4: teacher dashboard redesign

- stats hierarchy
- manual review cards
- drill-down affordances

### Phase 5: responsive and motion pass

- tablet/mobile cleanup
- small transitions
- spacing consistency

## 11. Scope Boundaries for This Pass

This redesign should be:

- mostly HTML/CSS + light JS rendering adjustments
- no major data contract changes
- no backend prompt changes
- no rewrite of student workflow logic

## 12. Acceptance Criteria

The redesign is successful if:

- student side feels like one coherent learning workspace
- failure vs success review families are visually distinguishable in under 3 seconds
- teacher side can scan stats and review evidence faster than before
- page still works on desktop and mobile
- existing tests still pass or are updated only for intentional UI structure changes

## 13. Recommended Next Step

Start implementation with:

1. design token cleanup in `static/style.css`
2. shell and student header restructuring in `static/index.html`
3. family-aware review surface polish in `static/app.js` + CSS

Teacher redesign should come immediately after student shell is stable, not before.
