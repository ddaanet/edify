# Brief: WT merge should not block on dirty worktree

## Bug

`claudeutils _worktree merge <slug>` exits with error when the **worktree** (not the main repo) has uncommitted changes:

```
Clean tree required for merge (worktree: uncommitted changes would be lost)
```

This blocks merging the last committed revision from the worktree branch.

## Expected Behavior

The merge target is a branch ref, not the working tree. Uncommitted changes in the worktree are irrelevant — the merge operates on committed history. The clean-tree check should only apply to the **main repo** (merge destination), not the worktree (merge source).

## Context

- User had a worktree with in-progress uncommitted work but wanted to merge the committed state
- The worktree's branch had valid committed work ready for merge
- The dirty-tree guard prevented a legitimate operation

## Fix Target

`src/claudeutils/worktree/merge.py` — the clean-tree precondition check. Remove or relax the worktree-side dirty check. Keep the main-repo-side clean check (merge destination must be clean).

## Scope

Small fix — single precondition guard in merge.py. Needs test coverage for the case: dirty worktree + clean main → merge succeeds on committed branch state.
