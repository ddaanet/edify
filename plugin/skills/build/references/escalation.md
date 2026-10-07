# When a Run Goes Wrong

Read on any of: a post-item verification that did not come back clean, a
dispatch that errored or returned an unexpected result, an agent that never
returned, or a run resuming after a context ceiling or a kill.

## Post-item remediation

`scripts/verify-step.sh` after a step whose work is committed, or at the entry
gate for its mask re-run:

- Exit 2 → the script itself failed, not the dispatch. Stop and report; do not
  remediate, since there is no established verdict to remediate against.
- Exit 1 → first, a `DIRTY:` listing the `sandbox-lies` hook annotates as
  sandbox masks is re-run once, not remediated: masks reach an unsandboxed
  reader when a sandboxed Bash call runs concurrently, so they say nothing about
  the dispatch. The annotation comes from the `phantom-untracked` detector of
  the optional `sandbox-lies` plugin's Bash hook. Without that plugin no listing
  is annotated, so this branch never fires, and a masked listing reads as dirt.
  A re-run annotated again → stop and report to the user. At a fresh run's entry
  gate, the re-run's verdict goes back to `SKILL.md` §2, whose STOP governs it:
  dirt there predates the run and is never remediated. On a resumed run it goes
  back to §Resuming step 2. After an item, or after a phase-boundary,
  review-gate or closing commit, any other exit 1 → remediate, below.

**Remediation after a committed step.** The gate held the tree clean before the
step, so non-exempt dirt is the step's own work, unless someone touched the tree
in between.

1. Resume the named agent once (`SendMessage to: <name>`): "Your dispatch left
   uncommitted work: finish it and commit it by name." On a `PRECOMMIT:` verdict
   over a clean tree, the message carries the failing output instead and asks
   for the fix, committed by name. Skip this step where there is no named agent
   (an item executed in session and self-reviewed), or the named agent commits
   nothing (a review dispatch) or holds no edit tools.
2. No owner to resume, or the resume fails or returns without progress → a fresh
   dispatch composed from the item by `references/dispatch-composition.md`,
   carrying the dirt — the `verify-step.sh` listing, the diff and any precommit
   output — as a prior attempt's work to examine and finish. After a tdd slice's
   step, the step names the agent: after its GREEN, `edify:test-driver` in GREEN
   mode; after its code-review, refactor or list-revision commit,
   `edify:artisan`. Either dispatch carries the slice's entry and the dirt.
   After a phase-boundary, review-gate or closing commit there is no item to
   compose from: go to step 3.
3. That fails → escalate to the user with the listing and the dispatch's
   findings.

After any remediation, note the RCA follow-up in the run summary.

This section is `/build`'s dirty-tree rule, and
`../../fragments/escalation-acceptance.md` §Dirty tree recovery defers to it.
Dirt is unfinished work to examine and finish; nothing reverts by default, and
the orchestrator never cleans up on its own judgement. The user decides
escalated dirt path by path. A path they decide to revert, the orchestrator
reverts in session with one call:

```bash
git restore --source=HEAD --staged --worktree -- <tracked or indexed paths> && rm -- <untracked paths>
```

Paths come from `git status -z`. Where one side has no paths, drop that half:
both commands error on an empty operand list. `git restore` in that form reverts
added, modified, deleted and renamed paths (probed on git 2.47.3).

## Escalation

**2-level model:** execution-level issues (missing files, failed commands, dirty
tree) are handled here; design-level issues escalate to the user. Every
resolution must pass precommit, leave a clean tree, and satisfy the item's own
criteria.

- **Unexpected result, no error** → stop and report to the user: the planning
  assumptions were wrong.
- **Report file missing after an agent completes** → ask the agent for the
  report (resume by name); if that fails, investigate before proceeding.
- **Same error from two dispatches** → stop and report the pattern: a systemic
  issue, not a one-off.
- **Agent never returns** → check its report path, `git log` and the tree:
  silence or an idle reply is not evidence it died. The report written or the
  commit landed → treat the agent as returned and proceed from its result.
  Neither → resume it by name once; a resume that produces the report → proceed.
  Otherwise escalate to the user. There is no in-band turn or duration bound
  (`../../fragments/escalation-acceptance.md`) — a runaway agent's only stop is
  the user.

