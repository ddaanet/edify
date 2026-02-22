# Cycle 2.2

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

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
