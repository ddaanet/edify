# Item 2.2/2 refactor: split the run-location tests

`tests/test_triage_feedback.py` was at 399/400 lines. Moved
`test_subdirectory_run_measures_the_repository_root` and
`test_cdpath_does_not_move_the_script_dir`, bodies unchanged, into
`tests/test_triage_feedback_location.py` (111 lines). The hub is now 308
lines, dropped the unused `_run_triage_relative` import, and its docstring
names the new sibling beside the three it already named.

Collected tests over `tests/test_triage_feedback*.py`: 26 before, 26 after.

Renames: none.
