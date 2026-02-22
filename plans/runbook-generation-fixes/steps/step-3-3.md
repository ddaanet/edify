# Cycle 3.3

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.3: Phase context omitted when preamble is blank or whitespace-only

**RED Phase:**

**Test:** `test_no_phase_context_when_preamble_empty`
**Setup:** Create runbook with:
- Phase 1 header followed by blank lines only before cycle header (whitespace-only preamble):
  ```
  ### Phase 1: Core (type: tdd, model: sonnet)


  ## Cycle 1.1: Direct start
  ```
- Phase 2 header with substantive preamble (control case):
  ```
  ### Phase 2: Extra (type: general)

  Some preamble here.

  ## Step 2.1: Thing
  ```

Run full pipeline.

**Assertions:**
- `extract_phase_preambles()` returns empty string (after strip) for Phase 1
- Generated cycle file `steps/step-1-1.md` does NOT contain `## Phase Context`
- Generated step file `steps/step-2-1.md` DOES contain `## Phase Context` with "Some preamble here." (control)

**Expected failure:** AssertionError — `extract_phase_preambles()` may return `"\n\n"` (raw blank lines) for Phase 1; if the generation guard uses `if phase_context:` instead of `if phase_context.strip():`, the whitespace-only preamble injects an empty `## Phase Context` section into the cycle file.

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext::test_no_phase_context_when_preamble_empty -v`

---

**GREEN Phase:**

**Implementation:** Ensure whitespace-only preamble guard uses `.strip()` in both extraction and injection.

**Behavior:**
- `extract_phase_preambles()` strips leading/trailing whitespace before returning each preamble; whitespace-only content returns empty string `""`
- `generate_step_file()` and `generate_cycle_file()` guard with `if phase_context.strip():` before injecting section
- Blank-line-only preamble → no `## Phase Context` section in output

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Verify `extract_phase_preambles()` strips preamble before storing; verify generation guard uses `.strip()` not bare truthiness
  Location hint: Return statement in `extract_phase_preambles()`, phase context injection block in both generation functions

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

### Phase 4: Orchestrator plan improvements (type: tdd, model: sonnet)

D-5: Phase file references in PHASE_BOUNDARY markers. Phase-agent model mapping.

**Post-Phase-2 state:** `extract_phase_models()` exists and `validate_and_create()` threads per-phase models to step/cycle generation. Phase models dict is available for orchestrator plan generation.

**Cumulative signature note (if Phases 3 and 4 run sequentially):** When implementing Phase 4, `validate_and_create()` already has `phase_models` (Phase 2) and `phase_preambles` (Phase 3) parameters. Add `phase_dir` as an additional parameter — do not replace the prior additions.

**Prerequisites:**
- Phase 2 complete (model propagation working)
- `agent-core/bin/prepare-runbook.py` — target file
- `tests/test_prepare_runbook_mixed.py` — test module (with Phases 1-3 tests)

**Completion validation:**
- All 2 cycles pass (RED fails then GREEN passes)
- `just test tests/test_prepare_runbook_mixed.py` — all tests pass (Phases 1-4)
- No regressions: `just test tests/test_prepare_runbook_inline.py`
- Orchestrator plan includes phase file paths and phase-model mapping table

---
