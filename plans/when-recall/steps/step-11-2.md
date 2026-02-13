# Cycle 11.2

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 11

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
