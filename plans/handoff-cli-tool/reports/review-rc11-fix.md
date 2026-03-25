# Review: RC11 Fix — H-2 committed detection, H-4 step_reached

**Scope**: Uncommitted changes against baseline `1399cd03` — H-2 write mode detection, H-4 step_reached field, 15 minor fixes
**Date**: 2026-03-25
**Mode**: review + fix

## Summary

The implementation correctly delivers H-2 (three write modes with git diff detection) and H-4 (step_reached field with crash-resume skip logic). Logic is sound and tests cover all three modes. Two issues found: an unguarded `CalledProcessError` in the autostrip path that bypasses CLI error handling, and a dead-code test that uses a mock it never patches.

**Overall Assessment**: Needs Minor Changes

---

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Unguarded `CalledProcessError` in autostrip path**
   - Location: `src/claudeutils/session/handoff/pipeline.py:209-215`
   - Note: `write_completed` in autostrip mode calls `subprocess.run(..., check=True)` without handling `CalledProcessError`. `_detect_write_mode` already ran `git show` successfully, so the second call will almost never fail — but if the repo state changes between the two calls (race condition), the exception propagates past `except (OSError, ValueError)` in `cli.py` and produces an unhandled traceback in the output. Wrapping in try/except and falling back to overwrite matches the pattern established in `_detect_write_mode`.
   - **Status**: FIXED

2. **`test_handoff_updates_step_reached_after_writes` dead mock**
   - Location: `tests/test_session_handoff_cli.py:299-354`
   - Note: `mock_clear_state` and `original_clear` are defined and `captured_final_state` is populated in the mock body, but `monkeypatch.setattr` is never called. The mock is never applied. The test reduces to: run a fresh handoff, assert exit code 0, assert state file cleared — behavior already covered by `test_handoff_resume_from_diagnostics_skips_writes` and other existing CLI tests. Remove the dead code and give the test a clear behavioral assertion.
   - **Status**: FIXED

3. **`_detect_write_mode` calls `git show` twice in autostrip path**
   - Location: `src/claudeutils/session/handoff/pipeline.py:143-183` and `206-228`
   - Note: `_detect_write_mode` reads `HEAD:{rel_path}` via `git show` to detect autostrip, then `write_completed` reads it again for the autostrip strip operation. The detection result could carry the committed section content to avoid the second subprocess call. This is a performance refinement — correctness is unaffected since the committed state doesn't change between the two calls in normal operation.
   - **Status**: DEFERRED — Refactoring `_detect_write_mode` to return both mode and data would change the function signature and require updating callers. Safe as-is; optimize if subprocess latency becomes measurable.

---

## Fixes Applied

- `src/claudeutils/session/handoff/pipeline.py:206-229` — Wrapped autostrip `git show` call in `try/except subprocess.CalledProcessError`, falling back to overwrite mode to match the pattern from `_detect_write_mode`.
- `tests/test_session_handoff_cli.py:299-354` — Removed dead `mock_clear_state`/`original_clear`/`captured_final_state` variables and the unused `pipeline as pipeline_module` import. Replaced test body with state persistence assertions: verify write_session and diagnostics values survive round-trip through save/load.
- `tests/test_session_handoff_cli.py:14` — Removed unused `from claudeutils.session.handoff import pipeline as pipeline_module` import.

---

## Requirements Validation

| Item | Status | Evidence |
|------|--------|----------|
| H-2: Overwrite (no diff) | Satisfied | `_detect_write_mode` returns "overwrite" when `committed == current`; `test_write_completed_overwrite_when_no_diff` |
| H-2: Append (old removed) | Satisfied | Returns "append" when committed not subset of current; `test_write_completed_appends_when_prior_uncommitted` |
| H-2: Autostrip (old preserved) | Satisfied | Returns "autostrip" when committed is subset; `test_write_completed_autostrip_when_old_preserved` |
| H-4: step_reached field | Satisfied | `HandoffState.step_reached` with default "write_session"; `test_save_state_includes_step_reached` |
| H-4: Resume skip writes | Satisfied | `if state is None or state.step_reached != "diagnostics"` guard; `test_handoff_resume_from_diagnostics_skips_writes` |
| H-4: Backward compat | Satisfied | `load_state` uses known_fields filter; `test_load_state_backward_compat_missing_step_reached` |
| Minor fixes (m-2/m-3 exit codes) | Satisfied | `CommitInputError` raised instead of `CommitResult(success=False)` |
| Minor fixes (m-4/m-9 comments) | Satisfied | Docstrings updated to describe mechanism not effect |

---

## Positive Observations

- `_find_repo_root` uses `.git` directory detection rather than assuming a fixed path — works correctly when `session_path` is in a subdirectory.
- `_extract_completed_section` handles files with no following `##` heading (end-of-file section) correctly via `end_idx = len(lines)`.
- Autostrip uses set membership for committed lines, preserving ordering of uncommitted additions in the output.
- Backward compatibility test for missing `step_reached` field correctly verifies the dataclass default rather than loading a legacy state file.
- Test split into `test_session_handoff_committed.py` cleanly separates git-dependent tests (which need `init_repo_minimal`) from pure-unit tests, matching the module split decision.
