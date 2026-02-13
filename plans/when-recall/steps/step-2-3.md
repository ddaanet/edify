# Cycle 2.3

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.3: Handle flat H2 files (workflow-core pattern)

**Prerequisite:** Read `agents/decisions/workflow-core.md:1-30` — understand flat H2 structure (13 H2 sections, no H3 nesting)

**RED Phase:**

**Test:** `test_flat_h2_file_ancestors`
**Assertions:**
- For H2 heading "Oneshot workflow pattern" in `workflow-core.md` (flat H2, no H3):
  - `compute_ancestors("Oneshot workflow pattern", "workflow-core.md", content)` returns:
    - `/when ..workflow-core.md` only (no parent heading — it IS top level)
- Heading hierarchy extraction produces flat list (all H2, no parent relationships among headings)

**Expected failure:** AssertionError — flat H2 headings incorrectly assigned parents or missing file link

**Why it fails:** Hierarchy extraction may not handle files where all headings are same level

**Verify RED:** `pytest tests/test_when_navigation.py::test_flat_h2_file_ancestors -v`

**GREEN Phase:**

**Implementation:** Handle edge case where all headings are H2 (no nesting).

**Behavior:**
- H2 headings have no parent heading (they ARE top level)
- Ancestors for H2 = just the file link
- No hierarchy relationships among sibling H2 headings

**Approach:** Stack-based parser naturally handles this — H2 pushes clear the stack, so no parent recorded.

**Changes:**
- File: `src/claudeutils/when/navigation.py`
  Action: Verify flat H2 handling works correctly (may need no code changes)
  Location hint: Hierarchy extraction and ancestor computation

**Verify GREEN:** `pytest tests/test_when_navigation.py::test_flat_h2_file_ancestors -v`
**Verify no regression:** `pytest tests/ -q`

---
