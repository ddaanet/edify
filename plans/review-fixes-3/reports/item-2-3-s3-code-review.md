# Review: Item 2.3 slice 3 code review (`item-2-3-s3-code-review`)

**Scope**: the test code in slice commit `327c5ea8`:
`tests/test_triage_feedback_behavioral.py`
(`test_failing_definition_grep_is_an_error_not_no`, module docstring) and
`tests/test_triage_feedback_log.py`
(`test_unwritable_log_is_an_error_not_a_usage_exit`, `directory` case). The
SUT, `plugin/bin/triage-feedback.sh`, was read only, apart from one in-place
mutation run that was restored. This is Item 2.3's last slice, so the review
also checked the whole item against its Interfaces block and m4/m5/m6.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

Both tests are sound evidence. Each one was proved red by a mutant at RED and
again at test review. There were three issues, all fixed:

- The `directory` case asserted `mkdir`'s localised wording on stderr. Its
  siblings assert the operand path instead.
- The behavioural module's docstring misplaced the log's failure arms.
- The parametrized fixture was split across two conditionals, both keyed on
  the case.

Every exit-2 cause in Item 2.3's Interfaces is now pinned across the triage
modules. The one exception is the documented `cd` residual.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The `directory` stderr positive depends on locale and on unverified BSD
   wording**
   - Location: `tests/test_triage_feedback_log.py:203` (as committed),
     `assert "Permission denied" in result.stderr`
   - Problem: `_run_triage` inherits `os.environ` and pins only
     `GIT_CONFIG_*`. Under a non-C `LANG` with coreutils translations
     installed, GNU `mkdir` translates both its message and `strerror`, so
     the assertion fails on a correct script. The test review's claim that
     the substring holds on BSD `mkdir` was never run on macOS (recall
     `macos-gate-target`). The project pattern is different: the slice-2
     sibling `test_unreadable_classification_is_an_error` and
     `test_line_limits_fails_when_find_cannot_walk` both assert the operand
     path on stderr and state the BSD bound in the docstring.
   - Fix: the positive asserts the directory path,
     `str(log_dir.relative_to(repo)) in result.stderr` (`plans/reports`).
     GNU and BSD both name the operand, and the locale does not change it.
     The `log.name not in result.stderr` negative is kept. It is what tells
     `mkdir`'s message apart from a bash redirection error on the log path,
     which also contains `plans/reports`. The docstring gains the residual
     bound: the wording is localised, and BSD `mkdir -p` naming the whole
     operand is unverified on macOS.
   - Discrimination is kept:
     - The suppressed-stderr mutant below reds on the new positive.
     - The swallow mutant from the test review (`|| true ||`) puts the
       bash error naming the log on stderr. The unchanged negative reds it.
     - The prints-no-exit, `exit 1` and guard-dropped mutants red on stdout
       and returncode assertions, which this fix leaves unchanged.
   - **Status**: FIXED

### Minor Issues

1. **The behavioural module docstring misplaced the log's failure arms**
   - Location: `tests/test_triage_feedback_behavioral.py:7-10`
   - Problem: this slice edited the docstring to say "The failure arms,
     apart from a failing definition grep and a failing diff, are in
     `tests/test_triage_feedback_failures.py`". The log's read and write
     failure arms are in `tests/test_triage_feedback_log.py`, as the failures
     module's own docstring says ("The behavioural-code and log failures stay
     in their own modules").
   - Fix: the docstring now says that a failing diff and a failing definition
     grep are tested here, the log's failure arms are in the log module, and
     the rest are in the failures module.
   - **Status**: FIXED

2. **The three-case fixture was split across two conditionals**
   - Location: `tests/test_triage_feedback_log.py:176-188` (as committed)
   - Problem: the setup ran `if directory / else mkdir`, then
     `if row / elif header`. Both chains keyed on `unwritable`, so a reader
     had to combine two conditionals to see any one case's fixture.
   - Fix: one `if directory / elif row / else` chain, with each case's
     fixture whole in its own branch. `header` takes the `else`, as it did
     before the slice. The assertion block's `if unwritable == "directory"`
     stays. It is short, and the docstring explains it. No split into a
     separate test is needed.
   - **Status**: FIXED

## Checked with no finding

- **Shim targets only the definition grep.** The SUT's only `grep` calls are
  line 152 `grep -qE` (definition) and line 176 `grep -E` (classification).
  `changed-files.sh` and `exempt-paths.sh` call no `grep`: a `command grep`
  over both finds only a comment. The shim compares each argument
  to exactly `-qE`. It runs the real tool first, so the pipe is drained and
  only the status carries the fault. Every other call goes through
  `exec "$real" "$@"`. It is written by `_write_shim`, which quotes the real
  path with `shlex.quote`, as the outline's list revision after 2.3/2
  requires.
- **macOS portability of the shim test**:
  - `#!/bin/sh` with `[ = ]`, `for arg in "$@"` and `exec` is POSIX.
  - BSD grep accepts `-qE`.
  - `shim: fail` comes from the shim itself.
  - `ERROR: grep failed` is the script's own line.
  - No assertion depends on grep's own wording.
- **Permission fixtures**:
  - The `os.geteuid() == 0` skip comes before the fixture.
  - `finally` restores `plans/` to 755 first, then `plans/reports` if it
    exists, then the log, so each path is reachable when its turn comes.
  - On `header` and `row`, `plans/` was never chmodded, and 755 there is
    harmless.
- **Docstrings**:
  - Summaries are 70 characters or fewer.
  - No `KD-N` or plan-item IDs appear.
  - No prose was shaved.
  - `docformatter -c` passes inside `just precommit`.
