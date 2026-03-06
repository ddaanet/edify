# Cycle 1.1

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.1: `merge()` function signature

Add `from_main: bool = False` parameter to `merge()` and thread to all phase functions.

**Files:** `src/claudeutils/worktree/merge.py`

**RED:** Test that `merge("main", from_main=True)` is accepted on an already-merged state (main is ancestor of HEAD). Create a real git repo with a branch, merge the branch, then call `merge("main", from_main=True)`. Assert: no error (exit code 0), function returns normally.

**GREEN:** Add `from_main` parameter to `merge()` signature. Thread to `_phase1_validate_clean_trees`, `_phase2_resolve_submodule`, `_phase3_merge_parent`, `_phase4_merge_commit_and_precommit`. Each phase function adds the parameter but does not yet branch on it (pass-through). Existing behavior unchanged.

**Dependencies:** None (foundation cycle)

**Stop/Error Conditions:**
- RED passes without implementation → parameter may already exist, check merge.py
- Existing tests break after GREEN → parameter threading changed a signature incorrectly
