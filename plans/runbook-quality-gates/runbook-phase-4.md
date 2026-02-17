# Phase 4: `red-plausibility` subcommand (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (modify)
- `tests/test_validate_runbook.py` (modify)

**Depends on:** Phase 1 (script scaffold, importlib infrastructure, `write_report` function)

**Parsing targets:** RED `**Expected failure:**` text (function/module names) + GREEN `**Changes:**` sections (what was created in prior cycles).

**Exit codes:** 0 = plausible (no violations), 1 = clear violation (function created in prior GREEN, RED expects ImportError), 2 = ambiguous (function exists but RED tests different behavior).

---

## Cycle 4.1: red-plausibility — happy path (RED function not in prior GREENs, exit 0)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` — understand current structure from Phase 1.

**RED Phase:**

**Test:** `test_red_plausibility_happy_path`
**Assertions:**
- Running `red-plausibility` on `VALID_TDD` fixture exits with code 0
- Report file written to expected path
- Report contains `**Result:** PASS`
- Report `Summary` shows `Failed: 0`, `Ambiguous: 0`

**Fixture:** `VALID_TDD` — Cycle 1.1 RED expects `ImportError` on `src.module`; no prior GREEN creates `src/module.py` (Cycle 1.1 RED comes before its own GREEN).

**Expected failure:** `AssertionError` — `red-plausibility` handler is still a stub; no report written.

**Why it fails:** `red-plausibility` handler not yet implemented.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_red_plausibility_happy_path -v`

---

**GREEN Phase:**

**Implementation:** Implement `check_red_plausibility(content, path)` and wire to `red-plausibility` handler.

**Behavior:**
- Process cycles in document order, maintaining `created_names` set (function/module names created in prior cycles' GREEN `**Changes:**` sections only)
- For each cycle N: check its RED `**Expected failure:**` line for function/module names referenced against `created_names` (built from cycles 1..N-1)
- After checking cycle N's RED: add cycle N's own GREEN `Action: Create` entries to `created_names` (making them available for cycles N+1 and beyond)
- If `ImportError` or `ModuleNotFoundError` expected on a name NOT in `created_names` → plausible (no violation)
- Write PASS report, exit 0

**Approach:** Parse `**Expected failure:**` with regex to extract module/function name (e.g., `ImportError` on `src.module` → extract `src.module` or `module`). Parse GREEN `**Changes:**` `Action: Create` entries for file stem names. Only prior cycles' GREENs (cycles 1..N-1) contribute to `created_names` when evaluating cycle N's RED — the current cycle's own GREEN must NOT be included (that GREEN hasn't executed yet when RED is written, so it cannot make the RED already-passing).

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add `check_red_plausibility(content, path)` with sequential RED-check then GREEN-accumulate per cycle; wire to handler
  Location hint: After `check_test_counts`, before `main()`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_red_plausibility_happy_path -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

## Cycle 4.2: red-plausibility — clear violation (function created in prior GREEN, RED expects ImportError, exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_red_plausibility` from Cycle 4.1 — understand `created_names` tracking and name extraction.

**RED Phase:**

**Test:** `test_red_plausibility_violation`
**Assertions:**
- Running `red-plausibility` on `VIOLATION_RED_IMPLAUSIBLE` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section names: the function (`widget`), prior GREEN cycle that created it (1.1), current RED cycle (1.2)
- Report `Summary` shows `Failed: 1`, `Ambiguous: 0`

**Fixture:** `VIOLATION_RED_IMPLAUSIBLE` — Cycle 1.1 GREEN creates `src/widget.py` with `widget()` function; Cycle 1.2 RED expects `ImportError` — `widget` not importable. Since `widget.py` was created in prior GREEN, RED would already pass.

**Expected failure:** `AssertionError` — current 4.1 implementation passes all inputs as plausible; violation detection not yet added.

**Why it fails:** 4.1 GREEN spec defines happy-path-only behavior (exit 0 for all plausible inputs); violation detection branch does not exist yet.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_red_plausibility_violation -v`

---

**GREEN Phase:**

**Implementation:** Add clear-violation detection to `check_red_plausibility`.

**Behavior:**
- When RED expects `ImportError` or `ModuleNotFoundError` on a name that IS in `created_names`: clear violation (exit 1)
- Violation record: `function_name`, `created_in` (prior cycle ID), `red_cycle_id`
- Write FAIL report with violations, exit 1

**Approach:** Collect `created_names` from prior cycles' GREENs only (cycles 1..N-1, NOT the current cycle's own GREEN). Check current cycle's RED `**Expected failure:**`. If failure type is `ImportError`/`ModuleNotFoundError` AND the name appears in `created_names` → violation. `sys.exit(1)` with violations.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add clear-violation check in RED-phase processing block of `check_red_plausibility`; update handler to exit 1
  Location hint: Inside `check_red_plausibility`, RED phase processing block

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_red_plausibility_violation -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

## Cycle 4.3: red-plausibility — ambiguous case (function exists, behavior test, exit 2)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_red_plausibility` — understand violation vs ambiguous distinction from Cycles 4.1–4.2.

**RED Phase:**

**Test:** `test_red_plausibility_ambiguous`
**Assertions:**
- Running `red-plausibility` on `AMBIGUOUS_RED_PLAUSIBILITY` fixture exits with code 2
- Report contains `**Result:** AMBIGUOUS`
- Report `## Ambiguous` section (sibling to `## Violations`) names the function and explains it exists but RED tests different behavior
- Report `Summary` shows `Failed: 0`, `Ambiguous: 1`

**Fixture:** `AMBIGUOUS_RED_PLAUSIBILITY` — Cycle 1.1 GREEN creates `src/widget.py` with `widget()` function; Cycle 1.2 RED expects `ValueError` — widget raises on invalid input. Function exists from prior GREEN, but RED tests different behavior (not importability).

**Expected failure:** `AssertionError` — current 4.2 implementation only handles `ImportError`/`ModuleNotFoundError` violations and passes `ValueError` cases as plausible (exit 0 instead of 2).

**Why it fails:** 4.2 checks only for import-type failures; `ValueError` on existing function not yet classified as ambiguous.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_red_plausibility_ambiguous -v`

---

**GREEN Phase:**

**Implementation:** Add ambiguous case handling to `check_red_plausibility`.

**Behavior:**
- When RED expects a non-import failure (e.g., `ValueError`, `AttributeError`) on a name in `created_names`: ambiguous case (neither clearly plausible nor clear violation)
- Ambiguous record: `function_name`, `created_in`, `red_cycle_id`, `failure_type`, `explanation: "function exists but RED tests different behavior"`
- No clear violations AND ambiguous cases present → write AMBIGUOUS report, exit 2
- Clear violations take precedence: if both violations and ambiguous → exit 1 (violations win)

**Approach:** Classify failure type: import failures (`ImportError`, `ModuleNotFoundError`) → violation when name exists; other failure types (`ValueError`, `AttributeError`, etc.) → ambiguous when name exists. `sys.exit(2)` only when ambiguous list non-empty and violations list empty.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add ambiguous classification in `check_red_plausibility` RED-phase block; update handler exit logic (exit 2 for ambiguous-only, exit 1 for violations); extend `write_report` to render `**Result:** AMBIGUOUS`, `## Ambiguous` section, and `Ambiguous:` count in Summary when `ambiguous` parameter is non-empty
  Location hint: Inside `check_red_plausibility` (after violation check) and `write_report` (ambiguous rendering path)

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_red_plausibility_ambiguous -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

**Checkpoint:** `just test tests/test_validate_runbook.py` — all tests pass.
