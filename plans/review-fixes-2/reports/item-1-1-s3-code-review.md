# Review: Item 1.1 slice 3 — code review (review-fixes-2)

**Scope**: HEAD `e4b3f5b4`'s behavioural-code computation in
`plugin/bin/triage-feedback.sh`. The script was re-audited wherever the commit
touched it. Tests are out of scope except for one new test, plus the module
split it forced.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The GREEN limits the diff to the list's paths correctly: literal pathspecs after
`--`, `--no-renames`, no diff on an empty list, and the git failure is caught by
the capture. The grep pipe was the weak point. Its correctness depended on grep
reading all of its stdin, and `pipefail` then read the pipeline's status rather
than grep's. That is fixed: grep's own status now decides, an early match is
pinned by a new test, and the mutation reds it.

**Overall Assessment**: Ready

## SIGPIPE probe (the lead's specific question)

The GREEN form is `printf '%s\n' "$committed_diff" | grep -E … > /dev/null`
under `pipefail`, then `elif [[ $? -ne 1 ]]`. The diff is captured first, so
the producer is `printf`, not `git diff`. A failing `git diff` therefore cannot
read as "no", and a SIGPIPE'd git cannot read as an error.

Measured here: GNU grep 3.11 (`/usr/bin/grep`, which the script resolves) and
bash 5.2.

- A 2.3 MB diff whose first added line is `def foo():` gave pipeline statuses
  `0 0` over 5 runs with `> /dev/null`. The full script printed `yes` and
  exited 0 over 3 runs. The GREEN form was **not broken on this platform**.
- With `-q`, the same pipe gave `141 0`. The GREEN's `elif` would then print
  `ERROR: grep failed` and exit 2.
- The reason is GNU grep NEWS 2.27: "Unless an early-exit option like -q, -l,
  -L, -m … grep now reads all of a non-seekable standard input … This works
  better with nonportable scripts that run `PROGRAM | grep PATTERN >/dev/null`".
  GNU 2.26 stopped early. Whether another grep reads all its input is not
  specified anywhere.
- With SIGPIPE ignored by the caller (`trap '' PIPE`), `printf` exits 1 on
  EPIPE instead. Under `pipefail`, any grep that stops early would turn that
  1 into a silent "no".

## Issues Found

### Major Issues

1. **Behavioural code read the pipeline's status, not grep's**
   - Location: `plugin/bin/triage-feedback.sh` (grep after the captured diff)
   - Problem: under `pipefail`, a grep that exits at its first match makes
     `printf` die of SIGPIPE (141). The script then reports `ERROR: grep
     failed` and exits 2 on a large diff with an early definition. Where
     SIGPIPE is ignored, `printf` exits 1 and the result reads "no". GNU grep
     ≥ 2.27 avoids this only by reading all its input when there is no
     early-exit option. GNU calls that usage nonportable, and nothing pins it.
   - Fix: `grep -qE … || grep_status=${PIPESTATUS[1]}`, then a `case`: 0 is
     `yes`, 1 is `no`, anything else prints `ERROR: grep failed` and exits 2.
     `-q` makes the early exit deterministic, so the test exercises the
     SIGPIPE path on every run. Ignoring `printf`'s status is sound: the diff
     is already captured, and its only failure is EPIPE after grep exits. The
     comment says so. There is still no here-string (m5).
   - Test: `test_early_match_in_a_large_diff_is_not_an_error` commits an
     `a.py` holding `def foo():` followed by 200,000 `x = 1` lines (about
     1.2 MB). It asserts `- Behavioral code: yes` before exit 0.
   - Mutation, in place: `grep_status=${PIPESTATUS[1]}` →
     `grep_status=$?`. The new test **redded** on its stdout assertion
     (`assert '- Behavioral code: yes' in ['ERROR: grep failed']`, exit 2),
     and the other 4 behavioural tests passed. Restored by the inverse edit.
   - **Status**: FIXED

### Minor Issues

1. **Residual-bound comment overclaimed "matches nothing"**
   - Location: `plugin/bin/triage-feedback.sh`, the comment above the list
     split
   - Problem: a newline-holding name splits into two list lines. Either half
     matches a path that the range changes and that has that exact name, for
     example an exempt `inbox/x.md` when the name is `inbox/x.md\nfoo`. That
     path's definitions would then count.
   - Fix: "which match nothing unless a half names another path the range
     changes".
   - **Status**: FIXED

