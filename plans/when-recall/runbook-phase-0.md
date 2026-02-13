# Phase 0: Fuzzy Engine Foundation

**Type:** TDD
**Model:** haiku
**Dependencies:** None (foundation)
**Files:** `src/claudeutils/when/fuzzy.py`, `tests/test_when_fuzzy.py`

**Design reference:** D-4 (Custom fuzzy engine), fzf-research.md scoring constants

**Scoring constants (from design):**
- scoreMatch = 16 (base per matched character)
- scoreGapStart = -3
- scoreGapExtension = -1
- bonusBoundaryWhite = 10
- bonusBoundaryDelimiter = 9
- bonusCamel123 = 7
- bonusConsecutive = 4
- bonusFirstCharMultiplier = 2

---

## Common Context

**Design reference:**
- D-4 (Custom fuzzy engine) — ~80 line custom implementation, tuned scoring constants
- plans/when-recall/reports/fzf-research.md — fzf V2 scoring algorithm reference

**Project conventions:**
- agents/decisions/testing.md — TDD RED/GREEN/refactor conventions
- agents/decisions/implementation-notes.md — Pydantic over dataclass, Path.cwd() patterns

**Project paths:**
- `src/claudeutils/when/fuzzy.py` — fuzzy engine module (create in Phase 0)
- `tests/test_when_fuzzy.py` — test file (create in Phase 0)
- `src/claudeutils/when/__init__.py` — package marker (empty)

