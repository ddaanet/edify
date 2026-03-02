# Session: Worktree — Session.md validator

**Status:** Focused worktree for parallel execution.

## In-tree Tasks

- [ ] **Session.md validator** — Scripted precommit check | sonnet | 2.4
  - Plan: session-validator
  - Includes plan-archive coverage check (deleted plans must have archive entry)
- [ ] **Execute flag lint** — precommit lint gate for `/inline ... execute` in session.md | haiku | 3.0
  - Scan session.md pending tasks for `/inline plans/.* execute` pattern
  - Flag as error: execute entry point in session.md bypasses Phase 2 recall (D+B anchor)