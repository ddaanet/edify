# Item 1.2 slice 1 RED — idempotent triage log append

Mode: RED. SUT `plugin/bin/triage-feedback.sh` untouched.

## Changes (uncommitted)

- `tests/test_triage_feedback_log.py` (new, 64 lines): `test_rerun_appends_no_duplicate_row`. Module docstring gives the line-cap split reason.
- `tests/triage_feedback_helpers.py`: new `_commit_reports_fixture(repo)`, the slice 1.1/2 fixture (planning commit, item-1-1 + notes.txt, item-1-12 + revisited runbook-review + explore/notes.md, review-code.md).
- `tests/test_triage_feedback.py` (339 lines): `test_reports_exclude_the_per_item_report` now calls the helper; the helper import is added.

## Per-test output

- `tests/test_triage_feedback_log.py::test_rerun_appends_no_duplicate_row` — FAILED on its assertion, not an error:
  `tests/test_triage_feedback_log.py:46: assert rows == [first_row]`
  with `rows` holding two identical rows, `| 2026-10-05 | j | Simple | 1 | 0 | no | match |` twice. The unconditional append duplicated the row on the second run.
- `tests/test_triage_feedback.py` and `tests/test_triage_feedback_behavioral.py`: 16 passed.

Legs after the failing one (pre-seeded row under `2000-01-01` gains none; a run commit adding `item-1-2.md` and `c.txt` moves Files changed to 2 and appends a second row, ending `| 2 | 0 | no | match |`) are not reached against the unchanged SUT. The pre-seeded leg would red against an unconditional append and the last leg against a skip keyed on job alone, but neither is demonstrated here.

Ruff check and format check pass on the three test files.

## Fixtures tried and rejected

- Re-seeding the log with a copy of the first row and the date changed in place via string replace on the whole line: rejected for splitting the row at the first ` | ` after the date column, which cannot also replace a matching substring elsewhere in the row.
- Building a fresh fixture inside the new module rather than moving the slice 1.1/2 builder: rejected, since it duplicates `test_reports_exclude_the_per_item_report`'s commits; the builder lives in helpers instead.
- Keeping the test in `tests/test_triage_feedback.py`: rejected, it would pass 400 lines.
