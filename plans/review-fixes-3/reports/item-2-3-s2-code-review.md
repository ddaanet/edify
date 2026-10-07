# Review: Item 2.3 slice 2 — code review

**Scope**: the slice commit's test code (`a03aaa11`), in
`tests/test_triage_feedback_failures.py`: the `_underclassified_repo`
helper, `test_unreadable_classification_is_an_error` and
`test_failing_label_sed_is_an_error`. This is a pinning slice, so there is
no implementation diff. `plugin/bin/triage-feedback.sh` was read-only,
apart from one in-place mutation run that was restored.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The two tests pin the classification grep's failure arm and the label
`sed`'s failure arm. They match the Interfaces block, and both shims and the
permission fixture are portable and correct. The review found two minor
issues and fixed both. The new helper sat above its users, and
`test_usage_error_exits_1` still built the same fixture inline. One docstring
also gains a clause on its macOS residual. A shared shim writer is flagged
for the orchestrator, not built here.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Helper defined before its users**
   - Location: `tests/test_triage_feedback_failures.py`,
     `_underclassified_repo` (was line 190).
   - Note: the shared convention is that definitions follow their users.
     The sibling module's only local helper, `_undated` in
     `tests/test_triage_feedback_log.py`, sits at the end of its module.
   - **Status**: FIXED. Moved to the end of the module.
2. **`test_usage_error_exits_1` builds the helper's fixture inline**
   - Location: `test_usage_error_exits_1`, lines 144–152 before the fix.
   - Note: `_init_repo` plus `_commit_item_report` with a `Simple`
     classification and a `def foo` is the helper's body, line for line. The
     slice added the helper but left this copy in place.
     `test_no_base_is_an_error_with_no_log_row` cannot use the helper,
     because it commits without an item report on purpose. The fixtures in
     other modules are out of this review's reach.
   - **Status**: FIXED. The test now calls `_underclassified_repo(repo)` and
     discards the return value. Its docstring stays accurate.
3. **The stderr assertion's macOS bound is unstated in the test**
   - Location: `test_unreadable_classification_is_an_error`, docstring.
   - Note: `"classification.md" in result.stderr` relies on grep naming the
     file in its diagnostic. The test review's report says BSD wording may
     differ, but the test did not say so (memory `macos-gate-target`: state
     the residual bound in a comment).
   - **Status**: FIXED. The docstring states that only the name is
     asserted, because the wording may differ on BSD grep, which is
     unverified on macOS.

## Refactoring signals

`REFACTOR-NEEDED: tests/test_triage_feedback_failures.py,
tests/test_changed_files_errors.py, tests/line_limits_helpers.py,
tests/triage_feedback_helpers.py — a shared PATH-shim writer.`

Four shims already repeat the same boilerplate: `shutil.which` the real
tool, assert it was found, `mkdir` a `bin`, write a `#!/bin/sh` script,
`chmod 755`. They are the git and sed shims here,
`test_changed_files_errors.py:172` and `line_limits_helpers.py:137`. Slice
2.3/3 adds a grep shim to the behavioural module. The bodies all differ, and
the sed shim needs the real path inside a branch, not only in a trailing
`exec`. A helper would therefore take a shell template and substitute the
quoted path, which is a new abstraction spanning three modules. It is not a
fix to apply in this slice.

A shared helper would also bring the pre-existing git shim
(`test_failing_reports_diff_is_an_error_not_none`) into line. That shim
still embeds the path as `"{real_git}"` rather than through `shlex.quote`.
That code predates this slice and was not raised as a finding here.

## Review verdicts on the dispatch's questions

- **Sed shim.** It uses POSIX-only constructs: `for arg in "$@"`, `case`,
  `exec`, and `echo` on a fixed literal. The `shlex.quote`d path is valid
  `sh` quoting. The SUT's `sed -E` with `;`-separated `s` commands is
  BSD-compatible, and macOS `/bin/sh` runs the shim unchanged.
  - The matching arm runs the real `sed`, so `Simple` reaches stdout, then
    exits 4. This makes the status the only carrier of the failure.
  - The `exec` pass-through is correct and has no caller, by construction:
    the SUT has one `sed` call, and `changed-files.sh` has none. This is a
    stated residual, as in the test review.
