# Phase 2: `lifecycle` subcommand (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (modify)
- `tests/test_validate_runbook.py` (modify)

**Depends on:** Phase 1 (script scaffold, importlib infrastructure, `write_report` function)

**Parsing targets:** `File:` + `Action:` fields across all cycles/steps to build create→modify dependency graph.

---

## Cycle 2.1: lifecycle — happy path (correct create→modify ordering, exit 0)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` — understand current structure from Phase 1: importlib block, `write_report`, subcommand stubs.

**RED Phase:**

**Test:** `test_lifecycle_happy_path`
**Assertions:**
- Running `lifecycle` on `VALID_TDD` fixture exits with code 0
- Report file written to expected path
- Report contains `**Result:** PASS`
- Report `Summary` shows `Failed: 0`

**Fixture:** `VALID_TDD` — file `src/module.py` is created in Cycle 1.1 and modified in Cycle 1.2 (correct ordering).

**Expected failure:** `AssertionError` — `lifecycle` handler is still a stub; no report written.

**Why it fails:** `lifecycle` handler not yet implemented; stub exits 0 without writing report.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_lifecycle_happy_path -v`

---

**GREEN Phase:**

**Implementation:** Implement `check_lifecycle(content, path)` and wire to `lifecycle` handler.

**Behavior:**
- Reads runbook content (directory → `assemble_phase_files`; file → read directly)
- Extracts all `File:` + `Action:` pairs from each cycle/step in order
- Action classification: "create" actions = `Create`, `Write new`; "modify" actions = `Modify`, `Add`, `Update`, `Edit`, `Extend`
- Builds ordered list of `(cycle_id, file_path, action_type)` tuples
- Records first-occurrence action per file path
- No violations if all first occurrences are "create" (or files are never modified before created)
- Write PASS report, exit 0

**Approach:** Iterate cycles in document order. For each cycle, extract `File:` lines in its `**Changes:**` section and the `Action:` field on the next line. Maintain `dict[file_path, first_seen_cycle_id]` and `dict[file_path, first_action_type]`. No violations for VALID_TDD.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add `check_lifecycle(content, path)` function with file action extraction and ordering logic; wire to `lifecycle` handler
  Location hint: After `check_model_tags`, before `main()`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_lifecycle_happy_path -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

## Cycle 2.2: lifecycle — modify-before-create violation (exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_lifecycle` implementation from Cycle 2.1 — understand action tracking data structures.

**RED Phase:**

**Test:** `test_lifecycle_modify_before_create`
**Assertions:**
- Running `lifecycle` on `VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section names the file that was modified before creation
- Report shows the modify cycle ID and states no prior creation found
- Report `Summary` shows `Failed: 1`

**Fixture:** `VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE` — Cycle 1.1 has `File: src/widget.py, Action: Modify`; no earlier cycle creates `src/widget.py`.

**Expected failure:** `AssertionError` — current `check_lifecycle` from 2.1 passes all inputs (only tracks creation, doesn't flag modify-before-create).

**Why it fails:** 2.1 GREEN only needs to handle happy path; modify-before-create detection not yet added.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_lifecycle_modify_before_create -v`

---

**GREEN Phase:**

**Implementation:** Add modify-before-create detection to `check_lifecycle`.

**Behavior:**
- When first occurrence of a file path is a "modify" action → violation: file modified before creation
- Violation record: `file_path`, `modify_location` (cycle ID), `"no prior creation found"`
- Write FAIL report with violations, exit 1

**Approach:** When processing a modify action: if `file_path` not in `created_files` set → append violation. Maintain `created_files` set (files where first action was "create"). Process in document order.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add modify-before-create check inside `check_lifecycle`; extend `write_report` to handle lifecycle violation format if needed
  Location hint: Inside `check_lifecycle`, within the action-processing loop

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_lifecycle_modify_before_create -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

## Cycle 2.3: lifecycle — duplicate creation violation (exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_lifecycle` — understand `created_files` tracking from Cycle 2.2.

**RED Phase:**

**Test:** `test_lifecycle_duplicate_creation`
**Assertions:**
- Running `lifecycle` on `VIOLATION_LIFECYCLE_DUPLICATE_CREATE` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section names the duplicated file and both creation cycle IDs
- Report `Summary` shows `Failed: 1`

**Fixture:** `VIOLATION_LIFECYCLE_DUPLICATE_CREATE` — Cycle 1.1 creates `src/module.py`; Cycle 2.1 also creates `src/module.py`.

**Expected failure:** `AssertionError` — current `check_lifecycle` doesn't detect duplicate creation (only tracks first occurrence, not repeated create actions).

**Why it fails:** 2.2 implementation records first creation but doesn't check if a "create" action occurs when file already in `created_files`.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_lifecycle_duplicate_creation -v`

---

**GREEN Phase:**

**Implementation:** Add duplicate creation detection to `check_lifecycle`.

**Behavior:**
- When a "create" action is found for a file already in `created_files`: violation with both cycle IDs
- Violation record: `file_path`, `first_creation_location`, `duplicate_creation_location`
- Write FAIL report with violations, exit 1

**Approach:** When processing a create action: if `file_path` already in `created_files` dict → append duplicate violation with `created_files[file_path]` (first location) and current cycle ID. Both violations (modify-before-create and duplicate creation) can appear in same report.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add duplicate creation check in `check_lifecycle` create-action branch
  Location hint: Inside `check_lifecycle`, create-action handling

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_lifecycle_duplicate_creation -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

**Checkpoint:** `just test tests/test_validate_runbook.py` — all tests pass.
