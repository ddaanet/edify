# Review: Item 1.1 / Slice 1 — test review

**Scope**: `tests/test_verify_step.py::test_exempt_paths_clean_in_any_porcelain_state`
(uncommitted diff) and `plans/build-fixes/reports/item-1-1-s1-red.md`. OUT:
`verify-step.sh` (SUT), slice 2, Item 1.2 onward, the module's pre-existing
tests.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The test builds the four states the slice names: staged add, staged delete,
worktree delete, and a genuine two-branch `UU`. Each state is independently
load-bearing. A mutant that drops any single one of `A`, `D` (X or Y column) or
`U` reds the test on its `returncode` assertion, with only that line listed as
dirt. The RED report's `[ M?]` mutant also reds. Fixes: the conflicting merge
now asserts its exit 1 through a `returncode=` parameter on `_run_git` (a
shared-helper compaction), the precommit marker is asserted, the docstring no
longer overclaims, and the test moved next to the other exemption tests.

**Overall Assessment**: Ready

## Mechanical check — mutation red reproduced

The behaviour is already implemented, so the test passes against the real
script (7/7 module pass, after fixes). The red evidence comes from mutation.

**My own mutation, distinct from the RED report's:** this drops only the
unmerged state.
Scratch copy `/tmp/claude/build-fixes/verify-step-mutant-s1-review.sh`, rebound
by `/tmp/claude/build-fixes/rebind_script_plugin_review.py`. That file is a copy
of the report's plugin with `MUTANT` pointed at the review copy. It is loaded
with `PYTHONPATH=/tmp/claude/build-fixes pytest -p rebind_script_plugin_review`.

```
19c19
< exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'
---
> exempt='^[^RCU][^RCU] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'
```

Whole-module run against it, post-fix: `6/7 passed, 1 failed`. Only the new
test failed, on `assert result.returncode == 0` (line 326):

```
AssertionError: DIRTY: uncommitted changes
  UU inbox/conflict.md
assert 1 == 0
```

The other six tests stay green, so the `UU` line is pinned by this test alone.

**Per-state independence**, pre-fix test, one scratch variant each (only line
19 differs):

| Mutant XY classes | Result | Sole line listed as dirt |
|---|---|---|
| `[^RCU][^RCU]` | FAILED (returncode) | `UU inbox/conflict.md` |
| `[^RCA][^RC]` | FAILED (returncode) | `A  .claude/handoff-new.md` |
| `[^RCD][^RC]` | FAILED (returncode) | `D  inbox/old.md` |
| `[^RC][^RCD]` | FAILED (returncode) | ` D .claude/handoff-task.md` |

**RED report's mutant re-run post-fix** (`[ M?][ M?]`, via the report's own
plugin): `0/1 passed, 1 failed`, on `returncode`, listing all four lines.
This matches the report.

Tracked script: `git diff --quiet plugin/skills/build/scripts/verify-step.sh`
→ `verify-step.sh untouched`, checked after every mutant run.

## Wrong-reason hunting

- **Can it pass for another reason?** `CLEAN:` needs every porcelain line
  filtered out and `just precommit` to succeed. The four lines are the only
  porcelain content: the test pins the whole porcelain string. A non-exempt
  stray cannot ride along, and a missing state cannot drop out unnoticed.
  The one remaining wrong-reason pass is an over-broad exemption (e.g. any
  path in any state). That belongs to the paired negatives elsewhere in the
  module: decoys in `test_conventional_dirt_...`, `test_memory_gitlink_...`,
  `test_quoted_exempt_path_...`, and the `R` line in
  `test_rename_out_of_exempt_path_is_dirty`. This test is the positive half of
  the contract, as the slice specifies.
- **Porcelain pre-assertion**: sound. It is an exact equality on
  `--untracked-files=all` output, the same flags the script uses. It would
  catch a fast-forwarded or auto-resolved merge, a stray `MERGE_MSG`-type
  untracked file, or a state drifting to `M`/`MM`.
- **Fixture matches the slice**: yes. The four XY pairs are exactly the
  slice's. `UU` comes from a real conflict on a tracked file: both branches
  rewrite the same line of `inbox/conflict.md`. The paths are the slice's
  names. The fixtures are `_init_repo` and `_stub_just`, as the item names.
