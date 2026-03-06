# Cycle 2.3

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.3: Delete/modify conflict auto-resolution (FR-3)

When `from_main=True`, auto-resolve delete/modify conflicts by accepting theirs (main's deletion). Detect via `git status --porcelain`: DU = deleted by theirs, UD = deleted by us.

**Files:** `src/claudeutils/worktree/merge.py`

**RED:** Two tests:
1. from_main with DU conflict (main deleted file, branch modified it): call `_auto_resolve_known_conflicts` with from_main=True. Assert: file resolved (accepted deletion), removed from conflicts list.
2. Regression: same DU conflict without from_main → remains in conflicts list (not auto-resolved).

**GREEN:** In `_auto_resolve_known_conflicts(conflicts, slug, from_main)`: when from_main, detect DU conflicts via `git status --porcelain`, resolve each by `git rm <file>` + `git add <file>`, remove from conflicts list. Report resolved files via `click.echo`.

**Dependencies:** Phase 1 (Cycles 1.1, 1.2)

**Stop/Error Conditions:**
- RED passes before implementation → DU conflict may not be in test fixture; verify delete/modify scenario creates proper conflict markers
- `git status --porcelain` shows unexpected markers → verify merge state is active (MERGE_HEAD exists)
- Regression test (worktree→main) changes behavior → from_main guard not gating correctly
