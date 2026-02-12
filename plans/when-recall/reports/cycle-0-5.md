# Cycle 0.5: Word-overlap tiebreaker

**Timestamp:** 2026-02-12T17:30:00Z
**Status:** GREEN_VERIFIED

## Summary

Implemented word-overlap tiebreaker to break scoring ties when fzf scores are identical. Feature correctly isolates word-level matching from character-level matching.

## RED Phase

**Test:** `test_word_overlap_tiebreaker`
**Expected failure:** AssertionError — test asserts feature not yet implemented
**Actual result:** Test failed as expected ✓

Key insight from blast radius assessment: Original cycle spec assertions would pass due to boundary bonuses creating score differences (212 vs 202), not due to word-overlap logic. Rewritten assertions with genuinely tied fzf scores:
- Query: "fix bug"
- Candidate 1: "fix this bug" → both words overlap = 2 words
- Candidate 2: "fix your bugfix" → only "fix" overlaps = 1 word
- Base fzf scores: Both 150.0 (tied)

Test expects `score1 > score2` with tiebreaker.

**RED verification:** `pytest tests/test_when_fuzzy.py::test_word_overlap_tiebreaker -v`
```
assert score1 > score2
E   assert 150.0 > 150.0
```

## GREEN Phase

**Implementation:** Added word-overlap calculation to `score_match` function.

File: `src/claudeutils/when/fuzzy.py`

Logic:
```python
# After gap penalty calculation
query_words = set(query.lower().split())
candidate_words = set(candidate_lower.split())
word_overlap = len(query_words & candidate_words)
word_overlap_bonus = word_overlap * 0.5
return base_score + gap_penalty + word_overlap_bonus
```

Word matching:
- Case-insensitive (lowercase)
- Exact word match only
- Intersection of sets
- Bonus: +0.5 per overlapping word

**GREEN verification:**
```
PASSED tests/test_when_fuzzy.py::test_word_overlap_tiebreaker
```

Scores after implementation:
- "fix this bug": 150.0 + 2*0.5 = 151.0 ✓
- "fix your bugfix": 150.0 + 1*0.5 = 150.5 ✓
- Test assertion: 151.0 > 150.5 ✓

**Regression check:** All tests pass, 1 test updated.

Found and fixed regression in `test_consecutive_match_bonus`:
- Test expected exact score of 52 for `score_match("ab", "ab")`
- Now scores 52.5 due to word overlap bonus (1 word overlap)
- Updated assertion to 52.5

## REFACTOR Phase

**Formatting:** Fixed 2 line-length violations in test comments (E501, >88 char)

**Precommit validation:** All checks pass
```
✓ Tests OK (760/761 passed, 1 xfail)
✓ Lint OK
✓ Precommit OK
```

## Files Modified

- `src/claudeutils/when/fuzzy.py` — Added word overlap calculation
- `tests/test_when_fuzzy.py` — Added test_word_overlap_tiebreaker, updated test_consecutive_match_bonus

## Quality Checks

- RED failure matches expected behavior ✓
- GREEN passes with correct scores ✓
- No regressions after fix ✓
- Lint passes ✓
- Precommit passes ✓
- Clean tree after commit ✓

## Decision Made

Word-overlap bonus is applied to all matches, including those with base_score > gap_penalty. This affects all scored matches universally, creating consistent tiebreaker behavior throughout ranking.

Bonus magnitude (0.5 per word) chosen to be smaller than fzf score granularity (16 base per char) but sufficient to break typical ties, allowing fzf scoring to dominate while word overlap serves as tiebreaker.

## Next Steps

Phase 0 remaining cycles:
- Cycle 0.6: Min score threshold
- Cycle 0.7: rank_matches (over-implemented, skip GREEN)
- Cycle 0.8: Prefix disambiguation (by design, may skip GREEN)
