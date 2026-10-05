# Review: Item 1.1 slice 1 — test review (review-fixes-2)

**Scope**: `tests/test_triage_feedback.py`, `tests/triage_feedback_helpers.py`
(both uncommitted), `plans/review-fixes-2/reports/item-1-1-s1-red.md`. SUT
`plugin/bin/triage-feedback.sh` read only, unchanged.
**Date**: 2026-10-05T16:07:36Z
**Mode**: review + fix

## Summary

The RED moves every surviving test to the `<job>`-only call, commits an
`item-1-1.md` report in every fixture, deletes
`test_simple_with_review_reports_matches`, and adds
`test_files_changed_is_the_review_gates_list` to the slice's spec. All five
tests red on an assertion against the usage exit, before and after the fixes.
Probing each fixture with the real `changed-files.sh` confirms it derives the
intended base and list. The fixes: two wrong D-number citations, an
interface clause no test pinned (`ERROR:` on a git failure), a dead helper
return, and a lint error that would have failed precommit.

**Overall Assessment**: Ready

## Mechanical check

`.venv/bin/pytest tests/test_triage_feedback.py` (`uv run` cannot take its
cache lock in the sandbox, so the venv's pytest was run directly). The module
holds five tests. All five FAILED, none PASSED, none ERROR, before and after
the fixes:

| Test | Origin | Fails at |
|---|---|---|
| `test_files_changed_is_the_review_gates_list` | new (slice 1) | `assert '- Files changed: 2' in []`, the stdout assertion, ahead of the exit-code one |
| `test_files_changed_counts_committed_changes_only` | moved | `_triage_lines` exit assertion, `Usage: triage-feedback.sh <job-dir> <baseline-commit>` |
| `test_uncommitted_definition_is_not_behavioral` | moved | same, first call |
| `test_forced_color_does_not_hide_definitions` | moved | same |
| `test_failing_diff_is_an_error_not_no` | moved | `assert 1 == 2` on the return code |

`HEAD`'s module had six tests. `test_simple_with_review_reports_matches` is
deleted, as the slice requires, and the other five are all accounted for
above. No moved test passes against the two-argument script. The RED's change
from `!= 0` to `== 2` in the failing-diff test is what stops it passing on
the usage exit. No test, fixture or `.allow` entry outside `plans/` refers to
the deleted test or the old helpers.

## Fixture probe

Each fixture was rebuilt with the helpers, and `changed-files.sh j` was run on
it. The raw `<base> HEAD` diff was taken for comparison.

| Fixture | Base | List | Raw diff |
|---|---|---|---|
| slice 1 | the outline-review commit (parent of `run: item 1.1`) | `a.txt`, `b.txt` | 6 paths: both item reports, `a.txt`, `b.txt`, `inbox/x.md`, `.claude/handoff-task.md` |
| files-changed | `track files` | `a.txt`, `d.txt`, `e.txt` | 4, the item report included |
| uncommitted-def, negative / positive | seed | `module.py`, `other.py` / plus `notes.txt` | list plus the item report |
| forced colour | seed | `module.py` | `module.py`, item report; the patch is ANSI-wrapped |
| failing diff | seed | `module.py`, exit 0 with the blob deleted | — |

So the base the fixtures produce is the one `changed-files.sh` derives. The
failing-diff fixture leaves `changed-files.sh` succeeding, which means the
script's exit 2 can only come from its own patch diff and not from the
`changed-files.sh` `ERROR:` path. The `unable to read <blob>` stderr assertion
pins that.

## Wrong-reason hunting

- **Slice 1 test:** 2 is distinct from the raw diff (6), from the diff minus
  `plans/j/` only (4), from the diff minus the exempt paths only (4), from the
  script's output counted with its `BASE:` line (3), and from a base at the
  seed with no filter (7). There is one coincidence. An implementation that
  takes the first item commit itself as the base (or `HEAD~1`) and does not
  filter reads `item-1-2.md` and `b.txt`, which is also 2. The slice fixes
  this fixture verbatim, so the test cannot break the tie by itself.
  `test_files_changed_counts_committed_changes_only` does break it: that
  implementation reads 2 there against an expected 3. The module catches it,
  so this is not a finding.
- **Files-changed test:** 3 differs from every neighbouring range. The
  unfiltered committed diff, 4 now that the item report is in range, also
  discriminates. The docstring did not list it (minor 3).
- **Uncommitted-definition test:** the negative is paired with a positive
  that differs only in committing the edits. A diff that reached the working
  tree or the index over the list's paths would read `yes` in the negative.
- **Forced colour:** confirmed that the repo-local `color.ui always` wraps
  the `+` lines in escapes, so `--no-color` is what the test discriminates.
- **Failing diff:** exit 2 alone could also come from a usage or
  `changed-files.sh` failure. The stderr assertion separates them, and the
  probe above shows `changed-files.sh` passing.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Committed-diff rule cited as D-91**
   - Location: `tests/test_triage_feedback.py:66`, `:92`
   - Note: Both docstrings cite D-91 for "the committed diff to HEAD only,
     never the working tree or the index". D-91 is the definition of dirt
     and the exempt paths. The `HEAD` form that keeps uncommitted work out is
     D-90's (`docs/references/build-run-state.md` D-90, "The `HEAD` form keeps
     uncommitted … out"), and the outline maps that rule to D-90 ("D-90 for
     the list").
   - **Status**: FIXED — both changed to D-90.

2. **Exit 2's `ERROR:` line pinned by no test**
   - Location: `tests/test_triage_feedback.py`, `test_failing_diff_is_an_error_not_no`
   - Note: The Item 1.1 interface puts `ERROR: <cause>` on stdout for a git
     failure. No slice in 1.1 asserts that line, and this test is the only one
     that drives a git failure. As written, a GREEN that exited 2 silently
     would pass.
   - **Status**: FIXED — added an assertion that some stdout line starts with
     `ERROR: `. A whole-line prefix is used because git's own `error:` is
     lowercase and goes to stderr. The docstring now names the line.

3. **Files-changed docstring missed one discriminating range**
   - Location: `tests/test_triage_feedback.py:66-69`
   - Note: With the item report now in range, the unfiltered committed diff
     reads 4. That is the neighbour separating the list from the raw diff, and
     the docstring's claim to cover "every neighbouring range" left it out.
   - **Status**: FIXED — added it to the docstring.

4. **Dead `_init_repo` return and stale "baseline" wording**
   - Location: `tests/triage_feedback_helpers.py:40-49`
   - Note: `_init_repo` still returned the seed sha as "a baseline commit".
     No caller reads it, because the script no longer takes a baseline.
   - **Status**: FIXED — it now returns `None`, and the docstring says "a
     seed commit, outside the run".

5. **Lint and format failures**
   - Location: `tests/test_triage_feedback.py:73` (ruff C420, a dict
     comprehension where `dict.fromkeys` fits), plus the format of the new
     assertion
   - Note: Precommit would have failed on these. They are recorded only
     because the fix touched the file.
   - **Status**: FIXED — ran `ruff check --fix` and `ruff format` on both
     files. `ruff check`, `ruff format --check` and `mypy` are all clean.

6. **Ragged docstring wrap**
   - Location: `tests/test_triage_feedback.py:30`
   - Note: There was a short line break in the middle of a sentence.
   - **Status**: FIXED — reflowed.

## Fixes Applied

- `tests/test_triage_feedback.py`: D-91 changed to D-90 in two docstrings.
  Added the `ERROR:` stdout assertion and its docstring clause to
  `test_failing_diff_is_an_error_not_no`. Added the unfiltered-diff neighbour
  to the files-changed docstring. Reflowed the slice-1 docstring. Applied
  `dict.fromkeys`.
- `tests/triage_feedback_helpers.py`: `_init_repo` now returns `None`, with a
  corrected docstring.

Re-run after the fixes: 5 failed, 0 passed, 0 errors, each at the same
assertion as in the table above. Line counts are 153 and 105, under 400.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Tests stay in `test_triage_feedback.py`, split to `triage_feedback_helpers.py` as `changed_files_helpers.py` does | Satisfied | Same helper set and shape (`_run_git`, `_init_repo`, `_commit`, runner), module docstring pointing at the helpers |
| Never shave docstrings | Satisfied | Each moved docstring kept its content; the base wording was adapted |
| Every fixture commits a `plans/j/reports/item-*` report | Satisfied | `_commit_item_report` in all five fixtures (`_def_edits_pending` included) |
| Moved tests use the `<job>`-only call and red on the usage exit | Satisfied | Table above |
| `test_simple_with_review_reports_matches` deleted | Satisfied | Absent from the module |
| Slice 1 test: fixture as specified, `- Files changed: 2`, stdout assertion before exit code | Satisfied | `tests/test_triage_feedback.py:23-54`; probe confirms the list is `a.txt`, `b.txt` |
| Comments cite D-numbers, never KD | Satisfied (after fix 1) | No `KD` in either file |

## Positive Observations

- The RED report records why the item report sits in a run commit rather
  than the pre-run one. That is the base derivation stated as a fixture
  constraint.
- The failing-diff test was tightened to `== 2` because the old `!= 0`
  passed on the usage exit. That is the vacuity check working on an
  inherited test.
- Both a raw-diff and an unfiltered implementation fail the slice test on
  its fixture, so the review gate's list is what it pins.
