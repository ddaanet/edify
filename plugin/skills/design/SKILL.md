---
name: design
description: >-
  Triage complexity and design implementation approach. Triggers on /design,
  architecture or implementation planning requests, or tasks needing
  complexity assessment. Triages simple/moderate/complex, produces design
  documents for complex jobs, routes moderate to /runbook.
allowed-tools: Agent, Read, Write, Bash, WebSearch, WebFetch, Skill
user-invocable: true
---

# Design Implementation Approach

Produce dense design documents that guide implementation by downstream agents (sonnet executors, opus reviewers).

## Downstream Consumers

- **Planning:** `/runbook` — phases typed tdd or general. Note which phases are behavioural (tdd) and which are infrastructure or prose (general) to guide per-phase typing. Whether an item is delegated is not a phase property; `/build` decides that per item.
- **Execution:** `/build` when the work needs no runbook (`references/route-to-execution.md`, reached from the Phase B sufficiency gate and from Phase C.5). Handles the execution lifecycle: entry gate, item walk, review gate, triage feedback, deliverable-review handoff.

## Process

### 0. Complexity Triage

**Requirements-clarity gate (D+B anchor):** Before any artifact reading or triage, assess requirements completeness. Produce this assessment block (visible output, not internal reasoning):

- **Requirements source:** [requirements.md / user request / brief.md]
- **Completeness:** [Each FR has concrete mechanism: Y/N] [Each NFR has measurable criterion: Y/N]
- **Routing:** [Proceed to triage / Route to `/requirements`]

Assessment rules:
- `requirements.md` exists: verify each FR/NFR has a concrete mechanism (not just a goal)
- User request only: verify intent is clear enough to triage (ask if not)
- Vague or mechanism-free: route to `/requirements` before proceeding

**Rationale:** Triage reads artifacts that depend on requirements being clear. Vague requirements propagate through design into planning, producing mechanism-free specifications downstream agents cannot implement. Structured output anchors the routing decision in observable evidence (IEEE 29148 validation activity principle).

Before doing design work, assess whether design is actually needed.

**Artifact check:** Read plan directory (`plans/<job-name>/`) for existing artifacts:
- `design.md` exists → route to `/runbook`
- `outline.md` is multi-sub-problem (contains individually-scoped sub-problems with dependency graph and per-sub-problem readiness routing) → Read `references/write-outline.md`, skip to multi-sub-problem sufficiency gate
- `outline.md` sufficient (concrete approach, no open questions, explicit scope, low coordination complexity) → Read `references/write-outline.md`, skip to outline sufficiency gate
- `outline.md` insufficient → Read `references/write-outline.md`, resume from A.5 (revise) or A.6 (review)
- Otherwise → classify below

#### Triage Recall (D+B anchor)

Surface codified decisions that constrain classification before it happens.

`Skill(skill: "edify:recall", args: "plans/<job> — decisions that constrain triage of this task's domain")`

This invocation is the structural anchor — it prevents classification from being skipped or rationalized. It fires whether or not anything relevant turns up, whether or not `/requirements` already wrote the artifact.

#### Classification Criteria

Assess two axes (Stacey Matrix-grounded), then classify. Classify only — do not route yet.

**Axes:**
1. **Implementation certainty** — is the approach known? Prior art in codebase? Known technique?
2. **Requirement stability** — are FRs agreed and mechanism-specified? Scope bounded?

**Complex:** Either axis low. Architectural decisions with multiple valid approaches, uncertain or evolving requirements, significant codebase impact.

**Moderate:** Both axes moderate-to-high. Clear requirements, no architectural uncertainty, well-defined scope. Behavioral code changes: new functions, changed logic paths, conditional branches.

**Simple:** Both axes high. Single file, obvious implementation, no architectural decisions. **No behavioral code changes** — new functions, changed logic paths, conditional branches are Moderate regardless of conceptual simplicity.

