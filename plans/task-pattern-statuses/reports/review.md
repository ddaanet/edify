# Review: Task Pattern Statuses

**Scope**: Uncommitted changes — TASK_PATTERN regex extension + classification.md inference
**Date**: 2026-03-01T00:00:00
**Mode**: review + fix

## Summary

Three TASK_PATTERN regex locations extended from `[ x>]` to `[ x>!✗–]` to match blocked `[!]`, failed `[✗]`, and canceled `[–]` task statuses. `classification.md` added as a recognized planstate artifact. Tests added for each change. The core regex change is correct and all three source locations are updated. One behavioral issue found: `check_worktree_format` now incorrectly flags terminal-status tasks in Worktree Tasks as missing `→ slug`.

**Overall Assessment**: Ready (after fixes applied)

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`check_worktree_format` flags terminal tasks for missing slug**
   - Location: `src/claudeutils/validation/session_structure.py:72-77`, `tests/test_validation_session_structure.py`
   - Note: After the TASK_PATTERN extension, `check_worktree_format` now matches `[!]`, `[✗]`, `[–]` tasks in Worktree Tasks and flags them as missing `→ slug`. Terminal tasks don't have active worktrees and should not be required to carry a slug marker. The fix: skip the slug check for terminal statuses.
   - **Status**: FIXED

2. **Test coverage missing for the terminal-status worktree format case**
   - Location: `tests/test_validation_session_structure.py` (TestCheckWorktreeFormat)
   - Note: No test verifies that `[!]`, `[✗]`, `[–]` tasks in Worktree Tasks section are exempt from the `→ slug` requirement.
   - **Status**: FIXED

3. **`agent-core/bin/focus-session.py` uses `[.]` (any char) task pattern**
   - Location: `agent-core/bin/focus-session.py:26`
   - Note: This script uses `re.compile(rf"- \[.\] \*\*{re.escape(task_name)}\*\*")` which is a legacy standalone script, not part of the production `src/` package. The `[.]` wildcard already matches all statuses (including the new ones), so there is no functional regression. This file is outside the review's changed-file scope and the `[.]` is intentionally broader (it's a lookup by task name, not a classification). Out of scope.
   - **Status**: OUT-OF-SCOPE — legacy standalone script outside changed files; `[.]` already matches all statuses including new ones

## Fixes Applied

- `src/claudeutils/validation/session_structure.py:72-77` — Added terminal status check in `check_worktree_format`: tasks with `[!]`, `[✗]`, or `[–]` status skipped for slug validation
- `tests/test_validation_session_structure.py` — Added test `test_terminal_status_exempt_from_slug` to TestCheckWorktreeFormat

## Positive Observations

- All three TASK_PATTERN sites updated consistently — no location missed
- `noqa: RUF001` comments correctly applied at all sites (EN DASH `–` is intentional, not ambiguous Unicode)
- `noqa: RUF002` correctly applied in test docstrings that contain `✗`
- `classification.md` addition to planstate inference is minimal and correctly placed in the baseline artifacts list
- Test for `classification.md` inference is correctly written — validates no false "no recognized artifacts" error
- Tests in `test_worktree_session.py` use both literal `✗` and `\u2013` escape forms — mixing is fine, both are unambiguous in context
- Unicode escape form `\u2717` used in `test_validation_session_structure.py` avoids the RUF002 linting issue in fixture data correctly

## Recommendations

The `task_pattern` local variable in `worktree/session.py:extract_task_blocks` could be a module-level constant like the other two files, but this is pre-existing style and outside the diff scope.
