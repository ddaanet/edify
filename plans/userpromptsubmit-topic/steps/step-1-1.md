# Cycle 1.1

**Plan**: `plans/userpromptsubmit-topic/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Builds `src/claudeutils/recall/topic_matcher.py` — the complete matching pipeline from index construction through scoring, resolution, and output formatting. Tests in `tests/test_recall_topic_matcher.py`.

**API promotions folded into GREEN phases:**
- Cycle 1.1: promote `_extract_keywords` → `extract_keywords` in `index_parser.py` (update internal callers at lines 113, 138)
- Cycle 1.4: promote `_extract_section` → `extract_section` in `when/resolver.py` (update internal callers at lines 117, 225)

**Heading reconstruction:** `IndexEntry.key` stores trigger text without `/when` or `/how` prefix. Try both `## When {key}` and `## How to {key}` heading forms — `extract_section()` returns empty string on miss, so the fallback is free. If both miss, skip the entry (FR-3 silent-skip).

---

---

## Cycle 1.1: Build inverted index from parsed entries

**RED Phase:**

**Test:** `test_build_inverted_index_maps_keywords_to_entries`
**Assertions:**
- Given 3 `IndexEntry` objects: entry_a with keywords `{"recall", "system", "effectiveness"}`, entry_b with keywords `{"recall", "hook", "injection"}`, entry_c with keywords `{"commit", "message", "format"}`
- `build_inverted_index([entry_a, entry_b, entry_c])` returns `dict[str, list[IndexEntry]]`
- Assert `"recall"` key maps to list containing both entry_a and entry_b (length 2)
- Assert `"hook"` key maps to list containing only entry_b (length 1)
- Assert `"commit"` key maps to list containing only entry_c (length 1)
- Assert total unique keys == union of all entry keywords

**Expected failure:** `ImportError` or `AttributeError` — `build_inverted_index` does not exist yet

**Why it fails:** `topic_matcher.py` module not created

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_build_inverted_index_maps_keywords_to_entries -v`

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/recall/topic_matcher.py` with `build_inverted_index()`.

**Behavior:**
- Iterate entries, for each keyword in `entry.keywords`, append entry to `index[keyword]`
- Return complete inverted index mapping

**Approach:** defaultdict(list), single pass over entries

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Create new module with `build_inverted_index(entries: list[IndexEntry]) -> dict[str, list[IndexEntry]]`
- File: `src/claudeutils/recall/index_parser.py`
  Action: Rename `_extract_keywords` → `extract_keywords` (public API). Update internal callers at lines 113 and 138.

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_build_inverted_index_maps_keywords_to_entries -v`
**Verify no regression:** `just test`

---
