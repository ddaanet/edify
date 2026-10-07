# Build leg 2 — review-fixes-3

A resume of `/build plans/review-fixes-3/outline.md`, following
`references/escalation.md` §Resuming. The gate came back `CLEAN`. Recall read
the artifact's eight files and loaded `craft:test-discipline`. Each dispatch
read the skill bodies from the plugin cache. The coordinator stopped the leg
after 2.4/1's GREEN, so the delegate can be recycled.

## Completed

All commits carry the subject prefix `review-fixes-3 Item …`, and every
committed step was followed by a `verify-step.sh` run that came back `CLEAN`.

| Slice | Commits (subject tails) |
|---|---|
| 2.2/1 | `— triage-feedback.sh measures from the repository root`; `— code-review fixes`; `— list revision` |
| 2.2/2 | `— triage-feedback.sh outside a work tree is one error line`; `— code-review fixes`; `— split the run-location tests from test_triage_feedback.py` (refactor); `— list revision` |
| 2.3/1 | `— pin triage's usage and changed-files.sh failure exits`; `— code-review fixes` (report only) |
| 2.3/2 | `— pin triage's classification grep and label sed failures`; `— code-review fixes`; `— one PATH-shim helper for the triage and changed-files tests` (refactor); `— list revision` |
| 2.3/3 | `— pin triage's definition grep and log directory failures`; `— code-review fixes` |
| 2.4/1 | `— /build's hash-reading git log commands pass --no-show-signature` (GREEN only) |

Reports are `item-2-2-s{1,2}-*`, `item-2-3-s{1,2,3}-*`, `item-2-4-s1-{red,test-review,green}.md`,
and the two `-refactor.md`.

## Run summary notes

- **2.2/1's GREEN fixed a bash 3.2 parse error that was already at HEAD.** A
  bare `case` pattern inside `$(…)` in `triage-feedback.sh` stopped the script
  from parsing. GREEN added a leading `(`, under the outline's 2.2 note, and
  the code review commented it. The triage suite now passes under bash 3.2.57
  at `/tmp/claude-1000/bash32/bin`, a scratch build that is still present.
- **2.2/1's code review found and fixed a regression the slice introduced.**
  With an exported `CDPATH`, `cd "$script_dir"` printed into the capture. The
  fix is `unset CDPATH`. A list revision added
  `test_cdpath_does_not_move_the_script_dir` to slice 2, proven by mutation.
  The test review then pointed `CDPATH` at a decoy directory instead of `.`,
  a departure from the revision text: `.` could not tell a moved `cd` apart.
- **Refactors:**
  - 2.2/2 moved the hub, at 399/400, into a new
    `tests/test_triage_feedback_location.py`.
  - 2.3/2 added `_write_shim` to `tests/changed_files_helpers.py`, which also
    put the old `git` shim on `shlex.quote`.
  - `tests/line_limits_helpers.py`'s shim was left alone because it is out of
    this job's scope.
- **List revisions:**
  - 2.2/1: the CDPATH test.
  - 2.2/2: the duplicated `$status` line, and the location module.
  - 2.3/2: slice 3 uses `_write_shim`.
  - 2.3/1 and 2.3/3: none.
- **Item 2.3 is complete.** Its last code review confirmed that every exit-2
  cause in Item 2.3's Interfaces block, and m4–m6, has a test. The one
  exception is the `cd`-after-`rev-parse` arm, which is the residual bound
  the outline accepts.
- **2.2/2's outline text is stale.** "Today stdout carries …" no longer
  matches. It is plan-as-written, so it was left.

## Open questions for my human partner

None blocking. The bash 3.2 `source` defect in `changed-files.sh` stays out
of scope, as ruled. `test_unloadable_exempt_paths_is_an_error_not_no_base[absent]`
is still the one bash-3.2 failure across the changed-files and triage modules.

## Current state

`main` is clean, apart from the two untracked `inbox/brief-*.md` files, which
are not this job's. `just precommit` is green, with 430/431 passing and 1
xfail. No dispatch is live, and no agent needs resuming.

## Next leg resumes at

**Item 2.4, slice 1, step (d): code review.** `item-2-4-s1-green.md` has
landed and `item-2-4-s1-code-review.md` has not. Dispatch `edify:corrector`
(opus) with scope IN as the five prose edits and
`tests/test_build_prose_git_log.py`, then commit its report with any fixes.
After that, take the list revision.

Still to do after that:

1. Items 3.1–3.6, which are general items, prose and opus.
2. Item 4.1.
3. Finish (`references/finishing.md`).

The dispatch notes from leg 1 still hold:

- Run git, just and pytest with `dangerouslyDisableSandbox: true`.
- Run `PATH=…/.venv/bin:$PATH just precommit` in the foreground.
- Point a dispatch at the skill bodies in the cache.
- Probe with `command grep`.
- On a `Tests cached` result, run the touched modules directly.
