# Cycle 1.3

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

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

**Expected failure:** With current code (no phase header injection in assembly), phases 3-5 will have incorrect `step_phases` mappings (C2 reproduction). Orchestrator plan will show misnumbered PHASE_BOUNDARY entries (M1) and potentially interleaved items (M2).

Note: This test uses the `MIXED_RUNBOOK_5PHASE` fixture directly (not phase files), so it tests `extract_sections()` phase detection on content that already has phase headers. The fixture must include `### Phase N:` headers to be realistic. The verification validates that the parsing pipeline produces correct downstream results.

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

### Phase 2: Model propagation (type: tdd, model: sonnet)

RC-1 fix. D-1 model priority chain: step body > phase-level > frontmatter > ERROR (no haiku default).

**Post-Phase-1 state:** Assembled content contains `### Phase N:` headers (injected by `assemble_phase_files()` when absent). All cycles in this phase can rely on phase headers being present in assembled content.

**Prerequisites:**
- Phase 1 complete (phase headers present in assembled content)
- `agent-core/bin/prepare-runbook.py` — target file
- `tests/test_prepare_runbook_mixed.py` — test module (created in Phase 1)

**Completion validation:**
- All 5 cycles pass (RED fails then GREEN passes)
- `just test tests/test_prepare_runbook_mixed.py` — all tests pass (Phase 1 + Phase 2)
- No regressions: `just test tests/test_prepare_runbook_inline.py`
- Model priority chain verified end-to-end: frontmatter → phase → step override → missing model error

---
