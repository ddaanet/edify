---
name: runbook
description: |
  Decompose a design into an executable runbook — phases of typed items
  (tdd / general / inline) that /orchestrate composes dispatch prompts from.
  Triggers on /runbook or when a design needs step-by-step planning.
allowed-tools: Agent, Read, Write, Edit, Skill, Bash(rg:*, git:*)
requires:
  - Design document from /design
  - CLAUDE.md for project conventions (if exists)
outputs:
  - Execution runbook at plans/<job-name>/runbook.md
user-invocable: true
continuation:
  cooperative: true
  default-exit: ["/handoff:handoff", "/commit-commands:commit"]
---

# Write the Runbook

**Usage:** `/runbook plans/<job-name>/design.md`

Produce `plans/<job>/runbook.md` — the terminal planning artifact. Item and
slice format: `references/runbook-format.md`. Pipeline context (see
`docs/design.md` §6.4 "Pipeline contracts"): `/design` → `/runbook` →
`runbook-corrector` → `runbook-simplifier` → `/proof` → `/orchestrate` in a
fresh session.

**Prerequisites check (D+B anchor):** Check the plan directory for a
design-stage artifact: `outline.md` or `design.md`. Absent
→ STOP. `/runbook` without prior `/design` gating is an error — scope was not
user-validated.

## Phase Type Model

Each phase declares `type: tdd`, `type: general` (default), or
`type: inline`. Type determines:

- **Item format:** tdd → `Slices:` with per-slice test lists; general →
  concrete action against a named target; inline → same, executed by the
  orchestrator itself. All per `references/runbook-format.md`.
- **Review criteria:** `runbook-corrector` applies slice rules to tdd items,
  clarity and readiness rules to all.
- **Dispatch:** tdd → four dispatches per slice (RED → test review → GREEN →
  code review); general → one dispatch; inline → no dispatch.

## Process

### 1. Recall and Discovery

0. **Documentation perimeter and requirements (if present):** If the design
   includes a "Documentation Perimeter" section, Read the files under
   "Required reading" and invoke any listed skill-loading directives. If it
   includes a "Requirements" section, note requirements and scope boundaries.

1. **Implementation recall (D+B anchor — tool call required):**
   `Skill(skill: "edify:recall", args: "plans/<job> — implementation patterns
   for this design")`. Patterns for building this, not classifying it.
   Upstream triage recall (from /design) does not satisfy this gate.

2. **Augment the recall artifact** (`plans/<job>/recall-artifact.md`): add
   the paths recall selected, with implementation focus — planning-relevant
   entries only (model selection failures, phase typing decisions, precommit
   gotchas). Execution-level detail reaches executors through dispatch
   prompts, not the artifact. If absent, write the initial artifact.

3. **Verify actual file locations:** `rg --files` / `rg` (Bash) for every
   source and test file the design references. Never assume paths from
   conventions. STOP if expected files are not found.

4. **Post-explore recall gate (D+B anchor):** exploration may surface domains
   step 1 did not anticipate. Invoke `Skill(skill: "edify:recall")` (no topic
   — selection runs against what exploration surfaced). New entries → add
   their paths to the artifact. None → state that explicitly.

### 2. Write the Runbook

Write `plans/<job>/runbook.md` per `references/runbook-format.md`:
requirements mapping table, typed phases, items with requirement IDs,
`Slices:` on tdd items, `Interfaces:` where one item's output is another's
input.

### 3. Self-Check

Before review, verify:

- **All implementation choices resolved** — no "choose" / "decide" /
  "determine" / "select approach" language; each item commits to one
  approach.
- **Inter-item dependencies declared** — `Depends on: Item N.K` wherever an
  item consumes another's output.
- **Requirement IDs on every item** — `Requirements: FR-x` present; no
  item without one.
- **Interfaces on cross-item dependencies** — every `Depends on:` target
  carries an `Interfaces:` block, one contract per line with full signature
  and return type.
- **Slices on tdd items** — `Slices:` present, slice 1 pins the external
  contract, each later slice one behaviour, each test named with its
  assertion stated.
- **No code blocks in items** — behaviour, targets and tests in prose;
  `Interfaces:` is the only formal element.
- **Code-fix items enumerate affected call sites** (file:function or
  file:line).
- **Later items reference post-phase state** — an item modifying a file a
  prior phase changed notes the expected state.
- **Phase size** — a phase over 8 items is a split signal: prefer splitting
  the phase at a clean boundary. Not a count gate.
- **Cross-cutting issues scope-bounded** — "addressed by items X, Y" / "out
  of scope: Z".
- **No vacuous items** — every item produces a functional outcome;
  scaffolding merges into the nearest behavioural item.
- **Foundation-first ordering** — existence → structure → behaviour →
  refinement; no forward dependencies.
- **Prose atomicity** — all edits to one prose artifact in one item.
- **Self-modification ordering** — when the runbook modifies pipeline tools
  it will later use, tool-improvement items precede tool-usage items; see
  `docs/design.md` D-39, which routes self-modifying work out of the runbook
  pipeline entirely when the risk cannot be ordered away.

### 4. Commit

Commit `runbook.md` before review — review agents operate on filesystem
state, and a committed checkpoint keeps their fixes diffable.

### 5. Review

Delegate to `edify:runbook-corrector` (fix-all mode); pass
`plans/<job>/recall-artifact.md` by path — the corrector Reads the artifact
and the files it lists. Never inline recall content in the prompt. Read the
returned report. Critical issues remaining → STOP and escalate to user.

### 6. Consolidate

Merge trivial work into adjacent items directly (single-constant changes,
setup that batches with feature work), then delegate to
`edify:runbook-simplifier` for pattern-level consolidation
(identical-pattern items → parametrized, same-module batches, sequential
additions). Read its report; verify requirements mapping survived.

### 7. Proof

Invoke `/proof plans/<job>/runbook.md` — the user validates the runbook
item by item. This is the human gate on the artifact execution will read.

## Continuation

Read `plugin/fragments/continuation-passing.md` and follow its §Consumption
Protocol as the final action of this skill; on failure, its §Error
Propagation. No prepend: orchestration runs in a fresh session via
`/handoff:handoff` — planning has consumed most of this session's context
budget, and the orchestrator needs its own.
