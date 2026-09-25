# Review: Item 1.1 / Slice 1 — test review

**Scope**: `tests/test_triage_feedback.py` (`test_simple_with_review_reports_matches`) and `plans/build-defects/reports/item-1-1-s1-red.md`; `plugin/bin/triage-feedback.sh` read only.
**Date**: 2026-09-25
**Mode**: review + fix (TDD test review, dispatch 2 of 4)

## Summary

The RED test failed on its own assertion (`- Reports: 3` against `- Reports: 0`). It had two wrong-reason gaps. First, no fixture file matched the plain `review.md` pattern. Second, the assertion only checked that files were left out of the count, so a GREEN that stopped counting reports at all would pass. Both gaps are fixed. The test still fails on its assertion, and a check against scratch copies of the script shows that every partial or over-broad GREEN now fails.

**Overall Assessment**: Ready

## Mechanical first check

`PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_triage_feedback.py -v`, before fixes: 1 failed, 0 passed, 0 errors. The failure was an `AssertionError` at `assert "- Reports: 0" in lines` with the script printing `- Reports: 3` / `underclassified`. It was red on an assertion, for the KD-3 reason.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`review.md` was not in the fixture, so a partial GREEN passed**
   - Location: `tests/test_triage_feedback.py`, reports fixture
   - Problem: KD-3 excludes `review.md`, `review-*.md` and `final-review.md`. The fixture had `review-skill.md`, `review-skip.md` and `final-review.md`, and both `review-*` files match the same glob. A GREEN of `! -name "review-*.md" ! -name "final-review.md"` would pass while still counting `review.md`, which is a single-group review gate's report. So the slice's claim that "one fixture covers every excluded name" did not hold. The test docstring's "all three are the KD-3 exclusion set" also mislabelled the three files as the three patterns.
   - Fix: add `reports/review.md` to the fixture and correct the docstring.
   - **Status**: FIXED

2. **A bare negative, with no positive control**
   - Location: `tests/test_triage_feedback.py`, the `- Reports: 0` / `match` assertions
   - Problem: `Reports: 0` / `match` only checks that files are left out of the count. A GREEN that zeroes `reports_count`, or that excludes `*review*` (catching real execution reports such as `item-N-M-s<k>-code-review.md` from `dispatch-composition.md` §Naming), passes it. Such a GREEN also switches off underclassification detection for every Simple job.
   - Fix: over the same fixture, add one `item-1-1-s1-code-review.md` (a slice code-review report, not a review-gate report per KD-3), re-run, and assert `- Reports: 1` and `underclassified`. The only difference between the two runs is a file that does not match the exclusion.
   - **Status**: FIXED

### Minor Issues

1. **`Behavioral code: no` precondition not asserted**
   - Location: `tests/test_triage_feedback.py`
   - Note: The verdict depends only on the report count when `Behavioral code: no`. That held only because of a comment. It is now an assertion in both runs, so a fixture drift that flips the verdict on code shows up as such.
   - **Status**: FIXED

2. **List-repr assertion messages were cut off**
   - Location: `tests/test_triage_feedback.py`, assertion messages
   - Note: After the helper started returning lines, pytest cut the list repr before the verdict. Messages now show the full stdout (`"\n".join(lines)`).
   - **Status**: FIXED

3. **Redundant parentheses `(plan_dir).mkdir`**
   - Location: `tests/test_triage_feedback.py`
   - **Status**: FIXED

## Wrong-reason checks (answered)

- **Partial GREENs**: each variant was run against a scratch copy of the script, never the SUT, by pointing the module's `SCRIPT` at the copy:

  | Variant (added to the `find` excludes) | Result |
  |---|---|
  | `review.md`, `review-*.md`, `final-review.md` (intended GREEN) | PASS |
  | only `final-review.md` | FAIL (Reports: 3) |
  | only `review-*.md` | FAIL (Reports: 2) |
  | `review-*.md` + `final-review.md` (no plain `review.md`) | FAIL (Reports: 1) |
  | `*review*` (over-broad) | FAIL (positive run reads 0 / `match`) |
  | `reports_count=0` forced | FAIL (positive run reads 0 / `match`) |
  | unfixed | FAIL (Reports: 4) |

