# Pipeline Simplification

Replace the two-stage runbook model (outline → expanded runbook → step
files → manifest-driven orchestration) with a one-stage model shaped like
superpowers' writing-plans / executing-plans / subagent-driven-development:
a single runbook file that a strong orchestrator reads and composes dispatch
prompts from live. Slice-batched TDD replaces the one-test-per-cycle loop;
the tester/implementer/reviewer separation is kept.

Decided in conversation 2026-08-28, validated by `/proof` 2026-08-29.
Supersedes D-34's Tier 3 rationale and reopens the "do not re-litigate" tier
structure in `docs/design.md` §1 — deliberately, on the grounds recorded
under C-1.

## Requirements

### Functional Requirements

**FR-1: One runbook stage**
The runbook is the artifact `/runbook` produces today as
`runbook-outline.md`: phases with typed items (tdd / general / inline), each
item a concrete action against a named target, with dependencies noted. It is
renamed `runbook.md` and is the terminal planning artifact — nothing expands
it. Acceptance: `/runbook` writes `plans/<job>/runbook.md`; no
`runbook-outline.md`, `runbook-phase-N.md`, `steps/`, `common-context.md`,
`orchestrator-plan.md`, or `manifest` artifacts exist anywhere in the plugin
or its docs; the Tier 2 / Tier 3 split inside `/runbook` collapses to one
path.

**FR-2: Delete the expansion machinery**
Remove `plugin/bin/prepare-runbook.py`, `plugin/bin/validate-runbook.py`
(with `tests/test_validate_runbook_reporting.py` and
`tests/fixtures/validate_runbook_fixtures.py` — it imports its parsers from
`prepare-runbook.py`, and four of its five checks validate expansion-only
content that FR-6 removes from the runbook by design),
`plugin/bin/assemble-runbook.py`, `plugin/scripts/split-execution-plan.py`,
the `/runbook` references that serve expansion (`tier3-expansion-process.md`,
`tier3-planning-process.md`, `tier3-outline-process.md`, and whichever of
`patterns.md`, `examples.md`, `tdd-cycle-planning.md`, `general-patterns.md`,
`error-handling.md`, `anti-patterns.md`, `conformance-validation.md` describe
the expanded form rather than the runbook), `plugin/skills/review-plan/` in
full, and the `runbook-corrector` agent. Cut whole machinery in one pass:
tests, fixtures, recipes, docs (`plugin/docs/tdd-workflow.md`,
`general-workflow.md`), README rows, `docs/design.md` §5.3 and D-26 rows
T3–T5, and every inbound reference. Acceptance: `rg` for each removed name
over the repo (excluding `plans/` reports and git history) returns nothing;
`just precommit` green.

**FR-3: Rename the outline gate to the runbook gate**
`runbook-outline-corrector` becomes `runbook-corrector` (the name freed by
FR-2). Its §5.5 "Append Expansion Guidance to Outline" step and every
expansion-facing criterion go; its requirements-coverage, design-alignment,
phase-structure and complexity-distribution checks stay. `runbook-simplifier`
keeps its role on the same artifact, with its "before expensive phase
expansion" framing removed. Acceptance: agent file renamed and reframed; D-26
gate T2 names `runbook-corrector`; no prose in either agent refers to a later
expansion stage.

**FR-4: Orchestrator composes prompts from the runbook**
`/orchestrate` reads `plans/<job>/runbook.md` and, per item, composes the
dispatch prompt itself from the item text, the design, and the recall
artifact — no step files, no manifest, no phase-agent mapping table. The
prompt names paths for design and recall artifact and carries the item text
inline: a child does not inherit the parent's context
(`cc-subagent-context-capabilities`), while the orchestrator, running as the
main session, receives each child's completion normally. Plan deviation
during execution is handled by re-composing the next prompt, not by
regenerating artifacts. Acceptance: `/orchestrate` has no preflight step
checking for prepared artifacts; §2 "Read Orchestrator Plan" and the step-file
dispatch mechanics in §3.1/§3.2 are replaced by runbook-item dispatch;
`verify-red.sh` / `verify-step.sh` are kept only if they still have a caller.

**FR-5: Slice-batched TDD, with RED dispatched separately from GREEN**
A tdd item carries a test list in prose, grouped into behaviour slices
ordered outside-in (`outside-in-tdd`): slice 1 pins the external contract
with the degenerate or naive happy-path case; each later slice adds one
behaviour — an error path, an edge, a second feature. Slice count is the
planner's call. The dispatch unit is the slice, four dispatches each:

