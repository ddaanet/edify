# Cycle 1.2

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.2: Status priority detection (parametrized — all 4 levels)

**Rationale:** Four status levels follow the same pattern — create artifacts, assert correct status and priority. Consolidated into a single parametrized cycle to avoid redundant RED/GREEN rounds for identical logic.

**Prerequisite:** Read design State Inference Rules table for artifact patterns and priority order.

**RED Phase:**

**Test:** `test_status_priority_detection` (parametrized)
**Parameters:**

| Status | Artifacts to create | Expected status | Expected artifacts |
|--------|-------------------|----------------|-------------------|
| requirements | requirements.md | "requirements" | {"requirements.md"} |
| designed | requirements.md + design.md | "designed" | {"requirements.md", "design.md"} |
| planned | design.md + runbook-phase-1.md + runbook-phase-2.md | "planned" | superset of {"runbook-phase-1.md", "runbook-phase-2.md"} |
| ready | design.md + runbook-phase-1.md + steps/ (mkdir) + orchestrator-plan.md | "ready" | superset of {"steps/", "orchestrator-plan.md"} |

**Assertions (per parameter set):**
- `infer_state(plan_dir).status` equals expected status string (exact match)
- `infer_state(plan_dir).artifacts` matches expected artifacts set
- `infer_state(plan_dir).name` equals directory basename (e.g., `"test-plan"` for `plans/test-plan/`)
- Result is PlanState instance (`isinstance(result, PlanState)`)
- Priority verified: higher-status artifacts override lower (designed > requirements, planned > designed, ready > planned)

**Expected failure:** `AttributeError: 'NoneType' object has no attribute 'status'` for requirements case (infer_state returns None)

**Why it fails:** infer_state() doesn't scan for any artifacts yet

**Verify RED:** `pytest tests/test_planstate_inference.py::test_status_priority_detection -v`

**GREEN Phase:**

**Implementation:** Build complete artifact detection priority chain in infer_state()

**Behavior:**
- Scan in priority order: ready (steps/ + orchestrator-plan.md) → planned (runbook-phase-*.md glob) → designed (design.md) → requirements (requirements.md)
- Highest-found status wins
- Collect all artifacts found, not just highest-status ones
- Extract plan name from directory basename

**Approach:** Check highest priority first, set status on first match, continue collecting all artifacts

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Implement full artifact detection priority chain in infer_state()
  Location hint: Existing file (from Cycle 1.1), check ready → planned → designed → requirements

- File: `tests/test_planstate_inference.py`
  Action: Add parametrized test with @pytest.mark.parametrize covering all 4 status levels
  Location hint: Existing file (from Cycle 1.1), use tmp_path fixture

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_status_priority_detection -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---
