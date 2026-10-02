# Review: Item 1.2 / slice 2 — test review

**Scope**: `test_exempt_paths_committed_in_the_run_are_dropped` in
`tests/test_changed_files.py` (uncommitted diff) and the RED report
`plans/build-fixes/reports/item-1-2-s2-red.md`. Out of scope: the SUT
(`changed-files.sh`), `exempt-paths.sh`, `verify-step.sh`, slice 3, and Item
1.3 onward.
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The test is red against the current SUT, and it fails on the exact-list
assertion rather than with an error. As handed over, its three KEEP
near-misses pinned the single-level `inbox/` glob, the `handoff-` prefix and
the exact name `memory`. Nothing pinned the `.md` suffix of either glob or
the leading anchor of the path. An exemption that dropped `inbox/x.txt`,
`.claude/handoff-task.json` or `docs/inbox/x.md` would have passed. Three
near-misses were added to close those gaps, and the docstring was fixed. To
check the result, the test was run against scratch copies of the SUT. Each
copy carried one candidate exemption: a correct one, and over-broad ones
that would pass the old test. The correct one passes and every over-broad
one fails, each on its own near-miss.

**Overall Assessment**: Ready

## Mechanical check

- The RED report lists one test,
  `test_exempt_paths_committed_in_the_run_are_dropped`, as FAILED on the
  exact-list assertion. Re-run before the fixes: FAILED, with the same
  failure the report shows. `test_base_is_parent_of_first_item_report_commit`
  passes.
- Re-run after the fixes: FAILED at `tests/test_changed_files.py:180` with
  `AssertionError`. The `returncode == 0` assertion holds. The actual list
  contains all nine committed non-`plans/j/` paths, including the three
  exempt ones. No ERROR, and nothing passed.
- `ruff check`, `ruff format --check` and `docformatter -c` on the test file
  are all clean. The file is 188 lines.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **The `.md` suffix of both globs was unpinned**
   - Location: `tests/test_changed_files.py`, the fixture of
     `test_exempt_paths_committed_in_the_run_are_dropped`
   - Problem: no KEEP path sat just past the `\.md` suffix boundary.
     `^(memory|\.claude/handoff-[^/]+|inbox/[^/]+)$` dropped exactly the
     three exempt paths and none of the old near-misses, so it passed. A
     `case` arm such as `inbox/*)` would pass the same way.
   - Fix: added KEEP paths `inbox/x.txt` and `.claude/handoff-task.json`.
   - **Status**: FIXED. The variant with no `.md` suffix now fails, keeping
     `.claude/handoff-task.json` and `inbox/x.txt` out of the list.

2. **The anchor at the path start was unpinned**
   - Location: same fixture
   - Problem: with every exempt and near-miss path at the repo root, an
     exemption missing its `^` behaved the same as a correct one.
     `(memory|…|inbox/[^/]+\.md)$` passed, so a nested `docs/inbox/x.md`
     would have been silently dropped. This matters for this slice because
     the shared alternation in `exempt-paths.sh` will probably carry no
     anchors of its own: `verify-step.sh` wraps it in a porcelain-specific
     `^[^RC][^RC] "?…"?$`. So `changed-files.sh` must add its own anchors,
     and that is where an anchor gets lost.
   - Fix: added KEEP path `docs/inbox/x.md`.
   - **Status**: FIXED. The variant with no `^` now fails on
     `docs/inbox/x.md` alone, so this near-miss does not repeat another
     one's check.

### Minor Issues

1. **The docstring broke an inline literal across lines and doubled a
   backslash**
   - Location: the test docstring
   - Problem: ``` ``.claude/handoff-`` ``` and ``` ``task.md`` ``` were
     split across a line break inside one inline literal. Also, in an
     `r"""` string, `inbox/[^/]+\\.md` renders with two backslashes, which
     is not the pattern.
   - Fix: rewrote the docstring. It now names each near-miss with the
     boundary it pins, and the alternation sits in an indented literal
     block with single backslashes. `docformatter -c` is clean.
   - **Status**: FIXED

2. **Literal hardcoding of the three names still passes**
   - Location: same test
   - Note: `case "$path" in memory|.claude/handoff-task.md|inbox/x.md)
     continue ;;` passes. It was run against the test and returned PASS. A
     test with two differently named exempt files per glob would rule out
     this one shape. It would still not prove KD-6's structural rule: the
     alternation has to come from `exempt-paths.sh`, the same source
     `verify-step.sh` reads, and a behavioural test of `changed-files.sh`
     alone cannot see where the pattern comes from. The dispatch asked for
     no over-engineering here. The near-miss set already rejects the
     realistic wrong patterns (shell `case` globs, missing anchors,
     ungrouped anchors, prefix and suffix drift). Sourcing is the GREEN's
     structural requirement, and the slice's code review checks it.
   - **Status**: OUT-OF-SCOPE. It is a structural property of the
     implementation (`exempt-paths.sh` sourced by both scripts), and the
     implementation is OUT for this review. Flagged for the code review.

