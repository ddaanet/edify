---
name: design
description: >-
  Triage complexity and design implementation approach: classify
  simple/moderate/complex, produce design documents for complex jobs, and
  route by whether the work needs a runbook. Triggers on /design, planning
  requests, or tasks needing complexity assessment.
allowed-tools: Agent, Read, Write, Edit, Bash, WebSearch, WebFetch, Skill
user-invocable: true
---

# Design Implementation Approach

Produce dense design documents that guide implementation by downstream agents
(sonnet executors, opus reviewers).

## Downstream Consumers

- **Planning:** `/runbook` — phases typed tdd or general. Note which phases are
  behavioural (tdd) and which are infrastructure or prose (general) to guide
  per-phase typing. Whether an item is delegated is not a phase property;
  `/build` decides that per item.
- **Execution:** `/build` when the work needs no runbook
  (`references/route-to-execution.md`, reached from both of
  `references/write-outline.md`'s sufficiency gates, from
  `references/write-design.md`'s C.5, and from Phase 0's Moderate non-prose
  route). Handles the execution lifecycle: entry gate, item walk, review gate,
  triage feedback, deliverable-review handoff.

## Process

### 0. Complexity Triage

**Requirements-clarity gate (D+B anchor):** Before any artifact reading or
triage, assess requirements completeness. Produce this assessment block (visible
output, not internal reasoning):

- **Requirements source:** [requirements.md / user request / brief.md]
- **Completeness:** [Each FR has concrete mechanism: Y/N] [Each NFR has
  measurable criterion: Y/N]
- **Routing:** [Proceed to triage / Route to `/requirements`]

Assessment rules:
- `requirements.md` exists: verify each FR/NFR has a concrete mechanism (not
  just a goal)
- User request only: verify intent is clear enough to triage (ask if not)
- Vague or mechanism-free: route to `/requirements` before proceeding

**Rationale:** Triage reads artifacts that depend on requirements being clear.
Vague requirements propagate through design into planning, producing
mechanism-free specifications downstream agents cannot implement. Structured
output anchors the routing decision in observable evidence (IEEE 29148
validation activity principle).

Before doing design work, assess whether design is actually needed.

**Artifact check:** Read plan directory (`plans/<job-name>/`) for existing
artifacts:
- `design.md` exists → Read `references/write-design.md`, skip to C.5, which
  routes by `references/route-to-execution.md`
- `outline.md` is multi-sub-problem (contains individually-scoped sub-problems
  with dependency graph and per-sub-problem readiness routing) → Read
  `references/write-outline.md`, skip to multi-sub-problem sufficiency gate
- `outline.md` sufficient (concrete approach, no open questions, explicit scope,
  low coordination complexity) → Read `references/write-outline.md`, skip to
  outline sufficiency gate
- `outline.md` insufficient → Read `references/write-outline.md`, resume from
  A.5 (revise) or A.6 (review)
- Otherwise → classify below

#### Triage Recall (D+B anchor)

Surface codified decisions that constrain classification before it happens.

`Skill(skill: "edify:recall", args: "plans/<job> — decisions that constrain triage of this task's domain")`

This invocation is the structural anchor — it prevents classification from being
skipped or rationalized. It fires whether or not anything relevant turns up,
whether or not `/requirements` already wrote the artifact.

#### Classify

**Only on the artifact check's "otherwise" branch** — a resumed `design.md` or
`outline.md` carries its own classification and skips this. Read
`references/triage.md` and work through it: the two axes and the four classes,
the work-type and artifact-destination tables, the multi-item decomposition
check that runs before classifying, and the classification block the gate writes
to `plans/<job>/classification.md`. Return here with that block filled in.

#### Routing

