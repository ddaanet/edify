## 2026-03-02: rm should remove completed task entries

### Problem

`_worktree rm` after merge leaves orphaned `[ ]` task entries in Worktree Tasks. `remove_slug_marker()` strips the `→ slug` marker but doesn't remove the entry. Manual cleanup during handoff required.

Caused by task-classification (D-4) which replaced `remove_worktree_task()` with `remove_slug_marker()` — "no move semantics" eliminated both section moves AND task removal. The removal was collateral damage.

### Design Decision

**Completion signal:** Check branch session.md for `[x]` status on the task (`git show <branch>:agents/session.md`). If completed in branch, remove entry from main's session.md. If not `[x]`, strip marker only (cleanup/abandoned case).

**Not merge state.** `_is_merge_of(slug)` doesn't distinguish "work complete" from "sync merge" or "partial progress merge." The branch's own task status is the authoritative signal.

### Scope

- `_update_session_and_amend()` in `cli.py`: after `remove_slug_marker`, check branch session.md for task completion, remove entry if `[x]`
- Needs `extract_task_blocks` or similar to read branch session.md and find task status
- Test: merge→rm sequence with `[x]` task in branch → entry removed; merge→rm with `[ ]` task → marker stripped, entry preserved

### Related

- wt-rm-dirty plan (delivered): fixed lifecycle.md dirty-state blocking amend
- task-classification RCA: design conflated move semantics with post-merge hygiene, also removed `_update_session_and_amend` (restored in wt-rm-dirty fix)
- Design-corrector finding: when design proposes removing functions, corrector should verify all purposes are addressed (purpose audit)

## 2026-03-06: Stale markers block validator, compound failure

### Evidence

During commit on discuss branch, `just precommit` failed because session-validator flagged 3 stale worktree markers (`session-scraping`, `explore-anthropic-plugins`, `wt-ls-session-ordering`) as "worktree marker not found" errors. These worktrees were previously removed via `_worktree rm` but markers persisted — the known `remove_slug_marker` gap.

### Compound Failure

Two systems interact: (1) `_worktree rm` doesn't clean markers (this task's scope), (2) session-validator treats stale markers as blocking errors (exit code 1, not warning). The validator is correct — a marker pointing to a nonexistent worktree IS invalid state. But the root cause is rm not cleaning up, not the validator being too strict.

### Implication for Design

The `[x]` branch-check approach in this brief's design decision should also handle the case where `_worktree rm` runs after worktree removal (no branch to check). The marker itself should be stripped unconditionally by rm — the `[x]` check governs whether the entire task entry is removed, not whether the marker is stripped.
