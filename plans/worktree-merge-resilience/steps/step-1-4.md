# Cycle 1.4

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.4: `merge()` routes `submodule_conflicts` state to Phase 3

**RED Phase:**

**Test:** `test_merge_continues_to_phase3_when_submodule_conflicts`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- When agent-core has MERGE_HEAD (submodule mid-merge), calling `merge(slug)` does not exit with "Clean tree required"
- Agent-core MERGE_HEAD is present (test verifies the starting condition)
- `_detect_merge_state` returns `"submodule_conflicts"` when called directly with agent-core in mid-merge state (test this explicitly before the CliRunner call)
- After CliRunner call: exit code is 0 or 3 (not 1), confirming state routing bypassed the clean-tree check

**Expected failure:** `SystemExit(1)` with "Clean tree required" — current Phase 1 detects agent-core is dirty (staged files from mid-merge); additionally `_detect_merge_state` does not yet return `"submodule_conflicts"` (not implemented until this cycle's GREEN)

**Why it fails:** `_detect_merge_state` (as of Cycle 1.2) does not check agent-core MERGE_HEAD, so state is misclassified as `"clean"` and the full pipeline runs, hitting the clean-tree check.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_continues_to_phase3_when_submodule_conflicts -v`

**Test setup:**
1. Use `repo_with_submodule` fixture (chdir already handled by fixture)
2. Create branch on parent repo (no changes — just branch pointer)
3. Manually put agent-core in mid-merge state: create a conflicting commit on agent-core, then `git -C agent-core merge --no-commit --no-ff <commit>` leaving it mid-merge with no conflicts (so parent Phase 3 can proceed)
4. Invoke `worktree merge slug` via CliRunner.
5. Assert exit code is NOT 1 from clean-tree check (accept 0 or 3 as valid outcomes)

**GREEN Phase:**

**Implementation:** Add submodule MERGE_HEAD check to `_detect_merge_state`, inserting it between the `merged` check and the parent MERGE_HEAD check (per D-5 detection order).

**Behavior:**
- After `_is_branch_merged` check (returns `"merged"` if True):
- Add: run `git -C agent-core rev-parse --verify MERGE_HEAD` (exit 0 = agent-core mid-merge) — return `"submodule_conflicts"` if found, before checking parent MERGE_HEAD
- Rest of function unchanged (parent MERGE_HEAD → `parent_resolved`/`parent_conflicts`, else `"clean"`)

This makes the full detection order match D-5: merged → submodule_conflicts → parent_resolved/parent_conflicts → clean.

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Insert `git -C agent-core rev-parse --verify MERGE_HEAD` check into `_detect_merge_state`, after `_is_branch_merged` and before the parent MERGE_HEAD check
  Location hint: `_detect_merge_state` body, between `merged` return and parent MERGE_HEAD check

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_continues_to_phase3_when_submodule_conflicts -v`
**Verify no regression:** `pytest tests/ -k "merge" -x -v`

---
