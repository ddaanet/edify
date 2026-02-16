# Deliverable Review: worktree-merge-data-loss Tests

**Date:** 2026-02-16
**Scope:** Test files for Track 1 (removal guard) and Track 2 (merge correctness)
**Design reference:** `plans/worktree-merge-data-loss/design.md`
**Convention reference:** `agents/decisions/testing.md`

## Summary

Test coverage is strong across both tracks. All design-specified scenarios are covered (some indirectly). Tests use real git repos with `tmp_path` and `init_repo` fixtures as required by project conventions. No mocked subprocess for git operations (except `mock_precommit` for justfile dependency, which is the documented exception). Two findings on test quality, two on code style.

## Findings

### Major

**M-1: `test_validate_merge_*` uses manual sys.stderr capture instead of capsys/capfd**
- File: `tests/test_worktree_merge_correctness.py:178-186, 203-211, 244-252`
- Axis: Specificity, Independence
- Three tests (`test_validate_merge_valid`, `test_validate_merge_invalid`, `test_validate_merge_single_parent_warning`) manually swap `sys.stderr` with a `StringIO` buffer and restore in a `finally` block. This pattern is fragile: if `_validate_merge_result` spawns a subprocess that writes to fd 2 (not Python's `sys.stderr`), the capture misses it. It also risks test pollution if the `finally` block fails to restore.
- The production code (`merge.py:273, 288`) uses `sys.stderr.write()`, so the StringIO capture does work in practice. However, `pytest.capsys` or `capfd` are the idiomatic, safe alternatives. `capfd` captures at the file descriptor level and handles both Python `sys.stderr.write` and subprocess stderr.
- Recommendation: Replace manual stderr capture with `capfd` fixture. Example:
  ```python
  def test_validate_merge_invalid(tmp_path, monkeypatch, init_repo, capfd):
      ...
      try:
          _validate_merge_result("test-branch")
      except SystemExit as e:
          exit_code = e.code
      captured = capfd.readouterr()
      assert "Error: branch test-branch not fully merged" in captured.err
  ```

### Minor

**m-1: Section banner comments in fixtures_worktree.py**
- File: `tests/fixtures_worktree.py:10, 81`
- Axis: Excess (project conventions)
- Two section banners (`# -- Shared helpers ...` and `# -- Fixtures ...`) violate the deslop convention: "No section banners -- let structure communicate grouping." The separation between helpers and fixtures is already clear from the `@pytest.fixture` decorator presence/absence.

**m-2: Trivial docstring on `_is_branch_merged`**
- File: `src/claudeutils/worktree/utils.py:42-52`
- Axis: Excess (deslop)
- This is a source file issue, not a test file issue, so flagging as informational only. The docstring on `_is_branch_merged` restates the function name and signature (`"Check if a branch is merged..."`, `Args: slug: Branch name to check`, `Returns: True if merged`). The function name communicates this. The one non-obvious detail (uses `merge-base --is-ancestor`) is worth keeping as a one-liner.
- **Note:** Review scope is test files. This is informational -- not actionable within this review.

**m-3: `test_rm_no_destructive_suggestions` calls `make_repo_with_branch` with `init_repo` on already-initialized repo**
- File: `tests/test_worktree_rm_guard.py:245-276`
- Axis: Functional correctness
- After initializing the repo at line 240 (`init_repo(repo)`), the test calls `make_repo_with_branch(repo, init_repo, ...)` three times. `make_repo_with_branch` checks `if not (repo_dir / ".git").exists()` and skips re-init, so this is safe. However, passing `init_repo` when it won't be used is misleading. The helper requires it as a parameter, so this is a design constraint of the fixture, not a test bug. Informational only.

## Design Coverage Matrix

### Track 1: Removal Guard

| Design scenario | Test | Verdict |
|---|---|---|
| Merged branch removal succeeds (exit 0) | `test_rm_allows_merged_branch` | Covered. Asserts exit 0, branch deleted, message "Removed merged-branch". |
| Focused-session-only unmerged removal succeeds (exit 0, reports type) | `test_rm_allows_focused_session_only` | Covered. Asserts exit 0, branch deleted, message includes "focused session only". |
| Real-history unmerged removal refused (exit 1, stderr message) | `test_rm_refuses_unmerged_real_history` (Scenario A) | Covered. Asserts exit 1, message includes commit count. |
| Worktree directory NOT removed when guard refuses | `test_rm_guard_prevents_destruction` | Covered. Asserts worktree dir exists, branch exists, session.md task intact, worktree registration intact. |
| No `git branch -D` in output for any case | `test_rm_no_destructive_suggestions` | Covered. Three scenarios (merged, focused, unmerged) all assert `git branch -D` not in output. |
| Orphan branch: refused with specific message (exit 1) | `test_rm_refuses_unmerged_real_history` (Scenario B) + `test_classify_orphan_branch` | Covered. Asserts "is orphaned (no common ancestor)" message and exit 1. |
| Branch-not-found: directory cleanup proceeds | `test_rm_post_removal_cleanup_idempotent` | Indirectly covered. Second `rm` invocation has no branch (deleted on first pass). Guard returns `(False, None)`, cleanup proceeds without error. |

### Track 2: Merge Correctness

| Design scenario | Test | Verdict |
|---|---|---|
| Parent repo file preservation | `test_merge_preserves_parent_repo_files` | Covered. Creates worktree with parent-only changes, merges, asserts file exists post-merge. |
| Two-parent merge commit structure | `test_merge_preserves_parent_repo_files` (line 300) | Covered. Asserts `len(parents.split()) == 2`. |
| Branch ancestry: slug is ancestor of HEAD | `test_merge_preserves_parent_repo_files` (line 302-308) + `test_validate_merge_valid` | Covered. Both `merge-base --is-ancestor` check and `_validate_merge_result` tested. |
| MERGE_HEAD checkpoint: absent MERGE_HEAD with unmerged branch -> exit 2 | `test_phase4_refuses_single_parent_when_unmerged` | Covered. Merges `--no-commit`, deletes MERGE_HEAD, calls phase4, asserts exit 2 and no new commit. |
| Already-merged idempotency | `test_phase4_allows_already_merged` | Covered. Branch already merged, stages additional changes, phase4 succeeds with new commit. |
| No MERGE_HEAD + no staged + branch not merged -> exit 2 | `test_phase4_no_merge_head_unmerged_exits` | Covered. Unmerged branch, no MERGE_HEAD, no staged changes, asserts exit 2. |
| No MERGE_HEAD + no staged + branch merged -> skip | `test_phase4_no_merge_head_merged_skips` | Covered. Already merged, no MERGE_HEAD, no staged, exit 0, no new commit. |

### Additional tests beyond design spec

| Test | Justification |
|---|---|
| `test_is_branch_merged` | Unit test for shared helper (D-7). Valid: helper is used by both tracks. |
| `test_classify_branch` | Unit test for classification helper. Valid: covers 4 branch types (focused, real-history, multi-commit, wrong-format marker). |
| `test_classify_orphan_branch` | Unit test for orphan path. Valid: design specifies orphan behavior. |
| `test_validate_merge_invalid` | Unit test for validation failure path. Valid: defense-in-depth check (D-5). |
| `test_validate_merge_single_parent_warning` | Diagnostic warning test. Valid: design specifies parent count < 2 warning. |

## Convention Compliance

| Convention | Status |
|---|---|
| Real git repos (tmp_path), no mocked subprocess | Pass. All tests use `init_repo` or `repo_with_submodule` fixtures with real git. `mock_precommit` is the documented exception (justfile dependency). |
| Behavioral assertions (not structural) | Pass. Tests assert on exit codes, file existence, message content, commit structure -- not on mock call counts or internal state. |
| Test isolation / independence | Pass. Each test creates its own repo via `tmp_path`. No shared mutable state between tests. |
| No vacuous assertions | Pass. No `assert True`, no `assert isinstance(x, list)` on potentially-empty collections. All assertions verify specific behavioral outcomes. |

## Positive Observations

- `test_rm_guard_prevents_destruction` is thorough: checks worktree directory, branch, session.md task entry, and worktree registration all survive guard refusal
- `test_phase4_refuses_single_parent_when_unmerged` correctly simulates the exact incident scenario (merge --no-commit then MERGE_HEAD loss) and verifies no commit is created
- `make_repo_with_branch` fixture handles diverse branch setups (files, empty commits, diverge, merge, n_commits) cleanly with keyword arguments
- Tests in `test_worktree_commands.py` (lines 363-400) were correctly updated to expect the new guard behavior (exit 1 for unmerged branches) while preserving FR-5 assertion