- **Simple, or Moderate agentic-prose** (artifact destination = `agentic-prose`)
  **→ one route.** Both produce an `outline.md` and hand it to `/build`; a
  branch that differs from another only in ceremony neither has is not a
  decision.
  1. **Recall:** from the in-context index, Read the memory and decision files
     matching the task's domain keywords.
  2. **Code reading:** Read the affected files the brief enumerates — the ones
     the work will actually change, not a summary of them — and resolve gaps
     between the brief's assumptions and actual codebase state. Where the brief
     does not enumerate them, `rg --files`/`rg` (Bash) to identify targets.
  3. **Generate** `plans/<job>/outline.md`: Read `references/write-outline.md`
     for the outline format; Read `references/design-content-rules.md`
     §Provenance Section and write the Provenance section it specifies. For
     agentic prose, record **what changes** rather than why the approach was
     chosen: the approach is not in question, so the outline's value is the
     change list. Where the outline carries a behavioural change, Read
     `../runbook/references/runbook-format.md` and write that change as an item
     in its shape — an item carrying `Slices:` carries nothing else to execute,
     and general work goes in its own item.
  4. **Proof:** Invoke `/edify:proof plans/<job>/outline.md` (outline-corrector
     dispatched by /proof on revise/kill).
  5. **Route (after /proof approval):** commit the outline, then name
     `/build plans/<job>` as the next command and stop. `/build` consumes no
     continuation, so this is a named handoff and not a tail-call.
  Skip design — all other operational rules (skills, project tooling,
  communication) remain in effect.
- **Moderate, non-prose** (all other artifact destinations) **→** ground the
  brief against the codebase, then plan and route:
  1. **Code reading:** Read affected files enumerated in the brief. Resolve gaps
     between brief assumptions and actual codebase state.
  2. **Generate** `plans/<job>/outline.md` using lightweight format (scope,
     per-file changes, dependencies, IN/OUT boundaries); Read
     `references/design-content-rules.md` §Provenance Section and write the
     Provenance section it specifies. Where the outline carries a behavioural
     change, Read `../runbook/references/runbook-format.md` and write that
     change as an item in its shape — an item carrying `Slices:` carries nothing
     else to execute, and general work goes in its own item.
  3. **Proof:** Invoke `/edify:proof plans/<job>/outline.md` (outline-corrector
     dispatched by /proof on revise/kill)
  4. **Route (after /proof approval):** Read `references/route-to-execution.md`
     and route by it. A failed precondition returns to step 2.
- **Complex →** Read `references/write-outline.md` for Phase A (research +
  outline) and Phase B (user validation + outline sufficiency gate).
- **Defect →** Route to structured-bugfix workflow: reproduce → root-cause → fix
  → verify. Skip design — the investigation structure replaces architectural
  design.

**Bundled work:** handled by §Multi-Item Decomposition in `references/triage.md`
— explicit bundling is one of its two triggers.

**Session state check:** If the session has significant pending work (>5 tasks
*— ungrounded threshold, needs calibration*), suggest `/handoff:handoff` before
proceeding.

## Author-Corrector Coupling

When a design modifies an "author" skill (a skill whose output is reviewed by a
corrector), check coupled dependencies before completing the design:

1. Identify the corrector from the transformation table (T1–T6 in
   `docs/references/pipeline-contracts.md` §D-26) — Read it; do not work from
   memory of it
2. Check: does the corrector's review criteria need corresponding update?
3. Check: does any mechanical validator need update?
4. Include corrector/validator updates in the same design scope

**Visible output (mandatory):** "Author change: X. Coupled corrector: Y. Update
needed: yes/no." This block forces awareness of coupling — designers check the
table, not silently skip it.

## Routing out

Each branch above stops there, naming its own next command or taking the
terminal action `references/route-to-execution.md` names. There is no tail-call:
`/design` states the command, the user or the session runs it.

- Simple, Moderate agentic-prose → `/build plans/<job>`
- Routed to `/build` by `references/route-to-execution.md` — reached from both
  of `references/write-outline.md`'s sufficiency gates, from
  `references/write-design.md`'s C.5, and from Phase 0's Moderate non-prose
  route → `/build plans/<job>`
- Routed to `/runbook` by that node → commit the artifact and stop; no next
  command
