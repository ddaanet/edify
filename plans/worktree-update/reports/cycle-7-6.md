# Cycle 7.6: Phase 2 submodule resolution — merge and commit

**Status:** STOP_CONDITION (quality-check: warnings found)

**Test command:** `pytest tests/test_worktree_merge.py::test_merge_submodule_merge_commit -xvs`

**RED result:** FAIL as expected (submodule merge not performed)

**GREEN result:** PASS (merge and commit logic implemented)

**Regression check:** 774/790 passed, 16 skipped (no regressions)

**Refactoring:**
- Removed unused `noqa: PLR0915` directive from test_merge_submodule_fetch
- Code properly formatted

**Files modified:**
- `src/claudeutils/worktree/merge.py` — Added submodule merge logic (lines 153-161)
- `tests/test_worktree_merge.py` — Added test_merge_submodule_merge_commit, fixed formatting

**Stop condition:** Precommit validation flagged:
1. test_merge_submodule_fetch: 51 statements (exceeds limit of 50) — PLR0915
2. test_worktree_merge.py: 491 lines (exceeds limit of 400)

**Decision made:** Architectural refactoring needed to reduce test complexity and file size. Requires refactor agent (sonnet) to consolidate/restructure tests.

## Implementation Details

Added submodule merge and commit logic to `merge()` function:

```python
_git("-C", "agent-core", "merge", "--no-edit", wt_commit)
_git("add", "agent-core")

result = subprocess.run(
    ["git", "diff", "--cached", "--quiet", "agent-core"],
    check=False,
)
if result.returncode != 0:
    _git("commit", "-m", f"🔀 Merge agent-core from {slug}")
```

This:
1. Performs merge on worktree's submodule commit (only if needed, prior checks prevent unreachable commits)
2. Stages the submodule
3. Checks if staged changes exist
4. Commits if changes present (handles no-op merges gracefully)
