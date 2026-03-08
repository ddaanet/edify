---
type: tdd
model: sonnet
name: bootstrap-tag-support
---

## Common Context

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Stop/Error Conditions (all cycles):**
STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any existing tests break (regression)

Actions when stopped: 1) Document in reports/ 2) Test passes unexpectedly → Investigate if feature exists 3) Regression → STOP, report broken tests 4) Scope unclear → STOP, document ambiguity

**Conventions:**
- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Target file: `agent-core/bin/prepare-runbook.py`
- Test file: `tests/test_prepare_runbook_mixed.py` (existing test file for mixed runbook features)
- Import pattern: use `importlib.util.spec_from_file_location` per existing test convention

### Phase 1: Fix mixed-type Common Context injection (type: tdd, model: sonnet)

Fix `assemble_phase_files` to inject `DEFAULT_TDD_COMMON_CONTEXT` when any phase has Cycles, not just when the first phase does.

## Cycle 1.1: Mixed-type assembly injects default Common Context

**RED Phase:**

**Test:** `test_mixed_assembly_injects_default_common_context` in `TestMixedCommonContext` class
**Assertions:**
- Create 2 phase files in tmp_path: phase-1 with `## Step 1.1:` (general), phase-2 with `## Cycle 2.1:` containing RED/GREEN phases (TDD) — no Common Context in either file
- Call `assemble_phase_files(tmp_path)` → returns `(content, phase_dir)`
- Assert `content is not None`
- Assert `"## Common Context"` in content
- Assert `"stop/error conditions"` in content.lower()

**Expected failure:** `AssertionError` — assembled content lacks `## Common Context` because `is_tdd` is False when first phase has Steps

**Why it fails:** `assemble_phase_files` sets `is_tdd = True` only when `i == 0` file has Cycle headers; mixed runbooks with general-first phase get `is_tdd = False`, skipping DEFAULT_TDD_COMMON_CONTEXT injection

**Verify RED:** `just test tests/test_prepare_runbook_mixed.py::TestMixedCommonContext::test_mixed_assembly_injects_default_common_context -v`

---

**GREEN Phase:**

**Implementation:** Fix mixed-type detection in `assemble_phase_files`

**Behavior:**
- Track whether ANY phase file has Cycle headers (not just first)
- Use tracked flag for DEFAULT_TDD_COMMON_CONTEXT injection decision

**Approach:** Initialize `has_any_cycles = False` before loop. In loop body, check each file for Cycle headers (move cycle detection out of the `if i == 0` guard). Set `has_any_cycles = True` when found. Use `has_any_cycles` instead of `is_tdd` for the injection condition at line 946.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Scan all phase files for Cycle headers, not just first. Use result for Common Context injection.
  Location hint: `assemble_phase_files` function, lines 897-947

**Verify lint:** `just lint`
**Verify GREEN:** `just test tests/test_prepare_runbook_mixed.py::TestMixedCommonContext -v`
**Verify no regression:** `just test tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_boundary.py -v`

### Phase 2: BOOTSTRAP tag support for 3-step cycle generation (type: tdd, model: sonnet)

Extend `split_cycle_content` to detect `**Bootstrap:**` sections and produce 3 step files (bootstrap + test + impl) per cycle. Update orchestrator generation to include BOOTSTRAP role.

## Cycle 2.1: split_cycle_content detects Bootstrap marker