## Resuming after a context ceiling or a kill

A run that hit a context ceiling, or whose session was killed, resumes from
committed state rather than from memory of what it was doing. Re-invoke `/build`
with the same `plans/<job>` path the run started with: nothing infers it, and
`/build` never writes the task frame, so it cannot be read back from there. A
run is resumed when `SKILL.md` §1's test finds an `item-*` report on disk; a
finished job re-invoked reads as resumed too, and its inventory finds every item
landed and goes to `/build` §5.

The run's base is the parent of the earliest commit adding an `item-*` report.
`scripts/changed-files.sh <job>` prints it as `BASE:` wherever it is needed, so
nothing captures or keeps it; its `NO-BASE:` means no item has landed yet, and
nothing needs the base before the first item commit. Where the work is a phased
runbook, the current phase's base resolves as `references/phase-boundary.md`
says.

1. **Inventory from report history**, never from commit subjects, which are
   labels only. An item has landed when the commit carrying its report has:
   `git log --no-show-signature --format=%H -- plans/<job>/reports/<name>.md`
   prints a hash, for the dispatch names of `references/dispatch-composition.md`
   §Naming and resumption — `item-N-M` for an item; for a tdd slice,
   `item-N-M-s<k>-green` (its GREEN commit) and `item-N-M-s<k>-code-review` (its
   code-review commit), and, where that code-review report flags a refactoring,
   `item-N-M-s<k>-refactor` (its refactoring commit). Phase P's boundary has
   landed as `references/phase-boundary.md` resolves it. For each phase whose
   items have all landed but whose boundary has not:
   - **`phase-<P>-corrector.md` is absent** → the boundary review has not run.
     Run `references/phase-boundary.md` for P before phase P+1's first item.
   - **The report is present, uncommitted and complete** → inspect the source to
     decide which of its fixes landed, because the corrector writes its report
     before it applies fixes. Apply in session the fixes that did not land,
     check the report for UNFIXABLE as `references/phase-boundary.md` §Review
     does, then commit the report with every fix, landed and applied, as its
     §Commit commits it. The fixes applied in session get no second review, the
     same bound as `references/finishing.md` §1's report-only second pass.
   - **The report is present but partial** → no fix was applied, for the same
     reason. Delete the report and run the boundary.

   A report is complete when it carries every section of `edify:corrector`'s
   report template (its §4) through `## Fixes Applied`; the sections after it
   are conditional or optional there.
2. **Run `/build` §2's gate**, `scripts/verify-step.sh`, with one change: a
   resumed run's dirt is examined, not refused, since a kill leaves no live
   agent to own it. Examine each dirty path's diff for relevance to the first
   remaining item and for quality. What is relevant and sound goes into that
   item's dispatch as prior work to examine and finish; anything else escalates
   to the user with the examination, decided path by path as §Post-item
   remediation closes. For tdd: without the slice's `-red.md` and
   `-test-review.md` on disk, its implementation-side dirt cannot enter RED,
   whose proof needs unchanged code, so it escalates too. A masked listing is
   re-run first, as `/build` §2 says. The other verdicts:
   - `CLEAN:` → proceed.
   - `DIRTY:` → examined, as above.
   - `PRECOMMIT:` over a clean tree, and exit 2 → STOP, as `/build` §2 does.

   `verify-step.sh` exits on `DIRTY:` before it runs `just precommit`, so a
   dirty resume reaches no precommit at the gate. Precommit first runs at the
   first remaining item's `SKILL.md` §4.4 verification, over the adopted prior
   work too. With no item remaining — a run killed inside `finishing.md` — dirt
   is judged against `finishing.md`'s first unlanded stage, and precommit first
   runs at the next verify-step `finishing.md` runs: after §1's report commit,
   or after §3.3's closing commit.
3. Run `/build` §3, then start §4 at the first remaining item.

**Do not use `just precommit` as a state-assessment tool.** It is a pass/fail
gate, not a diagnostic: a green run says the tree is valid, never which items
already landed, and a red one says nothing about where the run stopped.
