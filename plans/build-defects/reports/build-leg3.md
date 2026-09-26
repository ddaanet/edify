# build-defects — leg 3 (stopped at Item 2.5, blocked by the classifier)

**Status: stopped before any item edit landed.** The session is in auto mode,
and the first `Edit` of Item 2.5 on
`plugin/skills/build/references/dispatch-composition.md` came back "The
server-side auto mode classifier gave no verdict (it skipped this action)".
Per the leg's constraint, this leg stopped without a retry and without any
sed, script, patched-copy or `Write` route.

No item commit in this leg. Items 2.5–2.9 are not applied; §5 Finish has not
run.

## Entry state

- HEAD `f417fb30`; the tree was clean apart from the untracked
  `inbox/brief-corrector-reads-surfaces-against-each-other.md` (another
  session's, KD-7-exempt, not staged) and the untracked sandbox leftovers
  `.claude/launch.json`, `.claude/loop.md`, `.claude/output-styles`,
  `.claude/routines` and `.claude/workflows` (left alone).
- `tmp/build-baseline` holds `f44ddbbf89c4bea2ffa49a0fdfdd961cbe167474`,
  untouched.
- §2's entry gate had already passed for this run, so it was not re-run.

## Pre-work (§3)

- Brief check: no `plans/build-defects/brief.md`.
- Recall: no `recall-artifact.md`. Selected from the index
  `edify-commit-hook-gotchas`, `audit-a-contract-across-its-surfaces`,
  `reflow-joins-field-lines`, `cc-subagent-approval` and
  `classifier-denied-self-config`.
- Reference loading: `craft:directive-writing`, since Items 2.5–2.9 are all
  agent-facing directive text.

## Item 2.5 — blocked

- All five old strings in `item-2-5.md` were re-checked against the current
  files and still match verbatim, despite Items 2.1–2.4's nearby edits.
- The first `Edit`, §Naming `review-<group>` on `dispatch-composition.md`,
  got "gave no verdict". The exact old→new text for all five edits is in
  `item-2-5.md`, whose Status line now records this leg's attempt. That
  report is committed with this one.
- Per-item review plan, for whoever resumes: Item 2.5 fails §Proportionality's
  self-review conditions (three files, contract change), so applied in
  session under §4.1 it needs an `edify:corrector` dispatch scoped to its
  changes before §4.4.

## Items 2.6–2.9 — not started

## §5 Finish — not run

The two checks the review gate owes, still open:
- Item 2.3's reading of KD-2: the one report-only re-dispatch's findings go
  into the same `review-<group>.md` and are applied, with no further pass.
- Item 2.4's pointers to `dispatch-composition.md` resolve once 2.5 lands.

## Deferred and routed (carried from legs 1 and 2, not fixed)

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

Not run in this leg: no item commit landed, so §4.4 had nothing to verify.
The last run is leg 2's, after `24879259`, in `build-leg2.md`.

## Resume block

- **Where the next leg starts.** Item 2.5, from `item-2-5.md`, once edits
  under `plugin/` can land: the session out of auto mode, and any executor
  spawned after the mode change. Then Items 2.6–2.9 in order, then §5
  Finish.
- **Baseline.** `tmp/build-baseline` is unchanged; §5 reads it.
- **Commit form.** Every commit uses `git commit -- <paths>` (KD-7).
