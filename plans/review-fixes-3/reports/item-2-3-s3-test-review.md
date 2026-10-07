# Review: Item 2.3 slice 3 test review (`item-2-3-s3-test-review`)

**Scope**: uncommitted changes in `tests/test_triage_feedback_behavioral.py`
and `tests/test_triage_feedback_log.py`, plus
`plans/review-fixes-3/reports/item-2-3-s3-red.md`. The SUT,
`plugin/bin/triage-feedback.sh`, was mutated in place only and restored each
time.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

Both tests carry a mutation proof. Each proof was reproduced with a
different mutation of my own, and each test redded on its own assertion. Test
1 (`test_failing_definition_grep_is_an_error_not_no`) has no wrong-reason
path. The `[directory]` case did have one. With the `mkdir` guard swallowed,
or with the guard printing but not exiting, the header write fails next on
the same missing directory. Its guard prints the identical `ERROR:` line and
exits 2, so all three cases stayed green. Fixed by pinning the stdout tail
and stderr. Both mutants now red, and so does the RED report's own mutant.

**Overall Assessment**: Ready

## Mechanical check: mutation proofs reproduced

Each mutation was an exact-string replacement with its count checked as 1
first. It was restored by applying the same replacement with the two strings
swapped. After each restore, `command grep` for the mutant text gave 0 hits
and `git diff -- plugin/bin/triage-feedback.sh` was 0 bytes.