1. **RED** — the test-driver writes the slice's tests and gets a genuine red
   for each: for slice 1 it stubs the SUT importable but inert and runs, so
   every test fails on its assertion, never on a missing symbol
   (`genuine-red-not-missing-sut`); for later slices the SUT exists and
   returns wrong or nothing for the new behaviour. It stops before GREEN.
2. **Test review** — a reviewer a tier above the implementer reads the red
   output and hunts wrong-reason tests: one that came back green has named
   itself vacuous (`green-is-not-evidence`).
3. **GREEN** — the GREEN role receives the failing batch as its contract and
   makes the tests pass one at a time, growing the implementation rather than
   writing it in one lump.
4. **Code review** — may additionally run the batch once against a mutated
   SUT (the plausible-but-forbidden implementation) and confirm it reds; the
   stub run proves the tests detect absence, only this second run proves they
   detect wrongness.

After each slice's GREEN the orchestrator may revise the remaining slices'
test lists from what the slice revealed — the adaptation per-test TDD gets
from its practitioner, made cheap by FR-4's live prompt composition.

Acceptance: `test-driver.md` describes the slice RED dispatch and stops before
GREEN; the GREEN role's instructions state one-test-at-a-time; `/orchestrate`
sequences RED → test review → GREEN → code review per slice and names the
list-revision step; `tdd-auditor` checks RED-before-GREEN per slice and
test-at-a-time from the commit sequence; the "every 3-5 cycles" mid-execution
checkpoint (L-2) is removed with the cycle concept. Evidence from the dogfood
run: slices whose GREEN changed the remaining list, wrong-reason tests caught
at test review, dispatches per item. Per-test dispatch is the recorded
fallback if those counts say slices lose reviews.

Known risk, unvalidated: in the pre-teardown pipeline, implementation agents
that could see the whole test batch took implementation shortcuts, which is
why executor context was limited on an as-needed basis (model tier
unrecorded; roughly six months before this decision; adherence has since
improved). `tdd-auditor`'s commit-sequence check is the detector.

**FR-6: Runbook items are prose plus interfaces, never code**
Runbook items describe behaviour, target files and the tests to write in
prose. Where an item's output is consumed by another item, the runbook carries
an explicit interface block so two fresh subagents translating prose
independently cannot diverge: each method, dataclass, exception or file
contract on its own line with its full signature and return type — never a
run-on paragraph (`genuine-red-not-missing-sut`: un-cramming surfaces elided
return types). No item contains implementation or test code blocks.
Acceptance: the `/runbook` format section states both rules beside the item
format (D-53); `runbook-corrector` flags code blocks in items as a violation,
missing interface blocks on cross-item dependencies as a gap, and crammed or
return-type-elided contracts as a violation; pilfer FR-9 is satisfied by this
FR.

**FR-7: Rewire the design record**
`docs/design.md` §1 (Now / Do-not-re-litigate), §5.3 (pipeline structure),
D-24 (delegation by reference — the mechanism changes from step files to
composed prompts; the by-reference principle for design and recall artifacts
survives), D-26 (gate table), D-34 (tiers), D-49 (its mechanical/semantic
grounding example), L-2 (tier thresholds) and §7 Rejected alternatives are
rewired to the new model, and a changelog entry is added. The rejected Tier 3
model is recorded under §7 with the reasoning in C-1, not archived.
Acceptance: no present-tense claim in `docs/design.md` describes step files,
manifests, phase expansion, per-cycle dispatch or `validate-runbook.py`.

### Non-Functional Requirements

**NFR-1: Preserve what distinguishes edify from installing superpowers**
Artifact traceability (requirements → design → runbook, requirement IDs on
runbook items), pinned model tiers per agent, the `/proof` human gate on
planning artifacts, fix-all correctors at every remaining gate (D-27), and the
tester/implementer separation (FR-5). Inherited from pilfer NFR-1; if any of
these does not survive, the honest outcome is "use superpowers directly" and
that must be stated, not papered over.

Stated: deterministic validation does **not** survive. `validate-runbook.py`
was the only pipeline script with tests, and it goes under FR-2 — its
consumer (an orchestrator that crashed on malformed input) is gone, and a
validator with nothing downstream to fail for is ceremony (D-51).

**NFR-2: Measure, do not estimate**
Deletions are reported as measured line and token counts (`wc`, `edify
tokens`) before/after. Claims about slice-batched TDD's cost and about the
test review's catch rate are labelled unvalidated until the dogfood run
supplies counts. Provenance per pilfer NFR-2.

### Constraints

