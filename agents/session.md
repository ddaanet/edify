# Session: Worktree — Fix wt merge dirty-tree guard

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Fix wt merge dirty-tree guard** — Remove worktree-side clean-tree check from merge | sonnet
  - Plan: wt-merge-dirty-tree | Bug: merge blocks on dirty worktree even though it merges branch ref not working tree
  - Fix target: `src/claudeutils/worktree/merge.py`
