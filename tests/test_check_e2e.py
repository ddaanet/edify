"""End-to-end checks invoking real CrossHair on the seed fixtures.

These run the actual solver and are slower than the mocked tests.
"""

from pathlib import Path

from edify.check import CheckStatus
from edify.check_cli import run_crosshair

_FIXTURES = Path(__file__).parent / "fixtures" / "check_targets"


def test_buggy_head_is_refuted() -> None:
    """The no-precondition head is refuted (empty-list counterexample)."""
    result = run_crosshair(
        str(_FIXTURES / "head_buggy.py"), per_condition_timeout=10.0
    )
    assert result.status is CheckStatus.REFUTED
    assert result.findings


def test_fixed_head_is_verified() -> None:
    """Adding the precondition makes head verify."""
    result = run_crosshair(
        str(_FIXTURES / "head_fixed.py"), per_condition_timeout=10.0
    )
    assert result.status is CheckStatus.VERIFIED
