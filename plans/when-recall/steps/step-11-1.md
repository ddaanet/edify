# Cycle 11.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 11

---

## Cycle 11.1: Update recall index parser for `/when` format

**Prerequisite:** Read `src/claudeutils/recall/index_parser.py` — understand `IndexEntry` model and `parse_memory_index()` function (already read in Phase 0.5, re-read for implementation details)

**RED Phase:**

**Test:** `test_recall_parser_when_format`
**Assertions:**
- `parse_memory_index(index_with_when_format)` returns list of `IndexEntry` objects
- Entry `/when writing mock tests | mock patch, test doubles` under `## agents/decisions/testing.md`:
  - `key == "writing mock tests"` (trigger becomes key)
  - `description == ""` (no description in new format — or derive from heading)
  - `referenced_file == "agents/decisions/testing.md"` (from H2 section)
  - `keywords` includes "writing", "mock", "tests", "patch", "doubles" (from trigger + extras)
- Entry count matches `/when` and `/how` line count
- Old em-dash format entries → skipped (not parsed)

**Expected failure:** AssertionError — parser fails on `/when` format

**Why it fails:** `parse_memory_index()` expects em-dash entries (` — ` split at line 141), doesn't detect `/when` or `/how` prefix format

**Verify RED:** `pytest tests/test_recall_index_parser.py::test_recall_parser_when_format -v`

**GREEN Phase:**

**Implementation:** Update `parse_memory_index` to handle `/when` format.

**Behavior:**
- Detect `/when` and `/how` prefixed lines instead of em-dash lines
- Extract key from trigger text
- Extract keywords from trigger + extra triggers (not key + description)
- Preserve section tracking from H2 headings
- Keep IndexEntry model compatible (key, description, referenced_file, section, keywords)
- Description field: empty string or trigger text (backward compatible)

**Approach:** Replace `" — " in line` check with `/when ` or `/how ` prefix check. Extract trigger as key, extras as keyword source.

**Changes:**
- File: `src/claudeutils/recall/index_parser.py`
  Action: Update entry detection from em-dash to `/when` prefix, update keyword extraction
  Location hint: Main parsing loop (lines 117-167)

**Verify GREEN:** `pytest tests/test_recall_index_parser.py::test_recall_parser_when_format -v`
**Verify no regression:** `pytest tests/ -q`

---
