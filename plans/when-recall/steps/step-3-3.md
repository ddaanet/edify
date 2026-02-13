# Cycle 3.3

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.3: Section mode — global unique heading lookup

**Prerequisite:** Read `agents/decisions/workflow-core.md:1-20` and `agents/decisions/testing.md:1-20` — understand heading structure across files

**RED Phase:**

**Test:** `test_section_mode_resolves`
**Assertions:**
- Given decision files with unique heading `"Mock Patching Pattern"`:
  - `resolve("when", ".Mock Patching Pattern", index_path, decisions_dir)` returns string containing:
    - Exact heading text "Mock Patching Pattern"
    - Content between that heading and next same-level heading (exclusive boundary)
    - Does NOT contain content from adjacent sections (boundary verification)
- Heading lookup is case-insensitive: `.mock patching pattern` also works
- Ambiguous heading (exists in multiple files) raises `ResolveError` with file disambiguation

**Expected failure:** AssertionError — section mode not implemented

**Why it fails:** Section mode resolution not yet in resolver

**Verify RED:** `pytest tests/test_when_resolver.py::test_section_mode_resolves -v`

**GREEN Phase:**

**Implementation:** Implement section mode.

**Behavior:**
- Scan all `.md` files in decisions_dir
- Build heading→file mapping (all H2+ headings)
- Lookup query heading (case-insensitive)
- If unique match: extract content
- If multiple matches: raise ResolveError with disambiguation info
- If no match: raise ResolveError (handled in 3.8)

**Approach:** Walk decision files, collect headings with file paths. Dict lookup.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Implement section mode — heading collection across files, lookup, uniqueness check
  Location hint: Within `resolve` function, section mode branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_section_mode_resolves -v`
**Verify no regression:** `pytest tests/ -q`

---
