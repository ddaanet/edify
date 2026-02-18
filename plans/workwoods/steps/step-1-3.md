# Cycle 1.3

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 1

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
