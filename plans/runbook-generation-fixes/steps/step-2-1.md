# Cycle 2.1

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

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