- **SUT matches the pinned Interfaces.** Each exit-2 arm prints its `ERROR:`
  line to stdout before exiting 2, and none of them reaches the log append:
  - lines 32–36: rev-parse;
  - lines 39–42: cd;
  - lines 49–54: changed-files, printed first;
  - lines 84–101: reports diff;
  - lines 138–142: committed diff;
  - lines 157–160: definition grep;
  - lines 181–189: sed and classification grep;
  - lines 265–308: mkdir, header, read and row.

  Usage is lines 7–10: stderr, exit 1.

## Item 2.3 as a whole: exit-2 causes against tests

| Interfaces cause | SUT lines | Pinned by |
|---|---|---|
| Exit 1, usage (m6) | 7–10 | `test_triage_feedback_failures.py::test_usage_error_exits_1` (`no-args`, `stale-base`) |
| `changed-files.sh` exit 1, output first | 49–54 | `test_triage_feedback_failures.py::test_no_base_is_an_error_with_no_log_row` |
| `changed-files.sh` exit 2, output first (m5) | 49–54 | `test_triage_feedback_failures.py::test_changed_files_error_is_printed_then_exit_2` |
| failing git: `rev-parse` | 32–36 | `test_triage_feedback_failures.py::test_outside_a_work_tree_is_one_error_line` |
| failing git: reports diff | 84–101 | `test_triage_feedback_failures.py::test_failing_reports_diff_is_an_error_not_none` |
| failing git: committed diff | 138–142 | `test_triage_feedback_behavioral.py::test_failing_diff_is_an_error_not_no` |
| failing grep: definition (m4) | 157–160 | `test_triage_feedback_behavioral.py::test_failing_definition_grep_is_an_error_not_no` (this slice) |
| failing grep / unreadable `classification.md` (m4) | 186–189 | `test_triage_feedback_failures.py::test_unreadable_classification_is_an_error` |
| failing sed (m4) | 179–183 | `test_triage_feedback_failures.py::test_failing_label_sed_is_an_error` |
| log directory | 265–268 | `test_triage_feedback_log.py::test_unwritable_log_is_an_error_not_a_usage_exit[directory]` (this slice) |
| log header | 270–277 | `...[header]` |
| log row | 305–308 | `...[row]` |
| log read (duplicate check) | 290–301 | `test_triage_feedback_log.py::test_unreadable_log_is_an_error_and_appends_nothing` |

**Gaps:** none. The one exit-2 arm with no test is `cd "$repo_root"` failing
after a successful `rev-parse` (lines 37–42). That is the residual bound,
stated in the SUT comment and in the outline's Item 2.2 notes ("No input
provokes it without fault injection"). It is not a gap.

## Mutation run (single, restored)

- **Mutant**: `mkdir -p "$log_dir" || {` → `mkdir -p "$log_dir" 2>/dev/null || {`
  - Applied by exact-string replacement, with a count of 1 checked first.
  - This is the mutant that tests the new positive.
- **Result**: `[directory]` red on
  `assert str(log_dir.relative_to(repo)) in result.stderr`, with
  `assert 'plans/reports' in ''`. `[header]` and `[row]` passed (1 failed,
  2 passed).
- **Restore**: the same replacement was applied with the two strings
  swapped. After it, `command grep -c '"$log_dir" 2>/dev/null'` gave 0 and
  `git diff --stat -- plugin/bin/triage-feedback.sh` was empty.

## Fixes Applied

- `tests/test_triage_feedback_log.py:176-188`: the two setup conditionals
  became one `if/elif/else` chain, one branch per case.
- `tests/test_triage_feedback_log.py:206`: the stderr positive
  `"Permission denied"` became the operand path `plans/reports`.
- `tests/test_triage_feedback_log.py:166-170`: the docstring names the
  asserted path and states the localisation and BSD residual bound.
- `tests/test_triage_feedback_behavioral.py:7-11`: the module docstring
  places each failure arm in its actual module.

## Verification

- `PATH=.venv/bin:$PATH just precommit`, run in the foreground. Tests ran
  and were not cached. The summary was `421/422 passed, 1 xfail`, followed
  by the version, line-limit and design-link checks and `Precommit OK`. The
  three oversized-file warnings are pre-existing agent files, outside this
  slice.
- `.venv/bin/pytest -p no:markdown_report tests/test_triage_feedback*.py`:
  33 passed.
- Line counts: `tests/test_triage_feedback_log.py` 263,
  `tests/test_triage_feedback_behavioral.py` 223.
- Uncommitted (nothing was committed): the two test modules and this report.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m4: every triage failure arm tested, including the behavioural grep | Satisfied | definition grep (this slice), classification grep and sed (slice 2) |
| m5: the `changed-files.sh` error is printed, then exit 2 | Satisfied | `test_changed_files_error_is_printed_then_exit_2` (slice 1) |
| m6: usage exits 1 | Satisfied | `test_usage_error_exits_1` (slice 1) |
| Interfaces: unwritable log directory gives exit 2, `ERROR:` last, no row | Satisfied | `[directory]` case |

## Positive Observations

- The definition-grep shim runs the real tool before it fails. A guard keyed
  on output rather than status therefore cannot pass.
- The `Simple` + `def` fixture reaches a row on either misreading of the
  failure ("no" leads to `match`, a match leads to `underclassified`), so the
  no-row assertion discriminates.
- The `directory` tail assertion pins the `ERROR:` line once, right after
  the verdict. That is what separates the `mkdir` guard from the header
  guard, which prints the same line.
