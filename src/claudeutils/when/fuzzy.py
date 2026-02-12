"""Fuzzy matching engine using modified fzf V2 scoring algorithm."""


def score_match(query: str, candidate: str) -> float:
    """Score a candidate string using character subsequence matching.

    Returns a positive score if all query characters are found in order within
    the candidate string (case-insensitive). Returns 0.0 if the subsequence
    cannot be matched.

    Args:
        query: The search pattern (case-insensitive)
        candidate: The string to search in (case-insensitive)

    Returns:
        Float score: positive if match found, 0.0 or negative if no match
    """
    query_lower = query.lower()
    candidate_lower = candidate.lower()

    # Build DP matrix: score[i][j] = best score matching query[0:i] with candidate[0:j]
    m, n = len(query_lower), len(candidate_lower)

    if m == 0:
        return 0.0

    if m > n:
        return 0.0

    # DP matrix
    score = [[0.0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Base case: matching empty query succeeds with score 0
    for j in range(n + 1):
        score[0][j] = 0.0

    # Fill matrix: for each query character, try to match it at each position
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if query_lower[i - 1] == candidate_lower[j - 1]:
                # Characters match: score is base score per character
                match_score = 16  # base score per matched character
                # Consecutive bonus: if previous query char matched at j-1
                consecutive_bonus = (
                    4 if j > 1 and score[i - 1][j - 1] > score[i - 1][j - 2] else 0
                )
                # Boundary bonus: check character before match
                boundary_bonus = 0.0
                if j > 1:
                    prev_char = candidate_lower[j - 2]
                    if prev_char == " ":
                        boundary_bonus = 10
                    elif prev_char in ("/", "-", "_"):
                        boundary_bonus = 9
                    elif prev_char.islower() and candidate_lower[j - 1].isupper():
                        boundary_bonus = 7

                # First character match bonus multiplied by 2
                first_char_multiplier = 2 if i == 1 else 1

                score[i][j] = max(
                    score[i][j - 1],  # skip this candidate position
                    score[i - 1][j - 1]
                    + match_score * first_char_multiplier
                    + consecutive_bonus
                    + boundary_bonus,  # use this match
                )
            else:
                # No match at this position: carry forward best score
                score[i][j] = score[i][j - 1]

    final_score = score[m][n]

    # If we matched all query characters, return positive score
    if final_score > 0:
        return final_score

    # Otherwise subsequence not found
    return 0.0


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

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:limit]
