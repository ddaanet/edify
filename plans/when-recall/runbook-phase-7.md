# Phase 7: Key Compression Tool

**Type:** TDD
**Model:** haiku
**Dependencies:** Phase 0 (fuzzy)
**Files:** `agent-core/bin/compress-key.py`, `tests/test_when_compress_key.py`

**Design reference:** Key Compression Tool section

**Prior state:** Phase 0 provides `fuzzy.score_match()` and `fuzzy.rank_matches()` for uniqueness verification.

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

## Cycle 7.3: Verify uniqueness via fuzzy scoring

**RED Phase:**

**Test:** `test_uniqueness_verification`
**Assertions:**
- `verify_unique("how encode path", corpus)` returns True when trigger uniquely resolves to one heading
- `verify_unique("encode", corpus)` returns False when trigger matches multiple headings above threshold
- Uniqueness uses `fuzzy.rank_matches` — top match must be significantly above second match (score gap)

**Expected failure:** AttributeError — `verify_unique` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_compress_key.py::test_uniqueness_verification -v`

**GREEN Phase:**

**Implementation:** Create uniqueness verification using fuzzy engine.

**Behavior:**
- Score trigger against all headings in corpus
- Unique = top match score is significantly higher than second match (e.g., 2x or threshold gap)
- Return True/False

**Approach:** `rank_matches(trigger, corpus, limit=2)` then compare scores.

**Changes:**
- File: `src/claudeutils/when/compress.py`
  Action: Add `verify_unique(trigger, corpus)` function
  Location hint: After candidate generation

**Verify GREEN:** `pytest tests/test_when_compress_key.py::test_uniqueness_verification -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 7.4: Suggest minimal unique trigger

**RED Phase:**

**Test:** `test_suggest_minimal_trigger`
**Assertions:**
- `compress_key("How to Encode Paths", corpus)` returns shortest unique trigger (e.g., `"how encode path"`)
- Result is verified unique against corpus
- If no unique candidate found (heading too generic), returns full heading lowercased as fallback
- For heading `"When Writing Mock Tests"`, result is shorter than the full heading

**Expected failure:** AttributeError — `compress_key` doesn't exist

**Why it fails:** Main entry point not yet created

**Verify RED:** `pytest tests/test_when_compress_key.py::test_suggest_minimal_trigger -v`

**GREEN Phase:**

**Implementation:** Create main compress_key function.

**Behavior:**
- Generate candidates from heading (7.2)
- Test each candidate for uniqueness (7.3), shortest first
- Return first unique candidate
- Fallback: full heading lowercased if no shorter candidate is unique

**Approach:** Linear scan of sorted candidates, return first passing uniqueness check.

**Changes:**
- File: `src/claudeutils/when/compress.py`
  Action: Add `compress_key(heading, corpus)` function
  Location hint: Main entry point, after helper functions
- File: `agent-core/bin/compress-key.py`
  Action: Create CLI wrapper with shebang
  Location hint: New file

**Verify GREEN:** `pytest tests/test_when_compress_key.py::test_suggest_minimal_trigger -v`
**Verify no regression:** `pytest tests/ -q`
