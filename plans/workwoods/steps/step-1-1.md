# Cycle 1.1

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.1: Empty directory detection (not a plan)

**Rationale:** Testing empty directory first establishes the None-return baseline and list_plans() filtering contract. This is foundational behavior that all subsequent cycles depend on (empty dirs must not appear in results). Alternative ordering (happy path first) would require mocking list_plans() filtering before implementing it.

**Prerequisite:** Read design State Inference Rules table for artifact patterns.

**RED Phase:**

**Test:** `test_empty_directory_not_a_plan`
**Assertions:**
- `infer_state(tmp_path / "plans/empty")` returns exactly `None` (type check: `result is None`)
- `list_plans(tmp_path / "plans")` returns empty list `[]` when only empty directories exist
- No exception raised for empty directory (no try/except needed)

**Expected failure:** `ModuleNotFoundError: No module named 'claudeutils.planstate'` (module doesn't exist)

**Why it fails:** No planstate module exists yet

**Verify RED:** `pytest tests/test_planstate_inference.py::test_empty_directory_not_a_plan -v`

**GREEN Phase:**

**Implementation:** Create planstate module with infer_state() returning None for empty dirs

**Behavior:**
- infer_state() scans for recognized artifacts (requirements.md, design.md, etc.)
- If no artifacts found, return None
- list_plans() filters None results from plan directory scan

**Approach:** Check for artifact existence in priority order (highest status first)

**Changes:**
- File: `src/claudeutils/planstate/__init__.py`
  Action: Create module with public API exports (infer_state, list_plans)
  Location hint: New file

- File: `src/claudeutils/planstate/models.py`
  Action: Define PlanState dataclass (name, status, next_action, gate, artifacts fields)
  Location hint: New file

- File: `src/claudeutils/planstate/inference.py`
  Action: Implement infer_state(plan_dir: Path) -> PlanState | None
  Location hint: New file, returns None for empty dirs

- File: `tests/test_planstate_inference.py`
  Action: Create test with tmp_path fixture, empty plans/<name>/ directory
  Location hint: New file

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_empty_directory_not_a_plan -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---
