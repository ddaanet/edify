# Review: verify-step.sh, fragments, human docs, plan cross-refs

Scope: `plugin/skills/orchestrate/scripts/verify-step.sh`,
`plugin/fragments/{delegation,workflows-terminology,execution-routing,
escalation-acceptance,continuation-passing}.md`, `CLAUDE.md`, `README.md`,
`plugin/README.md`, `.claude/rules/workflow-work.md`,
`plans/pilfer-superpowers/requirements.md`, plus a repo-wide `rg` sweep for
removed names (FR-2/C-4). Baseline: a4aad0c8. Design reference:
`plans/pipeline-simplification/outline.md` (D1-D15, D12 struck).

## Verdict

All eleven files match the design decisions. One defect found and fixed
outside the eleven — a sweep hit the design outline itself calls out. No
other issues.

## `verify-step.sh` (D6, FR-4)

Matches D5/D6 exactly: clean-tree gate tolerates the resting ` M memory` line
(`grep -vx ' M memory' || true` — the sanctioned no-match-is-a-result use of
`|| true`), any other dirty path fails, then `just precommit`; no submodule
pointer-sync check (correctly dropped per D6). No error suppression beyond
that one grep. `shellcheck` clean. Executable bit set (`-rwxr-xr-x`). Confirmed
live caller: `plugin/skills/orchestrate/SKILL.md:100,178` — FR-4's "kept only
if it still has a caller" condition holds.

## Fragments

- **`delegation.md`** — "File Reference Dispatch" replaced by "Prompt
  Composition", correctly deferring to
  `plugin/skills/orchestrate/references/dispatch-composition.md` (one-line
  summary: item text inline, design/recall by path) rather than restating its
  naming/resumption/model-assignment content. No duplication defect.
  "step"→"item/dispatch"/"slice" vocabulary updated throughout the changed
  lines.
- **`workflows-terminology.md`** — Item and Slice rows added, consistent with
  `plugin/skills/runbook/references/runbook-format.md`'s definitions; Phase
  type row lists all three types (tdd/general/inline); "Runbook prep" row and
  its 4-point process removed (superseded by D8 — self-check kept as a split
  signal, not a named row); directory-naming note updated from "step files" to
  "reports".
