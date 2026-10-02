# Item 1.2 / Slice 3 — RED report

`test_no_item_report_exits_1` in `tests/test_changed_files.py`.

## Mode

RED. k>1 (slice 3 of Item 1.2): the SUT
(`plugin/skills/build/scripts/changed-files.sh`) was not touched, except for
the git-status check confirming that below. `git status --porcelain` at the
end of this dispatch shows only `tests/test_changed_files.py` modified.

## Fixture

The repo (`_init_repo` seed, per the module's existing pattern) holds:

- a committed `item-*` report for a **different** job —
  `plans/other/reports/item-1-1.md`
- two committed planning reports for job `j` that do not match `item-*` —
  `plans/j/reports/explore-x.md`, `plans/j/reports/outline-review.md`
- an **uncommitted** `plans/j/reports/item-1-1.md` written directly to disk
  (not `git add`ed, not committed)

No `plans/j/reports/item-*` report is ever committed. An implementation that
globs the filesystem, ignores the job, or matches any committed report
regardless of the `item-*` name would each wrongly derive a base from one of
these decoys instead of reporting `NO-BASE:`.

## Per-test output

### `test_no_item_report_exits_1`

Ran: `PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest
tests/test_changed_files.py -v`

Failure (against the current, unchanged `changed-files.sh`):

```
tests/test_changed_files.py:220: in test_no_item_report_exits_1
    assert result.returncode == 1, result.stdout + result.stderr
AssertionError: ERROR: cannot resolve the parent of first item report commit ""

assert 2 == 1
 +  where 2 = CompletedProcess(args=['/Users/david/code/edify/plugin/skills/build/scripts/changed-files.sh', 'j'], returncode=2, stdout='ERROR: cannot resolve the parent of first item report commit ""\n', stderr='').returncode
```

This is a genuine assertion-level red on unchanged code, not an
`ImportError`/`AttributeError`/missing-script failure: the script runs, but
conflates "no item report at all" with "the resolved commit has no parent"
and exits 2 with an `ERROR:` line instead of exit 1 with `NO-BASE:`. The
first assertion (`returncode == 1`) is the one that reds; the `NO-BASE:`
prefix and no-`BASE:`-line assertions below it never ran, per
`genuine-red.md`'s point that a red under `errexit`/`assert` is evidence only
for the assertion it lands on. Confirmed the two already-passing tests in
the same module still pass (no regression from the new fixture additions):

```
tests/test_changed_files.py::test_base_is_parent_of_first_item_report_commit PASSED
tests/test_changed_files.py::test_exempt_paths_committed_in_the_run_are_dropped PASSED
```

## Mutation proof

None. The behaviour `test_no_item_report_exits_1` asserts (exit 1 /
`NO-BASE:` when no `item-*` report is committed) is not already present in
the SUT — the current script exits 2 with `ERROR:` for this case, confirmed
by direct probe and by the pytest run above — so the ordering itself supplies
a genuine red and no mutation of `changed-files.sh` is needed or was
performed.

## Fixtures tried and rejected

- **Omit the other-job `item-*` report and the two same-job planning
  reports, keep only the uncommitted `item-1-1.md`.** Rejected: a red
  produced from this narrower fixture would not distinguish KD-1's
  "committed, job-scoped, `item-*`-named" derivation from a filesystem glob —
  both would see nothing *committed* for job `j` and both would also see
  the uncommitted file if they read the working tree, so the test would not
  separate a correct implementation from a glob-based one once the SUT is
  fixed. Any one of these three decoys alone is a red that the item's own
  future mutation testing would also produce (an unscoped job match, an
  unanchored `item-*` match, or a working-tree read), so all three are kept
  together to rule each out independently.
- **Asserting `"BASE:" not in result.stdout`.** Rejected: `"NO-BASE:"`
  contains the substring `"BASE:"` starting at its third character, so this
  assertion is vacuously satisfiable only by accident — it would pass on the
  correct `NO-BASE:` output and is not a meaningful check on its own, but
  worse, naively worded it could mask a leaked `BASE: <sha>` line in output
  that also happens to start `NO-BASE:`. Used
  `line.startswith("BASE: ")` (with the trailing space that `BASE:
  <sha>` always carries) instead, which does not match a `NO-BASE:` line.
- **Asserting the exact full stdout content (`==` a fixed list) for the
  `NO-BASE:` case.** Rejected: the interface block only commits to "stdout
  starting `NO-BASE:`" for exit 1, unlike the exit-0 interface which is
  fully pinned path-by-path. Pinning more than the interface promises would
  make this test fail on a GREEN implementation that adds explanatory text
  after `NO-BASE:`, which is not a behaviour this slice's contract rules
  out.

## Lint

- `PATH=/Users/david/code/edify/.venv/bin:$PATH ruff check
  tests/test_changed_files.py` — All checks passed!
- `PATH=/Users/david/code/edify/.venv/bin:$PATH docformatter -c
  tests/test_changed_files.py` — exit 0 (no reformatting needed; the first
  docstring line was shortened to fit without a mid-token wrap, since
  docformatter initially wanted to split `` ``NO-BASE:`` `` across two
  lines).

## Scope

Only `test_no_item_report_exits_1` was added. No edits to
`changed-files.sh`, `scripts/exempt-paths.sh`, or `verify-step.sh`. No
commit made (RED dispatch).
