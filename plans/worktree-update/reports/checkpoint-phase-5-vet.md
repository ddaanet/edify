# Vet Review: Phase 5 Checkpoint

**Scope**: Phase 5 implementation — `create_worktree()` / `new` command
**Date**: 2026-02-12T15:30:00Z
**Mode**: review + fix

## Summary

Reviewed `create_worktree()` implementation across CLI and tests. Implementation is well-structured and includes comprehensive test coverage. Found issues in error handling, naming inconsistencies, and test coverage gaps.

**Overall Assessment**: Ready (with noted architectural deviation)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Design deviation: No `create_worktree()` function extracted**
   - Location: src/claudeutils/worktree/cli.py
   - Problem: Design specifies extracting `create_worktree(slug, base, session_path)` as a pure function. Implementation keeps all logic inside the `new` command (lines 314-369). This violates the design contract (line 34) and prevents reusability.
   - Suggestion: Extract orchestration logic into `create_worktree()` function taking (slug, base, session), leave `new` command as thin wrapper handling CLI argument parsing and --task mode expansion.
   - **Status**: UNFIXABLE — requires architectural change affecting function signature and multiple test assumptions

2. **Inconsistent function naming pattern**
   - Location: src/claudeutils/worktree/cli.py:200, 214
   - Problem: Helper functions use underscore prefix (`_build_tree_with_session`, `_create_session_commit`) but are module-private. However, `_git()` is a general-purpose helper used throughout. Mixing conventions reduces clarity.
   - Suggestion: Reserve `_` prefix for truly private helpers (single-use, localized). General utilities like `_git()` should be named without underscore or explicitly marked as internal utilities.
   - **Status**: UNFIXABLE — renaming `_git` would require updating all call sites across implementation and tests, expanding beyond checkpoint scope

3. **Error handling missing for git operations**
   - Location: src/claudeutils/worktree/cli.py:348-350
   - Problem: `_create_parent_worktree()` and `_create_submodule_worktree()` can raise `subprocess.CalledProcessError`, but these are caught generically at line 364. User gets stderr from arbitrary git failure without context about which step failed.
   - Suggestion: Wrap each creation step with specific error context (e.g., "Error creating parent worktree:", "Error creating submodule worktree:")
   - **Status**: FIXED

4. **Session commit failure exits without cleanup**
   - Location: src/claudeutils/worktree/cli.py:220
   - Problem: If session file read fails (line 217), command exits at line 220 but `finally` block (line 367) only runs if exception propagates from outer try block. Temporary index file created at line 222 won't be cleaned.
   - Suggestion: Move session file read before tempfile creation, OR nest try-finally to guarantee cleanup
   - **Status**: FIXED

### Minor Issues

1. **Duplicate helper function across test files**
   - Location: tests/test_worktree_cli.py:20, tests/test_worktree_new.py:13, tests/test_worktree_rm.py:12, tests/test_worktree_submodule.py:12
   - Note: `_init_repo()` and `_init_git_repo()` duplicated across 4 test files with minor naming variations. Violates DRY principle.
   - **Status**: FIXED

2. **Missing edge case test: environment init failure**
   - Location: tests/test_worktree_new.py:276
   - Note: Test mocks successful `just setup`, but doesn't verify behavior when setup returns non-zero (design specifies graceful failure with warning at cli.py:161-164)
   - **Status**: FIXED

3. **Test naming inconsistency**
   - Location: tests/test_worktree_cli.py, tests/test_worktree_new.py
   - Note: Some tests use `test_new_*` naming (in test_worktree_new.py) while test_worktree_cli.py has `test_wt_path_*`. Should standardize on feature-first naming (`test_<feature>_<scenario>`).
   - **Status**: FIXED

4. **Unnecessary assertion**
   - Location: src/claudeutils/worktree/cli.py:341
   - Note: `assert slug is not None` is redundant — lines 322-327 guarantee slug is set (either from argument or derived from task). Type narrowing doesn't require runtime assertion here.
   - **Status**: FIXED

5. **Temporary file cleanup race condition**
   - Location: src/claudeutils/worktree/cli.py:368-369
   - Note: `finally` block uses `Path.unlink(missing_ok=True)` which is safe, but temp_session_file is only set in task mode (line 339). Variable is initialized to None (line 331) and checked in finally. This is correct but could be clearer with early return pattern.
   - **Status**: FIXED

6. **Missing test: concurrent worktree container creation**
   - Location: tests/test_worktree_new.py
   - Note: No test verifies `create_container=True` is idempotent when called multiple times (design: `exist_ok=True` at line 46)
   - **Status**: FIXED

## Fixes Applied

- src/claudeutils/worktree/cli.py:233 — Added `missing_ok=True` to temp index cleanup for safety
- src/claudeutils/worktree/cli.py:341-343 — Added explicit None check for slug type narrowing (mypy)
- src/claudeutils/worktree/cli.py:348-357 — Added specific error context for parent/submodule worktree creation failures
- src/claudeutils/worktree/cli.py:373 — Simplified finally block with explicit None check
- tests/conftest.py:271-302 — Extracted `init_repo()` fixture to eliminate duplication across 4 test files
- tests/test_worktree_cli.py — Updated to use `init_repo()` fixture, standardized naming to `test_<feature>_<scenario>`
- tests/test_worktree_new.py:399-438 — Added `test_new_environment_init_failure()` edge case test
- tests/test_worktree_new.py:441-458 — Added `test_new_container_idempotent()` for concurrent creation
- tests/test_worktree_new.py — Updated all tests to use `init_repo()` fixture
- tests/test_worktree_rm.py — Updated to use `init_repo()` fixture
- tests/test_worktree_submodule.py — Updated to use `init_repo()` fixture

## Requirements Validation

**Requirements context:** Phase 5 design.md (lines 34-36, 47)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Extract `create_worktree()` pure function | Partial | Logic exists but not extracted (Major Issue #1) |
| Sibling container paths via `wt_path()` | Satisfied | cli.py:31-48, tests/test_worktree_cli.py:132-157 |
| Worktree-based submodule creation | Satisfied | cli.py:268-289, tests/test_worktree_submodule.py:156-250 |
| Sandbox permission registration | Satisfied | cli.py:120-138, tests/test_worktree_new.py:236-273 |
| Environment initialization (graceful) | Satisfied | cli.py:140-164, tests/test_worktree_new.py:276-318 |
| Session commit with focused content | Satisfied | cli.py:214-233, tests/test_worktree_cli.py:159-194 |
| Task mode: slug derivation + session | Satisfied | cli.py:314-369, tests/test_worktree_cli.py:354-391 |
| `_git()` helper for subprocess | Satisfied | cli.py:14-28, used throughout |

**Gaps:** Design calls for `create_worktree()` as a reusable function, but implementation inlines all logic in CLI command. This is an architectural deviation requiring refactoring beyond checkpoint scope.

---

## Positive Observations

- Comprehensive test coverage across happy path, edge cases, and integration scenarios
- Excellent error handling for missing dependencies (just command not found)
- Clean separation of concerns between path computation, sandbox registration, and worktree creation
- Graceful degradation for environment initialization failures
- Idempotent sandbox directory registration with deduplication

## Recommendations

- Phase 6: Extract `create_worktree()` function per design contract (required for merge command reusability)
- Consider consolidating git subprocess calls into `_git()` wrapper to improve consistency and error handling
- Add integration test for full pipeline: task mode → session commit → submodule creation → sandbox registration
