# Cross-tree Operations

Enable worktrees to share data without merging. Currently worktrees are isolated — sharing requires merge ceremony or manual `git show`.

## Requirements

### Functional Requirements

**FR-1: Cross-tree test sentinel (content-hash cache)**
Cache test results by content hash of source files, shareable across worktrees. Currently each worktree runs full test suite even when source hasn't changed.
- Acceptance: Test sentinel in worktree A passes → worktree B with identical source hashes skips tests
- Acceptance: Cache stored in project-local `tmp/` (shared across worktrees via same parent directory)
- Acceptance: Any source file change invalidates the cache (conservative — no partial invalidation)

### Constraints

**C-1: No network dependency**
All cross-tree operations use local git operations only. No remote fetches.

### Out of Scope

- Cross-tree writes (writing to another branch's files) — read-only transport
- Merge conflict resolution (that's worktree-merge-resilience)