- **`execution-routing.md`**, **`escalation-acceptance.md`** — single-line
  vocabulary fixes ("Runbook step"→"Runbook item", "step file"→"dispatch
  prompt"), no residual stale terms.
- **`continuation-passing.md`** — "Tier 1/2"/"Tier 3" annotations on the
  cooperative-skills table dropped in favor of "no runbook"/plain; "per
  cycle"→"per dispatch" in the pivot-transactions table. Rest of the file
  (unchanged) is out of this job's scope and untouched.

## CLAUDE.md, README.md, plugin/README.md

- CLAUDE.md's generator example strips the dead `prepare-runbook.py` mention;
  the Skills paragraph names the single `orchestrate` route plus `design →
  inline`, describes the runbook as one artifact with typed phases/interfaces/
  slices, and states dispatch composition by reference — matches D4/D7/D8.
  Dated claims ("dropped in 2026-08" / "dropped in 2026-09") check out against
  today's date (2026-09-01) and the outline's decision date (2026-08-28,
  validated 2026-08-29).
- README.md / plugin/README.md: skills and agents tables verified against
  `ls plugin/skills plugin/agents` — exact match, 11 skills / 11 agents, no
  stale entries (`review-plan`, `runbook-outline-corrector` gone; `refactor`,
  `runbook-simplifier` present). plugin/README.md's Scripts table matches
  `ls plugin/bin` plus the one orchestrate script; the "Documentation" section
  pointing at deleted `plugin/docs/` is removed entirely.

## `.claude/rules/workflow-work.md`

"Key areas" line rewired to name delegation-by-reference/dispatch
composition, typed review gates, slice-batched TDD, and the two execution
routes. Confirmed both cited sections exist: `docs/design.md:370` "### 6.4
Pipeline contracts", `docs/design.md:498` "### 6.5 Execution routing" — titles
match the pointer text exactly.

## `plans/pilfer-superpowers/requirements.md`

FR-9 marked satisfied by pipeline-simplification FR-6 with a dated pointer;
FR-10 repointed to `runbook-format.md`/`runbook-corrector`; FR-12 gets a dated
note that the corrector count dropped by one; NFR-1 drops deterministic
validation from the preserved list with a dated retirement note tied to the
new NFR-1 verdict; Dependencies section repoints from
`memory/workflow-pipeline-revival.md` to the landed pipeline-simplification
job. All dates are 2026-09-01, consistent with today. No estimates presented
as fact — the one changed number ("corrector count dropped by one") is a
structural fact (agent file count), not a measurement claim.

## Repo-wide sweep (FR-2/C-4 acceptance)

Excludes `plans/`, `memory/`, `docs/changelog.md`, `docs/superpowers/`,
`tmp/`, `.claude/handoff-*`.

| Removed name | Hits | Classification |
|---|---|---|
| `prepare-runbook.py` | `docs/design.md:390,962`; **`agents/learnings.md:126`** | design.md = out of my scope (design reviewer, dated §7/history); learnings.md = **defect, fixed** (see below) |
| `validate-runbook.py` | `docs/design.md:923` | out of my scope (design reviewer, dated history) |
| `assemble-runbook.py` | none | clean |
| `split-execution-plan.py` | none | clean |
| `verify-red.sh` | none | clean |
| `review-plan` (skill) | none | clean |
| `runbook-outline` / `runbook-outline-corrector` | none | clean |
| `plugin/docs/` | none | clean |
| `tdd-workflow.md` / `general-workflow.md` | none | clean |
| `progress-tracking.md` | none | clean |
| `tier3-*` | none | clean |
| `runbook-phase-*` | none | clean |
| `common-context.md` / `orchestrator-plan` | none | clean |
| `Tier 1/2/3` (execution-tier sense) | none repo-wide (outside exclusions) | clean — **fixed** `agents/learnings.md:41` (see below) |
| `orchestrator manifest` | none | clean |
| bare `manifest` | `docs/design.md:242`, `docs/marketplace.md:9`, `plugin/README.md:68`, `scripts/release.sh` (×7), `package-lock.json` (×2) | all plugin/marketplace-manifest sense — correctly excluded per D10, not a defect |
| `steps/` (directory) | `agents/learnings.md:103` | keep-as-history — undated incident log entry intrinsically about the old step-file-in-worktree mechanism; the design outline's own sweep list names only lines 41 and 126 in this file for reword, not 103 |
| `common-scenarios.md` | `plugin/skills/review/SKILL.md:178` | not a defect — different live file (`review/references/common-scenarios.md`), explicitly excluded in the task brief |
| `test_validate_runbook*` / `validate_runbook_fixtures*` | none | clean |

**Defect found and fixed:** `agents/learnings.md` (repo root, not
`plugin/agents/`) is exactly the site the outline's own sweep addendum names
(D10: "`agents/learnings.md:41,126` (undated log — reword the two lines, do
not restructure)") — it wasn't touched by the implementation. Fixed both
lines in place, generalizing away from the dead terms without restructuring
the entries:

- Line 41: `Tier 3 concern (cross-session persistence) ... Tier 1/2
  (same-session, same-context)` → `a cross-session-persistence concern ...
  a same-session, same-context path`.
- Line 126: `` `prepare-runbook.py` regenerates agents with same names `` →
  `Regenerating agents with the same names`.

Line 103 (a different entry, "When dispatching step agents in worktrees") was
left as-is: it's an undated incident record intrinsically about the deleted
step-file/worktree mechanism, not a general principle borrowing tier/script
vocabulary as incidental illustration, and the design's own sweep addendum
scoped the reword to lines 41 and 126 only.

## Verification

- `shellcheck plugin/skills/orchestrate/scripts/verify-step.sh` — clean.
- `ls -l plugin/skills/orchestrate/scripts/verify-step.sh` — executable.
- `just precommit` — green (after the `agents/learnings.md` fix).
- README/plugin-README tables cross-checked against `ls plugin/skills
  plugin/agents plugin/bin`.
- `docs/design.md` §6.4/§6.5 section titles confirmed present and matching
  `.claude/rules/workflow-work.md`'s pointer.

## Not fixed / not flagged (correctly out of scope)

- `docs/design.md`, `docs/changelog.md` hits — design reviewer's territory,
  read for cross-check only.
- `plugin/skills/**/SKILL.md`, skill `references/` — skill reviewer.
- `plugin/agents/` — agent reviewer.
