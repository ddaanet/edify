"""Fuzzy matching engine using modified fzf V2 scoring algorithm."""

_NEG_INF = float("-inf")

MATCH_SCORE = 16
CONSECUTIVE_BONUS = 4
FIRST_CHAR_MULTIPLIER = 2
BOUNDARY_WHITESPACE = 10.0
BOUNDARY_DELIMITER = 9.0
BOUNDARY_CAMELCASE = 7.0
GAP_START_PENALTY = -3
GAP_EXTENSION_PENALTY = -1
WORD_OVERLAP_BONUS = 0.5
MIN_THRESHOLD_SINGLE_CHAR = 50.0


def _get_match_positions(
    query_lower: str, candidate_lower: str, score: list[list[float]]
) -> list[int]:
    """Backtrace DP matrix to find match positions.

    Args:
        query_lower: Lowercase query
        candidate_lower: Lowercase candidate
        score: DP score matrix

    Returns:
        List of candidate positions where query characters matched
    """
    m, n = len(query_lower), len(candidate_lower)
    positions = []

    i, j = m, n
    while i > 0 and j > 0:
        if query_lower[i - 1] == candidate_lower[j - 1]:
            # Check if this position was actually used (not skipped)
            if score[i - 1][j - 1] > score[i][j - 1] or i == 1:
                positions.append(j - 1)
                i -= 1
                j -= 1
            else:
                j -= 1
        else:
            j -= 1

    positions.reverse()
    return positions


def _compute_dp_matrix(query_lower: str, candidate_lower: str) -> list[list[float]]:
    """Compute DP matrix for character subsequence matching.

    Args:
        query_lower: Lowercase query
        candidate_lower: Lowercase candidate string

    Returns:
        DP score matrix[i][j] = best score matching query[0:i] with candidate[0:j]
    """
    m, n = len(query_lower), len(candidate_lower)
    score = [[_NEG_INF for _ in range(n + 1)] for _ in range(m + 1)]

    for j in range(n + 1):
        score[0][j] = 0.0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if query_lower[i - 1] == candidate_lower[j - 1]:
                consecutive_bonus = (
                    CONSECUTIVE_BONUS
                    if j > 1 and score[i - 1][j - 1] > score[i - 1][j - 2]
                    else 0
                )
                boundary_bonus = _boundary_bonus(candidate_lower, j)
                first_char_multiplier = FIRST_CHAR_MULTIPLIER if i == 1 else 1

                score[i][j] = max(
                    score[i][j - 1],
                    score[i - 1][j - 1]
                    + MATCH_SCORE * first_char_multiplier
                    + consecutive_bonus
                    + boundary_bonus,
                )
            else:
                score[i][j] = score[i][j - 1]

    return score


def _meets_minimum_threshold(
    query_lower: str,
    base_score: float,
    word_overlap: int,
) -> bool:
    """Check if match meets minimum score threshold.

    Single-character queries require either word overlap or very high base score
    to avoid spurious matches.

    Args:
        query_lower: Lowercase query
        base_score: Base fzf score before adjustments
        word_overlap: Number of query words found in candidate

    Returns:
        True if match meets threshold, False otherwise
    """
    return not (
        len(query_lower) == 1
        and word_overlap == 0
        and base_score < MIN_THRESHOLD_SINGLE_CHAR
    )


def _boundary_bonus(candidate_lower: str, match_pos: int) -> float:
    """Calculate boundary bonus for a character match.

    Args:
        candidate_lower: Lowercase candidate string
        match_pos: Position of matched character (1-indexed)

    Returns:
        Boundary bonus score (0.0 if no boundary, higher for stronger boundaries)
    """
    if match_pos <= 1:
        return 0.0

    prev_char = candidate_lower[match_pos - 2]
    curr_char = candidate_lower[match_pos - 1]

    if prev_char == " ":
        return BOUNDARY_WHITESPACE
    if prev_char in ("/", "-", "_"):
        return BOUNDARY_DELIMITER
    if prev_char.islower() and curr_char.isupper():
        return BOUNDARY_CAMELCASE

    return 0.0


def score_match(query: str, candidate: str) -> float:
    """Score a candidate string using character subsequence matching.

    Returns a positive score if all query characters are found in order within
    the candidate string (case-insensitive). Returns 0.0 if the subsequence
    cannot be matched.

    Args:
        query: The search pattern (case-insensitive)
        candidate: The string to search in (case-insensitive)

    Returns:
        Float score: positive if match found, 0.0 if no match
    """
    query_lower = query.lower()
    candidate_lower = candidate.lower()

    # Build DP matrix: score[i][j] = best score matching query[0:i] with candidate[0:j]
    m, n = len(query_lower), len(candidate_lower)

    if m == 0:
        return 0.0

    if m > n:
        return 0.0

    score = _compute_dp_matrix(query_lower, candidate_lower)

    base_score = score[m][n]

    # If no match found, return 0
    if base_score <= 0:
        return 0.0

    # Second pass: backtrace to find match positions and calculate gap penalties
    match_positions = _get_match_positions(query_lower, candidate_lower, score)

    gap_penalty = 0.0
    for idx in range(len(match_positions) - 1):
        prev_pos = match_positions[idx]
        curr_pos = match_positions[idx + 1]
        gap_length = curr_pos - prev_pos - 1
        if gap_length > 0:
            gap_penalty += GAP_START_PENALTY + (GAP_EXTENSION_PENALTY * gap_length)

    # Word-overlap tiebreaker: bonus for matching whole words
    query_words = set(query.lower().split())
    candidate_words = set(candidate_lower.split())
    word_overlap = len(query_words & candidate_words)
    word_overlap_bonus = word_overlap * WORD_OVERLAP_BONUS

    if not _meets_minimum_threshold(query_lower, base_score, word_overlap):
        return 0.0

    return base_score + gap_penalty + word_overlap_bonus


def rank_matches(
    query: str, candidates: list[str], limit: int = 5
) -> list[tuple[str, float]]:
    """Rank a list of candidates against a query and return top matches.

    Args:
        query: The search pattern
        candidates: List of candidates to score
        limit: Maximum number of results to return (default 5)

    Returns:
        List of (candidate, score) tuples sorted by score descending
    """
    scored = []
    for candidate in candidates:
        score = score_match(query, candidate)
        if score > 0:
            scored.append((candidate, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:limit]
