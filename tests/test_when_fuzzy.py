"""Tests for fuzzy matching engine."""

from claudeutils.when.fuzzy import score_match


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
    # Whitespace boundary bonus: 'mp' in "mock patching" has boundary bonus
    whitespace_bonus = score_match("mp", "mock patching")

    # No boundary bonus: 'mp' in "xmxpx" has no boundary bonuses
    no_bonus = score_match("mp", "xmxpx")

    # Whitespace boundary should score higher (bonusBoundaryWhite=10)
    assert whitespace_bonus > no_bonus

    # Delimiter boundary bonus: 'ep' in "encode/path" has boundary bonus
    delimiter_bonus = score_match("ep", "encode/path")

    # No boundary bonus: 'ep' in "xexpy" has no boundary bonuses
    no_bonus2 = score_match("ep", "xexpy")

    # Delimiter boundary should score higher (bonusBoundaryDelimiter=9)
    assert delimiter_bonus > no_bonus2

    # Whitespace boundary score > delimiter boundary score
    # (both have one boundary bonus, but whitespace=10 > delimiter=9)
    assert whitespace_bonus > delimiter_bonus
