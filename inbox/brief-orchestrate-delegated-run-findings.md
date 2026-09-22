## Brief: skipped dispatches, under-powered mutation gates, and the orchestrating layer

2026-09-20

Arrived from the `claude-plugin-dev` repo, which ran `/edify:orchestrate` over
`plans/2026-09-18-deliverable-review-fixes/runbook.md` — four phases, 40
commits, six TDD slices in Phase 1 and `general` items after. This note ends
that repo's involvement; nothing is tracked there.

Two inbox briefs overlap and are not repeated:
`brief-orchestrate-context-cost-and-tdd-process.md` and
`brief-corrector-scope-and-escalation-resume.md`; where this run bears on one of
their points it is flagged as field evidence. Sections are named, not
line-numbered; points were checked against `plugin/skills/build/`,
`plugin/agents/` and `plugin/fragments/` as they stand.

### Recommendations from the run's TDD audit

Source: `reports/tdd-audit.md`. All four target the execution skill.

1. **A skipped dispatch should leave an artifact.** Three Phase 1 code reviews
   were skipped for genuinely empty scope (test-only slices). A fourth was never
   dispatched: Item 1.3/1, commit `07b7ae9`, 29 changed lines of
   `scripts/self-release.sh`. The skip reasons lived only in the delegate's
   scratch log, so nothing in the repository distinguished the four absences.
   Cost, measured rather than assumed: the phase corrector then found two Major
   defects in exactly that hunk, one a `|| latest_tag=""` fail-open of the class
   the neighbouring item existed to close. A precedent to extend rather than a
   pattern to invent — `build/SKILL.md` §5 already replaces a skipped final
   review with `reports/review-skip.md`, "not confidence-gated", while
   `references/tdd-slice.md` has no skip provision for dispatches (b) and (d).
   Not acting leaves an omission indistinguishable from a justified skip until
   an audit runs.

2. **Require a GREEN report even for a test-only slice.** `tdd-slice.md` §(c)
   assumes every slice has an implementation. Three here did not — two assertion
   groups over one production change (Items 1.1, 1.3) and a control (1.2/1) — so
   GREEN reduced to "run the gate and commit one already-green file" and the
   orchestrator did it directly. Those commits have no recorded suite or gate
   result. Documentary risk only here, since the repo's pre-commit hook runs the
   gate unconditionally. This sharpens the first brief's "a gate verdict in
   every GREEN report": the report can be absent entirely, not merely thin.

3. **"Fixtures tried and rejected, and why" as a required RED heading.** In Item
   1.1/2 the executor's first fixture produced a red that would have passed
   under the item's mutation too; it recognised the red as vacuous, replaced the
   fixture, and reported the discarded attempt — "the single most valuable
   paragraph in the phase's evidence", the failure mode the audit exists to
   detect, caught upstream of it. `agents/test-driver.md` RED mode already says
   a passing test "has named itself vacuous", but nothing asks for the discarded
   attempt, so this stays one executor's judgement.

4. **A mechanism-claim probe in the code-review prompt.** Comment defects
   outnumbered code defects 5:1 across Phase 1's findings, and every one was a
   falsifiable claim about what a command does — a false `dist-v*` glob ordering
   claim, a self-contradicting hazard paragraph, two stale citations. One
   scratch-repo probe falsified each. One probe per mechanism claim in a new
   comment would have caught the glob claim at the slice, not at the boundary.

### A per-item mutation gate can certify assertions that cannot fail

Source: `reports/phase-2-corrector.md`, adjudications 1 and 2 — the run's
substantive new finding.

Item 2.1(d) swept a property across ten refusal scenarios; its runbook gate
defeated **one guard among the ten**. Three failures in one scenario, gate
green — and two of the item's new assertions were incapable of failing: an
`assert_contains` needle on the `gh` log that stayed green while `release create
v0.2.0` sat in that same log under a stronger mutation, and a refutation of a
tag name no path from that fixture creates. Defanging the **shared** refusal
mechanism instead (`die()` printing and returning 0) failed 41 checks across
nine of the ten refusals, and surfaced both.

