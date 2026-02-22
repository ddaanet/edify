# Cycle 2.4

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

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
