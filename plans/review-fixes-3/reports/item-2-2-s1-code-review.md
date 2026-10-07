# Review: Item 2.2 slice 1 code review — `triage-feedback.sh` measures from the repository root

**Scope**: `plugin/bin/triage-feedback.sh` as changed by bc986e6e (absolute
`script_dir`, `rev-parse --show-toplevel` + `cd` to the root, leading `(` on
the review-report `case` pattern). Tests out of scope.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The slice resolves `script_dir` to an absolute path, then changes to the
repository root before `changed-files.sh` runs, so every root-relative path
holds from any CWD; the `(` pattern fix makes the script parse under bash
3.2.57. The new `$(cd "$script_dir" && pwd)` introduced a CDPATH regression
(reproduced, fixed). The bash 3.2 paren had no reason in the file, so a
reason comment was added. The slice-2 guard is absent as intended.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **An exported CDPATH corrupts the new `script_dir` resolution**
   - Location: `plugin/bin/triage-feedback.sh:19` (before the fix)
   - Problem: `cd` with a relative operand that does not start with `./` or
     `../` searches CDPATH. When it resolves through a CDPATH entry, `.`
     included, it prints the destination to stdout, so the capture holds two
     lines. A decoy entry also sends it to another directory. Reproduced on
     the real script in a scratch repo with `plugin` symlinked in, invoked as
     `plugin/bin/triage-feedback.sh nojob` with `CDPATH=.`:
     `line 33: /tmp/cdprepo/plugin/bin\n/tmp/cdprepo/plugin/bin/../skills/build/scripts/changed-files.sh: No such file or directory`,
     `ERROR: changed-files.sh exited 127`. Without CDPATH the same run gives
     the correct `NO-BASE:` line. The same failure appears under bash 5 and
     bash 3.2. Before this slice, nothing ran `cd`, so this is a regression.
     Relative invocation from the root is how `/build` runs these scripts.
   - Fix: `unset CDPATH` before the resolution, with a reason comment. This
     follows `scripts/release.sh:25` and the shell-gotchas rule.
     `cd "$repo_root"` was never affected, because `rev-parse` output is
     absolute.
   - **Status**: FIXED. After the fix, the same `CDPATH=.` run prints
     `NO-BASE: …`, `ERROR: changed-files.sh exited 1` under both bash 5 and
     bash 3.2. No test pins this. Tests are outside this review's scope, so
     see Recommendations.

### Minor Issues

1. **The bash 3.2 `(` pattern carries no reason in the file**
   - Location: `plugin/bin/triage-feedback.sh:76` (before the fix)
   - Note: The leading `(` is the only parenthesised `case` pattern in the
     file. The suite catches its removal only when a bash 3.2 binary is
     first on `PATH`, which is not the default gate. Nothing in the file
     stops a later edit from "normalising" it back to the form that fails to
     parse on macOS.
   - **Status**: FIXED. A two-line comment above the `case` now states that
     inside `$(…)`, bash 3.2 reads a bare pattern's `)` as the end of the
     substitution.

## Checks with no finding

- **Absolute `script_dir`**:
  - A `script_dir` of `.` (bare-name invocation from the script's directory)
    becomes `pwd`, which is correct.
  - For a relative path through a directory symlink, the slice test runs
    `../../plugin/bin/...` from `repo/sub` via a `plugin` symlink. Logical
    `pwd` and the kernel's `..` resolution reach the real `skills/`, and the
    test passes.
  - A symlink to the file itself resolves to the link's directory. That
    limit is pre-existing and documented in `verify-step.sh`.
- **Header comment accuracy**: the D-90 comment's claim that
  `changed-files.sh` "reads the same `git rev-parse --show-toplevel`" holds
  (`changed-files.sh:84`). D-90 is the outline's sanctioned mapping for KD-6,
  and no KD-N appears in the script. The D-90 paragraph at line 28 still
  matches the code.
- **Slice 2 boundary**: a failing `rev-parse` or `cd` still exits through
  `set -e` with git's or bash's own message. There is no `ERROR:` guard and
  no residual-bound comment. This is deliberate, so slice 2's RED can still
  fail.
- **`2>/dev/null`**: none in the script. The `compgen … > /dev/null` at the
  review-artifact check discards stdout and is pre-existing.
- **Other `case` statements**: the `grep_status` cases are outside `$(…)`
  and need no paren.

## Fixes Applied

- `plugin/bin/triage-feedback.sh:17-21`: added `unset CDPATH` before
  `script_dir=$(cd "$script_dir" && pwd)` and extended the comment with the
  reason.
- `plugin/bin/triage-feedback.sh:77-78`: added a comment explaining the
  leading `(` on the review-report `case` pattern.

## Verification

- `bash --version` with `/tmp/claude-1000/bash32/bin` first on `PATH`:
  `GNU bash, version 3.2.57(2)-release`.
- `/tmp/claude-1000/bash32/bin/bash -n plugin/bin/triage-feedback.sh`: exit
  0, both before and after the fixes.
- Bash 3.2 triage suite
  (`PATH=/tmp/claude-1000/bash32/bin:$PATH .venv/bin/pytest -p no:markdown_report tests/test_triage_feedback*.py`):
  24 passed, before and after the fixes.
- **Mutated-SUT run** (once, before the fixes): replaced
  `cd "$repo_root"\n` with `: "$repo_root"\n` by exact-match replacement,
  then ran `test_subdirectory_run_measures_the_repository_root`. The test
  went **red** on `assert "- Reports: 1"`, with output `- Files changed: 1`,
  `- Reports: 0`, `- Behavioral code: no`. Restored by the inverse
  replacement, and `cmp` against a pre-mutation copy matched.
- `PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit` (foreground,
  tests not cached): `Version consistent: 0.3.0`;
  `412/413 passed, 1 xfail`; line limits (warnings only: `corrector.md` 682,
  `outline-corrector.md` 450, `design-corrector.md` 460, none touched);
  `design-links: 94 decisions indexed, defined once, conclusions match, 9 nodes present`;
  `Precommit OK`.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m1 / KD-6 (slice 1): measure from the root from any CWD | Satisfied | `triage-feedback.sh:27-28` `rev-parse --show-toplevel` + `cd`; slice test passes, mutated SUT reds |
| KD-6: `script_dir` absolute before the change | Satisfied | `triage-feedback.sh:21`, CDPATH-safe after the fix |
| Item 2.2 note: parses and passes under bash 3.2 | Satisfied | `bash -n` exit 0; 24/24 under 3.2.57 |
| KD-6 `rev-parse`/`cd` failure → one `ERROR:`, exit 2 | Deferred to slice 2 | Deliberately absent |

## Positive Observations

- The root change is placed before `changed-files.sh` runs, as KD-6
  requires. Every later root-relative path (`reports_dir`,
  `classification_file`, `log_dir`) is then correct without edits.
- The slice test's symlinked, relative `BASH_SOURCE` exercises exactly the
  case the absolute resolution exists for. The test reds when the `cd` is
  removed.

## Recommendations

- **Test gap, for the orchestrator**: no test pins the CDPATH fix. Tests are
  outside a code review's scope. A candidate slice for a list revision: a
  relative invocation with `CDPATH=.` in the environment exits 0 with the
  root's evidence. Removing `unset CDPATH` reds it, with
  `changed-files.sh` exiting 127.
