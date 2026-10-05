# Review: Item 1.2 slice 1 code review — idempotent triage log append

**Scope**: the log-append change HEAD (`ce22286e`) made to
`plugin/bin/triage-feedback.sh`, re-audited where it changed. Items 1.3
onward are out of scope.
**Date**: 2026-10-05
**Mode**: review + fix (TDD code review)

## Summary

The comparison is right on every row it reads. It strips `| ` and then the
date column by shortest-prefix expansion, and it compares the remainder whole.
The real log's ten rows parse cleanly, including the two
`Simple / Moderate agentic-prose (one route)` rows, and a job holding ` | `
compares correctly. Two defects remained, and both ended in a blind append:

- The unreadable-log `ERROR:` path never fired.
- An unterminated last line was skipped by the comparison, and the append then
  glued the new row onto it.

The data append also used `echo`. All three are fixed, each fix is pinned by a
new test, and each test was shown to fail against an in-place mutant.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

1. **Unreadable-log error path is dead; the script appends blindly and exits 0**
   - Location: `plugin/bin/triage-feedback.sh:248-257` (HEAD)
   - Problem: `if ! while …; done < "$log_file"; then`. When a compound
     command's own redirection fails, bash does not apply the `!`. Probe on
     bash 5.2: `! while …; done < f` gives status 1 for an unreadable `f`, and
     `! { while …; done < f; }` gives 0. So the condition was false, no
     `ERROR:` was printed, and the write-only log got a duplicate row with
     exit 0. KD-1 says no failure appends a log row. Nothing tested this path.
   - Fix: wrap the loop in `{ …; }` so that `!` negates the group's status.
     The comment now says why the braces are needed. New test
     `test_unreadable_log_is_an_error_and_appends_nothing` runs with a 0200
     log and checks exit 2, the `ERROR: cannot read …` line and an unchanged
     log. It skips under root, following `tests/test_line_limits_exit_codes.py`.
   - **Status**: FIXED

### Major Issues

1. **Unterminated last line: not compared, then corrupted by the append**
   - Location: `plugin/bin/triage-feedback.sh:248`, `:261` (HEAD)
   - Problem: `while IFS= read -r log_row` drops a final line that has no
     newline. If that line was the matching row, the run appended a duplicate.
     In every case `>>` joined the new row onto it:
     `… | match || 2026-10-05 | j | …`. The shell-gotchas `read` discipline
     applies here.
   - Fix: the loop condition is now
     `read -r log_row || { [[ -n $log_row ]] && log_lead=$'\n'; }`. The partial
     line is compared, and `log_lead` adds the missing newline before an
     append. New test `test_unterminated_last_row_is_compared_and_kept_whole`
     covers two cases:
     - a matching unterminated row leaves the log byte-for-byte unchanged;
     - an unterminated decoy row stays whole, and the new row lands on its own
       line.
   - **Status**: FIXED

### Minor Issues

1. **Data appended with `echo`**
   - Location: `plugin/bin/triage-feedback.sh:261` (HEAD)
   - Note: the row carries `$job_dir`, which is arbitrary data. It is now
     written with `printf '%s| %s | %s\n'`. The header `echo`s are fixed
     literals and were left as they are.
   - **Status**: FIXED

## Judged, no change

- **`|` in job or label.** `${log_rest#* | }` removes the shortest prefix, so
  only the date column is stripped and the rest is compared whole. A probe with
  job `a | b` gave one row across two runs, and a seeded unterminated row
  suppressed the append. A false match would need two different job/label
  splits to produce the same remainder. That cannot happen: a logged label is
  one of the four pipe-free class words (N-1), and every column after it is
  pipe-free.
- **Leading/trailing whitespace.** Comparison is exact. A job differing only
  in whitespace is a different job. A row with hand-added padding, trailing
  blanks or CRLF reads as different, so the run appends a row and loses
  nothing. Rows come only from this script with single-space padding, and
  `plans/` is outside rumdl's scope (`.rumdl.toml`), so no formatter pads them.
- **Real log rows.** All ten parse to date plus remainder. The two
  `Simple / Moderate agentic-prose (one route)` rows can never equal a new row
  because N-1 restricts the logged class. That is correct: KD-2 does not merge
  rows with different evidence.
- **Header creation when the log is absent.** The header is written, then
  read by the loop. Its remainder (`Job | Predicted | …`) cannot equal a row,
  because `Predicted` is not a class. The existing first-run leg covers this.
- **Here-strings and masked failures.** The change adds no here-string. The
  loop body under the `if` condition contains only assignments and `[[ ]]`, so
  disabled errexit hides nothing. The `while` status is the redirection's
  status.

## Mutation runs (in place, restored by inverse Edit)

| Mutant | Result |
|---|---|
| loop condition back to `read -r log_row` only | `test_unterminated_…` red at line 110: duplicate glued onto the seeded row |
| `printf` without `$log_lead` | `test_unterminated_…` red at line 116: decoy row joined with the new row |
| braces removed, i.e. HEAD's `if ! while … < "$log_file"` | `test_unreadable_…` red at line 142: exit 0 |

Before the fixes, both new tests also failed against HEAD's SUT, for the same
reasons.

## Fixes Applied

- `plugin/bin/triage-feedback.sh` — the duplicate-check loop is grouped in
  `{ …; }` under `if !`. The loop compares an unterminated last line and
  records `log_lead`. The append uses `printf` with `log_lead`. The comment
  covers the last-line handling and why the braces are needed.
- `tests/test_triage_feedback_log.py` — added
  `test_unterminated_last_row_is_compared_and_kept_whole` and
  `test_unreadable_log_is_an_error_and_appends_nothing`, plus the `os`,
  `pytest` and `_run_triage` imports. The module is 149 lines.

## Verification

- `shellcheck plugin/bin/triage-feedback.sh`: clean.
- Triage tests (`test_triage_feedback{,_log,_behavioral}.py`): 19/19 pass.
- `just precommit`: `Precommit OK`. 397/398 passed with 1 xfail. Version
  consistency, line limits and design links passed. The three
  `oversized-file` warnings for `plugin/agents/*corrector.md` existed before
  this change.

## Files changed

- `plugin/bin/triage-feedback.sh`
- `tests/test_triage_feedback_log.py`
