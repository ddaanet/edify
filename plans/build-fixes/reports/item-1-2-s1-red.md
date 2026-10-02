# Item 1.2 / slice 1 — RED report

## Scope

Stub `plugin/skills/build/scripts/changed-files.sh` (inert: shebang line
only, `chmod 755`, exits 0, prints nothing) and
`tests/test_changed_files.py` carrying
`test_base_is_parent_of_first_item_report_commit`.

## SUT stub

```
#!/usr/bin/env bash
```

Executable, no commands — exits 0 with empty stdout/stderr. `shellcheck`
clean.

## Test run

```
PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest tests/test_changed_files.py -vv
```

### `test_base_is_parent_of_first_item_report_commit` — FAILED

Failure line:

```
tests/test_changed_files.py:113: in test_base_is_parent_of_first_item_report_commit
    assert result.stdout.splitlines() == [
E   AssertionError:
E   assert [] == ['BASE: 7559c941c7e839354d534633db74d26b5138c788', 'a.txt', 'b.txt']
```

`result.returncode == 0` passed first (the inert stub's default exit status
is 0, matching the interface's exit-0 shape), so the red lands on the
content assertion — a wrong value (empty stdout vs. the expected `BASE:`
line plus `a.txt`/`b.txt`), not on a missing symbol or a crash before any
assertion ran.

## Fixtures tried and rejected

- **Indexing `lines[0]` / `lines[1:]` separately.** The first draft split
  the assertion into `lines[0] == f"BASE: {base_sha}"` then
  `lines[1:] == ["a.txt", "b.txt"]`. Against the inert stub's empty stdout,
  `lines[0]` raised `IndexError: list index out of range` — a crash before
  any assertion body evaluated, the same class as an `ImportError`/missing-
  symbol red the skill rules out: it proves the list is empty, not that the
  assertion discriminates a wrong value from a right one. Rejected in favor
  of one list-equality assertion (`result.stdout.splitlines() ==
  ["BASE: …", "a.txt", "b.txt"]`), which reds on a genuine wrong-value
  `AssertionError` against the stub and will do the same against a future
  mutation that gets the path list wrong without reordering it, or gets the
  `BASE:` line wrong.
- **Modelling `_init_repo`/`_run_script` as verbatim imports from
  `test_verify_step.py`.** Rejected: that module's `_init_repo` seeds
  `.claude/handoff-task.md`, which this slice's test does not exercise
  (exempt-path dropping is slice 2's test), and its `_run_script` threads a
  stub-`just` `bin_dir` that `changed-files.sh` has no interface for. Wrote
  a narrower `_init_repo` (seeds `README.md` and `b.txt`, the file the third
  run commit needs to pre-exist so it changes rather than adds it) and a
  narrower `_run_script` (no `PATH`/`just` plumbing), keeping only the
  config-insulation pattern (`GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM`) and the
  run-by-absolute-path-with-CWD-at-repo-root shape in common.

## Mutation proof

None. The test fails on its own assertion against the inert stub (an
`AssertionError` on a wrong value), so no behaviour is already present in the
SUT for a mutation to disprove — the stub is empty by construction, and
step 4 of the RED protocol applies only when a test has passed and its
behaviour needs mutation evidence that the SUT already implements it. No
mutation was performed.

## Scope confirmation

Only the stub and the one named test were touched. `exempt-paths.sh`,
`verify-step.sh`, slices 2 and 3, and Item 1.3 onward are untouched.

## Files

- `plugin/skills/build/scripts/changed-files.sh` (new, inert stub)
- `tests/test_changed_files.py` (new, one test)