The recommendation drawn: where an item sweeps a property across N scenarios,
its gate defeats the refusal mechanism shared by all N, not one guard among
them — which belongs where gates are specified (runbook authoring,
`runbook-corrector`) as much as in the executor. The run adopted it for Phase 3
as an **additive** check: the runbook's own gate runs and is quoted first, the
sweep covers only assertions the item itself adds, a surviving pre-existing
assertion is reported and left alone, and a sweep contradicting the runbook is
stop-and-return. It earned its place four times across two phases, and was
usefully wrong-footed once — a delegate's prediction that Item 3.1's gate
already defeated the shared mechanism proved false. Different axis from the
corrector brief's "predictions are a lower bound": that is about which rows go
red, this about whether the gate can.

### Observations from the supervising session

Evidence offered as observation, not requirement.

- **The orchestrating layer had to be `general-purpose`.** Main session → a
  `general-purpose` opus delegate invoking `/orchestrate` → item agents
  (`test-driver`, `artisan`, `corrector`, `tdd-auditor`). Nested dispatch
  worked; three layers are allowed by default. But every `edify:*` agent
  enumerates its tools and none lists `Agent`. An orchestrator agent declaring
  `tools: Agent(edify:test-driver, edify:corrector, …)` would make the layer
  first-class and bound what it can dispatch.
- **One opus delegate carried about one heavy phase** — three delegates, 217k,
  187k and 179k subagent tokens. `references/resuming.md` worked as written:
  each phase-boundary resume block carried what the next delegate needed, and
  each verified it against `git log` before trusting it. The cost is that every
  handoff was a manual re-dispatch by the supervising session. Field evidence
  for the first brief's recommendation A — make the phase-boundary split the
  scheduled path; `resuming.md` is still framed as recovery.
- **Non-ordinary reds have no named form.** Some slices could not take an
  ordinary red: two assertion groups over one production change, and a
  small-list control for a defect appearing only at ≥1 MB. Each took its red
  under the item's own named mutation, applied in place and reverted with
  `git diff --quiet` shown, and the auditor judged all of them legitimate — but
  each delegate justified it ad hoc and hand-carried the justification into the
  `tdd-audit` dispatch.
- **Two git-hygiene incidents from children.** A child's in-place mutation of a
  security hook (deny → allow) tripped an automated security review mid-run; and
  two staged files that were no part of the work were unstaged and rewritten
  mid-phase, consistent with a child using `git stash` / `git stash pop`.
  Confirmed after the fact: `reports/item-3-4.md` describes obtaining its
  pre-conversion red set "via `git stash` to isolate the two states, then
  popped back". Nothing under `build/`, `agents/` or `fragments/` currently
  forbids `git stash`, `git reset` or a blanket `git add`, or names the
  parent's pre-staged files as state an executor must leave alone.
- **One dispatch per item is the only grain.** `/orchestrate` composes a
  dispatch per runbook item and names it `item-N-M`, so a `Depends on:` chain
  of several items over one file yields one fresh agent per item, each
  re-reading the file. A runbook that wants one agent to own a file across
  its edits has to merge the items; there is no dispatch-level option for it.
- **"Stop on anything needing a user decision" conflated two things.** A
  delegate given that instruction came back twice; only one was a genuine fork
  (the mutation-gate escalation). The other was the expected context-ceiling
  handoff, which is self-describing and needs no decision.

### Constraints

- A brief's recommendations are input, not decisions: each carries its evidence
  and the cost of not acting, none is a conclusion about edify's design.
- One repository's run, over a shell-script deliverable behind a `just
  precommit` gate; the 5:1 comment-to-code defect ratio in particular is a
  property of that material.
- Sources, under `/Users/david/code/claude-plugin-dev/plans/2026-09-18-deliverable-review-fixes/`:
  `reports/tdd-audit.md`, `reports/phase-2-corrector.md`,
  `reports/phase-1-corrector.md`, and the seventeen Phase 1 slice reports.
