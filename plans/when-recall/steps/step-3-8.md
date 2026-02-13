# Cycle 3.8

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.8: Error handling — section not found

**RED Phase:**

**Test:** `test_section_not_found_lists_headings`
**Assertions:**
- `resolve("when", ".Nonexistent Section", index_path, decisions_dir)` raises `ResolveError`
- Error message contains `"Section 'Nonexistent Section' not found."`
- Error message contains `"Available:"` followed by list of actual heading names
- Available headings formatted as `.HeadingName` (one per line)

**Expected failure:** ResolveError raised but without available headings list

**Why it fails:** Section-not-found error doesn't list alternatives

**Verify RED:** `pytest tests/test_when_resolver.py::test_section_not_found_lists_headings -v`

**GREEN Phase:**

**Implementation:** Add section-not-found error with available headings.

**Behavior:**
- When heading lookup fails: raise ResolveError
- Collect all headings from all decision files
- Format: `"Section '<name>' not found. Available:\n  .Heading1\n  .Heading2"`
- Limit to first 10 suggestions (prevent overwhelming output)

**Approach:** Use already-collected heading mapping from section mode. Format as `.` prefixed list.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Add section-not-found error formatting
  Location hint: Section mode error branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_section_not_found_lists_headings -v`
**Verify no regression:** `pytest tests/ -q`

---
