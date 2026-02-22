# Cycle 1.2

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.2: Assembly preserves existing phase headers

**RED Phase:**

**Test:** `test_assembly_preserves_existing_phase_headers`
**Setup:** Create 3 phase files in `tmp_path`:
- `runbook-phase-1.md`: contains `### Phase 1: Core behavior (type: tdd, model: sonnet)\n\n## Cycle 1.1: Test\n\n**RED Phase:**\nTest.\n**GREEN Phase:**\nImpl.\n**Stop/Error Conditions:** STOP if unexpected.`
- `runbook-phase-2.md`: contains `### Phase 2: Infrastructure (type: general)\n\n## Step 2.1: Setup\n\nSetup content.`
- `runbook-phase-3.md`: contains `### Phase 3: Cleanup (type: inline)\n\n- Clean up resources`
- All files already have `### Phase N:` headers

**Assertions:**
- Assembled content contains exactly one `### Phase 1:` occurrence (not duplicated)
- Assembled content contains exactly one `### Phase 2:` occurrence
- Assembled content contains exactly one `### Phase 3:` occurrence
- Original header text preserved (includes type/model metadata)

**Expected failure:** Depends on Cycle 1.1 implementation — if injection doesn't check for existing headers, will produce duplicate `### Phase 1:` lines.

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseNumbering::test_assembly_preserves_existing_phase_headers -v`

---

**GREEN Phase:**

**Implementation:** Guard header injection against existing headers.

**Behavior:**
- Before injecting `### Phase N:`, check if content already contains a matching `### Phase N:` header
- Use regex `^###? Phase\s+N:` to detect existing headers (consistent with `extract_sections()` pattern)
- Skip injection when header already present

**Approach:** Add regex check in the injection logic from Cycle 1.1. The check runs per-file, matching the phase number from the filename.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add guard condition to the header injection logic
  Location hint: Same injection point as Cycle 1.1 — wrap in `if not re.search(...)` guard

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseNumbering -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_inline.py -v`

---
