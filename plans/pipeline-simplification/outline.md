# Outline — pipeline simplification

Requirements: `plans/pipeline-simplification/requirements.md` (FR-1..7, NFR-1..2,
C-1..5, Q-1..2). Recall: `recall-artifact.md`. Inbound-reference map:
`reports/explore-inbound-refs.md` (mechanical `rg`, re-derived at review per C-4).

## Approach

One planning artifact, `plans/<job>/runbook.md`, in today's runbook-outline
shape: phases typed `tdd` / `general` / `inline`, items as prose against named
targets, requirement IDs per item, interface blocks where one item's output is
another's input. `/runbook` produces it, `runbook-corrector` (the renamed
outline corrector) and `runbook-simplifier` gate it, `/proof` validates it,
and it hands off to `/orchestrate`, which reads it and composes every dispatch
prompt live — item text inline, design and recall artifact by path. TDD items
carry behaviour slices; each slice is four dispatches (RED → test review →
GREEN → code review), and after each GREEN the orchestrator may revise the
remaining slices' test lists in `runbook.md` itself. Everything that served
expansion — four scripts, the tier-3 references, `/review-plan`, the old
`runbook-corrector`, both `plugin/docs/` guides, the manifest/step-file
mechanics in `/orchestrate`, the tier vocabulary — is deleted in one pass.

## Key decisions

