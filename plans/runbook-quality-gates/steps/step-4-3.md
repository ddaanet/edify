# Cycle 4.3

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

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

# Phase 5: Integration — directory input and `--skip` flags (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (modify)
- `tests/test_validate_runbook.py` (modify)

**Depends on:** Phases 1–4 (all 4 subcommands implemented — integration exercises them together)

**Consolidation:** Originally 2 cycles (directory input + skip flags); merged since both are same-module argparse additions testable via single parametrized test.

---
