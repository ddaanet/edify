# Phase 11: Recall Parser Update

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 1 (parser implementation proven)
**Files:** `src/claudeutils/recall/index_parser.py`, `tests/test_recall_index_parser.py`

**Design reference:** Implementation Notes — Recall tool compatibility

**Prior state:** Phase 1 provides `WhenEntry` model and `parse_index()` in `src/claudeutils/when/index_parser.py`. The recall tool's `src/claudeutils/recall/index_parser.py` currently parses em-dash format.

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

## Cycle 11.2: Keyword extraction from trigger + extras

**RED Phase:**

**Test:** `test_keyword_extraction_from_triggers`
**Assertions:**
- `/when writing mock tests | mock patch, test doubles`:
  - Keywords include: "writing", "mock", "tests", "patch", "doubles"
  - Keywords exclude stopwords: "when" is NOT in keywords (it's the operator, not content)
- `/how encode paths | path encoding, URL encoding`:
  - Keywords include: "encode", "paths", "path", "encoding", "url"
  - Keywords exclude: "how", "to" (stopwords)
- Extra triggers contribute keywords beyond what trigger alone provides

**Expected failure:** AssertionError — keywords missing from extra triggers

**Why it fails:** Keyword extraction in `_extract_keywords()` (line 156) uses key+description text, not trigger+extras structure from new format

**Verify RED:** `pytest tests/test_recall_index_parser.py::test_keyword_extraction_from_triggers -v`

**GREEN Phase:**

**Implementation:** Update keyword extraction to use trigger + extras.

**Behavior:**
- Combine trigger text + all extra trigger texts for keyword extraction
- Apply existing `_extract_keywords()` function (stopword removal, tokenization)
- Exclude operator word ("when", "how") from keywords — add to STOPWORDS if not present

**Approach:** `_extract_keywords(trigger + " " + " ".join(extra_triggers))`

**Changes:**
- File: `src/claudeutils/recall/index_parser.py`
  Action: Update keyword extraction to include extra triggers, add operator words to stopwords
  Location hint: Lines 72-87 (`_extract_keywords`) and entry construction

**Verify GREEN:** `pytest tests/test_recall_index_parser.py::test_keyword_extraction_from_triggers -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 11.3: Verify recall analysis produces valid reports

**RED Phase:**

**Test:** `test_recall_analysis_with_new_format`
**Assertions:**
- Given index file in new `/when` format and a session transcript:
  - Recall analysis runs without error
  - Report contains entry matches (if any topics overlap)
  - Entry count in report matches index entry count
- Empty index → report shows 0 entries, 0 matches (no crash)

**Expected failure:** Test fails — recall analysis crashes or report format incorrect

**Why it fails:** Recall modules (`relevance.py` or `report.py`) may use IndexEntry.description field which becomes empty string in new format, causing AttributeError or KeyError on dict access

**Verify RED:** `pytest tests/test_recall_integration.py::test_recall_analysis_with_new_format -v`

**GREEN Phase:**

**Implementation:** Ensure recall analysis pipeline handles updated IndexEntry format.

**Behavior:**
- Recall analysis should work with empty description field
- Keywords are sufficient for relevance matching (description was redundant with keywords)
- Report generation uses key field (trigger text) for display

**Approach:** Check all recall modules for description field usage. Update if needed. Most likely `relevance.py` and `report.py`.

**Changes:**
- File: `src/claudeutils/recall/relevance.py`
  Action: Verify keyword-based matching works without description (may need no changes)
- File: `src/claudeutils/recall/report.py`
  Action: Use key field for display if description is empty
  Location hint: Report formatting logic

**Verify GREEN:** `pytest tests/test_recall_integration.py::test_recall_analysis_with_new_format -v`
**Verify no regression:** `pytest tests/ -q`
