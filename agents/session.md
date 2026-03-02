# Session: Worktree — Execute flag lint

**Status:** Focused worktree for parallel execution.

## In-tree Tasks

- [ ] **Execute flag lint** — precommit lint gate for `/inline ... execute` in session.md | haiku | 3.0
  - Scan session.md pending tasks for `/inline plans/.* execute` pattern
  - Flag as error: execute entry point in session.md bypasses Phase 2 recall (D+B anchor)
