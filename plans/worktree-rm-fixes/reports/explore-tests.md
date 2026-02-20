# Test Suite Exploration: Worktree Operations

## Summary

The worktree test suite is comprehensive with 27 dedicated test files covering creation (`new`), removal (`rm`), merging (`merge`), and submodule operations. The test infrastructure includes shared fixtures for repo initialization and worktree setup. Tests specifically target dirty tree checks, merge conflicts, and session file cleanup. **Critical gaps exist:** No tests for the three bugs identified in the task (dirty check on parent instead of target, broken worktree from failed new with exit 255, rm --confirm skipping submodule branch cleanup).

---

## Key Findings

### 1. Test File Locations

All worktree tests reside in `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/`.

#### Core test files by operation:

**Removal (`rm`):**
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_rm.py` — Basic rm functionality, merge commit handling, confirmation/force flags (351 lines)
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_rm_dirty.py` — Dirty tree checks, parent/submodule dirty detection (137 lines)
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_rm_guard.py` — Guard checks for unmerged branches, orphan detection, merge vs. non-merge logic (333 lines)

**Creation (`new`):**
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_new_creation.py` — Basic creation, directory collision detection, branch reuse (129 lines)
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_new_config.py` — Sandbox registration, environment initialization (`just setup`), task option, session handling (221 lines)

**Submodule operations:**
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_submodule.py` — New command with submodule initialization, branch/worktree setup in submodules (161 lines)
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_merge_submodule.py` — Merge with submodule conflict handling
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_merge_submodule_lifecycle.py` — MERGE_HEAD lifecycle after submodule merge failures (50 lines)

**Merge operations:**
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/test_worktree_merge_errors.py` — Git error formatting and propagation (100+ lines)
- 14 additional merge test files covering conflict resolution, session updates, validation, routing, strategies

#### Test fixtures:

- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/fixtures_worktree.py` — Shared fixtures and helpers (364 lines)
- `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/conftest.py` — Pytest configuration, API key clearing, project directory fixtures (loads fixtures_worktree plugin)

---

### 2. Test Fixtures and Setup Infrastructure

#### Fixture Location: `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/fixtures_worktree.py`

**Key shared fixtures:**

- **`init_repo()`** — Function fixture returning a repo initialization function (lines 138-166)
  - Sets up git config (user.email, user.name)
  - Creates initial README.md and commits
  - Used by all repo-based tests

- **`repo_with_submodule()`** — Pytest fixture (lines 170-251)
  - Creates main repo + agent-core submodule
  - Adds session files (agents/session.md, agents/learnings.md)
  - Full end-to-end test repo for merge/rm operations with submodules
  - Used in: test_worktree_clean_tree.py, test_worktree_merge_submodule_lifecycle.py

- **`commit_file()`** — Function fixture (lines 255-268)
  - Returns function to create, stage, commit files
  - Simplifies multi-file setup in tests

- **`setup_repo_with_submodule()`** — Function fixture (lines 272-363)
  - Creates repo with gitlink-based submodule (using git plumbing)
  - Allows tests to control submodule state
  - Used in: test_worktree_submodule.py

- **`mock_precommit()`** — Pytest fixture (lines 110-134)
  - Mocks `just precommit` subprocess calls
  - Prevents requiring justfile in test environments
  - Used in merge tests to avoid precommit validation

**Helper functions (not fixtures, import directly):**

- `_create_worktree(repo_path, slug, init_repo)` — Creates worktree via CLI (lines 16-24)
- `_branch_exists(name)` — Checks if branch exists (lines 27-35)
- `_run_git(repo, *args)` — Runs git commands (lines 38-46)
- `make_repo_with_branch()` — Creates repo with branch, optional divergence/merge (lines 49-90)
- `add_worktree(repo_dir, slug)` — Creates raw git worktree (lines 93-98)
- `last_commit_subject(repo_dir)` — Retrieves last commit message (lines 101-103)

#### Conftest Configuration: `/Users/david/code/claudeutils-wt/worktree-rm-fixes/tests/conftest.py`

- **Plugin loading:** Line 14 — `pytest_plugins = ["tests.fixtures_worktree"]`
  - Loads all fixtures from fixtures_worktree.py automatically
- **API key management:** Lines 18-33 — Clears ANTHROPIC_API_KEY for all non-e2e tests
- **Temp project directory:** Lines 37-60 — Provides isolated project directories with mocked history

