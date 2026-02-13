# Phase 1: Index Parser

**Type:** TDD
**Model:** haiku
**Dependencies:** None (Pydantic only)
**Files:** `src/claudeutils/when/index_parser.py`, `tests/test_when_index_parser.py`

**Design reference:** Index Format section, D-1 (Two-field format)
**Existing pattern:** `src/claudeutils/recall/index_parser.py` — Pydantic BaseModel pattern for entry parsing

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

## Cycle 1.2: Extract operator (when/how)

**RED Phase:**

**Test:** `test_operator_extraction`
**Assertions:**
- Line starting with `/when ` extracts operator `"when"`
- Line starting with `/how ` extracts operator `"how"`
- Line starting with `/what ` is skipped (not a valid operator)
- Line starting with bare text (no `/` prefix) is skipped

**Expected failure:** AssertionError — non-when/how lines incorrectly parsed or valid lines rejected

**Why it fails:** Operator validation not yet implemented (or only partial from 1.1)

**Verify RED:** `pytest tests/test_when_index_parser.py::test_operator_extraction -v`

**GREEN Phase:**

**Implementation:** Add operator validation to parser.

**Behavior:**
- Only lines starting with `/when ` or `/how ` are valid entries
- All other lines (including `/what`, `/why`, bare text, headers) are skipped
- Operator extracted as lowercase string without `/` prefix

**Approach:** Regex or string prefix check. Only `^/when ` and `^/how ` match.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Add operator prefix validation in parse loop
  Location hint: Entry detection logic

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_operator_extraction -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 1.3: Split primary trigger and extra triggers

**RED Phase:**

**Test:** `test_trigger_splitting`
**Assertions:**
- `/when auth fails | auth error, login failure` → trigger `"auth fails"`, extras `["auth error", "login failure"]`
- `/when auth fails` (no pipe) → trigger `"auth fails"`, extras `[]` (empty list)
- `/when auth | ` (trailing pipe, empty extras) → trigger `"auth"`, extras `[]` (empty segments filtered)
- `/when auth fails | single` → trigger `"auth fails"`, extras `["single"]`
- Extra triggers trimmed of whitespace: ` mock patch ` → `"mock patch"`

**Expected failure:** AssertionError — edge cases with missing extras or whitespace not handled

**Why it fails:** Pipe splitting and whitespace handling not yet robust

**Verify RED:** `pytest tests/test_when_index_parser.py::test_trigger_splitting -v`

**GREEN Phase:**

**Implementation:** Robust trigger/extras splitting.

**Behavior:**
- Split line on first `|` character
- Left side (after operator prefix): primary trigger, stripped
- Right side (if present): comma-separated extra triggers, each stripped
- Empty segments filtered out
- No pipe = empty extras list

**Approach:** `text.split("|", 1)` then `extras.split(",")` with strip and filter.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Implement trigger/extras splitting with edge case handling
  Location hint: Within entry parsing logic

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_trigger_splitting -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 1.4: Validate format (operator prefix, pipe separator)

**RED Phase:**

**Test:** `test_format_validation`
**Assertions:**
- `/when` alone (no trigger text) → skipped with warning logged
- `/when | extras` (empty trigger) → skipped with warning logged
- `/when   | extras` (whitespace-only trigger) → skipped with warning logged
- `/when valid trigger | ,,,` (all-empty extras) → accepted, extras `[]`
- parse_index returns only valid entries (malformed ones excluded from list)

**Expected failure:** AssertionError — empty triggers accepted or malformed entries included

**Why it fails:** Format validation not yet enforcing trigger non-empty requirement

**Verify RED:** `pytest tests/test_when_index_parser.py::test_format_validation -v`

**GREEN Phase:**

**Implementation:** Add format validation rules.

**Behavior:**
- Trigger must be non-empty after stripping
- Empty trigger → skip entry, log warning with line number
- Extra triggers: empty segments after splitting silently dropped (not a warning)
- Return only entries passing validation

**Approach:** Validation checks after parsing, before appending to entry list. Use `logging.warning()` for skipped entries.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Add trigger non-empty validation, log warnings for malformed entries
  Location hint: After trigger extraction, before WhenEntry construction

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_format_validation -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 1.5: Malformed entry handling (skip with warning)

**RED Phase:**

**Test:** `test_malformed_entries_skipped_gracefully`
**Assertions:**
- Index file with mix of valid and malformed entries: parse_index returns only valid entries
- Malformed line `/when` (no space after operator) → skipped
- Line with old format `Key — description` → skipped (no `/when` prefix)
- Completely empty file → returns empty list
- File with only headers (no entries) → returns empty list
- Warning count matches number of malformed entries (use caplog fixture)

**Expected failure:** AssertionError — malformed entries cause crash or are included in results

**Why it fails:** Graceful degradation for edge cases not fully tested

**Verify RED:** `pytest tests/test_when_index_parser.py::test_malformed_entries_skipped_gracefully -v`

**GREEN Phase:**

**Implementation:** Ensure robust error handling across all entry parsing.

**Behavior:**
- Any line that doesn't match `/when ` or `/how ` prefix → silently skip (not an entry)
- Lines matching prefix but failing validation → warning with line number
- File I/O errors → log warning, return empty list (graceful degradation per project convention)
- Never raise exceptions during parsing

**Approach:** Wrap entry parsing in try/except per line. Ensure parse_index never raises.

**Changes:**
- File: `src/claudeutils/when/index_parser.py`
  Action: Add comprehensive error handling, logging for malformed entries
  Location hint: Main parsing loop and file read

**Verify GREEN:** `pytest tests/test_when_index_parser.py::test_malformed_entries_skipped_gracefully -v`
**Verify no regression:** `pytest tests/ -q`
