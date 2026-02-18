# Cycle 5.1

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

### Cycle 5.1: Section identification via find_section_bounds()

**Prerequisite:** Read current _resolve_session_md_conflict() implementation (merge.py lines 58-113) and find_section_bounds() (session.py lines 85-115).

**RED Phase:**

**Test:** `test_section_identification`
**Assertions:**
- find_section_bounds(content, "Pending Tasks") returns tuple (2, 8) for content with Pending Tasks at line 2, next section at line 8
- find_section_bounds(content, "Worktree Tasks") returns tuple (9, 14) for section at line 9
- find_section_bounds(content, "Blockers / Gotchas") returns tuple (15, 20) for section with slash in name
- find_section_bounds(content, "Nonexistent") returns None
- Section at EOF: returns (N, len(lines)) where N is section start line

**Expected failure:** Test passes (find_section_bounds already exists) OR new test reveals edge cases

**Why it might pass:** find_section_bounds() already implemented in Phase 3 worktree-update

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_section_identification -v`

**GREEN Phase:**

**Implementation:** Use existing find_section_bounds(), add test coverage for merge use cases

**Behavior:**
- Verify find_section_bounds() works with all section names from D-5 table
- Test edge cases: sections at EOF, consecutive sections, missing sections
- Confirm existing implementation handles slash in "Blockers / Gotchas"

**Approach:** Test-only cycle if function works; fix if edge cases fail

**Changes:**
- File: `tests/test_worktree_merge_sections.py`
  Action: Create tests for all D-5 section names
  Location hint: New file, test each section type

- File: `src/claudeutils/worktree/session.py` (if needed)
  Action: Fix edge cases found by tests
  Location hint: find_section_bounds() function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_section_identification -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---
