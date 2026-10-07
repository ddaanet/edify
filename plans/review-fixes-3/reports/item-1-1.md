# Item 1.1 report

Collected tests (`pytest --collect-only -q -p no:markdown_report`; the
markdown-report plugin prints `0/0 passed` instead of a count otherwise):

- before (hub + phase): 15 tests collected
- after (hub + errors + phase): 15 tests collected

Line counts:

```
  248 tests/test_changed_files.py
  161 tests/test_changed_files_errors.py
  205 tests/test_changed_files_phase.py
   88 tests/changed_files_helpers.py
  702 total
```

`command grep -n 'KD-' tests/test_changed_files.py tests/test_changed_files_errors.py tests/test_changed_files_phase.py tests/changed_files_helpers.py`:

```
(empty)
```

Moved to `test_changed_files_errors.py`, bodies unchanged:
`test_git_failure_is_error_not_no_base`, `test_no_item_report_exits_1`,
`test_unsafe_job_name_is_a_usage_error`,
`test_unloadable_exempt_paths_is_an_error_not_no_base`. Hub and phase
docstrings now point at the errors module; the errors module and hub each
say they were split to keep each module under its line cap.

Citation rewrites:

| File | Old | New | Reason |
|---|---|---|---|
| hub, triage-by-base test | KD-6 (drops all of plans/j/) | D-90 | list minus the job's own record is D-90 |
| hub, exempt test | KD-6 (three exempt paths) | D-91 | citation is the exempt paths |
| errors, no-item test | KD-1 | D-88 | item-report history keys the base |
| hub, NUL-delimited test | "Item 1.2 reads the diff NUL-delimited" | "D-90 reads the diff NUL-delimited" | other plan's item takes the decision it implements |
| hub, rename test | "Item 1.1's commit" | unchanged | names the fixture's own item commit |
| phase, module | KD-2 and KD-8 ... Item 1.4 | D-89 and D-94 | phase boundary by path (D-89), subject a label (D-94); Item 1.4 implements D-89, already cited |
| phase, module | run base (KD-1) | run base (D-88) | |
| phase, without-boundary test | KD-2 and KD-8; KD-1 | D-89 and D-94; D-88 | as above |
| phase, latest-boundary test | KD-2 and KD-8 | D-89 and D-94 | as above |
| phase, keeps-filters test | KD-6 and Item 1.4 | D-89, D-90 and D-91 | filters are D-90/D-91; Item 1.4 implements --phase (D-89) |
| helpers | KD-1, KD-2 and KD-6 in plans/build-fixes/outline.md | D-88, D-89 and D-90 in docs/references/build-run-state.md | base, phase, list |

`just precommit`: green ("Precommit OK"); only pre-existing soft
oversized-file warnings for plugin/agents files.
