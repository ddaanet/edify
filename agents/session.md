# Session: Worktree — Merge artifact validation

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Merge artifact validation** — post-merge orphan detection in `_worktree merge` | sonnet
  - Plan: worktree-merge-resilience | Diagnostic: `plans/worktree-merge-resilience/diagnostic.md`
  - Pattern: in-place edits + tail divergence → git appends modified line as duplicate
  - Also: focused-session section stripping → content leaks into wrong section

## Blockers / Gotchas

- Manual post-merge check required until worktree-merge-resilience automated
**Validator orphan entries not autofixable:**

## Reference Files

- `plans/worktree-merge-resilience/diagnostic.md` — Merge artifact reproduction conditions
