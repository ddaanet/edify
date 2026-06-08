"""Seed (buggy): head with no precondition.

CrossHair refutes this on the empty list (``xs[0]`` raises ``IndexError``),
demonstrating the spec-refinement branch: the fix is to add a precondition.
"""

from icontract import ensure


@ensure(lambda xs, result: result == xs[0])
def head(xs: list[int]) -> int:
    """Return the first element of xs."""
    return xs[0]
