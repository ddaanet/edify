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
**Setup:** Assembled content string with phase headers and preamble text:
```
### Phase 1: Core behavior (type: tdd, model: sonnet)

RC-1 fix. Prerequisites: foo module exists.

**Constraints:** No backward-incompatible changes.

## Cycle 1.1: Test thing

Cycle content.

### Phase 2: Infrastructure (type: general)

Setup database connections. Verify connectivity.

## Step 2.1: Configure DB

Step content.

### Phase 3: Cleanup (type: tdd, model: sonnet)

## Cycle 3.1: Clean state

Cycle content with no preamble above.
```

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
2. In both functions, after `header_lines.extend(["", "---", ""])` and before appending step/cycle content: if `phase_context.strip()`, insert the `## Phase Context` section
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

## Cycle 3.3: Phase context preserved when phase has no preamble

**RED Phase:**

**Test:** `test_no_phase_context_when_preamble_empty`
**Setup:** Create runbook with:
- Phase 1 header immediately followed by cycle header (no preamble):
  ```
  ### Phase 1: Core (type: tdd, model: sonnet)
  ## Cycle 1.1: Direct start
  ```
- Phase 2 header with preamble (control case):
  ```
  ### Phase 2: Extra (type: general)

  Some preamble here.

  ## Step 2.1: Thing
  ```

Run full pipeline.

**Assertions:**
- `extract_phase_preambles()` returns empty string for Phase 1
- Generated cycle file `steps/step-1-1.md` does NOT contain `## Phase Context`
- Generated step file `steps/step-2-1.md` DOES contain `## Phase Context` with "Some preamble here." (control)

**Expected failure:** Depends on 3.2 implementation — if it doesn't handle empty preamble gracefully, may produce empty `## Phase Context` section or crash.

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext::test_no_phase_context_when_preamble_empty -v`

---

**GREEN Phase:**

**Implementation:** Guard against empty preamble in generation functions.

**Behavior:**
- `extract_phase_preambles()` returns empty string for phases with no content between header and first step/cycle
- `generate_step_file()` and `generate_cycle_file()` check `phase_context.strip()` before injecting section
- Empty or whitespace-only preamble → no `## Phase Context` section in output

**Approach:** The guard should already be in place from Cycle 3.2's implementation (which specifies "when non-empty"). If the 3.2 implementation uses `if phase_context.strip():` before injection, this test passes immediately. If not, add the guard.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Ensure empty-preamble guard in `generate_step_file()` and `generate_cycle_file()`
  Location hint: Phase context injection block in both functions

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`