**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` — `split_cycle_content` function (~line 1329) for current 2-way split logic

**RED Phase:**

**Test:** `test_split_with_bootstrap` and `test_split_without_bootstrap` in `TestBootstrapSplit` class
**Assertions (test_split_with_bootstrap):**
- Input content: `**Bootstrap:** Create stub module with default return.\n\n---\n\n**RED Phase:**\nWrite test.\n**GREEN Phase:**\nImplement.`
- Call `split_cycle_content(content)` → returns 3-tuple
- `result[0]` (bootstrap) contains `"Create stub"`
- `result[1]` (red) contains `"RED Phase"`
- `result[2]` (green) contains `"GREEN Phase"`

**Assertions (test_split_without_bootstrap):**
- Input content: `**RED Phase:**\nWrite test.\n**GREEN Phase:**\nImplement.` (no Bootstrap)
- Call `split_cycle_content(content)` → returns 3-tuple
- `result[0]` (bootstrap) is `""`
- `result[1]` (red) contains `"RED Phase"`
- `result[2]` (green) contains `"GREEN Phase"`

**Expected failure:** `AssertionError` — `split_cycle_content` returns 2-tuple, test expects 3-tuple. Unpacking fails with `ValueError: not enough values to unpack`

**Why it fails:** Function has no Bootstrap detection — returns `(red_content, green_content)` only

**Verify RED:** `just test tests/test_prepare_runbook_mixed.py::TestBootstrapSplit -v`

---

**GREEN Phase:**

**Implementation:** Extend `split_cycle_content` to detect and extract Bootstrap section

**Behavior:**
- Check for `**Bootstrap:**` marker in content
- If found, split on `---` separator between Bootstrap section and RED phase
- Extract Bootstrap content (everything from `**Bootstrap:**` marker up to `---` separator)
- Split remaining content on `**GREEN Phase:**` as before
- Return 3-tuple: `(bootstrap_content, red_content, green_content)`
- When no Bootstrap marker, return `("", red_content, green_content)` — backward compatible via leading empty string

**Approach:** Before the existing GREEN split, check for `**Bootstrap:**`. If present, find the `---` separator after it, split there. Pass remainder to existing GREEN split logic.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add Bootstrap detection in `split_cycle_content`, change return to 3-tuple
  Location hint: `split_cycle_content` function (~line 1329)

**Verify lint:** `just lint`
**Verify GREEN:** `just test tests/test_prepare_runbook_mixed.py::TestBootstrapSplit -v`
**Verify no regression:** `just test tests/test_prepare_runbook_mixed.py -v`

## Cycle 2.2: Generate bootstrap step files and update all callers

**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` — step file writing loop (~line 1747) and `generate_default_orchestrator` (~line 1344) for cycle item generation

**RED Phase:**

**Test:** `test_bootstrap_generates_three_step_files` and `test_no_bootstrap_generates_two_step_files` in `TestBootstrapStepFiles` class

**Assertions (test_bootstrap_generates_three_step_files):**
- Create TDD runbook with cycle: `**Bootstrap:** Create stub.\n\n---\n\n**RED Phase:**\nTest.\n**GREEN Phase:**\nImpl.\n**Stop/Error Conditions:** STOP if unexpected.`
- Run `_run_validate(tmp_path, content, "bootstrap-test")` → returns `(True, steps_dir)`
- `step-1-1-bootstrap.md` exists in steps_dir, contains `"Create stub"`
- `step-1-1-test.md` exists, contains `"RED Phase"` or `"Test"`
- `step-1-1-impl.md` exists, contains `"GREEN Phase"` or `"Impl"`

**Assertions (test_no_bootstrap_generates_two_step_files):**
- Create TDD runbook with cycle WITHOUT Bootstrap marker (existing format)
- Run `_run_validate`
- `step-1-1-test.md` and `step-1-1-impl.md` exist
- No `step-1-1-bootstrap.md` file exists

**Expected failure:** `AssertionError` — no `step-1-1-bootstrap.md` generated; OR `ValueError` from callers still expecting 2-tuple from `split_cycle_content`

**Why it fails:** Step writing loop unpacks 2-tuple from `split_cycle_content`, doesn't handle bootstrap content

**Verify RED:** `just test tests/test_prepare_runbook_mixed.py::TestBootstrapStepFiles -v`

---

**GREEN Phase:**

**Implementation:** Update step writing loop and all `split_cycle_content` callers for 3-tuple

**Behavior:**
- Unpack 3 values from `split_cycle_content`: `bootstrap_content, red_content, green_content`
- If `bootstrap_content` is non-empty, generate `step-X-Y-bootstrap.md` via `generate_cycle_file`
- Continue generating test and impl files as before
- Grep all `split_cycle_content` call sites — fix any remaining 2-tuple unpacking

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Update TDD cycle step file writing loop (~line 1753) and any other callers
  Location hint: grep for `split_cycle_content` across file