- **Permission fixture.** `skipif(os.geteuid() == 0)` is present, and
  `chmod(0o644)` runs in `finally` before `tmp_path` cleanup. This matches
  `test_unreadable_log_is_an_error_and_appends_nothing`.
- **Attribution probe.** The mode-000 run's full stderr is
  `grep: plans/j/classification.md: Permission denied`, and nothing else.
  No `git` call in `changed-files.sh` reads the file or names it, so the
  stderr assertion can only be met by the classification grep.
- **Docstrings.** The summaries fit within 70 characters, and the module
  docstring names both new arms. No code contains a `KD-N` or a plan-item
  ID. `D-90` is a design-decision ID and predates this slice.
- **Module size.** 273 lines before the fixes, 267 after.
- **SUT against the Interfaces block.** At `triage-feedback.sh` lines
  176–190:
  - grep exit 1 is a result, and any status above 1 prints
    `ERROR: grep failed` on stdout and exits 2.
  - The `sed` capture is guarded by `if !`, which prints
    `ERROR: sed failed` and exits 2.
  - Both arms exit before the log block, so neither writes a row.

  This matches "Exit 2: `ERROR: <cause>` on stdout and no log row, for a
  failing git, grep or sed; an unreadable `classification.md`".

## Mutated-SUT run (once)

- **Mutant.** In the sed failure arm,
  `echo "ERROR: sed failed"\n                exit 2\n` was replaced by
  `echo "ERROR: sed failed"\n`. The guard prints its line but does not stop
  the run. This is a different mutant from the RED report's dropped guard
  and the test review's mutants A, B and C.
  - The replacement count was checked to be exactly 1 before it was applied.
  - `git diff --stat` showed one deletion.
- **Result.** `test_failing_label_sed_is_an_error` went red at line 271, on
  the stdout equality assertion. The run went on to `## Evidence`, reached
  `underclassified` and printed `Triage: predicted Simple …`.
- **Restore.** The same replacement was applied in reverse.
  `git diff --exit-code -- plugin/bin/triage-feedback.sh` returned clean.

## Fixes Applied

- `tests/test_triage_feedback_failures.py`:
  - `_underclassified_repo` moved from above the slice's tests to the end
    of the module;
  - `test_usage_error_exits_1` builds its fixture with
    `_underclassified_repo(repo)` instead of an inline copy;
  - the `test_unreadable_classification_is_an_error` docstring states the
    BSD-grep wording bound.
- No SUT change. No helper was added to `tests/triage_feedback_helpers.py`.

## Gate

- `PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit` reported
  `Precommit OK`. The tests ran (not cached), with 419/420 passed and 1
  xfail. Version consistent at 0.3.0. Design links: 94 decisions indexed, 9
  nodes present.
- The line-limit warnings are pre-existing and outside this review:
  `plugin/agents/corrector.md` 682, `outline-corrector.md` 450 and
  `design-corrector.md` 460.
- `.venv/bin/pytest -p no:markdown_report tests/test_triage_feedback*.py`:
  31 passed.
- Tree: `tests/test_triage_feedback_failures.py` is modified and this report
  is untracked. Nothing is committed.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m4 (KD-5), the classification arms | Satisfied | the two tests pin the classification grep's `*)` arm and the label `sed` guard |
| Interfaces: unreadable `classification.md` gives exit 2, `ERROR:` on stdout, no row | Satisfied | `test_unreadable_classification_is_an_error` |
| Interfaces: failing `sed` gives exit 2, `ERROR:` on stdout, no row | Satisfied | `test_failing_label_sed_is_an_error`, plus the mutation run above |
| Item notes: shim pass-through, `shlex.quote`, root skip, mode restore | Satisfied | see the verdicts above |

## Positive Observations

- Exact-equality stdout assertions pin the whole interface. The mutation
  run shows this catches an arm that prints its line and carries on.
- The sed shim prints the real label before it fails. A status guard is
  then the only correct implementation, and an emptiness check fails the
  test.
- The grep test ties its shared `ERROR: grep failed` line to the right arm
  through grep's own diagnostic, not through fixture reasoning.
