# Cycle 5.2: Worktree-based submodule creation with branch reuse

**Execution Date:** 2026-02-12

## Status: GREEN_VERIFIED

## Phase Results

**RED Phase:**
- Test name: `test_new_worktree_submodule`
- Expected failure: ✓ AssertionError: submodule not created as worktree
- Actual result: Test failed as expected (submodule not in worktree list)

**GREEN Phase:**
- Implementation location: `src/claudeutils/worktree/cli.py` lines 277-305
- Changes made:
  - Replaced `submodule update --init --reference` with `git -C agent-core worktree add`
  - Added submodule branch detection using `rev-parse --verify`
  - Conditional worktree creation: reuse existing branch (no `-b`) or create new (`-b` flag)
  - Removed old `checkout -B` step (no longer needed with worktree)
- Test result: ✓ PASS

**Regression Check:**
- Previous cycle test `test_new_command_sibling_paths`: ✓ PASS
- Full test suite: ✓ 768/769 passed, 1 xfail

## Refactoring

**Complexity warnings:** None

**Code quality:**
- All lint checks: ✓ PASS
- Precommit validation: ✓ PASS
- Line limits: Moved submodule tests to new `test_worktree_submodule.py` (301 → 301 lines)
- Test file split:
  - `test_worktree_new.py`: 301 lines (was 462)
  - `test_worktree_submodule.py`: 256 lines (new file)

**Files modified:**
1. `src/claudeutils/worktree/cli.py` — Replaced submodule initialization logic
2. `tests/test_worktree_new.py` — Removed `test_new_submodule` and `test_new_worktree_submodule`
3. `tests/test_worktree_submodule.py` — New file with submodule-specific tests

## Key Implementation Details

The submodule initialization now uses git worktree for shared object store:

```python
# Check if submodule branch already exists
try:
    _git("-C", str(agent_core_local), "rev-parse", "--verify", slug)
    submodule_branch_exists = True
except subprocess.CalledProcessError:
    submodule_branch_exists = False

# Create submodule worktree with appropriate branch handling
if submodule_branch_exists:
    _git("-C", str(agent_core_local), "worktree", "add", str(submodule_path), slug)
else:
    _git("-C", str(agent_core_local), "worktree", "add", str(submodule_path), "-b", slug)
```

This approach:
- Shares the object store inherently (no `--reference` needed)
- Handles both fresh and existing branch creation
- Creates worktree entries visible via `git worktree list`
- Avoids detached HEAD state

## Test Coverage

All assertions from cycle spec verified:
- ✓ Submodule worktree created at correct path inside parent
- ✓ Submodule on correct branch matching slug
- ✓ No `--reference` flag present in code
- ✓ Existing branch detection prevents recreation
- ✓ New branch created with `-b` flag when needed
