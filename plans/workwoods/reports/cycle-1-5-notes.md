# Cycle 1.5: list_plans() helper for directory scanning

**Status:** STOP_CONDITION - RED phase violation

**Timestamp:** 2026-02-17

## RED Phase

**Test command:** `pytest tests/test_planstate_inference.py::test_list_plans_directory_scanning -v`

**Test created:** Added `test_list_plans_directory_scanning()` to test file with assertions for:
- list_plans returns 2 PlanState objects when given 2 valid plan directories
- "reports" directory excluded from results
- Empty directories excluded from results
- Missing directory returns empty list
- Result names sorted as ["plan-a", "plan-b"]

**RED result:** PASS (unexpected)

## Stop Condition

**Issue:** Test passes when expected failure was specified.

**Root cause:** The `list_plans()` function is already fully implemented in `src/claudeutils/planstate/inference.py` (lines 99-111):
```python
def list_plans(plans_dir: Path) -> list[PlanState]:
    """List all plans in a plans directory, filtering out empty directories."""
    if not plans_dir.exists():
        return []

    plans = []
    for plan_dir in sorted(plans_dir.iterdir()):
        if plan_dir.is_dir():
            state = infer_state(plan_dir)
            if state is not None:
                plans.append(state)

    return plans
```

This implementation includes:
- Directory existence check (returns [] for nonexistent)
- Sorted iteration with `sorted(plans_dir.iterdir())`
- Filtering via `infer_state()` (returns None for empty dirs, skips "reports")
- Complete directory scanning logic

**Expected per cycle spec:** list_plans stub from Cycle 1.1 returns empty list for populated directory
**Actual:** Function is fully implemented

**No [REGRESSION] marker:** The cycle spec does not include `[REGRESSION]` marker, so unexpected pass is a blocker.

## Decision

RED phase violation: test passed unexpectedly with no regression marker. Implementation already exists from prior execution. Requires orchestrator investigation before proceeding to next cycle.

**Test file status:** Modified (test added to test file, test passes)
**Source files status:** No changes needed (already implemented)
