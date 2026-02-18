## Phase 2: Submodule conflict pass-through (type: tdd)

**Goal:** Change `_phase2_resolve_submodule` to not abort when submodule merge produces conflicts. Instead: leave agent-core MERGE_HEAD in place, continue to Phase 3. This implements FR-1 and D-6.

**Files:** `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_submodule.py`

**Depends on:** Cycle 1.4 (state machine `submodule_conflicts` routing exists and is tested).

**Common context for all cycles:**
- The change is in `_phase2_resolve_submodule`, line 126: `_git("-C", "agent-core", "merge", "--no-edit", wt_commit)` — this uses the default `check=True` and raises `CalledProcessError` on conflict.
- D-6: Switch `_git(...)` call to use `check=False` (or use `subprocess.run` directly). Handle return code: non-zero = conflict, leave in progress.
- After Phase 2 leaves agent-core in conflict state, `_detect_merge_state` will return `"submodule_conflicts"` on re-run (from Phase 1). The routing handles continuation.
- Re-running Phase 2 when submodule already merged is a no-op (existing `wt_commit == local_commit` check at line 102).
- All test repos: real git repos via `repo_with_submodule` fixture, no mocks. Use `mock_precommit`.

---

## Cycle 2.1: Submodule merge conflict — agent-core MERGE_HEAD preserved, pipeline continues

**Prerequisite:** Read `src/claudeutils/worktree/merge.py:93-135` — understand `_phase2_resolve_submodule` structure: the `wt_commit != local_commit` branch, the `merge-base --is-ancestor` check, and the `_git("-C", "agent-core", "merge", "--no-edit", wt_commit)` call at line 126 that currently raises.

**RED Phase:**

**Test:** `test_submodule_conflict_does_not_abort_pipeline`
**File:** `tests/test_worktree_merge_submodule.py`

**Assertions:**
- When submodule merge produces conflicts, `merge(slug)` does NOT exit with `CalledProcessError` traceback
- Agent-core MERGE_HEAD exists after call (submodule conflict preserved)
- Exit code is 3 (conflicts need resolution — D-1, established in Phase 1 Cycle 1.3)
- Output does not contain "Traceback"

**Expected failure:** `SystemExit(1)` from uncaught `CalledProcessError` — current `_git("-C", "agent-core", "merge", ...)` with `check=True` raises when submodule merge conflicts.

**Why it fails:** `_git()` raises `subprocess.CalledProcessError` on non-zero return. Uncaught at call site — propagates up as unhandled exception through CliRunner → `SystemExit(1)`.

**Verify RED:** `pytest tests/test_worktree_merge_submodule.py::test_submodule_conflict_does_not_abort_pipeline -v`

**Test setup:**
1. Use `repo_with_submodule` fixture, monkeypatch chdir
2. Create branch with a commit in agent-core (different file change than main)
3. On main: make a different commit in agent-core (same file, different content) — creates genuine merge conflict in agent-core
4. Record the wt branch's agent-core commit SHA as `wt_submodule_commit`
5. Invoke `worktree merge slug` via CliRunner
6. Check: subprocess `git -C agent-core rev-parse --verify MERGE_HEAD` returns 0 (MERGE_HEAD exists)
7. Assert exit code == 3, "Traceback" not in output

**Setup detail:** The `repo_with_submodule` fixture creates agent-core as a submodule. To make agent-core commits conflict: on both branch and main, commit different content to the same file in agent-core (e.g., `conflict.txt`). The branch's agent-core commit must be recorded in the parent branch's tree (via `git add agent-core && git commit`).

**GREEN Phase:**

**Implementation:** Change `_phase2_resolve_submodule` to use `check=False` on the submodule merge call and handle the non-zero return code.

**Behavior:**
- Replace `_git("-C", "agent-core", "merge", "--no-edit", wt_commit)` with a call that uses `check=False`
- If return code == 0: proceed as before (stage and commit the submodule pointer)
- If return code != 0: leave agent-core in mid-merge state (MERGE_HEAD preserved), do NOT stage agent-core, do NOT commit, return from `_phase2_resolve_submodule` without error
- The caller (`merge()` via `clean` route) proceeds to `_phase3_merge_parent` which will handle the submodule conflict state
- Note: after submodule conflict, re-running via `submodule_conflicts` route skips `_phase2` and goes directly to `_phase3_merge_parent`

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: At line 126, change `_git("-C", "agent-core", "merge", "--no-edit", wt_commit)` to use `check=False` variant; add returncode check; skip staging/committing on conflict
  Location hint: `_phase2_resolve_submodule`, lines 118-134

**Verify GREEN:** `pytest tests/test_worktree_merge_submodule.py::test_submodule_conflict_does_not_abort_pipeline -v`
**Verify no regression:** `pytest tests/test_worktree_merge_submodule.py -v`

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
