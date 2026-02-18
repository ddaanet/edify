# Cycle 4.4

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.4: Rich mode plan + gate formatting

**RED Phase:**

**Test:** `test_rich_mode_plan_and_gate`
**Assertions:**
- Plan line:
  - For tree containing plan "foo" with status="designed", next_action="/runbook plans/foo/design.md":
    Output contains exactly: `  Plan: foo [designed] → /runbook plans/foo/design.md` (2-space indent)
  - Multiple plans: both plan lines shown in same tree section
  - No plans: no "  Plan:" line for that tree
- Gate line:
  - For plan with gate="vet stale — re-vet first":
    Output contains exactly: `  Gate: vet stale — re-vet first` (2-space indent)
    Gate line appears after plan line for same plan
  - For plan with gate=None: no "  Gate:" line for that plan
- Plans filtered by tree (only plans under current tree's plans/ directory shown)

**Expected failure:** Plan line not displayed (AttributeError or plan filtering not implemented)

**Why it fails:** Plan and gate line formatting not implemented

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_plan_and_gate -v`

**GREEN Phase:**

**Implementation:** Display plan lines with conditional gate lines for plans in current tree

**Behavior:**
- After task line, iterate through aggregated_status.plans
- Filter to plans belonging to current tree (plan directory under tree path)
- For each plan: output plan line `  Plan: <name> [<status>] → <next_action>`
- If plan.gate is not None: output gate line `  Gate: <gate message>`

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py` (Phase 1-3 artifact)
  Action: Verify PlanState includes tree association for filtering
  Location hint: Check AggregatedStatus.plans structure

- File: `src/claudeutils/worktree/cli.py`
  Action: Add plan + gate line output after task line in rich formatting loop
  Location hint: After task line in tree iteration

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with plans/ directory + stale design.md, verify Plan and Gate lines
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_plan_and_gate -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---
