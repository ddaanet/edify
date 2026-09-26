# Review: build-defects fragments group (Items 2.7, 2.8, 2.9)

**Scope**: `plugin/fragments/review-requirement.md` §Execution Context "Changed
files"; `plugin/fragments/escalation-acceptance.md` §Dirty tree recovery;
`plugin/fragments/delegation.md` §Multi-Step Verification. Diff against
f44ddbbf89c4bea2ffa49a0fdfdd961cbe167474.
**Date**: 2026-09-26
**Mode**: review + fix

## Summary

All three items land their requirement. Item 2.9 is correct as committed. I
read the surfaces against each other and found two seams. First, Item 2.7's
"base commit of the run or phase" did not say how a phase's base is found, and
its terms did not fit the `/review` consumer. Second, Item 2.8's restatement
of the owning rule dropped the sandbox-mask re-run clause and turned its
conditional fallback chain into an unconditional sequence. Both are fixed. I
found two more seams whose fix belongs in files outside this group. They are
recorded as OUT-OF-SCOPE.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Changed-files base gives no way to find a phase's base and does not fit
   `/review`**
   - Location: `plugin/fragments/review-requirement.md` §Execution Context,
     Changed files bullet
   - Note: "the base commit of the run or phase under review" names the base
     but not how to find it. KD-1 says a phase P>1 base is resolved, not
     stored, from the commit adding `phase-<P-1>-corrector.md`. A reader
     holding only the fragment could go looking for a stored phase base, which
     is the `tmp/build-phase-base` alternative KD-1 rejected. The fragment is
     also read by `plugin/skills/review/SKILL.md`, whose scopes (uncommitted
     work, recent commits, branch work) have neither a run nor a phase. The
     fix generalises the base to "the work under review" and points `/build`
     readers at `phase-boundary.md`, which holds the resolution. It does not
     restate the resolution, so there is no second copy to drift. The new
     pointer uses the `plugin/…` form the file already uses (lines 62, 209).
   - **Status**: FIXED

2. **Dirty-tree restatement omits the sandbox-mask re-run clause**
   - Location: `plugin/fragments/escalation-acceptance.md` §Dirty tree recovery
   - Note: the governing rule (`escalation.md` §Post-item remediation, exit-1
     bullet) says that before any remediation, a `DIRTY:` listing that the
     `sandbox-lies` hook annotates as masks is re-run once and not remediated.
     If the re-run is annotated again, the orchestrator stops and reports. The
     fragment's bullets skipped straight to "resume the owning agent", so a
     reader following only the fragment would remediate a masks-only listing.
     The governing rule forbids that. I added the clause.
   - **Status**: FIXED

3. **Remediation chain reads as unconditional**
   - Location: `plugin/fragments/escalation-acceptance.md` §Dirty tree
     recovery, second bullet
   - Note: "resume it once, then dispatch a fresh `edify:artisan`, then
     escalate" reads as three steps always taken. In the owning rule each step
     is conditional: the artisan runs only "if the resume fails or returns
     without progress", and escalation happens only "if recovery fails". The
     fix rewords it to "resume it once; if that fails, dispatch a fresh
     `edify:artisan`; if that fails too, escalate".
   - **Status**: FIXED

4. **The changed-files command includes tracked KD-7 exempt dirt**
   - Location: KD-1's form `git diff --name-only <base>`, used by
     `plugin/skills/build/references/phase-boundary.md` and `finishing.md` §1
     and restated in the fragment
   - Note: `git diff <commit>` compares the working tree to the commit. A
     tracked path left dirty by convention (`memory`, `.claude/handoff-*.md`)
     therefore lands in the changed-files list even when no commit in the
     range touched it, and gets routed to a reviewer. In this run those paths
     were also committed in range: `git diff --name-only <base>` and
     `git diff --name-only <base> HEAD` gave identical lists, so this is shown
     from git semantics, not from an observed misroute. For `/review` of
     uncommitted work the working-tree form is the right one, so the
     fragment's generic text stands. The `/build`-side choice (`<base> HEAD`,
     or filtering the KD-7 paths) belongs to KD-1 and the two references.
   - **Status**: OUT-OF-SCOPE — the fix lives in `phase-boundary.md`,
     `finishing.md` and KD-1, all outside this group's Changed files
     (recorded for follow-up)

