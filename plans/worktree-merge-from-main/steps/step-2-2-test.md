# Cycle 2.2

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.2: `remerge_session_md` from-main policy (FR-1)

When `from_main=True`, keep ours entirely in phase 4 remerge (skip structural merge, just git add current working tree version).

**Files:** `src/claudeutils/worktree/remerge.py`

**RED:** Two tests:
1. from_main=True: set up MERGE_HEAD state. Call `remerge_session_md(slug="main", from_main=True)`. Assert: session.md content is the worktree's version, main's tasks not injected.
2. Regression: from_main=False (default): existing behavior unchanged — structural merge via `_merge_session_contents` still runs.

**GREEN:** Add `from_main: bool = False` to `remerge_session_md`. When from_main: `git add agents/session.md` (current working tree version is already the branch's content). Skip `_merge_session_contents` call.

**Dependencies:** Cycle 2.1

**Stop/Error Conditions:**
- RED passes before implementation → remerge may not be called in test fixture; verify MERGE_HEAD state exists
- Regression test fails → from_main=False default not preserving existing structural merge behavior