- **`Behavioral code: no` guaranteed**: yes. The diff adds `notes.txt`, whose one line is `+just plain text, no code here`, and `+++ b/notes.txt` does not match either regex. Files under `plans/` are untracked, so they stay out of `git diff <baseline>`, and so does the script's own `plans/reports/triage-feedback-log.md`. The precondition is now asserted.
- **`## Verdict` next line**: the script prints `## Verdict` once and the verdict on the next line. `- Reports: N` is compared as a whole line, so the `Triage:` summary line (`reports=N`) cannot satisfy it.
- **Git insulation**: `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` point at `/dev/null` for both setup git and the script run. Identity is set per repo. This matches `tests/review_range_helpers.py`.
- **Invocation**: by absolute path (the recorded mode `100755` confirms the exec bit), CWD at the repo root, args `<bare job name> <baseline sha>`. That matches `finishing.md` §2: `plugin/bin/triage-feedback.sh <job> "$(cat tmp/build-baseline)"`, "pass the bare job name".
- **Classification shape**: `- **Classification:** Simple` matches `plugin/skills/design/references/triage.md:106` and the script's grep. The RED output proves it parsed: `underclassified` only comes from the `Simple` branch.

## Fixes Applied

- `tests/test_triage_feedback.py`: `_run_triage_feedback` became `_triage_lines`, which asserts exit 0 with the output attached and returns the stdout lines.
- `tests/test_triage_feedback.py`: added `reports/review.md` to the fixture.
- `tests/test_triage_feedback.py`: added a positive run: add `item-1-1-s1-code-review.md` → `- Reports: 1`, `underclassified`.
- `tests/test_triage_feedback.py`: `- Behavioral code: no` asserted in both runs; messages show full stdout; the docstring now names all three KD-3 patterns and the positive control; `(plan_dir)` parentheses dropped.

## Post-fix run

- `pytest tests/test_triage_feedback.py -v`: 1 failed, 0 passed, 0 errors. `AssertionError` at `assert "- Reports: 0" in lines` (`- Reports: 4`, `underclassified`). Still red on its assertion, for the KD-3 reason.
- `ruff check`: All checks passed. `ruff format --check`: already formatted. `mypy`: exit 0.
- `git status --porcelain`: only `?? plans/build-defects/reports/` and `?? tests/test_triage_feedback.py`. The SUT is unmodified.

## Note for GREEN

The intended exclusion is exactly `review.md`, `review-*.md`, `final-review.md`. `*review*` fails the positive run, because `item-1-1-s1-code-review.md` must still count.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| inline M3 / KD-3: `reports_count` excludes `review.md`, `review-*.md`, `final-review.md` | Pinned (red, pending GREEN) | fixture carries one file per pattern; positive control pins the boundary |
| Slice 1: `- Reports: 0` and `match` after `## Verdict` | Satisfied (asserted) | `tests/test_triage_feedback.py` first run |

## Positive Observations

- The verdict is found from the `## Verdict` heading, not a fixed index, and the assertions compare whole lines, not substrings.
- Setup failures report stderr (D-21), and git is insulated from user and system config, as in the house helper.

## Addendum — docstring fix

Requested by `build-defects-leg1` after GREEN: `docformatter -c` (part of
`just precommit`) flagged the 83-column summary line of
`test_simple_with_review_reports_matches`'s docstring against
`wrap-summaries = 80`.

**Change** (docstring only; no code, fixture or assertion touched):

- Summary is now `A Simple job whose only reports are review-gate ones matches.`
  and fits on one line.
- The closing-review point moved into the body: "... ``review-skip.md`` and
  the closing review's ``final-review.md`` together". The first body
  paragraph was rewrapped to 80 columns.

`plugin/bin/triage-feedback.sh`, which holds GREEN's uncommitted
implementation, was not touched.

**Checks** (foreground, `PATH=/Users/david/code/edify/.venv/bin:$PATH`, on
`tests/test_triage_feedback.py`):

- `docformatter -c`: exit 0
- `ruff check`: All checks passed (exit 0)
- `ruff format --check`: 1 file already formatted (exit 0)
- `mypy`: exit 0
- `pytest -v`: 1/1 passed. This is expected now that GREEN's implementation
  is in the tree.
