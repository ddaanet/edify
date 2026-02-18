# Cycle 3.7

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.7: Sort trees by latest_commit_timestamp descending

**RED Phase:**

**Test:** `test_tree_sorting_by_timestamp`
**Assertions:**
- Setup: Create main + 2 worktrees, commit to main at T1, worktree1 at T2, worktree2 at T3 (T3 > T2 > T1)
- Call aggregate_trees() → AggregatedStatus.trees[0] is worktree2 (most recent)
- Order verification: trees[0].latest_commit_timestamp > trees[1].latest_commit_timestamp > trees[2].latest_commit_timestamp
- Specific index check: trees[0].slug == "worktree-2", trees[1].slug == "worktree-1", trees[2].is_main == True
- Type check: All latest_commit_timestamp values are integers

**Expected failure:** Trees in wrong order (main first, or worktree1 before worktree2), or timestamps not descending

**Why it fails:** No sorting applied to trees list

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_tree_sorting_by_timestamp -v`

**GREEN Phase:**

**Implementation:** Sort trees by latest_commit_timestamp in descending order

**Behavior:**
- After collecting all TreeStatus objects, sort by latest_commit_timestamp
- Use sorted(trees, key=lambda t: t.latest_commit_timestamp, reverse=True)
- Store sorted list in AggregatedStatus.trees

**Approach:** Python sorted() with lambda key and reverse=True

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Add sorting step in aggregate_trees() before return
  Location hint: After tree collection loop, before creating AggregatedStatus

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with main + 2 worktrees, make commits at different times
  Location hint: New test function, verify order matches commit timestamps

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_tree_sorting_by_timestamp -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---
