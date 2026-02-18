# Cycle 3.1

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.1: Source conflict → MERGE_HEAD preserved, no abort, exit 3 (FR-2, NFR-2)

**Prerequisite:** Read `src/claudeutils/worktree/merge.py:137-175` — understand `_phase3_merge_parent` in full: the `git merge --no-commit --no-ff` call, the MERGE_HEAD check, the auto-resolution of agent-core/session/learnings, and the abort block at lines 170-175.

**RED Phase:**

**Test:** Update `test_merge_conflict_surfaces_git_error` in `tests/test_worktree_merge_errors.py`

Update assertions to:
- `result.exit_code == 3` (was `!= 0`)
- `subprocess.run(["git", "rev-parse", "MERGE_HEAD"], ...)` returns 0 after merge call (MERGE_HEAD still present)
- `"aborted"` NOT in `result.output` (old message removed)
- `"conflict"` or conflicted filename in `result.output` (some conflict indication)
- `"Traceback"` not in `result.output`

**Expected failure:** After updating the test: current code aborts (exit 1, MERGE_HEAD gone, "Merge aborted" in output) → test fails because:
- exit_code is 1 not 3
- MERGE_HEAD is absent (--abort removed it)
- "aborted" IS in output

**Why it fails:** Lines 170-175 abort the merge and exit 1; state is destroyed.

**Verify RED:** `pytest tests/test_worktree_merge_errors.py::test_merge_conflict_surfaces_git_error -v`

**GREEN Phase:**

**Implementation:** Remove abort block from `_phase3_merge_parent`. Replace with conflict listing + exit 3.

**Behavior:**
- In the `if conflicts:` branch (lines 170-175): remove `_git("merge", "--abort")`, `_git("clean", "-fd")`, `click.echo(f"Merge aborted: ...")`
- Replace with: list each conflict file via stdout, `raise SystemExit(3)` (no abort, no clean)
- MERGE_HEAD remains intact; staged auto-resolutions (session.md, learnings.md, agent-core) remain staged
- Note: `_format_conflict_report` (Phase 4) will replace the simple listing; for now, a basic `click.echo` of conflict file names suffices

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Remove lines 170-175; add conflict listing + `raise SystemExit(3)` in the `if conflicts:` branch
  Location hint: `_phase3_merge_parent`, lines 170-175

**Verify GREEN:** `pytest tests/test_worktree_merge_errors.py::test_merge_conflict_surfaces_git_error -v`

**CHECKPOINT after Cycle 3.1 — NFR-2 invariant:**
```
grep -n "merge.*--abort\|clean.*-fd" src/claudeutils/worktree/merge.py
```
Expected: no matches. If any `--abort` or `clean -fd` remain in merge.py, STOP and remove them (D-7).

---
