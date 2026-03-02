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
