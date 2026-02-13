# Cycle 7.2

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.2: Generate candidate triggers (word-drop algorithm)

**RED Phase:**

**Test:** `test_generate_candidates`
**Assertions:**
- `generate_candidates("How to Encode Paths")` returns list including:
  - `"how encode paths"` (drop "to")
  - `"how encode path"` (drop "to", singularize — or just drop trailing s)
  - `"encode paths"` (drop prefix)
  - `"how paths"` (drop middle word)
- Candidates sorted by length (shortest first, as they're more compressed)
- All candidates lowercase
- Minimum candidate length: 2 words

**Expected failure:** AttributeError — `generate_candidates` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_compress_key.py::test_generate_candidates -v`

**GREEN Phase:**

**Implementation:** Create word-drop candidate generator.

**Behavior:**
- Start from heading words (lowercased)
- Generate combinations by dropping words (prefer dropping stopwords and articles)
- Keep operator prefix ("when"/"how") where it disambiguates
- Minimum 2 words per candidate
- Sort by length ascending

**Approach:** Word combinations via itertools, filtered by minimum length.

**Changes:**
- File: `src/claudeutils/when/compress.py`
  Action: Add `generate_candidates(heading)` function
  Location hint: After corpus loading

**Verify GREEN:** `pytest tests/test_when_compress_key.py::test_generate_candidates -v`
**Verify no regression:** `pytest tests/ -q`

---