**D1 — Execution route after `/runbook` is always `/orchestrate`.** `/inline`
never consumes a runbook. Its "Delegated Execution (Tier 2)" section (piecemeal
TDD dispatch, cycle-scoped prompt composition, per-type recall artifacts) is
deleted; when an `/inline` task needs a sub-agent (D-39 self-modifying work
with behavioural code), it composes the dispatch per
`plugin/skills/orchestrate/references/dispatch-composition.md` — the single
source for prompt composition (D4's rules, written there rather than in
`/orchestrate`'s SKILL.md so `/inline` can cite it without loading the
orchestration lifecycle). `plugin/fragments/delegation.md` keeps the
agent-behaviour rules (report-to-file, resume-once, recall by reference) and
loses its step-file dispatch prose to it. *Deviation from the
requirements' presumption* (Out of Scope: "/inline consuming `runbook.md`
instead of `runbook-outline.md`"): what is deleted is only the
`/inline`-consumes-runbook hybrid; the old Tier 2 path per D-34 (ad-hoc
prompts from a design, no runbook) survives as `/inline` +
`dispatch-composition.md`. Runbook-or-not is a design-level decision
(`/design` C.5, D11's D-34 rewire); delegation is an execution-level decision
— the 2×2 is fully covered: no runbook + in-session (`/inline` direct), no
runbook + delegated (`/inline` per `dispatch-composition.md`), runbook +
in-session (orchestrator executes `inline` items itself, D13), runbook +
delegated (`/orchestrate`, D4). Keeping a second runbook consumer is the
duplication FR-1 removes. Tradeoff: a small all-inline
runbook still goes through `/orchestrate`'s lifecycle rather than `/inline`'s.

**D2 — Q-1: `test-driver` owns RED and GREEN as two dispatch modes.** The
prompt names the mode; a prompt without one is a dispatch defect the agent
refuses (stop, report). GREEN mode never edits a test file — the prohibition
sits beside the mode it constrains (D-53) — and reports `blocked: test <id> —
<why>` if a test looks wrong. `artisan` stays the general-item executor with no
TDD protocol. NFR-1's tester/implementer separation survives as a
dispatch-and-context separation, not an agent-file one: RED and GREEN are
distinct dispatches, so the GREEN instance never sees the RED instance's
reasoning about what the tests should assert (`cc-subagent-context-capabilities`
— a child inherits no context), and the test review sits between them.
Requirements Q-1 states either resolution satisfies the RED/GREEN separation.
Rejected: `artisan` as GREEN (adds a TDD mode switch to an agent only tdd items
would use; splits one protocol across two files, so a change to the RED/GREEN
contract has two edit sites). Tradeoff: one agent body carries two protocols;
kept under the 10,000-char cap by cutting the WIP-commit/REFACTOR machinery
(D3).

**D3 — Q-2: `refactor` runs per slice, on signal, after code review.** GREEN
mode's exit is lint + `just precommit` + the slice commit; precommit warnings
go into its report, not into refactoring (refactoring judgement sits with the
code-review corrector, not the implementer). The code-review
corrector applies fix-all; what it cannot fix in scope (module split, new
abstraction) it flags, and the orchestrator dispatches `refactor` before the
next slice's RED so later tests target the refactored shape. `refactor` loses
its "Tier 3: create a runbook, use /orchestrate" tier and its prepare-runbook
regeneration step; it commits its own `refactor:` commit on a clean tree
instead of amending a WIP. Rejected: per-phase (debt accumulates across
slices; each GREEN grows on the pre-refactor shape); dropped entirely (loses
the deslop pass and the opus escalation).

**D4 — Dispatch prompt composition (FR-4).** §1 "Verify Runbook Preparation"
goes: there are no prepared artifacts to check for, and a missing `runbook.md`
fails on the Read; no preflight survives. Per item
the orchestrator writes:
item id + text verbatim (including the interface blocks it consumes and
produces); `Read plans/<job>/design.md` (or `outline.md`) and `Read
plans/<job>/recall-artifact.md, then Read each file it lists`; scope IN (this
item) / OUT (the next items' targets, named); done criteria (`just precommit`
green, clean tree, commit subject); report path under `plans/<job>/reports/`
and the return contract (path or `blocked: <reason>`). Model: type default
(`artisan`/`test-driver` sonnet, `corrector` opus — the reviewer a tier above
the implementers) with the artifact-type
override (opus for skills, fragments, agents, `docs/design.md`; D-42) applied
by the orchestrator, and an optional `Model:` line on an item overriding both.
Every dispatch gets a `name` (`item-N-M`, `item-N-M-s<k>-red`, …) — resumption
is `SendMessage` to that name (`cc-subagent-approval`); a child's reply is the
only authoritative result (`cc-async-task-notification-quirks`). Deviation:
the orchestrator re-composes the next prompt from what the last report said;
list revisions are edits to `runbook.md` the orchestrator commits after the
slice, so
plan-as-executed vs plan-as-written is a `git diff` (one of FR-5's three
dogfood counts comes free). Tradeoff: the orchestrator's context carries the
whole runbook and design — C-1 accepts this; an overflow is a runbook too large.

**Run summary.** The orchestrator's own closing message, in context, not a
file: per item its dispatches (`item-N-M-s<k>-red`, …), each report path, each
remediation RCA, and the `/deliverable-review` follow-up. `/handoff:handoff`
carries it into the task frame. It is what supplies FR-5's remaining two
dogfood counts — dispatches per item, and wrong-reason tests the test review
caught (the count; the instances are in the review reports). This replaces
`progress-tracking.md` (D10) and the step-numbered progress log.

**D5 — Per-slice sequence and its gates (FR-5).** Slice `N.M/k`: (a) RED —
`test-driver` RED mode: for k=1 stub the SUT importable-but-inert, write the
slice's tests, run, every test fails on its assertion; for k>1 do not touch
the SUT. No commit — the tests stay uncommitted in the tree; report carries
the per-test output, then stop — RED mode writes no implementation and the
dispatch ends there (FR-5 acceptance 1). (b) Test review — `corrector` (opus),
scope IN = this slice's tests
+ the RED report; first check is mechanical (every listed test FAILED on an
assertion, none PASSED or ERROR), then wrong-reason hunting against the
vacuous-green catalogue written into the corrector's own criteria (agent and
skill text never references memory files); fix-all on tests, re-run to
confirm still red.
(c) GREEN — `test-driver` GREEN mode: one test at a time, full suite at the
end; one GREEN commit per slice, `<type>: Item N.M/k — <title>` with the type
the executor's choice (`feat`, `fix`, `docs`, `perf`, `test`, `build`, `chore`
all legitimate — a slice that pins an error path is not a feature), carrying
tests + implementation with the suite green — no commit ever leaves the suite red.
Nothing keys on the type: the gitmoji `commit-msg` hook rewrites the prefix to
an emoji before the commit is written, so the `Item N.M/k` marker, which the
hook preserves, is the only thing an auditor may match in a subject. A
reviewed slice carries two commits with that marker — this one and the
orchestrator's commit of (d)'s fixes.
(d) Code review — `corrector` (opus), scope IN = implementation files; may
run the slice's tests once against an in-place mutated SUT (save, mutate,
run, restore — never relocate the tests) and report whether they redded. The
corrector applies fix-all and never commits; the orchestrator commits its
fixes, the same step it takes at a phase boundary.
After (c), after the orchestrator's commit of (d)'s fixes, and after any
general item — not after (a)/(b), where uncommitted
tests are the designed state: `verify-step.sh` — clean tree (tolerating the
resting ` M memory`), precommit; exit 1 → resume the named agent once, then a
fresh `artisan` recovery, then escalate. This is the caller D6 keeps.
Then: `refactor` if (d) flagged; then the list-revision step (edit remaining
slices in `runbook.md`, or record "List revision: none"). Phase boundary:
`corrector` checkpoint as today. Completion: final review if single-phase,
`tdd-auditor` if any tdd item (D14), `/deliverable-review` follow-up named.

