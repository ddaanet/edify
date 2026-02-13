# Cycle 6.4

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.4: Collision detection

**RED Phase:**

**Test:** `test_collision_detection`
**Assertions:**
- Two entries `/when mock test` and `/when mock testing` both fuzzy-matching heading `"When Mock Testing"` → error "collision: multiple entries resolve to same heading"
- Two entries resolving to different headings → no collision error
- Error message identifies both colliding entries with line numbers

**Expected failure:** AssertionError — collisions not detected

**Why it fails:** Collision detection not yet implemented

**Verify RED:** `pytest tests/test_validation_memory_index.py::test_collision_detection -v`

**GREEN Phase:**

**Implementation:** Add collision detection.

**Behavior:**
- After fuzzy matching all entries to headings, check for heading duplication
- If multiple entries resolve to the same heading → collision error
- Report all colliding entries with line numbers and the shared heading

**Approach:** Build heading→entries reverse mapping. Any heading with >1 entry is a collision.

**Changes:**
- File: `src/claudeutils/validation/memory_index_checks.py`
  Action: Add collision detection after fuzzy matching
  Location hint: New check function or extension of orphan check

**Verify GREEN:** `pytest tests/test_validation_memory_index.py::test_collision_detection -v`
**Verify no regression:** `pytest tests/ -q`

---