**Defect:** Observed behavior ≠ expected behavior. Route to structured-bugfix regardless of apparent complexity — the investigation structure replaces architectural design. Cynefin Complicated domain: cause analyzable, fix knowable, but analysis must be structured to prevent premature-closure bias.

#### Work Type Assessment

Assess work type alongside complexity — independent dimension (XP spike/story, Boehm throwaway/evolutionary). Work type determines execution ceremony (quality obligations); complexity determines design ceremony.

| Work Type | Diagnostic Question | Deliverable | Done Criteria |
|-----------|-------------------|-------------|---------------|
| **Production** | Does this deliver capability to users/agents? | Working feature, behavior change | Tested, linted, reviewed, integrated |
| **Exploration** | Does this produce knowledge or validate an approach? | Prototype, spike, feasibility answer | Functional, produces intended learning |
| **Investigation** | Does this produce a decision or analysis? | Report, decision entry, requirements | Accurate, complete, actionable |

**Assessment signals:**
- Explicit constraints: "prototype first," "spike," "investigate," "explore"
- Artifact destination: `plans/prototypes/` → Exploration, `plans/reports/` → Investigation, `src/` → Production
- Requirement framing: "can we...?" → Exploration, "build X" → Production, "what is...?" → Investigation
- If ambiguous, default to Production (highest ceremony — safe default)

**Artifact destination** informs quality obligations (Boehm throwaway vs evolutionary prototype distinction):

| Destination | Paths | Quality Obligations |
|------------|-------|-------------------|
| **production** | `src/`, `plugin/bin/`, `plugin/lib/` | Tests, lint, module structure, review |
| **agentic-prose** | `plugin/skills/`, `plugin/fragments/`, `plugin/agents/`, `agents/` | Wording quality, behavioral verification |
| **exploration** | `plans/prototypes/`, `plans/spikes/` | Functional, documented purpose, no test mirrors |
| **investigation** | `plans/reports/`, `docs/design.md` | Accuracy, completeness, grounding |
| **ephemeral** | `tmp/` | None |

#### Multi-Item Decomposition

**Before classifying**, check both triggers. Either one means this invocation covers more than one work item:

- **Implicit bundling** — the input artifact contains multiple discrete items (deliverable review findings, PR review comments, multi-FR implementation list).
- **Explicit bundling** — the task frame or session notes fold additional work into this invocation ("address X during /design").

Both triggers run the same procedure — the source of the item list does not change how the items are handled:

1. Enumerate all discrete items explicitly, naming the trigger for each
2. Produce a per-item behavioral code check (does this item add functions, change logic paths, or add conditional branches?)
3. Classify each item individually, with its own visible output block (Requirements-clarity → Triage Recall → Classification) — any behavioral item elevates to Moderate minimum for that item
4. Only after every item is classified, route: Simple items can batch, Moderate+ items get their own routing

**Why:** Batch classification averages heterogeneous items — a behavioral change gets masked by non-behavioral siblings. The enumeration is the structural anchor: it forces explicit acknowledgment of each item rather than silently merging them into the primary task's classification.

#### Classification Gate

**Structural check (D+B anchor):** If classification is borderline Simple/Moderate, verify with `rg --files` or `rg` (Bash) on affected files to confirm whether behavioral code changes are involved (new functions, changed logic paths).

Produce this classification block before routing (visible output, not internal reasoning — **per-item if composite**):
- **Classification:** [Simple / Moderate / Complex / Defect]
- **Implementation certainty:** [High / Moderate / Low] — is approach known?
- **Requirement stability:** [High / Moderate / Low] — are FRs mechanism-specified?
- **Behavioral code check:** Does this task add functions, change logic paths, or add conditional branches? [Yes → Moderate minimum / No]
- **Work type:** [Production / Exploration / Investigation] — what does this deliver?
- **Artifact destination:** [production / agentic-prose / exploration / investigation / ephemeral]
- **Evidence:** Which criteria and recall entries informed the decision

