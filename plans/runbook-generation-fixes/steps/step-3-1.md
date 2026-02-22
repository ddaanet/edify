# Cycle 3.1

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.1: Extract phase preamble from assembled content

**RED Phase:**

**Test:** `test_extract_phase_preambles`
**Setup:** Assembled content string with 3 phases, each with a phase header followed by preamble text and then a step/cycle header:
- Phase 1: header `### Phase 1: Core behavior (type: tdd, model: sonnet)`, preamble "RC-1 fix. Prerequisites: foo module exists.\n\n**Constraints:** No backward-incompatible changes.", then `Cycle 1.1: Test thing`
- Phase 2: header `### Phase 2: Infrastructure (type: general)`, preamble "Setup database connections. Verify connectivity.", then `Step 2.1: Configure DB`
- Phase 3: header `### Phase 3: Cleanup (type: tdd, model: sonnet)`, NO preamble (header immediately followed by `Cycle 3.1: Clean state`)

**Assertions:**
- `extract_phase_preambles(content)` returns dict with 3 keys: `{1, 2, 3}`
- Phase 1 preamble contains "RC-1 fix" and "Constraints"
- Phase 2 preamble contains "Setup database connections"
- Phase 3 preamble is empty string (no content between phase header and first cycle header)
- Preamble does NOT include the phase header line itself
- Preamble does NOT include step/cycle content

**Expected failure:** NameError — `extract_phase_preambles` does not exist

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext::test_extract_phase_preambles -v`

---

**GREEN Phase:**

**Implementation:** New `extract_phase_preambles()` function.

**Behavior:**
- Iterate through content lines
- When a `### Phase N:` header is found, start collecting preamble lines
- When a `## Step` or `## Cycle` header is found (or another `### Phase` header), stop collecting and store preamble for that phase
- Return `{phase_num: preamble_text}` where preamble_text is stripped of leading/trailing whitespace
- Phases with no content between header and first step/cycle get empty string

**Approach:** Line-by-line state machine similar to `extract_sections()`. Two states: "collecting preamble" and "not collecting". Transition on phase header (start) and step/cycle header (stop).

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `extract_phase_preambles(content)` function
  Location hint: After `extract_phase_models()` (added in Phase 2), before `assemble_phase_files()`

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext::test_extract_phase_preambles -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

---
