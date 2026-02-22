# Cycle 2.5

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.5: Missing model produces error (no haiku default)

**RED Phase:**

**Test:** `test_missing_model_produces_error`
**Setup:** Create a runbook (string or file) with:
- No `model:` in frontmatter (or no frontmatter at all)
- Phase header with no `model:` annotation: `### Phase 1: Core (type: tdd)`
- Step/cycle body with no `**Execution Model**:` field

Run the pipeline through `validate_and_create()`.

**Assertions:**
- `validate_and_create()` returns `False` (error condition)
- Captured stderr contains a string with "model" (e.g., "ERROR: No model specified for step 1.1")
- No step files are written to `steps/` (pipeline aborts before artifact generation)
- The pipeline does NOT silently produce step files with `**Execution Model**: haiku`

**Expected failure:** AssertionError — current code silently defaults to haiku everywhere. `validate_and_create()` returns `True` and step files have `**Execution Model**: haiku`.

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation::test_missing_model_produces_error -v`

---

**GREEN Phase:**

**Implementation:** Remove haiku fallback, add model validation.

**Behavior:**
- The priority chain becomes: step body > phase model > frontmatter model > ERROR
- If a step/cycle resolves to no model at any level, the pipeline errors
- Error message identifies which step(s) have no model

**Approach:** Multiple changes:
1. In `validate_and_create()`: after computing `phase_models` and `model` (frontmatter), validate that every step/cycle has a model. For each cycle: check `phase_models.get(cycle['major'])` or step body `**Execution Model**:` or frontmatter `model`. If none found, collect the step identifier. After loop, if any unresolved: print error and return `False`.
2. In `extract_step_metadata()`: change default parameter from `default_model='haiku'` to `default_model=None`. When `default_model` is None and no step-level model found, return `model: None` in metadata.
3. In `assemble_phase_files()`: if no phase declares a model, don't hardcode `model: haiku` in frontmatter. Omit the `model:` line or set to detected value only.
4. In `generate_agent_frontmatter()`: change default from `model='haiku'` to require explicit model parameter.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add model validation in `validate_and_create()` before artifact generation
  Location hint: After phase_models computation, before "Create directories" (line ~849)
- File: `agent-core/bin/prepare-runbook.py`
  Action: Change `extract_step_metadata()` default_model from 'haiku' to None
  Location hint: Function signature (line ~573)
- File: `agent-core/bin/prepare-runbook.py`
  Action: Update `assemble_phase_files()` to not hardcode haiku when no model detected
  Location hint: Frontmatter generation (line ~496-501)

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

Note: Existing `test_prepare_runbook_inline.py` tests use fixtures with `model: haiku` in frontmatter — they should continue to pass since haiku is explicitly specified. Only the *default* fallback to haiku is removed.

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
