# Review: Item 1.1 slice 2 — code review (review-fixes-2)

**Scope**: the Reports count `787349b0` added to
`plugin/bin/triage-feedback.sh`, with the script re-audited where it
changed, under `shell-scripting:shell-gotchas` (bash 3.2 and macOS
included). Tests were read for context and extended where a fix changed
behaviour.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The GREEN implements KD-1's Reports rule correctly: `<base> HEAD` additions
directly under `plans/<job>/reports/`, minus `item-<N>-<M>.md` and the
review-gate reports, with the pathspec after `--` (m4) and a git failure
reaching `ERROR:` and exit 2. Two defects were in the read. First, a
here-string, which m5 rules out. Second, a newline-delimited read under
`core.quotepath=off`. That setting is applied per call (`git -c`), so the
GREEN's non-ASCII claim holds. But git C-quotes any name holding `"`, `\`
or a control byte whatever `core.quotePath` says, and such a name escapes
the exclusions. Both defects are fixed by a NUL-delimited read, as in
`changed-files.sh`. Two tests now pin the read and its failure path.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Report names read in git's quoted form, not byte-exact**
   - Location: `plugin/bin/triage-feedback.sh:55-73` (HEAD)
   - Problem: `git -c core.quotepath=off diff --name-only` stops quoting
     only bytes ≥ 0x80. Probed: `r/café.md` prints raw, but
     `r/review-a"b.md` prints `"r/review-a\"b.md"` and a tab name prints
     `"r/x\ty.md"`. The quoted basename ends `.md"`, so a review-gate report
     whose name holds `"` misses `review-*.md` and counts. The comment's
     "a path holding a newline counts as two" was also false: git C-quotes
     such a name onto one line. `changed-files.sh` reads `-z` with
     `read -r -d ''`, and that is the consistency bar.
   - Fix: the reports diff takes `-z` and the loop takes `read -r -d ''`.
     `-c core.quotepath=off` is dropped, because `-z` disables quoting.
     The comment states why. New test `test_reports_read_names_byte_exact`.
   - **Status**: FIXED

2. **Here-string in the reports loop (m5)**
   - Location: `plugin/bin/triage-feedback.sh:73` (HEAD), `done <<< "$added_reports"`
   - Problem: KD-1 m5 says no here-string. A NUL stream cannot be held in a
     bash variable in any case, so fix 1 needs a pipe.
   - Fix: `git diff … -z | while … printf x; done | wc -c | tr -d ' '`
     inside `if ! reports_count=$(…)`. Under `pipefail` a failing
     `git diff` fails the assignment, which gives `ERROR: git diff failed`
     and exit 2. The count leaves the subshell as one `x` per report. The
     `[[ -n $report_path ]]` guard goes, because `-z` yields no empty
     records. `wc -c | tr -d ' '` handles BSD padding.
   - **Status**: FIXED

3. **Reports-diff failure path untested**
   - Location: `plugin/bin/triage-feedback.sh` reports block
   - Problem: the pipe form loses the diff's status as soon as anything
     masks the substitution's exit, and no test reached the path.
     `test_failing_diff_is_an_error_not_no` deletes a blob. A name-only
     diff reads trees only, so the reports diff succeeds there. And any
     tree corruption fails `changed-files.sh`'s diff first.
   - Fix: `test_failing_reports_diff_is_an_error_not_none` puts a `git` shim
     on `PATH` that fails only `git diff … --diff-filter=A`, and asserts
     `ERROR: git diff failed`, no `- Reports:` and exit 2. `_run_triage`
     gains `path_prepend`, following `tests/line_limits_helpers.py`.
   - **Status**: FIXED

### Minor Issues

None.

## Fixes Applied

- `plugin/bin/triage-feedback.sh` reports block: NUL-delimited pipe count
  replaces the here-string loop. Comment rewritten: the NUL read and why,
  and the `pipefail` capture. `--no-color --no-ext-diff` dropped from the
  name-only diff, matching `changed-files.sh`. Probed:
  `color.diff=always`, `color.ui=always` and `diff.external` leave
  `--name-only -z` output as bare `f\0`.
