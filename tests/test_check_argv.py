"""Tests for building the CrossHair invocation argv."""

from edify.check import build_crosshair_argv


def test_argv_basic() -> None:
    """argv invokes `crosshair check` on the target."""
    assert build_crosshair_argv("foo.py") == [
        "crosshair",
        "check",
        "foo.py",
    ]


def test_argv_with_timeout() -> None:
    """A per-condition timeout is passed as a CrossHair option before target."""
    assert build_crosshair_argv("pkg.mod.fn", per_condition_timeout=5.0) == [
        "crosshair",
        "check",
        "--per_condition_timeout=5.0",
        "pkg.mod.fn",
    ]
