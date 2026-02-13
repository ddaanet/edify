# Cycle 2.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.1: Extract heading hierarchy from file content

**Prerequisite:** Read `agents/decisions/testing.md:1-30` — understand decision file heading structure (structural `.` prefix, semantic headings, H2/H3 nesting)

**RED Phase:**

**Test:** `test_extract_heading_hierarchy`
**Assertions:**
- Given markdown content with `## Section A` containing `### Sub A1` and `### Sub A2`:
  - Returns hierarchy mapping `"Sub A1" → parent "Section A"`, `"Sub A2" → parent "Section A"`
- Given nested `## A` → `### B` → `#### C`:
  - Returns `"C" → parent "B"`, `"B" → parent "A"`
- Returns heading level for each heading (H2=2, H3=3, H4=4)

**Expected failure:** ImportError — `navigation` module doesn't exist

**Why it fails:** Module `src/claudeutils/when/navigation.py` not yet created

**Verify RED:** `pytest tests/test_when_navigation.py::test_extract_heading_hierarchy -v`

**GREEN Phase:**

**Implementation:** Create `navigation.py` with heading hierarchy extraction.

**Behavior:**
- Parse markdown content line by line
- Track heading stack (H2 → H3 → H4)
- Build parent mapping: each heading maps to its nearest higher-level ancestor
- Return structured hierarchy (dict of heading → HeadingInfo with parent, level, line_number)

**Approach:** Stack-based parser. Push heading when level increases, pop when level decreases or equals.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Create module with heading hierarchy extraction function
  Location hint: New module

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_extract_heading_hierarchy -v`
**Verify no regression:** `pytest tests/ -q`

---
