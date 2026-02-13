"""Tests for fuzzy matching engine."""

from claudeutils.when.fuzzy import rank_matches, score_match


def test_subsequence_match_scores_positive() -> None:
    """Subsequence matching scores positive for matches and exact > sparse."""
    # Subsequence found in order: positive score
    abc_sparse = score_match("abc", "aXbXc")
    assert isinstance(abc_sparse, float)
    assert abc_sparse > 0

    # No subsequence: zero or negative
    abc_missing = score_match("abc", "xyz")
    assert abc_missing <= 0

    # Exact match should score higher than sparse match
    abc_exact = score_match("abc", "abc")
    assert abc_exact > abc_sparse


def test_boundary_bonuses_applied() -> None:
    """Boundary bonuses applied for matches after whitespace/delimiters."""
    # Whitespace boundary bonus: 'ab' in "a b" has whitespace boundary on 'b'
    whitespace_bonus = score_match("ab", "a b")

    # No boundary bonus: 'ab' in "axb" has no boundary bonuses
    no_bonus = score_match("ab", "axb")

    # Whitespace boundary should score higher (bonusBoundaryWhite=10)
    assert whitespace_bonus > no_bonus

    # Delimiter boundary bonus: 'ab' in "a/b" has delimiter boundary on 'b'
    delimiter_bonus = score_match("ab", "a/b")

    # No boundary bonus: 'ab' in "axb" has no boundary bonuses
    no_bonus2 = score_match("ab", "axb")

    # Delimiter boundary should score higher (bonusBoundaryDelimiter=9)
    assert delimiter_bonus > no_bonus2

    # Whitespace boundary score > delimiter boundary score
    # (both have one boundary bonus, but whitespace=10 > delimiter=9)
    assert whitespace_bonus > delimiter_bonus


def test_consecutive_match_bonus() -> None:
    """Consecutive matched characters score higher due to consecutive bonus."""
    # Consecutive match: "mock" in "mock patching" has consecutive characters
    consecutive = score_match("mock", "mock patching")

    # Separated match: "mock" in "mXoXcXk" has no consecutive characters
    separated = score_match("mock", "mXoXcXk")

    # Consecutive should score higher
    assert consecutive > separated

    # Consecutive bonus: 4 per consecutive char after first
    # i=1: 16*2 (first char) = 32
    # i=2: 32 + 16 + 4 (consecutive) = 52
    # Plus word overlap bonus: "ab" query word overlaps with "ab" candidate word = +0.5
    ab_exact = score_match("ab", "ab")
    assert ab_exact == 52.5


def test_gap_penalties_reduce_score() -> None:
    """Gap penalties reduce score based on gap length and position."""
    # Shorter gap scores higher than longer gap
    short_gap = score_match("ac", "abc")
    long_gap = score_match("ac", "aXXXXc")

    assert short_gap > long_gap

    # Gap penalties: starting gap (first unmatched) = -3, each additional = -1
    single_gap = score_match("ac", "aXc")
    double_gap = score_match("ac", "aXXc")

    assert single_gap > double_gap


def test_word_overlap_tiebreaker() -> None:
    """Word-overlap tiebreaker breaks ties when fzf scores are identical."""
    # Two candidates with identical fzf scores but different word overlap
    score1 = score_match("fix bug", "fix this bug")
    score2 = score_match("fix bug", "fix your bugfix")

    # Word overlap:
    # - "fix this bug": overlap with ["fix", "this", "bug"] = 2 words
    #   Base fzf: 150.0 + word bonus (2 * 0.5) = 151.0
    # - "fix your bugfix": overlap with ["fix", "your", "bugfix"] = 1 word
    #   Base fzf: 150.0 + word bonus (1 * 0.5) = 150.5
    # Word-overlap tiebreaker breaks the tie
    assert score1 == 151.0
    assert score2 == 150.5
    assert score1 > score2


def test_minimum_score_threshold() -> None:
    """Minimum score threshold filters spurious matches on short queries."""
    # Short query against long candidate string: high per-char threshold required
    short_query_long = score_match(
        "x", "extremely long candidate string with many words"
    )
    assert short_query_long == 0.0

    # Legitimate match: short query with reasonable match score
    legitimate_match = score_match("when", "when auth fails")
    assert legitimate_match > 0

    # No valid subsequence or below threshold
    no_match = score_match("zq", "writing mock tests")
    assert no_match == 0.0


def test_prefix_word_disambiguates() -> None:
    """Prefix words in query match prefix words in candidate headings."""
    # Prefix word "when" in query matches "when" at start of heading
    when_match = score_match("when writing mock tests", "When Writing Mock Tests")
    how_match = score_match("when writing mock tests", "How to Write Mock Tests")
    assert when_match > how_match

    # Prefix word "how" in query matches "how" at start of heading
    how_match2 = score_match("how encode paths", "How to Encode Paths")
    when_match2 = score_match("how encode paths", "When Encoding Paths")
    assert how_match2 > when_match2

    # Query without prefix: scores closer together (less disambiguation)
    no_prefix_when = score_match("writing mock tests", "When Writing Mock Tests")
    no_prefix_how = score_match("writing mock tests", "How to Write Mock Tests")
    with_prefix_gap = when_match - how_match
    without_prefix_gap = no_prefix_when - no_prefix_how
    assert with_prefix_gap > without_prefix_gap


def test_rank_matches_returns_sorted_limited() -> None:
    """Rank matches returns sorted list of (candidate, score) tuples."""
    candidates = [
        "mock patching",
        "mock test",
        "unrelated",
        "mocking framework",
        "something",
    ]
    results = rank_matches("mock", candidates, limit=3)

    # Results are tuples of (candidate, score)
    assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
    assert all(isinstance(r[0], str) and isinstance(r[1], float) for r in results)

    # Results are sorted by score descending
    scores = [r[1] for r in results]
    assert scores == sorted(scores, reverse=True)

    # Limit applied: at most 3 results
    assert len(results) <= 3

    # Zero-score candidates excluded
    assert all(score > 0 for _, score in results)

    # Test default limit is 5
    results_default = rank_matches("mock", candidates)
    assert len(results_default) <= 5


def test_dp_rejects_non_subsequence() -> None:
    """DP matrix correctly rejects candidates missing query characters."""
    # 'o' and 'k' from "mock" don't exist in candidate — not a valid subsequence
    assert score_match("when mock tests", "when evaluating test success metrics") == 0.0

    # Valid subsequence still scores positive
    assert score_match("mock", "mock patching") > 0