---

### 3. Existing Test Coverage for `rm`

#### Core rm functionality (test_worktree_rm.py):

| Test | Lines | Coverage |
|------|-------|----------|
| `test_rm_basic` | 15-33 | Removes worktree directory and deletes branch |
| `test_rm_dirty_warning` | 36-54 | Warns about uncommitted changes in worktree, proceeds with removal |
| `test_rm_branch_only` | 57-81 | Cleans up branch when worktree dir removed externally |
| `test_rm_detects_merge_commit` | 84-120 | Uses parent count to detect merge commits (0=root, 1=normal, 2+=merge) |
| `test_rm_amends_merge_commit_when_session_modified` | 123-195 | Amends session.md into merge commit using `git commit --amend` |
| `test_rm_does_not_amend_on_normal_commit` | 198-240 | Verify amend NOT applied to normal (non-merge) commits |
| `test_rm_output_indicates_amend` | 243-309 | Checks output messages distinguish merge vs. normal commit scenarios |
| `test_rm_refuses_without_confirm` | 312-329 | Exit code 2 without --confirm flag |
| `test_rm_force_bypasses_confirm` | 332-350 | --force flag bypasses confirm check |

#### Dirty tree checks (test_worktree_rm_dirty.py):

| Test | Lines | Coverage |
|------|-------|----------|
| `test_is_parent_dirty` | 15-30 | Function `_is_parent_dirty()` — detects untracked and staged files |
| `test_is_submodule_dirty` | 33-68 | Function `_is_submodule_dirty()` — checks agent-core for modifications |
| `test_rm_blocks_on_dirty_parent` | 71-89 | rm blocks (exit 2) when parent repo has uncommitted changes |
| `test_rm_blocks_on_dirty_submodule` | 92-115 | rm blocks (exit 2) when submodule has uncommitted changes |
| `test_rm_force_bypasses_dirty_check` | 118-136 | --force flag bypasses dirty checks |

**CRITICAL GAP:** These tests check `_is_parent_dirty()` and `_is_submodule_dirty()` in the **parent repo**. No tests verify dirty state of the **target worktree being removed**. Bug #1 (dirty check fails on parent instead of target) is NOT covered.

#### Guard checks for unmerged branches (test_worktree_rm_guard.py):

| Test | Lines | Coverage |
|------|-------|----------|
| `test_is_branch_merged` | 27-46 | `_is_branch_merged()` — checks if branch merged into main |
| `test_classify_branch` | 49-97 | `_classify_branch()` — returns (commit_count, is_focused_session) |
| `test_classify_orphan_branch` | 100-119 | Orphan branches return (0, False) |
| `test_rm_refuses_unmerged_real_history` | 122-152 | Refuses unmerged branches with real history or orphan branches |
| `test_rm_allows_merged_branch` | 155-170 | Allows merged branch removal with -d (safe delete) |
| `test_rm_allows_focused_session_only` | 173-193 | Allows focused-session-only branch with -D (force delete) |
| `test_rm_guard_prevents_destruction` | 196-225 | Verifies guard refusal (exit 2) prevents ALL destructive operations |
| `test_rm_no_destructive_suggestions` | 228-276 | Verifies CLI never suggests `git branch -D` (FR-5) |
| `test_rm_guard_exits_2` | 279-293 | Guard exits 2 when refusing unmerged branch |
| `test_delete_branch_exits_1_on_failure` | 296-314 | `_delete_branch()` raises SystemExit(1) on git failure |
| `test_rm_force_bypasses_guard` | 317-332 | Force flag bypasses guard check |

**Test infrastructure used:**
- `make_repo_with_branch()` with n_commits parameter to create real history
- `add_worktree()` to set up git worktree
- `_branch_exists()` to verify branch state
- `_run_git()` for worktree list verification

---

### 4. Existing Test Coverage for `new`

#### Creation and collision handling (test_worktree_new_creation.py):

| Test | Lines | Coverage |
|------|-------|----------|
| `test_new_collision_detection` | 13-27 | Reuses existing branch without error |
| `test_new_directory_collision` | 30-54 | Detects existing directory collision, exits 1 |
| `test_new_basic_flow` | 57-88 | Creates worktree with new branch in sibling container |
| `test_new_command_sibling_paths` | 91-128 | Multiple worktrees in same container, branch/existing reuse |

