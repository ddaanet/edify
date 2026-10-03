# Review: Item 1.4 slice 3 — test review (`test_phase_list_keeps_the_filters`)

**Scope**: `test_phase_list_keeps_the_filters` in
`tests/test_changed_files_phase.py` (uncommitted diff) and the RED report
`plans/build-fixes/reports/item-1-4-s3-red.md`. The SUT
`plugin/skills/build/scripts/changed-files.sh` was mutated in place for the
check and restored; no lasting SUT edit.
**Date**: 2026-10-03
**Mode**: review + fix

## Summary

One test pins two things: the shared exempt-path and `plans/j/` filters run
on the `--phase` list, and the slice-2 `:(glob)` fix on the boundary query.
The fixture discriminates. Every DROP path is one the diff since the boundary
really carries. The decoy commit sits after the kept files, so a base moved
by mistake empties the list. `phase-9/old-corrector.md` matches only through
`*` crossing `/`. Two defects were found, both fixed. The test's summary line
failed the project lint (D205), although the RED report said ruff was clean.
The docstring also understated the `sub/` decoy's role.

**Overall Assessment**: Ready

## Check 1 — mechanical

- Against the current SUT the test passes. That is expected: the code is
  shared, and the RED report's three mutations supply the red.
- Own mutations, different from the RED report's three. Each was an
  exact-string Edit, its target confirmed unique (`grep -cF` = 1) before
  applying, the landing proven by grep, and the restore done by the inverse
  Edit:
  1. **Subdirectory before `phase-`.** `":(glob)plans/$job/reports/phase-*-corrector.md"`
     -> `":(glob)plans/$job/reports/**/phase-*-corrector.md"`. Result: 6/7.
     Only `test_phase_list_keeps_the_filters` reds, on its list assertion:
     `BASE:` is the decoy commit (`17c1e14…` instead of `f4e0fa3…`) and the
     list is empty. Only `sub/phase-9-corrector.md` can cause this: under
     `:(glob)`, `phase-9/old-corrector.md` does not match `**/phase-*`. So
     the `sub/` decoy pins a behaviour of its own, and no other test in the
     suite catches this mutation.
  2. **Exempt regex end anchor dropped.** `exempt_re='^('"${EXEMPT_PATHS_ALTERNATION}"')$'`
     -> `…')'`. Result: 5/7. This test reds on the list assertion
     (`memoryx.txt` missing), and so does
     `test_exempt_paths_committed_in_the_run_are_dropped`. The `memoryx.txt`
     near-miss pins the anchor under `--phase`.
- Restore proven after each mutation: `grep -cF` of the mutation text gives 0
  and `git diff --quiet plugin/skills/build/scripts/changed-files.sh` exits
  0. After the final restore and the test fixes, the suite
  (`tests/test_changed_files.py` + `tests/test_changed_files_phase.py`) is
  7/7 green.

## Check 2 — wrong-reason hunting

- **DROP paths**: the three exempt paths each pin one alternative of the
  alternation. Deleting any one of them lists that path. `plans/j/` is pinned
  by an added report (`item-2-1.md`), a modified file (`runbook.md` v1->v2)
  and both decoys. All of them are in `<boundary> HEAD`, so a disabled filter
  has something to leak (RED mutations 1 and 2).
- **KEEP near-misses**: `inbox/sub/y.md` pins `[^/]+`, which is single-level.
  `memoryx.txt` pins the `$` anchor (own mutation 2). There is no
  `plans/jj/…` near-miss for the `plans/j/` prefix's trailing `/`. The
  `--phase` run still pins that boundary, through both sibling tests:
  `test_phase_without_boundary_gives_run_base` asserts the `--phase` output
  equals a bare list that holds `plans/jj/…`, and
  `test_phase_base_is_latest_boundary_commit` lists
  `plans/jj/reports/phase-2-corrector.md` under `--phase`. The other
  alternation near-misses (`^` anchor, `.md` suffix, `handoff-` prefix) are
  pinned in `test_exempt_paths_committed_in_the_run_are_dropped`, and the
  code is shared. Not a finding.
- **Base boundary**: `a.txt` (before the boundary) and `fix.txt` (in the
  boundary commit) being absent pins base = boundary, not the run base or the
  boundary's parent.
- **`:(glob)` decoy**: the pattern `plans/j/reports/phase-*-corrector.md`
  matches `plans/j/reports/phase-9/old-corrector.md` only when `*` matches
  `9/old`, which means crossing `/`. That exercise is genuine, and RED
  mutation 3 reds on it. Placing the decoy commit after the kept files is
  what makes a moved base observable. The RED report's rejected ordering
  records the reason.
- **`sub/` decoy**: the claim "matches neither way" is accurate. "Rides along
  as a near-miss" understated what it does (finding 2).

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Summary line fails the project lint (D205)**
   - Location: `tests/test_changed_files_phase.py:148-149`
   - Problem: the summary wrapped onto two lines (`… apply to the list
     under` / ``` ``--phase``. ```). `ruff check -q tests/`, the form
     `just lint` runs, reported D205 and exited 1. The RED report claimed
     `ruff check clean`, and that is not what the tree showed.
   - Fix: a one-line summary, `Under ``--phase`` the exempt-path and
     ``plans/j/`` drops still apply.` (76 columns, within docformatter's
     `wrap-summaries = 80`).
   - **Status**: FIXED

### Minor Issues

1. **The `sub/` decoy's role was stated vaguely**
   - Location: `tests/test_changed_files_phase.py`, docstring, second
     paragraph
   - Note: "rides along as a near-miss" did not name what the path rules
     out. Own mutation 1 shows it is the only guard against a pathspec that
     admits a directory before `phase-` (`reports/**/phase-*-corrector.md`).
     The docstring now says it pins the literal `reports/phase-` prefix, and
     names that pathspec.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_changed_files_phase.py:148`: two-line docstring summary
  replaced by a one-line summary (D205).
- `tests/test_changed_files_phase.py:163-166`: the `sub/` decoy sentence now
  states the prefix it pins and the mutation it catches. The paragraph was
  re-wrapped to 80 columns.

Verification after the fixes: `ruff check -q tests/` clean,
`ruff format --check` clean, `docformatter -c src tests` exit 0, 7/7 green,
SUT diff-clean. The file is 205 lines. The fixes touch only the docstring,
so the mutation results above still hold.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Item 1.4.3: exempt-path filter applies under `--phase` | Satisfied | DROP of `inbox/x.md`, `.claude/handoff-task.md`, `memory`; RED mutation 1; own mutation 2 |
| Item 1.4.3: `plans/<job>/` filter applies under `--phase` | Satisfied | DROP of `item-2-1.md`, `runbook.md`, decoys; RED mutation 2 |
| Slice-2 code review `:(glob)` fix pinned | Satisfied | `phase-9/old-corrector.md` decoy; RED mutation 3 |
| KD-2 literal `reports/phase-` prefix | Satisfied | `sub/phase-9-corrector.md` decoy; own mutation 1 |

**Gaps:** none.

## Positive Observations

- The RED report records a deviation from the slice text and its reason:
  the prompt's `sub/` decoy cannot red the `:(glob)` mutation. It also
  records the rejected decoy-before-kept ordering.
- The assertions compare the whole output, so a moved base and a leaked
  path both red on the same line, with nowhere to hide.
- Each pinned value is distinct (`BASE:` sha, two named paths). A swapped
  filter shows up as a specific wrong list.

## Recommendations

None.
