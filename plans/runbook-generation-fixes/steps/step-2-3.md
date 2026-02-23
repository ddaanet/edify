# Cycle 2.3

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

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

**Execution note:** This is a regression guard — Cycle 2.2 is already implemented at this point. Verify that step-level model override still works after phase-model threading. This test should PASS; if it fails, Cycle 2.2 introduced a regression in `extract_step_metadata()`.

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
