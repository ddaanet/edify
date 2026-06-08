"""Seed (fixed): head with a precondition. CrossHair verifies it."""

from icontract import ensure, require


@require(lambda xs: len(xs) > 0)
@ensure(lambda xs, result: result == xs[0])
def head(xs: list[int]) -> int:
    """Return the first element of xs."""
    return xs[0]
