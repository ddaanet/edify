# Cycle 3.2

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.2: Step and cycle files include phase context section

**Prerequisite:** Read `generate_step_file()` (line ~687-713) and `generate_cycle_file()` (line ~716-740) — understand the header/content structure of generated files. Read `validate_and_create()` cycle loop (line ~880-886) and step loop (line ~888-898) — understand where generation calls happen.

**RED Phase:**

**Test:** `test_step_and_cycle_files_include_phase_context`
**Setup:** Create mixed runbook in `tmp_path` with:
- Phase 1 (TDD): header + preamble "Phase 1 prerequisites: module X exists." + Cycle 1.1
- Phase 2 (general): header + preamble "Phase 2 constraints: no breaking changes." + Step 2.1

Run full pipeline through `validate_and_create()`.

**Assertions:**
- Cycle file `steps/step-1-1.md` contains `## Phase Context` section
- Cycle file `steps/step-1-1.md` contains "Phase 1 prerequisites: module X exists."
- Step file `steps/step-2-1.md` contains `## Phase Context` section
- Step file `steps/step-2-1.md` contains "Phase 2 constraints: no breaking changes."
- `## Phase Context` appears AFTER the metadata header (`**Plan**:`, `**Execution Model**:`, `**Phase**:`) and BEFORE the step/cycle body content

**Expected failure:** AssertionError — current `generate_step_file()` and `generate_cycle_file()` don't produce `## Phase Context` sections

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext::test_step_and_cycle_files_include_phase_context -v`

---

**GREEN Phase:**

**Implementation:** Add `phase_context` parameter to both generation functions and thread from `validate_and_create()`.

**Behavior:**
- `generate_step_file()` and `generate_cycle_file()` accept optional `phase_context` string parameter
- When `phase_context` is non-empty (after stripping), inject `## Phase Context\n\n{phase_context}\n\n---\n` between the metadata header block and the step/cycle body content
- When `phase_context` is empty or None, no section is added

**Approach:**
1. Add `phase_context=''` parameter to `generate_step_file()` and `generate_cycle_file()`
2. In both functions, before the final `header_lines.extend(["", "---", "", <content>, ""])` call: if `phase_context.strip()`, insert `## Phase Context\n\n{phase_context}\n\n---\n` between the divider and the step/cycle content (split the extend if needed)
3. In `validate_and_create()`: call `phase_preambles = extract_phase_preambles(body)` (where `body` is the assembled content post-frontmatter). Pass `phase_preambles.get(cycle['major'], '')` to `generate_cycle_file()` and `phase_preambles.get(phase, '')` to `generate_step_file()`.

Note: `validate_and_create()` needs `body` (assembled content without frontmatter). Currently `main()` calls `parse_frontmatter()` which returns `body`. Add `body` as parameter to `validate_and_create()` or pass it through. Alternatively, call `extract_phase_preambles()` in `main()` and pass result — consistent with Phase 2's `phase_models` pattern.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `phase_context` parameter to `generate_step_file()` and `generate_cycle_file()`, inject section when non-empty
  Location hint: `generate_step_file()` (line ~687), `generate_cycle_file()` (line ~716)
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `phase_preambles` parameter to `validate_and_create()`, thread to generation calls
  Location hint: Function signature (line ~808), cycle loop (line ~880-886), step loop (line ~888-898)
- File: `agent-core/bin/prepare-runbook.py`
  Action: In `main()`, call `extract_phase_preambles(body)` and pass to `validate_and_create()`
  Location hint: After `extract_phase_models(body)` call, before `validate_and_create()` call

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

---
