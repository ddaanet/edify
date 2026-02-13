# Cycle 2.5

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.5: Compute sibling entries (requires WhenEntry structures)

**RED Phase:**

**Test:** `test_compute_siblings`
**Assertions:**
- Given 3 WhenEntry objects all under same parent H2 "Test Organization":
  - Entry 1: trigger "mock patching pattern", section "Mock Patching Pattern"
  - Entry 2: trigger "testing strategy", section "Testing Strategy"
  - Entry 3: trigger "success metrics", section "Success Metrics"
  - `compute_siblings("Mock Patching Pattern", content, entries)` returns:
    - `/when testing strategy`
    - `/when success metrics`
  - The target heading itself ("mock patching pattern") is NOT included in siblings
- Entries under different parent headings are NOT included
- Empty list if heading has no siblings with index entries

**Expected failure:** AttributeError — `compute_siblings` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_navigation.py::test_compute_siblings -v`

**GREEN Phase:**

**Implementation:** Create `compute_siblings` function.

**Behavior:**
- Find the parent heading of the target heading
- Find all other headings under the same parent that have corresponding WhenEntry objects
- Return their triggers as `/when <trigger>` links
- Exclude the target heading itself

**Approach:** Map entries to their containing headings via hierarchy. Filter to same-parent group.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Add `compute_siblings(heading, file_content, index_entries)` function
  Location hint: After `compute_ancestors`

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_compute_siblings -v`
**Verify no regression:** `pytest tests/ -q`

---
