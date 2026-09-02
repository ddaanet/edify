# Deliverable Review (Layer 1, agentic prose): pipeline-simplification

**Date:** 2026-09-02
**Range:** f3f1015b..HEAD
**Baseline:** `plans/pipeline-simplification/requirements.md` (FR-1..7, NFR-1..2,
C-1..5), `plans/pipeline-simplification/outline.md` (D1–D11, D13–D15)

## Inventory

| File | Lines | Type | Review scope |
|---|---|---|---|
| plugin/skills/runbook/SKILL.md | 151 | agentic prose | whole file |
| plugin/skills/runbook/references/runbook-format.md | 121 | agentic prose | whole file |
| plugin/skills/orchestrate/SKILL.md | 181 | agentic prose | whole file |
| plugin/skills/orchestrate/references/dispatch-composition.md | 58 | agentic prose | whole file |
| plugin/skills/orchestrate/scripts/verify-step.sh | 19 | code | universal + robustness, idempotency, error signaling |
| plugin/agents/test-driver.md | 101 | agentic prose | whole file |
| plugin/agents/tdd-auditor.md | 155 | agentic prose | whole file |
| plugin/agents/runbook-corrector.md | 214 | agentic prose | whole file |
| plugin/agents/runbook-simplifier.md | 163 | agentic prose | whole file |
| plugin/agents/refactor.md | 190 | agentic prose | whole file |
| plugin/agents/artisan.md | 122 | agentic prose | whole file |
| plugin/agents/corrector.md | 595 | agentic prose | changed regions + runbook/step/cycle/tier prose |
| plugin/skills/inline/SKILL.md | 165 | agentic prose | whole file |
| plugin/skills/inline/references/review-dispatch-template.md | 82 | agentic prose | whole file |
| plugin/skills/design/SKILL.md | 186 | agentic prose | changed regions |
| plugin/skills/design/references/design-content-rules.md | 151 | agentic prose | changed regions |
| plugin/skills/proof/references/item-review.md | 78 | agentic prose | changed lines |
| plugin/skills/requirements/SKILL.md | 296 | agentic prose | changed lines |
| plugin/skills/review/references/example-execution.md | 52 | agentic prose | changed lines |
| plugin/skills/review/references/review-axes.md | 65 | agentic prose | changed lines |
| plugin/agents/design-corrector.md | 394 | agentic prose | changed lines |
| plugin/agents/outline-corrector.md | 388 | agentic prose | changed lines |

## Critical Findings