#### Configuration and environment setup (test_worktree_new_config.py):

| Test | Lines | Coverage |
|------|-------|----------|
| `test_new_sandbox_registration` | 14-47 | Registers container in .claude/settings.local.json (main + worktree) |
| `test_new_environment_initialization` | 50-87 | Runs `just setup` in worktree when available (mocked) |
| `test_new_task_option` | 90-129 | --task option for session-based worktree creation |
| `test_new_session_handling_branch_reuse` | 132-161 | Warns and ignores --session when branch exists |
| `test_new_environment_init_failure` | 164-197 | Warns when `just setup` fails but continues |
| `test_new_container_idempotent` | 200-220 | Container creation is idempotent |

**Mocking patterns:**
- `subprocess.run` patched to mock `just --version` and `just setup` calls
- Uses CliRunner for command execution

**CRITICAL GAP:** No tests for worktree creation failure scenarios:
- Exit code 255 from `git worktree add` failure
- Empty directory left behind
- Partial state (branch created but directory missing)
- Cleanup after failed `new`

---

### 5. Submodule Test Patterns

#### Test setup patterns (test_worktree_submodule.py):

**How submodules are created in tests:**

1. **Via `setup_repo_with_submodule` fixture** (fixtures_worktree.py:272-363):
   - Uses git plumbing (`git update-index --add --cacheinfo`) to create gitlink
   - Creates .gitmodules file
   - Allows controlled submodule state for testing

2. **Test example (test_new_submodule, lines 13-61):**
   ```python
   setup_repo_with_submodule(repo_path, init_repo)
   runner.invoke(worktree, ["new", "test-feature"])
   # Verify submodule initialized
   assert (worktree_path / "agent-core").exists()
   # Verify submodule is on correct branch
   git -C submodule_path rev-parse --abbrev-ref HEAD → test-feature
   ```

3. **Submodule worktree setup (test_new_worktree_submodule, lines 64-160):**
   - Creates feature-x worktree in main repo
   - Verifies submodule has its own worktree (git worktree list)
   - Verifies submodule is on feature-x branch
   - Tests reuse of existing submodule branches (feature-y)

#### Submodule lifecycle testing (test_worktree_merge_submodule_lifecycle.py:14-49):

**MERGE_HEAD orphaning bug test:**
- Sets up submodule conflict during merge
- Verifies MERGE_HEAD persists after parent merge succeeds (exit 0)
- **Expected behavior:** Exit 3 with orphaned MERGE_HEAD detected (line 38)
  ```python
  assert result.exit_code == 3
  merge_head_check = subprocess.run(
    ["git", "-C", str(agent_core_path), "rev-parse", "--verify", "MERGE_HEAD"]
  )
  assert merge_head_check.returncode == 0  # MERGE_HEAD still exists
  ```

#### Submodule merge conflict test helper (test_worktree_merge_submodule.py):

**`_setup_submodule_conflict()` helper:**
- Creates scenario where parent and submodule both make conflicting commits
- Used by merge tests to verify conflict handling
- Initializes conflict state for testing phase boundaries

---

### 6. Dirty Check Test Patterns

#### Dirty state creation patterns (test_worktree_rm_dirty.py):

**Parent dirty (lines 71-89):**
```python
(repo_path / "dirty.txt").write_text("dirty content")  # Untracked file
runner.invoke(worktree, ["rm", "--confirm", "test-feature"])
assert result.exit_code == 2  # Blocked
```

**Submodule dirty (lines 92-115):**
```python
# Mock returns dirty status for agent-core
monkeypatch.setattr(
    "claudeutils.worktree.cli._is_submodule_dirty",
    lambda: True
)
runner.invoke(worktree, ["rm", "--confirm", "test-feature"])
assert result.exit_code == 2  # Blocked
```

**Function location:** `_is_parent_dirty()` and `_is_submodule_dirty()` defined in src/claudeutils/worktree/utils.py

#### Dirty state verification patterns (test_worktree_clean_tree.py):

Tests use `clean-tree` command to verify dirty detection:
```python
(src_dir / "cli.py").write_text('modified content')
runner.invoke(worktree, ["clean-tree"])
assert result.exit_code == 1  # Reports dirty
```

