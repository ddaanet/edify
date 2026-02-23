### Phase 3: Phase context extraction (type: tdd, model: sonnet)

RC-2 fix. D-2: phase preamble → `## Phase Context` section in step/cycle files.

**Post-Phase-1 state:** Assembled content contains `### Phase N:` headers, enabling reliable phase boundary detection for preamble extraction.

**Prerequisites:**
- Phase 1 complete (phase headers present in assembled content)
- `agent-core/bin/prepare-runbook.py` — target file
- `tests/test_prepare_runbook_mixed.py` — test module (with Phase 1 and 2 tests)

**Completion validation:**
- All 3 cycles pass (RED fails then GREEN passes)
- `just test tests/test_prepare_runbook_mixed.py` — all tests pass (Phases 1-3)
- No regressions: `just test tests/test_prepare_runbook_inline.py`
- Step/cycle files contain phase preamble content; phases without preamble produce no `## Phase Context` section

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

## Cycle 3.2: Step and cycle files include phase context section

**Prerequisite:** Read `generate_step_file()` (line ~687-713) and `generate_cycle_file()` (line ~716-740) — understand the header/content structure of generated files. Read `validate_and_create()` cycle loop (line ~880-886) and step loop (line ~888-898) — understand where generation calls happen.

**RED Phase:**

**Test:** `test_step_and_cycle_files_include_phase_context`
**Setup:** Create mixed runbook in `tmp_path` with frontmatter `model: sonnet`:
- Phase 1 (TDD, model: sonnet): header + preamble "Phase 1 prerequisites: module X exists." + Cycle 1.1
- Phase 2 (general, model: sonnet): header + preamble "Phase 2 constraints: no breaking changes." + Step 2.1

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
  ### Phase 2: Extra (type: general, model: sonnet)

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
