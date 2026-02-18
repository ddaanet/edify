# Cycle 1.4

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.4: Gate attachment interface (stub vet call)

**Note:** Actual vet.py built in Phase 2. This cycle wires the interface and tests with mock VetStatus.

**RED Phase:**

**Test:** `test_gate_attachment_with_mock`
**Assertions:**
- `infer_state(plan_dir).gate is None` (exact None check) when vet status has no stale chains (all fresh)
- `infer_state(plan_dir).gate == "design vet stale — re-vet before planning"` (exact string) when mock VetStatus returns stale design.md → design-review.md chain
- `infer_state(plan_dir).gate is None` when no vet_status_func provided (default behavior)
- Mock VetStatus with `VetChain(source="design.md", report="reports/design-review.md", stale=True, source_mtime=200.0, report_mtime=100.0)`

**Expected failure:** `AssertionError: assert None == "design vet stale — re-vet before planning"` (gate field exists but not populated from vet status)

**Why it fails:** Gate field exists in PlanState (from Cycle 1.1) with default None, but no vet status integration populates it

**Verify RED:** `pytest tests/test_planstate_inference.py::test_gate_attachment_with_mock -v`

**GREEN Phase:**

**Implementation:** Add gate field to PlanState, stub get_vet_status() call with mock in tests

**Behavior:**
- infer_state() calls get_vet_status(plan_dir) if available
- Parse VetStatus.chains to find first stale chain
- Map stale chain to gate message (design → "design vet stale — re-vet before planning")
- Gate is None if no vet status or no stale chains

**Approach:** Accept optional vet_status_func parameter in infer_state() for testing (dependency injection)

**Changes:**
- File: `src/claudeutils/planstate/models.py`
  Action: Add gate: str | None field to PlanState dataclass
  Location hint: After next_action field

- File: `src/claudeutils/planstate/inference.py`
  Action: Add gate computation logic, accept optional vet_status_func for testability
  Location hint: After next_action derivation, before return

- File: `tests/test_planstate_inference.py`
  Action: Create test with mock VetStatus showing stale design.md → design-review.md chain
  Location hint: New test function, use unittest.mock.Mock for VetStatus

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_gate_attachment_with_mock -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---
