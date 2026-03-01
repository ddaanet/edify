# wt-rm-dirty: Fix dirty-state warning after merge+rm

## Requirements

### Functional Requirements

**FR-1: lifecycle.md changes included in merge commit**
`_append_lifecycle_delivered()` must run before the merge commit in phase 4, not after it. The "delivered" lifecycle entry should be part of the merge commit, not an unstaged post-commit artifact.

Acceptance criteria:
- After `_worktree merge <slug>`, `git status --porcelain` shows no lifecycle.md changes
- lifecycle.md "delivered" entry is present in the merge commit tree
- Existing test `test_merge_appends_lifecycle_delivered` still passes

**FR-2: rm session amend succeeds after merge**
`_worktree rm <slug>` immediately after `_worktree merge <slug>` should amend the merge commit with the session.md change (worktree task removal), not emit "Warning: skipping session amend (parent repo dirty)".

Acceptance criteria:
- `_worktree rm` after merge exits 0 with "Merge commit amended" in output
- No "parent repo dirty" warning emitted
- session.md change is included in the amended merge commit

**FR-3: Test coverage for merge-then-rm sequence**
Add integration test covering the full `merge` → `rm` sequence that reproduces the original bug: merge creates lifecycle.md change, rm attempts session amend.

Acceptance criteria:
- Test creates a plan with "reviewed" lifecycle status
- Test runs merge, then rm
- Test asserts rm amends the merge commit (no dirty-state warning)
- Test verifies both lifecycle.md and session.md changes are in final commit

### Constraints

**C-1: Lifecycle write must precede precommit validation**
Moving `_append_lifecycle_delivered` into phase 4 means it runs before `just precommit`. The lifecycle write must be staged so precommit sees the final tree state.

**C-2: Preserve existing merge test coverage**
Existing tests in `test_worktree_merge_lifecycle.py` and `test_worktree_merge_submodule_lifecycle.py` must continue to pass. The fix changes ordering, not behavior.

### Out of Scope

- `_update_session_and_amend` dirty-check logic redesign — the current filter (exclude only `session.md`) is correct given FR-1 eliminates the lifecycle.md dirty source
- Submodule lifecycle handling — separate concern (see "When Removing Worktrees With Submodules" decision)
- rm `--force` path — force bypasses all safety checks including amend

### References

- `plans/wt-rm-dirty/brief.md` (on main) — observed behavior and initial code path analysis
- `src/claudeutils/worktree/merge.py:380` — `_append_lifecycle_delivered` call site (after phase 4)
- `src/claudeutils/worktree/merge.py:287-321` — phase 4 commit logic
- `src/claudeutils/worktree/cli.py:296-317` — `_update_session_and_amend` dirty check