**C-1. The per-slice code review leaves an uncommitted tree that the next gate
reads as failure.** `plugin/skills/orchestrate/SKILL.md:96-98` runs
`verify-step.sh` "After GREEN (c), code review (d), and any general item";
`plugin/skills/orchestrate/scripts/verify-step.sh:6-11` exits 1 on any dirty
path. Dispatch (d) is `edify:corrector` under the fix-all policy (D-27), and
nothing in `plugin/agents/corrector.md` instructs it to commit — the word
"commit" appears there only in report-template and scope prose
(`corrector.md:174,261,389`), never as an action. So whenever the code review
fixes anything, which is its designed normal outcome, the very next step is
`DIRTY: uncommitted changes` → the remediation branch at
`plugin/skills/orchestrate/SKILL.md:105-111` ("resume the named agent once …
then a fresh `edify:artisan` … note the RCA follow-up"). **Design ids:** D5
(post-slice gate), D6 (`verify-step.sh` is the caller D6 keeps), D-27.
**Impact:** every slice whose code review applied a fix is routed through
recovery and logged as a remediation RCA in the run summary, so the run
summary's RCA count — one of the three dogfood counts D4 relies on — measures
the missing commit step rather than execution defects. Fix by giving the code
review a commit contract (`fix:` commit on its own, or "return with the tree
committed") or by moving the gate after a commit step.

## Major Findings

**M-1. `refactor` commits nothing it changed.**
`plugin/agents/refactor.md:150-155`: "You start from a clean tree … Commit the
refactoring as its own commit: `git commit -m "refactor: <what changed>"`".
The refactoring edits are unstaged at that point and there is no `git add`, so
the literal command exits non-zero with "no changes added to commit".
**Design id:** D3 ("commits its own `refactor:` commit on a clean tree").
**Impact:** the prescribed command fails; the agent must improvise the staging
step the instruction omits.

**M-2. `tdd-auditor`'s commit-subject checks cannot match this repo's
commits.** `plugin/agents/tdd-auditor.md:57` requires "Exactly one `feat: Item
N.M/k — <title>` commit" and `:72` a "separate `refactor:` commit". Edify's
`commit-msg` hook (`.git/hooks/gitmoji.sh:53-66`) rewrites a conventional
prefix into an emoji before the commit is written, so `feat: Item 2.1/1 — x`
is stored as `✨ Item 2.1/1 — x`. `git log` on this branch confirms it
(`✨`, `♻️`, `📝` subjects, no `feat:` anywhere). **Design ids:** D5 (commit
subject), D14 ("D5's report and commit-subject conventions exist to make these
checks mechanical"). **Impact:** run in edify — the repo the dogfood run
targets — the audit reports check 2 and check 4 as violated for every
compliant slice. The check needs to match the post-hook subject, or the
convention needs a marker the hook preserves.

**M-3. `refactor` Step 5 tells a mid-execution agent to rewrite the plan
directory.** `plugin/agents/refactor.md:131-135`: "Plans directory - All
designs and runbooks … Update any references found." `refactor` now runs
inside the slice loop (D3), where `runbook.md` is the orchestrator's own
artifact: D4 makes list revisions "edits to `runbook.md` the orchestrator
commits after the slice", and `plugin/agents/corrector.md:300-304` classifies
an item mutating its own plan directory as a MAJOR issue. **Design ids:** D3,
D4. **Impact:** two writers on `runbook.md` inside one slice, and the
orchestrator's plan-as-executed `git diff` picks up the refactor agent's
edits. Step 5's plans-directory sweep belongs to a standalone refactor, not to
the per-slice dispatch.

**M-4. The `escalated:` return has no consumer.**
`plugin/agents/refactor.md:29-30` promises a handler ("Architectural … |
Opus | Escalate for design"), and `:54-56`/`:88-92` return
`escalated: <reason and scope>` and stop. The only receiver,
`plugin/skills/orchestrate/SKILL.md:88-89`, says "On `escalated` → note the
opus follow-up in the run summary". No artifact dispatches an opus refactor.
**Design id:** D3, which kept `refactor` partly because dropping it "loses the
deslop pass and the opus escalation". **Impact:** an architectural refactoring
is recorded and never performed, and the escalation table's Handler column
names a handler that does not exist. Either name the opus dispatch in
`/orchestrate` or state in `refactor.md` that escalation is a report, not a
handoff.

**M-5. `runbook-simplifier` reads only `design.md`.**
`plugin/agents/runbook-simplifier.md:50-51` reads `plans/<job>/design.md`
unconditionally. Every sibling artifact accepts either name —
`plugin/skills/runbook/SKILL.md:29-31` ("`outline.md` or `design.md`"),
`plugin/agents/runbook-corrector.md:40`,
`plugin/skills/orchestrate/SKILL.md:24`,
`dispatch-composition.md:15`. This very plan has `outline.md` and no
`design.md` (`ls plans/pipeline-simplification/`). **Design id:** D9 (input
`runbook.md`, gate before `/proof`). **Impact:** the mandatory consolidation
gate loses its requirements context on any outline-only plan.

**M-6. `/inline`'s review routing sends outlines and designs to
`runbook-corrector`.**
`plugin/skills/inline/references/review-dispatch-template.md:47`: "Planning
artifacts (runbooks, outlines, designs) route to runbook-corrector per
pipeline contracts", echoed at `plugin/skills/inline/SKILL.md:123` ("Planning
artifacts → runbook-corrector"). The routing table in
`plugin/fragments/review-requirement.md:37-42` sends design documents to
`edify:design-corrector`, `outline-corrector.md` exists and owns outlines, and
`plugin/agents/runbook-corrector.md:42-51` rejects anything that is not
`runbook.md` with "Error: Wrong artifact type". **Design ids:** D-26 T1/T2,
D1. **Impact:** a design or outline dispatched from `/inline` Phase 4a returns
a rejection instead of a review.

**M-7. GREEN mode never runs `just precommit`.**
`plugin/agents/test-driver.md:54` ends the run at "Full suite at the end, plus
`just lint`", then `:56-58` says "**Precommit warnings go into the report**" —
warnings from a command the mode never invokes. **Design id:** D3 ("GREEN
mode's exit is lint + `just precommit` + the slice commit"). **Impact:** the
design-specified exit gate is missing from the agent body; it survives only as
a done criterion in the dispatch prompt (`dispatch-composition.md:19-21`), and
step 4 is unreachable as written.

## Minor Findings

**Vocabulary sweep residue** (my own `rg` over `plugin/`, per C-4 — the only
`Tier`, `step file`, `orchestrator-plan`, `common-context`, `runbook-outline`,
`runbook-phase`, `3-5 cycles` and orchestrator-`manifest` hits are zero; these
are `step`/`cycle` in the retired sense):

- `plugin/agents/corrector.md:301` — "Flag any **step** containing
  file-mutating commands", while `:303-304` in the same bullet group were
  converted to "items" and the identical line in
  `plugin/skills/review/references/review-axes.md:38` reads "item".
- `plugin/agents/corrector.md:156` — "Scope IN: What was implemented in this
  step/phase".
- `plugin/agents/tdd-auditor.md:33` — "not from a planned-vs-executed **cycle**
  count" names a concept the reader no longer has; the sentence works as "not
  from planned-versus-executed counts".

**Consistency and determinism:**

- `dispatch-composition.md:22` fixes the report path as
  `plans/<job>/reports/<dispatch name>.md`, contradicted by every named
  consumer: `orchestrate/SKILL.md:126` (`checkpoint-P-review.md` for a
  `phase-P-corrector` dispatch), `:159` (`review.md`), `:161`
  (`tdd-process-review.md`). Two rules for one field.
- `plugin/agents/tdd-auditor.md:148` — "Unclear commit range: **ask the
  caller** for the range" is not an available act for a one-shot sub-agent;
  `plugin/fragments/delegation.md:30-33` fixes the return to a filepath or an
  error. Should be `blocked: unclear commit range`.

**Frontmatter:**

- `plugin/skills/runbook/SKILL.md:7` — `allowed-tools` still carries
  `echo:*|pbcopy`; neither `echo` nor `pbcopy` appears in the body. `mkdir:*`
  likewise has no call site. `rg:*`, `git:*`, `Agent`, `Read`, `Write`,
  `Edit`, `Skill` all match real uses.
- `plugin/skills/orchestrate/SKILL.md:1-8` has no `allowed-tools` at all,
  unlike its two sibling lifecycle skills; the body uses Agent, Read, Edit,
  Bash, SendMessage and TaskOutput.
- Descriptions are purpose-first and free of stale stage names across all
  reviewed agents and skills, including the two D9 calls out
  (`runbook-simplifier.md:4` now reads "before `/proof`";
  `runbook-corrector.md:4` after the rename). Tool lists otherwise match body
  usage: `artisan.md:6` correctly dropped `Skill`, `tdd-auditor.md:26`
  correctly omits `Edit`.

**Ungrounded thresholds** (`runbook-corrector.md:99` and `:78` label theirs
"*(ungrounded — needs calibration)*"; these two do not):

- `plugin/agents/runbook-simplifier.md:87` — "Keep consolidated items ≤8
  assertions".
- `plugin/agents/runbook-simplifier.md:154` — "If the runbook has ≤10 items,
  report 'no consolidation candidates'".

**Excess / stale text:**

- `plugin/agents/refactor.md:187-190` — trailing `**Created:** 2026-01-30` /
  `**Purpose:**` metadata footer duplicating the Role section.
- `plugin/agents/artisan.md:65` — "Use **Bash `rg`** instead of `grep` or `rg`
  commands" instructs the reader to replace `rg` with `rg`.

**verify-step.sh (code axes):** robustness, idempotency and error signaling
are sound. Both failure paths print a labelled marker and exit 1
(`:8-10`, `:14-15`), success prints `CLEAN` and exits 0; the script is
read-only, so re-running is safe. The `|| true` at `:6` is the sanctioned
grep-found-nothing case per CLAUDE.md, and it correctly yields an empty
`status` when ` M memory` is the only entry. Two observations, neither a
defect: `set -x` with `exec 2>&1` means the trace interleaves with the
markers on stdout, and the script assumes the repo root as cwd for
`just precommit`.

**Axes with nothing to report:** vacuity — every reviewed artifact does real
work; no ceremony steps found. Scope boundaries — IN/OUT is specified
everywhere it is dispatched (`dispatch-composition.md:16-18`,
`orchestrate/SKILL.md:66,77,123-127`, `corrector.md:311,347`).

## Design conformance

| Design / requirement | Status | Reference |
|---|---|---|
| D1 — `/inline` never consumes a runbook; delegation via dispatch-composition | covered | `inline/SKILL.md:18,85` |
| D2 — test-driver RED/GREEN modes, refuses no-mode, GREEN never edits a test, `blocked: test <id> — <why>` | covered | `test-driver.md:13-16,25-42,48-50,68-73` |
| D3 — refactor per slice on signal after code review; own `refactor:` commit on a clean tree; no tier-3/prepare-runbook text | partial | covered at `refactor.md:13,148-158`; M-1 (no staging), M-3 (plans sweep), M-4 (escalation), M-7 (GREEN exit) |
| D4 — dispatch composition: item text verbatim, design + recall by path, scope IN/OUT, done criteria, report path, return contract, model default/override/`Model:`, `name` scheme, SendMessage resumption; run summary as closing message | covered | `dispatch-composition.md:11-51`; `orchestrate/SKILL.md:162-167` |
| D5 — RED → test review → GREEN → code review; verify-step after (c)/(d)/general; refactor on signal; list revision; `feat: Item N.M/k — <title>` | partial | `orchestrate/SKILL.md:57-93,96-102`; C-1 (gate fails on the corrector's fixes), M-2 (subject not matchable) |
| D6 — verify-step tolerates ` M memory`, fails other dirty paths, no submodule pointer check | covered | `verify-step.sh:5-11`; submodule block removed in the range |
| D7 — runbook format: phase header, item line, Slices, Interfaces, no code blocks, assertion quality, integration-first, conformance validation, surviving anti-pattern rows | covered | `runbook-format.md:13-26,28-43,66-121` (all seven anti-pattern rows present) |
| D8 — `/runbook` one path, SKILL.md ≤ 2,000 words | covered | `runbook/SKILL.md:47-151`; `wc -w` = 905 |
| D9 — runbook-corrector keep/drop/add lists; report at `reports/runbook-review.md`; simplifier description without "after Phase 0.85" | partial | `runbook-corrector.md:62-133,145`; `runbook-simplifier.md:4`; M-5 (simplifier design path) |
| D13 — general items per D4; inline items executed by the orchestrator with review proportionality | covered | `orchestrate/SKILL.md:37-53` |
| D14 — tdd-auditor per-slice criteria | partial | `tdd-auditor.md:49-72`; M-2 defeats checks 2 and 4 in this repo |
| Vocabulary sweep (`Tier 1/2/3`, cycle, step file, orchestrator-plan, common-context, runbook-outline, runbook-phase, "every 3-5 cycles", orchestrator-sense manifest) | covered | own `rg` over `plugin/`: zero hits; residual `step`/`cycle` prose in Minor findings; `plugin/README.md:68` `manifest` is the plugin-manifest sense allowed by D10 |
| FR-1 — one runbook stage, terminal artifact | covered | `runbook-format.md:3-6`; `runbook/SKILL.md:23` |
| FR-4 — orchestrator composes prompts, no preflight | covered | `orchestrate/SKILL.md:15-18,27` |
| FR-5 — slice-batched TDD, RED separate from GREEN | partial | see D5 |
| FR-6 — prose plus interfaces, never code | covered | `runbook-format.md:66-71`; `runbook-corrector.md:123-126` |
| NFR-1 — tester/implementer separation, pinned tiers, `/proof` gate, fix-all correctors, traceability | covered | `test-driver.md:13`; `dispatch-composition.md:33-40`; `runbook/SKILL.md:140-143`; `runbook-format.md:21-22` |

## Summary

| Severity | Count |
|---|---|
| Critical | 1 |
| Major | 7 |
| Minor | 12 |
