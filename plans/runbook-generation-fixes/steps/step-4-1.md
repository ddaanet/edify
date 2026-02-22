# Cycle 4.1

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Cycle 4.1: PHASE_BOUNDARY entries include phase file path

**Prerequisite:** Read `generate_default_orchestrator()` (line ~743-805) — understand PHASE_BOUNDARY generation at line ~798-800 and how `is_phase_boundary` is computed.

**RED Phase:**

**Test:** `test_orchestrator_plan_includes_phase_file_paths`
**Setup:** Create phase files in `tmp_path` directory:
- `plans/test-job/runbook-phase-1.md`: Phase 1 with general steps
- `plans/test-job/runbook-phase-2.md`: Phase 2 with TDD cycles

Assemble via `assemble_phase_files()`, run full pipeline through `validate_and_create()`.

**Assertions:**
- Orchestrator plan contains `Phase file: plans/test-job/runbook-phase-1.md` in Phase 1 PHASE_BOUNDARY entry
- Orchestrator plan contains `Phase file: plans/test-job/runbook-phase-2.md` in Phase 2 PHASE_BOUNDARY entry
- Phase file paths reference the actual source phase files (not assembled content)

**Expected failure:** AssertionError — current `generate_default_orchestrator()` does not include phase file paths in PHASE_BOUNDARY entries

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestOrchestratorPlan::test_orchestrator_plan_includes_phase_file_paths -v`

---

**GREEN Phase:**

**Implementation:** Add phase file references to PHASE_BOUNDARY entries.

**Behavior:**
- When runbook is assembled from phase files (directory input), PHASE_BOUNDARY entries include the source phase file path
- When runbook is a single file (no phase files), phase file paths are omitted
- Format: `Phase file: {phase_dir}/runbook-phase-{phase_num}.md` on a separate line within the PHASE_BOUNDARY block

**Approach:**
1. Add `phase_dir` parameter to `generate_default_orchestrator()` (default: `None`)
2. In PHASE_BOUNDARY block (line ~798-800): when `phase_dir` is not None, append `Phase file: {phase_dir}/runbook-phase-{phase}.md\n` after the checkpoint instruction line
3. In `validate_and_create()`: pass the source directory path (when assembled from phase files) to `generate_default_orchestrator()`. Add `phase_dir` parameter to `validate_and_create()` signature, populated from `main()` when input is a directory.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `phase_dir` parameter to `generate_default_orchestrator()`, include phase file path in PHASE_BOUNDARY
  Location hint: Function signature (line ~743), PHASE_BOUNDARY block (line ~798-800)
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `phase_dir` parameter to `validate_and_create()`, pass to orchestrator generation
  Location hint: Function signature (line ~808), orchestrator call (line ~904-908)
- File: `agent-core/bin/prepare-runbook.py`
  Action: In `main()`, pass source directory to `validate_and_create()` when input is directory
  Location hint: Directory handling branch (line ~955-967)

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestOrchestratorPlan -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

---
