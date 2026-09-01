# Outline Review — pipeline simplification (PDR)

Target: `plans/pipeline-simplification/outline.md`
Against: `plans/pipeline-simplification/requirements.md` (FR-1..7, NFR-1..2,
C-1..5, Q-1..2)
Criteria: approach meets requirements; options selected with rationale; risks
and open questions identified; scope boundaries explicit.
Date: 2026-08-29. All fixes applied to the outline.

## Verdict

**PDR pass, with fixes applied.** The approach is sound and traceable: every FR
has at least one decision, both open questions are resolved with rationale and
rejected alternatives, no decision contradicts a constraint, and scope is
enumerated both ways. One critical defect (task ordering destroying its own
migration sources), seven major gaps (two incomplete enumerations, one
decision/design contradiction, three missing decisions, one missing NFR
verdict) and eight minor gaps were found and fixed.

D1 and D12 are the two flagged deviations from the requirements' wording; both
were left as flagged, per instruction. Edits touching D1 add the missing
dispatch-reference filename and do not touch the deviation.

## Method note

C-4 requires the deletion set be re-derived by `rg` at review time rather than
taken from the document's lists (`spec-enumerations-need-rederiving`). It was:
the sweep was run over the working tree before reading either enumeration, and
its result compared to D10 and to `reports/explore-inbound-refs.md`. Six sites
turned up that neither list names (M1). This is the exact failure the memory
describes — conformance to D10 would have passed while leaving live references
behind.

## Critical

**C1 — Task 1 deletes the source material tasks 3 and 4 must migrate.**

The execution order put all deletion in task 1, but five files in the deletion
set have content the outline itself schedules for migration:

| File | Migrating content | Consumer |
|---|---|---|
| `tdd-cycle-planning.md` | assertion-quality table, integration-first ordering | D7 → `runbook-format.md` (task 3) |
| `conformance-validation.md` | exact-expected-string rule | D10 → `runbook-format.md` (task 3) |
| `anti-patterns.md` | seven surviving rows | D10 → `runbook-format.md` (task 3) |
| `tier3-planning-process.md`, `tier3-outline-process.md` | Phase 0.5 discovery steps, Phase 0.75 self-check list | D8's one-path process (task 3) |
| orchestrate `common-scenarios.md` | escalation rules | D10 → `/orchestrate` inline (task 4) |

Verified: `Phase 0.5` / `0.75` / `0.85` do **not** appear in
`plugin/skills/runbook/SKILL.md`. D8's citations point exclusively into
`tier3-planning-process.md` and `tier3-outline-process.md`, both in task 1's
deletion set.

Git history preserves the text, but a task that finds its source gone
reconstructs it from memory rather than reaching for `git show` — and the
reconstruction passes every downstream check, because nothing compares it to
the original.

**Fix applied:** D10 gains a "Deletion timing" clause — a file whose content
migrates is deleted by the task that performs the migration. The execution
order now scopes task 1 to the no-surviving-content set and moves the five
migrating files into tasks 3 and 4, with a closing reminder line.

## Major

**M1 — D10's enumeration is incomplete.** Six live sites named by neither D10
nor the `rg` map:

- `CLAUDE.md` is four regions, not the one line D10 cites: `:57` (generator
  example), `:178` (pipeline line naming Tier 3 / Tier 1-2 and `review-plan`),
  `:183-184` (backing scripts + `plugin/docs/`), `:187-190` (delegation by step
  file). Task 7 named the file, so the risk was bounded — but a reader working
  from D10's `CLAUDE.md:57` fixes one of four.
- `plugin/agents/outline-corrector.md:143` — its cross-component interface
  example is `runbook-phase-*.md`. `outline-corrector` is declared OUT of scope
  as *unchanged*; FR-2's acceptance makes this one line an unavoidable
  exception. Now stated as such, with "change nothing else".
