# build-defects — leg 4 (stopped at Item 2.5, blocked by the classifier)

**Status: stopped before any item edit landed.** The session is still in auto
mode. The first `Edit` of Item 2.5, the §Naming one on
`plugin/skills/build/references/dispatch-composition.md`, came back "The
server-side auto mode classifier gave no verdict (it skipped this action)". Per
the leg's constraint, this leg stopped without a retry and without any sed,
script, heredoc, patched-copy or `Write` route.

No item commit in this leg. Items 2.5–2.9 are not applied; §5 Finish has not
run. No dispatch was made.

## Entry state

- HEAD `469c6b2c`. The tree held the staged `.claude/handoff-task.md` (the main
  session's, kept out of every commit), the untracked
  `inbox/brief-corrector-reads-surfaces-against-each-other.md` (another
  session's, not staged) and the untracked sandbox phantoms
  `.claude/launch.json`, `.claude/loop.md`, `.claude/output-styles`,
  `.claude/routines` and `.claude/workflows` (left alone).
- `tmp/build-baseline` holds `f44ddbbf89c4bea2ffa49a0fdfdd961cbe167474`,
  untouched.
- §2's entry gate had already passed for this run, so it was not re-run.

## Pre-work (§3)

- Brief check: no `plans/build-defects/brief.md`.
- Recall: no `recall-artifact.md`. Selected from the index
  `edify-commit-hook-gotchas`, `audit-a-contract-across-its-surfaces`,
  `classifier-denied-self-config`, `cc-subagent-approval` and
  `subagent-write-blocks-report-basenames`.
- Reference loading: `craft:directive-writing`, since Items 2.5–2.9 are all
  agent-facing directive text.

## Item 2.5 — blocked

- All five old strings in `item-2-5.md` were re-checked against the current
  files and still match verbatim: `dispatch-composition.md` lines 91–92, 46–49
  and 34–38; `test-driver.md` 101–102; `refactor.md` 177–183.
- The first `Edit` got "gave no verdict". The exact old→new text for all five
  edits is in `item-2-5.md`, whose Status line now records this leg's attempt.
  That report is committed with this one.
- Per-item review plan, for whoever resumes: Item 2.5 fails §Proportionality's
  self-review conditions (three files, contract change), so applied in session
  under §4.1 it needs an `edify:corrector` dispatch scoped to its changes before
  §4.4.

## Items 2.6–2.9 — not started

## §5 Finish — not run

The two checks the review gate owes, still open:

- Item 2.3's reading of KD-2: the one report-only re-dispatch's findings go
  into the same `review-<group>.md` and are applied, with no further pass.
- Item 2.4's pointers to `dispatch-composition.md` resolve once 2.5 lands.

## Deferred and routed (carried from legs 1–3, not fixed)

- The `C` (copy) half of `verify-step.sh`'s `[^RC][^RC]` guard is unpinned: a
  `^[^R][^R]` mutant passes all five tests. My human partner's call.
- Unmerged exempt paths (`UU .claude/handoff-task.md`) read CLEAN; `"?…"?`
  accepts an unbalanced quote git never emits. Observations only.
- `references/tdd-slice.md`'s orchestrator commits lack the
  `git commit -- <paths>` form; outside IN.
- `review-dispatch-template.md` §Example dispatches a skill group through the
  fix-capable template, correct only under the plugin-dev-absent fallback.
- Pre-existing: leg 1's `xargs` / `|| true` DEFERRED item in
  `triage-feedback.sh`, and `just lint`'s RUF100 in
  `tests/line_limits_helpers.py`.

## Final `verify-step.sh` output

Not run in this leg: no item commit landed, so §4.4 had nothing to verify. The
last run is leg 2's, after `24879259`, in `build-leg2.md`.

## Resume block

- **What blocks.** Three legs in a row, every `Edit` under `plugin/` in auto
  mode has drawn "no verdict". Leg 2's only successful item edits came with the
  session out of auto mode (Item 2.1 in session; Items 2.2–2.4 by an artisan
  spawned under accept-edits). The restart before this leg did not change the
  mode.
- **Where the next leg starts.** Item 2.5, from `item-2-5.md`, once the session
  is out of auto mode and any executor is spawned after the mode change. Then
  Items 2.6–2.9 in order, then §5 Finish.
- **Baseline.** `tmp/build-baseline` is unchanged; §5 reads it.
- **Commit form.** Every commit uses `git commit -- <paths>` (KD-7).