5. **The confirmed destructive revert also destroys KD-7 exempt dirt**
   - Location: `escalation.md` §Post-item remediation (owner) and the
     fragment's third bullet (restatement)
   - Note: `git checkout -- .` reverts `.claude/handoff-*.md` edits, and
     `git clean -fd` deletes untracked `inbox/*.md` briefs. Those are the
     paths KD-7 says are dirty on purpose. The text justifies the
     confirmation with "destroys untracked work" and does not say that it also
     sweeps these conventional files. So the confirmation the user gives is
     under-informed. A path-scoped revert over the `DIRTY:` listing would
     avoid this. That changes KD-5's command, and the fragment must stay
     word-aligned with its owner.
   - **Status**: OUT-OF-SCOPE — owned by KD-5 and `escalation.md`, which is
     reviewed in another group and not edited here (recorded for follow-up)

## Fixes Applied

- `plugin/fragments/review-requirement.md` §Execution Context, Changed files:
  the base is now "the base commit of the work under review — under `/build`,
  the run's or phase's base as
  `plugin/skills/build/references/phase-boundary.md` resolves it". The
  "never a bare `git diff --name-only`" clause and its reason are kept. Reflowed
  by `just format`.
- `plugin/fragments/escalation-acceptance.md` §Dirty tree recovery: added the
  sandbox-mask re-run bullet (re-run once, act on the re-run, stop and report
  if it is annotated again), and rewrote the remediation chain as conditional
  fallbacks.
- `just precommit`: the first run failed on a rumdl reflow of
  `review-requirement.md`. I ran `just format`, and the second run passed
  (`Precommit OK`). It printed three `oversized-file` lines, for
  `plugin/agents/corrector.md`, `outline-corrector.md` and
  `design-corrector.md`. The gate still passes with them, and none of those
  files is in this group.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| orch C1 / KD-1 (Item 2.7) | Satisfied | `review-requirement.md` Changed files: `git diff --name-only <base>`, never bare, with the reason (index comparison, empty after commit). After the fix, the phase base resolution is reached through `phase-boundary.md`, which states phase 1 = `tmp/build-baseline` and phase P>1 = the commit adding `phase-<P-1>-corrector.md`, resolved by `git log --diff-filter=A` |
| orch M7 / KD-5 (Item 2.8) | Satisfied | §Dirty tree recovery names `escalation.md` §Post-item remediation as governing. It restates owner commits or reverts, then resume, artisan, escalate (now conditional), that the orchestrator never cleans up in its own session, and that `git checkout -- . && git clean -fd` runs only where no agent owns the dirt, after the user confirms. It matches the owning section's closing paragraph clause for clause |
| inline m2 (Item 2.9) | Satisfied | §Multi-Step Verification: one script owns the verdict, "`/build`'s `verify-step.sh`", named by skill with no new repo-relative path. It says why the compound fails (`git status --porcelain` exits 0 on a dirty tree, confirmed: `porcelain-exit=0` on this dirty tree). Its description matches the script: tree check, then `just precommit`, with `DIRTY:` or `PRECOMMIT:` naming the failed check |

**Gaps:** none.

## Surfaces read against each other

- **Dirty-tree rule.** Owner: `escalation.md` §Post-item remediation.
  Restatement: `escalation-acceptance.md` §Dirty tree recovery. After the
  fixes, the restatement carries every clause of the owner's exit-1 path that
  applies to a dirty tree: the mask re-run, the conditional resume, artisan
  and escalate chain, the ban on in-session cleanup, and the confirmed revert
  for unowned dirt only. The owner's back-pointer to the fragment is intact.
  One seam (issue 5) is shared by both surfaces.
- **Changed-files rule.** Rule: `review-requirement.md`. Consumers:
  `phase-boundary.md` (runs `git diff --name-only <phase base>` and resolves
  the base), `finishing.md` §1
  (`git diff --name-only "$(cat tmp/build-baseline)"`) and
  `review-dispatch-template.md` (Baseline hash plus an explicit per-group
  list). All three use a base, never the bare form. The fragment now points at
  the resolver instead of implying a stored phase base. One seam (issue 4)
  sits in the command form the consumers share.
- **Verification verdict.** `delegation.md` describes `verify-step.sh` as the
  script is written (exit 1 carries `DIRTY:` or `PRECOMMIT:`, exit 2 is a
  script failure). No other surface in `plugin/` or `docs/` still prescribes
  the `git status --porcelain && just lint` compound.

## Positive Observations

- Item 2.7 removes the "or known from implementation" escape. That escape was
  how a list could be put together with no base at all.
- Item 2.8 puts the governing pointer ahead of the restatement, so any drift
  resolves in the owner's favour.
- Item 2.9 gives the reason as mechanism (exit status), not as a claim about
  atomicity, and drops the false "both run or neither" line.
