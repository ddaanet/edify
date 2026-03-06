# Cycle 2.1

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.1: `resolve_session_md` from-main policy (FR-1)

When `from_main=True`, keep ours entirely — no additive merge. Checkout --ours, git add.

**Files:** `src/claudeutils/worktree/resolve.py`

**RED:** Set up merge with conflicting session.md (main has full task list, branch has focused session). Call `resolve_session_md(conflicts, slug="main", from_main=True)`. Assert: session.md content matches branch's original session exactly; main's tasks not injected.

**GREEN:** Add `from_main: bool = False` to `resolve_session_md`. When from_main: `git checkout --ours agents/session.md`, `git add agents/session.md`, return filtered conflicts. Skip `_merge_session_contents` entirely.

**Dependencies:** Phase 1 (Cycles 1.1, 1.2)

**Stop/Error Conditions:**
- RED passes before implementation → session.md may not be in conflicts list; verify test fixture creates actual conflict
- Branch session content changes after resolution → checkout --ours not working correctly
