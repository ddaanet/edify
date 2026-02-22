# Cycle 1.1

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.1: Assembly injects phase headers when absent

**RED Phase:**

**Test:** `test_assembly_injects_phase_headers_when_absent`
**Setup:** Create 3 phase files in `tmp_path`:
- `runbook-phase-1.md`: contains `## Step 1.1: Do thing\n\nStep content.`
- `runbook-phase-2.md`: contains `## Cycle 2.1: Test thing\n\n**RED Phase:**\nTest.\n**GREEN Phase:**\nImpl.\n**Stop/Error Conditions:** STOP if unexpected.`
- `runbook-phase-3.md`: contains `## Step 3.1: Final thing\n\nFinal content.`
- No `### Phase N:` headers in any file

**Assertions:**
- Assembled content contains `### Phase 1:` before Step 1.1 content
- Assembled content contains `### Phase 2:` before Cycle 2.1 content
- Assembled content contains `### Phase 3:` before Step 3.1 content
- Phase headers appear in order: Phase 1 position < Phase 2 position < Phase 3 position

**Expected failure:** AssertionError — `### Phase 1:` not found in assembled content (current code doesn't inject headers)

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseNumbering::test_assembly_injects_phase_headers_when_absent -v`

---

**GREEN Phase:**

**Implementation:** Inject `### Phase N:` headers during phase file assembly.

**Behavior:**
- For each phase file, prepend `### Phase {phase_num}:` header (derive N from filename `runbook-phase-N.md`)
- Preserve original content unchanged after the injected header
- No guard yet — unconditional injection (guard added in Cycle 1.2)

**Approach:** In `assemble_phase_files()`, before `assembled_parts.append(content)`, prepend `\n### Phase {phase_num}:\n\n` to content unconditionally.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add header injection logic in the phase file loop (line ~473-489)
  Location hint: Inside `for i, phase_file in enumerate(phase_files):` loop, after content validation, before `assembled_parts.append(content)`

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseNumbering::test_assembly_injects_phase_headers_when_absent -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_inline.py -v`

---
