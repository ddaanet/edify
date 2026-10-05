# Review: Item 1.2 slice 1 test review — idempotent triage log append

**Scope**: uncommitted `tests/test_triage_feedback_log.py` (new),
`tests/triage_feedback_helpers.py` (`_commit_reports_fixture`),
`tests/test_triage_feedback.py` (calls it), RED report
`item-1-2-s1-red.md`. SUT `plugin/bin/triage-feedback.sh` read-only.
**Date**: 2026-10-05
**Mode**: review + fix (TDD test review)

## Summary

The RED test reds on its assertion and the fixture move is behaviour-neutral,
but three plausible wrong implementations named in the dispatch passed the
test: a substring match on the row, a match ignoring the job column, and a
skip that reads only the last row. The pre-seeded leg also never checked the
header. Fixed by adding a decoy-row leg and seeding the decoy after the
matching row; every mutant now reds and a correct implementation passes.

**Overall Assessment**: Ready

## Mechanical check

- `test_rerun_appends_no_duplicate_row` FAILED on an assertion against the
  unchanged SUT, before and after the fixes: `tests/test_triage_feedback_log.py:54`
  `assert rows == [first_row]`, the second run holding
  `| 2026-10-05 | j | Simple | 1 | 0 | no | match |` twice. No ERROR.
- `tests/test_triage_feedback.py` and `tests/test_triage_feedback_behavioral.py`:
  16 passed.
- `test_reports_exclude_the_per_item_report`: `_commit_reports_fixture` runs
  `_init_repo` then the same four commits (planning, `_commit_item_report`
  with `notes.txt`, item 1.12, review) with the same paths, contents and
  messages as the HEAD version. The only reordering is the
  `classification = …` path binding, which now follows the commits; it is a
  `Path` value with no side effect. Assertions unchanged. Equivalent.
- Ruff check and format check pass on the three files. Line counts: 85, 339,
  157.

## Mutation run

Each mutant replaced the append line in a copy of `plugin/` under the
scratchpad (`$script_dir` resolution kept intact), with
`triage_feedback_helpers.SCRIPT` repointed at the copy; the repo SUT was not
touched. The skip compares `rest`, the row with `| <date> | ` stripped.

| Mutant | RED-phase test | Revised test |
|---|---|---|
| correct (every column but the date) | pass | pass |
| skip keyed on job alone | red, last leg | red, last leg (line 78) |
| skip on whole line incl. date | red, pre-seeded leg | red, pre-seeded leg (line 69) |
| substring match `*"$new_rest"*` | **pass** | red, decoy leg (line 60) |
| last row only (`tail -n 1`) | **pass** | red, pre-seeded leg (line 69) |
| every column but date and job | **pass** | red, decoy leg (line 60) |

## Issues Found

### Major Issues

1. **Substring and job-agnostic matches survive**
   - Location: `tests/test_triage_feedback_log.py` pre-seeded leg
   - Problem: the only pre-seeded row was the run's own row, so a match on
     any substring of it, or on every column but date and job, skipped
     exactly as the correct comparison does. KD-2 requires equality in every
     column but the date.
   - Fix: a leg seeding only a decoy row for job `other-j`, otherwise equal
     — its text from the job name on contains the run's row from the job
     name on — and asserting the run still appends its own row after it.
   - **Status**: FIXED

2. **A last-row-only comparison survives**
   - Location: same leg
   - Problem: the matching row was always the log's last row, so `tail -n 1`
     satisfied every leg. KD-2 says "the log already holds a row equal".
   - Fix: the pre-seeded log holds the run's row under `2000-01-01` followed
     by the decoy; the run must append nothing.
   - **Status**: FIXED

### Minor Issues

1. **Pre-seeded leg ignores the header and allows a rewrite**
   - Location: pre-seeded and last legs
   - Problem: both compared `splitlines()[2:]` only; a skip that rewrote the
     header, or the last leg rewriting earlier rows, went unchecked.
   - Fix: both legs compare the whole file — `lines == seeded`, then
     `lines[:4] == seeded` plus one new row.
   - **Status**: FIXED

2. **Last leg's row assertion is a substring**
   - Location: final assertion
   - Problem: `"| 2 | 0 | no | match |" in rows[1]` accepted any job and
     predicted label.
   - Fix: `_undated(lines[4]) == "j | Simple | 2 | 0 | no | match |"`.
   - **Status**: FIXED

3. **First row not pinned against known values**
   - Location: first leg
   - Problem: the seeded and decoy rows were derived from whatever the first
     run wrote; fixture drift (e.g. verdict) would go unnoticed and the
     seeded rows would follow it.
   - Fix: `_undated(first_row) == "j | Simple | 1 | 0 | no | match |"`, and
     the seeded and decoy rows are built from that literal.
   - **Status**: FIXED

4. **Module docstring cites D-90 for the one-row-per-evidence rule**
   - Location: module docstring
   - Problem: D-90 is the changed-files list definition; no decision record
     holds the log rule yet (it is KD-2 of this plan).
   - Fix: attribution dropped. The line-cap split reason stays.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_triage_feedback_log.py` — decoy-only leg (append expected),
  pre-seeded leg with the decoy after the matching row and a whole-file
  comparison, whole-file prefix check and exact undated row in the last leg,
  first row pinned to a literal, `_undated` helper defined after its user,
  test and module docstrings updated. The slice's four named legs and their
  assertions are kept.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Slice: first run leaves header + one row | Satisfied | lines 46–50 |
| Slice: same run again leaves exactly one row | Satisfied | lines 52–54 (reds on the SUT) |
| Slice: pre-seeded row under another date gains none | Satisfied | lines 64–69 |
| Slice: item-1-2.md + c.txt appends a second row | Satisfied | lines 71–80 |
| KD-2: equal in every column but the date | Satisfied | mutation table |

## Positive Observations

- Fixture moved to the helper instead of duplicated; the module split keeps
  `test_triage_feedback.py` at 339 lines with the reason in the docstring.
- The RED report states honestly which legs were not reached against the
  unchanged SUT.
