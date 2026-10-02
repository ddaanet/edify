# Review: build-fixes Item 1.2 / slice 1 — test review

**Scope**: `tests/test_changed_files.py`
(`test_base_is_parent_of_first_item_report_commit`), RED report
`plans/build-fixes/reports/item-1-2-s1-red.md`, stub
`plugin/skills/build/scripts/changed-files.sh` (stub completion only)
**Date**: 2026-10-02
**Mode**: review + fix (TDD test review)

## Summary

The mechanical check holds: the test failed on its content assertion against
the inert stub, not on an ERROR. The original fixture was too thin, though. In
the history seed → P → item 1.1 → item 1.2, three plausible wrong base
derivations landed on P, and two wrong list derivations produced
`a.txt, b.txt`. I rebuilt the fixture so that each of those yields a different
answer from the correct one, and checked that against eleven candidate
implementations. The test is still red on its assertion.

**Overall Assessment**: Ready

## Mechanical check

| Test | Against inert stub | Reason |
|------|--------------------|--------|
| `test_base_is_parent_of_first_item_report_commit` | FAILED | `AssertionError: assert [] == ['BASE: <P>', 'a.txt', 'b.txt']` at the list assertion; `returncode == 0` passed first |

The RED report's run matches: FAILED, with no PASSED and no ERROR. The stub
(`#!/usr/bin/env bash`, mode 755) runs and exits 0, so it has no gap. It was
not edited.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The base fixture let three wrong derivations land on P**
   - Location: `tests/test_changed_files.py`, original fixture (seed → P →
     C1 → C2)
   - Problem: the right base is P, the parent of C1. The original fixture also
     gives P for each of these:
     - `HEAD~2`, or `HEAD~<item-report count>`. There were exactly two item
       commits and nothing after them.
     - The first commit touching `plans/j/reports/`, used without taking its
       parent. P was the only non-item report commit, and it was C1's parent.
     - An unscoped `plans/*/reports/item-*` glob that ignores `<job>`. Only
       one job existed.

     Each of these passes the test while it violates KD-1. The root commit,
     P's parent and outline-review's parent were already distinct from P,
     because `_init_repo` puts a seed commit first.
   - Fix: added three decoy commits around P, plus a `_commit` helper (slices
     2 and 3 will reuse it). P stays C1's immediate parent and still adds
     `outline-review.md`, as the item specifies.
     - Before P, a commit adding `plans/other/reports/item-1-1.md`. This
       catches the unscoped glob.
     - Before P, a commit adding `plans/j/reports/explore-x.md` and
       `plans/j/runbook.md`. This catches the first-reports-commit derivations
       with or without the parent.
     - After item 1.2, a report-less code-review fix to `a.txt`. This catches
       `HEAD~2` and `HEAD~N`.
   - **Status**: FIXED

2. **The list assertion could not tell the committed diff from the
   working-tree diff, or a `reports/`-only drop from a `plans/<job>/` drop**
   - Location: same fixture
   - Problem: the original worktree was clean, so `git diff <base>` and
     `git diff <base> HEAD` agreed. The only `plans/j/` paths in range were
     under `reports/`, so dropping `plans/j/reports/` passed as well as KD-6's
     `plans/<job>/`. The item reports were in the range, so a script that
     dropped nothing did fail. That part was sound.
   - Fix:
     - Item 1.2's commit also revises `plans/j/runbook.md` (KD-6: "runbook.md
       list revisions are its record"). A drop limited to `reports/` now leaks
       it.
     - The test leaves an uncommitted edit to `README.md`. A working-tree
       diff now leaks it.

     The expected list is still exactly `a.txt`, `b.txt`.
   - **Status**: FIXED

### Minor Issues

1. **The docstring explained the old fixture and did not say why the order
   holds**
   - Location: test docstring
   - Note: rewrote it to give the history, the wrong derivation each decoy
     rules out, and the reason the order is fixed (`git diff` emits paths in
     sorted order).
   - **Status**: FIXED

## Order assertion (check 3)

The order assertion is justified. The interface emits one path per line from
`git diff`, which lists paths sorted by path. `a.txt` sorts before `b.txt`. In
the new history `a.txt` is touched twice, by C1 and by the fix commit, and the
order still holds because the diff is over the range, not per commit. An
implementation that walks `git log --name-only` would produce a different
order or duplicates. That is a deviation from the interface, so the test is
right to fail on it.

## Discrimination evidence

I ran the test with each candidate written in place over the stub path, one
at a time. The stub was then restored byte-for-byte (`cmp` clean, mode 755).
The tests themselves were not moved.

| Candidate | Result |
|-----------|--------|
| KD-1 query (`--diff-filter=A --reverse … item-*`, `^`), `<base> HEAD`, drop `plans/$job/*` | PASSED |
| root commit as base | FAILED |
| unscoped `plans/*/reports/item-*` | FAILED |
| first commit touching `plans/j/reports/`, no parent | FAILED |
| first commit touching `plans/j/reports/`, its parent | FAILED |
| parent of the commit adding `outline-review.md` | FAILED |
| `HEAD~2` | FAILED |
| parent of the latest item-report commit | FAILED |
| right base, working-tree diff (`git diff <base>`) | FAILED |
| right base, drops only `plans/j/reports/*` | FAILED |
| right base, drops nothing | FAILED |

These candidates were throwaway scripts in `$TMPDIR`, not committed, and they
are not a design for the implementation.

## Fixes Applied

- `tests/test_changed_files.py`: added the `_commit(repo, message, files)`
  helper, which writes the files, commits them and returns the sha.
- `tests/test_changed_files.py`: rebuilt the fixture of
  `test_base_is_parent_of_first_item_report_commit`. It adds the other-job
  item report, the `explore-x.md` and `runbook.md` planning commit, the
  `runbook.md` revision in item 1.2, the trailing code-review fix and the
  uncommitted `README.md` edit. The assertions are unchanged.
- `tests/test_changed_files.py`: rewrote the test docstring.
- `ruff format` and `ruff check` are clean, and the file is 135 lines.

## Re-run

```
PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest tests/test_changed_files.py -vv
```

`test_base_is_parent_of_first_item_report_commit` FAILED at
`tests/test_changed_files.py:131` with
`AssertionError: assert [] == ['BASE: <P>', 'a.txt', 'b.txt']`. This is red
on its assertion, as required.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Major 1 / KD-1: base is the parent of the earliest commit adding an `item-*` report | Pinned | the decoy fixture and the discrimination table |
| m1, m2, m18 / KD-6: committed diff since the base, `plans/<job>/` dropped | Pinned (the `plans/<job>/` part only) | the `runbook.md` revision, the item reports and the uncommitted `README.md`. Dropping exempt paths is slice 2's job. |

## Positive Observations

- The RED report rejected `lines[0]` indexing, which would have raised
  `IndexError`, in favour of a single list-equality assertion. That gives a
  genuine wrong-value red.
- The git calls are insulated from user and system config, and setup fails
  with the failing command's output attached (D-21).
- The expected sha comes from `rev-parse` on the fixture, not from a
  hand-written value.

## Recommendations

- The fixture does not test a sibling path that shares a prefix. A path such
  as `plans/jj/x.md` changed in the run should survive, and would catch an
  unanchored `^plans/j` match. Adding it changes this slice's specified list,
  so it is left for slice 2 or the code review to consider.
- `--diff-filter=A` cannot be told apart from no filter here. That needs a
  report from an earlier run that was deleted and then re-added. It is outside
  this slice.
