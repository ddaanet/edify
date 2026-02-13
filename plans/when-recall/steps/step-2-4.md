# Cycle 2.4

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.4: Structural heading detection (skip `.` prefix)

**RED Phase:**

**Test:** `test_structural_headings_skipped_as_nav_targets`
**Assertions:**
- Given content with `## .Test Organization` (structural, `.` prefix) containing `### Mock Patching Pattern` (semantic):
  - `compute_ancestors("Mock Patching Pattern", "testing.md", content)` returns:
    - `/when ..Test Organization` (structural parent included in ancestry)
    - `/when ..testing.md` (file link)
  - HeadingInfo for ".Test Organization" has `is_structural=True` flag
- Given 2 WhenEntry objects: one under semantic H2, one under structural H2 `.Test Organization`:
  - `compute_siblings` for entry under structural heading returns empty list (structural headings excluded from sibling grouping)
- Structural headings ARE traversed for ancestry (parent chain walks through them)

**Expected failure:** AssertionError — structural headings treated as regular semantic headings

**Why it fails:** No `.` prefix detection in heading classification

**Verify RED:** `pytest tests/test_when_navigation.py::test_structural_headings_skipped_as_nav_targets -v`

**GREEN Phase:**

**Implementation:** Detect and handle structural headings.

**Behavior:**
- Headings starting with `.` after `#+ ` are structural (organizational)
- Structural headings still participate in hierarchy (they ARE parent nodes)
- Ancestor links for structural headings still generated (agent can navigate up through them)
- Structural headings excluded from sibling computation (they're containers, not content)

**Approach:** Check if heading text starts with `.` after stripping `#` prefix. Flag in HeadingInfo.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Add structural heading detection (`.` prefix) and flag in hierarchy data
  Location hint: Heading parsing logic

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_structural_headings_skipped_as_nav_targets -v`
**Verify no regression:** `pytest tests/ -q`

---
