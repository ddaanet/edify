# Cycle 1.5

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.5: list_plans() helper for directory scanning

**RED Phase:**

**Test:** `test_list_plans_directory_scanning`
**Assertions:**
- `list_plans(plans_dir)` returns `list[PlanState]` with length 2 when plans/ contains "plan-a" (with requirements.md) and "plan-b" (with design.md)
- `"reports"` directory excluded (not in result list even if present in plans/)
- Empty directories excluded (create "empty-dir" with no artifacts → not in result)
- `list_plans(tmp_path / "nonexistent")` returns empty list `[]` (no exception for missing directory)
- Result list item names match directory names: `[ps.name for ps in result] == ["plan-a", "plan-b"]` (sorted)

**Expected failure:** `AssertionError: assert 0 == 2` or similar (list_plans stub from Cycle 1.1 returns empty list for populated directory)

**Why it fails:** list_plans() exists from Cycle 1.1 but only as stub returning [] — no directory scanning implemented

**Verify RED:** `pytest tests/test_planstate_inference.py::test_list_plans_directory_scanning -v`

**GREEN Phase:**

**Implementation:** Scan plans/ directory, call infer_state() per plan, filter None results

**Behavior:**
- Use `plans_dir.iterdir()` to list all items
- Skip dotfiles, "reports" directory, "claude" directory
- Call infer_state() for each directory
- Filter out None results (empty dirs, non-plans)
- Return list of PlanState objects

**Approach:** Generator expression with filter for None values

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Implement list_plans(plans_dir: Path) -> list[PlanState]
  Location hint: New function after infer_state()

- File: `src/claudeutils/planstate/__init__.py`
  Action: Export list_plans in __all__
  Location hint: Alongside infer_state

- File: `tests/test_planstate_inference.py`
  Action: Create test with multiple plan directories (some valid, some empty, include reports/)
  Location hint: New test function, use tmp_path with multiple subdirs

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_list_plans_directory_scanning -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---