## Points judged, no finding

- **m5 form**: there is no here-string. Exit 1 is "no" and ≥ 2 is `ERROR:`
  exit 2, which follows `verify-step.sh`'s filter pattern. Fault injection
  confirmed it. A `grep` shim exiting 2 gave `ERROR: grep failed`, exit 2,
  with the shim's stderr intact. A shim exiting 1 gave
  `- Behavioral code: no`. No test pins the ≥ 2 case, per the outline.
- **Git failure**: the `$(git diff …)` capture is tested with `if !`, and a
  failure prints `ERROR: git diff failed` and exits 2. It is pinned by
  `test_failing_diff_is_an_error_not_no`.
- **m4**: every list path is passed as a `:(literal)` pathspec after `--`.
  `--no-renames` matches the list's own `--no-renames`.
- **Empty list**: the whole diff/grep block sits under
  `[[ -n $changed_list ]]`, so an empty list runs no diff.
- **List split**: parameter expansion, safe on bash 3.2 (no `mapfile`). The
  `$'\n'` pattern idiom matches the script's existing `changed_output`
  split. A name starting `:` is neutralised by `:(literal)`. `$(…)` strips a
  trailing newline, so no empty pathspec can arise.
- **Ignored SIGPIPE, fixed form**: with `trap '' PIPE`, the script prints
  `yes` and exits 0, plus bash's
  `line 123: printf: write error: Broken pipe` on stderr. That stderr line
  appears only when the caller ignores SIGPIPE. Python's `subprocess`
  restores the default, so it does not appear under the suite. It was left
  unsuppressed (no `2>/dev/null`, per no-stderr-suppression).

## Fixes Applied

- `plugin/bin/triage-feedback.sh`: grep status taken from `PIPESTATUS[1]`
  under `grep -qE` and dispatched by `case`; comment explains SIGPIPE and
  `pipefail`; residual-bound comment corrected.
- `tests/test_triage_feedback_behavioral.py` (new, 178 lines): the four
  behavioural-code tests moved byte-identical from
  `tests/test_triage_feedback.py`, an AST comparison against HEAD showing all
  10 of the module's existing tests unchanged:
  `test_uncommitted_definition_is_not_behavioral`,
  `test_forced_color_does_not_hide_definitions`,
  `test_failing_diff_is_an_error_not_no` and
  `test_behavioral_code_reads_the_lists_paths_only`. It also holds the new
  `test_early_match_in_a_large_diff_is_not_an_error`, and its header follows
  `tests/test_changed_files_phase.py`'s split header.
- `tests/test_triage_feedback.py` (375 → 241 lines): the moved tests are
  removed, the unused `_def_edits_pending` import is dropped, and the
  docstring points to the split. The split is on the behavioural-code seam,
  because the new test would have taken the module past 400. No docstring was
  shaved.

## Verification

- `pytest tests/test_triage_feedback.py tests/test_triage_feedback_behavioral.py`:
  11/11 passed.
- Mutation run: as reported above, 4/5 passed and the new test failed on its
  assertion. Restored.
- `shellcheck plugin/bin/triage-feedback.sh`: clean.
- `just lint`: `Lint OK`.
- `just precommit`: `Precommit OK`, covering version consistency, tests
  389/390 passed with 1 xfail (pre-existing), line limits and design links.
  The only line-limit warnings are the three allowlisted corrector agents.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| KD-1 Behavioral code: diff limited to the list's paths, literal pathspecs | Satisfied | `:(literal)` per list line after `--` |
| KD-1 `--no-color --no-ext-diff --no-renames` | Satisfied | the `git diff` invocation |
| KD-1 empty list reads `no`, runs no diff | Satisfied | `[[ -n $changed_list ]]` guard |
| KD-1 residual-bound comment | Satisfied | corrected comment |
| KD-1 Failures: git or grep failure → `ERROR:` exit 2 | Satisfied | capture check; `case` default |
| m4 pathspecs after `--` | Satisfied | as above |
| m5 no here-string; grep 1 = no, ≥ 2 = error | Satisfied | PIPESTATUS/`case` form; fault-injected |

## Positive Observations

- Capturing the diff before matching separates git's failure from grep's.
  The SIGPIPE question then reduces to the `printf` side, and that side has
  no failure of its own to lose.
- The GREEN's comment already named the here-string temp-file hazard.
  Splitting the list by parameter expansion avoids both that and `mapfile`.
