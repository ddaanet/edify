# Cycle 1.2

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.2: Batch `from_main` adaptation of merge.py phase functions

Adapt 4 independent functions in merge.py to branch on `from_main`:

1. `_phase1_validate_clean_trees(slug, from_main)`: skip `wt_path(slug)` check when from_main. Validate current branch is not main: `git symbolic-ref --short HEAD` ≠ "main".
2. `_phase4_merge_commit_and_precommit(slug, from_main)`: skip `_append_lifecycle_delivered` when from_main. Pass `from_main` to `remerge_learnings_md` and `remerge_session_md`.
3. `_format_conflict_report(conflicts, slug, from_main)`: when from_main, hint says `claudeutils _worktree merge --from-main` instead of `claudeutils _worktree merge {slug}`.
4. `_phase3_merge_parent(slug, from_main)`: pass `from_main` to `_auto_resolve_known_conflicts`.

**Files:** `src/claudeutils/worktree/merge.py`

**RED:** 4 tests, one per function:
- `_phase1_validate_clean_trees("main", from_main=True)` on main branch → `SystemExit(2)` with "cannot merge main into itself"; on non-main branch → passes
- `_phase4_merge_commit_and_precommit` with from_main → no lifecycle "delivered" entries appended
- `_format_conflict_report(["some/file"], "main", from_main=True)` → output contains `merge --from-main`
- After `_phase3_merge_parent("main", from_main=True)` merge, commit message reflects direction

**GREEN:** Add `from_main` conditionals to each function. `_auto_resolve_known_conflicts` gains `from_main` parameter (pass-through for now — policies in Phase 2).

**Dependencies:** Cycle 1.1

**Stop/Error Conditions:**
- RED passes before implementation → function may already branch on from_main
- Existing worktree→main tests break → from_main=False default not preserving existing behavior
- "cannot merge main into itself" test passes on wrong branch → verify git symbolic-ref detection

**Checkpoint:** `just precommit` — all existing tests pass, new direction parameter accepted.