| Test | My mutation (differs from the RED's) | Result |
|---|---|---|
| `test_failing_definition_grep_is_an_error_not_no` | `grep_status=${PIPESTATUS[1]}` → `grep_status=1`. This is the status capture, unique to the behavioural grep. The failure reads as "no". | Red on `assert result.stdout.splitlines() == ["ERROR: grep failed"]`. The run printed `Behavioral code: no` and a verdict. |
| `test_unwritable_log_is_an_error_not_a_usage_exit[directory]` | `exit 2` → `exit 1` in the `mkdir` guard, taken with the following `if [[ ! -f "$log_file" ]]; then`, which makes it unique. | Red on `assert result.returncode == 2` (line 205). `[header]` and `[row]` passed. |

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`[directory]` cannot tell the `mkdir` guard from the header guard**
   - Location: `tests/test_triage_feedback_log.py`,
     `test_unwritable_log_is_an_error_not_a_usage_exit`, `directory`
     branch
   - Problem: the `mkdir` guard and the header-write guard print the same
     `ERROR: cannot write plans/reports/triage-feedback-log.md` and both
     exit 2. If the `mkdir` failure falls through, the header redirection
     fails next on the same missing directory, and its guard supplies the
     expected line and exit code. Two mutants were measured against the
     tests as received:
     - `mkdir -p "$log_dir" || {` → `mkdir -p "$log_dir" || true || {`
       (failure swallowed): 3 passed.
     - The guard's `exit 2` dropped, so it prints and continues: 3 passed.
       The duplicate `ERROR:` line was still the last stdout line.

     A probe of the unmutated case showed stderr is exactly `mkdir`'s one
     line. Under the swallow mutant, stderr adds `triage-feedback.sh: line
     271: plans/reports/triage-feedback-log.md: No such file or directory`.
   - Fix: for `directory`, two assertions replace the last-line check:
     - `stdout.splitlines()[-3:] == ["## Verdict", "match", error]`. This
       pins the error to appear once, directly after the verdict the run
       reached.
     - On stderr, `"Permission denied" in stderr` with
       `log.name not in stderr`. The positive shows `mkdir`'s diagnostic is
       surfaced. The negative shows nothing tried to write the log.

     Both substrings hold for GNU (`mkdir: cannot create directory
     'plans/reports': Permission denied`) and BSD (`mkdir: plans/reports:
     Permission denied`) `mkdir`. The test docstring gained the reason
     stderr is pinned.
   - **Status**: FIXED

### Minor Issues

None.

## Wrong-reason hunting, checked with no finding

- **Could `ERROR: grep failed` come from the classification grep?** No. The
  script's grep calls are line 152 `grep -qE` (definition) and line 176
  `grep -E` (classification). `changed-files.sh` has no grep call (its only
  hit, line 34, is a comment). The shim tests each argument for an exact
  `-qE`, so it cannot fire on the classification grep. The definition grep
  also runs first and exits the script. `shim: fail` on stderr shows the shim
  fired. My mutant above red the test without touching the classification
  arm.
- **Does "no row" discriminate?** Yes. The fixture is `Simple` with a `def`.
  A swallow-as-"no" path reaches `match` and a swallow-as-match path reaches
  `underclassified`, and both log a row. The RED's unfaulted control logs
  `underclassified`. The stdout equality is the stronger assertion anyway,
  since any continuation prints `## Evidence`.
- **Shim form**: the shim is written by `_write_shim` with the real path from
  `shlex.quote`. It runs the real grep before exiting 2, so the pipe is
  drained and a guard that keyed on output instead of status could not pass.
  Every other call goes through `exec "$real" "$@"`.
- **Mode 555 restore and root skip**: the `os.geteuid() == 0` skip precedes
  the fixture. `finally` restores `plans/` to 755 first, then `plans/reports`
  if it exists, then the log. Each is reachable at that point, so cleanup
  never meets an unreadable tree. For `header` and `row`, `plans/` was never
  chmodded, and setting it to 755 is harmless.
- **Would `[directory]` pass wrongly if `plans/reports/` existed?** No.
  `_commit_reports_fixture` creates `plans/j/...` and never `plans/reports`.
  If the directory existed it would be writable, the run would log a row
  and exit 0, and the case would red rather than pass. No precondition
  assertion was added, because the failure would already be loud.
- **Docstrings and IDs**: summaries are 70 characters or fewer, no `KD-N` or
  plan-item IDs appear, and no docstring was shortened. The behavioural
  module's docstring is accurate: `test_failing_diff_is_an_error_not_no`
  also lives there.

## Fixes Applied

- `tests/test_triage_feedback_log.py:200-204`: in the `directory` branch,
  the stdout last-line check became a three-line tail check, plus a stderr
  positive and negative.
- `tests/test_triage_feedback_log.py:164-167`: the test docstring now says
  why stderr is pinned.

## Post-fix verification

Mutants on `[directory]`, each restored and verified (`command grep` 0 hits,
SUT diff 0 bytes):

| Mutant | Result after fix |
|---|---|
| `|| true ||` (swallowed) | red at line 204, `log.name not in result.stderr` |
| guard prints, no `exit 2` | red at line 202, the stdout tail |
| guard `exit 1` (my proof mutant) | red at line 205, the returncode |
| guard dropped (RED report's mutant) | red at line 199, `error in result.stdout` |

Each mutant redded `[directory]` only (1 failed, 2 passed).

Unmutated final run:

```
.venv/bin/pytest -p no:markdown_report -q tests/test_triage_feedback_behavioral.py tests/test_triage_feedback_log.py
13 passed
```

Gate: `ruff check` passes, `ruff format --check` reports both files already
formatted, and `docformatter -c` passes. Line counts are 260 for
`tests/test_triage_feedback_log.py` and 222 for
`tests/test_triage_feedback_behavioral.py`.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m4: the behavioural grep's failure arm is tested | Satisfied | `test_failing_definition_grep_is_an_error_not_no` |
| Interface: exit 2, `ERROR:` and no row for an unwritable log directory | Satisfied | `test_unwritable_log_is_an_error_not_a_usage_exit[directory]`, now pinned to the directory guard |

## Positive Observations

- The definition-grep shim runs the real tool before failing, so only the
  status carries the fault, and that closes the output-keyed guard gap from
  slice 2.
- The `Simple` + `def` fixture makes "no row" discriminate both ways a
  failure could be misread.