**D6 — `verify-red.sh` is deleted; `verify-step.sh` stays, rewritten.**
`verify-step.sh` keeps its caller, placed explicitly in D5's post-slice gate —
FR-4 keeps it
only on that condition, and `/orchestrate` is rewritten wholesale, so the call
site is a thing the rewrite must add, not a thing it inherits. The rewrite
drops its submodule pointer-sync check — an agent-core-era plugin enforcement;
the `memory/` submodule needs no pointer sync, and gating on it would block
unattended execution behind gitlore's per-commit approval — and makes the
clean-tree check tolerate the resting ` M memory` while any other dirty path
still fails.
`verify-red.sh` asserts only "the file's run exits non-zero", which slice ≥2
satisfies vacuously (slice-1 tests now pass) and which cannot tell PASSED
from ERROR per test; making it check per-test ids is a new script with
behaviour and no tests — NFR-1 already states deterministic validation does
not survive, and D-51 says fail or do not check. The per-test red check moves
to the test reviewer's first step (D5b). *Reopen-if:* the dogfood shows the
reviewer missing a PASSED/ERROR line in RED output.

**D7 — Runbook item format (FR-1, FR-5, FR-6) — binding.** Header
`## Phase N: <title> (type: tdd|general|inline)`; items `- Item N.M: <target
path> — <concrete action>. Requirements: FR-x[, …]. Depends on: Item N.K`
(optional) `Model: opus` (optional). tdd items add `Slices:` — a numbered
list, slice 1 the external contract with the degenerate or naive happy path,
each later slice one behaviour — each slice naming its tests in prose with
the assertion stated (`test_parse_empty_returns_empty_list` — asserts `[]`
for `""`), specific enough that two executors would write the same test.
Any item whose output another item consumes adds `Interfaces:` — one
line per method/dataclass/exception/file contract with full signature and
return type. No code blocks anywhere in an item; the negative rules sit
beside the format (D-53). Format lives in
`plugin/skills/runbook/references/runbook-format.md` with one short example;
`tdd-cycle-planning.md`'s assertion-quality table and integration-first
ordering are rewritten into it, not kept.

**D8 — `/runbook` process (FR-1).** One path: recall + discovery (today's
Phase 0.5), write `runbook.md`, self-check (today's Phase 0.75 step 2 list
minus "≤8 items" — kept as a split signal, not a count gate), commit,
`runbook-corrector`, consolidation + `runbook-simplifier`, `/proof`, then
§Continuation prepending nothing — `/orchestrate` runs in a fresh session via
`/handoff:handoff` (D-25 kept on context-budget grounds; the model-tier
ground is dropped with the weak orchestrator). SKILL.md holds the process
(≤2,000 words); tier assessment, model-assignment tables, the two-tier
section and every `tier3-*` reference go.

