# Review: wt-rm-dirty bug fix (baseline c7d91d1)

**Scope**: Changes since baseline c7d91d128a42cae39e1a7530449e0ee5120bcdc1
**Date**: 2026-03-01T00:00:00Z
**Mode**: review + fix

## Summary

The fix moves `_append_lifecycle_delivered` from after the `merge()` function call into `_phase4_merge_commit_and_precommit`, and changes the return type to `list[Path]` so the caller can stage the written files before committing. This resolves the ordering bug where lifecycle.md was written after the merge commit, leaving it unstaged and causing `rm`'s dirty-check to block the session amend.

Two integration tests cover the fix: one end-to-end merge→rm sequence (FR-3) and one verifying lifecycle.md content is in the merge commit tree (FR-2 side effect). Both tests correctly reproduce the original bug scenario.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`test_rm_amends_after_merge_with_lifecycle` does not assert "Merge commit amended"**
   - Location: `tests/test_worktree_rm_after_merge.py:71`
   - Problem: The test asserts `"amended" in result.output.lower()` but the actual rm output message is "Merge commit amended" — the lowercase `.lower()` transform is fine, but the assertion still needs to match the actual string. More importantly: if `rm` emits nothing (silent success) the assertion fails correctly. The real risk is whether "amended" appears anywhere in output for reasons unrelated to the session amend (e.g., a warning message). The assertion is underspecified — it should anchor on the specific phrase.
   - Suggestion: Assert `"Merge commit amended" in result.output` (case-sensitive, matches the actual output string).
   - **Status**: FIXED

2. **`test_lifecycle_delivered_in_merge_commit` has no session.md setup but test_rm test does**
   - Location: `tests/test_worktree_rm_after_merge.py:74-112`
   - Problem: The second test does not add a session.md with a worktree task. This is correct for its scope (only testing lifecycle.md in commit), but it means the test does not cover the full FR-2 acceptance criterion: "session.md change is included in the amended merge commit." The test only covers one half of FR-3's requirement ("both lifecycle.md and session.md changes are in final commit") — the lifecycle.md half. The first test covers the rm-amends path but only weakly asserts "amended" appears.
   - Suggestion: The test split is appropriate; however, test 1 should explicitly verify the final commit contains both lifecycle.md and session.md (use `git show HEAD --name-only` or `git diff HEAD~1..HEAD --name-only`). Currently it only checks `result.output` for "amended".
   - **Status**: FIXED

### Minor Issues

1. **Docstring on `_append_lifecycle_delivered` is functional but exposes return contract in prose**
   - Location: `src/claudeutils/worktree/merge.py:19-22`
   - Note: The docstring says "Returns list of modified lifecycle.md paths (for staging by caller)." This accurately documents the new return type but narrates the caller's responsibility (staging) inside the callee's docstring. The caller's staging is visible at the call site — the docstring should only describe what the function returns, not what the caller must do with it.
   - **Status**: FIXED

2. **`_phase4_merge_commit_and_precommit` docstring is unchanged and doesn't mention lifecycle staging**
   - Location: `src/claudeutils/worktree/merge.py:293-298`
   - Note: The docstring describes the commit/precommit logic but doesn't acknowledge that lifecycle.md is now staged here. Not a bug, but the docstring is now misleading by omission — readers expect `remerge_*` functions to be the only staging operations.
   - **Status**: FIXED

3. **Test file missing `conftest.py` fixture delegation check**
   - Location: `tests/test_worktree_rm_after_merge.py:1-13`
   - Note: The test imports `mock_precommit` and `init_repo` from `tests.fixtures_worktree` directly via function parameter injection (pytest fixtures). This is correct — they are defined as `@pytest.fixture` in `fixtures_worktree.py`. However, these fixtures are NOT registered in `conftest.py` — they rely on pytest's fixture collection from the import in the test file itself. This is a non-standard pattern; if the test moves or the import is removed, the fixtures silently become unavailable. Standard pattern is to put shared fixtures in `conftest.py`.
   - **Status**: DEFERRED — The existing test suite already uses this pattern (fixtures_worktree.py imported directly in other test files). Changing to conftest.py is a codebase-wide refactor outside this bug fix scope.

## Fixes Applied

- `tests/test_worktree_rm_after_merge.py:71` — Changed `assert "amended" in result.output.lower()` to `assert "Merge commit amended" in result.output` for precise match against actual output message.
- `tests/test_worktree_rm_after_merge.py` — Added commit contents check in `test_rm_amends_after_merge_with_lifecycle` to verify both `lifecycle.md` and `agents/session.md` appear in the amended commit's changed files.
- `src/claudeutils/worktree/merge.py:19-22` — Trimmed docstring to remove caller-responsibility narration; kept return value description.
- `src/claudeutils/worktree/merge.py:293-298` — Updated `_phase4_merge_commit_and_precommit` docstring to mention lifecycle staging.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: lifecycle.md changes in merge commit | Satisfied | `_append_lifecycle_delivered` now called before `_git("commit", ...)` in phase 4; return value staged via `_git("add", str(lf))` |
| FR-2: rm session amend succeeds after merge | Satisfied | FR-1 eliminates the lifecycle.md dirty source; `_update_session_and_amend` filter (exclude `session.md`) now sees clean tree |
| FR-3: Integration test for merge→rm sequence | Satisfied | `test_rm_amends_after_merge_with_lifecycle` covers full sequence; post-fix assertion added for both files in final commit |
| C-1: Lifecycle write before precommit | Satisfied | `_append_lifecycle_delivered` runs at top of phase 4 before `just precommit` call |
| C-2: Preserve existing merge test coverage | Satisfied (assumed) | No changes to existing test files; return type change is backward-compatible (callers ignored `None`, now iterate `list[Path]`) |

---

## Positive Observations

- The return type change (`None` → `list[Path]`) is minimal and surgical — it only adds the staging loop at the call site without altering any other call path.
- Phase 4's structure (write → stage → check MERGE_HEAD → commit) correctly ensures the lifecycle files are staged whether or not a MERGE_HEAD exists, covering both the `merged` and `clean` state machines.
- `mock_precommit` fixture correctly intercepts `subprocess.run` by checking `cmd[0] == "just" and cmd[1] == "precommit"` — avoids over-broad mocking while still being portable.
- Tests use `_git_setup` (the cwd-aware helper) correctly for setup operations, and real `subprocess.run` for assertion commands — clear separation between setup and verification.
