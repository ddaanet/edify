# Cycle 1.5

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.5: `merge()` routes `clean` state through full pipeline

**RED Phase:**

**Test:** `test_merge_clean_state_runs_full_pipeline`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- `merge(slug)` on a clean repo with a diverged branch produces a merge commit: `HEAD` has exactly 2 parents after the call
- Exit code is 0
- Merge commit message matches `f"🔀 Merge {slug}"`
- `_is_branch_merged(slug)` returns True after call

**Expected failure:** `AssertionError` — as of Cycle 1.4, `_detect_merge_state` is implemented but `merge()` still calls `_phase1_validate_clean_trees` → `_phase2_resolve_submodule` → `_phase3_merge_parent` → `_phase4_merge_commit_and_precommit` directly (the old linear chain), without routing through `_detect_merge_state`. Write this test after Cycle 1.4 GREEN but before wiring `clean` routing into `merge()`. The test verifies the `clean` path specifically: if `merge()` is not yet calling `_detect_merge_state` for routing, break the test by temporarily having `_detect_merge_state` return `"merged"` for any input — a 1-line change confirmed to fail this test — then revert after writing.

**Why it fails:** The `clean` routing path must be confirmed to exercise all 4 phases in order. Before Cycle 1.5 GREEN, this is enforced by verifying the test fails when `_detect_merge_state` short-circuits to `"merged"` (which would skip Phase 3, producing no merge commit or a fast-forward, failing the 2-parent check).

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_clean_state_runs_full_pipeline -v` (after applying the 1-line `_detect_merge_state` sabotage)

**STOP condition for RED:** If the test passes without sabotage AND Cycle 1.2 routing was correctly wired, the `clean` assertion is too weak. Verify HEAD has exactly 2 parents, not just that exit code is 0.

**Test setup:**
1. Use `repo_with_submodule` and `mock_precommit` fixtures
2. Create branch with one unique file commit
3. Add a different commit on main (diverge) so merge produces a real merge commit
4. Invoke `worktree merge slug` via CliRunner (repo_with_submodule fixture already handles chdir).
5. Assert exit 0, `len(parents_of_HEAD) == 2`, commit message starts with `"🔀 Merge"`, `_is_branch_merged(slug)` returns True.

**GREEN Phase:**

**Implementation:** Confirm that the `clean` routing path in `merge()` from Cycle 1.2 calls all 4 phases in sequence. Revert the RED-phase sabotage if applied.

**Behavior:**
- `clean` route: `_phase1_validate_clean_trees` → `_phase2_resolve_submodule` → `_phase3_merge_parent` → `_phase4_merge_commit_and_precommit`
- No new changes needed if Cycle 1.2 routing was correctly wired; revert sabotage if used for RED verification

**Changes:** Revert the 1-line sabotage in `_detect_merge_state` (if applied for RED phase). No other changes required.
**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py -v`
**Verify no regression:** `pytest tests/ -k "merge" -v`

---

**Phase 1 STOP conditions:**
- RED fails to fail (test passes before GREEN) → STOP, assert is too weak or test setup is incorrect
- `_detect_merge_state` returns wrong state for any git scenario → STOP, debug detection logic
- Regression in existing merge tests → STOP, state machine routing broke existing path