**Verify lint:** `just lint`
**Verify GREEN:** `just test tests/test_prepare_runbook_mixed.py::TestBootstrapStepFiles -v`
**Verify no regression:** `just test -v`

## Cycle 2.3: Orchestrator plan includes BOOTSTRAP role items

**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` — `generate_default_orchestrator` cycle item building (~line 1381)

**RED Phase:**

**Test:** `test_orchestrator_includes_bootstrap_items` and `test_orchestrator_no_bootstrap_unchanged` in `TestBootstrapOrchestrator` class

**Assertions (test_orchestrator_includes_bootstrap_items):**
- Create cycles list with one cycle containing Bootstrap marker content
- Call `generate_default_orchestrator` with those cycles
- Output contains `"BOOTSTRAP"` role text
- BOOTSTRAP entry appears before TEST entry for same cycle number
- Order per cycle: BOOTSTRAP → TEST → IMPLEMENT

**Assertions (test_orchestrator_no_bootstrap_unchanged):**
- Create cycles list WITHOUT Bootstrap content (standard format)
- Call `generate_default_orchestrator`
- Output does NOT contain `"BOOTSTRAP"`
- Output contains TEST and IMPLEMENT entries only (existing behavior preserved)

**Expected failure:** `AssertionError` — orchestrator output has no BOOTSTRAP entries

**Why it fails:** `generate_default_orchestrator` only creates TEST and IMPLEMENT items per cycle

**Verify RED:** `just test tests/test_prepare_runbook_mixed.py::TestBootstrapOrchestrator -v`

---

**GREEN Phase:**

**Implementation:** Add BOOTSTRAP role to orchestrator generation

**Behavior:**
- In the cycle processing loop, call `split_cycle_content` to detect Bootstrap content
- If Bootstrap content exists, add a BOOTSTRAP item with sort key `cycle["minor"] - 1.0` (before TEST at `minor - 0.5`)
- Bootstrap file stem: `{base_stem}-bootstrap`
- Add to `max_turns_lookup` with same turns as test/impl

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add BOOTSTRAP item in `generate_default_orchestrator` cycle processing
  Location hint: `if cycles:` block (~line 1381)

**Verify lint:** `just lint`
**Verify GREEN:** `just test tests/test_prepare_runbook_mixed.py::TestBootstrapOrchestrator -v`
**Verify no regression:** `just test -v`

## Cycle 2.4: End-to-end integration with phase-file assembly

**RED Phase:**

**Test:** `test_full_pipeline_with_bootstrap_cycles` in `TestBootstrapEndToEnd` class

**Assertions:**
- Create phase-file directory: phase-1 general (Steps), phase-2 TDD with Bootstrap markers on cycles
- Run `validate_and_create` on assembled content
- Result is True (pipeline succeeds)
- Bootstrap step files exist for cycles with Bootstrap content
- Test/impl step files exist for all cycles
- Orchestrator plan references bootstrap step files
- No validation errors

**Expected failure:** `AssertionError` — integration test verifies all pieces work together. May reveal edge cases in assembly + splitting + generation chain.

**Why it fails:** If any component doesn't properly handle the 3-way split in context of full pipeline, integration test catches it.

**Verify RED:** `just test tests/test_prepare_runbook_mixed.py::TestBootstrapEndToEnd -v`

---

**GREEN Phase:**

**Implementation:** Fix any remaining integration issues

**Behavior:**
- All components work together: assembly → validation → splitting → file generation → orchestrator
- No special changes expected if prior cycles are correct — this validates integration

**Changes:**
- File: `agent-core/bin/prepare-runbook.py` (if needed)
  Action: Fix any edge cases revealed by integration test

**Verify lint:** `just lint`
**Verify GREEN:** `just test tests/test_prepare_runbook_mixed.py::TestBootstrapEndToEnd -v`
**Verify no regression:** `just precommit`