**D9 — `runbook-corrector` (FR-3, FR-6) — criteria in/out.** Keep:
requirements coverage, design alignment, phase structure, complexity
distribution, dependency sanity, vacuity, intra-phase ordering, density,
semantic propagation, deliverable-level traceability, step clarity,
execution readiness. Drop: §5.5 expansion guidance and every "note in
Expansion Guidance" fix (the fix is applied to the runbook directly),
checkpoint-spacing (phase-boundary correctors are the checkpoints; ">8 items"
becomes a phase-split signal). Keep growth projection — dropping only its
*split-recommendation wording* would contradict D-69, which requires runbook
planning to project file growth and insert split points rather than react per
slice; the projection stays, its output becomes a phase-split signal like the
item count.
Add: code block in an item → violation (rewrite as prose/interface block);
cross-item dependency with no `Interfaces:` block → gap (add it if derivable
from the design, else UNFIXABLE); crammed or return-type-elided contract →
violation (un-cram); tdd item without slices, slice 1 not the contract, or a
test an executor could write two ways → violation. The keep-list absorbs
`/review-plan`'s live criteria (it was the old corrector's review protocol):
its prescriptive-code and sequencing checks become the code-block and slice
rules above; its prerequisite-validation and script-evaluation checks die
with expansion — there are no expanded steps to validate — stated here so the
deletion is a disposition, not an omission. Report:
`plans/<job>/reports/runbook-review.md` (from `runbook-outline-review.md`).
Model stays opus (D-32). `runbook-simplifier`: input `runbook.md`, "before
`/proof`" framing, and its frontmatter `description:` loses "after Phase 0.85"
— a description is injected every session, so a stale one costs context in
every session, not only when the agent runs
(`skill-description-purpose-first`). Same check on `runbook-corrector`'s
description after the rename.

**D10 — Deletion set (FR-2), re-derived by `rg` at review (C-4).** Scripts:
`plugin/bin/prepare-runbook.py`, `validate-runbook.py`,
`assemble-runbook.py`, `plugin/scripts/split-execution-plan.py`,
`plugin/skills/orchestrate/scripts/verify-red.sh`; tests:
`tests/test_validate_runbook_reporting.py`,
`tests/fixtures/validate_runbook_fixtures.py`; skill:
`plugin/skills/review-plan/` whole; agent: `plugin/agents/runbook-corrector.md`
(old); references: all ten under `plugin/skills/runbook/references/`
(`conformance-validation.md`'s one rule — validation items with exact
expected strings when the design cites an external reference — moves into
`runbook-format.md`; `anti-patterns.md`'s surviving rows — setup-only,
god, presentation, weak-assertion, split-prose, unit-only, mocked-subprocess
— are rewritten there as item-level rules); docs: `plugin/docs/` whole;
`plugin/skills/orchestrate/references/progress-tracking.md` (step-numbered
progress file; the run summary replaces it) and `common-scenarios.md`
(rewritten inline as the orchestrator's escalation rules).

**Deletion timing.** A file whose content migrates is deleted by the task that
performs the migration, not by task 1: `tdd-cycle-planning.md`,
`conformance-validation.md` and `anti-patterns.md` by task 3 (into
`runbook-format.md`), orchestrate's `common-scenarios.md` by task 4, and
`tier3-planning-process.md` + `tier3-outline-process.md` by task 3 (D8's
one-path process is assembled from their Phase 0.5 discovery steps and Phase
0.75 self-check list — those phases live in these two files, not in
`runbook/SKILL.md`). Task 1 deletes only the files with no surviving content.
Recovering migrated text from `git show` after a premature delete works but is
an avoidable failure mode, and a task that finds its source already gone will
reconstruct it from memory.

Vocabulary removed everywhere: `Tier 1/2/3`, cycle, step file,
`orchestrator-plan`, `common-context`, `runbook-outline`, `runbook-phase`,
"every 3-5 cycles"; and `manifest` **only in its orchestrator sense** — the
plugin/marketplace manifest is a live unrelated term in
`plugin/.claude-plugin/plugin.json`, `scripts/release.sh`,
`docs/marketplace.md`, `docs/design.md:232` and `package-lock.json`, so the
sweep greps `orchestrator manifest`/`step artifacts and an orchestrator
manifest`, never bare `manifest`.

Sites the `rg` map (`reports/explore-inbound-refs.md`) adds beyond the
requirements' lists: `plugin/skills/requirements/SKILL.md:252` (tier route to
`/runbook`), `plugin/fragments/continuation-passing.md:97-98` (tier notes),
`plugin/agents/design-corrector.md:65,144` and `corrector.md:119-121,294`
(wrong-agent redirects and "steps/cycles" wording),
`plugin/skills/review/references/{example-execution,review-axes}.md`,
`agents/learnings.md:41,126` (undated log — reword the two lines, do not
restructure).

