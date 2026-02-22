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

## Cycle 2.1: Extract phase model from phase header metadata

**RED Phase:**

**Test:** `test_extract_phase_models_from_headers`
**Setup:** Assembled content string with 3 phases:
- Phase 1 header: `### Phase 1: Core behavior (type: tdd, model: sonnet)` followed by `Cycle 1.1: Test thing`
- Phase 2 header: `### Phase 2: Infrastructure (type: general)` followed by `Step 2.1: Setup`
- Phase 3 header: `### Phase 3: Refinement (type: tdd, model: opus)` followed by `Cycle 3.1: Refine`

**Assertions:**
- `extract_phase_models(content)` returns `{1: 'sonnet', 3: 'opus'}`
- Phase 2 (no model annotation) is absent from returned dict
- Function handles mixed parenthetical formats: `(type: tdd, model: sonnet)`, `(model: opus, type: tdd)`, `(type: general)` (no model)

**Expected failure:** NameError — `extract_phase_models` does not exist

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation::test_extract_phase_models_from_headers -v`

---

**GREEN Phase:**

**Implementation:** New `extract_phase_models()` function.

**Behavior:**
- Parse phase headers matching `### Phase N: ... (... model: MODEL ...)`
- Extract phase number and model string
- Return dict `{phase_num: model_string}`
- Phases without `model:` annotation are omitted from dict (caller uses frontmatter default)
- Model values normalized to lowercase

**Approach:** Regex on phase header lines. Pattern: `^###? Phase\s+(\d+):.*model:\s*(\w+)` with case-insensitive model match.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `extract_phase_models(content)` function
  Location hint: After `extract_sections()` (line ~427), before `assemble_phase_files()` (line ~430)

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation::test_extract_phase_models_from_headers -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

---

## Cycle 2.2: Phase model overrides frontmatter default

**Prerequisite:** Read `validate_and_create()` (line ~808-929) — understand how `model` is currently derived from `metadata.get('model', 'haiku')` and passed to `generate_cycle_file()` / `generate_step_file()`.

**RED Phase:**

**Test:** `test_phase_model_overrides_frontmatter`
**Setup:** Create mixed runbook in `tmp_path` with:
- Frontmatter: `model: haiku`
- Phase 1 header: `### Phase 1: Core (type: tdd, model: sonnet)`
- Cycle 1.1 in Phase 1 with NO explicit `**Execution Model**:` in body

Run full pipeline: `parse_frontmatter()` → `extract_sections()` → `extract_cycles()` → `validate_and_create()`

**Assertions:**
- Generated cycle file `steps/step-1-1.md` contains `**Execution Model**: sonnet` (not haiku)
- Phase model (sonnet) overrides frontmatter model (haiku)

**Expected failure:** AssertionError — step file has `**Execution Model**: haiku` (current code uses frontmatter default for all steps)

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation::test_phase_model_overrides_frontmatter -v`

---

**GREEN Phase:**

**Implementation:** Thread phase models through the artifact generation pipeline.

**Behavior:**
- `validate_and_create()` calls `extract_phase_models()` on assembled content
- Each cycle/step generation call receives the phase-level model as its default
- Priority: step body `**Execution Model**:` > phase model > frontmatter `model:`

**Approach:** Three changes in `validate_and_create()`:
1. After `model = metadata.get('model', 'haiku')` (line ~866): call `phase_models = extract_phase_models(assembled_content)`. This requires passing assembled content to `validate_and_create()` — add parameter or extract from sections.
2. In cycle generation loop (line ~880-886): `default_model = phase_models.get(cycle['major'], model)` → pass to `generate_cycle_file()`
3. In step generation loop (line ~888-898): `default_model = phase_models.get(phase, model)` → pass to `generate_step_file()`

Note: `validate_and_create()` needs access to the assembled content for `extract_phase_models()`. Options: (a) pass assembled content as new parameter, (b) call `extract_phase_models()` in `main()` and pass result. Option (b) is cleaner — add `phase_models` parameter to `validate_and_create()`.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `phase_models` parameter to `validate_and_create()`, use in cycle/step generation loops
  Location hint: Function signature (line ~808), cycle loop (line ~880-886), step loop (line ~888-898)
- File: `agent-core/bin/prepare-runbook.py`
  Action: In `main()`, call `extract_phase_models(body)` and pass result to `validate_and_create()`
  Location hint: After `extract_cycles(body)` (line ~980), before `validate_and_create()` call (line ~1038)

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

---

## Cycle 2.3: Step-level model overrides phase model [REGRESSION]

**Prerequisite:** Read `extract_step_metadata()` (line ~573-606) — understand how `**Execution Model**:` in step body is parsed and returned, falling back to `default_model` parameter.

**[REGRESSION] Test Phase:**

**Test:** `test_step_model_overrides_phase_model`
**Setup:** Create mixed runbook in `tmp_path` with:
- Frontmatter: `model: haiku`
- Phase 1 header: `### Phase 1: Core (type: tdd, model: sonnet)`
- Cycle 1.1 in Phase 1 with explicit `**Execution Model**: opus` in body