- **Born-green residual**: the mutant red lands on the `returncode`
  assertion. `stdout.startswith("CLEAN:")` and the new marker assertion have
  never redded on their own, which follows the module's existing
  three-assertion pattern for clean phases. Under every mutant above,
  stdout started `DIRTY:`, so the `CLEAN:` assertion would also fail if
  reached. Recorded for completeness; no change made.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Conflicting merge's exit was discarded**
   - Location: `tests/test_verify_step.py`, the `git merge feature` call.
   - Note: the merge ran through a bare `subprocess.run(..., check=False)` and
     discarded its result. A setup failure for another reason (exit 128, a
     clean merge) would surface only as a porcelain mismatch, with the merge
     output lost. It also duplicated `_run_git`'s env-insulation block
     verbatim.
   - Fix: `_run_git` gains keyword `returncode: int = 0`. The merge becomes
     `_run_git(repo, "merge", "feature", "-m", "merge", returncode=1)`, which
     asserts a conflict exit and attaches git's output on mismatch. Existing
     callers are unaffected (default 0).
   - **Status**: FIXED

2. **Precommit marker created but never asserted**
   - Location: end of the test.
   - Note: every other clean phase in the module asserts
     `marker.read_text(...) == "precommit\n"`. This one built the stub and
     dropped the check.
   - **Status**: FIXED

3. **Docstring overclaimed coverage**
   - Location: test docstring.
   - Note: "Every exempt path clears the tree in any non-rename XY state"
     claims `memory` (not exercised here) and every XY pair (four are). The
     mutation rationale named only the `[ M?]` mutant. The stronger property
     the test actually has went unstated: each line is independently
     load-bearing.
   - Fix: the summary now says the test covers states beyond ` M`/`MM`/`??`.
     The body states that losing any one of `A`/`D`/`U` in either column lists
     that line as dirt.
   - **Status**: FIXED

4. **Placement among the failure-mode tests**
   - Location: the test sat between `test_git_status_failure_exits_2` and
     `test_missing_just_exits_2`.
   - Note: the module groups the exemption tests first and the exit-2 tests
     after.
   - Fix: moved to follow `test_quoted_exempt_path_is_clean`.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_verify_step.py` `_run_git`: new `returncode: int = 0` keyword,
  asserted in place of the literal `0`; one docstring sentence names it.
- `tests/test_verify_step.py` new test: replaced the 11-line inline env +
  `subprocess.run` merge with one `_run_git(..., returncode=1)` call plus a
  one-line comment.
- Same test: added `assert marker.read_text(encoding="utf-8") == "precommit\n"`.
- Same test: rewrote the docstring (see Minor 3).
- Same test: moved before `test_git_status_failure_exits_2`.

Post-fix verification: `ruff format --check` and `ruff check` on the module
are clean. `pytest tests/test_verify_step.py` gives 7/7 passed. The review
mutant gives 6/7 (only the new test red, on its assertion). The report mutant
reds the new test on its assertion.

## Line cap

`tests/test_verify_step.py` is now **373 lines** (was 377), against the
400-line hard cap. Slice 2 has 27 lines of headroom. That slice's test is a
two-path untracked fixture plus a four-line `splitlines()` listing. In the
module's existing style, comparable tests run 30–40 lines including the
docstring, so slice 2 will likely press on or cross the cap. No docstrings were
shaved or lines crammed. If slice 2 overflows, the clean seam is a
`_status(repo)` helper for the `_run_git(repo, "status", "--porcelain",
"--untracked-files=all")` pre-assertion, which recurs in five tests. A
`bin_dir`/`marker`/`_stub_just` triple also recurs and could fold into a helper.
Neither was applied here: both touch the pre-existing tests, which are out of
scope.

## Observed outside scope

`just check` fails on `tests/line_limits_helpers.py:32:30: RUF100 Unused
noqa directive (PLR0913)`. That file is untouched by this diff
(`git status` shows only `tests/test_verify_step.py` modified under `tests/`).
Not fixed (OUT-OF-SCOPE). Reported so the next gate run is not a surprise.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Major 6 / F-4 (exemption holds in any non-rename porcelain state) | Satisfied for the four slice states | Per-state mutant table above |
| Slice: assert exit 0 and stdout starting `CLEAN:` | Satisfied | Test's final assertions |
| Slice: `UU` from a two-branch conflict on a tracked file | Satisfied | `feature`/`main` divergent commits; merge asserted exit 1; porcelain pinned |
| Item: tracked script never reverted; mutant is a rebound copy | Satisfied | `git diff --quiet` checks |

## Positive Observations

- The exact-equality porcelain pre-assertion makes the fixture
  self-verifying. This guards against the hand-written-markers and
  fast-forward drifts the RED report names.
- The RED report's rebind plugin asserts it is not a no-op. Reusing it with a
  different `MUTANT` was trivial.
- All four states share one tree. A single mutant run therefore shows exactly
  which line each narrowed class loses.
