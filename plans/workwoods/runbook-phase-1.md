### Phase 1: Plan State Inference (type: tdd)

**Purpose:** Create planstate module foundation with state inference from filesystem artifacts.

**Scope:**
- `src/claudeutils/planstate/__init__.py` - Public API exports
- `src/claudeutils/planstate/models.py` - Data models (PlanState, VetStatus, etc.)
- `src/claudeutils/planstate/inference.py` - Core inference logic
- `tests/test_planstate_inference.py` - Test coverage

**Dependencies:** None (foundation phase)

**Note:** Files in scope do not exist yet — this phase creates them. File references are validated as creation targets, not existing paths.

**Execution Model:** Sonnet (standard TDD implementation)

**Estimated Complexity:** Medium (new module setup with clear requirements)

**Weak Orchestrator Metadata:**
- Total Cycles: 5
- Restart required: No

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

## Cycle 1.3: Next action derivation from status

**RED Phase:**

**Test:** `test_next_action_derivation`
**Assertions:**
- Requirements status: `infer_state(requirements_only).next_action == "/design plans/test-plan/requirements.md"` (exact string with plan name substituted)
- Designed status: `infer_state(designed).next_action == "/runbook plans/test-plan/design.md"` (exact string)
- Planned status: `infer_state(planned).next_action == "agent-core/bin/prepare-runbook.py plans/test-plan"` (exact string, full path per design)
- Ready status: `infer_state(ready).next_action == "/orchestrate test-plan"` (exact string with plan name)
- Use parametrized test with 4 fixtures (one per status)

**Expected failure:** `AssertionError: assert '' == '/design plans/test-plan/requirements.md'` or `assert None == '/design ...'` (next_action field is empty/None)

**Why it fails:** next_action field not populated from status

**Verify RED:** `pytest tests/test_planstate_inference.py::test_next_action_derivation -v`

**GREEN Phase:**

**Implementation:** Map status to next action command string

**Behavior:**
- requirements → `/design plans/<name>/requirements.md`
- designed → `/runbook plans/<name>/design.md`
- planned → `agent-core/bin/prepare-runbook.py plans/<name>`
- ready → `/orchestrate <name>`

**Approach:** Status-to-command mapping table (dict or match statement)

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Add next_action derivation logic after status determination
  Location hint: After status is set in infer_state(), before return

- File: `tests/test_planstate_inference.py`
  Action: Add parametrized test covering all four status levels
  Location hint: Use @pytest.mark.parametrize with (status, artifacts, expected_next_action) tuples

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_next_action_derivation -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

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

## Phase 1 Checkpoint

**After all cycles complete:**

1. Run `just dev` to verify code quality
2. Functional review: Check that infer_state() returns correct status for all artifact combinations
3. Commit: All Phase 1 implementations and tests

**Expected state:**
- planstate module exists with inference.py, models.py, __init__.py
- All tests pass in test_planstate_inference.py
- list_plans() correctly scans plan directories and filters out non-plans
- Gate interface wired (actual vet integration in Phase 2)
