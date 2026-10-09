# Review: review-fixes-4 Item 1.1 slice 1, code review (GREEN)

**Scope**: `plugin/bin/triage-feedback.sh` as changed by the slice commit (the
residual-bound comment above the repository-root `cd` guard). Tests out of scope.
**Date**: 2026-10-09
**Mode**: review + fix

## Summary

The GREEN change is comment-only (7 lines, +4/-3). It narrows the residual
bound to the script-directory `cd`, drops the claim that no input provokes the
root `cd`, and names the test that pins the root guard. Every claim in the
comment checks out against the script. No issues found; no edits made.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Checks

- Script-directory `cd` sits above: `triage-feedback.sh:21`, inside the
  `script_dir=$(cd "$script_dir" && pwd) || {...}` assignment, ahead of the
  comment at lines 40-43. True.
- Builtin fed by `BASH_SOURCE`: `script_dir` comes from
  `${BASH_SOURCE[0]%/*}` (lines 13-16); `cd` is a shell builtin. True.
- False claim dropped: the old "no input provokes either" is gone; the root
  guard is no longer described as untestable. The remaining "no input reaches
  its failure" is scoped to the script-directory `cd` only, as the item
  directs.
- Width: comment lines are 80, 76, 78 and 75 columns (line 40 is exactly 80,
  within the limit).
- Named test exists: `test_root_cd_failure_is_one_error_line` at
  `tests/test_triage_feedback_failures.py:120`.
- Minimal growth: no code change, no new abstraction. `bash -n` passes. No
  `REFACTOR-NEEDED`.

## Mutated-SUT run

Mutation: replaced the guard (`if ! cd "$repo_root"; then printf ...; exit 2;
fi`) with a bare `cd "$repo_root"` via exact-string Edit. Ran
`test_root_cd_failure_is_one_error_line` once: FAILED on the stdout assertion
(`'' == 'ERROR: cannot change to <path>\n'`; bash's own `cd:` message went to
stderr). The test redded, so it detects the guard's absence. Restored by
swapping the Edit. Proof: `git diff -- plugin/bin/triage-feedback.sh` is empty
(0 bytes), `bash -n` passes, and all 9 tests in
`tests/test_triage_feedback_failures.py` pass.

## Fixes Applied

None.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Narrow comment to script-directory `cd` only | Satisfied | `triage-feedback.sh:40-42` |
| Builtin fed by `BASH_SOURCE`; new fault injection would be bash-version-dependent | Satisfied | line 41-42 |
| Drop claim that no input provokes the root `cd` | Satisfied | old text removed; line 43 points at the test |

## Positive Observations

- The comment states the residual bound for the one `cd` that stays untested
  and cites the test that now covers the other, so the two cannot drift apart
  unnoticed.