Run full pipeline.

**Assertions:**
- Generated cycle file `steps/step-1-1.md` contains `**Execution Model**: opus` (not sonnet, not haiku)
- Step-level model (opus) overrides phase model (sonnet) which overrides frontmatter (haiku)

**Execution note:** Write this test before implementing Cycle 2.2. This is a regression guard: `extract_step_metadata()` already returns the body-level model correctly, but Cycle 2.2's phase-model threading could inadvertently overwrite it. This test catches that regression. It passes against pre-2.2 code; verify it still passes after 2.2 GREEN.

**Expected failure (if 2.2 introduces regression):** `AssertionError: 'sonnet' != 'opus'` — step file contains phase model instead of step body model.

**Verify after 2.2 GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation::test_step_model_overrides_phase_model -v`

---

**GREEN Phase:**

**Implementation:** No code changes expected.

**Behavior:**
- `extract_step_metadata(content, default_model)` already parses step-level `**Execution Model**:` via regex
- When present in step body, the parsed model is returned regardless of `default_model`
- With 2.2's threading, `default_model` is now the phase model — but the regex match takes priority
- Priority chain: step body regex match > default_model (phase model) > function parameter default

**If tests fail:** `extract_step_metadata()` (line 573) is the investigation target — verify regex match takes priority over default_model in all code paths.

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

---

## Cycle 2.4: Agent frontmatter uses detected model (not hardcoded haiku)

**Prerequisite:** Read `assemble_phase_files()` (line ~430-515) — understand the hardcoded `model: haiku` at line ~498 in TDD frontmatter generation.

**RED Phase:**

**Test:** `test_assembly_frontmatter_uses_detected_model`
**Setup:** Create phase files in `tmp_path`:
- `runbook-phase-1.md`: TDD phase with header `### Phase 1: Core (type: tdd, model: sonnet)` and a cycle

Call `assemble_phase_files(directory)`.

**Assertions:**
- Returned assembled content starts with frontmatter containing `model: sonnet` (not `model: haiku`)
- Parse frontmatter from assembled content: `metadata['model'] == 'sonnet'`

**Expected failure:** AssertionError — assembled frontmatter has `model: haiku` (hardcoded at line ~498)

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation::test_assembly_frontmatter_uses_detected_model -v`

---

**GREEN Phase:**

**Implementation:** Replace hardcoded `model: haiku` with detected phase model.

**Behavior:**
- After assembling content, call `extract_phase_models()` on the assembled body
- Use first phase's model (lowest phase number) for frontmatter `model:` field
- If no phase has an explicit model, use frontmatter model from first phase file (if any)

**Approach:** In `assemble_phase_files()`, after `assembled_body = '\n'.join(assembled_parts)` (line ~505):
1. Call `extract_phase_models(assembled_body)` to get phase models
2. Determine frontmatter model: first phase's model from dict, or leave as `model: haiku` only if no phases declare a model (will be caught by 2.5's validation)
3. Replace hardcoded `model: haiku` in TDD frontmatter with detected model

Also check general-runbook path (line ~503: `frontmatter = ""`) — general runbooks assembled from phase files currently get no frontmatter. If phase files declare models, ensure they're propagated.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Replace hardcoded `model: haiku` with detected model in `assemble_phase_files()`
  Location hint: After `assembled_body` construction (line ~505), modify frontmatter generation (line ~496-501)

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

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
