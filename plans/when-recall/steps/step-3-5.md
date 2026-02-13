# Cycle 3.5

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.5: Section content extraction from decision file

**Prerequisite:** Read `src/claudeutils/when/navigation.py` — understand heading hierarchy patterns and section boundary detection (flat H2 vs nested H2/H3)

**RED Phase:**

**Test:** `test_section_content_extraction`
**Assertions:**
- Given file with `### Heading A` followed by content, then `### Heading B`:
  - Extract content for "Heading A" returns everything between `### Heading A` and `### Heading B` (exclusive)
- Last heading in file: content extends to EOF
- Nested headings: `## Parent` with `### Child` — extracting "Child" gets Child's content only (not sibling content)
- Flat H2 file (workflow-core pattern): extracting H2 heading gets content until next H2

**Expected failure:** AssertionError — content extraction not working correctly

**Why it fails:** Section boundary detection not yet implemented

**Verify RED:** `pytest tests/test_when_resolver.py::test_section_content_extraction -v`

**GREEN Phase:**

**Implementation:** Add section content extraction.

**Behavior:**
- Find target heading line in file content
- Collect all lines until next heading of same or higher level
- Return collected content (excluding the heading line itself)
- Handle both nested (H2/H3) and flat (all H2) structures

**Approach:** Find heading line, scan forward until next heading at same or lower level number. Slice content.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Add `_extract_section_content(heading, file_content)` helper function
  Location hint: Private helper, before `resolve`

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_section_content_extraction -v`
**Verify no regression:** `pytest tests/ -q`

---
