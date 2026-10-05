# Item 1.1 slice 3 — RED (review-fixes-2)

SUT `plugin/bin/triage-feedback.sh` untouched.

## Tests

- `tests/test_triage_feedback.py::test_behavioral_code_reads_the_lists_paths_only`
  — FAILED on its assertion, not an error:
  `assert "- Behavioral code: no" in lines` with stdout
  `Files changed: 0 / Reports: 0 / Behavioral code: yes`. Today's script diffs
  the whole `<base> HEAD` range and reads the `def` in `inbox/x.md`.
- The other 9 tests in the module pass (9/10 passed, 1 failed).

Later legs (`a.py` -> `yes`; non-empty-list repo -> `no`) are not reached in
the red run, since the first assertion stops the test. No mutation proof is
needed: the test fails without one.

## Fixture notes

- Leg 1 holds `item-1-1.md` (with the `class with an explicit whitelist`
  line) and `inbox/x.md` (`def foo():`) and asserts `Files changed: 0`, so the
  empty list is pinned, then `Behavioral code: no`. A further commit of
  `a.py` reads `yes` on the same repo.
- The module was 310 lines; it is 356 now, under 400. No split, so no
  deviation from "the tests stay in `tests/test_triage_feedback.py`". Slices
  4-5 and Item 1.2 may need one.
- `ruff check` and `ruff format` clean on the module.

## Fixtures tried and rejected

- Leg 1 alone, as the slice names it: its list is empty, so an
  implementation that returns `no` on an empty list but diffs the whole range
  for a non-empty one passes both its legs. Kept, and strengthened with a
  second repo (`notes.txt` plain, plus `inbox/x.md` holding the `def`) that
  asserts `Files changed: 1` and `Behavioral code: no`. That repo's `no`
  comes only from limiting the diff to the list's paths.
