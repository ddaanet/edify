# Item 1.2 / slice 2 — RED report

## Scope

Write `test_exempt_paths_committed_in_the_run_are_dropped` in
`tests/test_changed_files.py`. Slice 2 is not slice 1: the SUT
(`plugin/skills/build/scripts/changed-files.sh`, already implementing slice
1's base/diff behaviour) is untouched, per the dispatch's "later slices: do
not touch the SUT at all" rule.

## Test run

```
PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest tests/test_changed_files.py -vv
```

### `test_exempt_paths_committed_in_the_run_are_dropped` — FAILED

Failure line:

```
tests/test_changed_files.py:174: in test_exempt_paths_committed_in_the_run_are_dropped
    assert result.stdout.splitlines() == [
E   AssertionError: BASE: fb1b685b1071d4a6aaf718f004253674f841853a
E     .claude/handoff-task.md
E     .claude/other.md
E     inbox/sub/y.md
E     inbox/x.md
E     memory
E     memoryx.txt
E
E   assert ['BASE: fb1b6...'memory', ...] == ['BASE: fb1b6...'memoryx.txt']
E
E     At index 1 diff: '.claude/handoff-task.md' != '.claude/other.md'
E     Left contains 3 more items, first extra item: 'inbox/x.md'
```

`result.returncode == 0` passed first (the committed-diff behaviour from
slice 1 already exits 0 with a `BASE:` line), so the red lands on the exact
content assertion. The actual stdout carries all six committed paths —
including the three exempt ones (`.claude/handoff-task.md`, `inbox/x.md`,
`memory`) that the SUT does not yet drop — proving the red is a wrong value,
not a missing symbol or a crash before any assertion ran. It also carries the
three KEEP paths (`.claude/other.md`, `inbox/sub/y.md`, `memoryx.txt`) in
their expected positions, so the mismatch is specifically the un-dropped
exempt paths, not a wholesale wrong-shape failure that a trivial "drop
everything" or "drop nothing" implementation would both survive.

`test_base_is_parent_of_first_item_report_commit` (slice 1) still passes
unchanged, confirming slice 2's test addition did not disturb it.

## Non-vacuousness of the negative

The assertion is an exact full-list equality, not a subset check or a
"does not contain" check, so three failure shapes are all ruled out at once:

- An implementation that drops nothing (today's SUT) fails — demonstrated
  above.
- An implementation that drops all of `inbox/` (including `inbox/sub/y.md`)
  would omit `inbox/sub/y.md` from the actual list, violating the exact-list
  equality.
- An implementation that drops all of `.claude/` (including
  `.claude/other.md`) would likewise violate it.
- An implementation that drops nothing named `memory*` (including
  `memoryx.txt`) or treats `memory` as a prefix match would mis-list
  `memoryx.txt`.

The three KEEP paths were chosen to sit one step past each exemption's
boundary: `inbox/sub/y.md` is nested one level past the single-level glob
`inbox/[^/]+\.md`; `memoryx.txt` is not the exact name `memory`;
`.claude/other.md` does not match the `handoff-` prefix in
`.claude/handoff-[^/]+\.md` (the exemption alternation as it stands today in
`verify-step.sh`, which `exempt-paths.sh` will extract in a later slice).

## Fixtures tried and rejected

- **A separate commit per exempt/keep path.** Rejected in favor of one run
  commit carrying all six paths plus the item report, matching the slice
  text ("A run commit also touches inbox/x.md, .claude/handoff-task.md and a
  file named memory") and the KD-1 pattern already established in slice 1,
  where an item's report and its changed files land in the same commit. A
  multi-commit fixture would also leave the base-selection behaviour
  (already pinned by slice 1) doing incidental double duty in this test
  rather than isolating the exempt-path behaviour.
- **`docs/memory` instead of `memoryx.txt` as the near-miss for the exact
  name `memory`.** Both satisfy the dispatch's suggested near-misses
  equally; `memoryx.txt` was kept because it needs no extra directory and
  reads unambiguously as "not literally `memory`" without relying on a
  reader noticing a nested path is doing double duty (nested-ness is already
  `inbox/sub/y.md`'s job).
- **Dropping the KEEP paths entirely, asserting only that the three exempt
  paths are absent.** Rejected: a fixture carrying no KEEP path reds
  identically whether the SUT drops nothing, drops exactly the three exempt
  paths, or drops everything matching `inbox/`, `.claude/` or `memory` as a
  prefix — the case worth recording, since it is the red the item's own
  mutation-adjacent reasoning would also have produced on a widened guard.
  Adding the three KEEP paths and asserting the exact list is what rules the
  broader-drop implementations out, not just the no-drop one.
- **Asserting only `not in` for each exempt path**, dropping the exact-list
  form. Rejected: a `not in` assertion is a red this item's own future GREEN
  implementation would pass, but so would an implementation that dropped
  everything (including the KEEP paths), which the slice's own interface
  contract ("drop the exempt paths", not "drop more than the exempt paths")
  rules out. The exact-list form is the one `non-vacuous-negatives.md`'s
  "assert the exact output" rule and the mutation-adjacent reasoning above
  both call for.

## Mutation proof

None. The test fails on its own assertion against the unmodified SUT (an
`AssertionError` on a wrong value: the exempt paths are present where the
expected list has none), which is itself evidence the exempt-dropping
behaviour is absent from `changed-files.sh` today — confirmed by reading the
script, which excludes only the `plans/$job/` prefix and has no exempt
alternation of any kind. Per the RED protocol, mutation proof is required
only when the asserted behaviour already exists in the SUT and the ordering
cannot supply a red on its own; that does not hold here, so no mutation was
performed.

## Scope confirmation

Only the one named test was added to `tests/test_changed_files.py`. The SUT
(`plugin/skills/build/scripts/changed-files.sh`) was not touched.
`exempt-paths.sh`, `verify-step.sh`, slice 3
(`test_no_item_report_exits_1`), and Item 1.3 onward are untouched.

## Lint

```
PATH=/Users/david/code/edify/.venv/bin:$PATH ruff check tests/test_changed_files.py
```
→ All checks passed (after switching the new test's docstring to `r"""`,
required by `D301` because it carries a `\.` escape in a regex reference).

```
PATH=/Users/david/code/edify/.venv/bin:$PATH docformatter -c tests/test_changed_files.py
```
→ clean, no diff.

## Files

- `tests/test_changed_files.py` (one test added:
  `test_exempt_paths_committed_in_the_run_are_dropped`)