Sites the review's own `rg` adds beyond both (C-4 — the lists above are claims
about the corpus, `spec-enumerations-need-rederiving`):

- `CLAUDE.md` is four regions, not one: `:57` (generator example), `:178`
  (pipeline line naming Tier 3 / Tier 1-2 and `review-plan`), `:183-184`
  (backing scripts + `plugin/docs/`), `:187-190` (delegation-by-step-file
  paragraph).
- `plugin/agents/outline-corrector.md:143` — its cross-component interface
  example is `runbook-phase-*.md`. The requirements put `outline-corrector`
  out of scope as *unchanged*; FR-2's acceptance (`rg` returns nothing) makes
  this one line an exception. Reword the example, change nothing else.
- `plugin/skills/design/references/design-content-rules.md:41` (its
  naming-mismatch example is `outline-corrector` vs
  `runbook-outline-corrector` — pick a live pair), `:95` (integration-first
  ordering "defined in `/runbook` skill" → `runbook-format.md`), `:127`
  (§6.4 pointer).
- `plugin/skills/design/SKILL.md:163` — cites the transformation table as
  "T1-T6.5"; D11 renumbers to T1–T5.
- `plugin/skills/proof/references/item-review.md:14` — phased-plan markers
  `## Cycle` / `## Step` become `## Phase` / `Item`.
- `.claude/rules/workflow-work.md` — points at `docs/design.md` §6.4/§6.5 by
  title with "Key areas: Oneshot workflow pattern, TDD workflow integration,
  runbook structure"; repoint after D11.

Sweep exclusions, stated against FR-2's literal wording: `docs/changelog.md`
and the dated files under `docs/superpowers/` are write-time records
(`design-doc-writing`) and keep their references; `plans/` and `memory/`
bodies other than `workflow-pipeline-revival.md` are out of the sweep;
`.claude/handoff-task.md` and `handoff-todo.md` are session state, rewritten
by their own tooling, not swept.