- `plugin/skills/design/references/design-content-rules.md:41` (naming-mismatch
  example uses `runbook-outline-corrector`), `:95` (integration-first "defined
  in `/runbook` skill"), `:127` (§6.4 pointer).
- `plugin/skills/design/SKILL.md:163` — cites the transformation table as
  "T1-T6.5", which D11's renumbering breaks.
- `plugin/skills/proof/references/item-review.md:14` — phased-plan markers
  `## Cycle` / `## Step`.
- `.claude/rules/workflow-work.md` — points at §6.4/§6.5 with a "runbook
  structure" key-areas line.

Checked and correctly excluded (unrelated senses, no action needed):
`plugin/fragments/error-classification.md` and `execution-routing.md` ("model
tier"), `prerequisite-validation.md` ("escalation cycles"),
`tests/manual/pushback-validation.md` and `scripts/scrape-validation.py` (model
tier), `docs/design.md:546` ("dependency cycles"), `tests/test_agent_files.py`
(session-JSONL agent files, not pipeline agents).

**Fix applied:** new "Sites the review's own `rg` adds beyond both" block in
D10; the affected files added to execution tasks 6 and 7.

**M2 — D11's design.md rewire set is incomplete.** Four present-tense claims
about the dying machinery that FR-7's acceptance forbids, unlisted:

- §3.2 row **FR-11** — "Wrap **Tier 1/2** work in a lifecycle".
- **D-32** — "Paired fix: expansion guidance references design sections rather
  than reproducing implementation detail."
- **§6.3** (line 351) — "handled in batch at review checkpoints instead of
  RED/GREEN **cycles**".
- **D-69** (line 791) — "Runbook planning should project file growth and insert
  split points rather than react **per cycle**".

**Fix applied:** all four added to D11 with their replacements.

**M3 — D9 contradicts D-69.** D9 dropped "growth projection's
split-recommendation wording" from `runbook-corrector`, while D-69 requires
runbook planning to project file growth and insert split points. D11 did not
rewire D-69, so the outline as written left a standing decision mandating what
another decision removes.

**Fix applied:** D9 now keeps growth projection (its output becomes a
phase-split signal alongside the item count); D11 rewires D-69's "per cycle" to
"per slice" and notes D9 keeps the projection.

**M4 — No decision stated `tdd-auditor`'s criteria.** FR-5 acceptance clause 4
requires it to check RED-before-GREEN per slice and test-at-a-time from the
commit sequence, and FR-5's *Known risk* names that check as the detector for
the batch-visibility shortcut. The outline dispatched `tdd-auditor` at
completion (D5) and listed it in task 5, but never said what it checks — and
the current agent is built on planned-vs-executed cycle counts and a mandatory
per-cycle REFACTOR, both of which this job removes.

**Fix applied:** new **D14**, stating the three commit-sequence checks, the two
dropped checks and why, the link to D5's commit subjects that make the check
mechanical, and the FR-5 known risk it detects — labelled unvalidated per
NFR-2 (the pre-teardown observation is ~6 months old at an unrecorded model
tier).

**M5 — No NFR-1 verdict.** NFR-1 requires each of the five distinguishers be
shown to survive and requires an explicit "use superpowers directly" statement
if any does not — "not papered over". The outline made no such statement.

This matters most for the tester/implementer separation, which D2 collapses
into one agent file. D2's rejection rationale even argued the other way
("splits the tester/implementer contract across two files"), leaving the
impression the separation is agent-level and now gone. It is not: RED and GREEN
are distinct dispatches, so the GREEN instance inherits none of the RED
instance's reasoning (`cc-subagent-context-capabilities`), and the test review
sits between them. Requirements Q-1 explicitly blesses either resolution.

**Fix applied:** new "NFR-1 verdict" section itemising all five with their
decision references, plus the non-surviving item (deterministic validation).
D2's rationale reworded to state the separation it preserves and to give an
accurate reason for rejecting `artisan`-as-GREEN (one protocol, two edit
sites).

**M6 — `inline`-typed items had no execution decision.** FR-1 keeps three item
types. D4 covers dispatch composition and D5 covers tdd slices; nothing said
how the orchestrator executes an `inline` item. Today's `/orchestrate` §3.0
executes them in-session with a proportionality-gated self-review — the one
path where the orchestrator reviews its own edits — and §3.0 was on no
decision's keep list, so a wholesale rewrite would have dropped it silently.

**Fix applied:** new **D13** covering both `general` and `inline` items,
keeping §3.0's proportionality rule and its rationale for the threshold
staying the fragment's rather than the orchestrator's judgement.

**M7 — D1's "one source for prompt composition" named no file.** D1's whole
argument for deleting `/inline`'s Tier 2 path rests on `/inline` citing
"`/orchestrate`'s dispatch reference", but no decision created one — D7 names
`runbook-format.md` as the new reference and nothing names this one. Without it
the composition rules live inside `/orchestrate`'s SKILL.md and `/inline`
cannot cite them without loading the orchestration lifecycle.

**Fix applied:** D1 names
`plugin/skills/orchestrate/references/dispatch-composition.md`, states why it
is a reference rather than SKILL.md prose, and states what
`plugin/fragments/delegation.md` keeps versus loses to it; added to task 4.

## Minor

- **m1 — "run summary" was an undefined term** used by D10 ("the run summary
  replaces it") and inherited from today's §3.4/§6. It is also where two of
  FR-5's three dogfood counts have to live. *Fixed:* defined under D4 as the
  orchestrator's closing message (not a file), with its contents and the
  counts it supplies.
- **m2 — the vocabulary sweep listed bare `manifest`**, which collides with the
  live plugin/marketplace sense in `plugin/.claude-plugin/plugin.json`,
  `scripts/release.sh`, `docs/marketplace.md`, `docs/design.md:232` and
  `package-lock.json`. *Fixed:* scoped to the orchestrator sense with the grep
  pattern stated and the false-positive sites named.
- **m3 — FR-4's "no preflight step checking for prepared artifacts" was
  unstated.** D12 adds a preflight, so the distinction needed to be explicit.
  *Fixed:* D4 opens by retiring §1 "Verify Runbook Preparation" and naming
  D12's branch gate as the only survivor.
- **m4 — D6 asserted `verify-step.sh` "keeps its caller"** but `/orchestrate`
  is rewritten wholesale, so the call site is something the rewrite must add,
  not inherit; D5's sequence never placed it. *Fixed:* placed in D5 as the
  post-dispatch gate with its remediation ladder; D6 points at it.
- **m5 — D5(a) did not say RED mode stops before GREEN**, which FR-5 acceptance
  clause 1 requires `test-driver.md` to describe. *Fixed.*
- **m6 — `runbook-simplifier`'s frontmatter `description:` says "after Phase
  0.85"** and was not in D9's rewrite list. A description is injected every
  session, so a stale one costs context in every session
  (`skill-description-purpose-first`). *Fixed:* added to D9, with the same
  check on `runbook-corrector` after the rename.
- **m7 — D11 renumbered D-26's T-rows one clause after asserting "IDs are cited,
  never renumbered".** The two are reconcilable (T-numbers are positional row
  labels, FR IDs are cited identifiers) but the exception needed stating, and
  there is exactly one citation to repoint. *Fixed:* stated, with
  `design/SKILL.md:163` named.
- **m8 — `.claude/handoff-task.md` and `handoff-todo.md` carry machinery
  names** and were in no exclusion statement. *Fixed:* added to D10's
  exclusions as session state rewritten by its own tooling.

## Traceability check

Every FR acceptance clause maps to a decision. Post-fix:

| Requirement | Decisions | Notes |
|---|---|---|
| FR-1 one runbook stage | D7, D8, D10, D13 | three item types now all covered (M6) |
| FR-2 delete expansion machinery | D10 | enumeration corrected (M1), timing fixed (C1) |
| FR-3 rename the gate | D9, D11 | description sweep added (m6) |
| FR-4 orchestrator composes prompts | D1, D4, D6, D13 | preflight (m3), dispatch reference (M7), `verify-step.sh` (m4) |
| FR-5 slice-batched TDD | D2, D3, D5, D14 | acceptance 1 (m5), acceptance 4 (M4) |
| FR-6 prose plus interfaces, never code | D7, D9 | complete as written |
| FR-7 rewire the design record | D11 | four sites added (M2), D-69 conflict (M3) |
| NFR-1 preserve the distinguishers | NFR-1 verdict section | was absent (M5) |
| NFR-2 measure, do not estimate | D15 | complete as written |

Constraints: no decision contradicts C-1 (D4's tradeoff cites it), C-2 (D5,
D11 §7), C-3 (no shims or aliases introduced anywhere), C-4 (D10, now actually
re-derived), or C-5 (execution shape is an inline task sequence that never
invokes the SUT).

FR-5's three dogfood counts now all have a home: list revisions via the
`runbook.md` diff (D4), dispatches per item and test-review catches via the run
summary (D4, m1). Per-test dispatch is recorded as the fallback in §7 (D11).

## Not changed

- **D1** (`/inline` never consumes a runbook) and **D12** (branch gate not
  derived from any FR) — the two flagged deviations, left flagged for `/proof`.
  D1's edit adds the missing filename only.
- **D10's sweep exclusions** (`docs/changelog.md`, `docs/superpowers/`,
  `plans/`, `memory/`) — deliberate, justified against FR-2's literal wording,
  and consistent with `design-doc-writing`'s write-time-record rule. Extended
  by one entry (m8), not narrowed.
- **D7's format** and **D9's criteria in/out** — checked against FR-6 clause by
  clause; complete as written apart from the growth-projection conflict (M3).
