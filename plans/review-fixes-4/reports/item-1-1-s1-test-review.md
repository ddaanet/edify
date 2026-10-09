# Review: Item 1.1 slice 1 test review (review-fixes-4)

**Scope**: `tests/test_triage_feedback_failures.py::test_root_cd_failure_is_one_error_line` (uncommitted) and the RED report. SUT `plugin/bin/triage-feedback.sh` mutated transiently only.
**Mode**: review + fix (test review)
**Requirements validation**: outline Item 1.1 slice 1 only.

## Summary

The test pins the `cd "$repo_root"` guard through a `git` shim. It passes on HEAD by design. Three own mutations, each different from the RED dispatch's whole-block replacement, red it on the intended assertion; two minor hardening fixes applied. Overall Assessment: Ready.

## Mechanical first check (mutation reproduction)

Unmutated: test passes (9 passed in module). Each mutation by exact-string Edit, restored by the swapped Edit.

| Mutation (in the guard block) | Result |
|---|---|
| `cannot change to` -> `cannot chdir to` | RED on the stdout assertion (diff shows `chdir` vs `change`) |
| `exit 2` -> `exit 3` | RED on the exit-code assertion (`assert 3 == 2`); stdout assertion passed |
| `"$repo_root"` -> `$repo_root` in the `printf` (after the space fix below) | RED on the stdout assertion (path split, message printed twice) |

Both assertions discriminate. The exit-1-with-empty-stdout bare-`cd` behaviour is from the round-4 probe and the RED dispatch's stdout-red; I did not re-measure the exit code under the bare `cd` (stdout assertion fires first, and the exit assertion is shown to discriminate by the `exit 3` mutation).

Restore verified: `git diff --stat -- plugin/bin/triage-feedback.sh` empty; no `chdir`, `exit 3` or unquoted-`$repo_root` text left; lines 43-46 are the original guard; module green (9 passed).

## Wrong-reason hunt

- The shim is what fires the guard: it answers `rev-parse --show-toplevel` with a path that never exists and exits 0, so the earlier `rev-parse` guard (message `ERROR: git rev-parse --show-toplevel failed`) cannot produce the asserted stdout. The asserted line `ERROR: cannot change to <path>` is unique to the `cd` guard, and the exact-equality stdout check excludes any other ERROR line or prefix. The `chdir` mutation shows no other path emits that text.
- Fixture: `_init_repo` + `_run_triage(JOB, repo, path_prepend=bin_dir)` match production invocation (absolute script path, CWD at repo root, PATH prepended, git config insulated). `_write_shim` passes every other git call (fixture's own `_init_repo` runs before the shim is used via `_run_git`, which resolves git on the unshimmed PATH).
- Missing path: `tmp_path / "missing root"` is never created, so nonexistent by construction.
- Bare negative, birth-state and fallback shapes: none apply; the asserted output exists only when the guard runs.

## Issues Found

### Minor Issues

1. **Shim path echoed with `echo`**
   - Location: test file, shim body.
   - Problem: `echo {root}` in `/bin/sh` may interpret backslash escapes in a path (dash); `printf '%s\n'` does not.
   - **Status**: FIXED (`printf '%s\\n' {root}` in the Python source).

2. **Quoting not exercised**
   - Location: test file, `missing = tmp_path / "missing-root"`.
   - Problem: a path without a space cannot detect an unquoted `$repo_root` in the guard's message.
   - Fix: directory renamed `missing root`; docstring states why. The unquoted-`printf` mutation above reds on it.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_triage_feedback_failures.py` — `missing` named `missing root`; shim uses `printf '%s\n'`; docstring gains one sentence on the space. No other changes.

## Gates

- Test still passes unmutated; reds under all three mutations above.
- `ruff format --check`, `ruff check`, `docformatter -c`: clean. 283 lines (cap 400). Docstring summary line within 70 characters.
- No SUT change remains; nothing committed.

## Positive Observations

- Exact-equality stdout assertion plus a separate exit-code assertion, each shown independently discriminating.
- Shim reuses `_write_shim` and passes unrelated git calls through.
