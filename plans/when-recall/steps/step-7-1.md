# Cycle 7.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.1: Load heading corpus from decision files

**RED Phase:**

**Test:** `test_load_heading_corpus`
**Assertions:**
- Given `agents/decisions/` directory with `.md` files:
  - Returns list of heading strings from all files
  - Includes both H2 and H3 headings
  - Excludes structural headings (`.` prefix)
  - Heading count > 0 for non-empty directory
- Empty directory → returns empty list

**Expected failure:** ImportError — compress-key module doesn't exist

**Why it fails:** Module not yet created

**Verify RED:** `pytest tests/test_when_compress_key.py::test_load_heading_corpus -v`

**GREEN Phase:**

**Implementation:** Create compress-key module with heading corpus loading.

**Behavior:**
- Scan all `.md` files in decisions directory
- Extract H2+ headings (regex: `^#{2,}\s+(.+)$`)
- Filter out structural headings (starting with `.`)
- Return flat list of heading text strings

**Approach:** Glob + regex extraction. Can live in `src/claudeutils/when/compress.py` or directly in bin script.

**Changes:**
- File: `src/claudeutils/when/compress.py`
  Action: Create module with `load_heading_corpus(decisions_dir)` function
  Location hint: New module
- File: `tests/test_when_compress_key.py`
  Action: Create test file

**Verify GREEN:** `pytest tests/test_when_compress_key.py::test_load_heading_corpus -v`
**Verify no regression:** `pytest tests/ -q`

---
