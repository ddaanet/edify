# Review: handoff-cli-tool RC13 fix (9 commits)

**Scope**: 95e1cfd5..HEAD — RC13 fix addressing 18 of 22 carried minor findings
**Date**: 2026-03-25
**Mode**: review + fix

## Summary

9 commits fix 18 minors across implementation (pipeline.py, cli.py, status/cli.py) and tests. The functional fixes are sound: blank line preservation in append/autostrip, `_detect_write_mode` return type refactoring, trailing whitespace normalization, empty git output guard, status error message accuracy. Test changes are well-targeted: new coverage for the three fixed modes, split conflated tests, fixture ordering correction, assertion specificity.

4 of the original 22 minors (m-4, m-12, m-20, m-21, m-22) carry forward. m-16 was addressed (test removed). m-20/m-21/m-22 are out of scope.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **m-5 test uses weak assertion (`!= "autostrip"`) instead of specific mode**
   - Location: `tests/test_session_handoff_committed.py:204`
   - Note: The indentation scenario deterministically produces "append": committed `- Old task A` vs current `  - Old task A` (via `rstrip()`) — not a subset match. `assert mode == "append"` is more precise and catches regressions in mode detection logic that `!= "autostrip"` would miss.
   - **Status**: FIXED

2. **Autostrip committed_set uses `.strip()` while mode detection uses `.rstrip()` — inconsistency**
   - Location: `src/claudeutils/session/handoff/pipeline.py:209-217`
   - Note: `_detect_write_mode` uses `line.rstrip()` in both committed_lines and current_lines to preserve leading whitespace for indentation-aware comparison. But `write_completed` autostrip path uses `line.strip()` in committed_set and `line.strip()` in the filter predicate — losing leading whitespace. An indented committed line `  - Item` would be stripped to `- Item` in committed_set, causing a content-different line to match the committed set and be incorrectly stripped. Aligned to `line.rstrip()` throughout.
   - **Status**: FIXED

3. **m-6 test asserts absence of empty-block delimiters rather than absent block header**
   - Location: `tests/test_session_handoff_cli.py:365`
   - Note: `assert "```\n\n```" not in result.output` checks for a specific malformed shape but doesn't verify the entire diagnostic block is suppressed. `assert "**Git status:**" not in result.output` directly tests the specified behavior (block omitted when empty).
   - **Status**: FIXED

4. **m-15 test does not verify state file cleared after resume**
   - Location: `tests/test_session_handoff_cli.py:382-391`
   - Note: Resume test verifies session.md content (status + completed) but not that `clear_state()` ran. State clearing is covered separately in `test_handoff_updates_step_reached_after_writes`, so this is not a coverage gap — just a scope boundary choice.
   - **Status**: DEFERRED — state clearing coverage exists in adjacent test; resume test scope is write execution only

## Fixes Applied

- `tests/test_session_handoff_committed.py:204` — strengthened m-5 assertion from `!= "autostrip"` to `== "append"` (deterministic for indentation change scenario)
- `src/claudeutils/session/handoff/pipeline.py:209,212` — aligned autostrip committed_set from `line.strip()` to `line.rstrip()` to match mode detection normalization; filter predicate likewise from `line.strip()` to `line.rstrip()`
- `tests/test_session_handoff_cli.py:365` — strengthened m-6 test assertion from empty-block shape check to `"**Git status:**" not in result.output` (tests block omission, not delimiter shape)

**Verification**: 79/79 tests pass after fixes.

## Requirements Validation

All H-2 design requirements verified by new tests:

| Requirement | Status | Evidence |
|-------------|--------|----------|
| H-2 overwrite mode | Satisfied | `test_detect_write_mode_all_three_modes`, `test_write_completed_overwrite_when_no_diff` |
| H-2 append mode | Satisfied | `test_write_completed_appends_when_prior_uncommitted`, `test_write_completed_append_preserves_blank_lines` |
| H-2 autostrip mode | Satisfied | `test_write_completed_autostrip_when_old_preserved`, `test_write_completed_autostrip_preserves_blank_lines` |
| H-2 error fallback (git show fails) | Satisfied | `test_detect_write_mode_overwrite_on_no_head` |
| H-4 resume from write_session | Satisfied | `test_handoff_resume_from_write_session` |
| H-3 empty diagnostic omission | Satisfied | `test_handoff_skips_empty_git_block` |

## Positive Observations

- `_detect_write_mode` refactoring (m-2): returning `tuple[str, str]` eliminates the duplicate `git show HEAD:` subprocess call in autostrip path — clean, zero behavior change
- Blank line preservation (m-1): the fix correctly uses `list(current.splitlines())` (no filter) for append and `if not line.strip() or ...` for autostrip — symmetric treatment
- `_extract_completed_section` `.strip("\n")` addition makes section comparison newline-insensitive without affecting downstream logic (writers use `splitlines()` anyway)
- m-10 test split: `_init_repo_with_session` helper factored out cleanly; three independent tests with focused docstrings replace one conflated test
- Status error message (m-3): now quantifies the problem (`{n} task lines`) rather than misidentifying cause as "old-format"

## Carried Findings (not addressed in this changeset)

- **m-4** `commit_gate.py:66` — `len(line) > 3` guard; no practical impact
- **m-12** — Inconsistent submodule setup helpers across test files
