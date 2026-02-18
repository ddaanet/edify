# Cycle 3.6

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.6: Per-tree plan discovery (list_plans per tree)

**RED Phase:**

**Test:** `test_per_tree_plan_discovery`
**Assertions:**
- Setup: Create main repo with plans/plan-a/, create worktree with plans/plan-b/
- Call aggregate_trees() → AggregatedStatus.plans contains 2 PlanState objects
- Plan names: "plan-a" from main and "plan-b" from worktree both present
- Deduplication: Create same plan (plans/plan-c/) in both trees → only 1 PlanState in result
- Deduplication precedence: main tree plan overrides worktree plan (main wins on conflict)
- Verification: Uses actual list_plans() function (from Phase 1), not mocked

**Expected failure:** `ImportError: cannot import name 'aggregate_trees'` or `NameError` (function not yet created — Cycles 3.1-3.5 only created private helpers)

**Why it fails:** aggregate_trees() public function doesn't exist yet; this cycle creates it

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_per_tree_plan_discovery -v`

**GREEN Phase:**

**Implementation:** Create aggregate_trees() function, run list_plans() for each tree's plans/ directory, aggregate results

**Behavior:**
- For each tree_path in worktrees:
  - Run list_plans(tree_path / "plans")
  - Collect PlanState objects
- Deduplicate by plan name (main tree plans override worktree plans)
- Store all plans in AggregatedStatus.plans list

**Approach:** Dict keyed by plan name to deduplicate, convert to list at end

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Create aggregate_trees() public function with plan discovery loop (uses helpers from Cycles 3.1-3.5)
  Location hint: New public function composing _parse_worktree_list, _commits_since_handoff, _latest_commit, _is_dirty, _task_summary

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with main + worktree, both having plans/ directories
  Location hint: New test function, verify both trees' plans found

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_per_tree_plan_discovery -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---