**D11 — `docs/design.md` rewire (FR-7).** §1 Now (a status layer, not a task
queue: one-stage runbook landed, dogfood pending as validation status;
do-not-re-litigate → session boundary D-25, publication
D-9, one-stage runbook with C-1's grounds); §3.2 rows FR-9/10/11/12 reworded
(FR-11 names "Tier 1/2"), FR-19/20 removed (gaps stay — FR IDs are cited,
never renumbered); §5.3 rewritten; D-24 (mechanism → composed prompts,
principle survives), D-25
(tier clause dropped), D-26 table renumbered T1 requirements→design, T2
design→runbook (`runbook-corrector`), T3 runbook→simplified, T4
runbook→implementation (`corrector` per slice + phase boundary), T5
design/outline→implementation (inline); D-30 (type determines item format,
review criteria, dispatch); D-31 → superseding pointer (one level now; its
grounding incident moves to §7 as the reason expansion re-introduced
defects); D-32 keeps its 2×2 experiment and its opus verdict, loses its
"Paired fix: expansion guidance references design sections" clause — the
paired fix is now D7's prose-plus-interfaces rule; D-33 keeps its
consolidate-early principle, loses its expansion economics ("expanded
RED/GREEN detail", "the expansion cost", the ~12-item post-hoc figure) and
becomes consolidation before `/proof` — not a trivial rewire; D-34 → two
routes (`/inline` in-session vs `/orchestrate` by dispatch), boundary =
whether a runbook exists, decided at `/design` C.5; D-35 "tier" → "route";
D-39 "per cycle" → "per slice"; D-49 example → `verify-step.sh` vs
`corrector`; D-69's closing line "project file growth … rather than react per
cycle" → "per slice" (D9 keeps the projection); §6.3's "review checkpoints
instead of RED/GREEN cycles" → "instead of a slice of its own"; L-1 deleted;
L-2 → routing thresholds still ungrounded, tier numbers and "3-5 cycles"
removed; L-6
reworded; §7 adds: two-stage runbook for a weak orchestrator (C-1), per-test
dispatch (C-2), whole-task batching without a separate RED
(`green-is-not-evidence`), a deterministic runbook validator with nothing
downstream (D-51); `docs/changelog.md` entry dated at landing.

D-26's T-numbers are renumbered rather than gapped, unlike the FR IDs above:
they are positional row labels in one table, not cited identifiers — with one
exception, `plugin/skills/design/SKILL.md:163` ("the transformation table
(T1-T6.5 …)"), which the same pass repoints to T1–T5.
`.claude/rules/workflow-work.md` cites §6.4/§6.5 by title; both titles
survive, its "runbook structure" key-area line does not.

**D13 — General and inline items (FR-1's other two types).** A `general` item
is one dispatch composed per D4 (`artisan`, or `corrector` where the item is a
review), then `verify-step.sh`, then the phase-boundary `corrector`. An
`inline` item the orchestrator executes itself — Read, Edit, `just precommit`,
commit — with no dispatch, and its review follows the proportionality rule in
`plugin/fragments/review-requirement.md`: self-review by `git diff` only when
every one of that fragment's conditions holds, else a `corrector` dispatch.
This is today's §3.0 kept whole; it is the one path where the orchestrator
would review its own edits, so the threshold stays the fragment's rather than
the orchestrator's judgement. Unchanged by this job except for the vocabulary
(phase → item) and the artifact it reads (`runbook.md`, not the orchestrator
plan's `## Phase Files` section).

**D14 — `tdd-auditor` criteria (FR-5 acceptance 4).** Rewritten against
reports and slice diffs rather than planned-vs-executed cycle counts: per
slice, the RED report shows every test failing on its assertion and the test
review confirms still-red; exactly one GREEN commit per slice
(`<type>: Item N.M/k — <title>`) carries both tests and implementation — no
commit leaves the suite red — plus the orchestrator's review-fix commit where
the code review changed anything; and GREEN modified no reviewed test —
auditable by diffing the GREEN commit's test files against the RED report's
test list. The auditor keys on the hash the GREEN report names; that report
also records the tests run and the one-at-a-time sequence, with
the session's `subagents/` transcripts as the fallback where a report is
missing, and git only confirms the named commit and diffs it. The commit type
is the executor's choice and the auditor never keys on it — `Item N.M/k` is the
only subject content it may match. D5's report convention and that marker
exist to make these checks mechanical. The
REFACTOR-mandatory-per-cycle check goes (D3 makes refactor conditional);
"planned cycles completed" goes (the list is revised during execution by
design, so plan-vs-execution divergence is expected — the `runbook.md` diff
records it, D4). This is the detector FR-5 names for its known unvalidated
risk: an implementer seeing a whole slice's tests takes implementation
shortcuts. Unvalidated — the pre-teardown observation is roughly six months
old at an unrecorded model tier (NFR-2), and the dogfood run is the first
measurement.

**D15 — Measurement (NFR-2).** Task 0 records `wc -l` and `edify tokens`
over the deletion set and the rewrite set; the last task records the same
after. If the token API is unreachable from the sandbox, report bytes and say
so. Slice-batching cost and test-review catch rate are labelled unvalidated
in every place they are claimed until the dogfood run.

## Execution shape (C-5)

Inline task sequence on `main`, `/inline plans/pipeline-simplification
execute` after design `/proof`. Each task Reads its targets fresh before
editing and never invokes `/runbook`, `/orchestrate` or their agents (the SUT).
Order: 0 baseline measurement → 1 delete the no-surviving-content set
(D10: four scripts, `verify-red.sh`, the two tests, `review-plan/`, the old
`runbook-corrector.md`, `plugin/docs/`, `progress-tracking.md`, the seven
non-migrating `runbook/references/`) + `just precommit` → 2 rename/reframe
correctors (D9) → 3 `/runbook` rewrite (D7, D8), writing `runbook-format.md`
from `tdd-cycle-planning.md`, `conformance-validation.md`, `anti-patterns.md`,
`tier3-planning-process.md` and `tier3-outline-process.md`, then deleting those
five → 4 `/orchestrate` rewrite (D4, D5, D6, D13) +
`dispatch-composition.md`, folding orchestrate's `common-scenarios.md` in and
deleting it → 5 agents (`test-driver`, `artisan`, `refactor`, `tdd-auditor`
(D14), `corrector` markers) → 6 `/inline` trim (D1), `/design` consumers
(`SKILL.md:163`, `design-content-rules.md`) + coupling table,
`proof/references/item-review.md`, `outline-corrector.md:143`, fragments
(`delegation`, `workflows-terminology`, `execution-routing`,
`escalation-acceptance`) → 7 `docs/design.md` + changelog (D11),
`.claude/rules/workflow-work.md`, `README.md`, `plugin/README.md`, `CLAUDE.md`
(four regions), `plans/pilfer-superpowers/requirements.md` cross-refs,
`memory/workflow-pipeline-revival.md` → 8 sweep (`rg` every removed name and
the tier vocabulary, `manifest` scoped per D10; `just precommit`;
after-measurement) → 9 review dispatch per artifact group,
`/deliverable-review` follow-up.

Tasks 3 and 4 delete their own sources after migrating them; task 1 must not
(D10 Deletion timing).

## NFR-1 verdict

All five distinguishers survive, so the "use superpowers directly" outcome is
not reached:

- **Artifact traceability** — requirement IDs per item (D7), design and recall
  artifact named by path in every dispatch (D4).
- **Pinned model tiers per agent** — type default plus artifact-type override
  plus per-item `Model:` (D4); D-42 and D-32's opus verdicts kept (D9, D11).
- **`/proof` human gate on planning artifacts** — kept on `runbook.md` (D8);
  it moves from pre-expansion to terminal, which strengthens it (the gated
  artifact is now the one execution reads).
- **Fix-all correctors at every remaining gate (D-27)** — `runbook-corrector`
  (D9), test review and code review per slice, phase boundary (D5).
- **Tester/implementer separation** — survives as a dispatch-and-context
  separation rather than an agent-file one; see D2.

Not surviving, per NFR-1's own statement: deterministic validation
(`validate-runbook.py`, D-51). Recorded in §7 by D11.

## Open questions

None — Q-1 and Q-2 resolved by D2 and D3. The two places the design went
beyond or against the requirements' wording were settled at `/proof`
(2026-09-01): D1's deviation accepted, the D12 branch gate struck.

## Scope

IN: everything in D1–D11 and D13–D15 (D12 struck at `/proof`). OUT (per
requirements): design-outline stage and
`outline-corrector`; `/inline`'s lifecycle beyond D1; corrector-skeleton
compression (pilfer defect 21); pilfer Q-1; the dogfood run; memory
consolidation.