3. **No near-miss for a path under a `memory/` directory**
   - Location: same test
   - Note: a pathspec exclude `:!memory` also drops `memory/x`, which the
     anchored alternation keeps. That fixture cannot sit next to a regular
     file named `memory`, because one path cannot be both a file and a
     directory. In this repo, and in gitlore consumers, `memory` is a
     gitlink, so `memory/x` never appears in a parent-repo diff. Pinning it
     would need a separate test over a fixture the real pipeline does not
     produce.
   - **Status**: OUT-OF-SCOPE. The path cannot occur in a real run, so there
     is nothing to fix in this slice.

## Wrong-reason hunting

**The state that fails the test once implemented**: `changed-files.sh` drops
fewer or more paths than exactly the anchored alternation
`^(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)$`. If it drops fewer,
an exempt path shows up in the list. If it drops more, a KEEP path goes
missing.

**What else could produce the observable**: the three exempt paths vanish
from the list only if the SUT filters them. Nothing in the fixture removes
them upstream: they sit in the same commit as the item report, the base is
that commit's parent, and they are not under `plans/j/`. Exact-list equality
rules out the "drops too much" shapes.

**Scratch-copy runs.** Each variant copied the SUT to the scratchpad, added
one candidate exemption check after the `plans/<job>/` arm, and ran the
unmodified test function from the test module with only `SCRIPT` rebound.
The test file was never moved, and the real SUT was never touched
(`git diff -- plugin/` is empty).

| Variant | Result | Near-miss(es) dropped |
|---|---|---|
| correct `^(memory\|\.claude/handoff-[^/]+\.md\|inbox/[^/]+\.md)$` | PASS | none |
| shell `case` glob `memory\|.claude/handoff-*.md\|inbox/*.md` | FAIL | `inbox/sub/y.md` |
| ungrouped `^memory\|…\|inbox/[^/]+\.md$` | FAIL | `memoryx.txt`, `docs/inbox/x.md` |
| no leading `^` | FAIL | `docs/inbox/x.md` |
| no trailing `$` | FAIL | `memoryx.txt` |
| `memory.*` | FAIL | `memoryx.txt` |
| no `handoff-` prefix (`\.claude/[^/]+\.md`) | FAIL | `.claude/other.md` |
| no `.md` suffix | FAIL | `inbox/x.txt`, `.claude/handoff-task.json` |
| three hardcoded literals | PASS | none (Minor 2) |

The PASS for the correct variant shows the expected list is reachable. The
order is `git diff`'s byte-sorted output, and the test does not demand
anything an honest implementation cannot produce.

**Shape checklist**:
- Birth state: the paths start out present in the commit, so dropping them
  is a real change.
- Bare negative: no. Exact-list equality pairs each "exempt path absent"
  with "every near-miss present" over the same commit.
- A substring another line satisfies: no. The test compares whole lines.
- Fixture reachability: a regular file named `memory` stands in for the
  gitlink. `git diff --name-only` prints `memory` for both, so the filter
  sees the same input.

## Fixes Applied

- `tests/test_changed_files.py`, fixture: added KEEP paths `inbox/x.txt`,
  `.claude/handoff-task.json` and `docs/inbox/x.md`, and extended the
  expected list in sorted order.
- `tests/test_changed_files.py`, docstring: fixed the broken inline literal
  and the doubled backslash, put the alternation in a literal block, and
  named the boundary each near-miss pins.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Slice 2: a run commit also touching `inbox/x.md`, `.claude/handoff-task.md`, `memory`; none of them appears | Satisfied | all three are in the item 1.1 commit, and the exact-list assertion excludes them |
| Interface: exit 0, `BASE: <sha>`, then one path per line | Satisfied | asserts `returncode == 0`, then `BASE:` first, then paths |
| KD-6: alternation shared with `verify-step.sh` | Not testable here | Minor 2; for the GREEN's code review |

## Positive Observations

- Asserting the exact list, rather than `not in` checks, was already the
  right choice. The RED report records that the bare negatives were
  considered and rejected.
- The exempt paths share a commit with the item report, as the slice text
  specifies, so base selection is not doing double duty.
- The KEEP near-misses already there each pinned a real boundary. None was
  redundant once the new ones were added.

## Recommendations

- GREEN code review: confirm that `changed-files.sh` sources
  `exempt-paths.sh` and wraps the alternation in a grouped `^(…)$`, and that
  `verify-step.sh` builds its pattern from the same variable (KD-6). That
  check closes Minor 2.
