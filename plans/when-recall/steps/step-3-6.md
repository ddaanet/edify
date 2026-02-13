# Cycle 3.6

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.6: Output formatting (heading + content + navigation links)

**[Checkpoint: core resolver logic complete]**

**RED Phase:**

**Test:** `test_resolve_output_format`
**Assertions:**
- Full resolve output for trigger mode contains:
  - `"# When Writing Mock Tests"` (heading with `#` prefix)
  - Section content from decision file
  - `"Broader:"` section with ancestor links
  - `"Related:"` section with sibling links
- Sections separated by blank lines
- Heading uses H1 format (`#`) regardless of source level (H2/H3 in decision file)

**Expected failure:** AssertionError — output doesn't include navigation or formatting

**Why it fails:** Output formatting not yet combining content + navigation

**Verify RED:** `pytest tests/test_when_resolver.py::test_resolve_output_format -v`

**GREEN Phase:**

**Implementation:** Combine content extraction with navigation.

**Behavior:**
- Format heading as H1 (`# When/How to <Heading Text>`)
- Append section content
- Compute ancestors and siblings via navigation module
- Append formatted navigation links
- Return complete formatted string

**Approach:** Call navigation.compute_ancestors() and compute_siblings(), format_navigation(), concatenate.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Integrate navigation module output into resolve return value
  Location hint: End of `resolve` function, after content extraction

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_resolve_output_format -v`
**Verify no regression:** `pytest tests/ -q`

---