**Classification persistence (C-2):** Write the classification block verbatim to `plans/<job>/classification.md`. This file is consumed by `triage-feedback.sh` for post-execution comparison.

#### Routing

- **Simple, or Moderate agentic-prose** (artifact destination = `agentic-prose`) **→ one route.** Both produce an `outline.md` and hand it to `/build`; a branch that differs from another only in ceremony neither has is not a decision.
  1. **Recall:** from the in-context index, Read the memory and decision files matching the task's domain keywords.
  2. **Code reading:** Read the affected files the brief enumerates — the ones the work will actually change, not a summary of them — and resolve gaps between the brief's assumptions and actual codebase state. Where the brief does not enumerate them, `rg --files`/`rg` (Bash) to identify targets.
  3. **Generate** `plans/<job>/outline.md` per `references/write-outline.md`. For agentic prose, record **what changes** rather than why the approach was chosen: the approach is not in question, so the outline's value is the change list.
  4. **Proof:** Invoke `/proof plans/<job>/outline.md` (outline-corrector dispatched by /proof on revise/kill).
  5. **Route (after /proof approval):** commit the outline, then name `/build plans/<job>` as the next command and stop. `/build` consumes no continuation, so this is a named handoff and not a tail-call.
  Skip design — all other operational rules (skills, project tooling, communication) remain in effect.
- **Moderate, non-prose** (all other artifact destinations) **→** ground the brief against the codebase, then plan:
  1. **Code reading:** Read affected files enumerated in the brief. Resolve gaps between brief assumptions and actual codebase state.
  2. **Generate** `plans/<job>/outline.md` using lightweight format (provenance per `references/design-content-rules.md` §Provenance Section, scope, per-file changes, dependencies, IN/OUT boundaries)
  3. **Proof:** Invoke `/proof plans/<job>/outline.md` (outline-corrector dispatched by /proof on revise/kill)
  4. **Route (after /proof approval):** commit the outline, then name `/runbook plans/<job>` as the next command and stop.
- **Complex →** Read `references/write-outline.md` for Phase A (research + outline) and Phase B (user validation + outline sufficiency gate). *(Verb-oriented name: action the agent takes, not the artifact produced.)*
- **Defect →** Route to structured-bugfix workflow: reproduce → root-cause → fix → verify. Skip design — the investigation structure replaces architectural design.

**Bundled work:** handled by §Multi-Item Decomposition in Phase 0 — explicit bundling is one of its two triggers.

**Session state check:** If the session has significant pending work (>5 tasks *— ungrounded threshold, needs calibration*), suggest `/handoff:handoff` before proceeding.

## Author-Corrector Coupling

When a design modifies an "author" skill (a skill whose output is reviewed by a corrector), check coupled dependencies before completing the design:

1. Identify the corrector from the transformation table (T1–T6 in `docs/design.md` §6.4 "Pipeline contracts")
2. Check: does the corrector's review criteria need corresponding update?
3. Check: does any mechanical validator need update?
4. Include corrector/validator updates in the same design scope

**Dependency mapping:**

| Author Skill/Artifact | Corrector | Validator |
|----------------------|-----------|-----------|
| /design (outline format) | outline-corrector | -- |
| /runbook (runbook-format.md) | runbook-corrector | -- |
| /requirements (standard format) | -- (user-reviewed) | -- |

**Visible output (mandatory):** "Author change: X. Coupled corrector: Y. Update needed: yes/no." This block forces awareness of coupling — designers check the table, not silently skip it.

## Routing out

Each branch above names its own next command and stops there. There is no
tail-call: `/design` states the command, the user or the session runs it.

- Moderate non-prose → `/runbook plans/<job>`
- Simple, Moderate agentic-prose, or routed to `/build` by `references/route-to-execution.md` (B gate or C.5) → `/build plans/<job>`
- Routed to `/runbook` by that node → commit the artifact and stop; no next command
