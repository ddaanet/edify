# Cycle 2.2

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.2: Resume after manual submodule resolution — Phase 2 skipped, pipeline proceeds

**RED Phase:**

**Test:** `test_merge_resume_after_submodule_resolution`
**File:** `tests/test_worktree_merge_submodule.py`

**Assertions:**
- After manually resolving agent-core conflict and committing, re-running `merge(slug)` succeeds
- Exit code is 0 (parent merge completes)
- `git log --format=%s` shows exactly 2 commits since test start: the manual submodule resolution commit message and the final parent merge commit (🔀 Merge slug)
- `git -C agent-core merge-base --is-ancestor <wt_commit> HEAD` returns 0 (wt_commit is now ancestor of agent-core HEAD after manual resolution)

**Expected failure:** Test does not exist yet — `pytest` reports `ERRORS: test_merge_resume_after_submodule_resolution not found`.

**Why it fails:** Test is new. Once the test exists, Cycle 2.2 GREEN may pass immediately because the skip logic (`merge-base --is-ancestor` at lines 104-116) already handles the already-resolved case. This cycle is a regression guard: it verifies the pre-existing skip logic survives the Cycle 2.1 code change.

**Verify RED:** `pytest tests/test_worktree_merge_submodule.py::test_merge_resume_after_submodule_resolution -v`

**Test setup:**
1. Use `repo_with_submodule` fixture with submodule conflict scenario (same as Cycle 2.1 setup)
2. Run first `merge(slug)` → exit 3 (submodule conflict, from Cycle 2.1 GREEN)
3. Manually resolve: `git -C agent-core checkout --theirs conflict.txt && git -C agent-core add conflict.txt && git -C agent-core commit -m "Resolve submodule conflict"`
4. Stage the new agent-core pointer: `git add agent-core`
5. Re-run `worktree merge slug` via CliRunner (second invocation)
6. Assert exit 0
7. Check git log: final commit is parent merge commit, submodule pointer updated

**GREEN Phase:**

**Implementation:** No new code required — Phase 2 skip logic at lines 100-103 (`wt_commit == local_commit`) and the `merge-base --is-ancestor` check at lines 104-116 handle the already-resolved case. The `clean` state routing from Phase 1 correctly calls Phase 2, which then no-ops.

**Behavior:**
- On re-run: `_detect_merge_state` returns `"clean"` (no MERGE_HEAD after manual commit + staging)
- `clean` route calls `_phase2_resolve_submodule`
- `wt_commit` is now an ancestor of agent-core HEAD → `merge-base --is-ancestor` returns 0 → skip
- Proceeds to Phase 3 and Phase 4
- Parent merge completes

**Changes:** None (verification cycle — existing skip logic is correct).

**Verify GREEN:** `pytest tests/test_worktree_merge_submodule.py -v`
**Verify no regression:** `pytest tests/ -k "merge" -v`

---

**Phase 2 STOP conditions:**
- Submodule merge conflict causes traceback after GREEN → STOP, `check=False` not applied correctly
- Phase 2 skip logic fails after manual resolution → STOP, `merge-base --is-ancestor` logic broken
- Regression in `test_merge_submodule_merge_commit` or `test_merge_submodule_fetch` → STOP, Phase 2 success path broken
