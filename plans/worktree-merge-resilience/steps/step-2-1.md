# Cycle 2.1

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.1: Submodule merge conflict — agent-core MERGE_HEAD preserved, pipeline continues

**Prerequisite:** Read `src/claudeutils/worktree/merge.py:93-135` — understand `_phase2_resolve_submodule` structure: the `wt_commit != local_commit` branch, the `merge-base --is-ancestor` check, and the `_git("-C", "agent-core", "merge", "--no-edit", wt_commit)` call at line 126 that currently raises.

**RED Phase:**

**Test:** `test_submodule_conflict_does_not_abort_pipeline`
**File:** `tests/test_worktree_merge_submodule.py`

**Assertions:**
- When submodule merge produces conflicts, `merge(slug)` does NOT exit with `CalledProcessError` traceback
- Agent-core MERGE_HEAD exists after call (submodule conflict preserved)
- Exit code is 0 or 3 (not 1) — Phase 2 no longer raises; parent merge auto-resolves the submodule pointer (Phase 3 `checkout --ours agent-core`), so exit 0 is the most likely outcome for a submodule-only conflict
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
