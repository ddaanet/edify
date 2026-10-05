# Review: Item 1.1/2 test review — review-fixes-2

**Scope**: uncommitted `tests/test_triage_feedback.py`
(`test_reports_exclude_the_per_item_report`), `tests/triage_feedback_helpers.py`
(`_verdict`), RED report `item-1-1-s2-red.md`. SUT read-only.
**Date**: 2026-10-05
**Mode**: review + fix (TDD test review)

## Summary

The test reds on its first assertion against today's script, and every
other test in the module passes. A probe ran the test against a scratch copy
of the SUT with a KD-1-correct Reports block, and against one mutant per
plausible wrong implementation. The three mutants the dispatch named were
already killed. Three more survived the original fixture: a single-digit
item pattern, counting touched instead of added paths, and a recursive
pathspec. The fixture now carries a discriminator for each, and all seven
mutants red.

**Overall Assessment**: Ready

## Mechanical check

Module run after the fixes: 6 passed, 1 failed.
`test_reports_exclude_the_per_item_report` FAILED on
`assert "- Reports: 0" in lines` with stdout `- Files changed: 1`,
`- Reports: 4`, `- Behavioral code: no`, `- Review artifact: review`. Not an
ERROR. The 4 are the on-disk `find` count: `runbook-review.md`,
`explore-x.md`, `item-1-1.md` and `item-1-12.md`. `find -maxdepth 1` skips
`explore/notes.md` and excludes `review-code.md` by name. Before the fixes
the count was 3, as the RED report says.

## Mutation probe

How it was run: a scratch tree in `$TMPDIR` held a copy of
`triage-feedback.sh` and `skills/build/scripts/`. Its Reports block was
replaced by a `git diff --name-only --no-renames -z --diff-filter=A <base>
HEAD -- ":(glob)plans/j/reports/*"` loop, which excludes
`^item-[0-9]+-[0-9]+\.md$` and `review.md | review-*.md | final-review.md`.
`tests.triage_feedback_helpers.SCRIPT` was patched to point at it. The real
SUT was not touched, and the scratch tree is deleted.

| Variant | Original fixture | Strengthened fixture |
|---|---|---|
| correct (KD-1) | PASS | PASS |
| M1 on-disk count minus `item-*` (outline's rejected alternative) | RED `Reports: 0` | RED `Reports: 0` |
| M2 `item-*` glob exclusion | RED `Reports: 1` (third leg) | RED `Reports: 1` (third leg) |
| M3 `review-code.md` counted | RED `Reports: 0` | RED `Reports: 0` |
| M4 single-digit `item-[0-9]-[0-9].md` | **PASS** | RED `Reports: 0` |
| M5 touched, no `--diff-filter=A` | **PASS** | RED `Reports: 0` |
| M6 no `:(glob)`, matches below `reports/` | **PASS** | RED `Reports: 0` |
| M7 per-item report not excluded | RED `Reports: 0` | RED `Reports: 0` |

The correct variant passes all three legs, which confirms the verdict
expectations: `match`, `overclassified` at Complex, and `underclassified`
with the slice report.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Three of KD-1's Reports clauses had no discriminating fixture**
   - Location: `tests/test_triage_feedback.py`,
     `test_reports_exclude_the_per_item_report` fixture
   - Problem: KD-1 says Reports counts paths "directly under
     `plans/<job>/reports/` that `<base> HEAD` adds", minus
     `item-<N>-<M>.md` where N and M are digits. The fixture held one
     single-digit item report and only top-level additions, and modified no
     report. So M4, M5 and M6 passed all three legs. Each is a natural first
     write:
     - M4: a bash `case`/`==` pattern cannot say "one or more digits"
       without extglob.
     - M5: a bare `git diff --name-only`.
     - M6: a plain pathspec, whose `*` crosses `/`. `changed-files.sh`'s
       header documents that same pitfall.
   - Fix: a run commit `run: item 1.12`, between the item-1.1 commit and the
     review commit. It adds `item-1-12.md` (kills M4), revises the pre-base
     `runbook-review.md` (kills M5) and adds `explore/notes.md` below the
     reports directory (kills M6). All three paths sit under `plans/j/`,
     which the review gate's list drops, so `- Files changed` stays 1 and
     the `overclassified` leg stays in bounds. The docstring names each
     discriminator and the mutant it kills.
   - **Status**: FIXED

### Minor Issues

1. **`_verdict` raised `IndexError` when `## Verdict` is the last line**
   - Location: `tests/triage_feedback_helpers.py`, `_verdict`
   - Note: the absent case returns `""` so that the assertion message carries
     stdout. A truncated output (`## Verdict` with nothing after it) raised
     `IndexError` and lost the stdout. It now returns `""` there too.
   - **Status**: FIXED

## Check 3: overclassified bounds

The review gate's list for this fixture is `notes.txt` alone: 1 file. Every
other path the run commits is under `plans/j/`, which `changed-files.sh`
excludes. The relabels are uncommitted, as the RED report explains. Files
changed is 1 ≤ 2, Reports is 0 and Behavioral code is `no`, so `Complex`
reads `overclassified`. The correct-variant probe confirmed it.

## Check 4: line caps

`tests/test_triage_feedback.py`: 252 lines (was 238).
`tests/triage_feedback_helpers.py`: 113 lines. Both are under 400.

## Wrong-reason notes, not findings

- `- Behavioral code: no` is a bare negative in this test. Its paired
  positive is slice 1.1/3 (`a.py` adding `def foo():` reads `yes`). Here it
  only makes the `match` verdict attributable to Reports. Accepted.
- The Complex leg and the first leg red on the same Reports mutants. The
  Complex leg adds the verdict mapping for Complex, which is out of this
  slice's change. That is as specified, and not redundant.

## Fixes Applied

- `tests/test_triage_feedback.py`, the test's fixture: a new `run: item 1.12`
  commit adds `item-1-12.md`, revises `runbook-review.md` and adds
  `explore/notes.md`. The docstring is extended to name each discriminator.
- `tests/triage_feedback_helpers.py`, `_verdict`: returns `""` when nothing
  follows `## Verdict`.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Slice 1.1/2 fixture and three expectations | Satisfied | the outline's items are all present, and the additions sit beside them without changing any expectation |
| KD-1 Reports: added in `<base> HEAD` | Pinned | M5 reds |
| KD-1 Reports: directly under `reports/` | Pinned | M6 reds |
| KD-1 Reports: minus `item-<digits>-<digits>.md` | Pinned | M2, M4 and M7 red |
| KD-1 Reports: minus review-gate reports | Pinned | M3 reds |
| KD-1 Reports: planning reports outside range | Pinned | M1 reds |

Item 1.2 slice 1 reuses "the slice 1.1/2 fixture". The added commit changes
no evidence column (Files changed 1, Reports 0, code `no`), so that slice's
expectations are unaffected.
