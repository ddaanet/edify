### Phase 1: Phase numbering fix (type: tdd, model: sonnet)

RC-3 fix. `assemble_phase_files()` injects `### Phase N:` headers from filenames when absent. Fixes C2 (off-by-one), M1 (PHASE_BOUNDARY misnumbered), M2 (interleaving).

**Prerequisites:**
- `agent-core/bin/prepare-runbook.py` exists (source file)
- `tests/test_prepare_runbook_inline.py` exists (reference for test patterns)

**Completion validation:**
- All 3 cycles pass (RED fails then GREEN passes)
- `just test tests/test_prepare_runbook_mixed.py` — all tests pass
- No regressions: `just test tests/test_prepare_runbook_inline.py` — existing 7 tests pass

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

## Cycle 1.3: Downstream phase metadata and orchestrator plan correct (verification)

**Prerequisite:** Read `extract_sections()` (line ~298-427) — understand phase detection via `line_to_phase` mapping and `phase_pattern` regex. Read `generate_default_orchestrator()` (line ~743-805) — understand item sorting and PHASE_BOUNDARY generation.

**RED Phase:**

**Test:** `test_mixed_runbook_phase_metadata_and_orchestrator_correct`
**Setup:** Create a `MIXED_RUNBOOK_5PHASE` string fixture with 5 phases:
- Phase 1: 2 general steps (model: sonnet) — `## Step 1.1:`, `## Step 1.2:`
- Phase 2: 2 TDD cycles (model: sonnet) — `## Cycle 2.1:`, `## Cycle 2.2:`
- Phase 3: 1 general step (no explicit model) — `## Step 3.1:`
- Phase 4: 1 TDD cycle (model: opus) — `## Cycle 4.1:`
- Phase 5: inline — `(type: inline)`

Parse with `parse_frontmatter()`, `extract_sections()`, `extract_cycles()`.

**Assertions (phase metadata):**
- `step_phases['1.1'] == 1` and `step_phases['1.2'] == 1`
- `step_phases['3.1'] == 3`
- Cycle 2.1 has `major == 2`, Cycle 2.2 has `major == 2`
- Cycle 4.1 has `major == 4`
- `inline_phases` contains key `5`

**Assertions (orchestrator plan):**
- Generate orchestrator plan via `generate_default_orchestrator()`
- PHASE_BOUNDARY for phase 1 mentions "phase 1" (not phase 2 or 3)
- PHASE_BOUNDARY for phase 2 mentions "phase 2"
- Items appear in phase order: all phase-1 items before phase-2, phase-2 before phase-3, etc.
- No interleaving: consecutive items within same phase have monotonically increasing minor numbers

**Expected outcome (verification):** This test uses the `MIXED_RUNBOOK_5PHASE` fixture directly (not phase files) with correct `### Phase N:` headers already present. The test should PASS in RED — it verifies that `extract_sections()` parsing produces correct downstream results when headers are present. Passing confirms header injection from Cycle 1.1 is the complete fix for C2/M1/M2. If this test fails, investigate `extract_sections()` parsing independent of header injection.

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseNumbering::test_mixed_runbook_phase_metadata_and_orchestrator_correct -v`

---

**GREEN Phase:**

**Implementation:** No additional code changes expected — header injection from Cycle 1.1 fixes the root cause.

**Behavior:**
- With `### Phase N:` headers present in assembled content (either from source files or injected), `extract_sections()` `line_to_phase` mapping correctly tracks phase boundaries
- `generate_default_orchestrator()` receives correct `step_phases`, producing correctly numbered PHASE_BOUNDARY entries and non-interleaved items

**If tests fail:** Investigation targets:
- `extract_sections()` phase detection (line ~320-332): verify `phase_pattern` regex matches injected headers
- `generate_default_orchestrator()` sorting (line ~785): verify sort key produces correct ordering with correct phase numbers

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseNumbering -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_inline.py -v`
