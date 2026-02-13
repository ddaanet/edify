# Cycle 1.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.1: Parse `/when trigger | extras` format

**Prerequisite:** Read `src/claudeutils/recall/index_parser.py` — understand Pydantic BaseModel pattern for index entries

**RED Phase:**

**Test:** `test_parse_when_entry_basic`
**Assertions:**
- Parse line `/when writing mock tests | mock patch, test doubles` produces a WhenEntry with:
  - `operator == "when"`
  - `trigger == "writing mock tests"`
  - `extra_triggers == ["mock patch", "test doubles"]`
- Parse line `/how encode paths | path encoding` produces a WhenEntry with:
  - `operator == "how"`
  - `trigger == "encode paths"`
  - `extra_triggers == ["path encoding"]`

**Expected failure:** ImportError — `WhenEntry` and `parse_index` don't exist

**Why it fails:** Module `src/claudeutils/when/index_parser.py` not yet created

**Verify RED:** `pytest tests/test_when_index_parser.py::test_parse_when_entry_basic -v`

**GREEN Phase:**

**Implementation:** Create `index_parser.py` with `WhenEntry` model and `parse_index` function.

**Behavior:**
- `WhenEntry(BaseModel)` with fields: operator, trigger, extra_triggers, line_number, section
- `parse_index(index_path)` reads file, identifies `/when` and `/how` lines, parses into WhenEntry list
- Track current H2 section heading as context for each entry

**Approach:** Line-by-line parsing. Detect H2 headings for section context. Match `/when` or `/how` prefix. Split on `|` for trigger vs extras.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Create with WhenEntry BaseModel and parse_index function
  Location hint: New module

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_parse_when_entry_basic -v`
**Verify no regression:** `pytest tests/ -q`

---
