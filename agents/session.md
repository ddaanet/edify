# Session: Worktree — Merge artifact validation

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Merge artifact validation** — post-merge orphan detection in `_worktree merge` | sonnet
  - Plan: worktree-merge-resilience | Diagnostic: `plans/worktree-merge-resilience/diagnostic.md`
  - New instance found: `6086650e` merge produced 6 orphaned bullets in learnings.md (headingless, under wrong entry). Brief: `plans/worktree-merge-resilience/brief.md`

## Blockers / Gotchas

- Manual post-merge check required until worktree-merge-resilience automated
**Validator orphan entries not autofixable:**

## Reference Files

- `plans/worktree-merge-resilience/diagnostic.md` — Merge artifact reproduction conditions
- `plans/worktree-merge-resilience/brief.md` — Orphaned bullets instance from merge `6086650e`
