# Cycle 6.7

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.7: Update EXEMPT_SECTIONS

**RED Phase:**

**Test:** `test_exempt_sections_updated`
**Assertions:**
- After migration, EXEMPT_SECTIONS is empty set (no exempt sections remain)
- Validation runs on ALL sections (no skipping)
- Old exempt section names ("Behavioral Rules", "Technical Decisions") are not in EXEMPT_SECTIONS
- If index still has old exempt sections, they're validated like any other section

**Expected failure:** AssertionError — EXEMPT_SECTIONS still contains old section names

**Why it fails:** EXEMPT_SECTIONS constant not yet updated

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_exempt_sections_updated -v`

**GREEN Phase:**

**Implementation:** Update EXEMPT_SECTIONS constant.

**Behavior:**
- Set `EXEMPT_SECTIONS = set()` (empty — no exempt sections after migration)
- All sections validated equally
- Old section names no longer receive special treatment

**Approach:** Change constant value. May need to update in both checks.py and helpers.py if duplicated.

**Changes:**
- File: `src/claudeutils/validation/memory_index_helpers.py`
  Action: Set `EXEMPT_SECTIONS = set()`
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Same update if constant is duplicated here

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_exempt_sections_updated -v`
**Verify no regression:** `pytest tests/ -q`

# Phase 7: Key Compression Tool

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 0 (fuzzy)
**Files:** `agent-core/bin/compress-key.py`, `tests/test_when_compress_key.py`

**Design reference:** Key Compression Tool section

**Prior state:** Phase 0 provides `fuzzy.score_match()` and `fuzzy.rank_matches()` for uniqueness verification.

---
