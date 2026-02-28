# Cycle 1.3

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

## Cycle 1.3: Score, rank, and cap candidates

**RED Phase:**

**Test:** `test_score_candidates_ranks_by_relevance_and_filters` (parametrized)

**Case 1 — ranking and threshold filtering:**
**Assertions:**
- Given 3 candidates: entry_high (4/5 keywords match prompt → score ~0.8), entry_mid (2/5 keywords match → score ~0.4), entry_low (1/10 keywords match → score 0.1)
- `score_and_rank(prompt_keywords, {entry_high, entry_mid, entry_low}, threshold=0.3)` returns list of `(IndexEntry, RelevanceScore)` tuples
- Assert len(result) == 2 (entry_low excluded, below 0.3)
- Assert result[0][0] == entry_high (highest score first)
- Assert result[1][0] == entry_mid

**Case 2 — entry count cap:**
**Assertions:**
- Given 5 candidates all scoring above 0.3 threshold
- `score_and_rank(prompt_keywords, candidates, threshold=0.3, max_entries=3)` returns list
- Assert len(result) == 3
- Assert all returned scores >= score of any excluded entry (top-3 by score)

**Expected failure:** `AttributeError` — `score_and_rank` does not exist

**Why it fails:** Function not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_score_candidates_ranks_by_relevance_and_filters -v`

**GREEN Phase:**

**Implementation:** Add `score_and_rank()` to topic_matcher.py.

**Behavior:**
- Call `score_relevance(session_id="hook", session_keywords=prompt_keywords, entry=entry, threshold=threshold)` for each candidate
- Filter to entries where `is_relevant == True`
- Sort descending by score
- Slice to `max_entries` if set

**Approach:** List comprehension → filter → sort → slice

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `score_and_rank(prompt_keywords: set[str], candidates: set[IndexEntry], threshold: float = 0.3, max_entries: int | None = None) -> list[tuple[IndexEntry, RelevanceScore]]`
  Location hint: After `get_candidates()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_score_candidates_ranks_by_relevance_and_filters -v`
**Verify no regression:** `just test`

---