**Stop/error conditions:**
- Scoring constants: Use exact values from design (don't modify without justification)
- Test file must match function signatures (score_match, rank_matches)
- Verify RED fails before implementing GREEN

---

## Weak Orchestrator Metadata

**Total Steps:** 8
**Complexity:** Medium
**Model:** haiku
**Estimated tokens:** ~12000 (foundation module, isolated tests)

---

## Cycle 0.1: Character subsequence matching

**RED Phase:**

**Test:** `test_subsequence_match_scores_positive`
**Assertions:**
- `score_match("abc", "aXbXc")` returns a positive float (characters found in order)
- `score_match("abc", "xyz")` returns 0.0 or negative (no subsequence match)
- `score_match("abc", "abc")` returns higher score than `score_match("abc", "aXbXc")` (exact > sparse)

**Expected failure:** ImportError or AttributeError — `score_match` doesn't exist

**Why it fails:** Module `src/claudeutils/when/fuzzy.py` not yet created

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_subsequence_match_scores_positive -v`

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/when/__init__.py` (empty) and `fuzzy.py` with `score_match(query, candidate)` function.

**Behavior:**
- Find each query character in candidate (in order, case-insensitive)
- If all characters found in order, return positive score (base 16 per matched character)
- If subsequence not found, return 0.0
- Track match positions for bonus calculations in later cycles

**Approach:** Smith-Waterman style DP matrix — build score[i][j] for query[i] matched at candidate[j]. For this cycle, base scoring only (no bonuses yet).

**Changes:**
- File: `src/claudeutils/when/__init__.py`
  Action: Create empty file
- File: `src/claudeutils/when/fuzzy.py`
  Action: Create with `score_match` function implementing character-level subsequence matching with base score
  Location hint: Module-level function

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_subsequence_match_scores_positive -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 0.2: Boundary bonus scoring

**RED Phase:**

**Test:** `test_boundary_bonuses_applied`
**Assertions:**
- `score_match("mp", "mock patching")` scores higher than `score_match("mp", "xmxpx")` (whitespace boundary bonus)
- `score_match("ep", "encode/path")` scores higher than `score_match("ep", "xexpy")` (delimiter boundary bonus)
- Whitespace boundary score > delimiter boundary score for equivalent matches (bonusBoundaryWhite=10 > bonusBoundaryDelimiter=9)

**Expected failure:** AssertionError — both score the same (no boundary bonuses yet)

**Why it fails:** `score_match` only applies base scoring, no boundary detection

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_boundary_bonuses_applied -v`

**GREEN Phase:**

**Implementation:** Add boundary detection to scoring.

**Behavior:**
- When matched character follows whitespace, add bonus of 10
- When matched character follows delimiter (/, -, _), add bonus of 9
- When matched character is at CamelCase transition, add bonus of 7
- First character match bonus multiplied by 2

**Approach:** At each match position, check preceding character type. Apply corresponding bonus constant.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add boundary type detection and bonus application in score calculation
  Location hint: Within `score_match` function, after determining match positions

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_boundary_bonuses_applied -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 0.3: Consecutive match bonus

**RED Phase:**

**Test:** `test_consecutive_match_bonus`
**Assertions:**
- `score_match("mock", "mock patching")` scores higher than `score_match("mock", "mXoXcXk")` (consecutive characters)
- The score difference is approximately 4 points per additional consecutive character (bonusConsecutive=4)
- `score_match("ab", "ab")` returns exactly: 2*16 (base) + boundary + consecutive bonuses (verifiable math)

**Expected failure:** AssertionError — consecutive and separated score the same

**Why it fails:** No consecutive match bonus in scoring

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_consecutive_match_bonus -v`

**GREEN Phase:**

**Implementation:** Add consecutive match tracking.

**Behavior:**
- When a matched character immediately follows the previous matched character, add 4 per consecutive character
- Consecutive bonus accumulates (3 consecutive = 4+4)

**Approach:** Track previous match position. If current position == previous + 1, apply consecutive bonus.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add consecutive match detection and bonus in scoring loop
  Location hint: Within score_match, match position tracking

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_consecutive_match_bonus -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 0.4: Gap penalties

**RED Phase:**

**Test:** `test_gap_penalties_reduce_score`
**Assertions:**
- `score_match("ac", "abc")` scores higher than `score_match("ac", "aXXXXc")` (shorter gap = higher score)
- `score_match("ac", "aXc")` has gap penalty of -3 (start) applied
- `score_match("ac", "aXXXc")` has penalty of -3 (start) + -2 (2 extensions at -1 each)

**Expected failure:** AssertionError — all gaps score the same

**Why it fails:** No gap penalty in scoring

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_gap_penalties_reduce_score -v`

**GREEN Phase:**

**Implementation:** Add gap penalties between matched characters.

**Behavior:**
- Starting a gap (first unmatched character after a match): penalty of -3
- Each additional gap character: penalty of -1
- No gap penalty before first match or after last match

**Approach:** Between consecutive match positions, calculate gap length. Apply start + extension penalties.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add gap penalty calculation between match positions
  Location hint: Within score_match, after match position determination

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_gap_penalties_reduce_score -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 0.5: Word-overlap tiebreaker

**RED Phase:**

**Test:** `test_word_overlap_tiebreaker`
**Assertions:**
- Given two candidates with identical fzf scores (construct carefully):
  `score_match("auth fail", "when auth fails")` > `score_match("auth fail", "auth failover config")` when fzf scores are tied
- More specifically: "auth fail" has 2 word overlaps with "when auth fails" vs 1 with "auth failover config" (validates tiebreaker logic)

**Expected failure:** AssertionError — tied scores remain tied

**Why it fails:** No word-overlap tiebreaker logic

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_word_overlap_tiebreaker -v`

**GREEN Phase:**

**Implementation:** Add word-overlap tiebreaker to scoring.

**Behavior:**
- After fzf-style scoring, compute word overlap between query words and candidate words
- Each overlapping word adds a small bonus (0.5 or similar — smaller than fzf score granularity but breaks ties)
- Word matching is case-insensitive, exact word match only

**Approach:** Split query and candidate into word sets. Count intersecting words. Add fractional bonus per overlap.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add word overlap calculation as secondary scoring factor
  Location hint: At end of score_match, after primary scoring

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_word_overlap_tiebreaker -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 0.6: Minimum score threshold

**RED Phase:**

**Test:** `test_minimum_score_threshold`
**Assertions:**
- `score_match("x", "extremely long candidate string with many words")` returns 0.0 (short query, spurious match filtered)
- `score_match("when", "when auth fails")` returns positive (legitimate match above threshold)
- `score_match("zq", "writing mock tests")` returns 0.0 (no valid subsequence or below threshold)

**Expected failure:** AssertionError — single-char queries return positive scores for long strings

**Why it fails:** No minimum score threshold filtering

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_minimum_score_threshold -v`

**GREEN Phase:**

**Implementation:** Add minimum score threshold.

**Behavior:**
- After computing score, compare against a minimum threshold
- Threshold scales with query length (shorter queries need higher per-character scores to qualify)
- Return 0.0 if below threshold (not a meaningful match)

**Approach:** Define threshold as `min_score_per_char * len(query)`. If total_score / len(query) below threshold, return 0.0.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add threshold check at end of score_match
  Location hint: Before return statement

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_minimum_score_threshold -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 0.7: Rank matches with limit

**RED Phase:**

**Test:** `test_rank_matches_returns_sorted_limited`
**Assertions:**
- `rank_matches("mock", ["mock patching", "mock test", "unrelated", "mocking framework", "something"])` returns list of (candidate, score) tuples
- Results sorted by score descending
- `limit=3` returns at most 3 results
- Zero-score candidates excluded from results
- Default limit is 5

**Expected failure:** ImportError or AttributeError — `rank_matches` doesn't exist

**Why it fails:** Function not yet created

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_rank_matches_returns_sorted_limited -v`

**GREEN Phase:**

**Implementation:** Create `rank_matches` function.

**Behavior:**
- Score each candidate against query using `score_match`
- Filter out zero/negative scores
- Sort remaining by score descending
- Return top `limit` results as list of (candidate, score) tuples

**Approach:** List comprehension → filter → sort → slice.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add `rank_matches(query, candidates, limit=5)` function
  Location hint: After `score_match` function

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_rank_matches_returns_sorted_limited -v`
**Verify no regression:** `pytest tests/ -q`

---

## Cycle 0.8: Prefix word inclusion

**RED Phase:**

**Test:** `test_prefix_word_disambiguates`
**Assertions:**
- `score_match("when writing mock tests", "When Writing Mock Tests")` > `score_match("when writing mock tests", "How to Write Mock Tests")` (prefix "when" boosts when-headed candidates)
- `score_match("how encode paths", "How to Encode Paths")` > `score_match("how encode paths", "When Encoding Paths")` (prefix "how" boosts how-headed candidates)
- Query without prefix: `score_match("writing mock tests", "When Writing Mock Tests")` and `score_match("writing mock tests", "How to Write Mock Tests")` are closer in score (less disambiguation)

**Expected failure:** AssertionError — scores don't reflect prefix disambiguation

**Why it fails:** This tests the design requirement that query includes prefix word for disambiguation, verifying the scoring naturally handles it via word boundary bonuses.

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_prefix_word_disambiguates -v`

**GREEN Phase:**

**Implementation:** This cycle validates that existing scoring naturally produces disambiguation. May require tuning constants if disambiguation is insufficient.

**Behavior:**
- Prefix word "when"/"how" in query matches prefix word in candidate heading
- Word boundary bonus at the heading's first word provides disambiguation
- No new code required IF existing scoring already disambiguates; otherwise tune boundary constants

**Approach:** Run assertions — if they pass, existing scoring is sufficient. If not, increase first-character or word-boundary bonuses.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Potentially adjust scoring constants if disambiguation insufficient
  Location hint: Scoring constant definitions

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_prefix_word_disambiguates -v`
**Verify no regression:** `pytest tests/ -q`