**C-1: The weak-orchestrator premise is rejected**
The full-runbook tier existed so a weak (haiku) orchestrator could dispatch
pre-written sub-agent prompts. A strong orchestrator does not need them, and
pre-written prompts become harmful the moment implementation deviates from the
plan. The context-economy argument for step files only shifts the burden to
runbook generation; an orchestrator whose context overflows is the symptom of
a runbook too large to begin with (BDUF, non-converging deliverable review).
The old model also limited executor context deliberately, feeding it on an
as-needed basis because fuller context led to implementation shortcuts; that
rationale survives in a different form — the orchestrator composes exactly
what each dispatch sees (FR-4). This is the user's diagnosis from operating
the pre-teardown pipeline; it is architectural, so it does not need the
current pipeline run end-to-end to confirm.

**C-2: Per-test dispatch is too expensive for agents**
One-test red/green cycles cost four dispatches per test. Per-test dispatching
never delivered a human practitioner's continuity — executors saw limited
context by design (C-1) — so its benefit was the per-test genuine red, and a
stub run preserves that for a whole batch: one run shows every test's red
individually (`genuine-red-not-missing-sut`). Batch per behaviour slice
(FR-5); keep RED as a separate dispatch from GREEN, which is the specific
claim `green-is-not-evidence` backs with observed data (ghmem B1: one
wrong-reason test per task, invisible without a red to have watched).
Superpowers' whole-task batching is reported adequate in practice
(anecdotal, superpowers' own usage); Beck's Canon TDD test-list-then-revise
loop is the documented human practice the slice model follows, adapted
because agent economics differ.

**C-3: No compatibility obligations**
No user base (`distribution-published`). Artifact renames, format changes and
deleted scripts need no shims, aliases or migration notes.

**C-4: Cut whole machinery in one pass**
Per `remove-cleanly-no-vestigial`: no absence-guard tests, no hollow modules,
no "kept for reference" docs. Every inbound reference is re-derived by `rg` at
review time, not taken from this document's lists
(`spec-enumerations-need-rederiving`).

**C-5: Self-modifying work leaves the runbook pipeline (D-39)**
This job edits `/runbook`, `/orchestrate` and their agents. Execute it as an
inline task sequence with fresh instruction loads per task, not through the
pipeline it is changing.

### Out of Scope

- The design-outline stage and `outline-corrector` — unchanged.
- `/inline`'s lifecycle beyond consuming `runbook.md` instead of
  `runbook-outline.md` — pilfer FR-5/FR-6 (fix loop, rulings ledger) are
  separate.
- FR-12 corrector-skeleton compression (pilfer defect 21) — the corrector
  count drops by one here; the remaining bodies are pilfer's.
- Pilfer Q-1 (invoke superpowers skills vs vendor) — this job models on
  superpowers' shape and does not invoke its skills.
- The end-to-end dogfood run — it follows this job and runs against the
  simplified pipeline, not the current one.
- Memory consolidation (`memory/MEMORY.md` over budget) — separate item.

### Dependencies

- `plans/pilfer-superpowers/requirements.md` — FR-9 (interfaces block) is
  satisfied here; FR-12 defect 21 shrinks; NFR-1/NFR-2 are inherited. Update
  that doc's cross-references when this lands.
- `docs/design.md` D-39 — governs how this job itself executes (C-5).
- `memory/workflow-pipeline-revival.md` — its "never run end-to-end" caveat
  becomes moot for the deleted parts; update or retire after this lands.

### Open Questions

- Q-1: Does `artisan` remain the GREEN role for tdd items, or does
  `test-driver` own both RED and GREEN as two dispatches of the same agent
  with different instructions? Affects FR-5's agent surface; either satisfies
  the RED/GREEN separation.
- Q-2: `refactor` agent and REFACTOR phase — per slice after GREEN, per
  phase, or dropped in favour of the code-review dispatch flagging refactors?
  Not discussed.

### References

- `plans/pipeline-simplification/recall-artifact.md` — memory entries that
  ground C-1 through C-4 and FR-5.
- `plans/pilfer-superpowers/requirements.md` — parent requirements this
  narrows and partially satisfies.
- `plans/pilfer-superpowers/reports/edify-defects.md` — defect 21 measurement
  context.
- superpowers 5.1.0 `writing-plans`, `executing-plans`,
  `subagent-driven-development` (`~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/`)
  — the target shape; its verbatim-code rule rests on a stated
  zero-context/questionable-taste executor premise (`writing-plans/SKILL.md:10-12`)
  that C-2 does not adopt.
- Kent Beck, "Canon TDD" (2023) — test list first, one test at a time, revise
  the list after each green; the human practice FR-5's slice model adapts.

### Skill Dependencies (for /design)
- Load `plugin-dev:agent-development` before design (agents renamed and
  rewritten in FR-3, FR-5)
- Load `plugin-dev:skill-development` before design (`/runbook`,
  `/orchestrate` rewritten in FR-1, FR-4)