Session files are exempted:
```python
(agents_dir / "session.md").write_text("# Session\nModified\n")
runner.invoke(worktree, ["clean-tree"])
assert result.exit_code == 0  # Exits clean
```

---

## Test Execution Model

### How tests are structured:

1. **Setup phase:**
   - Use `monkeypatch.chdir(repo_path)` to set working directory
   - Initialize repo with `init_repo(repo_path)`
   - Create worktree/branch via CLI or git commands

2. **Execution phase:**
   - Use CliRunner to invoke worktree commands
   - `result = runner.invoke(worktree, ["rm", "--confirm", slug])`

3. **Verification phase:**
   - Check exit code: `assert result.exit_code == 0`
   - Check output: `assert "removed" in result.output.lower()`
   - Verify filesystem: `assert not worktree_path.exists()`
   - Verify git state: `assert not _branch_exists("slug")`
   - Check git objects: `subprocess.run(["git", "worktree", "list"])`

### Key testing utilities:

- **CliRunner** — Click's test runner for invoking CLI commands in isolation
- **monkeypatch** — pytest fixture for mocking/patching functions
- **tmp_path** — pytest fixture providing isolated temp directories
- **subprocess.run** — Direct git command execution for verification

---

## Critical Test Gaps

### Bug #1: Dirty check on parent instead of target worktree
- **Tests exist for parent dirty:** test_worktree_rm_dirty.py (rm blocks on parent changes)
- **Missing:** No test for worktree-specific dirty state (worktree has uncommitted changes, parent clean)
- **Expected test:** Modify file IN the worktree (not parent), verify rm detects it or uses worktree-specific check
- **Current behavior:** Tests only verify parent repo dirty detection

### Bug #2: Broken worktree from failed `new` (exit 255, empty dir)
- **Tests for new success:** test_worktree_new_creation.py + test_worktree_new_config.py
- **Missing:** No test for git worktree add failure scenarios
  - No test for exit 255 from git
  - No test for partial state (branch created, dir empty)
  - No test for cleanup after failure
- **Expected test:** Mock `git worktree add` to fail, verify error handling and cleanup

### Bug #3: `rm --confirm` skipping submodule branch cleanup
- **Tests for submodule setup:** test_worktree_submodule.py (verifies submodule on correct branch)
- **Tests for merge:** test_worktree_merge_submodule_lifecycle.py (MERGE_HEAD cleanup)
- **Missing:** No test for `rm` with submodule branch cleanup
  - No test verifying submodule branch deleted when worktree removed
  - No test for `rm --confirm` behavior with submodules
  - Current merge tests verify merge behavior, not rm behavior
- **Expected test:** Create worktree with submodule, rm it, verify both main and submodule branches deleted

---

## Code Coverage Summary

**Test count by operation:**
- `rm` operations: 20 tests across 3 files
- `new` operations: 10 tests across 2 files
- Submodule operations: 3 explicit tests + 10+ implicit (merge tests with submodules)
- Clean-tree/validation: 3 tests
- **Total dedicated worktree tests: 27 files, ~50+ distinct test functions**

**Fixture reuse:**
- `repo_with_submodule` — Used in 5+ test files
- `init_repo` — Used in 20+ test files
- `mock_precommit` — Used in all merge test files
- `setup_repo_with_submodule` — Used in submodule-specific tests

**Test patterns confirmed:**
- All rm tests use monkeypatch.chdir + CliRunner
- All new tests use CliRunner + worktree_path verification
- Submodule tests use subprocess.run for git verification
- Dirty state tests mock functions or create real dirty state

---

## Recommendations for New Tests

1. **For Bug #1 (target worktree dirty):**
   - Add test to test_worktree_rm_dirty.py: Modify file in worktree being removed, expect exit 2
   - Use `add_worktree(repo, slug)` then modify files in the worktree directory

2. **For Bug #2 (broken worktree):**
   - Add test to test_worktree_new_creation.py: Mock git worktree add to fail with exit 255
   - Verify directory cleaned up, branch potentially cleaned up, error message clear
   - Test scenarios: exit 255, exit 128, exit 1

3. **For Bug #3 (submodule branch cleanup):**
   - Add test to test_worktree_submodule.py: `test_rm_cleans_submodule_branch`
   - Create worktree via new (submodule gets branch)
   - Verify submodule branch deleted after rm
   - Check both main and submodule branches gone
   - Test with `rm --confirm` and `rm --force`