- `tests/test_triage_feedback.py`: added
  `test_reports_read_names_byte_exact` and
  `test_failing_reports_diff_is_an_error_not_none`, and the `shutil`
  import. The module goes from 252 to 310 lines.
- `tests/triage_feedback_helpers.py`: `_run_triage(job, cwd,
  path_prepend=None)`. The module goes from 113 to 121 lines.

Files changed: `plugin/bin/triage-feedback.sh`,
`tests/test_triage_feedback.py`, `tests/triage_feedback_helpers.py`.

## Mutation proof

Each mutation was an exact in-place replacement on the real SUT, run, then
restored by the inverse replacement.

| Mutation | Tests run | Result |
|---|---|---|
| GREEN's read restored: `git -c core.quotepath=off diff … --diff-filter=A` without `-z`, `read -r` without `-d ''` | module | RED: `test_reports_read_names_byte_exact` at `- Reports: 1` (got `Reports: 2`). The other 7 were green |
| Status masked: `wc -c \| tr -d ' ')` → `wc -c \| tr -d ' '; true)` | module | RED: `test_failing_reports_diff_is_an_error_not_none` at `ERROR: git diff failed` (stdout `Reports: 0`, exit 0). The other 8 were green |
| Single-digit item pattern `^item-[0-9]-[0-9]\.md$` | module | RED: `test_reports_exclude_the_per_item_report` (`Reports: 1`). The other 8 were green |

## Audit notes

- m4: the reports pathspec follows `--`. The behavioural `git diff` at
  `:88` has no `--`. That belongs to slices 3 and 5 (list pathspecs, a
  tracked `HEAD`), so it is not flagged.
- m5: the remaining here-string, `grep -qE … <<< "$committed_diff"`,
  belongs to slice 3, which rewrites it. Left as instructed.
- The job name reaches the `:(glob)` pathspec unvalidated by triage, but
  `changed-files.sh` runs first and rejects `*?[\` and `/`, with exit 2.
- The pathspecs and the `plans/<job>/…` file paths are CWD-relative, so the
  script assumes the repo root, as it did before this slice (the test
  helpers and `finishing.md` §2 run it there). Not a finding of this diff.
- bash 3.2: `read -d ''`, `[[ =~ ]]` with the regex in a variable, and
  `case` inside a `$( … )` pipeline all work there. No GNU-only flags.

## Requirements Validation

| Requirement (slice 2 scope) | Status | Evidence |
|---|---|---|
| Reports = `<base> HEAD` additions directly under `reports/` | Satisfied | `--diff-filter=A`, `:(glob)…/*`; test review's mutants M5 and M6 |
| minus `item-<N>-<M>.md` | Satisfied | `item_report_re`; single-digit mutant reds |
| minus `review.md`, `review-*.md`, `final-review.md` | Satisfied | `case` arm; now byte-exact |
| m4 pathspecs after `--` | Satisfied (reports diff) | slice 3/5 own the other diff |
| m5 no here-string | Satisfied (reports loop) | slice 3 owns the grep one |
| git failure → `ERROR:` stdout, exit 2, no row | Satisfied | new shim test, with a mutation proof |
| Comments cite D-numbers (m8) | Satisfied | D-90 |

## Verification

- `tests/test_triage_feedback.py`: 9/9 passed.
- `shellcheck plugin/bin/triage-feedback.sh`: clean.
- `just precommit`: version consistent, 387/388 passed plus 1 xfail, line
  limits, design links. Precommit OK. The three `oversized-file` warnings
  are on the corrector agents, which this slice does not touch.

## Positive Observations

- The capture-then-loop structure already guarded the git failure. The fix
  keeps that guarantee through `pipefail` and does not drop it.
- The test review's strengthened fixture (two-digit item, a revised
  pre-base report, a report below `reports/`) carried over unchanged and
  still discriminates.
