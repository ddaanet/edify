# Cycle 2.2

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.2: Compute ancestor headings (H4→H3→H2→file)

**RED Phase:**

**Test:** `test_compute_ancestors`
**Assertions:**
- For H3 heading "Mock Patching Pattern" under H2 "Test Organization" in `testing.md`:
  - `compute_ancestors("Mock Patching Pattern", "testing.md", content)` returns:
    - `/when .Test Organization` (parent H2)
    - `/when ..testing.md` (file link, always last)
- For H4 heading under H3 under H2:
  - Returns grandparent H2, parent H3, and file link (3 ancestors)
- For H2 heading (top-level):
  - Returns only file link (1 ancestor)

**Expected failure:** AttributeError — `compute_ancestors` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_navigation.py::test_compute_ancestors -v`

**GREEN Phase:**

**Implementation:** Create `compute_ancestors` function.

**Behavior:**
- Walk up heading hierarchy from target heading
- Collect all ancestor headings as `/when .SectionTitle` links
- Always append `..filename.md` as final link
- Skip the heading itself (only ancestors)

**Approach:** Use hierarchy from 2.1. Follow parent chain upward, collect links.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Add `compute_ancestors(heading, file_path, file_content)` function
  Location hint: After hierarchy extraction

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_compute_ancestors -v`
**Verify no regression:** `pytest tests/ -q`

---
