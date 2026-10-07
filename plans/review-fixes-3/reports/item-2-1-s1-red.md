# Item 2.1 slice 1 RED

## Test written

`tests/test_changed_files_errors.py::test_late_diff_failure_prints_error_alone`
(cites D-90). A `git` shim ahead on `PATH` runs the real git (absolute path from
`shutil.which`), then exits 128 when its first argument is `diff`. The run
commit adds `plans/j/reports/item-1-1.md` and `a.txt`, and changes the seeded
`b.txt`. Asserts exit 2, then stdout lines `== ["ERROR: git diff failed"]`.

Also changed: the module docstring gained one paragraph; `_run_script` in
`tests/changed_files_helpers.py` gained a keyword-only
`path_prepend: Path | None = None` (existing callers unchanged).
`changed-files.sh` untouched.

## Failing output (verbatim)

```
tests/test_changed_files_errors.py:200: in test_late_diff_failure_prints_error_alone
    assert result.stdout.splitlines() == ["ERROR: git diff failed"], result.stdout
E   AssertionError: BASE: 98c4c8bccbf534c1ce3495b8d3a0440e6d83ef54
E     a.txt
E     b.txt
E     ERROR: git diff failed
E
E   assert ['BASE: 98c4c... diff failed'] == ['ERROR: git diff failed']
E
E     At index 0 diff: 'BASE: 98c4c8bccbf534c1ce3495b8d3a0440e6d83ef54' != 'ERROR: git diff failed'
E     Left contains 3 more items, first extra item: 'a.txt'
FAILED tests/test_changed_files_errors.py::test_late_diff_failure_prints_error_alone
```

The exit-2 assertion passed (the script already exits 2); the red is on the
stdout assertion, line 200.

## Sibling tests

`tests/test_changed_files.py`, `tests/test_changed_files_errors.py`,
`tests/test_changed_files_phase.py`: 1 failed (the new test), 15 passed.
`ruff check` and `ruff format --check` on the two touched test files: clean.

## Mutation proof

None needed: the behaviour is absent from the SUT.

## Fixtures tried and rejected

None.
