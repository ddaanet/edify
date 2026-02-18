# Cycle 4.3

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.3: Rich mode header + task formatting

**Prerequisite:** Verify `src/claudeutils/planstate/aggregation.py` exists with `aggregate_trees()` function (Phase 1-3 dependency). If missing, STOP — Phase 4 requires completed planstate module.

**RED Phase:**

**Test:** `test_rich_mode_header_and_task`
**Assertions:**
- Header format:
  - For worktree with slug="test-wt", branch="feature", is_dirty=True, commits_since_handoff=3:
    Output contains: `test-wt (feature)  ●  3 commits since handoff`
  - For main tree with is_dirty=False, commits_since_handoff=0:
    Output contains: `main (main)  ○  clean`
  - Dirty indicator: `●` when is_dirty=True, `○` when is_dirty=False
- Task line:
  - For tree with task_summary="Implement foo feature":
    Output contains exactly: `  Task: Implement foo feature` (2-space indent)
  - For tree with task_summary=None:
    Output does NOT contain any line starting with "  Task:"
  - Task line appears directly after header line for same tree

**Expected failure:** Rich output not formatted (AttributeError accessing TreeStatus fields)

**Why it fails:** Rich output formatting not implemented

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_header_and_task -v`

**GREEN Phase:**

**Implementation:** Format header line and conditional task line from TreeStatus fields

**Behavior:**
- Call aggregate_trees() from planstate.aggregation
- For each tree: format header line with slug/branch, dirty indicator, commit status
- Slug display: tree.slug, or "main" when tree.is_main=True
- Dirty indicator: "●" when is_dirty=True, "○" when False
- Commit status: "N commits since handoff" when >0, "clean" when 0
- After header, if task_summary is not None: output `  Task: <summary>` (2-space indent)

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Import aggregate_trees from planstate.aggregation
  Location hint: Top of file, with other imports

- File: `src/claudeutils/worktree/cli.py`
  Action: Implement rich output with header + conditional task line in else branch
  Location hint: Inside ls function, else clause

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with real git repo + session.md, verify header format and task line
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_header_and_task -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---
