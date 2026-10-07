# gate-fix-narrow RED report

Job: review-fixes-2. Mode: RED. Nothing committed; the test and this report stay uncommitted for the GREEN commit.

## Changes

Only `/Users/david/code/edify/tests/test_changed_files.py`. The SUT is untouched.

- Module docstring D-90 sentence now names "the triage log ``plans/reports/triage-feedback-log.md``" in place of "the shared ``plans/reports/`` record".
- Test A renamed from `test_pipeline_record_under_plans_reports_is_dropped` to `test_triage_log_is_dropped_by_name`, with the docstring rewritten.

## Fixture

One run commit adds the files below. Expected stdout is BASE plus the sorted listed paths.

- Dropped:
  - `plans/j/reports/item-1-1.md` (the job's own record)
  - `plans/reports/triage-feedback-log.md`
- Listed:
  - `a.txt`
  - `plans/reports/explore-x.md` (Investigation deliverable)
  - `plans/reports/sub/x.md` (deliverable)
  - `plans/reports/triage-feedback-log.md.orig` (a prefix match wrongly drops it)
  - `docs/plans/reports/triage-feedback-log.md` (an unanchored match wrongly drops it)
  - `plans/reports/sub/triage-feedback-log.md` (a suffix or basename match wrongly drops it)
  - `plans/other/reports/item-1-1.md` (dropping all of `plans/` wrongly drops it)

## Per-test output

Command: `just test tests/test_changed_files.py -k triage_log_is_dropped` (foreground, unchanged script).

```
# Test Report

**Summary:** 0/1 passed, 1 failed

## Failures

### tests/test_changed_files.py::test_triage_log_is_dropped_by_name FAILED

```python
tests/test_changed_files.py:173: in test_triage_log_is_dropped_by_name
    assert result.stdout.splitlines() == [
E   AssertionError: BASE: 0a0dad2dbb43c50b8e7bb40c298519595967eb79
E     a.txt
E     docs/plans/reports/triage-feedback-log.md
E     plans/other/reports/item-1-1.md
E     
E   assert ['BASE: 0a0da.../item-1-1.md'] == ['BASE: 0a0da...-log.md', ...]
E     
E     Right contains 4 more items, first extra item: 'plans/reports/explore-x.md'
E     Use -v to get more diff
```
```

The test fails on its assertion, not on a missing symbol. The current `plans/reports/*` drop removes `explore-x.md`, `sub/x.md`, `.orig` and `sub/triage-feedback-log.md`.

## What each assertion discriminates

- `explore-x.md`, `sub/x.md`, `.orig` and `sub/triage-feedback-log.md` red now, because the current script drops all of `plans/reports/`.
- `docs/plans/reports/triage-feedback-log.md` and `plans/other/reports/item-1-1.md` already pass against the current script, so neither can red now. They guard only against a wrong GREEN: an unanchored or suffix match, and a drop of all of `plans/`. The code review should prove each by mutation.
- `sub/triage-feedback-log.md` reds now, but only because of the broad prefix drop. It also guards a basename or suffix GREEN.
- The log itself being dropped is satisfied by both old and new rules. It guards against GREEN removing the drop altogether.

## Near-misses dropped

`plans/reportsx.md` guarded only the old `plans/reports/` prefix's slash. An exact-path drop treats it like any unrelated path, so it no longer discriminates anything. `docs/plans/reports/x.md` was replaced by the `triage-feedback-log.md`-named copy, since the old name no longer tests the exact-path anchor.

## Mutation proof

None run; every red here is a genuine failure on the unchanged script.

## Fixtures tried and rejected

None.
