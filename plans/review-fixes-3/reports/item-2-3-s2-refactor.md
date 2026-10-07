# Item 2.3/2 refactor: one PATH-shim helper

Added `_write_shim(tmp_path, tool, body)` to `tests/changed_files_helpers.py`:
it resolves the real tool with `shutil.which`, writes `real=<shlex.quote path>`
as the shim's first line, appends the caller's body, `chmod 0o755`, returns the
bin directory. Placed there because neither helper module imports the other, so
the triage test module imports it without a cycle.

Migrated: the `git` shim and the `sed` shim in
`tests/test_triage_feedback_failures.py`, the `git` shim in
`tests/test_changed_files_errors.py`. Fault and pass-through are unchanged; the
older triage `git` shim now uses `shlex.quote`. Bodies reach the real tool as
`"$real"`. Unused `shlex`/`shutil` imports removed.

Left alone (outside job scope): `tests/line_limits_helpers.py` and its shim.

Verification: collected count 47 (unchanged modules, no tests added or
removed); bash 3.2 run 46 passed, 1 failed (the known
`test_unloadable_exempt_paths_is_an_error_not_no_base[absent]`).
All modules under 400 lines (largest 253).
