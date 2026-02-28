# Cycle 1.2

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

## Cycle 1.2: Match prompt keywords to candidate entries

**RED Phase:**

**Test:** `test_match_prompt_returns_candidates_with_overlap`
**Assertions:**
- Given inverted index built from 3 entries (entry_a: recall/system keywords, entry_b: recall/hook keywords, entry_c: commit/message keywords)
- `get_candidates("how does the recall system work", inverted_index)` returns set of IndexEntry
- Assert result contains entry_a (keywords "recall" and "system" both match)
- Assert result contains entry_b (keyword "recall" matches)
- Assert result does NOT contain entry_c (no keyword overlap)
- Assert len(result) == 2

**Expected failure:** `AttributeError` — `get_candidates` does not exist

**Why it fails:** Function not yet implemented in topic_matcher.py

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_match_prompt_returns_candidates_with_overlap -v`

**GREEN Phase:**

**Implementation:** Add `get_candidates()` to topic_matcher.py.

**Behavior:**
- Tokenize prompt text using `extract_keywords()` (same tokenization as index entries)
- For each prompt keyword, collect entries from inverted index
- Return union of all matched entries (deduplicated)

**Approach:** Set union over index lookups

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `get_candidates(prompt_text: str, inverted_index: dict[str, list[IndexEntry]]) -> set[IndexEntry]`
  Location hint: After `build_inverted_index()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_match_prompt_returns_candidates_with_overlap -v`
**Verify no regression:** `just test`

---
