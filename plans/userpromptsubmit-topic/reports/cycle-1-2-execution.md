# Cycle 1.2: Match prompt keywords to candidate entries

**Timestamp:** 2026-03-01

## Execution Report

**Status:** GREEN_VERIFIED

**Test command:** `pytest tests/test_recall_topic_matcher.py::test_match_prompt_returns_candidates_with_overlap -v`

**RED result:** FAIL as expected (ImportError: cannot import name 'get_candidates')

**GREEN result:** PASS (test passes after implementation)

**Regression check:** 1366/1367 passed, 1 xfail (no new regressions)

**Refactoring:**
- Made `IndexEntry` hashable: changed `keywords: set[str]` → `keywords: frozenset[str]`
- Added Pydantic `Config` class with `frozen = True` to enable instance hashing
- Updated all existing tests to use `frozenset` instead of `set` for keywords (5 test files updated)
- Converted 28 keyword constructor calls from set to frozenset across test files

**Files modified:**
- `/Users/david/code/claudeutils-wt/ups-topic-injection/src/claudeutils/recall/topic_matcher.py` — added `get_candidates()` function, imported `extract_keywords`
- `/Users/david/code/claudeutils-wt/ups-topic-injection/src/claudeutils/recall/index_parser.py` — changed keywords field to frozenset, added Config class, wrapped keyword extractions with frozenset()
- `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/test_recall_topic_matcher.py` — updated 3 test entries to use frozenset
- `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/test_recall_index_parser.py` — updated 1 IndexEntry to use frozenset
- `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/test_recall_calculation.py` — updated 5 IndexEntry constructors to use frozenset
- `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/test_recall_relevance.py` — updated 16 IndexEntry constructors to use frozenset

**Stop condition:** none

**Decision made:**
- Used frozenset for keywords to enable IndexEntry hashing (needed for set deduplication in `get_candidates`)
- Pydantic `frozen=True` makes all fields immutable, enabling safe hashing
- `get_candidates()` uses set union for O(1) deduplication across all matched entries
- Both cycles 1.1 and 1.2 tests now pass with no regressions
