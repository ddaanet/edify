# Item 1.1 slice 1 RED: review-fixes-4

Mode: RED. Job `review-fixes-4`, Item 1.1 (F3), slice 1. Nothing committed; the
test is left uncommitted in the tree.

## Test added

`tests/test_triage_feedback_failures.py::test_root_cd_failure_is_one_error_line`

A `git` shim written by `_write_shim` answers `rev-parse --show-toplevel` with
a nonexistent absolute path under `tmp_path` and exits 0; every other call
goes to `exec "$real" "$@"`. Triage runs from a fixture repo (`_init_repo`)
with the shim directory prepended to `PATH` (`_run_triage(..., path_prepend=)`).
Assertions: stdout equals `ERROR: cannot change to <path>\n`, exit 2.

Also added: `import shlex` (the shim's echoed path is quoted). The SUT was not
touched except for the transient mutation below.

## Run results

Unmutated tree, module run (`pytest -p no:markdown_report`):

- `test_root_cd_failure_is_one_error_line` PASSED
- Module: 9 passed.

This is the expected mutation-red case: the guard exists on HEAD, so the test
passes before mutation.

## Mutation proof

Mutation (Edit, old to new):

- Old: `if ! cd "$repo_root"; then` / `    printf 'ERROR: cannot change to %s\n' "$repo_root"` / `    exit 2` / `fi`
- New: `cd "$repo_root"`

Reds: `test_root_cd_failure_is_one_error_line`, on its stdout assertion (line 144):

```
E   AssertionError: .../triage-feedback.sh: line 43: cd: .../missing-root: No such file or directory
E   assert '' == 'ERROR: canno...issing-root\n'
FAILED tests/test_triage_feedback_failures.py::test_root_cd_failure_is_one_error_line
```

Observed stdout: empty. The `cd` error goes to stderr. The stdout assertion
fires first, so the exit code under mutation was not read from the test. The
round-4 probe recorded exit 1 with empty stdout; this dispatch did not
re-measure the exit code.

Restore (Edit, old and new swapped back to the guard block):

- `git diff --stat -- plugin/bin/triage-feedback.sh`: empty output
- `grep -n -F 'if ! cd "$repo_root"; then'`: line 43
- Bare `cd "$repo_root"` as a whole line: 0 matches
- Module run after restore: 9 passed

## Gates

- `ruff format --check tests/test_triage_feedback_failures.py`: already formatted
- `ruff check tests/test_triage_feedback_failures.py`: all checks passed
- `docformatter -c tests/test_triage_feedback_failures.py`: exit 0
- Line count: 282 (cap 400)

`just precommit` was not run, per the dispatch (the tree is intentionally
dirty).

## Fixtures tried and rejected

None.

## Tree state observed

`git status --porcelain` shows, besides `M tests/test_triage_feedback_failures.py`:

- `?? inbox/brief-corrector-reads-surfaces-against-each-other.md`
- `?? inbox/brief-review-range-verdict-binds.md`
- `?? inbox/brief-slice-code-review-mutation-runs.md`
- `?? .claude/launch.json`, `.claude/loop.md`, `.claude/output-styles`, `.claude/routines`, `.claude/workflows`

The three `inbox/` files were already untracked at session start and are not
touched. The `.claude/` entries are not in the session-start status snapshot
and were not created or touched by this dispatch; they are reported as
observed and left alone.
